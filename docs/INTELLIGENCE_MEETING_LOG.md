# Intelligence Center — Meeting Room Log

Canonical working log for the Academy Intelligence / Trade Intelligence Center consolidation. The existing `docs/MEETING_ROOM.md` and `docs/WHITEBOARD.md` remain the project's established meeting/task records; this file is the focused log for this workstream and must be linked from them during the next safe documentation update.

## 2026-11-09 — Owner direction and baseline audit

### Owner request
- Consolidate overlapping dashboard tabs and improve the overall information architecture.
- Main tab should become the central home for the gathered Academy, Playbook, Status, Lab Summary, Research Hub and AI capabilities.
- Review Technical Office, Spot and Radar for useful components/options, but do not change their behavior or options.
- Main center must include its own Meeting Room that preserves the discussion, project nucleus, decisions, what happened, completed work, upcoming work, recommendations and direction.
- Do not lose project history or start future sessions without a durable handoff.

### Decisions recorded
1. Primary destination is Academy Intelligence / Trade Intelligence Center (working title); it is the common front door and project memory, not a duplicate of every specialist engine.
2. Keep Lab as the sole empirical testing authority; fold Lab Summary into its overview and preserve all specialist lab functions.
3. Keep Playbook focused on actionable strategy guidance; it consumes accepted knowledge and measured Lab evidence.
4. Embed Research Hub's specialist views in the main center while preserving each module and snapshot ownership.
5. Integrate AI Agent Desk into Meeting Room task assignment and place research/backtest assistants in the relevant Research/Knowledge workflows.
6. Reuse read-only summaries from Technical Office, Spot and Radar only; no behavioral or options changes to those tabs.
7. Preserve Alerts and Prop Firms as focused operational functions unless later evidence shows a safe, useful consolidation.
8. No old route/page is removed until all capabilities/data are migrated, links have a path, and smoke checks pass.
9. Existing docs/MEETING_ROOM.md, WHITEBOARD.md, TASK_QUEUE.md, PROJECT_STATUS.md and GitLab work items remain source records; this focused log is an index/workstream journal, not a claim to have copied full historical conversations.

### Baseline audit findings
- Main navigation currently defines: Workspace, Radar, Technical Office, Playbook, Stats, AI, Alerts, Academy, Lab Summary, Research Hub, Prop Firms, Spot.
- Academy has Path, Schools, References and Lab tools; content lives in data/academy*.json and docs/academy/.
- Research Hub has Command Center, Truth Court, Plateau Lab, Regime Radar, Decision Trail, Decay Watch, Consensus Map and Kill Funnel. Its data contract uses independent data/hub/<id>.json snapshots.
- Playbook contains By trading style, Schools, Rules & timing and Full document; it overlaps Academy schools and Lab summaries.
- Lab Summary repeats decision desk, rotation scan, calibration and validation lab as collapsed sections.
- Stats contains Lab evidence, My journal, Monte Carlo, Edge Map, Robustness, Execution and a QuantStats report; only unique performance analytics should remain outside Lab.
- AI contains Mr X, Backtest agent and Agent desk. Agent Desk already describes creating tasks in the Meeting Room, so it should be integrated rather than orphaned.
- Technical Office already has an operations control room and task board. Reuse read-only status summaries; do not change its interface or options.
- Spot and Radar are separate operating desks and are excluded from behavior/option changes.

### Work already present on branch before this audit
- Shared Academy Intelligence data layer, Workspace widget, schema/spec, SQLite/PostgreSQL adapter path and tests exist on feat/academy-intelligence-core.
- PostgreSQL is not configured or production-tested. Live browser/Streamlit tests have not run. No MR/merge/deploy has occurred.
- Research Hub includes a mixture of real and mock-only modules; documented caveats must remain visible.
- Some Stats additions (Edge Map / Robustness / Execution) include mock/demo data and must not be presented as empirical findings.

### Next execution steps
1. Build read-only Command Center adapters to existing task/status/research/lab/knowledge sources.
2. Inspect the existing Meeting Room and Whiteboard write mechanisms before wiring any UI write action.
3. Implement a durable Meeting Room panel with append-only entries and task links; avoid creating an isolated second source of truth.
4. Map and consolidate Academy + Research views without changing their engines.
5. Consolidate Lab Summary into Lab overview; audit unique Stats features and avoid dropping journal/performance functions.
6. Integrate AI Agent Desk into task workflow.
7. Preserve legacy routes until migrated and tested.
8. Record each implementation commit, actual tests and outstanding limits here.

