# 2.6 — Matimatiki Strategy Research

**Status: isolated research workstream; no validated edge.** This project is separate from CFX, XPIX and live trading.

## Owner-approved scope
- Full standalone research product.
- Multi-market roadmap: XAUUSD first, then FX, then indices.
- Research mode only: historical studies, reproducible backtests and paper simulation. No live execution.
- Work remains on `research/strategy-2-6-2026-11-13`; do not merge without owner approval.

## Hypotheses
1. **H1 — Retracement entry:** for an up-leg L→H, candidate BUY = H − (H−L)/r; for a down-leg H→L, candidate SELL = L + (H−L)/r. Primary r=2.6; comparators 2.5, 2.618, 1/0.382 and 2.7.
2. **H2 — Liquidity projection:** measure a completed impulse, divide its range by r, then project from an independently identified EQH/EQL or swept liquidity reference. H2 is a separate event builder in `h2_liquidity.py` (run: `python3 research/strategies/2.6/h2_liquidity.py bars.csv --out DIR`; tests: `tests/test_two_six_h2.py`). Its pool / sweep / leg / zone rules are research assumptions documented in the module docstring; creator rules remain UNKNOWN. Not run on real XAUUSD data yet.
3. ICT/SMC, Fibonacci, Gann, session, volatility and news filters remain optional experiments, not assumed rules.

## Evidence ledger
- DfopgmVi8Wu — https://www.instagram.com/reel/DfopgmVi8Wu/ — prior notes: EQH/SSS, sweep above highs, measured downswing, range/2.6 projection, sell zone. Medium confidence; full re-review blocked by Instagram login/analysis credits.
- DewFqk8inTf — https://www.instagram.com/reel/DewFqk8inTf/ — prior notes: measure high-to-low range and project calculated level; Sell Limit example. Medium confidence; exact SL/OCR values inconsistent.
- DejFZYzi6ls — https://www.instagram.com/reel/DejFZYzi6ls/ — BUY trade showcase, not rules explanation.
- DeefIXeCLMA — https://www.instagram.com/reel/DeefIXeCLMA/ — CPI SELL management example, not a verified 2.6 rule.
- DeeeG1nC8NV — https://www.instagram.com/reel/DeeeG1nC8NV/ — Telegram forecast proof, not a calculation lesson.
- De1fHArC13H, DequTz2uL3W, Den55CXtbdY — promotion/commentary; no verified 2.6 rule.
- Pending: https://www.instagram.com/reel/DfjMQ08il9G/ ; https://www.instagram.com/reel/De1VUqhCWbN/ ; https://www.instagram.com/reel/Devxu-WCkGZ/

**Access limitation:** Instagram opened to a login wall. vidIQ analysis failed for insufficient credits; its tool reported reset on 2026-12-13. No claim is made that all reels were watched in this pass.

## Mathematics and references
- 1/2.6 = 0.3846153846 (38.4615%).
- 1/2.618 ≈ 0.38197097 (38.1971%); close but not identical.
- 13/5 = 2.6 and 89/34 ≈ 2.617647; numerical proximity does not prove the creator's derivation.
- Fibonacci: https://www.forex.com/en-uk/trading-academy/courses/advanced-technical-analysis/uk-fibonacci-theory/
- StockCharts: https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-annotation-tools/fibonacci-retracements
- BabyPips: https://www.babypips.com/learn/forex/fibonacci-who
- Gann primary text scan: https://djvu.online/file/EchlZmSRKlIMs — no direct 2.6 derivation verified.
- Osler / stop-loss clustering: https://www.newyorkfed.org/research/staff_reports/sr125.html

## Existing data caveat
The repository's CFX research uses yfinance GC=F gold futures, not broker spot XAUUSD. CFX figures (n=83, TP1-or-better 37.35%, +0.238R after stated $0.30 spread) belong to CFX and must not be attributed to 2.6. Generic Strategy Lab figures also do not validate 2.6.

## Current event-study harness
`event_study.py` currently tests H1 retracement only. It:
- delays pivot availability until right-side confirmation bars close;
- does not retrospectively replace earlier same-side pivots with later extrema;
- treats a touched level as a simulated limit fill and applies opening-price improvement on a gap through the limit;
- reports descriptive forward returns and MFE/MAE in leg-range units.

It is **not** a full P&L backtest. It does not verify SL/TP, sizing, partial exits, queue position, spread decomposition or realistic slippage. Its 70/30 event-tail summaries are descriptive and must not be called out-of-sample validation. Overlapping events remain a dependence risk.

CSV fields: datetime,open,high,low,close; optional volume. Timestamps must be valid ISO-8601, strictly increasing and unique. Prices must be positive and OHLC-consistent.

Example:
```bash
python research/strategies/2.6/event_study.py data/XAUUSD_M1.csv --left 3 --right 3 --wait-bars 80 --horizon-bars 40 --cost 0.30
```
Cost is an absolute price amount per filled event, not pips. Supply a cost assumption consistent with the instrument/account. Do not treat this single scalar as a complete spread/commission/slippage model.

## Required next steps
1. Obtain broker XAUUSD spot M1/M5 OHLC data with timezone and cost metadata; never substitute synthetic bars.
2. Recheck creator videos frame by frame after legitimate access or analysis credits return.
3. H2 builder done (assumption-based, synthetic-tested only); confirm its rules against the creator's videos and run it on real data.
4. Add matched controls, event de-clustering, block bootstrap/permutation, walk-forward and an untouched final holdout.
5. Add trade simulation only after creator SL/TP and invalidation rules are confirmed.
6. Add FX only after the XAUUSD pipeline is stable; keep each broker feed and GC=F proxy separately labelled.

## Test status
Unit tests cover ratio arithmetic, pivot confirmation delay, no retrospective same-side pivot replacement, leg direction, gap-fill assumption, per-event normalization, descriptive split labelling, and CSV timestamp/duplicate rejection. Passing unit tests do not establish market performance.

See `CONVERSATION_LOG.md` for owner decisions, constraints, branch/MR links and prior CI status.

## Data-contract hardening (2026-11-13)
- Timestamps are now required to be timezone-aware ISO-8601 values; naive datetimes are rejected.
- Non-finite cost and ratio parameters (NaN/Infinity) are rejected.
- A candle that is simultaneously a unique local high and low is excluded from pivot output because OHLC data cannot establish the intrabar order. This is a conservative ambiguity policy, not a claim that such bars never occur.

## Research Lab UI shell

A first static research dashboard shell is available at [app/2_6_lab.html](app/2_6_lab.html). It intentionally shows no fabricated market prices, signals, or performance metrics. The chart panel remains empty until validated broker XAUUSD OHLC data is supplied. H1 and H2 status are displayed separately; H2 is explicitly marked as not implemented.

The Streamlit page is wired into the dashboard sidebar under Research Labs as `2.6 Strategy Intelligence`. The HTML file remains a standalone visual preview. The page does not fetch market data or execute trades.
