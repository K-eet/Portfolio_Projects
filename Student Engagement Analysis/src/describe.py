"""Descriptive tables and charts for the OULAD engagement analysis.

Produces one table of outcome rates by deprivation band, and two charts that
the README embeds. Every chart carries a title, axis labels, and a caption
sentence returned alongside it.

Run directly to write the charts into outputs/ and print the table:

    python -m src.describe
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.clean import IMD_ORDER, build_analysis_table

OUTPUT_DIR = Path("outputs")

# Validated single-hue palette. See the data visualisation reference.
SERIES = "#2a78d6"
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

MISSING_LABEL = "not recorded"


def _style_axes(ax: plt.Axes) -> None:
    """Recessive chrome: no top or right spine, hairline horizontal grid."""
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
        ax.spines[side].set_linewidth(1.0)
    ax.grid(axis="y", color=GRIDLINE, linewidth=1.0)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK_MUTED, labelsize=9, length=0)


def outcome_rates_by_imd(df: pd.DataFrame) -> pd.DataFrame:
    """Outcome rates by deprivation band, for the analysis sample.

    Students whose imd_band is not recorded appear as their own row rather
    than being dropped.
    """
    sample = df.loc[df["in_analysis_sample"]].copy()
    band = sample["imd_band"].cat.add_categories([MISSING_LABEL]).fillna(
        MISSING_LABEL
    )
    grouped = sample.groupby(band, observed=True)

    table = pd.DataFrame(
        {
            "students": grouped.size(),
            "withdrawn_pct": grouped["withdrawn"].mean() * 100,
            "passed_pct": grouped["passed"].mean() * 100,
            "mean_score": grouped["mean_score"].mean(),
            "median_early_clicks": grouped["early_clicks"].median(),
        }
    )
    return table.round(1)


def plot_withdrawal_by_imd(df: pd.DataFrame, path: Path) -> str:
    """Bar chart of withdrawal rate by deprivation band. Returns the caption."""
    sample = df.loc[df["in_analysis_sample"] & df["imd_band"].notna()]
    rates = sample.groupby("imd_band", observed=True)["withdrawn"].mean() * 100
    rates = rates.reindex(IMD_ORDER)
    overall = sample["withdrawn"].mean() * 100

    fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.bar(range(len(rates)), rates.values, width=0.72, color=SERIES)
    _style_axes(ax)

    ax.axhline(overall, color=INK_MUTED, linewidth=1.2, linestyle=(0, (4, 3)))
    ax.annotate(
        f"All bands: {overall:.1f}%",
        xy=(len(rates) - 0.4, overall),
        xytext=(0, 6),
        textcoords="offset points",
        ha="right", fontsize=9, color=INK_SECONDARY,
    )

    # Label only the two ends; the table carries every exact value.
    for idx in (0, len(rates) - 1):
        ax.annotate(
            f"{rates.values[idx]:.1f}%",
            xy=(idx, rates.values[idx]), xytext=(0, 4),
            textcoords="offset points", ha="center",
            fontsize=9, color=INK,
        )

    ax.set_xticks(range(len(rates)))
    ax.set_xticklabels(rates.index, rotation=45, ha="right")
    ax.set_xlabel("Deprivation band of home area (0-10% = most deprived)",
                  fontsize=10, color=INK_SECONDARY, labelpad=8)
    ax.set_ylabel("Withdrew from the module (%)", fontsize=10,
                  color=INK_SECONDARY, labelpad=8)
    ax.set_title("Withdrawal rate by deprivation band",
                 fontsize=13, color=INK, loc="left", pad=14)
    ax.set_ylim(0, max(rates.values) * 1.22)

    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)

    excluded = int(
        (df["in_analysis_sample"] & df["imd_band"].isna()).sum()
    )
    return (
        f"Withdrawal is highest among students from the most deprived areas "
        f"({rates.iloc[0]:.1f}%) and lowest among those from the least deprived "
        f"({rates.iloc[-1]:.1f}%), a gap of "
        f"{rates.iloc[0] - rates.iloc[-1]:.1f} percentage points, though the "
        f"decline across the middle bands is uneven rather than steady. "
        f"{excluded:,} students whose band is not recorded are left out of this "
        f"chart."
    )


def plot_early_clicks(df: pd.DataFrame, path: Path) -> str:
    """Histogram of early clicks. Returns the caption."""
    clicks = df.loc[df["in_analysis_sample"], "early_clicks"]
    cutoff = int(clicks.quantile(0.99))
    median = int(clicks.median())
    above = int((clicks > cutoff).sum())

    # Truncate at the 99th percentile and pile the tail into a final bin, so
    # the shape is legible and nothing is quietly discarded.
    capped = clicks.clip(upper=cutoff)

    fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.hist(capped, bins=40, color=SERIES, rwidth=0.9)
    _style_axes(ax)

    ax.axvline(median, color=INK_MUTED, linewidth=1.2, linestyle=(0, (4, 3)))
    ax.annotate(
        f"Median {median} clicks",
        xy=(median, ax.get_ylim()[1] * 0.92), xytext=(8, 0),
        textcoords="offset points", fontsize=9, color=INK_SECONDARY,
    )

    ax.set_xlabel(
        f"Total VLE clicks in days 0-29  (final bar holds the "
        f"{above:,} students above {cutoff:,})",
        fontsize=10, color=INK_SECONDARY, labelpad=8,
    )
    ax.set_ylabel("Number of students", fontsize=10,
                  color=INK_SECONDARY, labelpad=8)
    ax.set_title("Early engagement is heavily skewed",
                 fontsize=13, color=INK, loc="left", pad=14)

    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)

    zero = int((clicks == 0).sum())
    return (
        f"Most students click a few hundred times in the first month, the "
        f"median being {median}, but the spread is wide and {zero:,} students "
        f"({zero / len(clicks) * 100:.1f}%) record no clicks at all."
    )


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    df, _ = build_analysis_table()

    table = outcome_rates_by_imd(df)
    print("Outcome rates by deprivation band (analysis sample)\n")
    print(table.to_string())

    caption_a = plot_withdrawal_by_imd(df, OUTPUT_DIR / "withdrawal_by_imd.png")
    caption_b = plot_early_clicks(df, OUTPUT_DIR / "early_clicks.png")

    print("\nwithdrawal_by_imd.png")
    print(f"  {caption_a}")
    print("\nearly_clicks.png")
    print(f"  {caption_b}")


if __name__ == "__main__":
    main()
