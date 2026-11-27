# Academy Intelligence Recovery Audit

**Audit date:** 2026-11-10  
**Project:** `6868-group/ai-trading-dashboard` (GitLab Project ID `88622818`)  
**Audit branch:** `audit/academy-intelligence-recovery`  
**Base:** `main` at `8e8089482336eefb71f7c66080921df75748f476`  
**Scope:** Recovery and verification only. No application code, page routing, Workspace bundle, specialist engine, production data, or credentials changed.

## 1. Executive result

The project is an existing implementation. PAGE 17 and the Academy Core are already present on `main`; the original Workspace Academy widget implementation is present on the older feature branch but is not ported to current `main`. The next implementation candidate is a narrowly scoped Workspace widget port, but it must follow the source-part/bundle regeneration workflow and be tested against the current Workspace.

The latest observed `main` SHA is the handoff SHA. PAGE 17 remains separate from TIA PAGE 12. The Academy database layer has SQLite support and a PostgreSQL adapter, but shared persistent storage is not proven: `requirements.txt` on main does not include psycopg, no `DATABASE_URL` configuration or PostgreSQL connection test was found.

No current-main test pass is established. The visible MR !49 pipeline failed with zero jobs; the latest visible main pipeline is also failed with zero jobs and references an older SHA than current main. Do not treat either as a test run.

## 2. GitLab baseline

- Project default branch: `main`.
- Current observed main SHA: `8e8089482336eefb71f7c66080921df75748f476`.
- Older source branch: `feat/academy-intelligence-core` at `3aa2f4271f5307d75a89f465391e871148cc4d68`.
- MR !49 is merged. Title: "Trade Intelligence Center as PAGE 17 (renumbered port of !27)".
- MR !49 merge commit: `90ec0c2d6c99f235c7484fcbb0b2c0969348735f`.
- MR !49 changed seven paths: `modules/academy_intelligence.py`, `modules/intelligence_center.py`, `modules/intelligence_center_ui.py`, `modules/intelligence_meeting.py`, `tests/test_academy_intelligence.py`, `tests/test_intelligence_meeting.py`, and `main.py`.
- MR !49 explicitly did not port the Workspace Academy widget, CI changes, stale i18n changes, or the psycopg dependency.
- MR !27 was superseded by !49; do not use !27 as the integration baseline.
- MR !52 ("Draft: TIA recovery archive and 30-image index") is still open and unmerged. It contains `data/tia_image_research_index.json`, `docs/TIA_IMAGE_RESEARCH_INDEX.md`, `docs/AI_TRADING_DASHBOARD_CONVERSATION_ARCHIVE.md`, and `docs/TIA_RECOVERY_PROMPT.md`. It is a separate documentation/archive increment, not part of the Academy widget port.
- MR !41 is merged but concerns Options restoration and overlap documentation; its changed `modules/tia_workspace.py` is outside this audit's implementation scope.

## 3. Current-main component matrix

| Component | Previous plan | Actual main status | Test evidence | Remaining work | Priority |
|---|---|---|---|---|---|
| Academy Core | One shared knowledge registry and retrieval layer | Present in `modules/academy_intelligence.py` | Test file exists; no current-main run established | Review schema, constraints, transactions, migrations and governance | P1 |
| Legacy import | Conservative, repeatable import of Academy lessons/references | Import functions and test coverage present | No current-main run established | Verify idempotency and owner-review preservation | P2 |
| Workspace Academy widget | Global widget under Workspace + Widget > Review | Not present on current main Workspace code/bundle | No browser test | Selective port from old branch; regenerate bundle from current source parts | P1 |
| PAGE 17 | Command Center, Knowledge, Research, Meeting Room | Present and routed as PAGE 17 under Learn & AI | No current UI/browser evidence | Visual, functional, navigation and responsive QA | P1 |
| TIA PAGE 12 | Preserve existing TIA | Existing route remains PAGE 12; PAGE 17 is additive | No regression test evidence | Run PAGE 12 regression after any port | P1 |
| Meeting Room | Append-only log and owner-reviewed proposals | Present in `modules/intelligence_meeting.py` and PAGE 17 UI | Tests exist; no current-main run established | Verify persistence, append-only semantics and no official task-board writes | P1 |
| Research Hub | Read-only published snapshots with provenance | Partial adapters in Intelligence Center | No live-data proof | Verify each module source, freshness, sample size and evidence labels | P2 |
| Playbook | Only reviewed procedures linked to Lab evidence | Existing Playbook remains separate; cross-link not complete | Not established | Link versioned rules to Academy records and Lab evidence | P2 |
| Shared PostgreSQL | Persistent shared database | Adapter code only; main requirements lacks psycopg | No connection test | Driver, owner-managed secret, migration, backup, concurrency and access tests | P1 |
| Research agents | Gemini Free + owner-provided Grok specialists + curator | Workflow specification only | No provider execution proof | Verify provider availability and actual run logging; no paid service without approval | P2 |
| Cross-section access | Shared read-only knowledge for authorized consumers | Not complete | Not established | Add explicit consumer APIs incrementally without changing specialist engines | P2 |
| 30-image archive | Preserve originals and index content | 30 original JPGs and ZIP found in Library; index is on unmerged !52 | Binary files confirmed by Library listing; not a strategy-validation test | Review !52 separately and preserve source mapping | P2 |
| Video research outputs | Reuse prior extracted tables/setups | Original tables are not recovered in this audit | No verifiable source table found | Recover the exact prior conversation outputs; do not retranslate videos by default | P1 |

