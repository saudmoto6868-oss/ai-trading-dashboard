# 2.6 — Matimatiki Strategy Research

**Status: research intake + event-study harness; no validated edge yet.**
This workstream is separate from CFX / XPIX / live trading logic.

## Scope
- Identify the exact 2.6 calculation from the creator's public explanations.
- Separate retracement-entry and liquidity-level projection hypotheses.
- Compare 2.6 against 2.618, 1/0.382, and nearby control ratios.
- Use causal pivots only; a pivot is unavailable until its right-side confirmation bars close.
- Report touch rate, forward excursion, sample size, costs, and chronological OOS results.
- Do not optimize on the final holdout; do not call a win-rate improvement an edge without costs and statistical testing.

## Current hypotheses (not verified as one unified system)
1. **Retracement:** for up-leg L→H, BUY = H − (H−L)/r; for down-leg H→L, SELL = L + (H−L)/r. At r=2.6, retracement fraction is 38.4615%.
2. **Liquidity projection:** measure a completed impulse, divide its range by 2.6, and project that distance from an EQH/EQL or other liquidity reference. Reel DfopgmVi8Wu appears consistent, but exact anchor and direction need frame-by-frame verification.
3. Test these separately. Do not blend projection setups into retracement samples.

## Evidence ledger
- DfopgmVi8Wu — https://www.instagram.com/reel/DfopgmVi8Wu/ — prior notes: EQH/SSS, sweep above highs, measured downswing, range/2.6 projection, sell zone. Medium confidence; full re-review blocked by Instagram login/analysis credits.
- DewFqk8inTf — https://www.instagram.com/reel/DewFqk8inTf/ — prior notes: measure high-to-low range and project calculated level; Sell Limit example. Medium confidence; exact SL/OCR values inconsistent and must not be adopted.
- DejFZYzi6ls — https://www.instagram.com/reel/DejFZYzi6ls/ — BUY trade showcase, not a rules explanation.
- DeefIXeCLMA — https://www.instagram.com/reel/DeefIXeCLMA/ — CPI SELL management example, not a 2.6 rule.
- DeeeG1nC8NV — https://www.instagram.com/reel/DeeeG1nC8NV/ — Telegram forecast proof, not a calculation lesson.
- De1fHArC13H, DequTz2uL3W, Den55CXtbdY — promotion/commentary, no verified 2.6 rule.
- Pending links: https://www.instagram.com/reel/DfjMQ08il9G/ ; https://www.instagram.com/reel/De1VUqhCWbN/ ; https://www.instagram.com/reel/Devxu-WCkGZ/

**Access limitation:** Instagram opened only to a login wall. vidIQ short-form analysis failed for insufficient credits; its tool reported reset on 2026-12-13. No claim is made that all reels were watched in this pass.

## Mathematics and related schools
- 1/2.6 = 0.3846153846 (38.4615%).
- 1/2.618 ≈ 0.38197097 (38.1971%); close, not identical.
- 13/5 = 2.6; 89/34 ≈ 2.617647. Numerical proximity does not prove the creator's derivation.
- Fibonacci: https://www.forex.com/en-uk/trading-academy/courses/advanced-technical-analysis/uk-fibonacci-theory/
- StockCharts: https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-annotation-tools/fibonacci-retracements
- BabyPips: https://www.babypips.com/learn/forex/fibonacci-who
- Gann primary text scan: https://djvu.online/file/EchlZmSRKlIMs — no direct 2.6 derivation verified.
- Osler / stop-loss clustering: https://www.newyorkfed.org/research/staff_reports/sr125.html
- Independent 2.6 playbook, not creator-authenticated: https://marketscore.io/blog/2-6-the-secret-unveiled
- Creator/course profile lead: https://www.coachli.co/%40dilyorjon_trades

## Existing project data caveat
The repository contains CFX research on yfinance GC=F gold futures, not broker spot XAUUSD. Existing CFX figures (n=83, TP1-or-better 37.35%, +0.238R after stated $0.30 spread) belong to CFX, not 2.6. Generic Strategy Lab figures also do not validate 2.6.

## Test harness
Input CSV columns: datetime,open,high,low,close; optional volume.
Example:
    python research/strategies/2.6/event_study.py data/XAUUSD_M1.csv --left 3 --right 3 --wait-bars 80 --horizon-bars 40 --cost 0.30
Cost is absolute price per filled event, not pips; configure it to feed/account. Test separate datasets:
- Broker XAUUSD spot M1 and M5 (primary).
- GC=F futures only as a separately labelled proxy.
- Different brokers as replication, not silently pooled.

The harness compares 2.5, 2.6, 2.618, 1/0.382 and 2.7. It records touches, time-to-fill, MFE/MAE and 5/10/20/40-bar returns in leg-range units. It does not invent stop-loss/TP rules. The event-tail split is provisional; reserve an untouched final holdout before tuning.

## Required next steps
1. Obtain real historical XAUUSD OHLC export with timezone, broker, timeframe, date range, spread/commission metadata. Never substitute synthetic bars.
2. Recheck creator videos frame by frame after legitimate Instagram access or analysis credits return. Resolve swing anchors, wick/body rules, direction, timeframe, stop, target, invalidation, and whether projection is a distinct setup.
3. Claude: review pivot causality, CSV quality, duplicate/overlapping events, same-bar ambiguity, cost model, and train/validation/untouched-test split.
4. Run separately for BUY/SELL, M1/M5, sessions, volatility and news regimes.
5. Add a trade simulation only after creator SL/TP and invalidation are confirmed. Include spread, commission, slippage, latency, partial exits, and worst-case same-bar SL/TP.
6. Compare matched random entries, 38.2%, 2.618, nearby ratios and simple swing retracement.
7. Robustness: bootstrap confidence intervals, block bootstrap/permutation, parameter neighbourhood, walk-forward, multiple-testing correction. Project gate: n>=100 and net t>3 before any edge claim.
8. Keep research-only. No live signals, XPIX, CFX, dashboard or execution wiring without a new owner instruction.

## Conversation archive\nSee CONVERSATION_LOG.md for the owner requests, decisions, current blockers, links to the branch/MR, and exact test/CI status.\n\n## Current test status
Unit tests added for arithmetic, pivot confirmation delay, leg direction and comparator grid. **Not run on historical XAUUSD candles.** No accuracy, win rate, expectancy or profitability number is reported.
