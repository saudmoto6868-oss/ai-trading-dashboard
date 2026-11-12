# Claude review of data/v7 (CFX v7 tab intake), 2026-11-10

Reviewed: `data/v7/README.md`, `sources.json` (16), `claims.json` (40) on `v7-single-indicator`. Read in full. Not reviewed: `research/cfx/*` (chart image, code, log); no links were opened (no network in my sandbox); I did not run the schema test (added as `tests/test_v7_intake.py`, to be run by CI / Antigravity).

## Verdict on the data
Good intake. Every claim has a source + locator, nothing is invented, "not covered" is honest (no ICT video timestamps, Investopedia RSI / MACD pages failed), and the project's own figures are labelled research, not edge. Accepted as `unverified` input; nothing in the app until a tab is approved by the owner.

## Things to fix before the tab is built
1. **Separate facts about our own project from external claims.** 12-13 of 40 rows (project-setting, process, backtest, e.g. 009-015, 020, 029, 031, 033, 036-040) describe what CFX does or what the owner asked. They are not research claims about markets. Mark them `category: project-fact` and keep them out of the "claims tested" percentage.
2. **Repo files typed as `article`.** Add a `repo` type to the contract and use it for the 5 CFX sources.
3. **Confidence is too high where only a lesson title was read.** Claims 022, 024 are already `medium`; 025 and 027 (Tradeskill, titles only) should be `medium` too, since the nested lesson pages were not opened.
4. **Claim 012 (variant B) contains selection bias.** Three variants were tried on the same sample and the one that fired and looked best was chosen after seeing the result. The record is 62 signals, 37 against / 25 with the next-8-bar move (59.7% against). That is NOT significant: a two-sided binomial test against 50% gives roughly p = 0.13. So it supports neither "works" nor "inverse works". Any further variant must be pre-registered (`docs/PREREG_*.md`) before it is run, on data not used to choose it.
5. **Link / date check not done.** Someone with network access should open the 11 external URLs and confirm the quoted sections still exist (contract section 4: re-check interval 90 days).

## Which claims the platform can test now (contract step 2)
The platform already has detectors and walk-forward statistics for much of this, so V7 should REUSE them, not add a third copy:
- Scanner strategy tags already exist for OB, FVG, OTE, Breaker, Unicorn, Liquidity sweep, CISD, SMT, CRT, Power of 3, Kill Zone Sniper (`STRATS` in `modules/ws/12_news_filters_context.js`) with per strategy x timeframe TP1 hit rates (`tfInfo`, `modules/backtest_tf.py`). Claims 016-028, 030, 032, 034 map to those: run them, report n and edge vs random.
- Indicator definitions (001-008) are testable by unit tests against exports (cheap, deterministic).
- Session claims (035, 036): measure range / volume per window on the platform's own data.
- Claims 015, 031, 037, 039 are rules / display requirements: `testable: false`, correct.

## Answers to the review questions
5. **Structure drawing vs requirements:** not verified by me (chart image and code not reviewed). Needs a visual check by Antigravity against CFX_REQUIREMENTS items 22-33.
6. **Variant B / edge wording:** the log is right to say it is not an edge. See point 4: also state it is not significant either way.
7. **Sessions:** the platform already runs a New York clock (`Ctx.session`, `TCE.nextSession`: London KZ 02:00, NY AM KZ 07:00, NY PM KZ 13:30, Asia 20:00 NY). CFX `SESS_WINDOWS` (Asia 19-02, London 02-09, NY 08-17 NY time) uses the same clock, which is good. BabyPips is a third definition. Recommendation: ONE shared session definition used by the platform and V7 (start from `Ctx.session`), shown as display boxes; measure range / volume per window before any claim that sessions matter.
8. **Tab placement:** a new top-bar item makes the bar longer. Better as a sub-page inside an existing hub (see `_HUBS` in `main.py`) with the next free index (18), not a new top-level entry. Owner decides; nothing is built.
9. **What else Claude can add:** (a) map each testable claim to an existing scanner tag and publish the measured table; (b) unit tests for the detectors against synthetic bars; (c) a pre-registration file for any new rule; (d) a coverage line at the top of the tab (sources, date range, % tested).
10. **News:** the platform already has `modules/news_feed.py` and `modules/calendar_feed.py`. Proposal: tag each headline with the symbols it concerns and a high-impact flag, show as context only, and run an event study (range in the N bars after releases vs normal) before claiming any effect. Only public feeds already used; no scraping behind logins; no keys in the repo; nothing auto-promoted to a claim.
11. **Session tracking:** per symbol, the rolling 90-day distribution of range / volume per session window, and "current session percentile" on the tab. Same shared session definition as point 7. Descriptive, not a signal.

## Decisions needed from the owner
- Accept the contract change (`repo` type, `project-fact` category).
- Tab name / place (point 8).
- Whether V7 reuses the platform's detectors (recommended) or keeps its own research implementation.
No merge, no app file edited.
