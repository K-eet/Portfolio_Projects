"""
chart.py
The one chart: how old the companies in the segment are, against the window
the lifecycle score rewards.

Deliberately a single chart rather than a dashboard. It has one job — to show
that the scoring window sits over a real, populated part of the segment rather
than over an empty stretch of the distribution — and a second chart would
dilute rather than support that.

Usage:  python chart.py
"""

import os

import matplotlib
matplotlib.use("Agg")  # No display in CI or a bare terminal.
import matplotlib.pyplot as plt
import pandas as pd

import config

# From the dataviz reference palette (light mode). One series, so one hue:
# categorical slot 1. The plateau band is deliberately neutral — it is
# annotation, not a second series, and must not read as one.
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
SERIES_1 = "#2a78d6"
BAND = "#e8e7e3"
GRID = "#dedcd6"


def build(scored, output_path):
    """Render the age histogram with the scoring plateau shaded behind it."""
    fig, ax = plt.subplots(figsize=(9, 5), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    # Shade first so the bars sit on top of the band, not behind it.
    ax.axvspan(config.AGE_PLATEAU_START, config.AGE_PLATEAU_END,
               color=BAND, zorder=0)

    ages = scored["AgeYears"].clip(upper=30)
    bins = range(0, 31)
    counts, edges, patches = ax.hist(
        ages, bins=bins, color=SERIES_1, zorder=2,
        # A 2px surface gap between adjacent bars, per the mark spec.
        edgecolor=SURFACE, linewidth=1.4,
    )

    # Direct label instead of a legend box — one series needs no legend, and
    # the band is annotation that should be named where it sits.
    peak = counts.max()
    ax.text((config.AGE_PLATEAU_START + config.AGE_PLATEAU_END) / 2, peak * 1.02,
            f"Full lifecycle score\n{config.AGE_PLATEAU_START:.0f}–{config.AGE_PLATEAU_END:.0f} years",
            ha="center", va="bottom", fontsize=9, color=INK_SECONDARY, zorder=3)

    ax.set_title(
        "London property developers by company age",
        fontsize=13, color=INK_PRIMARY, pad=18, loc="left",
    )
    ax.set_xlabel("Years since incorporation", fontsize=10, color=INK_SECONDARY)
    ax.set_ylabel("Companies", fontsize=10, color=INK_SECONDARY)

    # Recessive grid and axes: the data is the only thing that should be dark.
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=1)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9, length=0)
    ax.set_xlim(0, 30)

    # Everything over 30 is clipped into the final bar. Left unlabelled it reads
    # as a genuine spike of 30-year-old companies rather than as a pile-up, so
    # the tick says so.
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
    ax.set_xticklabels(["0", "5", "10", "15", "20", "25", "30+"])

    ax.text(0, -0.16, "Source: Companies House Free Company Data Product, "
                      f"{config.SNAPSHOT_DATE}. Companies over 30 years old are "
                      "grouped into the final bar.",
            transform=ax.transAxes, fontsize=8, color=INK_SECONDARY)

    fig.tight_layout()
    fig.savefig(output_path, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main():
    scored_path = os.path.join(config.OUTPUT_DIR, "scored_segment.csv")
    if not os.path.exists(scored_path):
        raise SystemExit(f"{scored_path} not found — run `python pipeline.py` first.")
    scored = pd.read_csv(scored_path)
    out = build(scored, os.path.join(config.OUTPUT_DIR, "segment_age.png"))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
