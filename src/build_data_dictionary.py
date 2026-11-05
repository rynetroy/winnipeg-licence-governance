"""
build_data_dictionary.py

Builds the data dictionary by combining:
    - metadata/field_mapping.csv       names and types in each source
    - metadata/field_definitions.csv   meanings, rules, sensitivity, issues (written by hand)
    - one snapshot                     blank rates, distinct counts, observed values,
                                       and per-field checks (computed here)

Writing meanings by hand and computing numbers in code keeps the two honest:
the words explain, the numbers always match the data.

Usage:
    python src/build_data_dictionary.py data/raw/api_20261104 2026-11-04

Outputs:
    metadata/data_dictionary.csv   for tools (Power BI, a catalogue)
    metadata/data_dictionary.md    for people

Privacy: values of Sensitive fields are never listed, only counted.

Personal project on public data. Not affiliated with or endorsed by the
City of Winnipeg.
"""

import sys
from pathlib import Path

import pandas as pd

from load_snapshot import load_snapshot

METADATA = Path(__file__).resolve().parent.parent / "metadata"
MAX_LISTED_VALUES = 20   # list every value for code-like fields up to this many


def field_checks(df: pd.DataFrame, snapshot_date: str) -> dict:
    """Field-specific checks. Each returns a short, countable statement."""
    code = df["neighbourhood_number"]
    bad_codes = int(((code != "") & ~code.str.fullmatch(r"\d\.\d{3}")).sum())
    def rows(k: int) -> str:
        return f"{k:,} row" + ("" if k == 1 else "s")

    expired = int((df["expiry_date"] < snapshot_date).sum())
    stale = int(((df["status"] == "Issued") & (df["expiry_date"] < snapshot_date)).sum())
    multi_code = int((df.groupby("neighbourhood_name")["neighbourhood_number"].nunique() > 1).sum())
    multi_ward = int((df.groupby("neighbourhood_name")["electoral_ward"].nunique() > 1).sum())
    no_point = int(((df["address"] != "") & (df["location"] == "")).sum())
    blank_addr = df[df["address"] == ""]["folder_type"].value_counts()
    return {
        "issue_date": f"expiry before issue: {rows(int((df['expiry_date'] < df['issue_date']).sum()))}",
        "expiry_date": f"expired before {snapshot_date}: {rows(expired)}",
        "status": f"'Issued' but expired before {snapshot_date}: {rows(stale)}",
        "neighbourhood_number": f"not in D.DDD format (blanks excluded): {rows(bad_codes)}",
        "neighbourhood_name": f"names with more than one code: {multi_code}",
        "electoral_ward": f"neighbourhoods under more than one ward name: {multi_ward}",
        "trade_name": f"'(none)' placeholder: {rows(int((df['trade_name'] == '(none)').sum()))}",
        "address": "blank, by family: " + ", ".join(f"{k} {v:,}" for k, v in blank_addr.items()),
        "location": f"address present but no point: {rows(no_point)}",
    }


def observed(series: pd.Series, field: str, sensitivity: str) -> str:
    s = series[series != ""]
    if sensitivity == "Sensitive":
        return "(values not listed: sensitive)"
    if field in ("issue_date", "expiry_date"):
        return f"{s.min()} to {s.max()}"
    counts = s.value_counts()
    if len(counts) <= MAX_LISTED_VALUES:
        return "; ".join(f"{k} ({v:,})" for k, v in counts.items())
    return f"{len(counts)} distinct values (not listed)"


