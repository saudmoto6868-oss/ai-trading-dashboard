# V7 / CFX master plan: agents, strategies, studies, tools, indicators (2026-11-12)

Owner request: V7 should work "via agents" (reasoning, strategies, studies, every tool, every indicator), is still missing a lot, and must keep improving. This plan is built from what is already in the repo, read on 2026-11-12: `docs/TIA_FOUNDATION.md` (seven specialist functions), `docs/SCHOOLS_COVERAGE_2026-11-06.md`, `docs/TASK_QUEUE.md`, `research/cfx/CFX_REQUIREMENTS.md`, `docs/V7_CFX_AUDIT_2026-11-12.md`. NOT read for this plan: the full chat transcripts (only the written docs), `strategy_lab` result files, `cfx_pipeline.py` / `cfx_lib.py`.

## 0. Key finding
The platform already has most of the engine V7 needs: the Scanner (`signals.py` DETECTORS, `scorer.py`), the weekly Lab (`strategy_lab.py`, walk-forward, costs, random baseline), the Day plan pieces (HTF alignment, sessions), SMT, order flow (72 h real trades for crypto). CFX re-implemented many of these separately for gold. **V7 should be a front end + agent layer over the existing engines, not a third copy.** Where CFX has a definition the platform lacks (CISD span, OB volume share, XPIX levels), port it with a test; where the platform already has a measured result, show that result.

## 1. The seven agents, mapped to V7
Same seven responsibilities as TIA (not seven separate AI instances): each one is a deterministic module first; an LLM may only EXPLAIN its output (cached per setup id, hard daily cap, stored short analysis rather than raw candles, per the token budget rule).
| # | Agent | Job in V7 | Exists today | Missing |
|---|---|---|---|---|
| 1 | Intelligence Director | Combine the other six into one verdict: LONG / SHORT / WAIT with the reasons that agree, the ones that conflict, and the invalidation | TIA `tia_intelligence.director_report`; CFX side panel (why / invalidation / weak alt) as a static snapshot | V7 director over LIVE data; conflict list (not only a count) |
| 2 | Market Intelligence | Session, kill zone, calendar / news, cross-asset (DXY, yields) | session maths (`TCE.nextSession`, `intermarket.session_of`); `news_feed.py`, `calendar_feed.py` | news tied to the symbol; DXY series for SMT on gold; an event study before any "news moves price" claim |
| 3 | Technical Intelligence | Structure (swings, BOS / CHoCH), levels (PDH / PDL, XPIX, EQH / EQL), zones (OB, FVG, breaker), fib / OTE, MTF bias | scanner tags; TIA CONF (4 timeframes); CFX snapshot has all, static | live versions of each, each tested against its definition |
| 4 | Order Flow & Liquidity | Delta, footprint, DOM, tape, liquidity pools | real crypto trades (72 h), book snapshots, source badges planned | gold has no tape: say "not available" (no estimated chips without data); taker-volume delta for big timeframes (Binance probe pending) |
| 5 | Strategy & Innovation Lab | Which rules are worth keeping | weekly lab with keys per school; pre-registration docs | V7's own rules (variant B and the CFX pipeline) are not in the lab; ablation by tool |
| 6 | Quant Validation & Risk | n, expectancy, costs, drawdown, risk size | `risk_policy.py` (0.25 % base, A+ 0.50 % with n >= 30), lab statistics | CFX still uses its own risk default (0.5) and R:R 1.5; must call the policy and R:R >= 2 |
| 7 | Trade Review & Decision | Challenge the plan (skeptic), rank, journal, learn | Order Flow Desk skeptic, Journal, Portfolio widget | a V7 plan card with the skeptic's objections and the measured history of that setup type |

## 2. Schools: measured status (from the repo, not from the images)
| School | Platform status | What V7 may do |
|---|---|---|
| Trend / MA / VWAP / Donchian | scored, in lab | indicators + context |
| SMC / ICT (OB, FVG, breaker, CISD, MSS, PD, Silver Bullet) | scored or flags, most in lab | tags with the lab number next to them |
| Liquidity (sweep, CRT) | scored, lab | same |
| Time / sessions | scored, lab | display + gate |
| Fibonacci / OTE | scored, lab | same |
| Elliott | context only (lab: ew3 -0.13 R, n = 775) | never a signal |
| Harmonic | radar flag only | context |
| Gann | lab says zone entries do not beat a random direction (n >= 100 on 1h / 4h) | map / confirmation only |
| Wyckoff, price action, chart patterns | NEW context detectors (2026-11-06), measured next weekly lab run | context until n >= 30 with costs |
| Momentum / divergence | confirm only | indicator |
| Intermarket SMT | board + tag, lab with peers | needs DXY for gold |
| Volume profile, anchored VWAP, pivots | not scanner setups | candidates (ranked idea 5) |

Rule from the docs: nothing is promoted without n >= 30 and real costs; an edge is claimed only at n >= 100 and t > 3.

## 3. What is missing, ranked (usefulness x feasibility)
1. **Day plan board** (top-down, per symbol, grouped by session / kill zone, with the schools that agree): ranked #1 in the schools audit, pieces exist, board does not. This is the natural home of the Director agent.
2. **Live V7 structure tools** (sessions, PDH / PDL, XPIX, EQH / EQL, FVG, 50 %, swings with BOS / CHoCH, OTE) with parity tests.
3. **Ablation study**: each tool / school added or removed from a setup, on long history, costs included, vs random direction. This is the only honest way to find the best combination; it needs a data source with years of candles and owner approval of a pre-registration file.
4. **Risk alignment**: CFX uses `risk_policy.py` and R:R >= 2.
5. **Exits**: time stop and "exit when the school's invalidation breaks" (missing per the audit); partial / trailing exist and are measured.
6. **News + calendar tied to the symbol** with an event study.
7. **Telegram alerts** for SMT and for V7 setups, only after a rule is measured.
8. **Volume-profile setups**, anchored VWAP, pivots as lab keys.
9. **Order-flow chips** for symbols that have real trades only.
10. Not now: Gann scanner bounce (needs the grid decision), Elliott as a signal, any gold order-flow claim.

## 4. Continuous development loop
Weekly: (a) lab run measures every key, including new ones; (b) a short report lists what changed (n, expectancy, vs random); (c) nothing is promoted without the thresholds above; (d) the V7 page shows the latest numbers next to each tool and the date of the run.
Per change: pre-registration (when a new rule), parity test against a Python reference, MR, CI `mr_tests`, review, owner browser check.
Owner-visible: every tool shows source, timestamp, n and status; unavailable data says "not available".

## 5. Decisions needed from the owner
1. Build order: Day plan board first, or live structure tools first?
2. CFX uses the platform risk policy and R:R >= 2 (yes / no).
3. Approve the ablation study: which instrument (gold perp on Hyperliquid, crypto on OKX, or both) and how much history we may download.
4. LLM explanations: allowed for the Director's wording only, cached per setup, daily cap (yes / no).
