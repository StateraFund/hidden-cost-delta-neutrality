# The Hidden Cost of Delta-Neutrality: Rethinking Hedging for Concentrated Liquidity

*An independent conceptual research note on concentrated-liquidity inventory, hedge turnover, and the trade-off between residual exposure and trading costs.*

## Abstract

Concentrated-liquidity (CL) positions can earn swap fees while their token inventory changes with the market price. A perpetual-futures hedge can offset some of the position's directional exposure, but maintaining a near-zero delta is not free: hedge adjustments can incur trading fees, bid–ask spread, slippage, funding, basis risk, and operational risk. A hedge rule that reacts more frequently may reduce measured directional exposure while increasing turnover and costs. Conversely, a rule that trades less may save costs while tolerating larger residual exposure.

This note develops a transparent framework for studying that trade-off. It derives the in-range inventory and delta of a simplified Uniswap v3-style position, defines a short-perpetual hedge target, and describes three candidate rebalancing policies: fixed-time, delta-band, and volatility-aware risk-adaptive rebalancing. It then proposes a reproducible experiment for comparing them on the same price path and under explicit cost assumptions.

The accompanying code is an educational research prototype. It uses synthetic prices and simplified cost assumptions to demonstrate mechanics; it is not a historical backtest, a forecast, or evidence that any policy is profitable. Real-world conclusions require position-specific fee accounting, venue-specific funding and execution data, realistic latency and fills, and out-of-sample validation.

## 1. The question is not simply whether to hedge

A concentrated-liquidity provider chooses a lower and upper price boundary. While the pool price remains inside that range, the position holds both assets. As price moves, its inventory changes: for an ETH/USDC position quoted as USDC per ETH, the position generally holds less ETH as ETH's price rises and more ETH as its price falls. This inventory path creates directional exposure and a locally short-gamma-like profile in the in-range region.

A perpetual futures contract can offset some of that directional exposure. But a hedge is a dynamic position, not a one-time switch. If the target hedge changes as the pool price moves, the strategy must decide when the expected benefit of adjusting the hedge is worth the cost and risk of doing so.

The central research question is therefore:

> Under a stated market, cost, and risk model, how should a CL position's hedge be rebalanced when reducing residual delta exposure competes with execution costs and carry?

This is a research question, not a claim that one policy is universally optimal. The answer can vary with range width, volatility, fee income, funding, liquidity, execution quality, and the risk tolerance of the operator.

## 2. A simplified concentrated-liquidity model

Let:

- \(P\) be the pool price in USDC per ETH;
- \(P_a\) be the lower price boundary;
- \(P_b\) be the upper price boundary, with \(P_a < P_b\);
- \(L\) be the position's liquidity parameter;
- \(x(P)\) be the position's ETH quantity;
- \(y(P)\) be its USDC quantity.

Within the selected range, the simplified inventory equations are

\[
x(P)=L\left(\frac{1}{\sqrt{P}}-\frac{1}{\sqrt{P_b}}\right)
\]

and

\[
y(P)=L\left(\sqrt{P}-\sqrt{P_a}\right).
\]

The position's marked value in USDC is

\[
V_{\mathrm{LP}}(P)=P\,x(P)+y(P).
\]

Differentiating the marked value with respect to \(P\) gives

\[
\frac{dV_{\mathrm{LP}}}{dP}=x(P)
\]

while the price is inside the range. In this model, the ETH inventory is the position's local delta when value is measured in USDC and the price is USDC per ETH.

A second derivative gives

\[
\frac{d^2V_{\mathrm{LP}}}{dP^2}
=-\frac{L}{2P^{3/2}}<0.
\]

The negative second derivative indicates local concavity of the position's marked value with respect to this price variable. This is often described as a short-gamma-like property: the inventory changes as price changes, so a hedge that was appropriate at one price may not remain appropriate after a move.

These equations describe the position's principal inventory under a simplified constant-product concentrated-liquidity model. They do **not** include fee balances, gas, swaps used to enter or exit a range, taxes, lending costs, or the details of a specific protocol implementation.

### What happens outside the range?

For the simplified model, below the lower boundary the position is entirely in ETH, and above the upper boundary it is entirely in USDC. Its inventory is therefore piecewise:

- If \(P \le P_a\), the position holds a fixed amount of ETH and no USDC.
- If \(P_a < P < P_b\), it holds both ETH and USDC according to the equations above.
- If \(P \ge P_b\), it holds a fixed amount of USDC and no ETH.

The in-range delta expression must not be applied blindly outside the range. Below the range, the ETH quantity is constant in this idealized model; above it, the ETH quantity is zero. A real position can also have fee balances and protocol-specific accounting details that need separate treatment.

## 3. Defining the hedge

