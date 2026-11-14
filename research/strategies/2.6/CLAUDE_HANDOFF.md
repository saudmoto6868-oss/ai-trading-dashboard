# Claude handoff — 2.6 Strategy Intelligence

Owner-approved scope: **full / multi-market / research-only**. Continue on branch `research/strategy-2-6-2026-11-13` only.

## Read first
- `research/strategies/2.6/README.md`
- `research/strategies/2.6/IMPLEMENTATION_PLAN.md`
- `research/strategies/2.6/ARCHITECTURE.md`
- `research/strategies/2.6/CLAUDE_TASKS.md`
- `research/strategies/2.6/event_study.py`
- `tests/test_two_six_event_study.py`
- `docs/MEETING_ROOM.md` entry for 2026-11-13

## Owner objective
Determine whether Matimatiki 2.6 has a reproducible statistical edge, improve test quality rather than tune for a prettier win rate, and preserve all evidence. The current event-study harness implements H1 retracement only; H2 liquidity projection remains separate and is not implemented.

## Self-review changes already committed
Commit `b4f370d4`:
- Removed retrospective same-side pivot replacement, which could rewrite a swing using a later, more extreme pivot.
- Added ISO-8601 timestamp parsing, strict chronological/unique timestamp validation, OHLC and positive-price checks.
- Added gap-through-limit opening-price improvement assumption.
- Corrected return normalization to normalize each event by its own leg range.
- Renamed event-tail partitions as descriptive only; they are not OOS validation.
- Explicitly labelled the harness H1-only and documented fill, overlap and cost limitations.
- Expanded tests for these cases.

