# CL Hedge Rebalancing Research Prototype

An educational Python project accompanying **“The Hidden Cost of Delta-Neutrality: Rethinking Hedging for Concentrated Liquidity.”**

## Scope

This repository demonstrates:
- simplified concentrated-liquidity inventory and value calculations;
- first-order LP delta and a linear perpetual hedge target;
- fixed-time, delta-band, and volatility-aware delta-band policies;
- a synthetic price-path experiment with transparent placeholder costs;
- unit tests for core model relationships.

**This is not a historical backtest, a forecast, or a live trading bot.** It does not fetch real market data, reconstruct actual LP fees, simulate a real order book, or execute trades. Numerical results are conditional on synthetic data and illustrative assumptions.

## Quick start

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

python -m pip install -r requirements.txt
python -m pytest
python run_experiment.py
```

The experiment writes CSV output and a chart under `outputs/`.

## Project structure

```text
.
├── ARTICLE.md
├── REFERENCES.md
├── CITATION_AUDIT.md
├── CHANGELOG.md
├── GITHUB_PUBLICATION_GUIDE.md
├── publication/
│   ├── ARTICLE_SUBSTACK.md
│   └── ARTICLE_MEDIUM.md
├── images/
│   ├── README.md
│   ├── chart_1_cl_inventory.png
│   ├── chart_2_delta_hedge.png
│   └── chart_3_hedging_cost_components.png
├── README.md
├── requirements.txt
├── pytest.ini
├── run_experiment.py
├── src/clhedge/
│   ├── __init__.py
│   ├── model.py
│   ├── policies.py
│   └── simulation.py
├── tests/
│   ├── test_model.py
│   ├── test_policies.py
│   └── test_simulation.py
├── data/
│   └── README.md
└── outputs/
    ├── policy_comparison.csv
    ├── per-policy CSV files
    └── synthetic_policy_comparison.png
```

## Main assumptions

- Price is USDC per ETH.
- The CL position is modeled with simplified concentrated-liquidity equations.
- The perpetual is modeled as a linear contract with signed ETH-equivalent quantity.
- Positive funding means longs pay shorts in this prototype's convention.
- Trading cost is proportional to absolute hedge adjustment notional.
- LP fee income is a synthetic placeholder accrued over elapsed intervals while the price is in range; it is not a fee estimator.
- Execution occurs at the observed simulation price; there is no latency, partial fill, market impact, or liquidation engine.
- Price paths are synthetic geometric Brownian motion, not market history. Volatility annualization accounts for `steps_per_day`.

The `author_only/` folder contains the publisher guide and pre-publication checklist. It is useful for private preparation but may be excluded from a public GitHub repository if you do not want to publish internal editorial notes. The `publication/` folder contains platform-specific article copies; keep them synchronized with `ARTICLE.md` when making future revisions.

## Research attribution

The article includes in-text citations and a References section. `CITATION_AUDIT.md` maps substantive claims to sources and records the scope of the attribution review. The bibliography distinguishes protocol documentation, AMM economics, and prior derivative-hedging research. Please verify cited source versions before making further scholarly claims.

The article chart set in `images/` is separate from the synthetic policy-comparison chart in `outputs/`. See `images/README.md` for the chart inputs and the distinction between illustrative chart inputs and the simulation configuration.

## Reproducibility and caution

The random seed is fixed in the sample configuration to make the example reproducible. The project includes a `pytest.ini` file so `python -m pytest` can discover the source package without extra path configuration. A single synthetic path is not statistically meaningful evidence. For a research study, run many paths and parameter scenarios, then use real historical data and out-of-sample validation.

Do not use this project for live trading. Do not add wallet seed phrases, private keys, exchange API secrets, or other credentials to this repository.

## AI assistance and responsibility

This project was prepared with AI assistance. The maintainer is responsible for reviewing the implementation, validating assumptions, running tests, and correcting errors. AI assistance does not independently verify the code or the conclusions.

## License

No license is included. Add one only after deciding how you want others to use, modify, and redistribute the project.
