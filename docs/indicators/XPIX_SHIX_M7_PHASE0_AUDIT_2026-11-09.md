# XPIX-SHIX-FIX M7 — Phase 0 Source Audit

Date: 2026-11-09  
Source: `XPIX-SHIX-FIX_M7  107.txt` on `main` (Pine v6 source embedded at lines 190–4005).  
Inventory: `docs/indicators/xpix_shix_m7_inventory.md`.  
This is a source-level audit and port specification. No Pine source has been changed and no Workspace feature is declared ported.

## Executive decision

Proceed only with a staged, isolated port. Do not attempt a one-shot 3,816-line translation. The source combines several independently testable systems: trend/signal state, trade management and historical outcome labels, multi-symbol/MTF tables, structure/liquidity, multiple order-block/imbalance layers, sessions, lower-timeframe candle-volume estimates, MCDX-derived signals and SMT.

The existing inventory correctly counts the source constructs, but its counts are not a semantic port map. Each family below requires calculation, event timing, invalidation, visuals, alert and test parity.

## 1. Source integrity and scope

- File length: 4,011 lines / 159,016 characters.
- Embedded Pine section: approximately lines 190–4005; scraped TradingView page text exists before and after it and must not be parsed as Pine.
- Pine version: v6; indicator uses `overlay=true`, `behind_chart=true`, and limits 500 labels, 500 lines and 100 boxes.
- Inventory: 3,816 Pine lines, 177 inputs / 28 groups, 19 `request.security` calls, 25 alerts, 48 labels, 33 lines, 20 boxes, 4 tables, 16 helper functions and 2 user-defined types.
- The source header explicitly says structural review only and asks for TradingView compilation verification. No TradingView runtime verification is available in this workflow.
- Provenance mismatch remains: inventory mentions `docs/xpix-shix-m7-source`, while the source is retrievable from `main`. Do not infer or invent the missing branch history.
- The source file must remain immutable during porting. Treat the exact Pine source as a versioned reference fixture.

## 2. Feature-family map and port requirements

| Family | Source area | Port requirement |
|---|---|---|
| EMA ribbon / core signals | approx. 329–392 and signal handling | Preserve exact EMA lengths, crossover semantics, bar-close confirmation, signal priority and alert dedupe. |
| Current trade state / ATR SL and TP | approx. 393–910 | Explicit state machine; entry bar, stop/target levels, same-bar TP/SL ambiguity policy and lifecycle parity. |
| Historical signal storage / outcomes | approx. 429–1223 | Bounded history, deterministic pruning, no backfilled signal presented as live-known; same-bar outcome rules. |
| Screener / MTF trend dashboard | approx. 1233–1809 | Per-symbol and per-timeframe provider mapping, coverage, rate limits, completed HTF bars, symbol availability and request failure states. |
| XPIX structure / liquidity / FVG / IFVG | approx. 1811–1993 | Confirmed pivots, BOS/CHoCH event timing, sweep semantics, zone score, create/extend/flip/invalidate/prune lifecycle. |
| Supply/demand map | approx. 1995 onward | Compare against existing Workspace zones; preserve separate semantics and avoid double-rendering or duplicate alerts. |
| Order blocks / volumetric structures | approx. 2130 onward | Identify actual source formula and source candle; distinguish true exchange volume from derived candle-volume estimates. |
| Sessions / kill zones | approx. 2500 onward | Exchange timezone, DST, overnight boundaries, session transitions, holidays and historical/live parity. |
| Lower-timeframe volume analysis | approx. 3152 onward | Source uses `request.security_lower_tf` and classifies sub-bars by close > open / close < open. This is **candle-direction volume estimation**, not bid/ask aggressor delta or executed trade-side volume. |
| MCDX-derived signals | approx. 3850 onward | Treat as a derived oscillator/heuristic; validate source formulas and close confirmation; do not claim institutional money flow. |
| SMT | approx. 3903 onward | Confirmed pivots on both symbols must refer to synchronized source bars; missing sessions/gaps and different market hours must be explicit. |

## 3. Specific correctness observations

### A. Confirmed structure and FVG layer
- `ta.pivothigh/low(high/low, len, len)` only returns a pivot after right-side bars have elapsed. The line is drawn back at `bar_index - pivotLen`; a port must preserve the confirmation timestamp separately from the visual pivot timestamp.
- BOS/CHoCH events are guarded by `barstate.isconfirmed` and a broken-state flag. Preserve one event per confirmed swing level.
- Sweeps are close-back-inside conditions on a confirmed bar. They are not proof of resting liquidity being consumed; name them wick sweeps, not verified order-book events.
- FVG creation is confirmed-bar only. IFVG flips occur on a confirmed close through the far edge. Preserve exact far-edge semantics and the direction-code lifecycle.
- FVG score includes HTF trend, ATR gap size, recent structure/sweep evidence, premium/discount location and structure alignment. The score is a heuristic, not a probability or expectancy score.
- Active FVG boxes are bounded by `xpixMaxFVG`; preserve pruning and avoid allowing drawings to expand the price scale.

