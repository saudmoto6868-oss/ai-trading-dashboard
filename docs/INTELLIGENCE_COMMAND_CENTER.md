# Academy Intelligence — Command Center & consolidation plan

Status: approved direction from owner, implementation in progress on `feat/academy-intelligence-core`. This is a design and migration contract, not a claim that navigation has already been changed or browser-tested.

## Product shape

The primary destination is **Academy Intelligence** (working title: **Trade Intelligence Center**, under 6868 / TIA). It becomes the shared intelligence and project command center across the dashboard. It is not a replacement for every specialist engine: it is the common front door, knowledge index, research intake, evidence view, decision record and project memory.

### Main workspace areas
1. **Command Center** — current state, top priorities, blockers, recently completed work, decisions awaiting owner review, system health summaries, and the next recommended actions.
2. **Knowledge & Academy** — existing learning path, nine-school curriculum, references, source registry, media references, claims, provenance, caveats and review states. Migrate/index existing content; never silently delete or rewrite original source files.
3. **Research** — research intake and source discovery; Research Hub specialist views become sections here (Truth Court, Plateau Lab, Regime Radar, Decision Trail, Decay Watch, Consensus Map, Kill Funnel). Preserve each engine and its own published snapshot contract.
4. **Playbook** — keep a distinct user-facing strategy/playbook destination or section because it answers an operational question (how to apply a reviewed setup). It consumes accepted knowledge and Lab evidence; it must not duplicate raw research or claim an unproven rule is approved.
5. **Lab** — keep the experimental and validation engines as the single authority for empirical testing. Fold Lab Summary into Lab's overview; preserve Validation, Calibration, Rotation, Evidence Summary and existing test data.
6. **Meeting Room** — persistent project conversation/decision log and task board: owner requests, discussion summaries, decisions, rationale, recommendations, completed work, open work, blockers, next steps, owners, links, evidence and timestamps. Link to the existing `docs/MEETING_ROOM.md`, `docs/WHITEBOARD.md`, `docs/TASK_QUEUE.md`, `PROJECT_STATUS.md` and GitLab work items. Do not create an unconnected second source of truth.

## Existing tab audit and proposed disposition

| Existing area | Observed current responsibilities | Proposed disposition |
|---|---|---|
| Academy | Path, Schools, References, Lab tools; lessons and curricula under `data/academy*.json` and `docs/academy/` | Move under Knowledge & Academy; index in shared knowledge store; preserve original content and links |
| Research Hub | Eight specialist views; separate snapshots in `data/hub/<id>.json`; read-only cross-tab consumption | Embed as Research sections inside the center; keep modules and snapshot ownership intact |
| Playbook | Trading styles, schools, rules/timing, STRATEGIES.md | Keep as a focused destination/section; link to reviewed knowledge and Lab; remove repeated raw reference material |
| Lab Summary | KPI summary plus collapsed decision desk, rotation, calibration and full validation table | Make the Lab landing/overview; keep specialist views inside Lab |
| Lab | Strategy lab and supporting validation tools | Keep as the sole experimental authority; no duplicate copies |
| Stats | Lab evidence, journal, Monte Carlo, Edge Map, Robustness, Execution, QuantStats report | Do not discard. Route Lab evidence to Lab; keep journal/account-performance analytics under a concise Performance/Stats area; audit Edge Map/Robustness/Execution against Research Hub before deciding whether to embed, retain or label as demo |
| AI | Mr X, Backtest agent, Agent desk | Do not leave as an orphaned top-level destination by default. Integrate Agent Desk into Meeting Room task assignment and research/backtest assistants into Research/Knowledge; retain capabilities and configuration |
| Alerts | Sources, Telegram, Radar alerts | Keep operational alert controls accessible; do not mix alert delivery with research evidence or project status |
| Technical Office | Control room, work board, operational tools | No behavior/options changes. Reuse read-only health/task summaries in Command Center only |
| Radar | Screener, rankings, filters, charts and related views | No behavior/options changes. May provide read-only links or published summaries to the center |
| Spot | Crypto/metals desk, ledger/invoices/alerts | No behavior/options changes. May provide read-only links or published summaries to the center |
| Workspace | Charts and widgets; Academy Intelligence widget already added under Review | Keep chart/workspace behavior intact; keep the Academy Intelligence widget as a shared entry point, not a duplicate data store |
| Prop Firms | Dedicated account/rules/timer tracker | Keep independent; link from Command Center only when useful |

