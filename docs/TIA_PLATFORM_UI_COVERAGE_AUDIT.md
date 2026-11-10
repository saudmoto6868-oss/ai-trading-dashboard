# Platform UI-to-Knowledge Coverage Audit — 2026-11-10

## Purpose and audit method

This is a repository/code-search audit, not a visual browser certification. It separates:
- **Registry present**: route and feature aliases exist in the canonical JSON.
- **Consumer found**: code imports/calls the shared router from that page.
- **UI verified**: rendered controls have been inspected in a running browser at desktop/mobile sizes.

A route existing is never counted as integration. Search was run on branch `feat/radar-market-intelligence-foundation` for `resolve_guidance`, `tia_knowledge_router`, `load_knowledge` and page implementation modules.

## Executive finding

- The registry contains **19 routes across 7 surfaces**.
- At audit time, search for `resolve_guidance` found no page consumer. A subsequent TIA-owned integration now consumes the presentation adapter in `modules/tia_page.py`; the other six surfaces remain pending.
- The visual reference catalog is consumed by `modules/tia_intelligence.py`; that is a TIA-specific knowledge path, not proof of platform-wide router integration.
- Therefore the platform-wide shared router is **implemented as a library/registry but not yet integrated into the page UIs**.
- This audit does not claim a complete rendered-control inventory or browser/mobile test.

## Surface coverage matrix

| Surface | Registry routes | Relevant implementation paths found | Shared router consumer | Current status |
|---|---:|---|---|---|
| Workspace | 6 | `modules/workspace.py`, `modules/ws/*`, generated `modules/workspace_app.html` | Not found | Registry ready; integration pending; generated HTML must not be edited |
| Radar | 5 | `modules/radar_agents.py`, `modules/radar_presets.py`, Radar app modules | Not found | Existing deterministic Radar specialists are separate; add read-only guidance context without duplicating scans |
| Spot | 4 | `modules/spot_page.py`, `spot_board.py`, `spot_brain.py`, `spot_flow.py`, `spot_outlook.py`, other `spot_*` | Not found | Integration pending; preserve spot/derivatives separation |
| TIA | 1 | `modules/tia_page.py`, `tia_workspace.py`, `tia_intelligence.py`, `tia_agent_*` | Found: `modules/tia_page.py` | Shared guidance is rendered in a collapsed read-only expander; capability metadata remains unasserted; browser/mobile verification pending |
| Trading Lab | 1 | `modules/strategy_lab.py`, `validation_lab.py`, `calibration_lab.py`, `lab_*` | Not found | Integration pending; experiment provenance/version binding required |
| Learn & AI | 1 | `modules/academy.py`, `ai_page.py`, `guide_ai.py` | Not found | Integration pending; lessons should link to canonical route/school cards |
| Order Flow Desk | 1 | `modules/desk_*`, shared agent contract | Not found | Read-only contract/proposal integration only; owner boundary remains |

## Registry route inventory

### Workspace — 6
- `workspace_charts`: charts, multi-chart, drawings, watchlist, timeframes.
- `workspace_indicators`: ADX, RSI, MACD, CCI, SAR, divergence, VWAP, ATR.
- `workspace_gann`: Gann, Square of Nine, Fan, angles, boxes/squares/circles, cycles.
- `workspace_patterns`: candlestick, chart and harmonic patterns.
- `workspace_orderflow`: Order Flow, DOM/depth, Time & Sales/tape, CVD/OFI, liquidity heatmap.
- `workspace_footprint`: footprint, bid/ask, imbalance, absorption, exhaustion, stacked imbalance.

### Radar — 5
- `radar_pulse`: market pulse, breadth, relative strength, rotation, regime, screener, correlation.
- `radar_flow`: long/short build-up, covering/unwinding, CVD, OI, funding, premium.
- `radar_liquidity`: DOM, heatmap, sweeps, absorption, depth imbalance.
- `radar_auction`: Volume Profile, POC/VAH/VAL/HVN/LVN, VWAP, acceptance/rejection.
- `radar_setups`: setups, signals, candidates, scanner, entry trigger.

