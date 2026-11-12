# TIA: real order flow on every timeframe + measured chart / candle patterns (plan, 2026-11-10)

Owner request: order flow must reflect real executed trades / order book / time & sales on ALL timeframes up to weekly and monthly, use what the research tabs added, and add chart-pattern and candlestick-pattern indicators after studying their schools.

## 1. Data truth table (what is real, what is an estimate)
| Layer | Real source | History | Honest status |
|---|---|---|---|
| Executed trades (footprint, T&S) | OKX public trades ws, stored in the browser (IndexedDB) | 72 h per symbol, only while the app is open | REAL, minutes/hours only. A permanent recorder exists (`recorder/`) but is not hosted. |
| Order book (DOM / heat map) | OKX / Hyperliquid book | latest snapshot only; no book history exists at the provider | REAL now, never historical. Any book picture on 1H+ is an estimate and must be labelled. |
| 1H / 4H / 1D order flow today | estimated traded-volume layer + book coverage bar (merged earlier, mock-tested) | candles | ESTIMATE |
| Weekly / monthly | none of the above | - | no real trade-level data can exist from public OKX; needs a different source |

## 2. Proposal: real delta on every timeframe from taker volume (to verify)
Binance public klines carry `taker buy base volume` per candle, so delta = 2 x takerBuy - volume exists for any interval including 1w / 1M, with years of history. This is real (aggressor side), not a footprint. Plan:
1. Feasibility check from a real browser (CORS, region, rate limit). NOT testable from the sandbox. Owner / Antigravity runs it.
2. If it works: a `Delta (taker)` sub-pane for BTC/ETH/etc. pairs on 15m..1M, tagged `REAL DELTA - Binance spot taker volume`, other symbols tagged `ESTIMATE`.
3. Every order-flow widget shows a source badge: REAL TRADES (72 h) / REAL DELTA (taker) / BOOK SNAPSHOT / ESTIMATE. No badge = not shown.

## 3. Patterns: measure, do not just mark
Existing: `modules/patterns.py` (chart patterns), `modules/chart_scan.py`, `modules/chart_explain.candles` (own simple geometry, Nison-style names), Radar candlestick filter (`modules/fv_screen.py`). Lab result already recorded: walk-forward Gann zones do not beat a random direction (n>=100 on 1h / 4h) so Gann stays a map / confirmation only.
Plan:
1. Study the schools first (Nison for candles, Edwards & Magee / Bulkowski for chart patterns). Write one table per pattern: definition, bias, failure rule, source. (ChatGPT research task.)
2. Run the existing walk-forward engine (`modules/backtest_tf.py`) per pattern x timeframe vs a random-direction baseline, with costs.
3. Show on the chart only: pattern label + measured hit rate + n; under n=30 print `not evidence`. A pattern whose edge does not beat random is drawn as `context`, never as a signal.
4. New indicator only after steps 1-3, built as a Workspace part in `modules/ws/` (then `python3 scripts/build_workspace.py`).

## 4. Who does what
- ChatGPT: step 3.1 research tables (schools, definitions, failure rules, sources). No code.
- Antigravity: browser feasibility of the Binance taker-volume delta + screenshots of order-flow widget on 1H / 1D / 1W today (what is shown, with which labels).
- Claude: badge system for order-flow widgets, delta sub-pane (after feasibility), pattern stats display, review.
- Owner: tell us if Binance is reachable from the browser in your region; decide whether to host the footprint recorder.

## Not done / not tested
Nothing here is built. Sandbox cannot reach price sites. All claims about Binance klines are from the public API description, unverified in this project.
