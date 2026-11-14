# QUICK_REF (read this before the long docs)

## Commands
- All checks, quiet: `bash scripts/check.sh` (only failures + 1-line summary)
- One area: `bash scripts/check.sh spot` (runs tests/test_*spot*.py)
- One test: `python3 tests/test_X.py 2>&1 | tail -15`
- Rebuild workspace after editing `modules/ws/*`: `python3 scripts/build_workspace.py`
- Run app: `streamlit run main.py --server.headless true`

## Conventions
- Never edit `modules/workspace_app.html` directly (generated, ~400 KB); edit `modules/ws/<part>`.
- Read big files by range: `grep -n` first, then `sed -n 'A,Bp'`. Never cat whole files.
- Page indexes fixed (see CLAUDE.md Map); new page = next free index.
- Arabic UI text via `L()` in `modules/i18n.py`.
- Secrets only in Streamlit Secrets / env. Never commit keys.
- No network to price sites in sandbox: mock (Playwright `page.route`), mark "mock-tested only".
- Honesty: no invented prices / win rates; n<30 = "not evidence".
- After each item: update its row in `PROJECT_STATUS.md` + change log; small commits.

## Token habits
- One task per session; `/clear` between unrelated tasks; `/compact` only in long threads.
- Don't switch model or add MCP servers mid-session (breaks the cache).
- Pipe noisy output through `tail`/`grep`; use `head_limit` on searches.
- Verbose exploration (>10K tokens of output) -> subagent; else inline.
