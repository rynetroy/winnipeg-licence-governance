# Data Quality Rules

Version 0.1, November 5, 2026. Personal project on public data. Not affiliated with or endorsed by the City of Winnipeg.

Each rule names **who is checked**, **what must be true** and a **threshold**, so it can pass or fail. Rules are owned by the project steward (charter section 4). Thresholds are this project's proposals and need owner approval before they are used for pass or fail.

Results come from the profile reports in `reports/`. Failures go to the [issue log](../governance/issue_log.md).

| ID | Dimension | Rule | Threshold (proposed) | Apr 2026 | Nov 2026 | Result (Nov) | Issue |
|---|---|---|---|---:|---:|---|---|
| QR-01 | Completeness | Every record must have an `issue_date` and an `expiry_date`. | 100% | 0 missing | 0 missing | Pass | |
| QR-02 | Validity | Every record must have `expiry_date` on or after `issue_date`. | 100% | 124 fail | 400 fail | Fail | I-003 |
| QR-03 | Timeliness | Records with status "Issued" must have `expiry_date` on or after the snapshot date. | 100% | 1,655 fail | 1 fail | Fail (1 record) | I-001 |
| QR-04 | Validity | `status` must be one of the values in the approved status list. | 100% | n/a | n/a | Not testable | I-007 |
| QR-05 | Uniqueness | No two rows may be identical in every field. | 0 duplicates (monitor only until a licence ID exists) | 4,082 (55.8%) | 2,158 (15.6%) | Monitor | I-002 |
| QR-06 | Validity | `neighbourhood_number` must be text in the form D.DDD. | 100% | 398 fail | 3 fail | Fail at source; handled in project | I-004 |
| QR-07 | Consistency | Each `folder_type` maps to exactly one `folder_description`. | 100% | NEEDS EVIDENCE | NEEDS EVIDENCE | Not yet computed | |
| QR-08 | Consistency | Each `neighbourhood_number` maps to exactly one `neighbourhood_name`. | 100% after codes are fixed as text | NEEDS EVIDENCE | NEEDS EVIDENCE | Not yet computed | |
| QR-09 | Completeness | `address` is blank only for rooming houses (LX). | 100% | NEEDS EVIDENCE | NEEDS EVIDENCE | Not yet computed | |

## Notes

- **Not testable** means the rule needs reference data the City does not publish (QR-04 needs a code list).
- **Not yet computed** rules are written but not yet in `profile_extract.py`. Adding them is the next step before the scorecard.
- A rule is not "acceptable quality" or "good enough". If it cannot fail, it is not a rule.
