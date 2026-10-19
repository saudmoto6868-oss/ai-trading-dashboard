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
3. A: drawing options phase 2: rectangle and channel now follow colour, width, dash (done 2026-10-19). Fibonacci and wave now follow colour / width / dash too (done 2026-10-19). Item 3 closed.
4. C: lab run #13 results (waiting on GitHub Actions).
5. C: xpix review follow-up (waiting on ChatGPT, issue #8).

Done 2026-10-19: multi-timeframe linkage uses the four bigger timeframes (ladder 1m,5m,15m,1H,4H,1D,1W): on a 5m chart the line shows 15m, 1H, 4H, 1D. Cache is shared by all charts (one request per timeframe per symbol per 5 min). Warning row uses the nearest bigger timeframe only. Mock-tested: four trend chips appear after the fetch, no page errors. Not checked on live OKX.

Done 2026-10-19: the counter-trend warning now looks at all bigger timeframes (four plus weekly and monthly): it fires when most of them with a known trend point the other way. Syntax-checked only.

Done 2026-10-19: drawing tools: price range (horizontal band with the price difference and %), date range (vertical band with the bar count), hide (the options bar hides a drawing; it is not drawn or selectable), edit text (text tool only). Mock-tested in headless Chromium: both bands paint without errors; hide sets the flag and clears the selection. Not done: a list of hidden drawings to show them again; brush / pen; object tree.

Done 2026-10-19 (owner choice 3): the trend chain is six frames around the chart: up to two smaller frames and then the bigger ones (weekly and monthly included). Example: 5m shows 1m, 15m, 1H, 4H, 1D, 1W. Mock-tested in headless Chromium (trend line shows the six); lists checked for every frame.

Done 2026-10-19 (owner): a fold arrow (▾ / ▸) at the top right of the chart folds the Gann definition text (summary, zone trades, lab out of sample); the Gann lines and labels stay. Mock-tested: the arrow draws in both states; the click toggle is not tested in the browser.

Done 2026-10-19 (owner): one fold arrow for all indicators (Elliott, Harmonic, Gann). It hides description text only: the grey indicator notes, the trend line, and the Gann definition lines. Lines, boxes, signals and the drawings stay. Mock-tested: with all three on, folding drops the description labels from 7 to 2 (labels on the drawings) and the stroke count is unchanged (11). The click on the arrow is not tested in the browser.
