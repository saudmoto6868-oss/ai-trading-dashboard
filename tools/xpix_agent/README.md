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
node tools/xpix_agent/xpix_agent.js params msb                    # every setting of an indicator (key, type, range, current value)
node tools/xpix_agent/xpix_agent.js set msb fib 0.3               # change a setting (validated: range / options / #rrggbb colours); saved with the layout
node tools/xpix_agent/xpix_agent.js layout standard               # standard | blank | save (= "save current layout as my standard")
node tools/xpix_agent/xpix_agent.js shot --out gold.png           # browser pixels at scale 2; --full = whole page; --workspace = workspace canvas
node tools/xpix_agent/xpix_agent.js record 20 --out demo.mp4        # high-quality video (add --res 4k = real 3840x2160 @ 60 fps, CRF 14): 1920x1080, 30 fps, H.264 CRF 16 (--size 2560x1440 --fps 60 --crf 14); needs ffmpeg (brew install ffmpeg)
node tools/xpix_agent/xpix_agent.js --out demo.mp4 batch '[{"cmd":"recstart"},{"cmd":"tf","args":["15m"]},{"cmd":"wait","args":["2"]},{"cmd":"page","args":["radar"]},{"cmd":"recstop"}]'   # record while other steps run
node tools/xpix_agent/xpix_agent.js batch '[{"cmd":"page","args":["workspace"]},{"cmd":"tf","args":["5m"]},{"cmd":"shot"}]'
```
Every command prints one JSON line (`{ok:true,...}` / `{ok:false,err}`), exit code 1 on error. Flags: `--url`, `--profile DIR` (persistent profile: saved layout / drawings survive), `--headed`.
Env: `XPIX_URL`, `XPIX_PROFILE`, `XPIX_CHROME` (a specific Chrome binary).

## Status (honest)
- Tested here against the real Streamlit app in a sandbox **without live prices** (OKX / Hyperliquid unreachable): pages, state, symbol / timeframe, indicator toggle, draw, screenshots work. Not tested with live data, on a Mac, or headed.
- Step 2 (settings + layouts) is mock-tested (`tests/browser/xcmd_settings_mock.js`) and was run through the agent against the real Streamlit app without live prices.
- Step 3 (video): CDP screencast JPEG q95 frames -> ffmpeg H.264 (Playwright's own recordVideo is low-bitrate, so it is not used). Tested in the sandbox on the real Streamlit app: a 31 s clip, 1920x1080, 30 fps, h264, 1.4 MB (a frame checked by eye: sharp). Frames come only when the screen changes, so a still page gives few frames (the clip is still the right length). Not tested: 60 fps / 1440p, long recordings, the Mac.
- Not built yet: HTTP wrapper for n8n (step 4). Moving / resizing panels by command is not there.

- 4K (`--res 4k`): the browser window is set to 3840x2160 (so the layout has twice the room; CDP screencast frames are always CSS pixels, a 2x device scale does not give more pixels). Tested: a 6 s clip, h264 3840x2160 60 fps (ffprobe). Heavy on CPU; use a fast Mac.
