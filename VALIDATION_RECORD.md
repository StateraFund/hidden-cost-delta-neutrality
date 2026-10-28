# Validation record — revised research pack

Date: 2026-10-21

## Scope and limitations

This record documents a local test run and one synthetic demonstration run. It is not an independent audit, a historical backtest, or evidence of trading profitability. The model remains educational and uses simplified accounting, synthetic prices, and placeholder fee/cost assumptions.

## Automated tests

Command: `python -m pytest -q`

Result: **17 passed**. Tests cover core inventory behavior, continuity at range boundaries, hedge sign convention, finite-difference checks of delta and curvature, policy behavior, volatility annualization, fee timing, and funding sign convention.

## Synthetic experiment

Command: `python run_experiment.py`

Result: completed successfully using the fixed seed in `SimulationConfig`. The outputs were regenerated under `outputs/`.

| Policy configuration | Net P&L (USDC) | Trading cost (USDC) | Funding P&L (USDC) | Synthetic fee income (USDC) | Rebalances |
|---|---:|---:|---:|---:|---:|
| Fixed-time, every step | -278.546570 | 11.556785 | 43.053999 | 32.752501 | 18 |
| Fixed-time, every 7 steps | -277.591618 | 5.035356 | 43.087064 | 32.752501 | 4 |
| Delta band, 0.03 ETH | -278.013232 | 11.514400 | 43.051892 | 32.752501 | 17 |
| Delta band, 0.08 ETH | -279.519472 | 11.413017 | 43.050774 | 32.752501 | 15 |
| Risk-adaptive illustrative band | -282.544696 | 11.516666 | 43.055883 | 32.752501 | 16 |

These values are conditional on one synthetic price path and the configured assumptions. Do not interpret them as forecasts or as evidence that one policy is superior. The model does not include actual position-specific LP fee accounting, realistic order-book fills, latency, liquidation, or all costs of operating a live position.

## Corrections made in this revision

- Removed the author-only instruction from the public article and replaced it with a reader-facing AI-assistance and limitations disclosure.
- Added an `author_only/` folder to separate the publisher guide and private pre-publication checklist from public-facing files.
- Added `pytest.ini` so the documented test command can import the source-layout package.
- Changed synthetic fee accrual to apply only over elapsed intervals, using the start-of-interval LP value and range status; no fee is accrued at the initial time point.
- Changed the simplified funding notional to use the start-of-interval price for consistency with the interval convention.
- Made volatility annualization account for `steps_per_day`.
- Added tests for finite-difference delta/curvature, volatility annualization, elapsed-interval fee timing, and funding sign convention.
- Added `.gitignore` and excluded generated Python/test cache files from the ZIP.
- Regenerated the CSV and chart outputs.

## Remaining limitations

This remains a prototype. Before drawing real-market conclusions, the model needs protocol-accurate inventory/fee reconstruction, venue-specific perpetual contract and funding data, realistic execution and margin modelling, multiple market paths/regimes, and out-of-sample validation. The current funding rate and synthetic fee yield are illustrative parameters, not estimates of actual market conditions.
