# Playbooks: one trading style at a time (item 25)

Rule: each style has its own timeframe, its own tools, its own RR and its own journal row. Nothing is promoted to "live" until
the lab shows n >= 100, t > 3 vs random, and a positive result in BOTH halves (in-sample and out-of-sample). Costs are not in the lab.

## Tools by layer (same order as docs/PIPELINE.md)
1. Regime: ATR% (not dead) - all styles
2. Bias: HTF trend (mtf) - all styles; a style uses the next HTF up (scalp 15m, intraday 4h, swing 1w)
3. Location: value area / POC, levels, premium-discount of the 50-bar range
4. Trigger: ONE detector family per style (see table) - never stack families for "more votes" (lab: 4+ families = -0.06R)
5. Confirmation: order flow / volume (only where the journal shows it helps)
6. Timing: session (London / New York for intraday; daily for swing)
7. Risk: stop = 1.5 ATR, target chosen by the exit test (below), risk <= 1% of account per trade, stop trading for the day after -3R
8. Review: journal row keeps style, layers, R. Read it weekly per style, not all at once.

## Styles (status from the data we have, 2026-10-18)
| style | timeframe | evidence so far | status |
|---|---|---|---|
| Scalp | 1m | journal: 737 trades, -151R, win 32% | OFF (already off by default, SCAN_1M). Only back on with a lab pass |
| Intraday | 1h | journal: longs +18R (136 trades, win 46%), shorts -48R (145, win 27%) | Longs only, as a CANDIDATE; re-test out-of-sample |
| Swing | 1d | journal: 70 trades, -12.5R (small) | Watch only; no conclusion |
| Position | 1w | journal: shorts +37R, win 90%, but n=30 | NOT evidence; keep on paper until n >= 100 |

## RR and exit (what to test, not what to assume)
- Break-even win rate = 1 / (1 + RR): 40% at 1.5R, 33% at 2R, 25% at 3R. Add 2-5 points for costs (research note).
- The lab now tests RR 1.0 / 1.5 / 2.0 / 3.0 and break-even stops on the SAME entries (table "Exit variants").
- Pick the RR with the best expectancy AND positive in both halves. Do not pick the RR with the highest win rate alone.

## Risk (conventions, not lab results)
- Max 1% of account per trade; max 3R loss per day then stop; max 3 open trades in the same direction (MAX_SAME_SIDE already exists).
- A plan is only "taken" when price touches the entry (the chart shows a waiting label until then).

## Next steps (in order)
1. Lab run (in progress) -> read "Exit variants" and "Chain grades" per style timeframe.
2. Per style, pick ONE rule that passes the gate, put it in the scanner config for that style only, and record it here with the date.
3. Journal: export weekly; compare each style to its own row above. Change a rule only after 100 trades in that style.
