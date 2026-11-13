# Claude handoff — 2.6

Review and continue this isolated research task. Do not merge, deploy, wire signals, or edit live strategy/dashboard modules.

## Read first
- research/strategies/2.6/README.md
- research/strategies/2.6/event_study.py
- tests/test_two_six_event_study.py
- docs/MEETING_ROOM.md entry for 2026-11-13

## Owner objective
Determine whether Matimatiki 2.6 has a reproducible statistical edge on gold, improve test quality rather than tune for a prettier win rate, and preserve all evidence/links. Exact workstream name: **2.6**.

## Review checklist
1. Audit pivot confirmation: no pivot or anchor may be used before right-side bars close.
2. Check alternating-pivot selection and document ambiguous double pivots.
3. Verify event timestamps, entry fill, horizon indexing, spread units and OHLC validation.
4. Prevent overlapping/clustered events inflating effective sample size; add event de-clustering and block bootstrap.
5. Keep retracement and liquidity-projection hypotheses separate.
6. Obtain broker XAUUSD M1/M5 exports; GC=F is futures, not spot. Never reuse CFX n=83 as a 2.6 result.
7. Confirm creator rules: anchor, wick/body, direction, stop, TP, invalidation, session and timeframe. Mark unverified rules.
8. Pre-register 60/20/20 chronological train/validation/test; preserve an untouched final holdout. Compare r={2.5,2.6,2.618,1/0.382,2.7} without selecting on final test.
9. Add spread, commission, slippage and realistic execution. Use worst-case if SL and TP fall in one candle.
10. Report n, hit rate, expectancy R, profit factor, max drawdown, average R, confidence intervals, net t-stat and regime breakdowns. No edge claim unless n>=100 and net t>3 under project policy.
11. Add reproducible tests and save raw-input provenance / SHA-256 hashes. No fabricated performance numbers.
12. Append review results to workstream notes and reply in the MR.

## Known context
1/2.6 = 38.4615%, close to but not equal to Fibonacci 38.2%. 13/5=2.6 and 89/34≈2.618; proximity does not prove creator derivation. Direct Gann/Square-of-Nine derivation is not established. See README.