## 4. Workspace widget recovery findings

The old branch comparison contains a concrete implementation sequence:
- `5cf1d910`: add Academy Intelligence panel view.
- `eb2591e6`: add Academy to the Workspace widget menu.
- `f9f1d6c9`: add Arabic/English labels.
- `23f56c56`: pass Academy snapshot into the iframe payload.
- `e7722d08` and `9438cb90`: regenerate the bundled Workspace HTML.
- `574506a2`: add Academy panel behavior to the panel class/registry.
- `72404d6a` and `6bc73361`: PostgreSQL adapter work and database-session cleanup.

Relevant old-branch paths include:
- `modules/workspace.py` — adds `workspace_snapshot()` output to `CFG.academy`.
- `modules/ws/22_panels.js` — adds `build_academy()`.
- `modules/ws/26_snap.js` — adds Academy to the Review widget group and its short code.
- `modules/workspace_app.html` — generated bundle containing the old panel.
- The old branch also changes `requirements.txt` to add psycopg.

Current-main checks found no `build_academy` in `modules/ws/22_panels.js` or `modules/workspace_app.html`, and no Academy snapshot injection in `modules/workspace.py`. The current main source parts exist under `modules/ws/`. The port must not copy old generated HTML or replace current source parts. The exact widget registration/restore path must be reviewed in the current Panel and saved-layout implementation before editing.

## 5. PAGE 17 and Meeting Room findings

Current UI source: `modules/intelligence_center_ui.py`. It renders four tabs: Command Center, Knowledge, Research and Meeting Room. It contains a dark navy/teal visual header, KPI cards, a research trial chart, Knowledge search/status controls and Meeting Room proposal review controls.

Current data adapter: `modules/intelligence_center.py`. It aggregates read-only task/Lab/Research Hub snapshots and counts Academy records.

Meeting journal: `modules/intelligence_meeting.py`. It stores entries through Academy DB sessions and exposes proposal/review queries. The test file includes append/list ordering, owner review, 505-proposal lifecycle and URL validation cases.

The UI labels Decision Trail and Decay Watch as `MOCK ONLY` pending real `signal_log`. Preserve this label. Do not treat a snapshot as live data. The current code has visual components, but no screenshot, preview URL, browser test, mobile test or PAGE 12 + PAGE 17 runtime regression evidence was found.

## 6. Storage review

Current `modules/academy_intelligence.py`:
- SQLite is the default/local adapter; `ACADEMY_DB_PATH` controls its path.
- `DATABASE_URL` selects a lazy-imported psycopg PostgreSQL adapter.
- `initialize()` creates tables and indexes using `CREATE TABLE IF NOT EXISTS`.
- `db_session()` closes sessions in a finally block.
- Knowledge records and review events are separate tables.
- Review decisions update record status and append a review event; administrative acceptance does not itself upgrade evidence grade.

Current `requirements.txt` does not include `psycopg[binary]`. No configured `DATABASE_URL`, real PostgreSQL endpoint, migration version table, backup/restore evidence, multi-instance concurrency test or access-control test was observed. Therefore PostgreSQL readiness is code-level only, not production readiness.

## 7. Issues

