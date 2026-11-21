# TIA — Sources & Origins Research (2026-11-13)

Scope: origins and primary/academic sources for every school TIA covers (order flow, auction/profile, Wyckoff, ICT/SMC, Gann, Elliott, candles/patterns) plus validation science.
Method: web search on 2026-11-13. Bibliographic facts (journal, volume, pages, DOI) are from indexes (RePEc/SSRN/arXiv/publisher). Full texts were NOT read unless noted. Retail/vendor pages are listed only as secondary and are not evidence.

Evidence grade: **A** = peer-reviewed empirical. **B** = primary historical source / book by originator. **C** = practitioner framework, no independent validation. **D** = marketing / unverified claim.

## 1. Order flow & microstructure (the scientific core of TIA)

| Source | What it gives TIA | Grade | Link |
|---|---|---|---|
| Kyle (1985), *Continuous Auctions and Insider Trading*, Econometrica 53(6):1315–1335 | Price impact λ = slope of price on signed order flow; informed vs noise traders | A | https://econometricsociety.org/publications/econometrica/1985/11/01/continuous-auctions-and-insider-trading |
| Lee & Ready (1991), *Inferring Trade Direction from Intraday Data*, J. Finance 46(2):733–746, DOI 10.2307/2328845 | Aggressor classification (buy/sell volume, delta) when the feed has no side flag | A | https://ideas.repec.org/a/bla/jfinan/v46y1991i2p733-46.html |
| Finucane (2000), JFQA 35(4):553–576 | Lee-Ready ≈ tick test; both less accurate than assumed — delta from inferred side is noisy | A | https://econpapers.repec.org/RePEc:cup:jfinqa:v:35:y:2000:i:04:p:553-576_00 |
| Cont, Kukanov & Stoikov (2014), *The Price Impact of Order Book Events*, J. Fin. Econometrics 12(1):47–88 | Order Flow Imbalance (OFI) at best bid/ask explains short-horizon price moves linearly; slope ∝ 1/depth. Basis for DOM imbalance features | A | https://arxiv.org/abs/1011.6402 |
| Easley, López de Prado & O'Hara (2012), *Flow Toxicity and Liquidity in a High-frequency World*, RFS 25(5):1457–1493, DOI 10.1093/rfs/hhs053 | VPIN: volume-time buckets, buy/sell imbalance = flow toxicity | A | https://papers.ssrn.com/abstract=1695596 |
| Osler (2003), *Currency Orders and Exchange Rate Dynamics*, J. Finance 58(5):1791–1819 | Real order data: take-profits cluster AT round numbers, stop-losses just PAST them. Only academic basis for "liquidity sweep / stop hunt" ideas | A | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr125.html |
| Linn Software / MarketDelta history | "Footprint" name and chart came from MarketDelta (~2005–06); imbalance = diagonal ask vs bid one level below; thresholds (e.g. 3:1) are user choices, not science | C | https://www.linnsoft.com/marketdelta-footprint |

TIA implication: Footprint/delta/OFI/VPIN are valid only with classified trade prints or L1/L2 data. OHLCV cannot rebuild them (already TIA policy).

## 2. Auction Market Theory / Market Profile / Volume Profile

| Source | Note | Grade | Link |
|---|---|---|---|
| J. Peter Steidlmayer, CBOT; CBOT Market Profile released 1985 (dev. ~1981–84, dates differ by source) | Origin of TPO / value area / POC | B | https://en.wikipedia.com/wiki/Market_profile |
| Steidlmayer & Koy, *Markets and Market Logic* (1986); *Steidlmayer on Markets* (1989) | Originator's own texts | B | — |
| Dalton, Jones & Dalton, *Mind Over Markets* (1990) | Standard practitioner framework (acceptance/rejection, day types) | C | https://www.safaribooksonline.com/library/view/mind-over-markets/9781118659762/f02.html |
| Interview / CBOT manual | Historical | B/C | https://www.traders.com/Documentation/FEEDbk_docs/2007/12/Interview/interview.html |

No peer-reviewed test of profile day-types was found in this pass.

## 3. Wyckoff

- Richard D. Wyckoff course ~1931 (Wyckoff Stock Market Institute); Wyckoff died 1934. Grade B (original course not located online).
- The modern A–E phase schematics were codified **after** Wyckoff by later instructors; a 2006 MTA article revised them (1 accumulation + 2 distribution). So "Wyckoff schematics" ≠ Wyckoff's own drawings. Grade C.
- Secondary: https://www.prorealcode.com/wp-content/uploads/2019/11/WyckoffSchematics-VisualTemplatesForMarketTimingDecisions.pdf , https://www.stageanalysis.net/blog/389159/top-5-books-to-learn-the-wyckoff-method
- No peer-reviewed validation found.

## 4. ICT / Smart Money Concepts

