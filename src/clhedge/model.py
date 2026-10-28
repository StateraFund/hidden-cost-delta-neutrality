"""Simplified concentrated-liquidity model.

Price convention: P is USDC per ETH. The model uses a Uniswap v3-style
liquidity parameter L and omits fees, gas, tick rounding, and protocol-specific
integer arithmetic. It is for education/research scaffolding, not production.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class LPInventory:
    eth: float
    usdc: float
    value_usdc: float
    delta_eth: float
    region: str


def lp_inventory(price: float, lower: float, upper: float, liquidity: float) -> LPInventory:
    """Return simplified token inventory, principal value, and local ETH delta.

    Below the range the position is all ETH; above it the position is all USDC.
    Within the range, use the standard square-root-price inventory equations.
    The delta is d(value in USDC)/d(price in USDC per ETH), expressed in ETH.
    """
    if not all(math.isfinite(v) for v in (price, lower, upper, liquidity)):
        raise ValueError("All inputs must be finite.")
    if price <= 0 or lower <= 0 or upper <= 0:
        raise ValueError("Prices must be positive.")
    if lower >= upper:
        raise ValueError("lower must be strictly less than upper.")
    if liquidity < 0:
        raise ValueError("liquidity must be non-negative.")

    sqrt_lower = math.sqrt(lower)
    sqrt_upper = math.sqrt(upper)

    if price <= lower:
        eth = liquidity * (1.0 / sqrt_lower - 1.0 / sqrt_upper)
        usdc = 0.0
        region = "below"
        delta = eth
    elif price >= upper:
        eth = 0.0
        usdc = liquidity * (sqrt_upper - sqrt_lower)
        region = "above"
        delta = 0.0
    else:
        sqrt_price = math.sqrt(price)
        eth = liquidity * (1.0 / sqrt_price - 1.0 / sqrt_upper)
        usdc = liquidity * (sqrt_price - sqrt_lower)
        region = "in_range"
        delta = eth

    value = price * eth + usdc
    return LPInventory(eth, usdc, value, delta, region)


def hedge_target(delta_eth: float) -> float:
    """First-order hedge target for a linear ETH perpetual.

    Signed convention: positive = long ETH, negative = short ETH.
    """
    if not math.isfinite(delta_eth):
        raise ValueError("delta_eth must be finite.")
    return -delta_eth
