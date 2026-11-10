# TIA Shared Platform Knowledge Router

Status: architecture and read-only router implementation; integration into every UI/agent remains staged. This is a shared knowledge service, not a second scanner, strategy engine, or execution engine.

## Owner objective

One canonical knowledge base should help the whole XPiX platform think consistently. The same Gann, Elliott, Price Action, SMC/ICT, Volume Profile, Footprint, indicator, risk and validation knowledge should be reusable from Workspace, Radar, Spot, TIA, Trading Lab, Learn & AI and the Order Flow Desk.

The platform's "mastermind" chooses the relevant knowledge and specialist roles based on the current page, selected feature, user task and verified data capabilities. It should not paste every school into every answer.

## Existing surfaces found in the repository

- Workspace: multi-chart canvas, drawing tools, watchlist/timeframes, Gann, support/resistance, regime, Volume Profile, Order Flow Map, Footprint/TCLASS, Time & Sales, DOM, indicators and chart patterns. Parts are in `modules/ws/*`; `modules/workspace_app.html` is generated. Never edit the generated HTML directly.
- Radar: Market Pulse, breadth/relative strength/rotation, screener, regime/news, Flow, Liquidity, Auction & Volume, Setups, Evidence & Indicators, plus the deterministic Radar Agent Control Room.
- Spot: spot-specific data, watchlists/holdings, flow, indicators, news, outlook and the four horizon brain (day/week/month/year). Keep Spot and futures/perpetual datasets separate.
- TIA: Director, specialist roles, persistent tasks/memory/handoffs and educational visual-knowledge readiness.
- Trading Lab: strategy validation, backtests, calibration, rotation and evidence promotion.
- Learn & AI: Academy's nine schools and AI/visual tracks, lessons, examples and research tutor.
- Order Flow Desk: separate owner stream and code boundary; shared knowledge is consumed through the result/proposal contract, not by editing its files.

## Shared decision chain

Regime → Higher-timeframe structure → Location → Trigger → Order Flow gate (only where the setup requires it and the data is valid) → Timing → Plan → Evidence status.

Not every feature uses every stage. For example, a long-horizon Spot thesis emphasizes portfolio exposure and staged invalidation; Footprint emphasizes feed semantics and price response; Learn & AI emphasizes source, examples and exercises.

## Router contract

The read-only public API is in `modules/tia_knowledge_router.py`:
- `load_registry()`
- `resolve_guidance(page, feature, task=None, available_data=None)`
- `list_routes()`

The JSON source of truth is `data/tia_platform_knowledge_registry.json`. Other page owners may import these public functions without editing TIA files. `available_data` is capability metadata only (e.g. `volume_at_price`, `classified_trades`, `options_chain`); do not pass raw account data, secrets or market payloads.

The router returns purpose, thinking steps, selected schools, blocked capabilities, required output fields, next actions, related routes and global safety rules. Unknown routes fail closed to `unmapped`; absent data creates a visible gate, never a fabricated conclusion.

## Feature coverage

| Surface | Routes |
|---|---|
| Workspace | chart interpretation; indicators; Gann; candle/chart/harmonic patterns; Order Flow/DOM/Tape; Footprint |
| Radar | market pulse; flow/OI/funding; liquidity/DOM/heatmap; auction/Volume Profile; setup candidates |
| Spot | portfolio/horizons; Gann price-time context; Elliott scenarios; patterns and staged plans |
| TIA | Director orchestration, task contract, specialists, evidence map and audit trace |
| Trading Lab | hypothesis freeze, data quality, costs, baselines, ablation, walk-forward/OOS and promotion |
| Learn & AI | source-led lessons, worked/failed examples, rules, exercises and evidence status |
| Order Flow Desk | feed-aware interpretation and proposals within its separate ownership boundary |

## Knowledge cards / schools

Each school defines its role, when it should be used, data prerequisites and limitations. The registry deliberately classifies Gann, Elliott, SMC/ICT and Harmonic as context/hypothesis schools until their individual rules pass validation. Price Action and Trend are primary candidates, not automatically proven. Order Flow is a confirmation gate; Volume Profile is location context. Indicators are derived context, not independent votes. Risk and Validation are mandatory gates.

## Specialist routing

- Intelligence Director: frames task, chooses routes and delegates.
- Market Scout: universe, regime, breadth, relative strength and events.
- Chart Reader: structure, levels, patterns and indicator state.
- Flow Analyst: trade prints, delta/CVD/OFI and footprint when data supports them.
- Liquidity Sentinel: venue-specific book, depth, sweeps and persisted history.
- Auction Guide: VWAP/profile/value acceptance when valid volume-at-price exists.
- Risk Guardian: invalidation, costs, exposure and configured risk policy.
- Trade Reviewer: alternate explanation, failure cases and evidence grade.
- Research Tutor: canonical lesson, sources, worked examples and next study step.

Specialists return structured evidence, not free-form certainty. Use the shared agent result contract from `docs/AGENT_CONTRACT.md`; no agent may claim live data if the source is mock, stale, partial or unavailable.

## Data gates

- Footprint/Delta/Absorption require classified trade prints with documented aggressor methodology, venue, timestamps and coverage.
- Volume Profile POC/VAH/VAL/HVN/LVN require genuine volume-at-price and explicit profile period/algorithm.
- Historical liquidity heatmap requires persisted book snapshots/deltas; candle volume is not a substitute.
- Options/GEX require a valid, timestamped options chain; estimates must be labelled.
- Gann fan requires frozen anchor and explicit price/time units; 1x1 screen angle is not universal.
- Elliott requires alternate counts and invalidation; never force a single count.
- Indicator values require formula, parameters, timeframe and confirmation timing.
- Spot holdings and futures positions must remain separate.

## Integration plan

1. Read-only integration first: pages call `resolve_guidance` and render a compact "Why this matters / What to check next" panel.
2. Add context to the existing Radar and Spot agents via the shared agent-result schema; do not duplicate scanners or request duplicate feeds.
3. Add Academy links from each guidance card and let Learn & AI render the same card as a lesson.
4. Trading Lab stores the exact school/setup version and router route used by each experiment.
5. TIA Director selects specialists, delegates bounded tasks and records the route, evidence, missing data and handoff.
6. Order Flow Desk consumes the registry read-only and submits proposals through its own owner workflow.
7. Add browser/mobile smoke tests and per-page contract tests before enabling each integration.

## Boundaries and non-goals

- No direct edit to `modules/workspace_app.html`; it is generated from `modules/ws/*`.
- This commit does not wire the panel into every page. It provides the canonical registry, read-only resolver and contract tests.
- Do not modify Claude-owned `brain*.py`, risk, horizons, GEX or core money logic. Do not modify Grok-owned `desk_*` files. Do not modify other streams' files without their owner approval.
- No LLM tool execution, order routing, broker calls, background agent autonomy or adaptive strategy weights are added here.
- No profitability claim; no tests are claimed until executed in the repository environment.
