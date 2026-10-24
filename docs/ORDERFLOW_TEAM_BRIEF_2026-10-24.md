# Order flow: brief for the Claude Team (owner 2026-10-24: "do NOT archive ChatGPT's order-flow work, take it out and put the team on it")

Read first, in this order: `docs/OWNER_CONVERSATION_ORDERFLOW_2026-10-23.md` (owner + ChatGPT record, binding decisions), this file, `docs/OPEN_REQUESTS_2026-10-24.md`.

## What the owner and ChatGPT decided (binding)
1. Scope = Order Flow ONLY. Footprint works: do not touch it. No Volume Profile work without a new order.
2. Nothing of the order flow (heat map, bubbles, DOM bars) may be drawn over the candle bodies. Everything lives in the dedicated column right of the price axis. Closing the column must leave NOTHING over the candles.
3. The column must fill a bigger area and be visible on EVERY chart in EVERY tab (owner: "I don't see it on all the charts").
4. No claim without evidence: a static/text test is not proof the drawing is right in a browser. Never write "done" before a visual check; say what was NOT tested.
5. Price-scale drag, pan, zoom, resize, reload must not break the column or squeeze the price scale.
6. Footprint untouched, no merge/deploy without the owner's OK per item.

## State of the code on main (2026-10-24)
- #82 merged (ChatGPT's #67 + main): dedicated column, no painters over candles; migration of old saved state (dom/bub without dcol -> column on) and colW clamp (60 px .. 85 %).
- #80 merged: price grouping (DOM + heat column).
- #83 merged: sync card ✕ in both layouts; gauge ✕ since #68 (owner confirmed both work).
- DRAFT #106 = ChatGPT's #63 rebased: 7-day heat-map history (localStorage, best-effort), saves every 2 min on idle, quota retry; urgent bit (OKX WS 8443 -> 443) already merged as #107.
- Known limits (not fixed): history is best-effort ~3 symbols in 5 MB localStorage; real fix = IndexedDB. The depth feed is a REST poll every 1.5 s but `okx()` caches 10 s, so snapshots repeat. Recording only starts when the book layer is active.

## The owner's mandatory checklist (from the ChatGPT record) and where each item stands
| # | Check | Status |
|---|---|---|
| 1 | screenshot before, with the column state | open (needs real run) |
| 2 | close the order-flow column: no heat map / bubbles over candles | open: mock exists only as a text test (test_orderflow_render_policy.py) |
| 3 | open column, DOM only | open |
| 4 | Bubbles only | open |
| 5 | 3-dots / grouped mode | open |
| 6 | everything stays inside the column | open |
| 7 | price-scale drag up/down | open |
| 8 | pan, zoom, window resize | partly: free-zoom + resize mocks pass (blank-frame bug fixed) |
| 9 | reload restores dcol | partly: migration mock passes (old state -> colOn on 4 charts) |
| 10 | Order Book + Time & Sales keep updating | open |
| 11 | live OKX data | impossible from the sandbox: needs the owner's browser |
| 12 | before/after screenshots + repro steps | open |

## What the team should do (one draft PR per item, mock test, honest "not tested", report)
1. Run items 1-10 in a real headless browser with the mocked OKX feed (Playwright, see tests/browser/*.js for the pattern) and save screenshots; add a regression test for item 2 (a pixel/paint-call check that nothing is drawn over candles when colOn is false).
2. Verify the column on every chart tab / layout (the owner sees it on the first workspace only).
3. Decide #106 (merge after the owner's OK) and write the IndexedDB design note for long history.
4. Fix the repeated-snapshot feed problem (cache 10 s vs 1.5 s poll) if it matters visually.
5. Ask the owner for live checks only at the end (item 11), in one short list.