### Spot — 4
- `spot_overview`: spot watchlist, holdings, portfolio and horizons.
- `spot_gann`: Square of Nine, Fan and price/time cycles.
- `spot_elliott`: wave counts and alternate Elliott scenarios.
- `spot_patterns`: candlestick/chart/harmonic context.

### Other surfaces — 4
- `tia_director`: Director, agents, team, memory, tasks, handoffs, session preparation.
- `trading_lab_validation`: backtest, validation, calibration, walk-forward and evidence.
- `learn_ai_lessons`: Academy, schools, lessons, examples, AI tutor and research.
- `order_flow_desk`: flow, DOM, tape, footprint, delta and liquidity.

## Cross-cutting feature and data gates

| Feature family | Required metadata/capability | Must remain blocked/limited when absent |
|---|---|---|
| Footprint / delta / absorption | classified trade prints, aggressor methodology, venue, timestamps, coverage | No reconstructed bid/ask footprint from OHLCV |
| Volume Profile / auction | true volume-at-price, period and profile algorithm | No POC/VAH/VAL/HVN/LVN from candle volume |
| Historical liquidity heatmap | persisted book snapshots/deltas, venue and time coverage | No historical liquidity inferred from candle volume |
| DOM / depth | venue-specific live or timestamped depth, freshness | Never call one venue's book global liquidity |
| Options / GEX | timestamped chain, expiry/strike coverage, model assumptions | Label estimate/model limits; no standalone directional conclusion |
| Gann | stable anchor, pivot time and known/confirmation time, frozen price/time units | No current-bar fallback, repainting or zoom-dependent calculation |
| Elliott / harmonic / SMC-ICT | explicit objective rules, alternatives, trigger and invalidation | Hypothesis/context only until tested |
| Indicators | formula, parameters, timeframe, confirmation timing | No independent votes from correlated indicators |
| Spot holdings | spot inventory and portfolio exposure | Never merge with futures/perpetual positions |
| Backtests | chronological splits, costs, slippage, funding, realistic fills, baselines | No promotion based only on in-sample or n<30 |

## Prioritized integration backlog

1. **TIA-owned safe foundation:** add a compact reusable presentation adapter for router results and tests; do not change page owners' files.
2. **Workspace:** owner-approved import into the Python wrapper or source component under `modules/ws/*`; never edit generated HTML. Rebuild and run workspace sync tests.
3. **Radar:** consume existing scan/agent result, attach route guidance read-only; do not add a second scanner or extra feed request.
4. **Spot:** route overview/Gann/Elliott/pattern guidance using spot-only capabilities.
5. **TIA:** Director selects route and specialists; show source, missing capabilities, evidence and handoff trace.
6. **Trading Lab:** record route ID and registry/schema version with each experiment.
7. **Learn & AI:** render the same canonical school cards as lessons, worked/failed examples and exercises.
8. **Order Flow Desk:** owner-reviewed read-only contract/proposal only; do not edit `modules/desk_*`.
9. Add per-surface tests, unmapped-control tests, data-gate tests and desktop/mobile smoke tests.

## Release gates and unresolved blockers

- MR !46 must remain Draft until its 30-commit divergence from `main` is safely reconciled and GitLab reports a mergeable state.
- Latest observed pipeline failed with zero jobs; no tests were executed. Restore CI job creation/identity verification and inspect job logs.
- Run compile/import checks and the newly expanded TIA quality suite; do not infer success from YAML edits.
- Complete visual control inventory in a running app. Repository paths and route aliases are not a substitute.
- Preserve the three-stream ownership model and session-note rule.
- No merge, deployment, live trading or broker action is authorized by this audit.

## Evidence and scope note

This audit is based on GitLab branch file contents and GitLab project blob search. It does not claim access to a running local checkout, browser session, exchange account, secrets or private live market feeds.
