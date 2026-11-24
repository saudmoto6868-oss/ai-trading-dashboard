# X77 — pre-registered school-pair test (2026-11-21)

Status: FROZEN at the commit that adds this file. Written before any pair result was opened.
Any change after a run = a new registration with a new date.

## Why pairs
The "count of agreeing families" score was killed on history (see `X77_PREREG_COMBINER_2026-11-21.md`, addendum).
This tests a narrower idea: a few pairs that the schools themselves teach as one setup.
Pairs were picked from doctrine only, not from lab numbers. The lab's per-pair outcomes were not opened.

## The 4 pairs (no others, no re-cuts)
| id | name | side A | side B | source of the idea |
|---|---|---|---|---|
| P1 | Sweep then OTE | `sweep` | `ote` | ICT: liquidity raid, then entry in the 62-79% retracement |
| P2 | Sweep + divergence | `sweep` | `rsi_div` or `macd_div` | reversal: stop raid confirmed by momentum divergence |
| P3 | Candle at level | `level` | `pa_engulf` or `pa_pin` | classic price action: rejection candle on support / resistance |
| P4 | Trend pullback to Fib | `ma_cross` or `ema_stack` | `fib` | trend following: buy the retracement inside an MA trend |

Keys are the repo detector keys (`modules/signals.py`, `modules/pa_patterns.py`), run with `detect_all(win, detectors=...)`
limited to: ma_bull, fib_bull, ote_bull, sweep_signal_bull, key_level_bull, rsi_div_bull, macd_div_bull, pa_engulf_bull, pa_pin_bull.

## Pair rule
At bar i, pair fires in direction d when side A AND side B each fired in direction d at some bar in [i-2, i],
and at least one of them fired at bar i. One trade per pair per market per 6 bars (cooldown). Window = last 400 bars (lab WIN).

## Trade and label (same as `modules/strategy_lab.py`)
Entry = close of bar i. Stop = 1.5 x ATR14. Target = 1.5R. Time exit 48 bars (1h), marked to market.
Same bar touching stop and target = stop. Cost = 0.10R per trade (lab `COST_R`). Outcome = net R.

## Data
Markets = `strategy_lab.SYMBOLS` (12: gold, silver, WTI, Brent, EUR, JPY, GBP, S&P 500, Nasdaq-100 via Hyperliquid xyz; BTC, ETH, SOL via OKX).
Timeframe 1h, 1,500 bars per market, fetched once with `strategy_lab._fetch` on the run date.

## Stage 1 — history (kill only, one run)
All this history was already used by the single-detector labs, so it can only reject.
A pair is KILLED if: n < 30, or net mean R <= 0, or net mean R <= 0 in either time half.
A pair that survives is NOT evidence. It only earns a forward test.

## Stage 2 — forward (confirm), from 2026-11-22 00:00 UTC
Same code, only signals at or after that time. Pass needs all of:
- n >= 100 trades for that pair, across >= 60 distinct days;
- net mean R > 0 with t > 3, standard error clustered by day;
- net mean R > 0 in both time halves.
4 pairs are tested; t > 3 (p about 0.0027) covers that many at 0.05 after Bonferroni.
Short n = "inconclusive", not pass and not fail.

## Report, not gated
Per pair: win %, gross and net mean R, n per market. A random-direction baseline on the same bars.

## Result — stage 1 history, run once on 2026-11-21 (`research/x77_pairs.py`, output `research/x77_pairs_history.json`)
12 markets, 1h, 1,500 bars each (about 57 days), net of 0.10R cost. No fetch errors.

| Pair | n | days | win % | net mean R | t (day-clustered) | half 1 | half 2 | random baseline | verdict |
|---|---|---|---|---|---|---|---|---|---|
| P1 sweep + OTE | 253 | 53 | 43.1 | -0.042 | -0.55 | -0.026 | -0.058 | -0.170 | KILLED |
| P2 sweep + divergence | 495 | 56 | 38.2 | -0.144 | -2.00 | -0.275 | -0.013 | -0.134 | KILLED |
| P3 candle at level | 523 | 57 | 39.6 | -0.130 | -2.54 | -0.104 | -0.156 | -0.031 | KILLED |
| P4 trend pullback to Fib | 964 | 57 | 41.1 | -0.081 | -1.60 | -0.211 | +0.050 | -0.148 | KILLED |

All 4 pairs fail the history rule (net mean <= 0). Stage 2 (forward) is not run: nothing survived.
P1 and P4 lose less than a random direction on the same bars, but are still below zero after costs; that is not an edge.
Limit: only ~57 days of 1h history per market (the data source cap at 1,500 bars), so this is one market period.