Let \(h\) be the signed ETH-equivalent quantity of a linear ETH perpetual position: \(h>0\) means long ETH and \(h<0\) means short ETH. If the LP's local delta is \(x(P)\), a first-order delta-neutral target is

\[
h^*(P)=-x(P).
\]

The required adjustment is not the full target every time. It is the difference between the target and the hedge already held:

\[
q_t=h^*_t-h_{t^-},
\]

where \(h_{t^-}\) is the hedge position immediately before the adjustment. If \(q_t<0\), the adjustment sells or increases the short position; if \(q_t>0\), it buys or reduces the short position.

This is only a first-order hedge. It does not remove the LP's curvature, impermanent-loss path dependence, funding exposure, basis risk, liquidity risk, smart-contract risk, or execution risk. A delta-neutral snapshot is not the same thing as a risk-free portfolio.

The model also assumes the perpetual is linear and quoted in the same price convention. In practice, contract multipliers, inverse contracts, collateral currency, exchange position conventions, and the difference between the pool price and the perpetual mark price must be handled explicitly.

## 4. Why continuous correction can be expensive

A hedge policy trades off at least two categories of loss:

1. **Residual-risk cost:** the cost of leaving the combined LP-plus-hedge portfolio exposed to price moves.
2. **Adjustment cost:** commissions, spread, slippage, market impact, and other costs from changing the hedge.

Funding and basis are additional carry or relative-price effects. Funding can be either a cost or a receipt depending on the position sign and the funding rate. A short perpetual does not automatically earn funding; the sign and venue convention must be checked.

Frequent adjustments can keep the hedge closer to its target, but they may increase turnover and transaction costs. Infrequent adjustments can reduce turnover, but allow the hedge to drift away from the target. The trade-off is especially relevant for narrow ranges, where inventory and target hedge can change quickly near the boundaries, although the actual effect depends on price path and position sizing.

There is no universal answer based on rebalance frequency alone. A rule should be evaluated against the same price path, initial position, funding assumptions, cost model, and risk objective.

## 5. Three candidate policies

### 5.1 Fixed-time rebalancing

The hedge is checked and adjusted at predetermined intervals—for example, every hour or once per day.

**Potential advantages**
- Simple to implement, explain, and audit.
- Predictable operational schedule.
- Easy to compare across interval choices.

**Potential disadvantages**
- May trade when the adjustment is small and not worth its cost.
- May wait too long during a fast move.
- Performance depends on the chosen interval and the timing of observations.

Fixed-time rebalancing is a useful baseline, not necessarily a good final policy.

### 5.2 Delta-band rebalancing

The hedge is adjusted only when the gap between the current hedge and the target exceeds a defined threshold. The threshold can be specified in ETH units, US-dollar notional, or as a proportion of a risk budget.

**Potential advantages**
- Can avoid small, low-value adjustments.
- Directly expresses tolerance for hedge drift.
- Is relatively transparent and straightforward to test.

**Potential disadvantages**
- A fixed threshold may be too loose in a high-volatility regime and too tight in a quiet one.
- A threshold based only on absolute ETH quantity may not scale well as position value changes.
- A band can be crossed between observations; the policy cannot react to moves it does not observe.

The threshold must be defined with clear units. A “0.1” threshold is meaningless without saying whether it means 0.1 ETH, 0.1% of notional, or another measure.

### 5.3 Volatility-aware risk-adaptive rebalancing

A risk-adaptive rule can vary its tolerance according to a stated risk measure. For example, it may tighten the permitted hedge gap as estimated volatility rises, or as the portfolio approaches a pre-defined exposure or loss limit.

This is a family of policies, not one uniquely defined algorithm. Any implementation must specify the volatility estimator, update frequency, thresholds, and hard risk limits. A more elaborate rule is not automatically better: added parameters can overfit historical data and make the system harder to audit.

The accompanying prototype uses a deliberately simple illustrative rule: a base hedge-gap threshold is reduced as a trailing volatility estimate rises. This is only one testable design choice. It does not establish that the rule is optimal, and its parameters are not calibrated to a live venue or strategy.

## 6. A common evaluation framework

The three policies should be compared using the same underlying price path and the same initial LP position. At a minimum, record:

- LP principal value and fee assumptions;
- hedge position and residual delta over time;
- hedge turnover and number of adjustments;
- estimated trading costs;
- funding cash flow;
- net marked-to-market P&L under the stated accounting convention;
- maximum drawdown and volatility of returns;
- time spent outside the chosen CL range;
- the frequency and magnitude of risk-limit breaches.

The risk objective should not be reduced to net P&L alone. A policy may report higher simulated P&L simply because it tolerated more unhedged exposure. Report both the result and the risk taken to obtain it.

One possible abstract objective is

\[
J(\pi)=\lambda_{\Delta}R_{\Delta}(\pi)
+C_{\mathrm{execution}}(\pi)
+C_{\mathrm{carry}}(\pi),
\]

