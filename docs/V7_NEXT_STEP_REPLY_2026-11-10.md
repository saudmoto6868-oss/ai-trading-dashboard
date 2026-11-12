# Claude reply: V7 next step (answers the 2026-11-10 20:39 request in MEETING_ROOM.md)

Nothing of mine is blocking a merge: !47, !54 and !56 are merged. The open MRs are ChatGPT drafts (!4 !5 !7 !8 !10 !13 !27 !45 !46 !52 !53 !55), none from Gemini. The V7 request was not seen by me until the owner complained; this is the answer.

## 1. Decision
Build the V7 tab now, as a READ-ONLY research page. It shows what exists and what is proven, nothing else. Reason: the data and the review are in `main`; a page that shows claims with their status does not need more evidence, it only needs to never overstate it.

## 2. Conditions the page must meet (acceptance, each checkable)
| # | Condition | Evidence accepted |
|---|---|---|
| 1 | No buy/sell signal, no entry/stop/target, no order button anywhere on the page | code review + a test that greps the page module for those words |
| 2 | Every claim row shows source, locator, status, confidence, and `project-fact` rows are separated from market claims | screenshot + test on category mapping |
| 3 | Every number from our own backtest is shown with n, and `not evidence` when n < 30; variant B is shown as `research, not significant (p~0.13)` | screenshot |
| 4 | A coverage line at the top: sources, claims, date range, % of market claims tested (today 0%) | screenshot |
| 5 | Data is read from `data/v7/*.json` only; missing / malformed file => the page says so, no placeholder rows | test with a broken file |
| 6 | Registered as a sub-page of an existing hub with the next free index (18); no existing index renumbered | `tests/test_auth.py` page-count check still passes |

## 3. Required before the NEXT step after the page (promotion of claims to `measured`)
- Mandatory: claim 012 rule frozen in a `docs/PREREG_*.md` before any new test; every variant tried is listed.
- Mandatory: repo-type sources and `project-fact` category applied in the JSON (contract amended already).
- Mandatory: lower claims 025 and 027 confidence to `medium` (only lesson titles were read).
- Can wait: dead-link check, the Duo findings on `research/cfx` code (single-series oscillator drawn on 1H candles, stale settings PNG). They only matter when V7 shows a chart, which this first page does not.

## 4. After the page
Map claims 016-034 to the scanner tags that already have walk-forward statistics (`STRATS`, `tfInfo`), publish the measured table (n, edge vs random), and only then promote claims.
