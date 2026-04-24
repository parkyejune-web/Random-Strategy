from __future__ import annotations

import argparse
import numpy as np
import pandas as pd

from strategy_discovery.discovery import discover_strategies, save_survivors


def synthetic_ohlcv(rows: int = 6000, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0001, 0.01, size=rows)
    close = 100 * np.exp(np.cumsum(rets))
    open_ = np.concatenate([[close[0]], close[:-1]])
    spread = np.abs(rng.normal(0.0, 0.005, size=rows)) * close
    high = np.maximum(open_, close) + spread
    low = np.minimum(open_, close) - spread
    volume = rng.lognormal(mean=12, sigma=0.5, size=rows)

    ts = pd.date_range("2010-01-01", periods=rows, freq="h")
    return pd.DataFrame(
        {
            "timestamp": ts,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Random strategy discovery engine")
    parser.add_argument("--input-csv", type=str, default=None, help="Optional OHLCV input CSV")
    parser.add_argument("--n-strategies", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default="survivors.csv")
    args = parser.parse_args()

    if args.input_csv:
        df = pd.read_csv(args.input_csv)
    else:
        df = synthetic_ohlcv()

    survivors = discover_strategies(df, n_strategies=args.n_strategies, seed=args.seed)
    save_survivors(survivors, args.output)

    print(f"Generated: {args.n_strategies} random strategies")
    print(f"Survivors: {len(survivors)}")
    print(f"Saved to: {args.output}\n")

    if survivors.empty:
        print("No survivors. Relax thresholds or generate more strategies.")
        return

    print("Top 20 surviving strategies:")
    cols = [
        "strategy_id",
        "expectancy",
        "stability_score",
        "max_drawdown",
        "winrate",
        "trade_count",
        "rules",
    ]
    print(survivors.loc[:19, cols].to_string(index=False, max_colwidth=120))


if __name__ == "__main__":
    main()
