# ChatGPT / TIA session record — 2026-11-10 — Shared platform knowledge and recovery

## Purpose of this record
Preserve the complete actionable state of the 2026-11-10 conversation so a new ChatGPT conversation or another authorized project contributor can resume without relying on the previous chat. This is a factual engineering handoff, not a claim that all planned integrations are complete.

## Owner request (substance)
The owner asked that the research and analytical guidance being developed for Gann and related trading methods be reusable across the whole AI Trading Dashboard, not isolated to TIA or one indicator. The requested surfaces explicitly include Workspace, Radar, Spot, TIA, Trading Lab, Learn & AI, Order Flow, Footprint, chart patterns, indicators and any other useful platform feature. The owner wants the "mastermind" / Intelligence Director to select and apply the relevant knowledge, explain how each school thinks, guide analysis and entry planning, and make the knowledge useful to the rest of the platform team. The owner then asked to continue and preserve a full record inside the AI Trading Dashboard so it can be recovered if the chat crashes or becomes unavailable, and to provide a copy/paste command for a new conversation.

## Project identity and current working location
- GitLab project: `6868-group/ai-trading-dashboard`
- Project ID: `88622818`
- Working branch: `feat/radar-market-intelligence-foundation`
- Merge request: !46, target `main`, remains Draft / not merged.
- MR: https://gitlab.com/6868-group/ai-trading-dashboard/-/merge_requests/46
- Do not merge automatically. Do not change ownership boundaries.
- GitLab CI previously could not run because identity verification was required. No CI pass is claimed.

## Conversation decisions and architecture

### A. Shared knowledge model
A single canonical registry is the source of truth. Platform pages should not maintain separate contradictory copies of Gann/Elliott/SMC/ICT/Price Action/Order Flow/Volume Profile/indicator/risk/validation definitions. The Intelligence Director chooses the relevant route and specialists using page, feature, task and verified data capability. Each returned guidance package should include:
- purpose / why the feature is relevant;
- reasoning steps and the school(s) selected;
- data prerequisites and missing-capability gates;
- definitions, hard rules, soft rules, confirmation and invalidation;
- outputs required for the current page;
- next action and Academy/Lab links;
- source/provenance, uncertainty, limitations and evidence status.

### B. Platform coverage requested
1. Workspace: charts, multi-chart, drawings, timeframes, watchlist, indicators (ADX, RSI, MACD, CCI, SAR, divergence, VWAP, ATR), Gann, Square of Nine, Gann Fan, geometry, candle/chart/harmonic patterns, Order Flow Map, DOM, Time & Sales, Footprint, TCLASS.
2. Radar: market pulse, breadth, relative strength, rotation, regime, screener, similar/correlation, flow, OI/funding, liquidity/DOM, historical heatmap, auction/Volume Profile, setups, evidence and indicators.
3. Spot: spot-specific holdings/watchlist/flow/news/outlook, day/week/month/year horizons, Gann, Elliott, patterns, staged accumulation/protection. Spot and derivatives remain separate.
4. TIA: Intelligence Director, specialist selection, tasks, memory, handoffs, evidence map, audit trail.
5. Trading Lab: hypothesis freeze, backtest, calibration, baselines, ablation, walk-forward, out-of-sample, cost model and promotion gate.
6. Learn & AI: same canonical school knowledge as lessons, references, worked examples, counterexamples, exercises and lab evidence.
7. Order Flow Desk: feed-aware flow/DOM/footprint interpretation and proposals; its separate code ownership boundary remains intact.

### C. Shared analysis chain
Regime → Higher-timeframe structure → Location → Trigger → Order Flow gate (only where required and valid) → Timing → Plan → Evidence status.
This is a flexible reasoning scaffold, not a requirement to force every stage into every feature. Spot investment horizons and Footprint interpretation have distinct task-specific steps.

### D. School roles and cautions
- Price Action / Market Structure and Trend are primary candidates, not automatically proven profitable.
- Sessions are timing/context.
- SMC/ICT, Elliott, Gann and Harmonic are hypothesis/context schools until their own objective rules and tests pass.
- Order Flow is a confirmation gate, not a standalone direction oracle.
- Volume Profile is location/auction context and requires genuine volume-at-price.
- Indicators are derived context; avoid double-counting correlated measurements.
- Risk and Validation are gates.
- Options/GEX are model-dependent context and require a valid chain.
- Never claim institutional intent from OI/volume/DOM alone.

## Work completed in GitLab in this conversation

### Commit 1 — Gann image archive index
- Commit: `0795657f669ae1bb5616707b7d6b75716132e7d1`
- Title: Expand TIA image archive index to include Gann and geometry references.
- Files: `docs/TIA_IMAGE_RESEARCH_INDEX.md`, `data/tia_image_research_index.json`.
- Archive: 30 original images indexed as TIA-Reference-01 through TIA-Reference-30 in Library under `/TIA Image Research/Originals/`.
- Gann/geometry refs 20–30; ref 26 is a Tesla number graphic and must not be conflated with Gann. Exact source-to-image attribution remains a research task.

### Commit 2 — Gann research playbook
- Commit: `b4721fbdd17a788d551a765efa4cacdb5de4350d`
- Title: Add comprehensive Gann research playbook and specification.
- Files: `docs/TIA_GANN_RESEARCH_PLAYBOOK.md`, `data/tia_gann_research_spec.json`.
- Covered anchor stability, Square of Nine convention, fan price/time calibration, geometry, time cycles, historical case ledger, validation and test plan.
- Square of Nine formula `(sqrt(anchor_price) +/- degrees/180)^2` is documented as a modern practitioner reconstruction, not verified verbatim original Gann wording.
- Gann remains unvalidated; no profitability claim.