where \(\pi\) denotes a policy, \(R_{\Delta}\) is a chosen measure of residual exposure, \(C_{\mathrm{execution}}\) is estimated execution cost, and \(C_{\mathrm{carry}}\) is estimated funding or financing cost. The coefficient \(\lambda_{\Delta}\) expresses how the chosen risk measure is weighted relative to monetary costs. Its value depends on the units and scaling of the risk measure; it is not a universal constant.

This objective is a framework for thinking, not a complete utility function. In a production system, risk limits should also be enforced as explicit constraints—for example, maximum residual delta, maximum position size, maximum drawdown, minimum collateral buffer, and maximum allowed execution cost. Hard limits should not be replaced by a penalty coefficient that can be overwhelmed by a favorable cost estimate.

## 7. What a credible test requires

A meaningful historical test needs more than a price chart. It requires synchronized and correctly timestamped data for:

1. The exact CL position, range, liquidity, and token quantities.
2. Pool price and tick history, including enough information to reconstruct inventory.
3. Position-specific fee entitlement or a validated fee-accounting reconstruction.
4. The actual perpetual venue's prices, contract specifications, funding history, and fee schedule.
5. Bid–ask spread, order-book depth, and a realistic model of slippage, partial fills, and latency.
6. Gas and other on-chain costs for range changes or liquidity operations.
7. Collateral, margin, liquidation, and financing rules.

Pool-wide swap volume is not the same as fees earned by one position. A position's fee entitlement depends on its active liquidity, range, the pool's fee accounting, and the swaps that occurred while it was active. Applying a pool-wide fee rate directly to a position without reconstructing entitlement can materially misstate revenue.

A robust test should also prevent look-ahead bias. A policy may only use information that would have been available at the time it makes a decision. Parameter selection should be separated from out-of-sample evaluation. Results should be tested across different market regimes, fee conditions, volatility levels, and plausible cost assumptions.

## 8. What the accompanying code does—and does not do

The companion repository implements a small, inspectable research prototype. It:

- calculates simplified CL inventory and marked value;
- computes the first-order hedge target;
- simulates a synthetic ETH price path;
- compares fixed-time, delta-band, and volatility-aware band policies on the same path;
- applies explicitly parameterized trading-cost and funding assumptions;
- reports illustrative turnover, costs, residual exposure, and marked-to-market results;
- includes tests for core mathematical relationships.

It does **not** download real data, reconstruct actual position-specific fees, model a real exchange order book, submit trades, or demonstrate a profitable strategy. The synthetic fee rate is a placeholder rather than a prediction of fees earned by a live position. The execution model is simplified and should not be interpreted as a fill simulator.

Consequently, any numerical outputs from the example program are illustrations of how to compare policies under chosen assumptions. They are not empirical evidence about which policy is best in production.

## 9. Practical implications

The appropriate question is not “Which rebalancing rule is best in all circumstances?” It is “Which policy performs acceptably for this position, market, venue, cost structure, and risk budget—and does that conclusion survive out-of-sample testing?”

A sensible research sequence is:

1. Verify the CL inventory model and units.
2. Establish a fixed-time baseline.
3. Compare it with transparent delta-band alternatives.
4. Add volatility-aware rules only when there is a clear hypothesis to test.
5. Include execution, funding, and operational costs as faithfully as available data allows.
6. Stress-test parameter sensitivity and adverse price paths.
7. Paper-trade and reconcile simulated results against observed market data before considering live automation.

The most useful outcome may not be a single “winning” policy. It may be a map showing the conditions under which a policy saves costs, the conditions under which it allows too much exposure, and the assumptions that determine the result.

## Conclusion

Delta-neutrality is a useful exposure target, but it is not free and it is not synonymous with low total risk. For a concentrated-liquidity position, the hedge is changing because the underlying inventory is changing. Rebalancing decisions therefore involve a trade-off between residual exposure and the costs and risks of adjusting the hedge.

Fixed-time, delta-band, and volatility-aware policies provide a practical starting set of hypotheses. None should be declared superior without a consistent comparison that includes risk, costs, and realistic data. The discipline that matters most is to state the model clearly, measure what can be measured, expose assumptions, and avoid presenting an illustrative simulation as proof of live performance.

### Research note and AI assistance

This is a conceptual research note accompanied by an educational simulation, not a report of a completed historical backtest or verified trading performance. The accompanying prototype uses synthetic prices and simplified cost assumptions. It should not be used to make live trading decisions without independent validation, realistic data, security review, and appropriate risk controls.

AI tools assisted with drafting this article and developing the accompanying research prototype. The simulation uses synthetic prices and simplified cost assumptions; its outputs are illustrative and do not establish the profitability or superiority of any hedging policy.
