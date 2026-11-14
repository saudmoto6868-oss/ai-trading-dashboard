# 2.6 rulebook (Task 2) — what the code tests, rule by rule

Status words: **CODE** = implemented exactly as written; **ASSUMPTION** = our choice, not from the creator;
**UNKNOWN** = not verified from the creator's own explanation (promotional / showcase reels are not evidence).
Source ledger: `README.md` (only DfopgmVi8Wu and DewFqk8inTf explain a calculation; medium confidence).

## Shared (H1 and H2)
| rule | value | status |
|---|---|---|
| Pivot | bar high (low) strictly the unique max (min) of `left`+1+`right` bars; default 3 / 3 | CODE + ASSUMPTION (window size) |
| Pivot known at | bar `idx + right` closes (no use before that) | CODE |
| Bar that is both pivot high and low | skipped (OHLC cannot tell which came first) | CODE |
| Leg | two **adjacent** pivots of opposite kind; same-kind neighbours are kept, never replaced by a later extreme | CODE |
| Ratios compared | 2.5, 2.6, 2.618, 1/0.382 (2.61780), 2.7; 2.6 is primary | CODE; why 2.6 = UNKNOWN |
| Entry | resting limit placed after the bar that reveals the anchors closes; fills on the first touch within `wait_bars` (80) | CODE + ASSUMPTION |
| Gap through the limit | fills at the bar open (price improvement) | ASSUMPTION — a touch is not a guaranteed fill (queue, spread side) |
| Cost | one scalar per filled event, price units, from the dataset manifest | CODE; real spread / commission = owner's broker |
| Outcome | forward close at 5 / 10 / 20 / 40 bars and MFE / MAE over 40 bars after the fill bar, all ÷ leg span | CODE (descriptive, not P&L) |
| Fill-bar excursion | not counted in MFE / MAE (order inside the bar unknown) | CODE — limitation |
| Stop loss / take profit / invalidation | none simulated | **UNKNOWN** |
| Timeframe, session, instrument | any; XAUUSD spot first | **UNKNOWN** (creator's own TF not verified) |
| Wick vs body anchors | wicks (high / low) | **UNKNOWN** |

## H1 — retracement (`event_study.py`)
| rule | value | status |
|---|---|---|
| Up-leg L→H | BUY limit at H − (H − L) / r (r 2.6 = 38.46 % back) | CODE; creator's use as retracement = UNKNOWN |
| Down-leg H→L | SELL limit at L + (H − L) / r | CODE |
| Which leg | every adjacent leg, no size / trend filter | ASSUMPTION |

## H2 — liquidity projection (`h2_liquidity.py`) — never pooled with H1
| rule | value | status |
|---|---|---|
| Pool | two adjacent same-kind pivots within `eq_tol` 0.05 % of price, ≤ 100 bars apart, nothing traded beyond in between; level = the more extreme | ASSUMPTION (reel DfopgmVi8Wu shows EQH) |
| Sweep | first later bar (≤ 200) with wick through the level and close back inside; a close beyond first = breakout, pool consumed | ASSUMPTION |
| Leg measured | latest completed leg in the reversal direction confirmed by the sweep bar | ASSUMPTION ("measured downswing" in DfopgmVi8Wu) |
| Zone | EQH: level + span / r (SELL); EQL: level − span / r (BUY) | ASSUMPTION (reels DfopgmVi8Wu, DewFqk8inTf: "range / 2.6 projection") |

## Evaluation (`evaluation.py`, `report.py`)
De-clustered per ratio (no overlapping forward windows), 60 / 20 / 20 by date with purge, test locked, matched
random-timing controls, block bootstrap CI. n < 30 in a cell = not evidence. Choosing the best ratio is a multiple test.

## Open questions for the creator / owner
1. Retracement (H1) or projection from a liquidity level (H2), or both?
2. Stop, targets, invalidation, and when a setup expires.
3. Timeframe and session; wick or body; which leg (last impulse? minimum size?).
4. Why 2.6 and not 2.618?