def main(snapshot_path: str, snapshot_date: str) -> None:
    df = load_snapshot(snapshot_path)
    mapping = pd.read_csv(METADATA / "field_mapping.csv", dtype=str, keep_default_na=False)
    defs = pd.read_csv(METADATA / "field_definitions.csv", dtype=str, keep_default_na=False)
    dictionary = mapping.merge(defs, left_on="canonical_name", right_on="field", how="left")

    missing = dictionary[dictionary["definition"].isna()]["canonical_name"].tolist()
    if missing:
        sys.exit(f"field_definitions.csv has no entry for: {missing}")

    checks = field_checks(df, snapshot_date)
    n = len(df)
    dictionary["blank_rows"] = [int((df[f] == "").sum()) for f in dictionary["canonical_name"]]
    dictionary["blank_pct"] = (dictionary["blank_rows"] / n * 100).round(1)
    dictionary["distinct_values"] = [int(df[f].nunique()) for f in dictionary["canonical_name"]]
    dictionary["observed_values"] = [
        observed(df[f], f, sens) for f, sens in zip(dictionary["canonical_name"], dictionary["sensitivity"])]
    dictionary["snapshot_check"] = [checks.get(f, "") for f in dictionary["canonical_name"]]
    dictionary["city_definition_published"] = "No"   # all 13 portal column descriptions are blank
    dictionary["snapshot"] = Path(snapshot_path).name

    columns = ["canonical_name", "csv_header", "api_field", "api_data_type", "definition",
               "format_rule", "sensitivity", "sensitivity_note", "blank_rows", "blank_pct",
               "distinct_values", "observed_values", "snapshot_check", "known_issues",
               "dq_dimensions", "city_definition_published", "snapshot"]
    dictionary = dictionary[columns]
    dictionary.to_csv(METADATA / "data_dictionary.csv", index=False)

    md = [
        "# Data dictionary: City of Winnipeg Business Licenses\n",
        f"Source: City of Winnipeg Open Data, dataset `d5k3-sfzx`. Figures computed from snapshot "
        f"`{Path(snapshot_path).name}` ({n:,} rows, snapshot date {snapshot_date}) by "
        "`src/build_data_dictionary.py`.\n",
        "**City definitions:** the portal publishes no description for any of the 13 fields. "
        "Definitions below are this project's working definitions, based on field names, "
        "observed values and the dataset description.\n",
"**Grain:** not documented by the City. What one row represents (a licence, a renewal, or a licence "
        "on a given date) is unknown, so exact duplicates cannot be judged as errors (decision D-011, issue I-008).\n",
        "**Metadata types in this project:** business (`field_definitions.csv`, `downtown_definitions.csv`), "
        "technical (`field_mapping.csv`), operational (`pull_metadata.json`, profile reports).\n",
        "**Sensitivity** (this project's proposed classification, not the City's):\n",
        "- **Public**: safe to publish row by row.",
        "- **Sensitive**: could identify an individual or a home. Publish aggregated counts only.\n",
        "Personal project on public data. Not affiliated with or endorsed by the City of Winnipeg.\n",
        "## Summary\n",
        dictionary[["canonical_name", "api_data_type", "sensitivity", "blank_pct",
                    "distinct_values", "dq_dimensions"]]
        .rename(columns={"canonical_name": "field", "api_data_type": "API type",
                         "blank_pct": "blank %", "distinct_values": "distinct",
                         "dq_dimensions": "quality dimensions"})
        .to_markdown(index=False),
        "\n## Fields\n",
    ]
    for _, r in dictionary.iterrows():
        md += [
            f"### `{r.canonical_name}`\n",
            f"{r.definition}\n",
            f"- **Names:** CSV `{r.csv_header}`, API `{r.api_field}` ({r.api_data_type})",
            f"- **Format rule:** {r.format_rule}",
            f"- **Sensitivity:** {r.sensitivity}" + (f": {r.sensitivity_note}" if r.sensitivity_note else ""),
            f"- **Blank:** {r.blank_rows:,} rows ({r.blank_pct}%)  |  **Distinct:** {r.distinct_values:,}",
            f"- **Observed:** {r.observed_values}",
        ]
        if r.snapshot_check:
            md.append(f"- **Check on this snapshot:** {r.snapshot_check}")
        md += [f"- **Known issues:** {r.known_issues}",
               f"- **Quality dimensions:** {r.dq_dimensions}\n"]

    (METADATA / "data_dictionary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print(f"\nWrote {METADATA / 'data_dictionary.csv'} and {METADATA / 'data_dictionary.md'}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python src/build_data_dictionary.py <snapshot> <snapshot_date YYYY-MM-DD>")
    main(sys.argv[1], sys.argv[2])
