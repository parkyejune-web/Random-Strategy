import unittest

import pandas as pd

from strategy_discovery.backtest import backtest_strategy, monte_carlo_stability
from strategy_discovery.rules import Strategy


class BacktestBehaviorTests(unittest.TestCase):
    def test_same_bar_tp_sl_prefers_sl_conservatively(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2020-01-01", periods=4, freq="h"),
                "open": [100.0, 100.0, 100.0, 100.0],
                "high": [101.0, 102.0, 100.0, 100.0],
                "low": [99.0, 98.0, 100.0, 100.0],
                "close": [100.0, 100.0, 100.0, 100.0],
                "volume": [1_000, 1_000, 1_000, 1_000],
            }
        )
        strategy = Strategy(entry_rules=[], filters=[], exit_rule={"type": "atr_rr", "atr_n": 1, "sl_atr": 1.0, "tp_atr": 1.0})

        result = backtest_strategy(df, strategy, fee=0.0)
        self.assertGreaterEqual(len(result.trades), 1)

        first = result.trades.iloc[0]
        self.assertAlmostEqual(first["entry_price"], 100.0)
        # If TP and SL are both touched on bar 1, SL must be chosen first.
        self.assertAlmostEqual(first["exit_price"], 98.0)
        self.assertAlmostEqual(first["ret"], -0.02)

    def test_fee_is_applied_to_trade_return(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2020-01-01", periods=3, freq="h"),
                "open": [100.0, 100.0, 100.0],
                "high": [100.0, 100.0, 100.0],
                "low": [100.0, 100.0, 100.0],
                "close": [100.0, 100.0, 100.0],
                "volume": [1_000, 1_000, 1_000],
            }
        )
        strategy = Strategy(entry_rules=[], filters=[], exit_rule={"type": "time_stop", "bars": 1})

        fee = 0.0006
        result = backtest_strategy(df, strategy, fee=fee)
        self.assertGreaterEqual(len(result.trades), 1)
        self.assertAlmostEqual(result.trades.iloc[0]["gross_ret"], 0.0)
        self.assertAlmostEqual(result.trades.iloc[0]["ret"], -fee)

    def test_monte_carlo_shuffle_preserves_positive_edge(self):
        trades = pd.DataFrame({"ret": [0.01] * 20 + [-0.002] * 5})
        score = monte_carlo_stability(trades, runs=50, seed=1)
        self.assertGreaterEqual(score, 0.9)


if __name__ == "__main__":
    unittest.main()
