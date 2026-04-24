from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from . import indicators as ind


@dataclass
class Rule:
    kind: str
    params: Dict[str, float]

    def describe(self) -> str:
        p = self.params
        if self.kind == "close_gt_sma":
            return f"close > SMA({p['n']})"
        if self.kind == "close_lt_sma":
            return f"close < SMA({p['n']})"
        if self.kind == "rsi_lt":
            return f"RSI({p['n']}) < {p['x']:.1f}"
        if self.kind == "rsi_gt":
            return f"RSI({p['n']}) > {p['x']:.1f}"
        if self.kind == "break_highest":
            return f"close breaks Highest({p['n']})"
        if self.kind == "break_lowest":
            return f"close breaks Lowest({p['n']})"
        if self.kind == "bb_touch_upper":
            return f"close touches BB upper (n={p['n']}, k={p['k']:.2f})"
        if self.kind == "bb_touch_lower":
            return f"close touches BB lower (n={p['n']}, k={p['k']:.2f})"
        if self.kind == "atr_above":
            return f"ATR({p['n']}) > {p['threshold']:.5f}"
        if self.kind == "vol_above_sma":
            return f"volume > SMA(volume, {p['n']})"
        if self.kind == "trend_ema":
            return f"EMA({p['fast']}) > EMA({p['slow']})"
        return f"{self.kind}:{self.params}"


@dataclass
class Strategy:
    entry_rules: List[Rule]
    filters: List[Rule]
    exit_rule: Dict[str, float]

    def describe(self) -> str:
        entry = " AND ".join(r.describe() for r in self.entry_rules)
        flt = " AND ".join(r.describe() for r in self.filters) if self.filters else "None"
        exit_desc = self.exit_rule["type"]
        if exit_desc == "atr_rr":
            exit_desc += (
                f"(atr_n={self.exit_rule['atr_n']}, sl={self.exit_rule['sl_atr']:.2f},"
                f" tp={self.exit_rule['tp_atr']:.2f})"
            )
        elif exit_desc == "time_stop":
            exit_desc += f"(bars={self.exit_rule['bars']})"
        return f"Entry: {entry} | Filters: {flt} | Exit: {exit_desc}"


class IndicatorCache:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.cache: Dict[Tuple, pd.Series] = {}

    def get(self, key: Tuple):
        if key not in self.cache:
            name = key[0]
            if name == "sma_close":
                self.cache[key] = ind.sma(self.df["close"], key[1])
            elif name == "ema_close":
                self.cache[key] = ind.ema(self.df["close"], key[1])
            elif name == "rsi":
                self.cache[key] = ind.rsi(self.df["close"], key[1])
            elif name == "bb_upper":
                _, upper, _ = ind.bollinger_bands(self.df["close"], key[1], key[2])
                self.cache[key] = upper
            elif name == "bb_lower":
                _, _, lower = ind.bollinger_bands(self.df["close"], key[1], key[2])
                self.cache[key] = lower
            elif name == "atr":
                self.cache[key] = ind.atr(self.df, key[1])
            elif name == "highest":
                self.cache[key] = ind.highest(self.df["high"], key[1])
            elif name == "lowest":
                self.cache[key] = ind.lowest(self.df["low"], key[1])
            elif name == "sma_volume":
                self.cache[key] = ind.sma(self.df["volume"], key[1])
            else:
                raise ValueError(f"Unsupported indicator key: {key}")
        return self.cache[key]


def eval_rule(rule: Rule, df: pd.DataFrame, cache: IndicatorCache) -> pd.Series:
    c = df["close"]
    if rule.kind == "close_gt_sma":
        x = cache.get(("sma_close", int(rule.params["n"])))
        return (c > x).fillna(False)
    if rule.kind == "close_lt_sma":
        x = cache.get(("sma_close", int(rule.params["n"])))
        return (c < x).fillna(False)
    if rule.kind == "rsi_lt":
        x = cache.get(("rsi", int(rule.params["n"])))
        return (x < rule.params["x"]).fillna(False)
    if rule.kind == "rsi_gt":
        x = cache.get(("rsi", int(rule.params["n"])))
        return (x > rule.params["x"]).fillna(False)
    if rule.kind == "break_highest":
        x = cache.get(("highest", int(rule.params["n"]))).shift(1)
        return (c > x).fillna(False)
    if rule.kind == "break_lowest":
        x = cache.get(("lowest", int(rule.params["n"]))).shift(1)
        return (c < x).fillna(False)
    if rule.kind == "bb_touch_upper":
        up = cache.get(("bb_upper", int(rule.params["n"]), float(rule.params["k"])))
        return (df["high"] >= up).fillna(False)
    if rule.kind == "bb_touch_lower":
        lo = cache.get(("bb_lower", int(rule.params["n"]), float(rule.params["k"])))
        return (df["low"] <= lo).fillna(False)
    if rule.kind == "atr_above":
        a = cache.get(("atr", int(rule.params["n"])))
        return (a > rule.params["threshold"]).fillna(False)
    if rule.kind == "vol_above_sma":
        v = cache.get(("sma_volume", int(rule.params["n"])))
        return (df["volume"] > v).fillna(False)
    if rule.kind == "trend_ema":
        fast = cache.get(("ema_close", int(rule.params["fast"])))
        slow = cache.get(("ema_close", int(rule.params["slow"])))
        return (fast > slow).fillna(False)
    raise ValueError(f"Unknown rule type: {rule.kind}")


