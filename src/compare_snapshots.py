"""
compare_snapshots.py

Compares two Business Licenses snapshots and writes a markdown report:
what grew, what disappeared, whether duplicates and stale statuses persist,
and how the downtown "active licence" count changes between them.

Usage:
    python src/compare_snapshots.py <old> <old_date> <new> <new_date>

    python src/compare_snapshots.py data/raw/Business_Licenses_20260404.csv 2026-04-04 data/raw/api_20261104 2026-11-04

Dates are the day each snapshot was taken. Validity ("not expired") is judged
against each snapshot's own date, not today's.

The report shows counts only. It never prints addresses or trade names,
because some licence types (personal services) relate to individuals.

Personal project on public data. Not affiliated with or endorsed by the
City of Winnipeg.
"""

import sys
from pathlib import Path

import pandas as pd

from load_snapshot import load_snapshot

# Fields that identify a licence record apart from its status. There is no
# licence number in the data, so this is the closest thing to a key we have.
RECORD_KEY = ["folder_type", "subdescription", "trade_name", "address",
              "issue_date", "expiry_date", "neighbourhood_name"]


def downtown_funnel(df: pd.DataFrame, as_of: str) -> list[int]:
    dt = df[df["community_characterization_area"] == "Downtown"]
    issued = dt[dt["status"] == "Issued"]
    deduped = issued.drop_duplicates()
    valid = deduped[deduped["expiry_date"] >= as_of]  # ISO text compares correctly
    return [len(dt), len(issued), len(deduped), len(valid)]


def summary(df: pd.DataFrame, as_of: str) -> dict:
    dupes = df.duplicated()
    return {
        "rows": len(df),
        "distinct rows": len(df.drop_duplicates()),
        "exact duplicate rows": int(dupes.sum()),
        "duplicate share": f"{dupes.mean():.1%}",
        "earliest issue date": df["issue_date"].min(),
        "latest issue date": df["issue_date"].max(),
        "licence families (folder_type)": ", ".join(sorted(df["folder_type"].unique())),
        "licensed activities (subdescription)": df["subdescription"].nunique(),
        "'Issued' but expired before snapshot date":
            int(((df["status"] == "Issued") & (df["expiry_date"] < as_of)).sum()),
        "expiry before issue": int((df["expiry_date"] < df["issue_date"]).sum()),
    }


def main(old_path, old_date, new_path, new_date):
    old, new = load_snapshot(old_path), load_snapshot(new_path)
    old_label, new_label = f"Old ({old_date})", f"New ({new_date})"
    out = [f"# Snapshot comparison: {old_date} vs {new_date}\n",
           f"- Old: `{Path(old_path).name}`",
           f"- New: `{Path(new_path).name}`\n"]

    # 1. Headline numbers side by side
    s = pd.DataFrame({old_label: summary(old, old_date), new_label: summary(new, new_date)})
    out += ["## 1. Headline numbers\n", s.to_markdown(), ""]

    # 2. Rows by licence family
    fam = pd.DataFrame({
        old_label: old["folder_type"].value_counts(),
        new_label: new["folder_type"].value_counts(),
        f"{new_label} duplicate rows": new[new.duplicated()]["folder_type"].value_counts(),
        f"{old_label} duplicate rows": old[old.duplicated()]["folder_type"].value_counts(),
    }).fillna(0).astype(int)
    out += ["## 2. Rows by licence family\n",
            "LP = personal sales, LQ = personal services, LR = residential, LX = rooming houses\n",
            fam.to_markdown(), ""]

    # 3. Same time window: only records issued within the old snapshot's range
    lo, hi = old["issue_date"].min(), old_date
    new_window = new[(new["issue_date"] >= lo) & (new["issue_date"] <= hi)]
    win = pd.DataFrame({
        old_label: [len(old), len(old.drop_duplicates())],
        f"{new_label}, issued {lo} to {hi}": [len(new_window), len(new_window.drop_duplicates())],
    }, index=["rows", "distinct rows"])
    out += [f"## 3. Same issue-date window ({lo} to {hi})\n", win.to_markdown(), ""]

    # 4. Do the old records still exist in the new snapshot?
    old_keys = old[RECORD_KEY].drop_duplicates()
    new_keys = new[RECORD_KEY].drop_duplicates()
    merged = old_keys.merge(new_keys, how="left", indicator=True)
    found = int((merged["_merge"] == "both").sum())
    missing = merged[merged["_merge"] == "left_only"]
    out += ["## 4. Old records found in the new snapshot\n",
            f"Matched on {', '.join(RECORD_KEY)} (status excluded, since status is expected to change).\n",
            f"- Distinct old records: {len(old_keys)}",
            f"- Found in new snapshot: {found} ({found / len(old_keys):.1%})",
            f"- Not found: {len(missing)}, by family: {missing['folder_type'].value_counts().to_dict()}", ""]

    # 5. Status changes for records present in both
    o = old.drop_duplicates(subset=RECORD_KEY + ["status"])
    n = new.drop_duplicates(subset=RECORD_KEY + ["status"])
    both = o.merge(n, on=RECORD_KEY, suffixes=("_old", "_new"))
    both = both[both.groupby(RECORD_KEY)["status_old"].transform("size") == 1]  # unambiguous matches only
    changes = both[both["status_old"] != both["status_new"]]
    stale = both[(both["status_old"] == "Issued") & (both["expiry_date"] < old_date)]
    out += ["## 5. Status changes (records matched one-to-one)\n",
            f"- Matched one-to-one: {len(both)}",
            f"- Status changed: {len(changes)}",
            "",
            changes.groupby(["status_old", "status_new"]).size().rename("records").to_frame().to_markdown()
            if len(changes) else "(none)",
            "",
            f"- Old records that were 'Issued' but already expired: {len(stale)}",
            f"  - now a different status: {int((stale['status_new'] != 'Issued').sum())}",
            f"  - still 'Issued': {int((stale['status_new'] == 'Issued').sum())}", ""]

    # 6. Downtown funnel for each snapshot
    steps = ["Downtown rows, any status", "...Status = 'Issued'",
             "...after removing exact duplicates", "...not expired as of snapshot date"]
    fun = pd.DataFrame({old_label: downtown_funnel(old, old_date),
                        new_label: downtown_funnel(new, new_date)}, index=steps)
    out += ["## 6. Downtown 'active licence' funnel\n", fun.to_markdown(), ""]

    Path("reports").mkdir(exist_ok=True)
    report = Path("reports") / f"compare_{old_date}_vs_{new_date}.md"
    report.write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
    print(f"\nWrote {report}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("Usage: python src/compare_snapshots.py <old> <old_date> <new> <new_date>")
    main(*sys.argv[1:])
