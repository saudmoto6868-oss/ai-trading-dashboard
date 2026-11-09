# XPIX Intelligence — Agent Start Here
**Owner-approved workstream · 2026-11-09 · canonical handoff for every human/AI coding agent**

> Read this before touching the widget. This is the entry point, not a replacement for detailed sources. Durable project references, not chat memory, are the source of truth.

## 0. Owner's product intent
Build **XPIX Intelligence** as a standalone market-analysis cockpit inside the existing Workspace, opened beside and linked to the user's chart. It must feel like a professional market terminal, not a chatbot and not a replacement chart.

Core experience:
- Select/link instrument, venue and timeframe.
- Footprint: bid×ask volume per price, delta, imbalance, POC and absorption.
- Order Flow / liquidity Heatmap, resting DOM, liquidity add/pull/execute where feed supports it.
- Time & Sales: aggressor side, size/notional, sequence, timestamp, pace, delta, large prints and absorption candidates.
- Volume Profile / Auction Market Theory: POC, VAH/VAL, value migration, session profile, acceptance/rejection, excess and balance/imbalance.
- Market structure/context: HTF bias, levels, sessions, volatility/regime, news/macro and cross-market relationships.
- Dedicated Indicators area to select existing chart indicators.
- Deterministic setup reviewer ranks Setup 1/2/3, explains qualification/failure and builds a complete plan.
- Chart-linked alert/annotation only after validated trigger, entry zone, stop, target ladder, invalidation and expiry. Explain the exact theory/rules and evidence. Otherwise show WAIT / NO TRADE and what's missing.
- Every metric, tool, indicator, setup and confirmation has concise Egyptian Arabic help inline/on hover.
- AI/voice copilot is optional and secondary. Evidence, tools and setup engine are the product core.

## 1. Product placement — where this belongs
**Runtime home: Workspace.** Internal panel type 'intel' in 'modules/ws/'. Workspace owns live chart-adjacent experience, symbol/timeframe linking, panel layout and chart annotations.

Do not relocate this widget to another top-level page:
- **TIA:** institutional parent identity/orchestration above XPIX, Radar, Workspace, Technical Office, Spot, Lab, Playbook, Alerts and Prop Firms. TIA may later show a summary/link, but must not duplicate the cockpit.
- **Technical Office:** engineering/research governance, detector analysis, strategy map, Flow Lab, backtests, risk and validation. Review/validation home, not live cockpit.
- **Academy:** canonical teaching/rulebook knowledge: school meanings, hard/soft rules, setup conditions, confirmations and invalidation. XPIX consumes Academy rules; don't duplicate curriculum in UI code.
- **Radar:** broad market scanning/candidate discovery. It may pass candidate symbols/setups into XPIX; it is not the cockpit.
- **Spot (page 11):** separate long-only spot portfolio, holdings/ledger/invoices and spot analysis. Do not put this widget there or confuse spot with futures/CFDs.
- **Research Hub / Labs:** independent validation, multiple-testing control, walk-forward/OOS, decay monitoring and promotion. Not a duplicate live panel.
- **Playbook:** strategy/style configuration and journal conventions; supplies per-style settings to the setup engine.

Preserve page identities/indices documented in CLAUDE.md.

## 2. Mandatory start-up reading order
1. AGENTS.md
2. docs/AGENT_PROMPT.md
3. CLAUDE.md
4. docs/MEETING_ROOM.md (newest owner instructions)
5. docs/WHITEBOARD.md (scope/priority/ownership)
6. This file
7. docs/XPIX_INTELLIGENCE_WORKSPACE_SPEC.md
8. docs/MEETING_XPIX_INTELLIGENCE_2026-11-09.md
9. docs/WORKSPACE_PARTS.md
10. docs/academy/MANIFEST.md, docs/academy/README.md, docs/academy/ai/SCHEMA.md
11. docs/academy/INDICATOR_MAP.md, docs/PLAYBOOKS.md, docs/PIPELINE.md
12. docs/RESEARCH_HUB.md, STRATEGY_LAB.md, docs/academy/BACKTEST_EVIDENCE.md
13. docs/AGENT_CONTRACT.md and relevant tests.

For each school being implemented, read its exact docs/academy/ai/NN-*.json.md. Use docs/academy/visual/ for UI explanations only; never derive executable rules from visual lessons.

