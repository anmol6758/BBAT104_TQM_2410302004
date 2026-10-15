"""
Pareto Analysis (80/20 Rule) Chart Generator
BBAT104: Fundamentals of TQM (Academic Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Quality Goal [Q07: Improve Data Accuracy]
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for robust chart generation
import matplotlib.pyplot as plt
import pandas as pd

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.defect_logger import DefectLogger


def generate_pareto_chart(output_path=None):
    """
    Constructs a dual-axis Pareto 80/20 chart from empirical defect logs.
    Saves publication-quality chart to reports/pareto_chart.png.
    """
    if output_path is None:
        report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        os.makedirs(report_dir, exist_ok=True)
        output_path = os.path.join(report_dir, "pareto_chart.png")

    matrix, total = DefectLogger.get_checksheet_matrix()
    if not matrix or total == 0:
        DefectLogger.seed_empirical_checksheet_data(force=True)
        matrix, total = DefectLogger.get_checksheet_matrix()

    df = pd.DataFrame(matrix)

    # Shorten labels for clean chart presentation
    df["label"] = df.apply(lambda r: f"{r['code']}\n{r['category'][:14]}", axis=1)

    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor("#f8f9fa")
    ax1.set_facecolor("#ffffff")

    # Bar chart for defect frequency (Vital Few vs Trivial Many coloring)
    colors = ["#005f73" if cp <= 82 else "#94d2bd" for cp in df["cumulative_pct"]]
    bars = ax1.bar(df["label"], df["frequency"], color=colors, edgecolor="#0a9396", width=0.6, zorder=3)

    # Bar value labels
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f"{int(height)}",
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9, fontweight="bold", color="#212529")

    ax1.set_xlabel("Defect Classification (Poka-Yoke Categories)", fontsize=11, fontweight="bold", labelpad=10)
    ax1.set_ylabel("Defect Frequency (Count)", fontsize=11, fontweight="bold", color="#005f73")
    ax1.tick_params(axis="y", labelcolor="#005f73")
    ax1.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)

    # Secondary Axis for Cumulative Percentage Line
    ax2 = ax1.twinx()
    ax2.plot(df["label"], df["cumulative_pct"], color="#d90429", marker="o", linewidth=2.2, markersize=6, zorder=4)
    ax2.set_ylabel("Cumulative Percentage (%)", fontsize=11, fontweight="bold", color="#d90429")
    ax2.tick_params(axis="y", labelcolor="#d90429")
    ax2.set_ylim(0, 105)

    # 80% Cutoff Reference Line (Juran's Principle)
    ax2.axhline(80, color="#ee9b00", linestyle="--", linewidth=1.8, label="80% Cutoff (Vital Few)", zorder=2)

    # Cumulative percentage point labels
    for i, txt in enumerate(df["cumulative_pct"]):
        ax2.annotate(f"{txt:.1f}%",
                     xy=(i, txt),
                     xytext=(0, 8), textcoords="offset points",
                     ha="center", fontsize=8, fontweight="bold", color="#d90429")

    # Titles & Annotations
    plt.title(
        "Pareto Analysis (80/20 Rule) - Pharmacy Data Accuracy Defects\n"
        "BBAT104 Fundamentals of TQM | Anmol Joshi (Roll No: 2410302004) | Goal Q07",
        fontsize=12, fontweight="bold", pad=15, color="#001219"
    )

    # Legend
    ax2.legend(loc="center right", frameon=True, facecolor="#ffffff", edgecolor="#cccccc", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    return output_path


if __name__ == "__main__":
    out = generate_pareto_chart()
    print("Pareto Chart successfully generated at:", out)
