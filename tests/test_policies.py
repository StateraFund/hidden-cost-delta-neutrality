import numpy as np
import pytest

from clhedge.policies import (
    FixedTimePolicy, DeltaBandPolicy, RiskAdaptiveBandPolicy,
    trailing_annualized_volatility,
)


def test_fixed_time_policy_schedule():
    policy = FixedTimePolicy(interval_steps=3)
    assert policy.should_rebalance(0, 1, 0, 0)
    assert policy.should_rebalance(3, 1, 0, 0)
    assert not policy.should_rebalance(2, 1, 0, 0)


def test_delta_band_policy():
    policy = DeltaBandPolicy(band_eth=0.1)
    assert policy.should_rebalance(1, -0.2, 0.0, 0.0)
    assert not policy.should_rebalance(1, -0.05, 0.0, 0.0)


def test_risk_adaptive_band_tightens_as_volatility_rises():
    policy = RiskAdaptiveBandPolicy(
        base_band_eth=0.08, sensitivity=2.0,
        min_band_eth=0.01, max_band_eth=0.20
    )
    assert policy.effective_band(1.0) < policy.effective_band(0.0)


def test_trailing_volatility_is_nonnegative_and_uses_history():
    prices = np.array([100.0, 101.0, 99.0, 102.0, 100.0])
    assert trailing_annualized_volatility(prices, 1) == 0.0
    assert trailing_annualized_volatility(prices, 4) >= 0.0


def test_invalid_policy_parameters_raise():
    with pytest.raises(ValueError):
        FixedTimePolicy(interval_steps=0)
    with pytest.raises(ValueError):
        DeltaBandPolicy(band_eth=-0.1)


def test_volatility_annualization_respects_observation_frequency():
    prices = np.array([100.0, 101.0, 99.0, 102.0, 100.0])
    daily = trailing_annualized_volatility(prices, 4, steps_per_year=365)
    four_per_day = trailing_annualized_volatility(prices, 4, steps_per_year=365 * 4)
    assert four_per_day == pytest.approx(daily * 2.0)


def test_volatility_rejects_nonpositive_annualization_frequency():
    with pytest.raises(ValueError):
        trailing_annualized_volatility(np.array([100.0, 101.0, 102.0]), 2, steps_per_year=0)