## 3. Canonical sources — do not create competing rulebooks
| Need | Canonical reference | Use |
|---|---|---|
| Machine-readable schools, hard/soft rules, setups, entry/stop/targets/confirmations/invalidation | docs/academy/ai/ + SCHEMA.md | Executable school logic |
| Human lessons and Arabic explanations | docs/academy/visual/ | UI help and teaching |
| Style, timeframe, confirmations, risk and exits | docs/PLAYBOOKS.md | Keep playbooks separate |
| Indicator-to-school-to-detector mapping | docs/academy/INDICATOR_MAP.md | Update for every new indicator |
| Validation/promotion | docs/PIPELINE.md, docs/academy/DEVELOPMENT_NOTES.md, docs/RESEARCH_HUB.md | No promotion by AI vote |
| Historical results and caveats | STRATEGY_LAB.md, docs/academy/BACKTEST_EVIDENCE.md, docs/research/STRATEGY_RESEARCH_2026-11-06.md | Preserve dataset/cost/OOS caveats |
| Trade classes and journal | modules/ws/24b_tclass.js, modules/ws/14_journal_chain.js | Reuse school/style tags and journal |
| Frozen Flow Confluence v1 | modules/ws/24_flow_confluence_misc.js | Preserve; version changes |
| Footprint calculations/recorder/store | modules/ws/13_okx_levels_regime_footprint.js and tests/test_footprint_rules.py, test_footprint_recorder.py, test_footprint_store.py | Baseline parity first |
| OFM/heatmap | modules/ws/22_ofmap.js | Shared Hub feed |
| DOM/Tape/Limit tracking | modules/ws/22_panels.js, modules/ws/23_orderflow.js | Preserve independence; audit sequencing/dedup/timestamps/staleness |
| Indicators | modules/ws/15_ws_hub_indicators.js, modules/ws/20_chart_canvas.js, modules/ws/21_drawing_tools.js | Inspect actual registry |
| Guide / optional AI and voice | modules/ws/25_guide.js, modules/guide_ai.py, modules/guide_bridge/ | Reuse Guide; live voice is Gemini Live, not OpenAI voice |

## 4. Trading decision chain — not indicator voting
1. **Regime:** trend / range / high volatility / low activity / unknown.
2. **HTF bias:** direction from fixed higher-timeframe structure/trend rule.
3. **Location:** value area / POC / VAH / VAL / prior session levels / premium-discount / validated S/R.
4. **Trigger:** one explicitly defined setup detector; precise and testable.
5. **Participation / execution gate:** actual prints, delta, footprint imbalance, absorption, DOM/heatmap evidence. Only where feed supports it.
6. **Timing:** session / kill-zone / event timing where relevant.
7. **Risk & plan:** entry, invalidation, stop, target ladder, R, size, expiry and no-trade reasons.
8. **Review:** journal outcomes and net expectancy by setup, symbol, timeframe, venue and regime.

Do not stack correlated candle-pattern detectors and call that confluence. Project research found 4+ detector families agreeing performed worse than 1–2 in one reported study; the measured chain did not improve quality in its first run. Re-read docs/PIPELINE.md and current STRATEGY_LAB.md before ranking changes. Do not assume A+++ grade predicts success.

## 5. School map and intended role
- **Levels / Price Action:** primary candidate. HH/HL/LL/LH, fixed S/R zones, candle trigger only at active level, failed break and breakout-retest. docs/academy/ai/01-levels.json.md.
- **Trend / Turtle / TSMOM:** primary candidate; Donchian 20/55, SMA 10/40, fixed MA rules and ATR sizing. docs/academy/ai/02-trend.json.md. Intraday costs are a major caveat.
- **Sessions / Liquidity:** timing layer, not standalone clock signal. Asia range, sweep/reclaim, London/NY windows, fixed sweep definition. docs/academy/ai/03-sessions.json.md.
- **SMC / ICT:** context/unproven. BOS/CHoCH, pools, FVG/IFVG, OB, premium/discount and OTE need strict definitions and ablation. docs/academy/ai/04-smc.json.md.
- **Elliott:** context/unproven; hard cardinal rules, wave-2 invalidation, wave-3 continuation hypothesis. docs/academy/ai/05-elliott.json.md.
- **Gann:** context/unproven. Anchors fixed and scale-calibrated; keep user's separate Gann tool independent. docs/academy/ai/06-gann.json.md.
- **Harmonic:** context/unproven; each pattern separately parameterized and tested. docs/academy/ai/07-harmonic.json.md.
- **Order Flow:** execution gate / confirmation at an existing location, not standalone directional prediction. docs/academy/ai/08-orderflow.json.md.
- **Mean reversion:** separate regime/system; do not combine grade with trend. docs/academy/ai/09-meanrev.json.md.
- **VWAP:** session VWAP ±2σ reversion / pullback are research candidates; separate by regime and validate costs. Owner's Nasdaq long-only stretch (close < VWAP - 25 points, 1 ATR stop) is explicitly untested. docs/research/STRATEGY_RESEARCH_2026-11-06.md.
- **EMA/SMA:** EMA 9/21 with EMA200 filter, 50/200 cross are candidate rules, not automatic confirmation votes.
- **Session levels:** PDH/PDL, daily/weekly open reactions/breaks are candidates; log session.
- **ORB:** 5m/15m opening range breakout research is mixed/weak; do not promote without local tests.

