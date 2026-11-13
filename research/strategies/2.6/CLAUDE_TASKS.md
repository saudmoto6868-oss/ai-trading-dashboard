# Claude Work Orders — 2.6 Strategy Intelligence

Owner-approved scope: **full / multi-market / research-only**. Work only on branch `research/strategy-2-6-2026-11-13` and paths under `research/strategies/2.6/`, plus the explicitly authorized meeting-room log entry. Do not merge, deploy, enable live trading, or modify CFX/XPIX.

## Task 1 — Audit current implementation (first priority)
Review `event_study.py` and tests. Check:
- pivot confirmation timing and all lookahead paths;
- leg direction, anchor selection, ratio arithmetic, touch definition;
- duplicate/overlapping events and same-bar ambiguity;
- forward-window censoring and missing/gapped bars;
- cost units and whether costs are applied consistently;
- metric definitions and test completeness.
Deliver a written review with severity, file/line references, minimal fixes, and new regression tests. Do not rewrite the algorithm before documenting findings.

## Task 2 — Formalize hypotheses
Write `docs/RULEBOOK.md` and `docs/EVENT_DEFINITIONS.md`. Specify H1 retracement and H2 liquidity projection independently. Record unresolved creator-specific rules as UNKNOWN. No inference from promotional or trade-showcase reels.

## Task 3 — Data contract and validation
Implement canonical OHLCV schema, dataset manifest, timezone normalization, duplicate/gap checks, OHLC integrity checks, symbol metadata, and explicit cost metadata. Add synthetic fixtures only. Do not download or commit licensed broker history or secrets.

## Task 4 — Controls and evaluation protocol
Add matched random/control events, chronological train/validation/untouched holdout, event de-clustering, bootstrap/permutation diagnostics, parameter-neighborhood checks, and multiple-testing disclosure. Preserve negative results. Do not tune on holdout.

## Task 5 — Reports
Generate a reproducible report with event counts, touch rates, time-to-touch, MFE/MAE, forward horizons, cost assumptions, confidence intervals, and stratification by instrument/timeframe/side/session/regime. Keep H1 and H2 results separate.

## Task 6 — Multi-market readiness
Implement instrument metadata abstractions. Validate XAUUSD spot first. Add FX only after the XAUUSD pipeline and tests are stable. Keep broker feeds separate and GC=F proxy explicitly distinct.

## Task 7 — UI and paper simulation (later; gated)
Only after owner approves the research core, propose UI wiring for 2.6 LAB and deterministic paper-only simulation. UI must display Research/Simulated labels and provenance. No live order endpoint or broker credentials.

## Required Claude response format
1. Findings (critical/high/medium/low)
2. Files changed and rationale
3. Tests run with exact command and result
4. Remaining unknowns / blockers
5. Data required from owner
6. Explicit confirmation: no CFX/XPIX changes, no merge, no deployment, no live trading

## Acceptance criteria
- Causal/no-lookahead behavior covered by regression tests.
- H1/H2 are separate in code, data, metrics, and reports.
- Dataset provenance and costs are explicit.
- Reproducible run from config + manifest + revision.
- CI/test status reported honestly; quota failures are not described as test failures.
- All changes remain isolated on the research branch pending owner review.
