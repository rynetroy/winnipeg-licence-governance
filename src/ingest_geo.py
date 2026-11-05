"""
ingest_geo.py

Pulls a map (boundary) dataset from the City of Winnipeg open data portal
as GeoJSON and saves it as a dated, untouched snapshot. Same rules as
ingest_api.py: check the row count, save metadata, never overwrite.

Usage:
    python src/ingest_geo.py sbkq-35fn neighbourhoods

    first argument:  the portal's dataset ID
    second argument: a short name for the folder and file

Output:
    data/raw/geo_<name>_YYYYMMDD/<name>.geojson
    data/raw/geo_<name>_YYYYMMDD/pull_metadata.json

Optional app token, never stored in this file: SOCRATA_APP_TOKEN.

Personal project on public data. Not affiliated with or endorsed by the
City of Winnipeg.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

DOMAIN = "https://data.winnipeg.ca"
TIMEOUT = 60
LIMIT = 50000   # boundary datasets are small; one request should hold them all


def headers() -> dict:
    token = os.environ.get("SOCRATA_APP_TOKEN")
    return {"X-App-Token": token} if token else {}


def get(url: str, params: dict | None = None):
    resp = requests.get(url, params=params, headers=headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def main(dataset_id: str, name: str) -> None:
    pulled_at = datetime.now(timezone.utc)
    out_dir = Path("data/raw") / f"geo_{name}_{pulled_at:%Y%m%d}"
    if out_dir.exists():
        sys.exit(f"{out_dir} already exists. Snapshots are never overwritten.")

    base = f"{DOMAIN}/resource/{dataset_id}"
    print(f"Pulling {base}.geojson")
    expected = int(get(f"{base}.json", {"$select": "count(*) AS n"})[0]["n"])
    print(f"API reports {expected} features")
    geo = get(f"{base}.geojson", {"$limit": LIMIT})
    received = len(geo.get("features", []))

    try:
        meta = get(f"{DOMAIN}/api/views/{dataset_id}.json")
        dataset_meta = {
            "name": meta.get("name"),
            "description": meta.get("description"),
            "category": meta.get("category"),
            "rows_updated_at": datetime.fromtimestamp(meta["rowsUpdatedAt"], timezone.utc).isoformat()
            if meta.get("rowsUpdatedAt") else None,
            "columns": [{"field_name": c.get("fieldName"), "display_name": c.get("name"),
                         "data_type": c.get("dataTypeName")} for c in meta.get("columns", [])],
        }
    except requests.RequestException as err:
        dataset_meta = {"error": str(err)}

    out_dir.mkdir(parents=True)
    (out_dir / f"{name}.geojson").write_text(json.dumps(geo), encoding="utf-8")
    (out_dir / "pull_metadata.json").write_text(json.dumps({
        "dataset_id": dataset_id,
        "endpoint": f"{base}.geojson",
        "pulled_at_utc": pulled_at.isoformat(),
        "rows_expected": expected,
        "rows_received": received,
        "complete": received == expected,
        "dataset_metadata": dataset_meta,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved {received} features to {out_dir}")
    if received != expected:
        print(f"WARNING: expected {expected} but received {received}. Treat as incomplete.")
    if received:
        print("Fields on each feature:", sorted(geo["features"][0].get("properties", {}).keys()))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python src/ingest_geo.py <dataset_id> <short_name>")
    main(sys.argv[1], sys.argv[2])
