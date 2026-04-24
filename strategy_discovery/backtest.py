from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Dict, List, Optional

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


def _build_signals(df: pd.DataFrame, strategy: Strategy) -> tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
    cache = IndicatorCache(df)
    entry_mask = pd.Series(True, index=df.index)
    for r in strategy.entry_rules:
        entry_mask &= eval_rule(r, df, cache)

    filter_mask = pd.Series(True, index=df.index)
    for f in strategy.filters:
        filter_mask &= eval_rule(f, df, cache)

    signal = (entry_mask & filter_mask).fillna(False).to_numpy()
    opposite_signal = None
    if strategy.exit_rule["type"] == "opposite_signal":
        opposite_signal = (~entry_mask & filter_mask).fillna(False).to_numpy()

    atr_vals = None
    if strategy.exit_rule["type"] == "atr_rr":
        atr_vals = cache.get(("atr", int(strategy.exit_rule["atr_n"]))).to_numpy()

    return signal, opposite_signal, atr_vals


def backtest_strategy(df: pd.DataFrame, strategy: Strategy, fee: float = 0.0006) -> BacktestResult:
    signal, opposite_signal, atr_vals = _build_signals(df, strategy)

    exit_type = strategy.exit_rule["type"]
    close = df["close"].to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()

    raw_entries = np.flatnonzero(signal)
    trades: List[dict] = []
    last_exit = -1

    while True:
        # Explicitly allow new entry only when no position is open.
        start = np.searchsorted(raw_entries, last_exit + 1)
        if start >= len(raw_entries):
            break
        idx = int(raw_entries[start])
        if idx >= len(df) - 1:
            break

        entry_price = close[idx]
        exit_idx = None
        exit_price = None

        if exit_type == "time_stop":
            exit_idx = min(idx + int(strategy.exit_rule["bars"]), len(df) - 1)
            exit_price = close[exit_idx]

        elif exit_type == "opposite_signal":
            candidates = np.flatnonzero(opposite_signal[idx + 1 :])
            exit_idx = int(idx + 1 + candidates[0]) if len(candidates) else len(df) - 1
            exit_price = close[exit_idx]

        elif exit_type == "atr_rr":
            atr = atr_vals[idx]
            if not np.isfinite(atr) or atr <= 0:
                last_exit = idx
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
            elif tp_i is None:
                exit_idx = sl_i
                exit_price = sl
            elif sl_i is None:
                exit_idx = tp_i
                exit_price = tp
            elif sl_i <= tp_i:
                # Conservative same-bar assumption: if both touched in the same bar,
                # assume SL is executed first.
                exit_idx = sl_i
                exit_price = sl
            else:
                exit_idx = tp_i
                exit_price = tp
        else:
            raise ValueError(f"Unknown exit type: {exit_type}")

        if exit_idx is None or exit_idx <= idx:
            last_exit = idx
            continue

        gross = (exit_price - entry_price) / entry_price
        ret = gross - fee
        trades.append(
            {
                "entry_idx": int(idx),
                "exit_idx": int(exit_idx),
                "entry_time": df.iloc[idx]["timestamp"],
                "exit_time": df.iloc[exit_idx]["timestamp"],
                "entry_price": float(entry_price),
                "exit_price": float(exit_price),
                "gross_ret": float(gross),
                "fee": float(fee),
                "ret": float(ret),
            }
        )
        last_exit = int(exit_idx)

    trades_df = pd.DataFrame(trades)
    return BacktestResult(metrics=_performance_metrics(trades_df), trades=trades_df)


def monte_carlo_stability(trades: pd.DataFrame, runs: int = 200, seed: int = 0) -> float:
    if trades.empty:
        return 0.0

    rng = random.Random(seed)
    rets = trades["ret"].to_numpy()
    scores = []
    for _ in range(runs):
        # Shuffle trade order (no replacement), preserving trade distribution.
        order = np.array(rng.sample(range(len(rets)), len(rets)))
        sample = rets[order]
        eq = np.cumsum(sample)
        dd = np.maximum.accumulate(eq) - eq
        net = eq[-1]
        maxdd = dd.max() if len(dd) else 0.0
        score = net / (1e-9 + maxdd)
        scores.append(score)
    scores = np.array(scores)
    return float((scores > 0).mean())


def walk_forward_stability(df: pd.DataFrame, strategy: Strategy, fee: float = 0.0006) -> float:
    # Anchored walk-forward: evaluate forward OOS segments only when prior IS segment is viable.
    splits = np.array_split(np.arange(len(df)), 4)
    if len(splits) < 2:
        return 0.0

    oos_expectancies = []
    for i in range(1, len(splits)):
        train_idx = np.concatenate(splits[:i])
        test_idx = splits[i]
        train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]

        train_bt = backtest_strategy(train_df, strategy, fee=fee)
        if train_bt.metrics["trade_count"] < 10 or train_bt.metrics["expectancy"] <= 0:
            oos_expectancies.append(-1.0)
            continue

        test_bt = backtest_strategy(test_df, strategy, fee=fee)
        oos_expectancies.append(test_bt.metrics["expectancy"])

    evs = np.array(oos_expectancies, dtype=float)
    if len(evs) == 0:
        return 0.0

    consistency = float((evs > 0).mean())
    smoothness = float(1 / (1 + np.std(evs)))
    return 0.7 * consistency + 0.3 * smoothness


def perturbation_stability(df: pd.DataFrame, strategy: Strategy, seed: int = 0, fee: float = 0.0006) -> float:
    rng = random.Random(seed)
    base = backtest_strategy(df, strategy, fee=fee).metrics["expectancy"]
    if base == 0:
        return 0.0

    vals = []
    for _ in range(6):
        perturbed = perturb_strategy(strategy, rng, pct=0.2)
        ev = backtest_strategy(df, perturbed, fee=fee).metrics["expectancy"]
        vals.append(ev / (abs(base) + 1e-12))
    vals = np.array(vals)
    return float(np.clip(np.mean(vals > 0.5), 0, 1))


def stability_score(df: pd.DataFrame, strategy: Strategy, trades: pd.DataFrame, fee: float = 0.0006) -> Dict[str, float]:
    wf = walk_forward_stability(df, strategy, fee=fee)
    mc = monte_carlo_stability(trades)
    ps = perturbation_stability(df, strategy, fee=fee)
    total = 0.4 * wf + 0.3 * mc + 0.3 * ps
    return {"wf_score": wf, "mc_score": mc, "param_score": ps, "stability_score": total}
