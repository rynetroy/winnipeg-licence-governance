"""
ingest_api.py

Pulls the full City of Winnipeg Business Licenses dataset (d5k3-sfzx) from
the open data portal's Socrata API and saves it as a dated, untouched
snapshot. Analysis never reads the live API; it reads these snapshots, so
every number can be traced back to one specific pull.

Usage:
    python src/ingest_api.py

Output (one folder per pull, named by the UTC pull date):
    data/raw/api_YYYYMMDD/business_licenses.json   every record, as returned
    data/raw/api_YYYYMMDD/pull_metadata.json       when, where, how many

Optional: set an app token to avoid throttling. Never put it in this file.
    Windows (PowerShell):  $env:SOCRATA_APP_TOKEN = "your-token"
    Mac / Linux:           export SOCRATA_APP_TOKEN="your-token"

Personal project on public data. Not affiliated with or endorsed by the
City of Winnipeg.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

DATASET_ID = "d5k3-sfzx"
DOMAIN = "https://data.winnipeg.ca"
RECORDS_URL = f"{DOMAIN}/resource/{DATASET_ID}.json"   # SODA2 records endpoint
METADATA_URL = f"{DOMAIN}/api/views/{DATASET_ID}.json"  # dataset-level metadata
PAGE_SIZE = 1000   # the portal's default limit; we page through instead of raising it
TIMEOUT = 60       # seconds per request


def headers() -> dict:
    token = os.environ.get("SOCRATA_APP_TOKEN")
    return {"X-App-Token": token} if token else {}


def get_json(url: str, params: dict | None = None):
    resp = requests.get(url, params=params, headers=headers(), timeout=TIMEOUT)
    resp.raise_for_status()  # stop loudly on 4xx/5xx instead of saving an error page
    return resp.json()


def expected_row_count() -> int:
    # Ask the API to count rows itself, so we can check the pull is complete.
    result = get_json(RECORDS_URL, {"$select": "count(*) AS n"})
    return int(result[0]["n"])


def fetch_all_records() -> list[dict]:
    records, offset = [], 0
    while True:
        page = get_json(RECORDS_URL, {
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$order": ":id",  # stable sort, so pages don't overlap or skip rows
        })
        records.extend(page)
        print(f"  fetched {len(records)} rows")
        if len(page) < PAGE_SIZE:
            return records
        offset += PAGE_SIZE


def fetch_dataset_metadata() -> dict:
    # Owner, last-updated timestamps, column descriptions. Not critical:
    # if this call fails, the pull still counts, and we record the failure.
    try:
        meta = get_json(METADATA_URL)
    except requests.RequestException as err:
        return {"error": str(err)}

    def ts(key):
        value = meta.get(key)
        return datetime.fromtimestamp(value, timezone.utc).isoformat() if value else None

    return {
        "name": meta.get("name"),
        "description": meta.get("description"),
        "category": meta.get("category"),
        "attribution": meta.get("attribution"),
        "rows_updated_at": ts("rowsUpdatedAt"),
        "view_last_modified": ts("viewLastModified"),
        "columns": [
            {
                "field_name": c.get("fieldName"),
                "display_name": c.get("name"),
                "data_type": c.get("dataTypeName"),
                "description": c.get("description"),
            }
            for c in meta.get("columns", [])
        ],
    }


def main() -> None:
    pulled_at = datetime.now(timezone.utc)
    out_dir = Path("data/raw") / f"api_{pulled_at:%Y%m%d}"
    if out_dir.exists():
        sys.exit(f"{out_dir} already exists. Snapshots are never overwritten; "
                 "delete or rename it yourself if you really want to re-pull today.")

    print(f"Pulling {RECORDS_URL}")
    expected = expected_row_count()
    print(f"API reports {expected} rows")
    records = fetch_all_records()
    dataset_meta = fetch_dataset_metadata()

    complete = len(records) == expected
    out_dir.mkdir(parents=True)
    (out_dir / "business_licenses.json").write_text(
        json.dumps(records, ensure_ascii=False), encoding="utf-8")
    (out_dir / "pull_metadata.json").write_text(json.dumps({
        "dataset_id": DATASET_ID,
        "endpoint": RECORDS_URL,
        "pulled_at_utc": pulled_at.isoformat(),
        "rows_expected": expected,
        "rows_received": len(records),
        "complete": complete,
        "used_app_token": bool(os.environ.get("SOCRATA_APP_TOKEN")),
        "dataset_metadata": dataset_meta,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved {len(records)} rows to {out_dir}")
    if not complete:
        print(f"WARNING: expected {expected} rows but received {len(records)}. "
              "Treat this snapshot as incomplete.")


if __name__ == "__main__":
    main()
