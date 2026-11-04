# Decision Log

Every decision that changes a definition, standard, rule, source or what gets published. Decision rights are set in [charter.md](charter.md), section 4. Newest last.

| ID | Date | Decision | Why | Decided by | Affects |
|---|---|---|---|---|---|
| D-001 | 2026-11-04 | Business question narrowed to licensed activities: "Can the City's business licence data be trusted to count active licensed businesses downtown, what would it take, and what can it never tell you?" | The City licenses only a short list of activities, so the dataset cannot count businesses in general. | Project owner | README, all outputs |
| D-002 | 2026-11-04 | Keep the April 2026 CSV extract as the baseline; use newer pulls for timeliness and rerun tests. | April ties to the earlier downtown analysis; a second snapshot is needed to test timeliness and repeatability. | Project owner | Snapshot comparison |
| D-003 | 2026-11-04 | Ingest through the City's open data API into dated, immutable snapshots, with a row-count check before acceptance. | A repeatable pull replaces manual downloads, and each figure can be traced to one pull. | Project owner | `ingest_api.py`, charter standard 1 |
| D-004 | 2026-11-04 | Raw snapshots stay local and are not committed; Sensitive fields appear only as counts. | The November snapshot includes addresses and some trade names for personal services licences, which may relate to individuals. | Project owner | `.gitignore`, reports, charter standard 2 |
| D-005 | 2026-11-04 | November 2026 API snapshot is the primary dataset; April 2026 is the "before" baseline. | November is current and API-sourced; April shows how much the data changed. | Project owner | Quality rules, scorecard, README |
| D-006 | 2026-11-04 | Neighbourhood codes are stored and compared as text; dates as ISO `YYYY-MM-DD`. | Stored as numbers, codes lost trailing zeros (398 rows in April). Two sources used two date formats. | Project steward | `load_snapshot.py`, data dictionary, charter standards 4 and 5 |
| D-007 | 2026-11-04 | Working definitions: **downtown** = community characterization area "Downtown"; **active licence** = status "Issued", exact duplicates removed, expiry on or after the snapshot date. | The City publishes no definitions. These are explicit and testable, and they produce the downtown funnel. | Project owner | Downtown funnel, quality rules |
| D-008 | 2026-11-04 | Sensitivity scheme: Public or Sensitive per field, with family-level notes where the same field is sensitive for some licence families only. | Address, location and trade name carry different risk for personal services than for business premises. | Project owner | Data dictionary, Phase 2 access matrix |
| D-009 | 2026-11-04 | Charter covers two layers: a real charter for the project's copy of the data, plus clearly labelled proposed roles for the City. | The project cannot know the City's internal roles, but can recommend them from evidence. | Project owner | Charter, RACI |
