# Radar Market Intelligence — Implementation Plan
Date: 2026-11-09
Target repository: 6868-group/ai-trading-dashboard
Base: main
Branch: feat/radar-market-intelligence-foundation

## Owner intent
Upgrade the existing Radar into a competitor-class Market Intelligence workspace inspired by OrderBlock/TBTflow/OptionAlgo/Bookmap/ATAS, while preserving current Radar, Scanner, Workspace, Technical Office, Academy, Lab, and data workflows. Free-first. No paid subscriptions or automatic order execution in this phase.

## Non-duplication rules
- Do not create a second Scanner or a second Radar page. Radar already exists in main.py and contains chart grid, Signals, Screener, Similar, Performance/Correlation, shared filters, confirmed/candidate ranking, market-regime strip, and Lab evidence.
- Keep the existing Workspace Scanner and its saved presets intact.
- Reuse existing market_cache/data_fetcher/hl_feed/market_map/Order Flow/DOM/Time & Sales/Limit Tracking modules where their data contract is valid.
- Historical Liquidity Heatmap remains separate from live Order Flow. Persist snapshots/events; never reconstruct historical DOM from candle volume.
- Keep Spot and Futures datasets separate. Never merge exchange order books or label one venue's depth as global liquidity.
- No claim of institutional activity from OI/volume/DOM alone.
- No automatic trading. All outputs are research/decision support until owner separately approves execution.
- Do not mix this work with XPiX Market Pulse 3D, CRT Gold, X77/GANN CORE, or other repositories.

## Existing implementation found on main (audit snapshot)
- Top-level navigation already includes Workspace, Radar, Spot, TIA and grouped Trading/Lab/Learn & AI hubs.
- Radar already has shared filters, chart cards, confirmed/candidate ranking, signal list, Finviz-like screener, regime/news/data-age strip, and Lab evidence.
- Existing market_map.py calculates market breadth, class average change, relative strength and filters for Hyperliquid TradFi markets.
- radar_presets.py already includes Oversold bounce, Overbought fade, Bull/Bear trend stack, Volume breakout/breakdown, reversal patterns, channels/trendlines, SMC/ICT and Elliott presets.
- Academy has nine schools with AI and visual tracks: Levels/Price Action, Trend, Sessions/Liquidity, SMC/ICT, Elliott, Gann, Harmonic, Order Flow, Mean Reversion.
- INDICATOR_MAP.md defines Regime → HTF → Location → Trigger → OF gate → Timing → Plan.
- DEVELOPMENT_NOTES.md has R1–R10 research queue. BACKTEST_EVIDENCE.md says Trend/TSMOM, Mean Reversion, and Levels deserve earlier testing; SMC/ICT is context, Order Flow is a gate, Elliott/Gann/Harmonic are context until validated.
- Current README describes the original Streamlit app and may lag behind current navigation; verify live UI before modifying page architecture.

## Radar information architecture (inside existing Radar page)
1. Market Pulse: breadth, up/down participation, relative strength, sector/class rotation, top movers, volatility/regime, data freshness.
2. Flow: Long/Short build-up, short covering/long unwinding where futures OI is available; executed buy/sell pressure, CVD, volume delta and OFI where tick data permits.
3. Liquidity: live DOM depth by venue, spread, depth imbalance, liquidity changes, sweeps and absorption candidates; separate live book from persisted historical liquidity.
4. Auction & Volume: session/anchored VWAP, Volume Profile POC/VAH/VAL/HVN/LVN, value acceptance/rejection and LVN traversal. Use only data with valid volume semantics.
5. Setups: searchable setup catalogue and live candidates, with explicit trigger/confirmation/invalidation/SL/TP/timeframe/regime/source fields. Reuse existing Radar strategy/pattern detectors.
6. Evidence & Indicators: detector-level sample size, net R after costs, in/out-of-sample status, confidence/evidence state, indicator definitions and ablation results.

## Data source policy — free-first
- Crypto spot: public Binance and OKX REST/WebSocket feeds first; Bybit as a later fallback.
- Crypto derivatives: exchange-specific Binance/OKX/Bybit public feeds; Hyperliquid for its own venue only.
- Forex/Gold: keep current MT5 feed as the primary broker-specific source; optional delayed/historical sources only after symbol mapping and entitlement checks.
- US equities: existing Finnhub integration first; FMP free for EOD/reference/fundamental enrichment; Alpaca Basic only as an optional IEX-limited source.
- Options/GEX: do not fabricate options flow. Start with derived analytics only when a legitimate chain/OI/IV feed is available; otherwise mark unavailable.
- Macro: reuse FRED integration and existing economic calendar.
- Charts: reuse current chart stack; TradingView Lightweight Charts is an option only if a replacement/additional chart renderer is actually required.