def random_entry_rule(rng: random.Random) -> Rule:
    kind = rng.choice(
        [
            "close_gt_sma",
            "close_lt_sma",
            "rsi_lt",
            "rsi_gt",
            "break_highest",
            "break_lowest",
            "bb_touch_upper",
            "bb_touch_lower",
        ]
    )
    if kind in {"close_gt_sma", "close_lt_sma", "break_highest", "break_lowest"}:
        return Rule(kind, {"n": rng.randint(5, 200)})
    if kind in {"rsi_lt", "rsi_gt"}:
        return Rule(kind, {"n": rng.randint(5, 50), "x": rng.uniform(10, 90)})
    return Rule(kind, {"n": rng.randint(10, 60), "k": rng.uniform(1.5, 3.5)})


def random_filter_rule(rng: random.Random) -> Rule:
    kind = rng.choice(["atr_above", "vol_above_sma", "trend_ema"])
    if kind == "atr_above":
        return Rule(kind, {"n": rng.randint(5, 50), "threshold": rng.uniform(0.001, 3.0)})
    if kind == "vol_above_sma":
        return Rule(kind, {"n": rng.randint(5, 120)})
    fast = rng.randint(5, 50)
    slow = rng.randint(max(10, fast + 1), 200)
    return Rule(kind, {"fast": fast, "slow": slow})


def random_exit_rule(rng: random.Random) -> Dict[str, float]:
    kind = rng.choice(["atr_rr", "opposite_signal", "time_stop"])
    if kind == "atr_rr":
        return {
            "type": kind,
            "atr_n": rng.randint(5, 50),
            "sl_atr": rng.uniform(0.5, 4.0),
            "tp_atr": rng.uniform(0.5, 8.0),
        }
    if kind == "time_stop":
        return {"type": kind, "bars": rng.randint(2, 100)}
    return {"type": kind}


def generate_random_strategy(rng: random.Random) -> Strategy:
    n_entries = rng.randint(2, 4)
    n_filters = rng.randint(1, 2)
    entry_rules = [random_entry_rule(rng) for _ in range(n_entries)]
    filters = [random_filter_rule(rng) for _ in range(n_filters)]
    exit_rule = random_exit_rule(rng)
    return Strategy(entry_rules=entry_rules, filters=filters, exit_rule=exit_rule)


def perturb_strategy(strategy: Strategy, rng: random.Random, pct: float = 0.2) -> Strategy:
    def tweak(v: float) -> float:
        return max(1e-6, v * (1 + rng.uniform(-pct, pct)))

    new_entries = []
    for r in strategy.entry_rules:
        params = {k: (round(tweak(v)) if isinstance(v, int) else tweak(v)) for k, v in r.params.items()}
        params = {k: int(max(2, v)) if isinstance(r.params[k], int) else v for k, v in params.items()}
        new_entries.append(Rule(r.kind, params))

    new_filters = []
    for r in strategy.filters:
        params = {k: (round(tweak(v)) if isinstance(v, int) else tweak(v)) for k, v in r.params.items()}
        params = {k: int(max(2, v)) if isinstance(r.params[k], int) else v for k, v in params.items()}
        new_filters.append(Rule(r.kind, params))

    new_exit = dict(strategy.exit_rule)
    for k, v in list(new_exit.items()):
        if k == "type":
            continue
        if isinstance(v, int):
            new_exit[k] = int(max(1, round(tweak(v))))
        else:
            new_exit[k] = tweak(v)

    return Strategy(new_entries, new_filters, new_exit)
