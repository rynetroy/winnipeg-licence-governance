# Winnipeg Business Licence Data Governance

> **Status: work in progress (Phase 1 of 2).** Personal portfolio project on public data. Not affiliated with or endorsed by the City of Winnipeg.

**Question:** Can the City of Winnipeg's business licence open data be trusted to count active licensed businesses downtown, what would it take to make it trustworthy, and what can it never tell you?

## Findings so far

**1. The data can't count downtown businesses in general.** The City licenses only a short list of activities (used goods and precious metal dealers, rooming houses and similar). A restaurant or an office will never appear in this dataset. Any "downtown business count" built on it measures licensed activities only.

**2. In April 2026, a naive downtown count was about 18 times too high.**

| Downtown licences | April 4, 2026 | November 4, 2026 |
|---|---:|---:|
| Status = "Issued" | 621 | 234 |
| ...after removing exact duplicate rows | 322 | 197 |
| ...and not expired on the snapshot date | **34** | **196** |

In April, 1,655 records across the city still said "Issued" after their expiry date. By November that number was 1.

**3. The dataset changed a lot between the two snapshots, with no visible changelog.**

- History now goes back to 2010 (April started at 2021).
- Two more licence families and ten more licensed activities appear.
- Exact duplicate rows fell from 55.8% to 15.6%. Personal sales duplicates went from 3,585 rows to 0.
- All 436 matched records that were "Issued" but expired in April now show a closed or ceased status.

The same dataset ID gave a very different answer seven months apart. Whether the data can be trusted depends on the day it was pulled, and nothing on the portal documents the changes.

**Not yet proven (NEEDS EVIDENCE):**
- Why the April duplicates existed. With no licence number in the data, an exact duplicate can't be confirmed as an error. Rooming house addresses are redacted, so separate rooming houses can look identical.
- Whether the remaining rooming house duplicates are errors or distinct licences.

## How it works

```
City open data API ──► ingest_api.py ──► dated raw snapshot (local only)
                                               │
                     load_snapshot.py  ◄───────┘  (also reads the April CSV)
                           │
         ┌─────────────────┴──────────────────┐
  profile_extract.py                 compare_snapshots.py
         │                                    │
  reports/profile_*.md            reports/compare_*.md
```

- `src/ingest_api.py` pulls the full dataset from the City's API, checks the row count, and saves a dated snapshot that is never overwritten.
- `src/load_snapshot.py` reads either the API snapshot or a CSV export into one standard format, using `metadata/field_mapping.csv`.
- `src/profile_extract.py` profiles one snapshot.
- `src/compare_snapshots.py` compares two snapshots.
- `src/build_data_dictionary.py` builds the [data dictionary](metadata/data_dictionary.md) from hand-written definitions plus figures computed from a snapshot.

Reports show counts only. Raw data is not stored in this repo; see [data/README.md](data/README.md).

## Run it

```
pip install -r requirements.txt
python src/ingest_api.py
python src/profile_extract.py data/raw/api_YYYYMMDD YYYY-MM-DD
```

## Roadmap (DAMA-DMBOK knowledge areas)

| Deliverable | Knowledge area | Status |
|---|---|---|
| Profiling and snapshot comparison | Data Quality | Done |
| API ingestion with immutable snapshots | Data Integration | Done (first version) |
| Data dictionary | Metadata Management | Done |
| Governance charter and RACI | Data Governance | Next |
| Quality rules, scorecard, issue log | Data Quality | Planned |
| Business glossary and lineage diagram | Metadata Management | Phase 2 |
| Reference codes and golden record matching | Reference & Master Data | Phase 2 |
| Field classification and access matrix | Data Security | Phase 2 |
| Conceptual, logical and physical model | Data Modeling & Design | Phase 2 |
| Power BI quality scorecard and insight page | DW & BI | Phase 2 |

## Source

City of Winnipeg Open Data, Business Licenses (dataset `d5k3-sfzx`), data.winnipeg.ca. Snapshots: April 4, 2026 (CSV export) and November 4, 2026 (API pull).
