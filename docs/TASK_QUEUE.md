# Task queue (cost-aware)

Rule: cheap first. Each item has a tier. Slow mode = only tier A and B, no web search, no lab runs, no new agents.

| Tier | Meaning | Examples | Model / cost |
|---|---|---|---|
| A | Owner-visible bug or request on the chart | yellow OTE box shown like the indicator; drawing options | small edits, one file, mock test |
| B | Multi-timeframe linkage (bigger to smaller) | next-TF count context | one extra OKX request per symbol per 5 min |
| C | Research, lab, reviews | lab keys, harmonic evidence, xpix review | heavy: only when owner asks |

Open now (in order):
1. A: OTE yellow box drawn for every count, as in the indicator (done 2026-10-19: unreached-zone filter removed).
2. B: linkage phase 2 (count of a bigger TF shown on a smaller TF). Needs one design answer first: which TF pairs.
3. A: drawing options phase 2 (fib / rect / channel colour and width).
4. C: lab run #13 results (waiting on GitHub Actions).
5. C: xpix review follow-up (waiting on ChatGPT, issue #8).

Done 2026-10-19: multi-timeframe linkage uses the four bigger timeframes (ladder 1m,5m,15m,1H,4H,1D,1W): on a 5m chart the line shows 15m, 1H, 4H, 1D. Cache is shared by all charts (one request per timeframe per symbol per 5 min). Warning row uses the nearest bigger timeframe only. Mock-tested: four trend chips appear after the fetch, no page errors. Not checked on live OKX.
