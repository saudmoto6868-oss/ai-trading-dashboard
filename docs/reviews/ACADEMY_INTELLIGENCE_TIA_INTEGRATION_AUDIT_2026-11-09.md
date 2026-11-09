# Academy Intelligence integration audit
Date: 2026-11-09
Status: reviewed against the TIA institutional operating model; no merge authorized by this audit.

## Executive decision

**Retain and integrate the Academy Intelligence work. Do not merge its branch as-is.** It contains valuable shared-knowledge, command snapshot and append-only meeting-journal capabilities, but its page/navigation integration conflicts with the already-merged TIA terminal and its current UI contains branding and observability issues.

The intended destination is the existing TIA institutional terminal / Trade Intelligence Center. Academy Intelligence becomes the shared knowledge and memory service; it is not a second parent product or a second top-level command center.

## Branch and scope

- Branch: `feat/academy-intelligence-core`
- Head observed during audit: `67b9d5cd09438320ad3d2e363a23c5d61450871a`
- Compared with `main`: 37 commits, 19 changed paths, no compare timeout.
- The branch changes `main.py`, `modules/workspace.py`, Workspace JavaScript/HTML, requirements, Academy documentation, and adds the Academy Intelligence store, center aggregator/UI, migration script and tests.
- No full tests, Streamlit AppTest, browser/mobile test, PostgreSQL deployment test or production verification is evidenced in the branch notes.

## Keep — valuable capabilities

1. `modules/academy_intelligence.py`: shared knowledge record schema, provenance, claim types, evidence grades, SQLite local adapter and optional PostgreSQL adapter.
2. Idempotent legacy Academy indexing that leaves original JSON content untouched.
3. Promotion gate that distinguishes source/agent agreement from empirical validation and requires sample size, out-of-sample evidence, costs and lookahead checks.
4. `modules/intelligence_center.py`: read-only aggregation from existing task, Lab, Research Hub and Academy sources.
5. `modules/intelligence_meeting.py`: append-only journal with typed entries and URL validation.
6. Workspace knowledge snapshot and tests as a possible read-only consumer, subject to review of its UI and performance behavior.

## Blockers and corrections before integration

### 1. Duplicate top-level route / navigation conflict — blocking
- The Academy branch adds `Trade Intelligence Center` at page index 12.
- The merged TIA terminal already occupies page index 12 in `main` through MR !3.
- A straight merge would collide with the same route index and produce duplicate or overwritten navigation behavior.
- Resolution: do not merge the branch's `main.py` navigation hunk. Integrate the center as a section/service within the existing TIA page, preserving all current page IDs and old specialist destinations until migration is tested.

### 2. Branding drift — blocking
- `modules/intelligence_center_ui.py` labels the institution `6868 Capital · Trade Intelligence Agency`.
- The current owner-approved hierarchy is Trade Intelligence Agency (TIA) as the institution, AI Trading Dashboard as a product, and 6868 as a quiet ownership signature only.
- Remove the visible `Capital` label and do not present 6868 as the parent-company title.

### 3. Silent source failures / false zeroes — high
- `modules/intelligence_center.py` uses `_safe(..., 0)` / `_safe(..., {})` and reports zero counts or empty snapshots when sources fail.
- `academy_intelligence.workspace_snapshot()` catches all exceptions and returns an empty list.
- The UI can therefore confuse unavailable/error with a genuine zero/empty state.
- Add per-source status objects (available, partial, unavailable, error), last-success timestamp and bounded error detail; never silently convert an exception to a real zero. Keep the UI read-only for the first integration.

### 4. Storage and deployment boundary — high
- SQLite is suitable for local development/tests only; ephemeral app storage is not an institution-wide durable database.
- PostgreSQL is only a selectable adapter. The branch does not prove that `DATABASE_URL`, the driver, migrations, connection pooling, backup/restore, permissions or multi-instance behavior are configured and tested.
- Do not call the journal or knowledge store production-durable until shared persistent storage is provisioned and verified.
- Review `psycopg[binary]` dependency and runtime compatibility before adoption.

### 5. Meeting-room source of truth — high
- The new journal stores append-only entries in the Academy database, while `docs/MEETING_ROOM.md`, `docs/WHITEBOARD.md`, `docs/TASK_QUEUE.md`, `PROJECT_STATUS.md` and GitLab issues remain existing project records.
- The UI currently says the new journal is empty and points to the old markdown archive, but there is no demonstrated migration/indexer connecting historical decisions/tasks.
- Keep old records untouched. Add explicit links/indexing and migration provenance; do not pretend a new empty journal contains the complete conversation history.

### 6. Knowledge-store correctness and governance — medium
- The schema is a useful starting point, not a complete institutional knowledge platform.
- Review status transitions and authorization before enabling accepted/rejected/archived mutations in the UI.
- Validate URL/source metadata, timestamps, language, size limits and structured details at ingestion boundaries.
- Ensure the promotion gate fails closed for malformed or missing evidence fields (including non-numeric sample_size) and does not equate the minimum sample-size threshold with profitability.
- Ensure legacy import counts are idempotent and report actual inserted/updated/skipped records rather than only iterated lessons.

### 7. Workspace integration — medium
- The branch modifies Workspace rendering and client payloads. Review payload size, HTML/JS contract, XSS-safe rendering and performance before merging.
- Keep this as a read-only knowledge widget; no changes to Radar, Spot or Technical Office behavior/options.
- Test empty, large, malformed and unavailable knowledge payloads.

## Integration map into the seven TIA functions

| Shared service / existing engine | TIA owner function | Integration contract |
|---|---|---|
| Academy knowledge registry | Strategy & Research Intelligence | Ingest, classify, cite, review and version knowledge |
| Research Hub snapshots | Strategy & Research Intelligence + Trading Intelligence orchestration | Read published snapshots; preserve each specialist engine |
| Lab / validation engines | Quant & Risk Intelligence | Lab remains the sole empirical validation authority |
| Meeting journal + task references | Trading Intelligence / institutional governance | Append-only decisions and work records; link to canonical task sources |
| Workspace knowledge widget | Product interface / shared services | Read-only projection of the shared knowledge registry |
| Radar, Spot, Technical Office | Their existing accountable desks | Read-only summaries only; no duplicated engine or altered controls |

## Required next changes

1. Create a TIA integration branch from current `main`; do not merge the Academy branch directly.
2. Port only the knowledge schema/store, append-only journal and tested read-only adapters after code review.
3. Adapt the center UI into the existing TIA terminal and remove duplicate navigation.
4. Correct branding and seven-function labels to the approved institutional model.
5. Replace silent exception fallbacks with explicit source-health states.
6. Add migrations/indexing for historical meeting/task records without altering originals.
7. Run focused unit tests, full test suite, Streamlit AppTest and browser/mobile checks.
8. Test PostgreSQL only after a persistent database is provisioned; otherwise label it development-only.
9. Open a focused MR with a file-by-file diff and explicit test evidence.

## Verification limits

This is a source and diff audit only. No branch merge, code execution, UI test, database provisioning or deployment was performed as part of this review.