### Commit 3 — Shared platform knowledge router
- Commit: `e740f92e729266d297c11b397035f119baab6dfe`
- Title: Add shared platform knowledge router for all XPiX surfaces.
- Files:
  - `data/tia_platform_knowledge_registry.json` — canonical registry and school/route cards.
  - `modules/tia_knowledge_router.py` — read-only public router.
  - `tests/test_tia_knowledge_router.py` — contract tests added, not executed.
  - `docs/TIA_PLATFORM_KNOWLEDGE_ROUTER.md` — architecture and integration plan.
- Routes cover Workspace charts, indicators, Gann, patterns, Order Flow and Footprint; Radar pulse, flow, liquidity, auction and setups; Spot overview, Gann, Elliott and patterns; Trading Lab; Learn & AI; TIA Director; Order Flow Desk.
- Public API: `load_registry()`, `resolve_guidance(page, feature, task=None, available_data=None)`, `list_routes()`.
- Registry is read-only and fails closed for unknown routes. Missing capabilities return a gate, not fabricated analysis.
- `available_data` is capability metadata only; do not pass secrets or raw market payloads.
- MR !46 received a note describing this commit and explicitly stating tests were not run and page UIs are not yet wired.

## Prior Gann constraints carried forward
- Gann must remain standalone, not mixed with XPIX SHIX.
- Do not base new implementation on v16 alone. Inspect v1.2, v1.3, v1.4.1, v17/v18 and original source history.
- Stable confirmed HTF anchor; keep old valid anchor until a new pivot is confirmed. Distinguish pivot/event time from known/confirmation time.
- No current-close/current-bar fallback anchor; no future leakage or repainting.
- Square of Nine, time cycles and target/direction defaults were previously requested ON; Gann Fan, star/geometry shapes and channel OFF by default; all groups independently toggleable.
- Freeze instrument modifier and price/time units per anchor epoch; chart zoom must not alter calculations.
- Drawings must not compress chart scale.
- Legacy 30/45/90-bar cycle choices are project conventions, not universal Gann laws.
- Historical examples must include failed cases and avoid cherry-picking.

## Data integrity and research gates
- Every observation should carry source, venue, instrument type, timestamp, freshness, coverage and raw/derived quality.
- Spot, perp and futures books are not interchangeable; do not call one venue's depth "global liquidity".
- Footprint requires classified trade prints and documented aggressor-side methodology.
- Volume Profile requires genuine volume-at-price; OHLCV candles alone are insufficient.
- Historical liquidity heatmap requires persisted book snapshots/deltas; candle volume is not a substitute.
- Options/GEX requires a valid timestamped chain and must be labelled as model-dependent.
- Confirm higher-timeframe data; no lookahead/future leakage.
- Do not double-count correlated indicators.
- Keep failures and neutral results in the ledger.
- Use realistic spread, fees, slippage, funding, fill assumptions and chronological OOS testing.
- No agent can place a live order or take external action without separate explicit approval.

## Team ownership boundaries
The shared registry is readable across the platform, but code ownership remains separate:
- TIA owns `modules/tia_*` and `docs/TIA_*`.
- Claude/Core owns core brain, risk, horizons, GEX and related money logic; do not edit those files without the owner stream's review/order.
- Grok/Order Flow Desk owns `modules/desk_*` and `docs/proposals/grok/*`; do not edit those files.
- `modules/workspace_app.html` is generated; edit only the relevant `modules/ws/*` source part and run `scripts/build_workspace.py`.
- No generated workspace HTML edits in the shared knowledge-router commit.

## What is NOT done
- Router is not yet wired into every page or UI.
- The registry has initial routes/school cards; exhaustive option-by-option inventory of every live widget/control still needs a page-by-page audit.
- No autonomous LLM worker, cross-agent runtime integration, permission broker or automatic knowledge feedback loop was added.
- Gann original-source-to-image crosswalk and historical case-study ledger remain open.
- Existing Gann script versions must be retrieved and compared before any code change.
- Router tests have been authored but not run.
- GitLab CI has not passed; identity verification had blocked jobs.
- MR !46 is not merged.
- No trading performance/profitability claims.

## Immediate next work — ordered
1. Inspect current branch and MR !46 state; preserve the Draft status and do not merge.
2. Run local syntax/import and targeted router tests in a safe project checkout if available; report actual results only.
3. Perform a complete page-by-page live UI inventory (all tabs, panels, toggles, sub-options, indicators, patterns, Workspace parts, Radar/Spot/TIA/Lab/Learn/Order Flow).
4. Map every discovered option to registry route(s), school cards, data prerequisites, reasoning steps, outputs and next actions. Add unmapped items to a coverage ledger rather than silently omitting them.
5. Integrate router into one surface at a time, starting Workspace, then Radar, then Spot, then TIA, Trading Lab and Learn & AI. Order Flow Desk consumes read-only contract/proposals under its owner.
6. Add per-surface tests and desktop/mobile smoke tests. Avoid duplicate data requests and duplicate scanners.
7. Continue Gann primary-source research and crosswalk refs 20–30, then create case ledger with successes and failures.
8. Inspect historical Gann code versions before implementing calculation engines.
9. Update this session note and recovery prompt after each material increment; add a new dated session note rather than overwriting history.

## Recovery instruction
The new conversation should read this note and `docs/TIA_RECOVERY_PROMPT.md` first, inspect current branch/MR and the three commits above, then continue from "Immediate next work". Do not ask the owner to repeat already documented decisions. If a path or artifact cannot be verified, say so rather than guessing.
