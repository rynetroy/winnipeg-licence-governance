"""
load_snapshot.py

Reads a Business Licenses snapshot in either source format and returns one
standard table, so every later step (profiling, quality rules, pipeline)
works the same way no matter where the data came from.

    - Manual CSV export:  data/raw/Business_Licenses_20260404.csv
    - API snapshot:       data/raw/api_20261104/  (folder from ingest_api.py)

What "standard" means here:
    - column names from metadata/field_mapping.csv (canonical_name)
    - every value is text, blanks are "" (never NaN)
    - dates converted to ISO text, YYYY-MM-DD
    - all 13 columns present, even when the API left a field out

Personal project on public data. Not affiliated with or endorsed by the
City of Winnipeg.
"""

import json
from pathlib import Path

import pandas as pd

MAPPING_PATH = Path(__file__).resolve().parent.parent / "metadata" / "field_mapping.csv"
CSV_DATE_FORMAT = "%Y %b %d %I:%M:%S %p"   # "2023 May 10 12:00:00 AM"
API_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"   # "2023-05-10T00:00:00.000"
DATE_COLUMNS = ["issue_date", "expiry_date"]


def _mapping() -> pd.DataFrame:
    return pd.read_csv(MAPPING_PATH, dtype=str, keep_default_na=False)


def _to_iso(series: pd.Series, fmt: str) -> pd.Series:
    # Blank stays blank. A value that doesn't match the expected format
    # raises an error on purpose: a silent NaT would hide a real problem.
    parsed = pd.to_datetime(series.where(series != ""), format=fmt)
    return parsed.dt.strftime("%Y-%m-%d").fillna("")


def load_snapshot(path: str) -> pd.DataFrame:
    path = Path(path)
    mapping = _mapping()
    canonical = mapping["canonical_name"].tolist()

    if path.is_dir():
        # API snapshot folder. The API leaves out fields that are empty,
        # so reindex adds them back as blank columns.
        records = json.loads((path / "business_licenses.json").read_text(encoding="utf-8"))
        df = pd.DataFrame(records)
        df = df.rename(columns=dict(zip(mapping["api_field"], canonical)))
        df = df.reindex(columns=canonical).fillna("").astype(str)
        date_format = API_DATE_FORMAT
    else:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df = df.rename(columns=dict(zip(mapping["csv_header"], canonical)))
        df = df.reindex(columns=canonical).fillna("")
        date_format = CSV_DATE_FORMAT

    for col in DATE_COLUMNS:
        df[col] = _to_iso(df[col].str.strip(), date_format)
    return df


if __name__ == "__main__":
    import sys
    data = load_snapshot(sys.argv[1])
    print(data.shape)
    print(data.head(3).T)