## Data integrity requirements
- Every observation carries source, venue, instrument type (spot/perp/future/option/CFD), timestamp, freshness, and whether it is raw or derived.
- Normalize exchange timestamps and symbol identifiers; preserve source-native IDs.
- WebSocket is the live stream; REST is bootstrap/recovery/backfill, not a high-frequency polling substitute.
- Store trades, book snapshots/deltas and candles as separate event families.
- Rebuild each venue order book from valid snapshots + ordered deltas; detect sequence gaps and mark book invalid until resynced.
- Historical liquidity requires persisted book/trade events with retention policy; candle volume is not a substitute.
- Distinguish OI changes from position direction; label Long/Short Build-up only when price and OI conditions are both met, and display the formula/limitations.
- Show stale/missing/partial data explicitly; never silently convert missing values to zero.

## Confluence and setup scoring
- Keep the existing decision chain: Regime → HTF → Location → Trigger → OF gate → Timing → Plan.
- Primary candidates initially: Levels/Price Action and Trend; Mean Reversion is a separate regime-gated system.
- Sessions are timing/context; SMC/ICT, Elliott, Gann and Harmonic are context/invalidation until individual tests pass.
- Order Flow is a confirmation gate at a pre-defined level, not a standalone direction oracle.
- GEX/FRED are context, never entry triggers.
- No ranking based only on number of indicators agreeing. Use calibrated, tested features and report unknown/insufficient evidence.
- Maintain the project risk setting of 0.5% per trade unless the owner explicitly changes it.

## Delivery sequence
### Phase 0 — audit and freeze interfaces
Inventory current Radar render path, data providers, scanner detectors, cache keys, existing DB/storage, tests and navigation. Record what works vs code-only vs live-verified. No duplicate modules.
Acceptance: inventory and baseline tests; no UI behavior changes.

### Phase 1 — Radar UX shell
Add six internal views within existing Radar (Market Pulse, Flow, Liquidity, Auction & Volume, Setups, Evidence & Indicators). Keep shared symbol/timeframe/market filters and preserve current chart grid and screener. Empty states must say why data is unavailable.
Acceptance: desktop/mobile smoke tests, existing Radar tests pass, no duplicate Scanner.

### Phase 2 — Market Pulse reuse
Extend existing market_map and Radar KPI strip with breadth, relative strength, class/sector rotation and volatility regime. Reuse cached candles/market data; do not make redundant API calls.
Acceptance: unit tests on synthetic data, source timestamps and stale-data display.

### Phase 3 — Free crypto Flow and Liquidity
Integrate one exchange at a time using public WebSocket feeds. Start with trades, top-of-book/depth, OI/funding where supported. Add CVD, delta, OFI, depth imbalance and absorption candidates only with explicit definitions.
Acceptance: reconnect/sequence-gap tests, source/venue labeling, no fabricated historical book.

### Phase 4 — Auction & Volume
Implement session/anchored VWAP and Volume Profile (POC/VAH/VAL/HVN/LVN) from valid volume data; define acceptance/rejection and LVN traversal as testable setups.
Acceptance: reproducible profile calculations and chart/price-level alignment tests.

### Phase 5 — Setup catalogue and confluence
Normalize recovered video setups and Academy setups into a single schema. Keep unverified video-derived setups as research drafts, not live signals. Add entry, confirmation, invalidation, stop, targets, timeframe, regime, source, and evidence fields.
Acceptance: every setup has deterministic rules or is explicitly marked discretionary/unverified.

### Phase 6 — Lab, backtest and Academy feedback
Prioritize existing R1 Trend Daily with costs, R2 Location+Levels, R3 Mean Reversion with ADX gate, R4 session sweep, R5 FVG/OB, R6 absorption journal, then R10 Trend+MR portfolio. Require adequate sample size (n >= 30 as minimum gate from current owner decision), costs, out-of-sample and walk-forward where appropriate.
Every validated detector updates INDICATOR_MAP, AI school notes, visual lessons, examples, and BACKTEST_EVIDENCE. The Academy explains what the Radar displays; the Radar links to the relevant lesson and setup card.

