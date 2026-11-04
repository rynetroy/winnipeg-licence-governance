"""
profile_extract.py

Profiles one Business Licenses snapshot and writes a markdown report.
Works on either source format (manual CSV or API snapshot folder), because
it reads through load_snapshot.py.

Usage:
    python src/profile_extract.py data/raw/Business_Licenses_20260404.csv 2026-04-04
    python src/profile_extract.py data/raw/api_20261104 2026-11-04

The second argument is the snapshot date (the day the data was pulled).
"Is this licence still valid?" can only be answered relative to a date.

Privacy: the report never lists actual addresses, trade names or
coordinates. Some licence types (personal services) relate to individuals,
so only counts are shown for those columns.

Personal project on public data. Not affiliated with or endorsed by the
City of Winnipeg.
"""

import sys
from pathlib import Path

import duckdb
import pandas as pd

from load_snapshot import load_snapshot

# Columns whose values could identify a person or a home. Counted, never listed.
MASKED_COLUMNS = {"trade_name", "address", "location"}


def column_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col].str.strip()
        if col in MASKED_COLUMNS:
            top_values = "(values not shown: may identify individuals)"
        else:
            top = s.value_counts().head(3)
            top_values = "; ".join(f"{k or '(blank)'} ({v})" for k, v in top.items())
        rows.append({
            "column": col,
            "blank": int((s == "").sum()),
            "blank_pct": round((s == "").mean() * 100, 1),
            "distinct": int(s.nunique()),
            "top_values": top_values,
        })
    return pd.DataFrame(rows)


def main(path: str, snapshot_date: str) -> None:
    df = load_snapshot(path)
    n = len(df)

    # DuckDB can query a pandas DataFrame registered under a table name.
    # Dates are ISO text, so TRY_CAST turns them into real dates (blank -> NULL).
    con = duckdb.connect()
    con.register("lic", df)
    checks = con.execute(f"""
        WITH d AS (
            SELECT *,
                   TRY_CAST(NULLIF(issue_date, '')  AS DATE) AS issue_dt,
                   TRY_CAST(NULLIF(expiry_date, '') AS DATE) AS expiry_dt
            FROM lic
        )
        SELECT
            SUM(CASE WHEN issue_dt  IS NULL THEN 1 ELSE 0 END)     AS missing_issue_date,
            SUM(CASE WHEN expiry_dt IS NULL THEN 1 ELSE 0 END)     AS missing_expiry_date,
            SUM(CASE WHEN expiry_dt < issue_dt THEN 1 ELSE 0 END)  AS expiry_before_issue,
            SUM(CASE WHEN status = 'Issued'
                      AND expiry_dt < DATE '{snapshot_date}' THEN 1 ELSE 0 END) AS issued_but_expired,
            MIN(issue_dt) AS min_issue,
            MAX(issue_dt) AS max_issue
        FROM d
    """).df().iloc[0]

    exact_dupes = int(df.duplicated().sum())
    dupe_groups = int(df[df.duplicated(keep=False)].drop_duplicates().shape[0])

    # The "active downtown" funnel: how the count changes as each rule is applied.
    downtown = df[df["community_characterization_area"] == "Downtown"]
    step1 = downtown[downtown["status"] == "Issued"]
    step2 = step1.drop_duplicates()
    step3 = step2[step2["expiry_date"] >= snapshot_date]  # ISO text sorts like dates
    funnel = pd.DataFrame([
        ("Downtown rows, any status", len(downtown)),
        ("...with status = 'Issued'", len(step1)),
        ("...after removing exact duplicate rows", len(step2)),
        ("...and expiry date on or after the snapshot date", len(step3)),
    ], columns=["step", "rows"])
    by_type = step3["folder_type"].value_counts().to_dict()

    out = [
        f"# Profile: {Path(path).name}\n",
        f"Snapshot date used for validity checks: {snapshot_date}\n",
        f"Rows: {n}  |  Columns: {df.shape[1]}\n",
        "## Column profile\n",
        column_profile(df).to_markdown(index=False),
        "\n## Licensed activities by family\n",
        "LP = personal sales, LQ = personal services, LR = residential, LX = rooming houses\n",
        pd.crosstab(df["subdescription"], df["folder_type"]).to_markdown(),
        "\n## Status values\n",
        df["status"].value_counts().to_frame("rows").to_markdown(),
        "\n## Row-level checks\n",
        f"- Exact duplicate rows (every column identical): {exact_dupes} "
        f"({exact_dupes / n:.1%}), across {dupe_groups} distinct records",
        f"- Missing issue / expiry dates: {int(checks.missing_issue_date)} / "
        f"{int(checks.missing_expiry_date)}",
        f"- Expiry date before issue date: {int(checks.expiry_before_issue)}",
        f"- Status 'Issued' but expired before {snapshot_date}: {int(checks.issued_but_expired)}",
        f"- Issue date range: {str(checks.min_issue)[:10]} to {str(checks.max_issue)[:10]}",
        "\n## Downtown 'active licence' funnel\n",
        funnel.to_markdown(index=False),
        f"\nFinal step by family: {by_type}\n",
    ]

    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"profile_{snapshot_date}.md"
    report_path.write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
    print(f"\nWrote {report_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python src/profile_extract.py <csv_or_snapshot_folder> <snapshot_date YYYY-MM-DD>")
    main(sys.argv[1], sys.argv[2])