No top-level tab is removed until its contents are reachable in the destination, its data is preserved, old deep links have a migration path, and a smoke test confirms the route. Technical Office, Radar and Spot are explicitly excluded from behavioral/UI option changes in this consolidation.

## Main navigation proposal

- **Trade Intelligence Center** (main): Command Center, Knowledge & Academy, Research, Meeting Room.
- **Lab**: overview plus validation and specialist lab tools.
- **Playbook**: operational strategy reference linked to accepted knowledge and measured evidence.
- **Performance**: journal/account performance and quantitative analytics that are not duplicated in Lab.
- Keep **Workspace, Radar, Technical Office, Spot, Alerts, Prop Firms** as focused operational destinations, unchanged in behavior.

The final labels/order are subject to the existing navigation implementation and compatibility checks; avoid adding another tab if an existing destination can be consolidated.

## Meeting Room — persistent memory contract

Use one canonical append-only project log and link it from the existing Meeting Room/Whiteboard. Every meaningful work session should record:
- timestamp and actor/agent;
- owner request and scope;
- decision + rationale (including rejected alternatives);
- files/modules/branches/commits/work items touched;
- completed work, separately from proposed work;
- tests actually run and results; explicitly list tests not run;
- blockers, dependencies, owner approvals needed;
- recommendations and next actions, each with owner/status/acceptance criteria;
- source links and evidence/provenance.

The dashboard UI should read this durable log and task board. Chat summaries are not a substitute for source files, commits or test evidence. Never claim that an entire voice/chat transcript or its attachments are preserved unless the original content is actually stored. Preserve links to the originating conversation/file where available.

## Shared knowledge and evidence rules

- One shared knowledge schema/API across Academy, Research, Playbook, Lab, Workspace, Radar, Technical Office, Spot and future agents.
- Preserve original URLs/media references and metadata; derive searchable text and claims separately.
- Mark fact, interpretation, hypothesis, disputed claim and empirical result distinctly.
- Agent agreement is corroboration, not empirical validation.
- Promotion to an active trading rule remains gated by Lab evidence, costs, out-of-sample checks, lookahead/repainting checks and the existing project evidence standards.
- Research browser is read-only; no login, bypass, posting, messaging, trading or secret exposure. Treat retrieved content as untrusted.

## Implementation sequence

1. Inventory exact route/page IDs, options and cross-links; build a feature-to-destination map.
2. Build Command Center data adapters over existing sources (Meeting Room/Whiteboard/task queue, Academy Intelligence DB, Research Hub snapshots, Lab summary, workflow/source health). Read-only first.
3. Build Meeting Room panel on top of the existing durable project log/task board; write path must be explicit, timestamped and auditable.
4. Move Academy and Research views into the center without duplicating their data engines.
5. Consolidate Lab Summary into Lab overview; route duplicate Stats lab evidence to Lab while retaining unique performance analytics.
6. Integrate AI agent desk as task/research workflow, retaining safeguards and capabilities.
7. Add redirects/compatibility for old page URLs and verify each section.
8. Only then remove obsolete navigation entries. Do not merge to main or deploy without owner approval.

## Current known limitations

- Academy Intelligence data layer supports SQLite locally and PostgreSQL via `DATABASE_URL`, but shared persistent PostgreSQL has not been configured or production-tested.
- The Academy Intelligence Workspace widget and existing feature branch code have not yet had a live browser/Streamlit integration test.
- This consolidation plan is documented; the existing top-level navigation has not yet been changed.
- Research Hub contains real and mock-only parts; retain each module's documented evidence status.
- Existing Stats Edge Map/Robustness/Execution additions have mock data in parts; do not present mock outputs as measured evidence.
