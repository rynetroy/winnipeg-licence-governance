# RACI Matrix: Winnipeg Business Licence Data

Version 0.1, November 4, 2026. Companion to [charter.md](charter.md). Personal project on public data. Not affiliated with or endorsed by the City of Winnipeg.

**R** = Responsible (does the work) · **A** = Accountable (owns the outcome, one per row) · **C** = Consulted · **I** = Informed

RACI is by **role**, not person. In this project one person holds the owner, steward and custodian roles (see the charter's note on separation of duties).

## Project layer

| Activity | Project owner | Project steward | Project custodian | Consumers |
|---|:---:|:---:|:---:|:---:|
| Pull a snapshot from the API | I | I | **A / R** | |
| Accept a snapshot (row count matches, metadata saved) | I | C | **A / R** | |
| Maintain the field mapping and canonical schema | I | **A / R** | C | |
| Write and update business definitions | **A** | R | | I |
| Classify field sensitivity | **A** | R | C | I |
| Define quality rules and thresholds | C | **A / R** | C | |
| Run quality checks on each snapshot | I | A | **R** | |
| Log issues with root cause and recommended fix | I | **A / R** | C | |
| Report issues upstream to the City | **A** | R | | |
| Approve a change to a standard (charter section 5) | **A** | R | C | I |
| Publish an output (report, README figure, dashboard) | **A** | C | R | I |
| Control access to raw snapshots | I | C | **A / R** | |

## Source layer (proposed, for the City)

These rows describe how the City could assign responsibility. They are recommendations based on gaps found in this project, not a description of current City practice.

| Activity | Source data owner (licensing area) | Source steward (proposed role) | Source publisher (open data portal) | Project (as a consumer) |
|---|:---:|:---:|:---:|:---:|
| Maintain licence records in the source system | **A** | R | | |
| Define fields, codes and statuses | **A** | R | C | I |
| Decide what is redacted, by licence family | **A** | R | C | I |
| Publish the dataset and its metadata | C | C | **A / R** | I |
| Publish a changelog for scope or structure changes | C | R | **A** | I |
| Correct records reported as wrong | **A** | R | I | C |
