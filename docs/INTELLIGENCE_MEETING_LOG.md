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