## Paid options — reference only, not approved for purchase
- TBTflow: free scans; paid passes advertised at ₹499/week, ₹999/month, ₹2,399/quarter.
- OptionAlgo: free screens/backtests/guides; Analytics Pro ₹999/month; Order Flow ₹1,999/month.
- Bookmap: Digital Free; Digital Plus advertised $19/month; Global $49/month, excluding market-data subscriptions.
- ATAS: Start free; Plus/Pro/Ultra are paid tiers. Not needed for initial build.
- FMP Starter advertised $19/month billed annually; Twelve Data Grow $79/month; neither needed for initial free-first phase.
Prices are snapshots from public pricing pages on 2026-11-09 and may change. Do not purchase without separate owner approval.

## Known validation limits
Prior repository notes include tests that passed on isolated/stubbed data but do not prove live exchange connectivity or production UI behavior. Verify the actual current main branch and CI before claiming a feature is complete. No live order execution is in scope.


## Visual design system — owner reference images (2026-11-09)
Treat the three uploaded references as the product's visual identity, not generic inspiration:
- Radial intelligence: circular/radial KPI compositions, segmented rings, gauges and orbital indicators for aggregate state and confluence.
- Data observatory: dense multi-panel analytics, fine grid lines, waveform/area plots, distribution tables and connected-node visualizations.
- Institutional command center: one wide operational canvas with many synchronized panels and persistent agent/alert activity.
Do not copy illegible pseudo-text or decorative fake numbers from the references. All labels must be readable, values sourced, and charts tied to real data contracts.

### Tokens
- Canvas #090D11; panel #111820; raised panel #172129; subtle grid #26333B.
- Gold #D8B46A = key levels / targets / premium attention.
- Cyan #36D6CE = live feed / flow / active data.
- Green #36C98F = positive / confirmed bullish.
- Red #F06464 = negative / risk / bearish.
- Amber #E8A85B = warning / candidate / stale soon.
- Text #E7ECEF; muted #93A1AA.
Color is never the sole carrier of meaning; pair with labels, icons, arrows, line styles and numeric values. Use restrained glow only for active states.

### Density and layout
- Default desktop is a single high-density canvas, not a page of tall cards.
- Three visual layers: (1) 3–5 decision KPIs in the header, (2) synchronized central chart/flow/radial context, (3) compact detail strips, tables and agent trace.
- Combine related views into one canvas and use compact segmented controls / drawers for detail. Keep no more than six top-level Radar destinations; prefer one page with contextual panels.
- Avoid excessive donut charts, 3D charts, decorative gradients, illegible labels and equal visual weight across all widgets.
- On mobile, reflow into priority summary + one primary chart + compact agent/alert strip; do not squeeze the full desktop wall into a narrow viewport.

### Interaction model
- Cross-filtering: selecting symbol/timeframe/level in any panel synchronizes the other panels.
- Hover/focus tooltips reveal exact values, source, venue, timestamp and formula.
- Clicking an agent marker opens its live activity trace, evidence and recommended next action; agent suggestions never silently alter a trade or execute an order.
- Agent rail shows specialist identity, status, last action, source evidence and confidence/evidence quality. Use a visible activity timeline / trace tree, pause and dismiss controls, and an audit log. Agents are not animated mascots that move randomly; their movement must point to a real alert, chart level or action.
- Guided pointers are contextual, dismissible and rate-limited. Each pointer names the reason and linked evidence.
- Support layout options: Observatory (radial/analytical), Command (wide operational wall), Compact (high-density reading). Persist user choice after implementation.

### Agent roles for Radar
- Market Scout: breadth, relative strength, rotation, regime.
- Flow Analyst: trades, CVD, delta, OI/funding when source supports them.
- Liquidity Sentinel: book validity, depth, spread, sweeps, absorption candidates.
- Auction Guide: VWAP, value area, POC/HVN/LVN and acceptance/rejection.
- Risk Guardian: invalidation, event risk, data freshness, risk limits.
- Research Tutor: links signals to Academy lessons and Lab evidence.
Each agent must expose status (idle/working/attention/error), exact inputs, timestamp, result and evidence level. If the required data source is missing/stale, agent status is blocked/limited rather than fabricating a conclusion.

### Accessibility and performance
- Contrast, legible numeric typography, aligned values, keyboard focus, reduced-motion preference, responsive layout.
- No continuous decorative animation. Use short purposeful state transitions; honor reduced motion.
- Lazy-load secondary visualizations; reuse cached normalized data and shared filters to avoid duplicate API requests.
- Each panel must expose a compact/expanded mode and a last-updated/source marker.
