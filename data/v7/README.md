# V7 tab intake (data only)

Folder: `data/v7/`  
Branch: `v7-single-indicator`  
Contract: `docs/NEW_TAB_INTAKE_CONTRACT.md`  
Fetched: 2026-11-10 (Africa/Cairo)

This folder is research intake for a future **V7** tab about the CFX v7 single-oscillator chart (Stochastic 5,3,3 + RSI 14 + MACD 12,26,1, SMA 144/77, SMC/ICT overlays, session boxes). It is **data only**. No application file was edited for this delivery. A V7 page has not been registered in `main.py`.

## Files

- `sources.json` — JSON array, one object per source. Required contract fields plus `recheck_interval_days` (default 90, contract §4).
- `claims.json` — JSON array, one object per claim. Every claim has `source_id` + `timestamp_or_locator`. `status` is `unverified` on every row (contract default). `confidence` is how clearly the source states the idea, not whether it is true.
- This README.

Counts at delivery: **16 sources**, **40 claims**.

Schema notes:

- Contract `type` is only `video` / `post` / `article` / `paper`. Official docs, educational pages, and this repo’s own research files are typed as `article`.
- `published` is the date printed on the page when one exists. Several official or living docs do not show a date; those rows use `"undated"` rather than an invented day.
- Repo files are cited with their GitLab blob URL on this branch and a section / function locator, not a video timestamp.
- No API keys, tokens, or personal data.

## How the table was made

1. Read the intake contract on `main`.
2. Listed the concepts the V7 research actually uses (owner settings, oscillator rule, SMC/ICT overlays, sessions, XPIX, backtest figures) from `research/cfx/CFX_REQUIREMENTS.md`, `research/cfx/CFX_FIX_LOG.md` (section “v7 — 10 Nov 2026”), `research/cfx/CFX_GAP_AUDIT.md`, `research/cfx/cfx_pipeline.py`, and `research/cfx/cfx_lib.py`.
3. Looked up public definitions for the same ideas. Each public page used below was opened and read (WebFetch or the MQL5 documentation returned in search) on 2026-11-10. Locators are section titles, parameter lists, glossary entries, or code identifiers from those pages — not guessed.
4. Split “what a public page says” from “what this project implemented”. Owner parameter choices (Stochastic 5,3,3 at 15/85, RSI levels 10/90, MACD signal period 1, SMA 144/77, CFX session clocks, 0.10 ATR equal-high tolerance, XPIX helper) are sourced to our committed files, not attributed to Investopedia or MQL5.
5. Numbers appear only where the cited locator contains them (variant table, vis-window table, backtest line, BabyPips session clocks, CFX `SESS_WINDOWS`, `EQ_TOL_ATR`, FVG minimum 0.30 ATR, OTE `(0.62, 0.79)`).
6. Transcripts and articles were paraphrased. Nested lesson bodies and walkthrough trade tickets were not copied. The Tradeskill daily gap-fill percentages and the ICTKillzone NQ / EURUSD walkthrough prices were **not** turned into claims.

## What was NOT covered

- **No YouTube / ICT primary videos.** Timestamps were not invented. No Inner Circle Trader lecture was opened or transcribed in this pass, so there is no video `timestamp_or_locator`. Secondary written pages were used instead.
- **Investopedia RSI and MACD pages** returned HTTP 402 when fetched. **StockCharts MACD** returned HTTP 500. Therefore there is no sourced claim here that “standard RSI levels are 30/70” or that “standard MACD is 12, 26, 9”. MACD is described only from the MQL5 parameter list (fast, slow, signal, applied price).
- **Nested Tradeskill lesson pages** (the full essays behind the OB, breaker, IFVG, premium/discount, and OTE titles) were not opened. Claims from that domain cite the index titles and the category summary only; breaker and IFVG rows are marked `medium` for that reason.
- **ICT killzones** as a separate timetable (for example Asian 20:00–00:00 New York, London 02:00–05:00, New York AM 07:00–10:00) were not given a claim, because no primary page with that table was verified here. CFX display sessions use `SESS_WINDOWS` in `cfx_pipeline.py` (see claim-036) and differ from the BabyPips city-session table (claim-035).
- **Silver Bullet, Judas swing, IPDA, unicorn, turtle soup**, and other ICT named models that V7 does not implement as detectors.
- **News calendar / headline wiring.** CFX_REQUIREMENTS item 52 lists news as missing; `NEWS_EVENTS` in `cfx_pipeline.py` is an empty list. No news claims were written. Contract §4 (append-only `news.jsonl` from feeds the platform already uses) is left for Claude’s review.
- **Footprint, DOM, absorption, exhaustion, tape imbalance** — not implemented in CFX v7 (no tape feed).
- **Gann, Harmonic, and Wyckoff detectors** (requirements sheet marks them n/a).
- **A full historical liquidity-pool map** beyond PDH/PDL, visible EQH/EQL, CISD/breaker sweeps, and XPIX.
- **Compiled Pine and an MT5 / TradingView widget.**
- **The five owner MT5 settings JPEGs** named in the v7 brief; those hashes were not on disk. Parameter values follow the extracted dialogs as already written in `CFX_REQUIREMENTS.md` item 39.
- **External textbook source for the name “XPIX levels”.** Claim-038 states only how this project’s helper draws the last completed 15-minute and 1-hour high/low.
- No edge is claimed. Variant B’s 59.7% against-move rate (n=62) and the pipeline backtest (n=83, 37.35%, +0.238R after $0.30 spread) are recorded as research figures and stay `unverified` for Claude’s gate.

## What Claude is asked to do next

See the 2026-11-10 post in `docs/MEETING_ROOM.md` on this branch. In short: run the contract review gate (schema, dead links, missing locators, which claims the lab can test), answer the owner’s review questions, and do **not** merge to `main` or edit application files unless the owner later asks.