### Verification status
- Source inspection only for this baseline. No UI navigation changes or live app tests have been performed as part of this audit.
- Branch: feat/academy-intelligence-core.
- Main branch untouched; no merge/deploy.


## 2026-11-09 — First implementation increment

### Implemented on feat/academy-intelligence-core
- Added `modules/intelligence_meeting.py`: append-only meeting entries using the shared Academy Intelligence database adapter; typed entries for owner requests, decisions, completed work, next steps, blockers, recommendations, meeting notes, agent reports and test results; bounded retrieval and summary.
- Added `modules/intelligence_center.py`: read-only command snapshot aggregating existing task board, Academy index/legacy lesson counts, Lab summary, published Research Hub snapshots and Meeting Room summary. Technical Office, Radar and Spot are explicitly represented as read-only sources.
- Added `tests/test_intelligence_meeting.py`: persistence/order, input validation and URL validation tests.

### Not yet done / verification
- Files were confirmed present on the feature branch via GitLab raw-file retrieval.
- Tests have NOT been executed. No syntax check, Streamlit AppTest, browser test or live deployment check has run.
- No main navigation change yet. The new aggregation/journal modules are not yet wired into the Streamlit page; next step is a safe UI integration and migration of existing meeting-room/whiteboard records without losing history.
- SQLite remains local-only; cross-instance durability still requires configured and tested persistent PostgreSQL via `DATABASE_URL`.


## 2026-11-09 — Additive Center UI + historical records

### Implemented
- Added `modules/intelligence_center_ui.py` with four sections: Command Center, Knowledge, Research snapshots and Meeting Room.
- Added page index 12, “Trade Intelligence Center”, to `main.py` and placed it near the start of the page selector. All existing page IDs and routes remain available; no old tab was removed.
- Added read-only rendering of the existing `docs/MEETING_ROOM.md`, `docs/WHITEBOARD.md`, this workstream log and the Center architecture contract inside the Meeting Room section. Original files are read from disk and are not overwritten.
- Corrected the Command Center task adapter to use the existing `modules.office_ui.load_tasks()` source instead of duplicating JSON parsing. Lab summary uses `modules.office_kpi.load()/summary()`; Academy legacy lesson count uses the actual `modules.academy.load()` API; Research Hub snapshots use the documented `hub_core.read(id)` contract.

### Review notes / outstanding
- The Meeting Room UI can append entries to the new journal. This journal is separate from the historical Markdown meeting log; both are visible, but no claim is made that every past chat transcript or attachment has been archived.
- SQLite is still local/dev persistence. Do not rely on cross-instance or production durability until a persistent PostgreSQL service is configured and tested.
- No tests, py_compile, Streamlit AppTest, browser test or deployment test have been executed. UI is code-integrated but not live-verified.
- Existing specialist routes remain unchanged; Technical Office, Radar and Spot behavior/options were not edited.
- No MR, merge or deployment.

### Next
1. Inspect task-board schema and add a safe, explicit task handoff from Meeting Room only after confirming current task write contract.
2. Review Research Hub snapshot presentation against actual snapshot payload shapes and add timestamps/empty-state clarity.
3. Run available automated tests and syntax checks in a real branch checkout/CI environment; report failures honestly.
4. Design persistent PostgreSQL setup separately; do not silently claim SQLite is production durable.


## 2026-11-09 — Meeting Room task proposal handoff
- Added a dedicated task-proposal form to Trade Intelligence Center → Meeting Room.
- Proposal fields: title, scope/outcome, priority, area, suggested owner and next action.
- Proposals are appended to the existing meeting journal as `recommendation` entries with metadata `kind=task_proposal` and status `awaiting_owner_review`; the UI lists pending proposals separately.
- **Safety boundary:** this does not write to `data/office_tasks.json`. Repository audit found that file is explicitly maintained by the site manager and no official task-write API exists. Formal board integration remains pending an owner-approved write contract.
- Also hardened optional source/link rendering against null values and corrected the queue metric label to “Active project tasks”.
- Runtime tests and live Streamlit verification remain outstanding.


### Owner review lifecycle for task proposals
- Added append-only review actions: “Approve for manual board entry” and “Decline proposal”.
- A review is a separate `decision` journal entry carrying `kind=task_proposal_review`, the original proposal ID, and an explicit `official_board_written=false` marker.
- The original proposal is never edited. The UI derives its current review state from the latest review event in the loaded journal window.
- Approval means permission for a human to enter the item in the official board; it does not write or assign a Technical Office task.
- Added a regression test covering proposal metadata, review linkage and the no-board-write invariant. Test execution is still pending because this GitLab project has no CI configuration file.
