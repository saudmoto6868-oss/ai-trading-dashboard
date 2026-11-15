# desk_brain: the ai-desk engine inside the dashboard

Copied from GitLab `6868-group/ai-desk` (`desk/` package), owner order 2026-11-15 ("one brain").
Page: `modules/desk_page.py` (Learn & AI > AI Desk, PAGE 21). Tests: `python3 tests/test_desk_page.py`.

- `agents/`: the agent floor. Head, 8 specialists (Wyckoff, ICT, COT, OrderFlow, Sentiment, Macro, Seasonality, News),
  Bull / Bear, Risk, Auditor, Reviewer. Each one is an LLM ReAct loop with tools (`agents/tools.py`).
  The fixed gate at the end of `agents/team.py` has the last word; the model never overrides it.
- `views.watchlist`: the Watchlist engine (3+ reasons from 2+ departments, stars).
- `risk.py`: the three prop accounts (personal floor = half the firm's daily limit, 0.5% risk) and lots per account.
- `manage.py`: 5-minute paper trade management (fill, stop first on an ambiguous bar, BE at T1, ATR trail, T2).
- `journal.py`: paper journal (SQLite in `DESK_DATA_DIR`, a temp folder on Streamlit Cloud, so it resets on reboot).

Settings come from env / Streamlit Secrets only (`modules/desk_page.setup_env`): `GEMINI_API_KEY` (free, first),
optional `LLM_BASE_URL` / `LLM_MODEL` / `LLM_FALLBACKS` / `AGENT_MODELS`, `DESK_FLOOR_DAILY_CAP` (default 3 runs a day).
Data chain: Binance -> Yahoo -> Hyperliquid -> cache -> demo. Demo data is labelled and never journaled.
Paper only: nothing here places an order. Keep this folder in sync with ai-desk when either side changes.
