"""
Ishikawa (Fishbone / Cause-and-Effect) Diagram Generator
BBAT104: Fundamentals of TQM (Academic Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Quality Goal [Q07: Improve Data Accuracy]
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_fishbone_diagram(output_path=None):
    """
    Renders an Ishikawa Fishbone root cause diagram across 6 TQM categories.
    Saves publication-quality chart to reports/fishbone_diagram.png.
    """
    if output_path is None:
        report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        os.makedirs(report_dir, exist_ok=True)
        output_path = os.path.join(report_dir, "fishbone_diagram.png")

    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")
    ax.axis("off")

    # Coordinates
    spine_y = 0.5
    head_x = 0.90
    tail_x = 0.08

    # Central Spine Arrow
    ax.annotate(
        "",
        xy=(head_x, spine_y),
        xytext=(tail_x, spine_y),
        arrowprops=dict(arrowstyle="->", color="#005f73", lw=4.5, mutation_scale=25)
    )

    # Problem Statement (Fish Head)
    head_box = dict(boxstyle="round4,pad=0.8", facecolor="#d90429", edgecolor="#800f2f", lw=2)
    ax.text(
        head_x + 0.02, spine_y,
        "EFFECT / PROBLEM:\n\nPharmacy Data\nInaccuracies &\nClerical Errors",
        ha="left", va="center", fontsize=11, fontweight="bold", color="#ffffff",
        bbox=head_box
    )

    # 6 Major Bone Categories (3 Top, 3 Bottom)
    bones = [
        # Top Bones (x_anchor, angle, label, causes)
        (0.24, 1, "PEOPLE\n(Staff & Clerks)", [
            "Cognitive fatigue during peak hours",
            "Clerk misreading handwriting",
            "Lack of formal Poka-Yoke training"
        ]),
        (0.50, 1, "PROCESS\n(Standard Workflows)", [
            "Free-text date entry variance",
            "Unchecked verbal telephone orders",
            "Skipping verification before commit"
        ]),
        (0.76, 1, "SOFTWARE CODE\n(Legacy Architecture)", [
            "Missing regex input masking",
            "Unchecked dropdown enums",
            "Absence of real-time auto-complete"
        ]),
        # Bottom Bones
        (0.24, -1, "MACHINE / TECH\n(Hardware Layer)", [
            "Sticky mechanical keyboards",
            "Small screens causing misclicks",
            "Local station power hiccups"
        ]),
        (0.50, -1, "MEASUREMENT\n(Auditing & QC)", [
            "Lack of automated audit logging",
            "Infrequent paper checksheet audits",
            "Delayed inventory reconciliation"
        ]),
        (0.76, -1, "ENVIRONMENT\n(Dispensary Clinic)", [
            "Distracting noise in counter rush",
            "Poor physical lighting near shelves",
            "High customer queue pressure"
        ]),
    ]

    for x_base, direction, category, causes in bones:
        y_branch = spine_y + (0.34 * direction)
        x_branch = x_base - 0.08

        # Major Bone Branch
        ax.annotate(
            "",
            xy=(x_base, spine_y),
            xytext=(x_branch, y_branch),
            arrowprops=dict(arrowstyle="->", color="#0a9396", lw=2.5, mutation_scale=15)
        )

        # Category Box
        cat_box = dict(boxstyle="round,pad=0.5", facecolor="#005f73", edgecolor="#001219", lw=1.5)
        ax.text(
            x_branch, y_branch + (0.04 * direction),
            category,
            ha="center", va="center", fontsize=10, fontweight="bold", color="#ffffff",
            bbox=cat_box
        )

        # Sub-branch causes
        for idx, cause in enumerate(causes):
            sub_frac = 0.28 + (idx * 0.26)
            sub_x = x_branch + (x_base - x_branch) * sub_frac
            sub_y = y_branch + (spine_y - y_branch) * sub_frac

            # Horizontal tick arrow for cause
            cause_dir = -0.06 if direction == 1 else -0.06
            ax.plot([sub_x - 0.04, sub_x], [sub_y, sub_y], color="#ca6702", lw=1.5)
            ax.text(
                sub_x - 0.05, sub_y,
                f"• {cause}",
                ha="right", va="center", fontsize=8, color="#212529",
                bbox=dict(boxstyle="square,pad=0.2", facecolor="#ffffff", edgecolor="#e9ecef", alpha=0.9)
            )

    # Title Banner
    plt.title(
        "Ishikawa (Fishbone) Diagram - Root Cause Analysis of Pharmacy Data Inaccuracies\n"
        "BBAT104 Fundamentals of TQM | Anmol Joshi (Roll No: 2410302004) | Quality Goal [Q07]",
        fontsize=13, fontweight="bold", pad=20, color="#001219"
    )

    # Footer note
    ax.text(
        0.5, 0.02,
        "Root causes in 'Software Code' and 'Process' are systematically resolved via Q07 Poka-Yoke Controls & SQLite Triggers.",
        ha="center", va="center", fontsize=9, fontstyle="italic", color="#6c757d"
    )

    ax.set_xlim(0, 1.15)
    ax.set_ylim(0, 1.0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    return output_path


if __name__ == "__main__":
    out = generate_fishbone_diagram()
    print("Ishikawa Fishbone Diagram successfully generated at:", out)
