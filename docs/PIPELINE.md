# A+++ pipeline (item 25) - how the parts must connect

## What the lab already says (STRATEGY_LAB.md, real candles, no costs)
- Only **`level`** passes the edge gate (n ~3150, +0.08R vs random -0.02R). Everything else: no proven edge yet.
- Top by avg R but **not significant**: `sma1040` (n 78), `sess_amd` (n 360), `wavec` (n 88).
- **Stacking detectors does NOT help**: "4+ families agree" = -0.06R, worse than 1-2 families. Counting votes of
  correlated pattern detectors is not confluence - they mostly read the same candles.

## How institutions do it (the chain)
Desks do not add pattern votes; they filter by **independent layers**, each answering a different question:

| # | layer | question | in the app today | lab tag |
|---|---|---|---|---|
| 1 | Regime | is the market moving at all? | ATR / `mtf` | `reg`: ATR% >= 0.8x its 100-bar median |
| 2 | HTF bias | which side is the tide? | `mtf`, trend filter | `htf`: 100-bar trend on the trade side |
| 3 | Location | is price cheap/expensive in its range? (value, premium/discount) | volume profile, POC, levels, Fib | `loc`: long in the lower third / short in the upper third of the 50-bar range |
| 4 | Trigger | what exactly fires the entry? | 35 detectors (`signals.py`) | detector key |
| 5 | Participation | is real volume behind it? | order flow, delta, VP | `vol`: bar volume >= 1.2x 20-bar mean |
| 6 | Timing | is it a liquid session? | kill zones, sessions | `time`: London / New York |
| 7 | Risk | fixed stop / target | 1.5 ATR stop, 1.5R | same for all (comparable) |
| 8 | Review | expectancy per setup + grade | journal, Performance | grade table below |

**Grade** = how many of the 5 context layers agree: A+++ = 5, A+ = 4, A = 3, B = 2, C = 0-1.

## Gates (nothing is "A+++" by opinion)
A grade or a "grade / detector" combo counts only if: **n >= 100, t > 3 vs random direction, avg R > 0 in the first half
(in-sample) AND the second half (out-of-sample)**. Under n = 30 = not evidence. Costs are not modelled, so real results are worse.

## Plan (executed in order, each step measured)
1. **Done (code):** lab tags every signal with the 5 layers + grade + in/out-of-sample half; report section "Chain grades".
   Unit-tested on synthetic candles only. Real numbers need the GitHub Actions lab run (this sandbox cannot reach price APIs).
2. Read the result: which layers add R on their own ("layer X" vs "no X"), which grade passes the gate, which detector
   inside which grade.
3. Wire the winners: scanner ranks by measured grade (not by number of agreeing detectors); Setup Card shows the grade
   and the 5 layers; signals in failing combos get demoted.
4. Journal: store the grade + layers with every trade; Performance shows win % / avg R per grade, so live trades check the lab.
5. Repeat weekly (lab cron); keep only what still passes out-of-sample. Drop layers that do not help.
