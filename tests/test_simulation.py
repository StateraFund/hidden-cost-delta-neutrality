import pytest

from clhedge.policies import FixedTimePolicy
from clhedge.simulation import SimulationConfig, run_policy


def test_no_synthetic_fee_is_accrued_at_initial_observation():
    config = SimulationConfig(
        initial_price=2000.0, lower_price=1800.0, upper_price=2200.0,
        initial_lp_value_usdc=10000.0, days=3, steps_per_day=1,
        synthetic_fee_yield_per_day=0.01, funding_rate_per_day=0.0,
        commission_bps=0.0, slippage_bps=0.0,
    )
    frame, _ = run_policy([2000.0, 2000.0, 2000.0], FixedTimePolicy(99), config)
    assert frame.loc[0, "synthetic_fee_income_usdc"] == pytest.approx(0.0)
    assert frame.loc[1, "synthetic_fee_income_usdc"] > 0.0
    assert frame.loc[2, "synthetic_fee_income_usdc"] > 0.0
    assert frame.loc[2, "cumulative_fees_usdc"] == pytest.approx(
        frame.loc[1, "synthetic_fee_income_usdc"] * 2.0
    )


def test_positive_funding_is_received_by_short_hedge_under_model_convention():
    config = SimulationConfig(
        initial_price=2000.0, lower_price=1800.0, upper_price=2200.0,
        initial_lp_value_usdc=10000.0, days=3, steps_per_day=1,
        synthetic_fee_yield_per_day=0.0, funding_rate_per_day=0.001,
        commission_bps=0.0, slippage_bps=0.0,
    )
    frame, _ = run_policy([2000.0, 2001.0, 2002.0], FixedTimePolicy(99), config)
    assert frame.loc[1, "funding_cash_usdc"] > 0.0
    assert frame.loc[2, "funding_cash_usdc"] > 0.0
