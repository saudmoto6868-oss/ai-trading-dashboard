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

## Result of the first real lab run (data/strategy_lab.json, built 2026-10-31, 12 symbols x 5 TFs, 1.5 ATR stop, no costs)
Read honestly - **the chain did NOT raise quality yet**:
- All 62,719 signals: avg R -0.019 (t -0.79). No row passes the gate (`edge` = 0 rows).
- **Grade does not rank trades**: A+++ n 485 -0.040R, A+ n 9,671 -0.016R, A n 21,849 -0.031R, B -0.013R, C -0.008R.
  More agreeing layers did not mean better trades. Do **not** wire "grade" into the scanner ranking as a quality score.
- Layers one by one (avg R with the layer vs. without): `loc` (location) +0.023R with t 2.25 and positive in BOTH halves
  (IS +0.020 / OOS +0.026) vs -0.031R without it (t -2.10): the only layer that is consistent in both halves - keep testing it.
  `htf` with the layer -0.026R (t -2.45) is worse than without (-0.009R); `vol` has t +2.93 but both halves negative;
  `reg` (volatility) and `time` show nothing.
- Best detectors (n >= 100): `sess_amd` n 663, +0.117R at RR 1.5 (+0.22R at RR 3, t 3.2); in the chain "A+ / sess_amd" n 122 +0.204R
  (IS +0.245 / OOS +0.163, t 2.47). Promising but it does NOT pass the gate (t < 3 at RR 1.5, ~50 detectors x several RRs were tested, so a
  t of 3 is partly luck, and the per-detector rows carry no IS/OOS split yet). `sma1040` +0.5R but n 49 = not evidence.
- **Earlier claim withdrawn**: `level` "passes the edge gate" (+0.08R, n 3,150) - on the larger run it is -0.003R at RR 1.5 (n 5,098, t -0.15).
- Not tested: trading costs / slippage, other stop sizes per layer, the lab's 1m series are shortest history, no live data.

## Next (measured, not guessed)
0. **Done (code, awaiting the next weekly lab run):** chain table now has `loc / <detector>` and `no loc / <detector>` rows (n, t vs random, IS/OOS halves, `net` = avgR - 0.10R cost). Per-detector rows already compute IS/OOS in code; the committed JSON rows predate that (they show no t / IS / OOS), the next run fills them. Mock-tested on synthetic candles only.
1. Add IS/OOS halves to the per-detector rows (needed to judge `sess_amd`).
2. Test `loc` as a hard filter on the 2-3 best detectors (only `sess_amd` first), with a cost model (0.05R/trade) and a fresh out-of-sample window.
3. Journal (step 4) stays: store grade + layers so live trades confirm or kill this.
Nothing is promoted to "A+++" until it passes: n >= 100, t > 3, positive in both halves, after costs.
