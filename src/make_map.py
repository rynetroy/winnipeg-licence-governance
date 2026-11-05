"""
make_map.py

Draws the downtown map and a ranked chart of active licences by
neighbourhood, using the project's two downtown definitions (decision D-010):

    - Downtown (CentrePlan 2050): the 11 neighbourhoods inside the City's
      statutory downtown plan boundary, outlined in bold on the map.
    - Downtown planning area: the licence data's 'Downtown' value, which covers
      downtown and surrounding neighbourhoods.

Group membership lives in metadata/downtown_definitions.csv, not in this code.
Neighbourhoods with no licence records (for example Portage & Main) are still
drawn, so the map has no holes.

Usage:
    python src/make_map.py data/raw/Business_Licenses_20260404.csv 2026-04-04 data/raw/api_20261104 2026-11-04 data/raw/geo_neighbourhoods_csv/Neighbourhoods_20261104.csv

Outputs:
    reports/figures/downtown_map.png
    reports/figures/downtown_by_neighbourhood.png
    reports/downtown_by_neighbourhood.csv   (the numbers behind both charts)

Join rule: licences and boundaries share no code, so they are joined on the
neighbourhood name with case, spaces and punctuation ignored. The script stops
if any name fails to match.

Privacy: only neighbourhood totals are drawn. No licence location is used.

Personal project on public data. Not affiliated with or endorsed by the
City of Winnipeg.
"""

import math
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Polygon as MplPolygon, Rectangle
from matplotlib.lines import Line2D
import pandas as pd
from shapely import wkt
from shapely.ops import unary_union

from load_snapshot import load_snapshot

ROOMING, OTHER = "#2a78d6", "#eb6834"          # categorical slots 1 and 2
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
LAND, LAND_CORE, EDGE = "#f3f2ee", "#e2e0d8", "#c4c2bb"
GROUP_ORDER = ["downtown", "partly downtown", "surrounding"]
GROUP_LABEL = {"downtown": "Downtown (CentrePlan 2050)",
               "partly downtown": "Partly downtown",
               "surrounding": "Surrounding neighbourhoods"}
DEFINITIONS = Path(__file__).resolve().parent.parent / "metadata" / "downtown_definitions.csv"


