## Owner-approved scope
Build a new independent Workspace widget named **XPIX Intelligence** (internal panel type: `intel`) that unifies the existing Footprint, Order Flow, Liquidity Map, DOM, Time & Sales, Limit Tracking, Volume Profile, Flow Confluence, Setup Card, Signals and Risk outputs, while preserving each existing tool as a standalone panel.

This owner instruction explicitly expands the previous Order Flow-only scope to include development and integration of the existing Footprint, Order Flow and Time & Sales tools. It does not authorize merging to main, deployment, paid API purchases, connecting brokerage/trading accounts, or automated order execution.

## Current repository facts audited on 2026-11-09
- Project: `6868-group/ai-trading-dashboard`, default branch `main`.
- Workspace is generated: edit `modules/ws/*`, then run `python3 scripts/build_workspace.py`; do not edit `modules/workspace_app.html` directly.
- Existing parts include `13_okx_levels_regime_footprint.js`, `22_ofmap.js`, `23_orderflow.js`, `24_flow_confluence_misc.js`, `25_guide.js`, and `22_panels.js`.
- Existing UI includes Footprint, Order Flow/Heatmap, DOM, Time & Sales/Tape, Limit Tracking, Volume Profile, Setup Card, Signals/Alerts, Flow Confluence, and Guide.
- Existing Guide text can use OpenAI when configured; current live voice path is Gemini Live via `modules/guide_ai.py` and `modules/guide_bridge/`. Reuse/extend rather than duplicate.
- Workspace parts must remain synchronized with generated HTML and existing Playwright/mock tests.
- Prior Order Flow visual regression requirements remain: heatmap/bubbles must not paint over candles when the dedicated column is closed; scale, pan, zoom, resize, reload and data freshness must be checked.
- The existing Footprint behavior is a protected baseline: capture regression tests/screenshots before changing its calculation or rendering.

## Widget identity and UX
- Display name: **XPIX Intelligence**.
- Internal panel type: `intel`.
- Purpose: a decision-support workspace, not a replacement chart or an auto-trading bot.
- Tabs/sections: Overview, Footprint Lab, Order Flow, Liquidity Map, Time & Sales, DOM Analytics, Auction & Volume, Options/GEX, Setups, Trade Plan, Risk & Execution, AI Voice.
- Arabic-first Egyptian Arabic explanations, preserving standard trading terms (POC, Delta, OFI, Absorption, DOM, Stop, Target).
- The assistant must explain the evidence, missing data, conflicting signals, entry zone, invalidation/stop, targets, position risk and why a setup is rejected.
- Voice should announce material state changes and trade-plan updates, be user-controllable (mute, voice on/off, push-to-talk/interrupt), and never repeatedly speak on every price tick.
- Voice output must be grounded only in the structured decision packet; do not invent prices or imply certainty.
- Keep an explicit distinction between measured facts, calculated features, hypotheses, and model-generated explanations.

## Inputs and data contracts
1. Market context: symbol, asset class, venue, session, timeframe, OHLCV, ATR/realized volatility, VWAP/AVWAP, profile levels, market regime.
2. Executed flow: exchange timestamp, receive timestamp, trade ID/sequence, price, quantity, aggressor side if known, venue/source.
3. Resting liquidity: book snapshot + sequenced deltas, side, price, quantity, order count if available, source, sequence continuity, latency, snapshot recovery state.
4. Footprint: per-price bid/ask volume, delta, cumulative delta, imbalance definitions, bar/session boundaries and source quality.
5. Options/derivatives (only where available): option chain, expiry, strike, right, volume, OI, IV, Greeks, underlying, timestamp; futures/crypto OI, funding, liquidations.
6. Provenance/quality: source, venue, timestamp, delayed/live flag, missing-data state, aggregation method, estimated-vs-exchange volume, confidence/quality status.

Normalize events without pretending that different venues are one central order book. XAUUSD broker CFD volume/book must remain distinct from COMEX GC; each crypto exchange book remains separately identified; stocks require venue/consolidated-feed distinctions.