### B. MTF requests
- The six dashboard `request.security` calls use `lookahead_off` with current HTF EMA values. On a lower timeframe, the still-forming HTF candle can evolve. `lookahead_off` prevents historical future leakage but does not by itself make the live HTF value final/closed. A port must distinguish provisional current-HTF state from last-completed-HTF state.
- The XPIX HTF filter at lines 1905–1906 uses prior HTF values `close[1]` and `ta.ema(close,50)[1]` with `lookahead_on`, which is a common confirmed-HTF pattern. Preserve and test it as a separate, explicit rule.
- The nine screener requests use the chart timeframe. Symbol availability, exchange calendars, currency, session gaps and request failures must not become a neutral/bearish value or zero.

### C. Volume/delta terminology
- The lower-timeframe helper sums volume where sub-bar close > open and close < open. It does not know whether a buyer or seller initiated the trades. It must be labelled `up-candle volume estimate` / `down-candle volume estimate`, never exchange bid/ask delta, CVD or footprint aggressor volume.
- True aggressor-side data requires a trade feed that provides aggressor side or a documented inference method with its limitations.

### D. Historical trade outcome ambiguity
- The historical TP/SL state must be audited for candles where both stop and target are inside the same OHLC range. OHLC alone cannot reveal which was hit first. Do not award the favorable outcome by assumption. Mark ambiguous, use lower timeframe/tick data, or apply a declared conservative stop-first rule.
- Historical labels are drawn at historical bars; their display must retain the actual confirmation time so they are not mistaken for information available at the earlier visual bar.

### E. Object limits and visual behavior
- Pine sets 500 labels, 500 lines and 100 boxes. The port needs bounded object registries and cleanup on symbol/timeframe changes, history resets and layer toggles.
- All overlays must be price-scale neutral unless a layer intentionally plots a price series. Test zoom, pan, auto-scale, symbol changes and mobile rendering.
- Avoid duplicate IDs and duplicate alerts after reconnect, backfill or repeated polling.

## 4. Non-negotiable port contract

1. Preserve the original Pine file and record its exact checksum in the implementation manifest.
2. Store source bar time, confirmation bar time, source timeframe and calculation version for every event.
3. No future leakage. No pivot event before right-side confirmation. No confirmed HTF signal from an evolving candle.
4. Closed-bar signals by default. Provisional intrabar values, if ever exposed, must be separately labelled and excluded from historical confirmed stats.
5. Distinguish real trade-side volume, exchange-reported volume, lower-timeframe candle-direction estimates and unavailable data.
6. Every source-dependent output declares provider, symbol, timeframe, timestamp/age, coverage and quality state.
7. Every stateful zone/trade event has a bounded lifecycle, stable ID and dedupe key.
8. Same-bar TP/SL ambiguity is explicit and conservative.
9. All drawings are bounded, cleaned up and price-scale neutral.
10. Do not silently change original defaults or confluence thresholds.

## 5. Proposed implementation sequence

### Phase 0 — completed source inventory; semantic audit captured here
Produce a complete group-by-group feature map, including inputs, calculations, events, outputs, alerts, object lifecycle and known ambiguity. The existing inventory gives structural counts; implementation work must extend it with semantic behavior.

### Phase 1 — trend core
Implement EMA ribbon and core signals only. Build deterministic OHLC fixtures and compare signal direction, source bar, confirmation bar and ATR levels. Keep screener disabled/out of scope for this first slice.

### Phase 2 — structure and liquidity
Implement confirmed pivots, BOS/CHoCH, wick sweeps, EQH/EQL and FVG/IFVG lifecycle with source/confirmation timestamps.

### Phase 3 — zones
Implement each order-block and supply/demand family independently after documenting its actual source formula. Do not collapse visually similar zone types into one generic algorithm.

### Phase 4 — sessions and MTF
Add timezone/DST-safe session logic and separate provisional vs completed HTF values. Only then consider multi-symbol screener work, with provider coverage and rate-limit budgets.

### Phase 5 — advanced layers
Add lower-timeframe volume estimates, MCDX-derived signals, SMT and statistics. Keep estimated volume distinct from true aggressor-side order flow.

## 6. Validation gates

- Deterministic Python reference calculations and fixture candles for every family.
- If the owner can provide exported TradingView values, compare source outputs on matching bars; without them, state that parity is against our own interpretation, not TradingView.
- Timeframes: 1m, 5m, 15m, 1h, 4h and 1D where supported.
- Live-bar vs closed-bar tests; HTF boundary tests; session/DST tests.
- Same-bar TP/SL tests; missing bars; exchange holidays; partial symbol history.
- Browser tests for pan/zoom, scale, symbol/timeframe changes, reload, backfill, reconnect and mobile layout.
- Unit tests, integration tests and a focused MR for each phase. No phase is production-ready on mock tests alone.

## Status

Phase 0 source-level audit is recorded. No XPIX code has been ported, no TradingView compilation has been verified, no Workspace regression tests have been run, and no merge/deployment has occurred.