def name_key(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", name.upper())


def date_label(d: str) -> str:
    t = pd.Timestamp(d)
    return f"{t:%B} {t.day}, {t.year}"


def active_counts(path: str, as_of: str) -> pd.DataFrame:
    """Active = status 'Issued', exact duplicates removed, not expired (decision D-007)."""
    df = load_snapshot(path)
    active = df[df["status"] == "Issued"].drop_duplicates()
    active = active[active["expiry_date"] >= as_of].copy()
    active["key"] = active["neighbourhood_name"].map(name_key)
    active["kind"] = active["folder_type"].map(lambda t: "rooming" if t == "LX" else "other")
    return active.groupby(["key", "kind"]).size().unstack(fill_value=0) \
                 .reindex(columns=["rooming", "other"], fill_value=0)


def planning_area_keys(path: str) -> set:
    df = load_snapshot(path)
    return set(df[df["community_characterization_area"] == "Downtown"]["neighbourhood_name"].map(name_key))


def main(old_path, old_date, new_path, new_date, boundary_path):
    defs = pd.read_csv(DEFINITIONS, dtype=str, keep_default_na=False)
    defs["key"] = defs["neighbourhood"].map(name_key)
    bounds = pd.read_csv(boundary_path, dtype=str, keep_default_na=False)
    bounds["key"] = bounds["Name"].map(name_key)
    bounds = bounds.set_index("key")

    missing = [n for n, k in zip(defs["neighbourhood"], defs["key"]) if k not in bounds.index]
    if missing:
        sys.exit(f"Neighbourhoods in downtown_definitions.csv with no boundary match: {missing}")
    in_area = planning_area_keys(old_path) | planning_area_keys(new_path)
    undefined = sorted(in_area - set(defs["key"]))
    if undefined:
        sys.exit(f"Planning-area neighbourhoods missing from downtown_definitions.csv: {undefined}")

    keys = defs["key"].tolist()
    old = active_counts(old_path, old_date).reindex(keys, fill_value=0)
    new = active_counts(new_path, new_date).reindex(keys, fill_value=0)

    table = pd.DataFrame({
        "neighbourhood": defs["neighbourhood"].values,
        "group": defs["group"].values,
        "in_licence_planning_area": [k in in_area for k in keys],
        f"rooming_{old_date}": old["rooming"].values, f"other_{old_date}": old["other"].values,
        f"rooming_{new_date}": new["rooming"].values, f"other_{new_date}": new["other"].values,
    })
    for d in (old_date, new_date):
        table[f"total_{d}"] = table[f"rooming_{d}"] + table[f"other_{d}"]
    table["group_rank"] = table["group"].map(GROUP_ORDER.index)
    table = table.sort_values(["group_rank", f"total_{new_date}"], ascending=[True, False]) \
                 .drop(columns="group_rank")
    Path("reports").mkdir(exist_ok=True)
    table.to_csv("reports/downtown_by_neighbourhood.csv", index=False)
    group_totals = table.groupby("group")[[f"total_{old_date}", f"total_{new_date}"]].sum() \
                        .reindex(GROUP_ORDER)

    shapes = {k: wkt.loads(bounds.loc[k, "Location"]) for k in keys}
    group_of = dict(zip(keys, defs["group"]))
    core_outline = unary_union([s for k, s in shapes.items() if group_of[k] == "downtown"])
    minx = min(s.bounds[0] for s in shapes.values()); maxx = max(s.bounds[2] for s in shapes.values())
    miny = min(s.bounds[1] for s in shapes.values()); maxy = max(s.bounds[3] for s in shapes.values())
    aspect = 1 / math.cos(math.radians((miny + maxy) / 2))   # keeps Winnipeg from looking stretched
    top = int(max(old.sum(axis=1).max(), new.sum(axis=1).max()))
    bar_h_per = (maxy - miny) * 0.17 / top                     # short enough that bars don't collide
    bar_w = (maxx - minx) * 0.03
    halo = [pe.withStroke(linewidth=2.5, foreground=SURFACE)]
    reach = max(shapes[k].representative_point().y + max(old.loc[k].sum(), new.loc[k].sum()) * bar_h_per
                for k in keys)
    y_top = max(maxy, reach) + (maxy - miny) * 0.05

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

    # ---- Figure 1: the map ----
    fig, axes = plt.subplots(1, 2, figsize=(11, 6.4), facecolor=SURFACE)
    for ax, (d, counts) in zip(axes, [(old_date, old), (new_date, new)]):
        ax.set_facecolor(SURFACE)
        for k, shape in shapes.items():
            fill = LAND_CORE if group_of[k] == "downtown" else LAND
            for poly in getattr(shape, "geoms", [shape]):
                ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True,
                                        facecolor=fill, edgecolor=EDGE, linewidth=0.7, zorder=1))
        for poly in getattr(core_outline, "geoms", [core_outline]):
            ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True, fill=False,
                                    edgecolor=INK, linewidth=1.8, zorder=2))
        for k in sorted(keys, key=lambda k: -shapes[k].representative_point().y):
            p = shapes[k].representative_point()
            r, o = int(counts.loc[k, "rooming"]), int(counts.loc[k, "other"])
            x0 = p.x - bar_w / 2
            if r:
                ax.add_patch(Rectangle((x0, p.y), bar_w, r * bar_h_per, facecolor=ROOMING,
                                       edgecolor=SURFACE, linewidth=0.8, zorder=3))
            if o:
                ax.add_patch(Rectangle((x0, p.y + r * bar_h_per), bar_w, o * bar_h_per,
                                       facecolor=OTHER, edgecolor=SURFACE, linewidth=0.8, zorder=3))
            ax.plot([p.x - bar_w * 0.9, p.x + bar_w * 0.9], [p.y, p.y], color=INK_2, lw=0.8, zorder=3)
            ax.text(p.x, p.y + (r + o) * bar_h_per + (maxy - miny) * 0.01, str(r + o),
                    ha="center", va="bottom", fontsize=9, color=INK, zorder=5,
                    fontweight="bold", path_effects=halo)
            if max(old.loc[k].sum(), new.loc[k].sum()) >= 10:   # name the big ones; the ranked chart names all
                ax.text(p.x, p.y - (maxy - miny) * 0.012, bounds.loc[k, "Name"], ha="center", va="top",
                        fontsize=7.5, color=INK_2, zorder=5, path_effects=halo)
        ax.set_xlim(minx - bar_w, maxx + bar_w)
        ax.set_ylim(miny - (maxy - miny) * 0.03, y_top)
        ax.set_aspect(aspect)
        ax.axis("off")
        core = int(group_totals.loc["downtown", f"total_{d}"])
        ax.set_title(f"{date_label(d)}: {int(counts.values.sum())} active, {core} downtown",
                     loc="left", color=INK, fontsize=12, fontweight="bold")
    fig.suptitle("Active licences in downtown Winnipeg and surrounding neighbourhoods", x=0.012, ha="left",
                 color=INK, fontsize=14, fontweight="bold", y=0.975)
    fig.text(0.012, 0.925, "Bold outline = downtown as defined by CentrePlan 2050 (11 neighbourhoods). "
             "Bar height = active licences, same scale in both maps.", color=INK_2, fontsize=10)
    fig.legend(handles=[Patch(color=ROOMING, label="Rooming houses"),
                        Patch(color=OTHER, label="All other licence types"),
                        Line2D([], [], color=INK, lw=1.8, label="CentrePlan 2050 downtown")],
               loc="upper left", bbox_to_anchor=(0.006, 0.915), frameon=False, ncol=3, fontsize=9)
    fig.text(0.012, 0.045, "Active = status 'Issued', exact duplicates removed, not expired on the snapshot date. "
             "Neighbourhood totals only, no licence locations. Downtown groups matched by eye to the CentrePlan 2050 map.",
             color=INK_2, fontsize=7.5)
    fig.text(0.012, 0.02, "Sources: City of Winnipeg Open Data (Business Licenses d5k3-sfzx; neighbourhood boundaries); "
             "CentrePlan 2050 (City of Winnipeg). Personal project, not affiliated with the City.",
             color=INK_2, fontsize=7.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.80, bottom=0.08, wspace=0.03)
    out = Path("reports/figures"); out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "downtown_map.png", dpi=200, facecolor=SURFACE)

    # ---- Figure 2: ranked bars, grouped, with exact numbers ----
    # Each group gets a header row of its own, so labels never sit on top of bars.
    items = []   # (kind, payload): ("header", group) or ("bar", row)
    for g in GROUP_ORDER:
        items.append(("header", g))
        items += [("bar", r) for _, r in table[table["group"] == g].iterrows()]
    n = len(items)
    fig2, axes2 = plt.subplots(1, 2, figsize=(10, 7.2), sharey=True, facecolor=SURFACE)
    xmax = table[[f"total_{old_date}", f"total_{new_date}"]].values.max() * 1.15
    for ax, d in zip(axes2, [old_date, new_date]):
        ax.set_facecolor(SURFACE)
        for yi, (kind, item) in enumerate(items):
            if kind == "header":
                if yi:
                    ax.axhline(yi - 0.5, color=GRID, linewidth=1, zorder=1)
                ax.text(0, yi + 0.1, f"{GROUP_LABEL[item]}: {int(group_totals.loc[item, f'total_{d}'])}",
                        ha="left", va="center", fontsize=9, color=INK, fontweight="bold")
                continue
            a, b = item[f"rooming_{d}"], item[f"other_{d}"]
            ax.barh(yi, a, color=ROOMING, height=0.62, zorder=2, edgecolor=SURFACE, linewidth=1)
            ax.barh(yi, b, left=a, color=OTHER, height=0.62, zorder=2, edgecolor=SURFACE, linewidth=1)
            ax.text(a + b + xmax * 0.012, yi, str(int(a + b)), va="center", fontsize=8.5, color=INK)
        ax.set_xlim(0, xmax)
        ax.set_ylim(n - 0.5, -0.6)
        ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
        ax.tick_params(colors=INK_2, length=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.set_title(date_label(d), loc="left", color=INK, fontsize=11, fontweight="bold")
    axes2[0].set_yticks(range(n), ["" if k == "header" else r["neighbourhood"] for k, r in items], color=INK)
    fig2.suptitle("Active licences by neighbourhood", x=0.012, ha="left",
                  color=INK, fontsize=13, fontweight="bold", y=0.975)
    fig2.legend(handles=[Patch(color=ROOMING, label="Rooming houses"),
                         Patch(color=OTHER, label="All other licence types")],
                loc="upper left", bbox_to_anchor=(0.006, 0.945), frameon=False, ncol=2, fontsize=9)
    fig2.text(0.012, 0.018, "Groups follow decision D-010 (metadata/downtown_definitions.csv). "
              "Same definitions and sources as the map. Personal project, not affiliated with the City.",
              color=INK_2, fontsize=7.5)
    fig2.subplots_adjust(left=0.19, right=0.98, top=0.86, bottom=0.07, wspace=0.08)
    fig2.savefig(out / "downtown_by_neighbourhood.png", dpi=200, facecolor=SURFACE)

    print(table.to_string(index=False))
    print("\nGroup totals:\n" + group_totals.to_string())
    print(f"\nWrote {out / 'downtown_map.png'}, {out / 'downtown_by_neighbourhood.png'} "
          "and reports/downtown_by_neighbourhood.csv")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        sys.exit("Usage: python src/make_map.py <old> <old_date> <new> <new_date> <boundaries.csv>")
    main(*sys.argv[1:])
