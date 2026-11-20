# XPIX-SHIX-FIX M7 — Workspace Port Plan

Status: Phase 0 audit in progress  
Tracking: GitLab Issue #1  
Working branch: `feat/xpix-shix-m7-port-audit`  
Baseline: `main` at branch point `946ce83a6d67f317f95ce5370dfcd6493b1113ff`

## 1. Source of truth

- Source file: `XPIX-SHIX-FIX_M7  107.txt` on `main`.
- File length observed: 4,011 lines / 159,016 characters.
- The inventory describes the Pine source as lines 190–4005, excluding scraped TradingView page text.
- Inventory: `docs/indicators/xpix_shix_m7_inventory.md`.
- Inventory totals: 3,816 Pine lines, 177 inputs in 28 groups, 19 `request.security` calls, 25 alerts, 48 labels, 33 lines, 20 boxes, 4 tables, 16 helper functions and 2 user-defined types.
- The inventory currently says no code has been ported and nothing has been tested.
- Provenance discrepancy: inventory names `docs/xpix-shix-m7-source` as source branch, but a current branch search for `xpix` returned no matching branch. The source file itself is present on `main`; treat that as the currently retrievable source until provenance is reconciled.

## 2. Existing Workspace areas to compare before porting

| XPIX feature family | Existing code to audit | Initial status |
|---|---|---|
| Chart drawing, indicators, price scale | `modules/ws/20_chart_canvas.js` | Shared drawing/chart infrastructure exists; exact parity not established |
| Drawing tools and Gann | `modules/ws/21_drawing_tools.js` | Gann implementation exists; not a substitute for all XPIX layers |
| Indicator data hub / signals | `modules/ws/15_ws_hub_indicators.js` | Shared indicator polling exists |
| Flow confluence / CVD forward test | `modules/ws/24_flow_confluence_misc.js` | Separate flow implementation exists |
| Python signal engine | `modules/signals.py`, `modules/scorer.py`, `modules/sig_filters.py` | Separate scanner engine exists; integration must be deliberate |
| Gann research | `modules/gann_lab.py`, `STRATEGY_LAB.md` | Research/backtest exists; evidence is mixed/weak |

Do not count a feature as ported merely because a similarly named feature exists. Compare calculation, confirmation timing, invalidation, visual semantics, alerts and data source.

## 3. Port matrix

| Phase | Pine feature families | Required output |
|---|---|---|
| 0 — Audit | All 28 input groups, helper functions, user types, drawing and alert calls | Line-by-line feature map; identify reusable code vs gaps |
| 1 — Trend core | EMA ribbon, EMA 200, crossovers, core signal state, ATR risk levels | Matched closed-bar trend states and signals |
| 2 — Structure/liquidity | Confirmed pivots, BOS/CHoCH, EQH/EQL, sweeps | Stable structure events with explicit pivot confirmation |
| 3 — Zones | FVG/IFVG, supply/demand, volumetric OB, MSB-OB, Unicorn | Zone lifecycle parity: create, extend, touch, invalidate, prune |
| 4 — Sessions/MTF | Asia/London/NY ranges, kill zones, PDH/PDL, MTF dashboard | Timezone/DST-safe sessions and confirmed HTF values |
| 5 — Advanced layers | Volume/delta, MCDX, SMT, screener, statistics, alerts | Data-qualified advanced layers and parity evidence |

## 4. Non-negotiable correctness rules

1. Closed-bar confirmation for actionable signals unless a feature is explicitly labelled provisional.
2. A pivot cannot be used until its right-side confirmation bars have elapsed.
3. Higher-timeframe values used for confirmed decisions must come from completed HTF candles. `lookahead_off` alone does not prevent an evolving HTF value from changing before that HTF candle closes.
4. No future leakage, negative offsets used to imply earlier knowledge, or backfilled signals presented as live-known.
5. Distinguish exchange-reported volume/delta from candle-derived estimates and unavailable data.
6. Deduplicate events by symbol, timeframe, event type and source bar.
7. Drawing objects must be bounded and cleaned up; they must not alter the chart price range or degrade scrolling/zooming.
8. Keep the Pine source unchanged. Do not silently alter the original model's defaults or trading rules during porting.

## 5. Validation plan

- Build deterministic fixtures from the same OHLCV candles for Pine reference and Workspace.
- Compare signal direction, source bar, confirmation bar, levels and invalidation state.
- Test at least 1m, 5m, 15m, 1h, 4h and 1D where the source feature supports them.
- Test live-bar updates separately from closed-bar results.
- Test chart pan/zoom, timeframe switching, symbol switching, reload and historical backfill.
- Add unit tests for calculations and Playwright tests for Workspace rendering/interaction.
- Report mock-only tests honestly; do not claim live exchange validation where unavailable.

## 6. First implementation slice

Do not implement all 3,816 lines in one change.

1. Complete the Phase 0 source-to-feature mapping.
2. Implement Phase 1 EMA/trend core in a dedicated, isolated Workspace module or clearly bounded section.
3. Add parity fixtures and tests before exposing it as a default signal source.
4. Submit a focused MR; do not merge without review and passing tests.

## 7. Following work, after XPIX port

1. Unify the signal engine/scorer using the verified XPIX outputs and existing detector families.
2. Improve Order Flow data quality, event logging and forward tests.
3. Close system-wide MTF / anti-repaint gaps.
4. Expand walk-forward and out-of-sample tests with market-specific costs.
5. Unify risk management and explainable trade-plan acceptance/rejection.

These are ordered follow-up stages, not scope to mix into the initial XPIX port.
