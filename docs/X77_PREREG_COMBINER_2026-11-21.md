# X77 phase 4 — pre-registered confluence test (2026-11-21)

Status: DESIGN ONLY. Nothing run. Freeze this file (commit hash) before any run; any change after a run = new registration.

## Hypothesis (one)
Trades with confluence score >= 3 have net mean R > 0 and beat score = 1 trades, out-of-sample.

## Frozen inputs (confirm against the labs before freezing)
- Universe: 10 symbols (to pick), one timeframe 1h. Costs ~0.14% round trip (crypto) — check the lab's cost figure.
- Detectors: `modules/x77_detect.py` (repo detectors only), mapped to 8 signed families:
  SMC structure, liquidity sweep, MA trend, divergence, Elliott, candle, chart pattern, Wyckoff.
  A family fires if any member fired in the same direction in the last 3 bars.

## Label
Triple barrier: stop -1R (1 x ATR14), target +1.5R, time exit 24 bars, entry next bar open. Outcome = net R after costs.
Fixed 24-bar return: robustness report only, not in the gate.

## Models
- Primary: count score = number of agreeing families (0-8), threshold k = 3 fixed now. No fitted parameters.
- Secondary (one only): L1 logistic on 8 families + regime; C by inner CV on train only. No trees.
- No hand-picked combos (pairs of 40 detectors = 780 tests = snooping).

## Split
Walk-forward, expanding train >= 12 months, 3-month test blocks, 5 folds. Purge 24 bars + embargo 24 bars. One open trade per symbol.

## Contamination
All history was already seen by the single-detector labs. History can only kill the idea. Only forward data after the registration date can confirm it.

## Statistics
Aggregate R by day (or cluster SE by date). Uplift vs score = 1: daily block bootstrap, 5,000 resamples.
Multiple testing: 3 tests (primary, L1, fixed horizon), Bonferroni; owner bar t > 3 kept.

## Pass rule (all, forward out-of-sample, one run, fail closes it)
- n >= 100 trades with score >= 3, across >= 60 distinct days.
- Net mean R > 0, clustered t > 3.
- Positive in both halves.
- Uplift vs score = 1 > 0, one-sided p < 0.01.

## Power warning
R sd ~1.2: t > 3 at n = 100 needs ~+0.36R per trade (unrealistic). A real 0.1R edge needs ~1,300 trades.
Short n = "inconclusive", not "pass" and not "fail".

## Report, not gated
Dose-response (mean R at score 1, 2, 3, 4+). Random-entry baseline matched on direction + regime (1,000 permutations).

Source: design reviewed by one advisor question (Fable), 2026-11-21. Numbers marked "confirm" still need checking against the lab code.

## Addendum 2026-11-21 — history check (from the existing lab run, nothing new run)
The strategy lab already measures confluence (`modules/strategy_lab.py`, "confluence": families agreeing on one bar,
majority vote, same 1.5 x ATR stop / 1.5R target). Latest saved run: `data/strategy_lab.json`, commit b0997ef1
(2026-11-17), 12 markets x 5 timeframes, gross R (no costs):

| Families agreeing, no opposition | n | win % | avg R gross |
|---|---|---|---|
| 1 | 30 | 33.3 | +0.041 |
| 2 | 404 | 40.3 | +0.067 |
| 3 | 1,187 | 39.3 | +0.054 |
| 4+ | 951 | 36.5 | -0.057 |

Score >= 3 pooled: n = 2,138, avg about +0.005R gross, about -0.095R after the lab's 0.10R cost.
No dose-response (more agreement does not raise R; 4+ is the worst). Win rates sit at or under the 40% break-even of a 1.5R target.

Verdict: **killed on history.** The run differs from this registration (all timeframes pooled, lab family set, majority vote,
48-bar horizon on 1h), but the gross mean is near zero with n > 2,000, so a 0.10R cost cannot be beaten by re-cutting the
same data. The forward test is not worth running for "count of agreeing families". A new hypothesis (for example
specific family pairs under one regime) needs its own registration before any data is looked at.
