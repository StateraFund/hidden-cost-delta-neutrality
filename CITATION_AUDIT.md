# Citation audit — original CL hedging article

## Purpose and scope

This audit records the principal scholarly claims in `ARTICLE.md`, why attribution is needed, and how the cited source is used. It is not a claim that every sentence requires a citation. Standard algebra and the project's own implementation details are described directly; sources are cited for protocol mechanics, prior concepts, and existing methods.

| Article location / claim | Attribution needed? | Source(s) | What the source supports | Editorial treatment / limit |
|---|---|---|---|---|
| Related work: concentrated-liquidity design | Yes | [1] Adams et al. (2021) | Uniswap v3's range-bounded concentrated-liquidity mechanism | Cite as protocol foundation; do not present the protocol's mechanism as original to this note. |
| Model: inventory equations and range interpretation | Yes | [1] | Protocol mechanics underlying simplified inventory equations | State equations are a simplified representation; this implementation omits protocol integer arithmetic, ticks, fees, and other operational details. |
| Related work / economics: LVR and adverse selection | Yes | [2] Milionis et al. (2022; revised 2024) | LVR as an AMM adverse-selection / stale-price cost concept | Explicitly distinguish LVR from impermanent loss. The prototype does not estimate LVR. |
| Related work: static option replication of CL impermanent loss | Yes | [3] Deng et al. (2023) | Static replication formulas using European calls or puts | Acknowledge prior option-hedging research; do not claim that option hedging itself is novel. |
| Related work: static and dynamic IL hedging | Yes | [4] Lipton et al. (2025) | Frameworks for static and dynamic IL-protection hedging | Acknowledge existing work; this article's experiment is about perpetual hedge-rebalancing policies, not a replication of their methods. |
| Related work / linear hedging context | Yes | [5] Maire & Wunsch (2024) | Market-neutral CL hedge portfolio using options and futures, with practical capital considerations | Cite as adjacent existing research; do not imply the prototype implements their portfolio. |
| Fixed-time, delta-band, risk-adaptive policy descriptions | Citation optional for generic definitions; cite prior source if claiming a specific borrowed algorithm | No specific external algorithm claimed | These are the policies as defined in this project's code | Describe the risk-adaptive rule as a simple illustrative design, not a novel or optimal method. |
| Synthetic results and cost assumptions | No external source supports these particular outputs | `run_experiment.py`, `src/clhedge/`, `outputs/`, `VALIDATION_RECORD.md` | The package's own implementation and one configured synthetic run | Identify outputs as synthetic and conditional. Never attribute these results to the literature or call them historical backtest results. |
| Chart 1–2 inventory / delta illustrations | Cite model foundation | [1] plus `images/README.md` | CL mechanics and stated illustrative chart inputs | Chart inputs are Pₐ=1,500, Pᵦ=2,500, L=1,000; these are distinct from simulation config. |
| Chart 3 cost components | No scholarly source for hypothetical values | `images/chart_3_hedging_cost_components.png`, `images/README.md` | Accounting illustration only | Values are hypothetical; not historical, not outputs of the policy experiment, and not a forecast. |

## Verified bibliographic metadata used in this revision

- [1] Official Uniswap v3 Core whitepaper lists Adams, Zinsmeister, Salem, Keefer, and Robinson and is dated March 2021: https://blog.uniswap.org/whitepaper-v3.pdf
- [2] arXiv record for *Automated Market Making and Loss-Versus-Rebalancing*: https://arxiv.org/abs/2208.06046. The PDF records an initial 2022 version and a May 2024 revision.
- [3] Elsevier record for Deng, Zong, and Wang, *Operations Research Letters* 51(3), 206–211 (2023), DOI 10.1016/j.orl.2023.03.002: https://doi.org/10.1016/j.orl.2023.03.002
- [4] Publisher metadata for Lipton, Lucic, and Sepp, *Digital Finance* 7(3), 429–477 (2025), DOI 10.1007/s42521-025-00144-5: https://doi.org/10.1007/s42521-025-00144-5
- [5] Ledger record for Maire and Wunsch, *Ledger* 9, 73–88 (2024), DOI 10.5195/ledger.2024.389: https://doi.org/10.5195/ledger.2024.389

## Audit limitations

This is a focused audit of the core research article and related publication materials, not a systematic review of all CL hedging literature. It identifies relevant foundational and directly related sources; additional literature may be relevant. Before making any claim of novelty, conduct a broader literature search and read the full papers, not only abstracts or metadata.
