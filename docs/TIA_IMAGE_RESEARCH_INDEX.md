# TIA Image Research — Reference Batch 01

Status: originals archived in the ChatGPT Library; extracted knowledge is tracked in this repository. The original JPEG binaries are **not yet committed to GitLab**.

## Original image archive

All 10 original JPEGs are stored under the Library folder `/TIA Image Research/Originals/`:
- TIA-Reference-1.jpg through TIA-Reference-10.jpg

## Reading guide and research queue

The ten-image batch covers four related domains. The image-to-topic grouping below is a first-pass index; verify individual diagrams against the original before using any specific rule.

| Image IDs | Topic | What to learn | Missing continuation / research required | TIA treatment |
|---|---|---|---|---|
| 1–3 | Price-action structures | Swing structure; ranges; double/triple tops/bottoms; head-and-shoulders; triangles; flags; wedges; channels | Objective swing/pivot definitions; breakout vs fakeout; retest rules; volume/context; measured-move math; invalidation; failed-pattern examples | Reference only until objective detectors and out-of-sample tests exist |
| 4–6 | Candlestick patterns | Single-, double- and multi-candle formations; rejection, momentum and indecision | Exact OHLC definitions; body/wick thresholds normalized by ATR; trend/location context; close-confirmation; next-bar trigger; invalidation; sample size and expectancy | Educational reference; never a standalone signal |
| 7–8 | Volume Profile | POC, VAH, VAL, value area, HVN/LVN, session profiles | Volume-at-price source; profile anchor/session; value-area algorithm; developing vs fixed profile; session boundaries; futures/spot venue differences; acceptance/rejection and retest playbooks | Blocked until verified volume-at-price is available |
| 9–10 | Order Flow / Footprint | Bid/ask volume, delta, imbalance, absorption and exhaustion concepts | Classified trade prints; aggressor-side methodology; exchange/feed coverage; timestamp alignment; aggregation; latency; spoofing/iceberg caveats; repeatable confirmation rules | Blocked until verified classified trade prints are available |

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

### Priority 1 — Setup definitions
- Build an objective price-action glossary: swing high/low, BOS, CHoCH, range, breakout, retest, failed breakout.
- For each pattern, collect complete lessons including prerequisites, confirmation, invalidation, targets and failure cases.
- Convert candle names into measurable OHLC/ATR rules; distinguish candle recognition from trade entry.

### Priority 2 — Market context and confluence
- Study trend/range regime filters and multi-timeframe alignment.
- Study session context and opening-range behavior without assuming one session model fits every instrument.
- Study liquidity sweeps and auction acceptance/rejection as hypotheses that need measurable definitions.
- Prevent double-counting correlated confirmations (e.g., candle pattern + price pattern from the same bars).

### Priority 3 — Data and validation
- Identify a trustworthy volume-at-price provider and document venue, contract, session and aggregation semantics.
- Identify a trustworthy trade-print feed with aggressor classification for footprint/delta.
- Define data quality checks, missing intervals, timestamp alignment and replay capability.
- Create labeled examples and a chronological evaluation set.

## Research guardrails

- A diagram is a learning reference, not evidence of profitability.
- POC is not guaranteed to act as a magnet; VAH/VAL depend on the profile period and algorithm.
- The common 70% value-area convention is not a universal law.
- OHLCV candles cannot reconstruct true volume-at-price or true bid/ask footprint.
- Open interest or profile shape alone does not prove institutional intent.
- Pattern detection must use only information available at the decision time; confirmed pivots are delayed by their right-side confirmation bars.
- No image-derived rule may place or authorize an order.
- Do not mark a setup validated until realistic costs, chronological out-of-sample testing and forward observation support it.

## Suggested TIA workflow

Image → concept card → missing-lesson checklist → objective rule specification → labeled examples → deterministic detector → candidate-only report → backtest → paper/forward review → promotion decision.

Current status remains `educational_reference_unvalidated`. Volume Profile and Footprint remain blocked pending the required source data.
