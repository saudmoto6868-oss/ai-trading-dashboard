# TIA image research extraction — first pass

Date: 2026-11-10  
Status: **Educational reference / unvalidated**  
Inputs: ten user-provided chart-reference images (pattern sheets, candlestick cheat sheets, volume-profile diagrams, and footprint/order-flow screenshots).

## What was extracted

1. **Price action:** head-and-shoulders and inverse, double/triple tops and bottoms, ascending/descending/symmetrical triangles, flags, wedges, channels and ranges.
2. **Candlesticks:** long-body candles, marubozu, doji variants, hammer/hanging man, inverted hammer/shooting star, engulfing, piercing/dark-cloud, morning/evening star, soldiers/crows, tweezers, inside/outside bars and harami.
3. **Volume profile:** POC, VAH, VAL, 70% value area convention, HVN and LVN; profile period/anchor matters.
4. **Order flow:** footprint, bid/ask imbalance, delta, absorption and exhaustion are concepts requiring verified trade-side data.

## TIA integration rules

- These images are reference material, not evidence that a setup is profitable.
- No pattern is a signal by itself. TIA must first establish regime and location, then require confirmation and explicit invalidation.
- Volume profile must be disabled/unavailable unless a true volume-at-price adapter is connected. Candle OHLCV cannot recreate it faithfully.
- Footprint and delta must be disabled/unavailable unless exchange prints are classified by aggressor side with known coverage and latency.
- Never infer institutional intent from an HVN, POC, open interest, or a static screenshot alone.
- No image-derived rule may send or prepare a live order.

## Proposed deterministic workflow

1. Higher-timeframe regime and levels.
2. Structure/pattern detection using confirmed swing points.
3. Candle confirmation at the level.
4. Volume-profile context only with actual volume-at-price.
5. Order-flow confirmation only with verified trade-side prints.
6. Entry, stop/invalidation, target, cost and risk calculation.
7. Store as a hypothesis until the project evidence gate is passed.

## First implementation boundary

The structured catalog lives in `data/tia_visual_knowledge.json` and is loaded by `modules/tia_visual_knowledge.py`. It is intended to let the TIA UI explain what evidence is required and whether a data adapter is available. It must not silently turn reference patterns into trading signals.

## Not done / not claimed

- No computer-vision extraction of exact geometric coordinates from the reference sheets.
- No validated candle or chart-pattern detector was created by this extraction.
- No true volume-at-price or footprint feed was added.
- No backtest or browser/mobile UI test has run in this change.
