# TIA Image Research — Reference Batch 01

Status: all 10 original JPEGs are archived in the user's Library at `/TIA Image Research/Originals/`. The extracted knowledge and research index are tracked in this repository. The original JPEG binaries are **not yet committed to GitLab**.

## Image-by-image index

| Image | Visible subject | What it contributes | What is missing / what to search next | TIA status |
|---|---|---|---|---|
| 01 | Institutional/technical chart-pattern cheat sheet | Broad pattern vocabulary and schematic examples | Formal swing-point rules; pattern boundaries; breakout/retest; failure cases; target measurement; instrument/timeframe caveats | Reference only |
| 02 | Forex technical analysis chart-pattern cheat sheet | Bullish/bearish pattern examples and likely continuation/reversal families | Objective detection rules; close-confirmed breakout; retest criteria; false-break filters; invalidation and stop/target math | Reference only |
| 03 | Green/red volume-profile distribution shapes with directional sketches | Profile-shape hypotheses and possible directional interpretations | Exact meaning of each profile shape; whether bars are volume-at-price or another distribution; profile period/anchor; acceptance/rejection; sample evidence and failure examples | Reference only; do not assume directional certainty |
| 04 | Volume Profile anatomy: POC, value area, HVN/LVN, Asian range and bullish/bearish examples | Key profile vocabulary and session-context illustrations | Provider/venue; volume-at-price construction; value-area algorithm; fixed vs developing profile; session definitions; acceptance/rejection and retest rules; test the claimed session effects | Blocked pending verified volume-at-price |
| 05 | Ten-part Volume Profile with Price Action guide | A learning roadmap connecting profile concepts to execution ideas | Obtain the complete original lesson; expand each of the ten steps into rules, examples, counterexamples, entry/stop/target and risk; validate each step separately | Reference/lesson incomplete |
| 06 | Footprint/order-flow platform screenshot | Realistic footprint-style display with bid/ask or traded-volume columns | Identify platform/feed, exchange, aggressor classification, aggregation, timestamps, missing data, latency, imbalance thresholds, absorption/exhaustion definitions and replay examples | Blocked pending verified classified trade prints |
| 07 | Candlestick cheat sheet | Common single- and multi-candle pattern names and shapes | Exact OHLC rules; body/wick thresholds normalized by ATR; trend/location context; confirmation; next-bar trigger; invalidation; frequency and expectancy | Educational reference only |
| 08 | Buy/Sell candlestick-pattern sheet mixed with chart-pattern examples | A compact visual catalogue of bullish/bearish pattern labels | Separate candle patterns from chart structures; verify ambiguous labels; define objective rules and context; avoid treating BUY/SELL labels as direct signals | Educational reference only |
| 09 | Chart-pattern examples on price charts | Visual examples of head-and-shoulders, flags, triangles, wedges, double bottoms/tops and related structures | Label exact pivots; distinguish confirmed from developing patterns; breakout/retest; invalidation; measured moves; failed patterns; no-lookahead detector rules | Reference only |
| 10 | Large candlestick-pattern encyclopedia | Broad reversal/continuation candle vocabulary, including less common and multi-bar formations | Verify translations/names and exact candle sequences; remove duplicates/ambiguous variants; define OHLC/ATR thresholds, trend context, confirmation and invalidation | Educational reference only |

## Four research workstreams

### A. Price-action structures — images 01, 02, 09
Study: swing structure, ranges, double/triple tops and bottoms, head-and-shoulders, triangles, flags, wedges, channels, breakout, retest, failed breakout.
Missing: objective swing/pivot definitions, confirmed-bar timing, pattern boundaries, volume/context filters, measured-move math, invalidation and failed-pattern examples.

### B. Candlestick patterns — images 07, 08, 10
Study: single-, double- and multi-candle formations; rejection, momentum, indecision, reversal and continuation labels.
Missing: exact OHLC definitions, ATR-normalized body/wick thresholds, trend/location context, close-confirmation, next-bar trigger, invalidation, sample size and expectancy. Separate visual pattern recognition from entry logic.

### C. Volume Profile — images 03, 04, 05
Study: profile shape, POC, VAH, VAL, value area, HVN/LVN and session profiles.
Missing: verified volume-at-price source; exact profile anchor/session; value-area algorithm; developing vs fixed profile; session boundaries; venue differences; acceptance/rejection and retest playbooks. The common 70% value-area convention is not a universal law.

### D. Order Flow / Footprint — image 06
Study: bid/ask volume, footprint, delta, imbalance, absorption and exhaustion.
Missing: verified classified trade prints; aggressor-side methodology; exchange/feed coverage; timestamp alignment; aggregation; latency; spoofing/iceberg caveats; repeatable confirmation rules. OHLCV candles cannot reconstruct true bid/ask footprint.

## Required completion checklist for every candidate setup

1. Market and venue, instrument, session and timezone.
2. Higher-timeframe regime and location in the dealing range.
3. Exact formation rules and confirmed swing points (no future leakage).
4. Setup prerequisites and explicit disqualifiers.
5. Confirmation rule and the bar/event at which it becomes knowable.
6. Entry trigger, order type and realistic fill assumptions.
7. Structural invalidation and stop placement.
8. Target logic, partial exits and minimum reward/risk after costs.
9. Spread, commission, slippage, funding and liquidity assumptions.
10. Screenshot/example set: valid, failed, ambiguous and counterexamples.
11. Backtest with chronological split, out-of-sample evaluation and no lookahead.
12. Forward/paper observation and versioned change log.

## Search plan — next research tasks

Priority 1 — obtain complete lessons and objective definitions:
- Full chart-pattern course: formation, breakout, retest, invalidation, targets and failed examples.
- Full candlestick course: exact sequences and OHLC thresholds, trend/location context, confirmation and invalidation.
- Full Volume Profile lesson behind image 05, including the source methodology and each of its ten steps.
- Footprint/order-flow lesson tied to the actual platform shown in image 06, including data-source semantics.

Priority 2 — context and confluence:
- Trend/range regime filters and multi-timeframe alignment.
- Session context and opening-range behavior, tested per instrument.
- Liquidity sweeps and auction acceptance/rejection as measurable hypotheses.
- Prevent double-counting correlated confirmations (e.g. candle and chart pattern from the same bars).

Priority 3 — data and validation:
- Identify a trustworthy volume-at-price provider and document venue, contract, session and aggregation semantics.
- Identify a trustworthy trade-print feed with aggressor classification for footprint/delta.
- Define data-quality checks, missing intervals, timestamp alignment and replay capability.
- Create labeled examples and a chronological evaluation set.

## Research guardrails

- A diagram is a learning reference, not evidence of profitability.
- POC is not guaranteed to act as a magnet; VAH/VAL depend on profile period and algorithm.
- OHLCV candles cannot reconstruct true volume-at-price or true bid/ask footprint.
- Open interest or profile shape alone does not prove institutional intent.
- Pattern detection must use only information available at decision time; confirmed pivots are delayed by their right-side confirmation bars.
- No image-derived rule may place or authorize an order.
- Do not mark a setup validated until realistic costs, chronological out-of-sample testing and forward observation support it.

## Suggested TIA workflow

Image → concept card → missing-lesson checklist → objective rule specification → labeled examples → deterministic detector → candidate-only report → backtest → paper/forward review → promotion decision.

Current status remains `educational_reference_unvalidated`. Volume Profile and Footprint remain blocked pending the required source data.
