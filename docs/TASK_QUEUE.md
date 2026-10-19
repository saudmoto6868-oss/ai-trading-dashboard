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
