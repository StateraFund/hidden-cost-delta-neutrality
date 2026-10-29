"""Run the illustrative synthetic comparison and save outputs."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from clhedge.policies import FixedTimePolicy, DeltaBandPolicy, RiskAdaptiveBandPolicy
from clhedge.simulation import SimulationConfig, generate_synthetic_prices, run_policy


def main():
    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    config = SimulationConfig()
    prices = generate_synthetic_prices(config)

    policies = [
        FixedTimePolicy(interval_steps=1),
        FixedTimePolicy(interval_steps=7),
        DeltaBandPolicy(band_eth=0.03),
        DeltaBandPolicy(band_eth=0.08),
        RiskAdaptiveBandPolicy(
            base_band_eth=0.08, sensitivity=1.5,
            min_band_eth=0.01, max_band_eth=0.20
        ),
    ]

    summaries = []
    paths = {}
    for policy in policies:
        frame, summary = run_policy(prices, policy, config)
        name = summary["policy"]
        if name == "FixedTimePolicy":
            name += f"_{policy.interval_steps}step"
        elif name == "DeltaBandPolicy":
            name += f"_{policy.band_eth:.2f}ETH"
        else:
            name += "_illustrative"
        frame.to_csv(output_dir / f"{name}_path.csv", index=False)
        summary["run_label"] = name
        summaries.append(summary)
        paths[name] = frame

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(output_dir / "policy_comparison.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for name, frame in paths.items():
        ax.plot(frame["step"], frame["net_pnl_vs_initial_lp_usdc"], label=name)
    ax.set_title("Synthetic demonstration: net P&L under stated assumptions")
    ax.set_xlabel("Observation step")
    ax.set_ylabel("Net P&L vs initial LP principal (USDC)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "synthetic_policy_comparison.png", dpi=160)
    plt.close(fig)

    print("Illustrative synthetic experiment completed.")
    print("These results are not a historical backtest or performance forecast.")
    print(summary_df.to_string(index=False))
    print(f"\nOutputs saved to: {output_dir}")


if __name__ == "__main__":
    main()
