# Issue Log

Version 0.1, November 5, 2026. Companion to [charter.md](charter.md) and [quality/quality_rules.md](../quality/quality_rules.md). Personal project on public data. Not affiliated with or endorsed by the City of Winnipeg.

Every data issue found in a snapshot is recorded here before it is investigated. Workflow: **identify and record → assess impact and priority → investigate root cause → assign → resolve or report upstream → verify → close → monitor**. Escalation: project steward → project owner → source data owner (the City), reported upstream.

Issues at the source cannot be fixed by this project. For those, "resolution" means the project's workaround plus a recommendation to the City (charter section 7).

| ID | Found | Snapshot | Description | Affected data | Rule | Impact | Priority | Owner | Status | Root cause | Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| I-001 | 2026-11-04 | 2026-04-04 | 1,655 records had status "Issued" after their expiry date. | `status`, `expiry_date`, all families | QR-03 | Naive "active" counts overstated; Downtown planning area count fell from 322 to 34 once expiry was applied. | High | Project steward | Monitoring | Statuses not updated after expiry at the source (NEEDS EVIDENCE). | Project rule: an active licence must not be expired on the snapshot date (D-007). November shows 1. Keep monitoring each snapshot. |
| I-002 | 2026-11-04 | both | Exact duplicate rows: 4,082 (55.8%) in April, 2,158 (15.6%) in November. | All fields | QR-05 | Counts inflated unless duplicates are removed. | High | Project steward | Open | Unknown. No licence ID, and redacted rooming house addresses can make separate licences look identical (NEEDS EVIDENCE). | Remove exact duplicates for counts, but do not label them errors. Recommend a unique licence ID to the City. |
| I-003 | 2026-11-04 | both | `expiry_date` earlier than `issue_date`: 124 rows in April, 400 in November. | `issue_date`, `expiry_date` | QR-02 | Validity checks and duration measures unreliable for these rows. | Medium | Project steward | Open | Unknown (NEEDS EVIDENCE). | Investigate which families and activities are affected before deciding a treatment. |
| I-004 | 2026-11-04 | both | Neighbourhood codes lost trailing zeros (for example 3.17 instead of 3.170): 398 rows in April, 3 in November. | `neighbourhood_number` | QR-06 | Joins and group-bys by code split one neighbourhood in two. | Medium | Project steward | Resolved (project) | Published as a number at the source. | Codes stored as text; joins use normalized names (D-006). |
| I-005 | 2026-11-04 | both | No field definitions, code lists, licence ID, redaction policy or changelog are published. | Whole dataset | n/a | Same dataset ID gave very different answers seven months apart, with nothing documenting why. | High | Project owner | Reported upstream: not yet (NEEDS EVIDENCE) | Metadata not maintained at the source. | Working definitions in `metadata/`; six recommendations in charter section 7. |
| I-006 | 2026-11-04 | both | Licence data's "Downtown" planning area is much wider than the CentrePlan 2050 downtown. | `community_characterization_area` | n/a | "Downtown" figures can be off by a factor of about 40 (196 vs 5 active in November). | High | Project owner | Resolved (project) | Planning area and plan boundary are different definitions. | Two named definitions (D-010); report the planning area as "downtown and surrounding neighbourhoods". |
| I-007 | 2026-11-04 | 2026-11-04 | Status values carry an undocumented "(L)" suffix (for example "Closed (L)"). | `status` | QR-04 | Status meaning cannot be confirmed. | Low | Project steward | Open | No code list published (NEEDS EVIDENCE). | Record observed values in the reference list (Phase 2); ask the City. |
| I-008 | 2026-11-05 | n/a | The grain (what one row represents) is not documented. | Whole dataset | n/a | Duplicates cannot be judged as errors or separate records until the grain is known. | High | Project owner | Open | No data model or documentation at the source. | Recorded as unknown in the data dictionary (D-011). Phase 2 modeling starts here. |

## How to add an issue

1. Add a row with the next ID, the date found and the snapshot.
2. Link the quality rule that caught it, if any.
3. State impact in terms of the business question (downtown active licence counts).
4. Leave root cause as NEEDS EVIDENCE until it is shown.
5. Close only after the fix is verified on a new snapshot.
