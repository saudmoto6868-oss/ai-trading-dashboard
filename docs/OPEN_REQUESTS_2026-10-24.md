# Open requests (owner + team), 2026-10-24 — what is NOT done yet

Source: owner messages in the manager chat, PROJECT_STATUS.md priority table, open PR list. Honest status: "done" = merged to main; **nothing below was tested on real data by the owner yet** unless stated.

## A. Waiting for the OWNER (cannot move without him)
1. **Blink**: test after the latest merges (Ctrl+Shift+R), and the 2-minute no-touch test: does a new `[XPIX] page load #N` appear on its own? (decides if Streamlit remounts the iframe).
2. **Order-flow "balance" table has no close button**: the pressure gauge has ✕ since #68 (only drawn when DOM is on and the column >= 230 px), the sync card got ✕ in #83. He must send a screenshot of the table he means.
3. **Setup Card "refresh / list"**: needs his words for what it should do.
4. **Name XPiX -> XPX**: ON HOLD until an approved name/meaning (options sent: Cross-market·Price action·eXpectancy / eXecution·Position·eXit / Cross Price eXplorer). Keys, GitHub repo name, Streamlit URL, saved layouts are NOT affected; only text + logo (16 files, ~254 hits).
5. **Options candles feed**: data-source decision deferred by the owner (options cannot be scanned without candles).
6. Real **logos** for tickers without one (SOXL, SOXS, KORU, MU ...): they show a readable letter badge now; real logos need a ticker -> domain map (his OK).
7. Keys: Finnhub WS token looks invalid/expired (console: ws.finnhub.io failed), Finnhub/Unusual Whales keys (PROJECT_STATUS #4), Coinversa REST key (#16).

## B. For the CLAUDE TEAM (steady pace, one draft PR each, mock tests, report; Sonnet merges after owner OK)
1. **Order flow (ChatGPT's work)**: #82 merged (dedicated column). Still open: #63 (retain up to 7 days of history + clarify estimated volume profile: decide merge or close), #67 is superseded by #82 (close), check the column on every chart tab with real data, `docs/OWNER_CONVERSATION_ORDERFLOW_2026-10-23.md` is the owner's record (read it first).
2. **Full-system review** (owner asked for it, in a separate track): finish, then ask the owner before merging.
3. **Per-chart colours** (#103): volume / sub-pane / indicator colours still follow the theme; add them if the owner wants.
4. **Scan coverage with real data**: verify Stocks / Oil & Gas / Bonds / Forex / Indices really produce READY setups (the class filter only filters what was scanned); measure the scan time after +7 Hyperliquid symbols (#105).
5. **Radar / Scanner redesign** (A-F from the earlier plan), **chart-patterns column restore**, **MBS follow-up** (see PROJECT_STATUS / MEETING_ROOM).
6. PR #75 (XPIX-SHIX_M7 port): inventory only; owner has not said "start the indicator port".
7. Finnhub WS: optional retry cap (already backs off 5 s -> 60 s).

## C. PR hygiene
- Superseded, can be closed: #67 (by #82), #87 (by #88).
- Others still open: #63, #75, #81 (OpenAI guide provider; ready, not reviewed by me).

## D. PROJECT_STATUS table, not done
#4 keys (owner), #16 Coinversa (owner), #18 TradingView session (hold), #19 MT5 (hold), #24 marginal tools, **#25 A+++ pipeline review (owner: "most important")**, #26 material themes (waiting for his pictures).

## E. Done in this stretch (for reference, all mock-tested only)
#84 st.iframe revert, #85/#86/#89/#90/#92/#93/#95/#97 blink + repaint fixes, #88 Hyperliquid 429 backoff, #91 fast first chart load, #94 console diagnostics, #96/#98/#99 softer flashes + markers, #79 limits legend, #83 sync-card ✕, #100 letter badges, #101 free zoom, #102 test fix, #103 per-chart colour menu, #82/#80 order-flow column + price grouping, #104/#105 class filter + mini charts + wider scan.
