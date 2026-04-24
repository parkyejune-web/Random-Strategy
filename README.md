# Random Strategy Discovery Engine (StrategyQuant-style)

This project discovers trading strategies by **random rule generation + large-scale backtesting + robustness filtering**.

## Features

- Vectorized indicator library (SMA, EMA, RSI, Bollinger Bands, ATR, Highest, Lowest).
- Random modular strategy generation:
  - 2-4 entry rules
  - 1-2 filters
  - 1 randomized exit logic
- Backtesting with trade-level simulation and portfolio metrics.
- Robustness checks:
  - 4-way walk-forward stability
  - Monte Carlo trade resampling
  - Parameter perturbation (+/-20%)
- Survivors database to CSV.
- Ranking by expectancy, stability, and drawdown.

## Usage

```bash
python run_discovery.py --n-strategies 3000 --seed 42 --output survivors.csv
```

Optional: provide your own OHLCV CSV with columns:
`timestamp, open, high, low, close, volume`.

```bash
python run_discovery.py --input-csv your_data.csv --n-strategies 5000
```

## Output

- `survivors.csv`: full survivors table.
- Console output: top 20 surviving strategies with rule definitions.
