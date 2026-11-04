"""
make_figures.py

Draws the README chart: the downtown "active licence" funnel for two
snapshots, side by side on the same scale. The numbers come from the same
function the comparison report uses, so the chart can't disagree with it.

Usage:
    python src/make_figures.py data/raw/Business_Licenses_20260404.csv 2026-04-04 data/raw/api_20261104 2026-11-04

Output:
    reports/figures/downtown_funnel.png

Personal project on public data. Not affiliated with or endorsed by the
City of Winnipeg.
"""

import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw to a file; no window needed
import matplotlib.pyplot as plt

from compare_snapshots import downtown_funnel
from load_snapshot import load_snapshot

# One hue (blue), stepped light to dark: each funnel step is a stricter rule.
STEP_COLOURS = ["#86b6ef", "#3987e5", "#1c5cab"]
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
STEPS = ["Status = 'Issued'", "Exact duplicates removed", "Not expired on snapshot date"]


def label(d: str) -> str:
    return date.fromisoformat(d).strftime("%B %-d, %Y") if sys.platform != "win32" \
        else date.fromisoformat(d).strftime("%B %#d, %Y")


def main(old_path, old_date, new_path, new_date):
    panels = []
    for path, d in [(old_path, old_date), (new_path, new_date)]:
        funnel = downtown_funnel(load_snapshot(path), d)[1:]  # skip "any status" row
        panels.append((label(d), funnel))
    top = max(max(f) for _, f in panels)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True, facecolor=SURFACE)

    for ax, (title, values) in zip(axes, panels):
        ax.set_facecolor(SURFACE)
        y = range(len(STEPS))
        ax.barh(y, values, height=0.56, color=STEP_COLOURS, zorder=2)
        for yi, v in zip(y, values):
            ax.text(v + top * 0.015, yi, f"{v:,}", va="center", ha="left",
                    color=INK, fontsize=11, fontweight="bold" if yi == 2 else "normal")
        ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="bold", pad=8)
        ax.set_xlim(0, top * 1.15)
        ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
        ax.tick_params(colors=INK_2, length=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
    axes[0].set_yticks(range(len(STEPS)), STEPS, color=INK)
    axes[0].invert_yaxis()  # axes share y, so flip once: first rule on top

    fig.suptitle("Downtown licences counted as active, rule by rule",
                 x=0.012, ha="left", color=INK, fontsize=14, fontweight="bold")
    fig.text(0.012, 0.86, "Same dataset, two snapshots seven months apart. "
             "Each bar applies one more rule than the bar above it.",
             ha="left", color=INK_2, fontsize=10)
    fig.text(0.012, 0.02, "Source: City of Winnipeg Open Data, Business Licenses (d5k3-sfzx). "
             "Downtown = community characterization area 'Downtown'. "
             "Personal project, not affiliated with the City.",
             ha="left", color=INK_2, fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 0.86))
    fig.subplots_adjust(top=0.70)

    out = Path("reports/figures")
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "downtown_funnel.png", dpi=200, facecolor=SURFACE)
    print(f"Wrote {out / 'downtown_funnel.png'}")
    for title, values in panels:
        print(title, values)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("Usage: python src/make_figures.py <old> <old_date> <new> <new_date>")
    main(*sys.argv[1:])
