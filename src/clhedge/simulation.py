"""Synthetic-path comparison for simple CL hedge policies."""
from dataclasses import dataclass
import math
import numpy as np
import pandas as pd

from .model import lp_inventory, hedge_target
from .policies import trailing_annualized_volatility


@dataclass(frozen=True)
class SimulationConfig:
    initial_price: float = 2000.0
    lower_price: float = 1800.0
    upper_price: float = 2200.0
    initial_lp_value_usdc: float = 10_000.0
    annualized_volatility: float = 0.80
    annualized_drift: float = 0.0
    days: int = 180
    steps_per_day: int = 1
    seed: int = 7
    commission_bps: float = 2.0
    slippage_bps: float = 3.0
    funding_rate_per_day: float = 0.00005
    synthetic_fee_yield_per_day: float = 0.0002
    volatility_lookback: int = 20

    def validate(self):
        if self.initial_price <= 0 or self.lower_price <= 0 or self.upper_price <= 0:
            raise ValueError("All prices must be positive.")
        if not self.lower_price < self.initial_price < self.upper_price:
            raise ValueError("For this demo, initial price must be strictly in range.")
        if self.initial_lp_value_usdc <= 0:
            raise ValueError("Initial LP value must be positive.")
        if self.days < 2 or self.steps_per_day < 1:
            raise ValueError("days must be >= 2 and steps_per_day >= 1.")
        if self.annualized_volatility < 0:
            raise ValueError("Volatility must be non-negative.")
        if self.commission_bps < 0 or self.slippage_bps < 0:
            raise ValueError("Cost bps must be non-negative.")
        if self.synthetic_fee_yield_per_day < 0:
            raise ValueError("Synthetic fee yield must be non-negative.")


def generate_synthetic_prices(config: SimulationConfig) -> np.ndarray:
    """Generate a reproducible geometric-Brownian-motion price path."""
    config.validate()
    rng = np.random.default_rng(config.seed)
    n = config.days * config.steps_per_day
    dt = 1.0 / (365.0 * config.steps_per_day)
    sigma = config.annualized_volatility
    mu = config.annualized_drift
    z = rng.normal(0.0, 1.0, size=n - 1)
    increments = (mu - 0.5 * sigma * sigma) * dt + sigma * math.sqrt(dt) * z
    prices = np.empty(n, dtype=float)
    prices[0] = config.initial_price
    prices[1:] = config.initial_price * np.exp(np.cumsum(increments))
    return prices


def _liquidity_for_target_value(config):
    unit = lp_inventory(
        config.initial_price, config.lower_price, config.upper_price, 1.0
    ).value_usdc
    return config.initial_lp_value_usdc / unit


