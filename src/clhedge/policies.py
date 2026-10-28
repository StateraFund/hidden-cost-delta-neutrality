"""Transparent hedge-rebalancing policy examples."""
from dataclasses import dataclass
import math
import numpy as np


@dataclass
class FixedTimePolicy:
    """Rebalance every `interval_steps` observations."""
    interval_steps: int = 1

    def __post_init__(self):
        if self.interval_steps < 1:
            raise ValueError("interval_steps must be >= 1")

    def should_rebalance(self, step, target, current, volatility):
        return step == 0 or step % self.interval_steps == 0


@dataclass
class DeltaBandPolicy:
    """Rebalance when target/current hedge gap exceeds an absolute ETH band."""
    band_eth: float = 0.05

    def __post_init__(self):
        if self.band_eth < 0 or not math.isfinite(self.band_eth):
            raise ValueError("band_eth must be finite and >= 0")

    def should_rebalance(self, step, target, current, volatility):
        return step == 0 or abs(target - current) >= self.band_eth


@dataclass
class RiskAdaptiveBandPolicy:
    """Illustrative volatility-aware band; not a calibrated optimal policy.

    The band tightens as trailing annualized volatility rises:
        band = base_band / (1 + sensitivity * max(volatility, 0))
    `volatility` is supplied by the simulator using past returns only.
    """
    base_band_eth: float = 0.08
    sensitivity: float = 1.5
    min_band_eth: float = 0.01
    max_band_eth: float = 0.20

    def __post_init__(self):
        vals = (self.base_band_eth, self.sensitivity, self.min_band_eth, self.max_band_eth)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError("Policy parameters must be finite.")
        if self.base_band_eth < 0 or self.sensitivity < 0:
            raise ValueError("Base band and sensitivity must be non-negative.")
        if self.min_band_eth < 0 or self.max_band_eth < self.min_band_eth:
            raise ValueError("Invalid minimum/maximum band.")

    def effective_band(self, volatility):
        vol = max(float(volatility), 0.0) if math.isfinite(float(volatility)) else 0.0
        raw = self.base_band_eth / (1.0 + self.sensitivity * vol)
        return min(self.max_band_eth, max(self.min_band_eth, raw))

    def should_rebalance(self, step, target, current, volatility):
        return step == 0 or abs(target - current) >= self.effective_band(volatility)


def trailing_annualized_volatility(prices, end_index, lookback=20, steps_per_year=365):
    """Estimate annualized volatility from log returns available through end_index.

    `end_index` is the current observation index; only returns ending at or
    before it are used. Returns 0 when too few observations are available.
    """
    if steps_per_year <= 0:
        raise ValueError("steps_per_year must be positive.")
    if lookback < 1:
        raise ValueError("lookback must be >= 1.")
    if end_index < 2:
        return 0.0
    start = max(0, end_index - lookback)
    window = np.asarray(prices[start:end_index + 1], dtype=float)
    if len(window) < 3 or np.any(window <= 0):
        return 0.0
    log_returns = np.diff(np.log(window))
    if len(log_returns) < 2:
        return 0.0
    return float(np.std(log_returns, ddof=1) * math.sqrt(steps_per_year))