All five requested work items remain open in GitLab at audit time:
- #3 — Shared Academy knowledge access and safe web research browser for agents.
- #4 — Academy Core: shared knowledge schema, media registry and retrieval index.
- #5 — Workspace Academy Intelligence Hub widget and cross-section integration.
- #7 — Multi-agent research, curation and validation pipeline.
- #8 — Academy evidence governance, strategy playbooks and Lab validation standards.

Issue #5's history records the widget implementation on the old branch and explicitly says no Python, browser/Playwright or Streamlit test was run. Issue #3 records the 30-image archive as prepared locally/Library, not confirmed as uploaded to Notion or committed to GitLab at that time. Do not close these issues based solely on MR !49.

## 8. Images, videos and conversation recovery

The Library contains:
- `/TIA Image Research/Originals/TIA-Reference-01.jpg` through `TIA-Reference-30.jpg`.
- `/AI_Trading_Dashboard_Reference_Images_2026-11-09.zip`.
- Video files including `4766.mp4` and `Screen_Recording_20261109_052529_Threads.mp4`.
- `نسخة_المحادثة_المتاحة_جزئية.pdf`, a two-page partial transcript that explicitly says it is not the complete original conversation.

The unmerged !52 image index classifies #06 as Footprint/Order Flow; #03–05 as Auction/Volume Profile; #23, #24, #27, #29 and #30 as circular/radial references; #28 as Gann Fan; #26 as Tesla-number research; and confirms no dedicated Heatmap image in the 30-image set. These are educational/reference classifications, not evidence of profitable strategies.

The requested old tables and structured setup results from more than nine videos were not found in the recovered conversation context or the current-main repository files inspected. This remains a recovery blocker. Do not invent setup names, entry rules, win rates or source citations, and do not repeat video extraction unless the owner asks for it after recovery options are exhausted.

## 9. CI and test evidence

- MR !49 pipeline `3048182405`: failed, zero jobs; no test execution.
- Latest visible main pipeline `3048674917`: failed, zero jobs; pipeline SHA `4ba86a1da43d848ebb06df8db66e2d1f5a2a796c`, which is older than current main SHA `8e8089482336eefb71f7c66080921df75748f476`.
- The current `.gitlab-ci.yml` defines MR test jobs, but the observed zero-job pipeline does not prove they ran.
- `mr_tests` is configured with `allow_failure: true`; this must not be represented as a passing quality gate.
- No current-main `compileall`, focused pytest, Streamlit import/startup, navigation, browser, saved-layout, Arabic/English, PostgreSQL, or PAGE 12 regression result was available to this audit.

## 10. Not changed

This audit did not modify:
- `main`.
- TIA PAGE 12 or `modules/tia_workspace.py`.
- Radar, Spot or Technical Office behavior.
- Workspace source parts or generated bundle.
- `data/office_tasks.json`.
- secrets, provider credentials, external services or trading accounts.

No MR was merged and no deployment was performed.

## 11. Recommended next sequence

1. Review this audit and keep it as the baseline record.
2. Inspect current Workspace Panel registry, menu dispatch, saved-layout restoration, I18n, iframe CFG and bundle generation scripts.
3. Port only the Academy panel and snapshot bridge onto a fresh branch from the then-current main; do not port old generated HTML.
4. Add focused tests for menu creation, saved-layout restoration, bilingual labels, search/filter behavior, HTTP(S) source links and shared Academy Core data.
5. Run compileall and focused Academy/Meeting Room tests in a real runner or reproducible local checkout; inspect actual job logs.
6. Run Streamlit import/startup and PAGE 12/PAGE 17 smoke checks, then browser/mobile checks and capture a real screenshot/preview.
7. Handle PostgreSQL as a separate owner-configured storage task; do not claim shared persistence before a real connection and multi-instance test.
8. Recover prior video-derived tables from original conversation records or existing artifacts; do not redo video analysis by default.
9. Update Issues #3/#4/#5/#7/#8 with evidence-based progress only. Leave them open until their acceptance criteria are met.

## 12. Acceptance guardrails

- One canonical Academy knowledge source; no per-page database copies.
- Research/Academy acceptance is not empirical strategy validation.
- Lab alone owns empirical testing and evidence promotion.
- No untested or disputed rule becomes a live signal or Playbook operating rule.
- No unverified Gemini/Grok/other-agent execution claims.
- No mock/snapshot presented as live.
- No automated trading or order placement.
- No merge or deploy without explicit owner approval.