### Entry / exit examples (see Academy schema for exact rules)
- Levels trend pullback: price enters defined demand/supply while structure intact; bullish/bearish candle trigger; enter beyond signal bar; stop beyond zone/signal extreme; target prior swing then tested R multiples.
- Breakout-retest: close beyond level, wait retest hold, enter rejection/resumption; stop beyond retest; invalidate on close back through level.
- Failed breakout: excursion beyond level then close back inside within fixed K bars; trigger reclaim/rejection; invalidate on accepted break outside.
- Asia sweep: sweep Asia high/low with one fixed definition, reclaim close, trigger reclaim or micro BOS; stop beyond sweep extreme; targets opposite range / prior-day level / tested R.
- Turtle 20/55: close beyond prior channel; ATR stop and exit/trailing variant fixed per experiment.
- SMC sweep-FVG / sweep-OB / OTE: context only until strict mechanical rules and tests pass.
- Elliott wave 3: count must pass hard rules; wave 2 cannot break wave 1 origin; trigger minor corrective break; stop beyond origin; state count uncertainty.
- Mean reversion: range regime only; separate book; use tested VWAP/value/oscillator conditions and exits.

Never use illustrative documentation prices as live levels. Deterministic engine calculates levels from validated data.

## 6. Frozen Order Flow Confluence v1
1. Price inside untouched stacked-imbalance zone from Footprint (direction).
2. Current bar Delta same sign.
3. Last 60 seconds of Tape >55% volume same direction.
4. Absorption same side within 3 price rows in last 2 minutes.
Fires at 3/4, but rule 1 is mandatory; 5-minute cooldown per symbol/side.
Do not edit v1 silently. A changed rule is v2 or a separately versioned setup, with tests and journal key.

## 7. Evidence / validation hard gates
- Separate facts, calculated features, hypotheses and AI explanation.
- Every datum carries instrument, venue/source, timestamp, timeframe/window, units, coverage and quality (live/delayed/mock/estimate/missing).
- Never conflate broker XAUUSD CFD, Hyperliquid gold (HL:xyz:GOLD), and COMEX GC futures. Never call one venue's DOM global liquidity.
- Executed trades and resting orders differ. DOM walls can be cancelled; displayed wall is not executed flow.
- Stale feed, sequence gap, symbol/venue mismatch, missing required fields, unavailable market or unverified calculation => WAIT / NO TRADE.
- No look-ahead, repainting, future leakage, survivorship or selection leakage.
- Backtests require spread, fees, slippage, latency/impact where material, walk-forward/OOS and benchmark/random baseline.
- Follow existing docs/PIPELINE.md and Research Hub promotion gates; do not invent a new threshold. n<30 = NOT EVIDENCE.
- Evidence score is not win probability. No percentage win chance without calibrated OOS probability evidence.
- Journal signal through entry/exit/expiry using existing Journal/Chain and Decision Trail.
- No live order execution, brokerage credentials, wallet or automatic placement.

## 8. Instrument and feed contract
Browser Hub shares OKX 'book' and 'trades' subscriptions across panels. Reuse it; never duplicate polling in 'intel'.
- Yahoo-backed Y: markets explicitly have no book/tape; show unavailable.
- Venue and entitlements are distinct: Hyperliquid, broker CFD, COMEX, crypto spot/perp books are not interchangeable.
- Show source and freshness. Hub polls book/trades every 1.5 seconds and tickers every 3 seconds; respect rate limits and lifecycle cleanup.
- Gold mapping requires explicit venue choice: broker XAUUSD vs HL gold vs COMEX GC. Matching chart symbol is not proof the order book matches.

## 9. Workspace implementation rules
- Edit source parts only in modules/ws/; never edit generated modules/workspace_app.html directly.
- Build: python3 scripts/build_workspace.py; check: python3 scripts/build_workspace.py --check.
- Run tests/test_workspace_parts_sync.py and relevant tests; browser tests live in tests/browser/.
- Protect Footprint baseline; parity tests before calculation/render changes.
- Keep OFM/DOM/Tape independent; intel composes shared data and provides navigation/highlighting, not duplicate fetch loops.
- Preserve panel drag/resize/minimize/maximize, saved state, symbol/timeframe link and mobile/tablet layout.
- First shell is modules/ws/22x_intelligence.js; it is not feature complete. Inspect current branch HEAD and fix integration defects before extending.
- Chart annotations must use existing drawing/alert APIs after inspection. XCMD is read/draw only, not an order interface.
- Guide optional; live voice is Gemini Live. Do not claim ChatGPT voice is integrated.

