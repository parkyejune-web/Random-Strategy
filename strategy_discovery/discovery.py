from __future__ import annotations

import random
from typing import Dict, List, Optional

import pandas as pd

from .backtest import backtest_strategy, stability_score
from .rules import Strategy, generate_random_strategy


DEFAULT_THRESHOLDS: Dict[str, float] = {
    "min_net_profit": 0.0,
    "min_winrate": 0.35,
    "max_drawdown": 0.35,
    "min_expectancy": 0.0002,
    "min_sharpe": 0.2,
    "min_trade_count": 20,
    "min_stability": 0.55,
}


def passes_thresholds(metrics: Dict[str, float], thresholds: Dict[str, float]) -> bool:
    return (
        metrics["net_profit"] >= thresholds["min_net_profit"]
        and metrics["winrate"] >= thresholds["min_winrate"]
        and metrics["max_drawdown"] <= thresholds["max_drawdown"]
        and metrics["expectancy"] >= thresholds["min_expectancy"]
        and metrics["sharpe"] >= thresholds["min_sharpe"]
        and metrics["trade_count"] >= thresholds["min_trade_count"]
    )


def discover_strategies(
    df: pd.DataFrame,
    n_strategies: int = 3000,
    seed: int = 42,
    thresholds: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    if missing := required.difference(df.columns):
        raise ValueError(f"DataFrame missing required columns: {missing}")

    thresholds = thresholds or DEFAULT_THRESHOLDS
    rng = random.Random(seed)
    survivors: List[dict] = []

    for i in range(n_strategies):
        strategy: Strategy = generate_random_strategy(rng)
        bt = backtest_strategy(df, strategy)

        if not passes_thresholds(bt.metrics, thresholds):
            continue

        stab = stability_score(df, strategy, bt.trades)
        if stab["stability_score"] < thresholds["min_stability"]:
            continue

        row = {
            "strategy_id": f"SQGEN_{i:06d}",
            "rules": strategy.describe(),
            **bt.metrics,
            **stab,
        }
        survivors.append(row)

    if not survivors:
        return pd.DataFrame(
            columns=[
                "strategy_id",
                "rules",
                "net_profit",
                "winrate",
                "max_drawdown",
                "expectancy",
                "sharpe",
                "trade_count",
                "wf_score",
                "mc_score",
                "param_score",
                "stability_score",
            ]
        )

    out = pd.DataFrame(survivors)
    out = out.sort_values(
        by=["expectancy", "stability_score", "max_drawdown"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    return out


def save_survivors(df_survivors: pd.DataFrame, path: str = "survivors.csv") -> None:
    df_survivors.to_csv(path, index=False)