def run_policy(prices, policy, config: SimulationConfig):
    """Run one policy on one price path.

    Accounting convention:
    - LP principal value is marked at each observation.
    - Perp P&L for an interval uses the hedge held during that interval.
    - Hedge adjustment costs are charged when a trade is made.
    - Funding cash flow uses the held hedge, current price, and configured
      per-day rate. Positive funding means longs pay shorts.
    - Synthetic LP fees are added as cash income only while price is in range.
    - No execution latency, partial fills, market impact, liquidation, or
      real protocol fee accounting is modeled.
    """
    config.validate()
    prices = np.asarray(prices, dtype=float)
    if len(prices) < 2 or np.any(prices <= 0) or not np.all(np.isfinite(prices)):
        raise ValueError("prices must contain at least two finite positive values.")

    liquidity = _liquidity_for_target_value(config)
    n = len(prices)
    dt_days = 1.0 / config.steps_per_day
    steps_per_year = 365 * config.steps_per_day
    trade_rate = (config.commission_bps + config.slippage_bps) / 10_000.0

    rows = []
    hedge = 0.0
    cumulative_fees = 0.0
    cumulative_trade_cost = 0.0
    cumulative_funding = 0.0
    cumulative_perp_pnl = 0.0
    turnover = 0.0
    rebalance_count = 0
    previous_price = prices[0]
    initial_lp_value = lp_inventory(
        prices[0], config.lower_price, config.upper_price, liquidity
    ).value_usdc

    for i, price in enumerate(prices):
        inv = lp_inventory(price, config.lower_price, config.upper_price, liquidity)
        target = hedge_target(inv.delta_eth)
        vol = trailing_annualized_volatility(
            prices, i, lookback=config.volatility_lookback,
            steps_per_year=steps_per_year
        )
        # Gap before the decision is the exposure drift the policy observes.
        hedge_gap_before_decision = target - hedge
        trade_eth = 0.0
        trade_cost = 0.0
        funding_cash = 0.0
        perp_interval_pnl = 0.0
        fee_income = 0.0

        if i > 0:
            # The previous hedge is held across the price move into this step.
            perp_interval_pnl = hedge * (price - previous_price)
            cumulative_perp_pnl += perp_interval_pnl
            # Approximate interval funding using the start-of-interval price.
            funding_cash = -hedge * previous_price * config.funding_rate_per_day * dt_days
            cumulative_funding += funding_cash

        # Accrue synthetic fees only for elapsed intervals, using the
        # start-of-interval LP value and range status. No fee is earned at t=0.
        if i > 0:
            previous_inv = lp_inventory(
                previous_price, config.lower_price, config.upper_price, liquidity
            )
            if previous_inv.region == "in_range":
                fee_income = (
                    previous_inv.value_usdc
                    * config.synthetic_fee_yield_per_day
                    * dt_days
                )
                cumulative_fees += fee_income

        if policy.should_rebalance(i, target, hedge, vol):
            trade_eth = target - hedge
            trade_cost = abs(trade_eth) * price * trade_rate
            cumulative_trade_cost += trade_cost
            turnover += abs(trade_eth) * price
            if abs(trade_eth) > 1e-12:
                rebalance_count += 1
            hedge = target

        total_value = (
            inv.value_usdc
            + cumulative_fees
            + cumulative_perp_pnl
            + cumulative_funding
            - cumulative_trade_cost
        )
        rows.append({
            "step": i,
            "price": price,
            "lp_eth": inv.eth,
            "lp_usdc": inv.usdc,
            "lp_value_usdc": inv.value_usdc,
            "lp_delta_eth": inv.delta_eth,
            "target_hedge_eth": target,
            "hedge_eth_after_decision": hedge,
            "hedge_gap_eth_before_decision": hedge_gap_before_decision,
            "hedge_gap_eth_after_decision": target - hedge,
            "trailing_annualized_vol": vol,
            "trade_eth": trade_eth,
            "trade_cost_usdc": trade_cost,
            "funding_cash_usdc": funding_cash,
            "perp_interval_pnl_usdc": perp_interval_pnl,
            "synthetic_fee_income_usdc": fee_income,
            "cumulative_fees_usdc": cumulative_fees,
            "cumulative_trade_cost_usdc": cumulative_trade_cost,
            "cumulative_funding_pnl_usdc": cumulative_funding,
            "cumulative_perp_pnl_usdc": cumulative_perp_pnl,
            "turnover_usdc": turnover,
            "rebalance_count": rebalance_count,
            "total_value_usdc": total_value,
            "net_pnl_vs_initial_lp_usdc": total_value - initial_lp_value,
            "in_range": inv.region == "in_range",
            "region": inv.region,
        })
        previous_price = price

    frame = pd.DataFrame(rows)
    equity = frame["total_value_usdc"]
    running_peak = equity.cummax()
    drawdown = equity / running_peak - 1.0
    frame["drawdown_fraction"] = drawdown
    summary = {
        "policy": type(policy).__name__,
        "observations": len(frame),
        "net_pnl_usdc": float(frame["net_pnl_vs_initial_lp_usdc"].iloc[-1]),
        "trade_cost_usdc": float(frame["cumulative_trade_cost_usdc"].iloc[-1]),
        "funding_pnl_usdc": float(frame["cumulative_funding_pnl_usdc"].iloc[-1]),
        "synthetic_fee_income_usdc": float(frame["cumulative_fees_usdc"].iloc[-1]),
        "perp_pnl_usdc": float(frame["cumulative_perp_pnl_usdc"].iloc[-1]),
        "turnover_usdc": float(frame["turnover_usdc"].iloc[-1]),
        "rebalance_count": int(frame["rebalance_count"].iloc[-1]),
        "mean_abs_hedge_gap_eth": float(frame["hedge_gap_eth_before_decision"].abs().mean()),
        "max_drawdown_fraction": float(frame["drawdown_fraction"].min()),
        "time_in_range_fraction": float(frame["in_range"].mean()),
    }
    return frame, summary
