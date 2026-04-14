"""
Tune DYNAMIC_STRENGTH for the Fed Rate DCA strategy.

Run this from your 'fed rate' template directory:
    python tune_dynamic_strength.py

Or in Jupyter:
    %run "tune_dynamic_strength.py"
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

try:
    from template.model_development_template_eth import (
        compute_window_weights,
        precompute_features,
    )
    import template.model_development_template_eth as model_module
    from template.prelude_template_eth import backtest_dynamic_dca, load_data
except ImportError:
    from model_development_template_eth import (
        compute_window_weights,
        precompute_features,
    )
    import model_development_template_eth as model_module
    from prelude_template_eth import backtest_dynamic_dca, load_data

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.WARNING,  # suppress verbose logs during sweep
    datefmt="%Y-%m-%d %H:%M:%S",
)

# =============================================================================
# Config
# =============================================================================

BACKTEST_START = "2025-04-07"
BACKTEST_END   = "2026-01-05"

# Strengths to sweep — add or remove values as you like
STRENGTHS_TO_TEST = [-3.0, -2.0, -1.5, -1.0, -0.5, -0.25, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0]

# =============================================================================
# Load data once (reused across all runs)
# =============================================================================

print("Loading BTC data...")
os.chdir(
    "/Users/mig/Documents/LSE/Capstone Project/"
    "lse-bitcoin-analytics-capstone-template/eda"
)
btc_df = load_data()
btc_df.index = pd.to_datetime(btc_df.index)

os.chdir(
    "/Users/mig/Documents/LSE/Capstone Project/"
    "lse-bitcoin-analytics-capstone-template/template/ETH bullish related"
)

signal = pd.read_csv("eth_bullish.csv", index_col=0).iloc[:, 0]
signal.index = pd.to_datetime(signal.index, dayfirst=True)
signal.name = "signal"


print(f"Sweeping {len(STRENGTHS_TO_TEST)} values of DYNAMIC_STRENGTH...\n")

# =============================================================================
# Sweep
# =============================================================================

results = []

for strength in STRENGTHS_TO_TEST:

    # --- Patch the module constant and recompute features ---
    model_module.DYNAMIC_STRENGTH = strength
    features_df = precompute_features(btc_df, signal)

    # --- Build a weights function that closes over this features_df ---
    def make_weights_fn(feat_df):
        def compute_weights(df_window: pd.DataFrame) -> pd.Series:
            if df_window.empty:
                return pd.Series(dtype=float)
            start = df_window.index.min()
            end   = df_window.index.max()
            return compute_window_weights(feat_df, start, end, end)
        return compute_weights

    weights_fn = make_weights_fn(features_df)

    # --- Run backtest ---
    df_spd, exp_decay_pct = backtest_dynamic_dca(
        btc_df,
        weights_fn,
        features_df=features_df,
        strategy_label=f"strength={strength}",
        start_date=BACKTEST_START,
        end_date=BACKTEST_END,
    )

    if df_spd.empty:
        print(f"  strength={strength:+.2f} → no windows, skipping")
        continue

    win_rate      = (df_spd["dynamic_percentile"] > df_spd["uniform_percentile"]).mean() * 100
    score         = 0.5 * win_rate + 0.5 * exp_decay_pct
    mean_excess   = (df_spd["dynamic_percentile"] - df_spd["uniform_percentile"]).mean()
    median_excess = (df_spd["dynamic_percentile"] - df_spd["uniform_percentile"]).median()

    results.append({
        "strength":       strength,
        "score":          round(score, 4),
        "win_rate":       round(win_rate, 4),
        "exp_decay_pct":  round(exp_decay_pct, 4),
        "mean_excess":    round(mean_excess, 4),
        "median_excess":  round(median_excess, 4),
        "wins":           int((df_spd["dynamic_percentile"] > df_spd["uniform_percentile"]).sum()),
        "losses":         int((df_spd["dynamic_percentile"] <= df_spd["uniform_percentile"]).sum()),
    })

    print(
        f"  strength={strength:+.2f} | score={score:.2f}% | "
        f"win_rate={win_rate:.1f}% | mean_excess={mean_excess:+.3f}%"
    )

# =============================================================================
# Summary table
# =============================================================================

df_results = pd.DataFrame(results).sort_values("score", ascending=False)

print("\n" + "=" * 70)
print("RESULTS (sorted by score, best first)")
print("=" * 70)
print(df_results.to_string(index=False))

best = df_results.iloc[0]
print(f"\n✅ Best DYNAMIC_STRENGTH = {best['strength']} "
      f"(score={best['score']:.2f}%, win_rate={best['win_rate']:.1f}%)")

# =============================================================================
# Plot
# =============================================================================

sns.set_style("whitegrid")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# --- Score ---
axes[0].bar(
    df_results["strength"].astype(str),
    df_results["score"],
    color=["#10b981" if s == best["strength"] else "#6366f1" for s in df_results["strength"]],
    edgecolor="black",
)
axes[0].axhline(50, color="red", linestyle="--", linewidth=1.5, label="50% target")
axes[0].set_title("Final Score by Strength", fontweight="bold")
axes[0].set_xlabel("DYNAMIC_STRENGTH")
axes[0].set_ylabel("Score (%)")
axes[0].tick_params(axis="x", rotation=45)
axes[0].legend()

# --- Win Rate ---
axes[1].bar(
    df_results["strength"].astype(str),
    df_results["win_rate"],
    color=["#10b981" if s == best["strength"] else "#f59e0b" for s in df_results["strength"]],
    edgecolor="black",
)
axes[1].axhline(50, color="red", linestyle="--", linewidth=1.5, label="50% target")
axes[1].set_title("Win Rate by Strength", fontweight="bold")
axes[1].set_xlabel("DYNAMIC_STRENGTH")
axes[1].set_ylabel("Win Rate (%)")
axes[1].tick_params(axis="x", rotation=45)
axes[1].legend()

# --- Mean Excess Percentile ---
colors = [
    "#10b981" if v > 0 else "#ef4444"
    for v in df_results["mean_excess"]
]
axes[2].bar(
    df_results["strength"].astype(str),
    df_results["mean_excess"],
    color=colors,
    edgecolor="black",
)
axes[2].axhline(0, color="black", linestyle="-", linewidth=1)
axes[2].set_title("Mean Excess Percentile by Strength", fontweight="bold")
axes[2].set_xlabel("DYNAMIC_STRENGTH")
axes[2].set_ylabel("Mean Excess (%)")
axes[2].tick_params(axis="x", rotation=45)

plt.suptitle(
    f"DYNAMIC_STRENGTH Sweep  |  Backtest {BACKTEST_START} → {BACKTEST_END}",
    fontsize=13,
    fontweight="bold",
    y=1.02,
)
plt.tight_layout()

output_path = Path("dynamic_strength_sweep.png")
plt.savefig(output_path, dpi=150, bbox_inches="tight")
plt.show()
print(f"\nPlot saved to: {output_path.resolve()}")