## 10. Agent boundaries and work packages
Use separate branches and bounded deliverables; don't let agents edit the same files concurrently.
| Role | Deliverable | Likely files (coordinate first) |
|---|---|---|
| Integration lead | architecture/contracts/merge coordination/test plan | this doc, spec, meeting room, whiteboard |
| Market data/microstructure | normalized feed, freshness, book/tape/footprint contracts | 15_ws_hub_indicators.js, 13_okx_levels_regime_footprint.js, 22_ofmap.js, 23_orderflow.js |
| Auction/Volume Profile | session profiles, POC/VAH/VAL, acceptance/rejection, value migration | inspect existing VP in 10_feeds_charts_math.js first |
| Strategy/setup | deterministic setup definitions and decision packets | 24_flow_confluence_misc.js and strategy modules |
| Chart/UX | cockpit tabs, symbol linking, explainers, chart markers | 22x_intelligence.js, 22_panels.js, 26_snap.js, 11_i18n_helpers_themes.js |
| Quant/validation | replay, costs, OOS, calibration, promotion | Research Hub/lab files and tests |
| AI explainer (optional) | Arabic explanation of verified packet; optional voice | guide_ai.py, 25_guide.js, guide_bridge/ |

Cross-stream docs/AGENT_CONTRACT.md remains authoritative. Read-only reuse is preferred. No agent crosses code ownership boundaries.

## 11. Decision packet contract proposal
Every candidate setup is serialized before AI explanation or chart alert:
~~~json
{
  "setup_id": "levels_long_pullback_v1",
  "symbol": "instrument-id",
  "venue": "explicit-venue",
  "timeframe": "5m",
  "created_at": "ISO-8601",
  "data_quality": "live|delayed|mock|estimate|missing",
  "status": "WATCH|WAIT|READY|INVALID|NO_TRADE|EXPIRED",
  "direction": "LONG|SHORT|NONE",
  "school": "levels",
  "evidence": [{"id":"location","kind":"fact|feature|hypothesis","value":"...","source":"...","ts":"..."}],
  "confirmations": [{"id":"...","passed":false,"reason":"..."}],
  "conflicts": [],
  "entry_zone": null,
  "trigger": "...",
  "invalidation": "...",
  "stop": null,
  "targets": [],
  "risk_per_unit": null,
  "position_size": null,
  "r_multiple": null,
  "expires_at": null,
  "no_trade_reasons": []
}
~~~
This is a proposed contract until implemented/tested. AI may explain it but cannot alter prices, stop, target, status or risk.

## 12. Current status and first task for incoming agents
- Branch: feat/xpix-intelligence-workspace. GitLab Issue #9.
- Shell: modules/ws/22x_intelligence.js; menu/label registration in 26_snap.js, 24_flow_confluence_misc.js, 11_i18n_helpers_themes.js.
- Current shell is an initial Hub-connected cockpit (book/trades, mid, delta, top-10 liquidity, data status and shortcuts), not a completed trading system.
- CI attempt was blocked by GitLab identity verification; no CI/browser proof recorded.
- No merge/deploy; do not modify main; no paid API/workflow without separate owner approval.
- First action: inspect current branch HEAD, run local build/check/tests in proper checkout, fix shell lifecycle/Hub payload handling, then parity-safe Footprint/OFM/Tape integration plan.

## 13. Research sources already selected
- Cont, Kukanov & Stoikov (2014), The Price Impact of Order Book Events: https://academic.oup.com/jfec/article/12/1/47/816163
- Cboe / Mandy Xu, Evaluating the Market Impact of SPX 0DTE Options (2023): https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0dte-options/
- Amaya et al. (2025), 0DTE Index Options and Market Volatility: https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf
- ECB (2023), The risks from hidden leverage in short-term equity options: https://www.ecb.europa.eu/press/financial-stability-publications/fsr/focus/2023/html/ecb.fsrbox202311_02~0cf2c71d00.ro.html
- Topics to map into Academy and testable detectors: Auction Market Theory, Volume Profile/Market Profile, Footprint, Order Flow/Microstructure, Bookmap liquidity, DeepCharts/DeepDOM, Options Flow, GEX, market-maker hedging and delta/gamma hedging. Concepts are not proof of a profitable signal.

## 14. End-of-task handoff required
Every agent updates docs/MEETING_ROOM.md, docs/WHITEBOARD.md, docs/ACTIVITY_LOG.md and docs/sessions/<agent>-YYYY-MM-DD.md. Update this file/spec when durable decisions/contracts change.
Final report: **Done / Tested / Not tested / Next owner action**. Never claim a test passed unless it was run.
