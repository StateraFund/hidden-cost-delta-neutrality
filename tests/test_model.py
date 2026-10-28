import math
import pytest

from clhedge.model import lp_inventory, hedge_target


def test_in_range_inventory_is_nonnegative_and_value_reconciles():
    inv = lp_inventory(2000.0, 1800.0, 2200.0, 1000.0)
    assert inv.region == "in_range"
    assert inv.eth >= 0
    assert inv.usdc >= 0
    assert inv.value_usdc == pytest.approx(2000.0 * inv.eth + inv.usdc)


def test_below_range_is_all_eth():
    inv = lp_inventory(1700.0, 1800.0, 2200.0, 1000.0)
    assert inv.region == "below"
    assert inv.eth > 0
    assert inv.usdc == 0
    assert inv.delta_eth == pytest.approx(inv.eth)


def test_above_range_is_all_usdc():
    inv = lp_inventory(2300.0, 1800.0, 2200.0, 1000.0)
    assert inv.region == "above"
    assert inv.eth == 0
    assert inv.usdc > 0
    assert inv.delta_eth == 0


def test_boundaries_are_continuous_in_value():
    L = 1000.0
    lower, upper = 1800.0, 2200.0
    eps = 1e-7
    below = lp_inventory(lower - eps, lower, upper, L)
    at_lower = lp_inventory(lower, lower, upper, L)
    above = lp_inventory(lower + eps, lower, upper, L)
    assert abs(below.value_usdc - at_lower.value_usdc) < 1e-3
    assert abs(above.value_usdc - at_lower.value_usdc) < 1e-3

    below_u = lp_inventory(upper - eps, lower, upper, L)
    at_upper = lp_inventory(upper, lower, upper, L)
    above_u = lp_inventory(upper + eps, lower, upper, L)
    assert abs(below_u.value_usdc - at_upper.value_usdc) < 1e-3
    assert abs(above_u.value_usdc - at_upper.value_usdc) < 1e-3


def test_hedge_target_is_opposite_delta():
    assert hedge_target(1.25) == pytest.approx(-1.25)
    assert hedge_target(0.0) == pytest.approx(0.0)


def test_invalid_range_raises():
    with pytest.raises(ValueError):
        lp_inventory(2000.0, 2200.0, 1800.0, 1000.0)


def test_analytic_delta_matches_finite_difference():
    price, lower, upper, liquidity = 2000.0, 1800.0, 2200.0, 1234.0
    eps = 1e-3
    v_plus = lp_inventory(price + eps, lower, upper, liquidity).value_usdc
    v_minus = lp_inventory(price - eps, lower, upper, liquidity).value_usdc
    numerical_delta = (v_plus - v_minus) / (2 * eps)
    analytic = lp_inventory(price, lower, upper, liquidity).delta_eth
    assert numerical_delta == pytest.approx(analytic, rel=1e-6)


def test_in_range_second_derivative_is_negative():
    price, lower, upper, liquidity = 2000.0, 1800.0, 2200.0, 1234.0
    eps = 0.1
    v_plus = lp_inventory(price + eps, lower, upper, liquidity).value_usdc
    v_mid = lp_inventory(price, lower, upper, liquidity).value_usdc
    v_minus = lp_inventory(price - eps, lower, upper, liquidity).value_usdc
    numerical_gamma = (v_plus - 2 * v_mid + v_minus) / (eps ** 2)
    assert numerical_gamma < 0
