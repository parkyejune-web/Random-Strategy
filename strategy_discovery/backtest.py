from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Dict, List

import numpy as np
import pandas as pd

from .rules import IndicatorCache, Strategy, eval_rule, perturb_strategy


@dataclass
class BacktestResult:
    metrics: Dict[str, float]
    trades: pd.DataFrame


def _performance_metrics(trades: pd.DataFrame) -> Dict[str, float]:
    if trades.empty:
        return {
            "net_profit": 0.0,
            "winrate": 0.0,
            "max_drawdown": 0.0,
            "expectancy": 0.0,
            "sharpe": 0.0,
            "trade_count": 0,
        }

    rets = trades["ret"].to_numpy()
    equity = np.cumsum(rets)
    peaks = np.maximum.accumulate(equity)
    drawdowns = peaks - equity

    winrate = float((rets > 0).mean())
    expectancy = float(rets.mean())
    vol = float(np.std(rets))
    sharpe = float((expectancy / vol) * math.sqrt(len(rets))) if vol > 0 else 0.0

    return {
        "net_profit": float(rets.sum()),
        "winrate": winrate,
        "max_drawdown": float(drawdowns.max()) if len(drawdowns) else 0.0,
        "expectancy": expectancy,
        "sharpe": sharpe,
        "trade_count": int(len(rets)),
    }


def backtest_strategy(df: pd.DataFrame, strategy: Strategy) -> BacktestResult:
    cache = IndicatorCache(df)
    entry_mask = pd.Series(True, index=df.index)
    for r in strategy.entry_rules:
        entry_mask &= eval_rule(r, df, cache)

    filter_mask = pd.Series(True, index=df.index)
    for f in strategy.filters:
        filter_mask &= eval_rule(f, df, cache)

    signal = (entry_mask & filter_mask).fillna(False).to_numpy()

    exit_type = strategy.exit_rule["type"]
    close = df["close"].to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()

    opposite_signal = (~entry_mask & filter_mask).fillna(False).to_numpy() if exit_type == "opposite_signal" else None
    atr_vals = None
    if exit_type == "atr_rr":
        atr_vals = cache.get(("atr", int(strategy.exit_rule["atr_n"]))).to_numpy()

    entry_indices = np.flatnonzero(signal)
    trades: List[dict] = []
    last_exit = -1

    for idx in entry_indices:
        if idx <= last_exit or idx >= len(df) - 1:
            continue

        entry_price = close[idx]
        exit_idx = None
        exit_price = None

        if exit_type == "time_stop":
            exit_idx = min(idx + int(strategy.exit_rule["bars"]), len(df) - 1)
            exit_price = close[exit_idx]

        elif exit_type == "opposite_signal":
            candidates = np.flatnonzero(opposite_signal[idx + 1 :])
            if len(candidates):
                exit_idx = int(idx + 1 + candidates[0])
            else:
                exit_idx = len(df) - 1
            exit_price = close[exit_idx]

        elif exit_type == "atr_rr":
            atr = atr_vals[idx]
            if not np.isfinite(atr) or atr <= 0:
                continue
            sl = entry_price - atr * float(strategy.exit_rule["sl_atr"])
            tp = entry_price + atr * float(strategy.exit_rule["tp_atr"])

            hit_tp = np.flatnonzero(high[idx + 1 :] >= tp)
            hit_sl = np.flatnonzero(low[idx + 1 :] <= sl)
            tp_i = int(idx + 1 + hit_tp[0]) if len(hit_tp) else None
            sl_i = int(idx + 1 + hit_sl[0]) if len(hit_sl) else None

            if tp_i is None and sl_i is None:
                exit_idx = len(df) - 1
                exit_price = close[exit_idx]
            elif tp_i is None or (sl_i is not None and sl_i < tp_i):
                exit_idx = sl_i
                exit_price = sl
            else:
                exit_idx = tp_i
                exit_price = tp
        else:
            raise ValueError(f"Unknown exit type: {exit_type}")

        if exit_idx is None or exit_idx <= idx:
            continue

        ret = (exit_price - entry_price) / entry_price
        trades.append(
            {
                "entry_idx": int(idx),
                "exit_idx": int(exit_idx),
                "entry_time": df.iloc[idx]["timestamp"],
                "exit_time": df.iloc[exit_idx]["timestamp"],
                "entry_price": float(entry_price),
                "exit_price": float(exit_price),
                "ret": float(ret),
            }
        )
        last_exit = exit_idx

    trades_df = pd.DataFrame(trades)
    return BacktestResult(metrics=_performance_metrics(trades_df), trades=trades_df)


def monte_carlo_stability(trades: pd.DataFrame, runs: int = 200, seed: int = 0) -> float:
    if trades.empty:
        return 0.0

    rng = random.Random(seed)
    rets = trades["ret"].to_numpy()
    scores = []
    for _ in range(runs):
        sample = np.array([rets[rng.randrange(len(rets))] for _ in range(len(rets))])
        eq = np.cumsum(sample)
        dd = np.maximum.accumulate(eq) - eq
        net = eq[-1]
        maxdd = dd.max() if len(dd) else 0.0
        score = net / (1e-9 + maxdd)
        scores.append(score)
    scores = np.array(scores)
    return float((scores > 0).mean())


def walk_forward_stability(df: pd.DataFrame, strategy: Strategy) -> float:
    splits = np.array_split(np.arange(len(df)), 4)
    evs = []
    for s in splits:
        part = df.iloc[s]
        bt = backtest_strategy(part, strategy)
        evs.append(bt.metrics["expectancy"])
    evs = np.array(evs)
    if not len(evs):
        return 0.0
    consistency = float((evs > 0).mean())
    smoothness = float(1 / (1 + np.std(evs)))
    return 0.6 * consistency + 0.4 * smoothness


def perturbation_stability(df: pd.DataFrame, strategy: Strategy, seed: int = 0) -> float:
    rng = random.Random(seed)
    base = backtest_strategy(df, strategy).metrics["expectancy"]
    if base == 0:
        return 0.0

    vals = []
    for _ in range(6):
        perturbed = perturb_strategy(strategy, rng, pct=0.2)
        ev = backtest_strategy(df, perturbed).metrics["expectancy"]
        vals.append(ev / (abs(base) + 1e-12))
    vals = np.array(vals)
    return float(np.clip(np.mean(vals > 0.5), 0, 1))


def stability_score(df: pd.DataFrame, strategy: Strategy, trades: pd.DataFrame) -> Dict[str, float]:
    wf = walk_forward_stability(df, strategy)
    mc = monte_carlo_stability(trades)
    ps = perturbation_stability(df, strategy)
    total = 0.4 * wf + 0.3 * mc + 0.3 * ps
    return {"wf_score": wf, "mc_score": mc, "param_score": ps, "stability_score": total}
