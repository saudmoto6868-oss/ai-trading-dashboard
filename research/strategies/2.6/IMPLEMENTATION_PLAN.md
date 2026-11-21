# 2.6 Strategy Intelligence — Implementation Plan

**Owner-approved configuration (2026-11-13)**
- Scope: `full` — standalone research product.
- Markets: `multi`; rollout order: XAUUSD first, then FX majors, then selected equity/index CFDs or futures with instrument-specific data contracts.
- Mode: `research` — historical research, reproducible backtests, and paper trading only.
- Isolation: separate from CFX and XPIX. No imports, shared signal state, shared execution adapters, or changes to their code paths.

## 1. Product objective

Build an evidence-led research platform that turns the Matimatiki 2.6 observations into explicit, testable hypotheses. The platform must preserve provenance from source observation to rule, event, result, and report. It must not present an unverified setup as a validated trading signal.

## 2. Research hypotheses — never merge prematurely

### H1 — Retracement entry
For a completed directional leg with high H, low L, and range R=H-L:
- bullish leg: candidate retracement price = H - R/r
- bearish leg: candidate retracement price = L + R/r
- primary r=2.6; comparators include 2.5, 2.618, 1/0.382, and 2.7.
This hypothesis tests a price level inside the measured leg.

### H2 — Liquidity projection
Measure a completed impulse range R, calculate D=R/r, then project D from a separately identified liquidity reference (e.g. EQH/EQL or a swept level). The anchor, direction, and trigger must be explicit per setup.
This is not the same event as H1. Store and report it independently.

### H3 — Optional confluence (later phase)
ICT/SMC structure, Fibonacci, Gann, session, volatility, and news regime are optional explanatory filters. They must not be silently required for the base 2.6 hypotheses. Test each filter as an ablation and against matched controls.

## 3. Delivery phases and exit criteria

### P0 — Research contract and data specification
Deliver: rulebook, glossary, source-evidence ledger, instrument metadata schema, dataset acceptance checklist.
Exit: every rule has an unambiguous formula, direction, anchor, timeframe, timestamp convention, invalidation, and evidence grade; unknown fields remain explicitly unknown.

### P1 — Data and mathematical core
Deliver: canonical OHLCV schema, timezone-normalized ingestion, data-quality checks, ratio/level calculator, causal swing detector.
Exit: deterministic calculations; unit tests cover boundaries, missing bars, duplicates, DST/timezone conversion, and pivot confirmation delay.

### P2 — Event construction and liquidity engine
Deliver: separate H1/H2 event builders; EQH/EQL clustering; sweep definition; BOS/CHoCH definitions as optional context; event IDs and provenance.
Exit: no future leakage; event timestamp is the first time all required information is observable; overlapping events are flagged and handled by a documented policy.

### P3 — Statistical evaluation
Deliver: baseline event study, matched random/control entries, costs model, chronological train/validation/untouched holdout, confidence intervals, bootstrap/permutation checks, parameter-neighborhood sensitivity.
Exit: reproducible report by market, instrument, timeframe, side, session, and regime. No optimization on the final holdout.

### P4 — Confluence experiments
Deliver: feature flags and ablation experiments for ICT/SMC, Fibonacci, Gann, sessions, volatility, news.
Exit: incremental value is measured out-of-sample against the same baseline and matched controls. No narrative-only confluence score.

### P5 — Trade simulation and paper trading
Deliver: explicit entry/SL/TP policy only after creator rules are verified; spread, commission, slippage, latency, partial fills, same-bar ambiguity, and risk limits.
Exit: deterministic replay and paper-only order lifecycle; no broker credentials or live order routes.

### P6 — 2.6 LAB user interface
Deliver: Research Overview, Evidence Library, Setup Explorer, Chart Replay, Backtest Lab, Results/Robustness, Trade Journal, Data & Settings.
Exit: every displayed result links to dataset version, rule version, event IDs, run configuration, and report artifact.

### P7 — Multi-market expansion
Deliver: instrument adapters and per-market cost/contract metadata; XAUUSD first, FX second, indices third.
Exit: market-specific validation; never pool raw results across instruments without normalized units and stratified reporting.

## 4. Architecture boundaries

- Research domain package: formulas, pivots, liquidity events, hypothesis builders.
- Data domain: immutable raw imports plus validated normalized datasets and manifests.
- Evaluation domain: event studies, backtests, controls, statistical diagnostics.
- Application/API domain: read-only research endpoints and paper simulation endpoints.
- UI domain: research views only.
- Persistence: versioned datasets, experiment configs, event outputs, metrics, and audit log.
- No dependency on CFX/XPIX packages. If shared infrastructure is considered later, propose a separately reviewed interface; do not import their strategy logic.

## 5. Dataset and reproducibility contract

Required fields: timestamp, open, high, low, close; volume optional with source semantics. Manifest must record provider/broker, symbol, asset class, timeframe, timezone, date range, price precision, contract size, spread/commission assumptions, download time, gaps/duplicates, and file checksum. Preserve original timestamps and normalized UTC timestamps. Keep broker spot XAUUSD distinct from GC=F futures proxy and distinct broker feeds.

## 6. Evaluation protocol

- Compare r in {2.5, 2.6, 2.618, 1/0.382, 2.7}; include matched random and conventional swing-retracement controls.
- Report event count, touch rate, time-to-touch, forward excursion, MFE/MAE, and return horizons in instrument-native units and normalized R only when a valid risk definition exists.
- Apply realistic spread, commission, slippage, and execution timing. Do not invent SL/TP.
- Split chronologically; reserve an untouched holdout. Avoid leakage from pivot confirmation, scaling, normalization, labels, or overlapping forward windows.
- Report uncertainty and multiple-testing controls. A candidate research gate is n>=100 and net t-stat>3 after costs, but this is not a guarantee or substitute for independent replication.
- Negative and inconclusive results must be retained.

## 7. Safety and release gates

Default mode is research. Paper trading must be clearly labelled simulated. No live broker integration, order placement, deployment, or production alert routing. Any future change requires a new explicit owner approval and a separate security/risk review. Do not merge MR !70 without owner review.

## 8. Immediate next actions

1. Claude reviews the current event-study implementation for causal correctness and test coverage.
2. Add a formal schema and dataset validation module.
3. Write independent H1 and H2 event specifications and fixtures.
4. Add matched-control and chronological holdout evaluation.
5. Obtain broker XAUUSD M1/M5 OHLC data with timezone and cost metadata.
6. Only after XAUUSD baseline is reproducible, add FX adapter and instrument metadata tests.