## Required immediate review
1. Run: `python -m unittest tests/test_two_six_event_study.py -v` (or the repository's equivalent test discovery command).
2. Inspect all changed lines and confirm dataclass import/test discovery works in the project's Python version.
3. Check whether timestamp timezone-awareness should be enforced by the canonical dataset contract; mixed naive/aware timestamps must not be silently compared.
4. Add regression coverage for event overlap, right-boundary censoring, insufficient horizon, zero/negative parameters, malformed numeric fields, and simultaneous high/low pivots.
5. Verify the pivot sequence policy: adjacent same-kind pivots are intentionally retained; only opposite-kind adjacent pairs form legs. Do not reintroduce retrospective extrema replacement.
6. Assess the gap-fill assumption and document its limitations; a bar touch is not guaranteed execution.
7. Add event de-clustering and block bootstrap before interpreting sample size or significance.
8. Keep the 70/30 event-tail summary descriptive. Implement a date-based 60/20/20 train/validation/untouched-test split only when event overlap and horizon leakage are handled.
9. Implement H2 liquidity projection as a distinct event builder with explicit causal liquidity anchors, sweep, direction and trigger. Do not mix H1 and H2 samples.
10. Report exact commands, tests and results. Distinguish a workflow/rules/CI quota failure from a Python assertion failure.

## Research checklist
- No pivot or anchor may be used before right-side bars close.
- Prevent overlapping/clustered events inflating effective sample size.
- Obtain broker XAUUSD spot M1/M5 exports; GC=F is futures, not spot. Never reuse CFX n=83 as a 2.6 result.
- Confirm creator rules: anchor, wick/body, direction, stop, TP, invalidation, session and timeframe. Mark unverified rules as UNKNOWN.
- Add spread, commission, slippage and realistic execution. Use worst-case if SL and TP fall in one candle.
- Preserve an untouched final holdout; compare r={2.5,2.6,2.618,1/0.382,2.7} without selecting on final test.
- No fabricated performance numbers or edge claims.

## Hard boundaries
- Do not modify/import CFX or XPIX logic, configs, registries, databases or UI.
- Do not merge MR !70, deploy, add live broker connectivity, or place real orders.
- Keep all work on the isolated 2.6 research branch and report back in MR !70.


## Additional hardening committed for review
- Require timezone-aware ISO-8601 timestamps; reject naive timestamps before chronological comparisons.
- Reject NaN/Infinity for cost and ratio inputs.
- Exclude dual high/low pivot candles because OHLC bars cannot determine which extreme occurred first; add regression coverage.
- These changes still require a real local/CI test run. GitLab CI jobs were blocked before runner startup by `ci_quota_exceeded`; this is infrastructure/quota, not a Python assertion result.

## Claude review 2026-11-13 (MR !72 merged + H2)
- Fixed: limit fill missed bars gapping wholly past the level; naive-timestamp test wrote a literal backslash-n; research-labs sidebar test expected 2 labs after the 2.6 UI merge.
- Shared helpers `find_fill` / `measure` in `event_study.py` are used by H1 and H2.
- H2 implemented in `h2_liquidity.py` (EQH/EQL pool -> wick sweep with close back inside -> latest reversal-direction leg -> zone = level +/- span/ratio -> limit fill). Rules are assumptions; creator rules UNKNOWN.
- Tests: `python3 -m unittest tests/test_two_six_event_study.py tests/test_two_six_h2.py` -> 19 OK. Synthetic data only; no real XAUUSD run, no edge claim.
- Still open: de-clustering, matched controls, block bootstrap, date-based holdout, real broker data, creator SL/TP.

## Claude 2026-11-14 — Task 4 (evaluation protocol)
- `evaluation.py`: `decluster` (per ratio, drop entries inside the previous kept forward window), `split_bounds` / `segment_of` (date-ordered 60/20/20 by bar index, purge events whose window crosses a boundary), `block_bootstrap_ci` (circular blocks), `matched_controls` (same side / span / horizon / segment, random entry at bar open), `evaluate` (per ratio: raw vs de-clustered n, purged, train / validation mean + CI + control mean + vs_control; **test locked unless `reveal_test=True`**; refuses mixed H1 / H2 events).
- Tests: `python3 -m unittest tests/test_two_six_evaluation.py tests/test_two_six_event_study.py tests/test_two_six_h2.py` -> 24 OK. Synthetic only; no real XAUUSD run, no edge claim.
- Still open: parameter-neighbourhood checks, report generator (Task 5), data contract (Task 3), broker XAUUSD export (owner), creator SL / TP rules (UNKNOWN).
- Not merged to main; on branch `ccr-fba879d1-5edbbl` (GitHub). No CFX / XPIX changes, no deploy, no live trading.

## Claude 2026-11-14 — Task 3 (dataset contract)
- `dataset.py`: `build_manifest` (sha256, bars, UTC first / last, provider, symbol, asset class, timeframe, source tz, precision, contract size, spread / commission / slippage -> `cost_per_event` in price units, gap scan with weekend closes apart), `verify` (refuses a file whose bytes changed), CLI `python3 dataset.py FILE.csv --provider ... --symbol XAUUSD --timeframe 5m --spread 0.30 --write`. GC=F can never be labelled spot XAUUSD (and XAUUSD never as a futures proxy).
- Tests: `python3 -m unittest tests/test_two_six_dataset.py tests/test_two_six_evaluation.py tests/test_two_six_event_study.py tests/test_two_six_h2.py` -> 28 OK. Synthetic only.
- Owner next: broker XAUUSD export -> run the CLI with the real spread -> keep the manifest next to the CSV (CSV itself stays out of git).

## Claude 2026-11-14 — Task 5 (report)
- `report.py`: `python3 report.py FILE.csv FILE.csv.manifest.json [--horizon 40] [--key 20] [--out report.md] [--reveal-test]`. Verifies the checksum, cost = manifest `cost_per_event`, runs H1 and H2 separately; per family: descriptive table (ratio x side: n, touch % for H1, positive %, median MFE / MAE, bars to fill) + evaluation table (raw / de-clustered / purged n, train / validation mean, block-bootstrap CI, control mean, vs control, "not evidence" under n 30); test locked. Same input -> identical report.
- Fix in `evaluation.block_bootstrap_ci`: block capped at n // 2 (a block as long as the sample gave a zero-width CI on tiny samples).
- Tests: 30 OK across the five `tests/test_two_six_*.py` files. Synthetic only.
