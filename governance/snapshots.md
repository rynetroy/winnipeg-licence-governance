# Snapshot Register

Every snapshot accepted into the project, as required by charter standard 1 and decision D-003. Raw records stay local (D-004); this register is the public record that each one existed and was complete.

| Snapshot | Pulled | Method | Rows expected | Rows received | Complete | SHA-256 / evidence | Accepted by | Used for |
|---|---|---|---:|---:|---|---|---|---|
| `Business_Licenses_20260404.csv` | 2026-04-04 | Manual CSV export (earlier project) | n/a | 7,313 | Not checkable (no API count) | `45C90B0BB569EA5E1D63442FAE7F1CBE3EE99B24265B383FBAE92D7F4E6F341E` | Project custodian | Baseline (D-002) |
| `api_20261104` | 2026-11-04 (21:31 UTC) | API pull, `src/ingest_api.py` | 13,825 | 13,825 | Yes | `pull_metadata.json` committed under `governance/pull_metadata/` (D-014) | Project custodian | Primary dataset (D-005) |
| `Neighbourhoods_20261104.csv` | 2026-11-04 | Manual CSV export | n/a | 237 | n/a | `9AD3531E484B789627B8369193997EC5FD149A6394D5370F276167273F8ADF1F` | Project custodian | Map join |

## Retention

Raw snapshots are kept locally for the life of the project and are never edited. A snapshot is retired only by a decision log entry, and its row in this register stays.
