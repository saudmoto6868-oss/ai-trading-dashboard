# XPiX Agent (step 1)

Drives the **real** platform in a real browser so n8n / the Claude team / the Telegram bot can use it like a person: open any page (tab), change symbol / timeframe,
toggle any indicator, add / close panels, draw, take screenshots. Read / view / draw only: no orders, no keys, no outside pages (same rules as `docs/XPIX_BOT_BRIEF.md`).

## Setup on the Mac (once)
```
npm i playwright && npx playwright install chromium     # in any folder; or use the repo's node_modules
streamlit run main.py                                   # the platform, default http://localhost:8501
```
## Use
```
node tools/xpix_agent/xpix_agent.js pages                         # the page bar (Workspace, Radar, ...)
node tools/xpix_agent/xpix_agent.js page radar                    # open a page by name or index
node tools/xpix_agent/xpix_agent.js page workspace
node tools/xpix_agent/xpix_agent.js state                         # panels, symbols, timeframes, indicators on
node tools/xpix_agent/xpix_agent.js symbol HL:xyz:GOLD            # (--panel p2 for one chart)
node tools/xpix_agent/xpix_agent.js tf 15m
node tools/xpix_agent/xpix_agent.js toggle msb on                 # any indicator id from `list`
node tools/xpix_agent/xpix_agent.js shot --out gold.png           # browser pixels at scale 2; --full = whole page; --workspace = workspace canvas
node tools/xpix_agent/xpix_agent.js batch '[{"cmd":"page","args":["workspace"]},{"cmd":"tf","args":["5m"]},{"cmd":"shot"}]'
```
Every command prints one JSON line (`{ok:true,...}` / `{ok:false,err}`), exit code 1 on error. Flags: `--url`, `--profile DIR` (persistent profile: saved layout / drawings survive), `--headed`.
Env: `XPIX_URL`, `XPIX_PROFILE`, `XPIX_CHROME` (a specific Chrome binary).

## Status (honest)
- Tested here against the real Streamlit app in a sandbox **without live prices** (OKX / Hyperliquid unreachable): pages, state, symbol / timeframe, indicator toggle, draw, screenshots work. Not tested with live data, on a Mac, or headed.
- Not built yet: high-quality video recording (step 3), settings-panel editing, HTTP wrapper for n8n (step 4).