## Engines and outputs
- Market Context Engine: AMT, balance/imbalance, acceptance/rejection, Market Profile/TPO, Volume Profile, VWAP, regime.
- Footprint Engine: bid/ask at price, delta/CVD, diagonal/stacked imbalance, absorption candidates, exhaustion candidates.
- Tape Engine: trade velocity, size anomalies, burst detection, aggressor-side confidence.
- Order Book/Liquidity Engine: spread, depth imbalance, OFI, liquidity persistence/pulling/replenishment, sweep candidates, book resilience; only when feed quality supports the feature.
- Derivatives Engine: OI/funding/liquidations and options Greeks/GEX where the source supports them; label dealer positioning as estimated, never direct fact.
- Setup Engine: rule-based candidates for value rejection/acceptance, failed auction, LVN traversal, absorption, imbalance continuation, delta divergence, OFI momentum, liquidity sweep/reclaim, VWAP reclaim/rejection, opening-range/initial-balance and derivatives context.
- Risk/Trade Manager: structural/profile/ATR/volatility/time invalidation stops; fixed-R/profile/liquidity targets; partial exits, trailing, time exits; quantity from risk budget, contract multiplier, tick value and estimated costs.
- Decision packet output: `bias`, `setup_id`, `status` (watch/wait/ready/invalid/no-trade), `entry_zone`, `trigger`, `invalidation`, `stop`, `targets[]`, `risk_per_unit`, `position_size`, `R_multiple`, `evidence[]`, `conflicts[]`, `data_quality`, `source_timestamps`, `expiry`, `reason_ar`, `spoken_summary_ar`.
- Every output must carry symbol, venue, timeframe and as-of timestamp.

## Safety and decision governance
- Advisory / paper-first only. No brokerage connector, account credentials, wallet, order placement or automated execution.
- Human remains responsible for every trade decision.
- LLM explains and summarizes; deterministic engines calculate price levels, risk, sizing and state transitions.
- A separate verifier checks quote freshness, symbol/venue match, stop/target arithmetic, minimum reward/risk policy, conflicting signals and missing fields before any spoken recommendation.
- If data is stale, sequence gaps exist, market is closed, venue is unknown, or required fields are missing: return WAIT / NO TRADE and explain why.
- Never call a quality/evidence score a win probability. No profitability claims without out-of-sample evidence after costs.
- No paid API or workflow runs without a separate owner approval. No secrets in code, docs, commits, or tool outputs.

## Implementation phases
### Phase 0 — Audit and baseline
Map current panel types, state, feeds, storage, rendering, tests, Guide and voice bridge. Capture current Footprint/Order Flow/Tape behavior and record known gaps. No code changes to live calculations before the baseline.
### Phase 1 — Widget shell
Add `intel` panel to Workspace through the source parts; create responsive tabs, state contract and empty/loading/stale/error states. No duplicate data polling.
### Phase 2 — Existing tool integration
Read existing shared Hub/cache outputs for Footprint, OF, DOM, Tape, Limit Tracker, VP and Flow Confluence. Do not create competing feeds or poll the same endpoint again. Add cross-panel navigation/highlighting.
### Phase 3 — Decision packet and deterministic verifier
Implement normalized features, setup explanations, risk calculations and fail-closed validation. Start with a small, explicit setup set; each setup separately testable.
### Phase 4 — Arabic AI copilot
Extend the existing Guide, reuse the current text provider routing and voice bridge where suitable. Evaluate ChatGPT/OpenAI voice as a provider option without breaking Gemini Live. Add push-to-talk, interrupt, mute, event throttling and spoken trade-plan summaries.
### Phase 5 — Replay and research
Historical replay, event alignment, signal logging, backtest with spread/fees/slippage, walk-forward and out-of-sample checks. No mock result described as evidence.
### Phase 6 — Cross-market adapters
Implement per-market adapters for crypto exchanges, futures, US equities/options, XAUUSD/FX, EGX and Tadawul. Track venue/source and data entitlements independently.

## Acceptance criteria
- Existing panels continue to work independently; no duplicate polling.
- Footprint parity tests pass against baseline.
- Order Flow rendering isolation and pan/zoom/scale tests pass.
- Time & Sales freshness, ordering, deduplication and reconnect behavior pass.
- Widget clearly shows source, venue, timeframe, timestamp, live/delayed and data quality.
- Every setup has written entry, trigger, stop, target, invalidation, sizing and failure conditions.
- Arabic explanation matches the deterministic packet; no fabricated levels.
- Voice is opt-in/controllable and event-driven, not every tick.
- No order execution or account connection.
- All new tests pass; tests not run are explicitly listed.
- Work remains on `feat/xpix-intelligence-workspace`; no merge/deploy without separate owner approval.

## Initial files to audit
`modules/ws/22_panels.js`, `22_ofmap.js`, `23_orderflow.js`, `13_okx_levels_regime_footprint.js`, `24_flow_confluence_misc.js`, `25_guide.js`, `modules/guide_ai.py`, `modules/guide_bridge/index.html`, `modules/workspace.py`, `scripts/build_workspace.py`, existing tests under `tests/browser/` and `tests/test_*`.