- Originator: Michael J. Huddleston ("Inner Circle Trader"), YouTube/mentorship; retail vocabulary (order block, FVG, liquidity sweep, Power of 3, killzones). Grade C/D.
- Only quantitative item found: Agarwal, OSF preprint on "Power of 3" (not peer-reviewed, promotional tone): https://ideas.repec.org/p/osf/osfxxx/7yw86.html
- A skeptical 2026 preprint ("no evidence ICT/SMC concepts work as literally taught") is cited second-hand only — NOT verified: https://www.tradervue.com/blog/the-ict-trading-strategy
- The measurable part (stops clustered past round/obvious levels) is supported by Osler (2003), section 1. TIA should test that mechanism, not the labels.

## 5. Gann

- W.D. Gann (1878–1955). The spiral "Square of Nine" appeared in his *Master Charts* correspondence course, now inside the *Master Commodities Course*; Gann himself called it the "Spiral Chart" and used "Square of Nine" for a different chart. He never gave a course solely on it. Grade B (claims from secondary sources).
- https://www.wikipedia.org/wiki/W._D._Gann , https://www.topstep.com/blog/unlocking-w-d-ganns-the-tunnel-thru-the-air
- No peer-reviewed validation found. Keep as hypothesis (TIA image refs #20–#30).

## 6. Elliott Wave

- R.N. Elliott, *The Wave Principle* (Aug 1938, with C.J. Collins); Financial World articles 1939. Revived by Frost & Prechter, *Elliott Wave Principle* (1978); Elliott Wave International 1979. Grade B/C.
- https://www.elliottwave.com/?p=1361
- Main testability problem: wave counts are subjective and re-labelled after the fact (look-ahead). No peer-reviewed validation found.

## 7. Candlesticks & chart patterns

- Munehisa Homma (18th-c. Japan, rice markets) is the traditional origin; brought West by Steve Nison, *Japanese Candlestick Charting Techniques* (1991). Grade B/C. https://www.penguinrandomhouse.com/books/350650/japanese-candlestick-charting-techniques-by-steve-nison/
- Thomas Bulkowski, *Encyclopedia of Chart Patterns* (2nd ed.): largest practitioner pattern statistics (no costs/out-of-sample discipline). Grade C.
- Lo, Mamaysky & Wang (2000), *Foundations of Technical Analysis*, J. Finance 55(4):1705–1765, DOI 10.1111/0022-1082.00265 — automatic pattern detection by kernel regression; some patterns add incremental information (US stocks 1962–1996). Grade A. https://web.mit.edu/Alo/www/Papers/techanal.html

## 8. Does technical analysis work? (overall evidence)

| Source | Finding | Grade | Link |
|---|---|---|---|
| Brock, Lakonishok & LeBaron (1992), J. Finance 47(5):1731–1764 | MA and range-break rules on DJIA 1897–1986 beat null models (bootstrap); no costs | A | https://econpapers.repec.org/RePEc:bla:jfinan:v:47:y:1992:i:5:p:1731-64 |
| Park & Irwin (2007), J. Econ. Surveys 21(4):786–826 | Profits in FX/futures until early 1990s; most studies suffer data snooping, ex-post rule selection, cost/risk errors | A | https://ideas.repec.org/a/bla/jecsur/v21y2007i4p786-826.html |

## 9. Validation science TIA must apply before any strategy is "approved"

- Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*, J. Portfolio Mgmt 40(5) — corrects for multiple testing and non-normal returns. https://papers.ssrn.com/abstract=2460551
- Bailey, Borwein, López de Prado & Zhu, *The Probability of Backtest Overfitting* (CSCV), J. Computational Finance. https://papers.ssrn.com/abstract=2326253 ; R package `pbo`.
- TIA gap: Phase 6C has walk-forward + purge gap, but no DSR / PBO / multiple-testing correction yet. Recommended next engine item.

## 10. Map to TIA reference images

| Images | School | Best primary source above |
|---|---|---|
| #06 | Footprint / order flow | §1 (Lee-Ready, Cont et al., VPIN) |
| #03–#05 | Volume / Market Profile | §2 |
| #14 | Accumulation–manipulation–distribution | §3 Wyckoff + §4 Osler |
| #07–#12, #01–#02, #09, #15 | Candles / chart patterns | §7 |
| #13 | Market structure (BOS/CHoCH) | §4 (no academic source) |
| #16–#19 | Indicator / scalping claims | §8–§9 (test, don't trust) |
| #20–#30 | Gann / wheels / numerology | §5 (hypothesis only) |

## Not done / limits
- Videos not searched or watched. No full-text paper read; findings are from abstracts/indexes.
- Original Wyckoff 1931 course and Gann course texts not located online.
- Images #01–#30 not inspected in this session (owner to send).
