# 6868 X - platform review (2026-10-16)

Basis: reading the code, the repo data files and running the unit tests. **No real market results exist** - see section 1.

## 1. Real backtest data
- OKX and Yahoo are unreachable from the build sandbox (HTTP 000/403 from the egress proxy), so `modules.backtest_filters`, `modules.backtest_signals`, `modules.backtest_tf` could NOT be run on real candles. No number below comes from real data.
- `data/tf_stats.json` (the "best timeframe per strategy" table) is **empty** (`"stats": {}`): that feature currently ranks nothing.
- `data/signal_stats.json` and `data/filter_compare.json` do not exist.
- All 10 unit-test files pass, but they use synthetic / hand-made candles: they prove the code runs and the rules are applied as written, not that any signal has an edge.
- To get real results the owner (or a GitHub Actions job) must run: `python -m modules.backtest_filters BTC-USDT ETH-USDT SOL-USDT`, `python -m modules.backtest_signals`, `python -m modules.backtest_tf` on a machine with OKX access and send the output.

## 2. Journal (workspace_app.html, `Journal`)
Works as designed: logs ready setups/alerts that pass `planOk`, >= 50% strength, R:R >= 1; entry-fill awareness; stop-first on the same candle; `nf`/`exp` excluded from the win rate.
Weaknesses (real, not cosmetic):
1. **Browser-only storage** (localStorage, last 1500). Not shared across devices/browsers, lost if site data is cleared, only logs while a tab is open. The server-side `signal_log.py` (GitHub Actions) is the trustworthy record; the two are never reconciled.
2. **Win = TP1 only.** TP2/TP3 are ignored, no partial exits, no fees, slippage or funding. Reported R is optimistic by the cost of trading; with ~33% win rate the plan needs average winner >= 2R just to break even, so the cost matters.
3. **Not independent samples.** The cool-down key is symbol|side|type, so the same market idea on different timeframes (and correlated BTC/ETH/SOL) is counted several times: n looks bigger than it is, and the win rate's error bar is wider than shown.
4. **Selection by the scanner itself.** Setups are logged only when the scanner shows them, so the journal measures "what the scanner displayed while a tab was open", not all signals. Fine for a sanity check, not for proving an edge.
5. **Coarse settlement candles** (1m < 4.5 h, then 1H, then 1D): the stop-first rule is conservative, but a fill and a stop inside one 1H/1D candle cannot be ordered - result is biased to losses on wide candles.
6. **Expired trades count as R = 0 and are excluded** from the win rate: if many setups expire, win rate and profit factor overstate quality. Show `exp` and `nf` counts next to the win rate (the counts exist, the headline % ignores them).
7. Win-rate "~33%" reported earlier was measured BEFORE the fill-awareness fix; it must be re-measured on new data.

## 3. Claims in STRATEGIES.md vs evidence
- Every strategy is marked "in stars" / "new" with **no measured result**. The file itself says so (Evidence section). Correct reading: all are hypotheses.
- "Daily bias", "Premium/Discount", killzones, Model 2022, CISD: ICT-course concepts, "unverified edge" - agree.
- The star count (families agreeing) and the Telegram "quality" score are **evidence heuristics, not probabilities** (the messages already say this). The +8/-12 MTF adjustment and the other point weights (10/-12/8/-10/6...) are hand-picked, never tuned or validated.
- `backtest_signals.walk` measures direction hit-rate over H bars vs a random baseline (no stops, targets, costs). Even a "pass" there would not prove a tradable edge; `backtest_filters` is the same type of test.
- Several detectors only exist as scanner flags and are explicitly not counted: fine.

## 4. Structural issues / contradictions
1. **Two performance systems**: browser Journal (client) and `signal_log.py` (server). Different rules (Journal: fill within 0.15%, 1m/1H/1D candles; server: entry must be filled, 48 bars max). They will give different numbers for the same setups. Pick one as the source of truth (recommend the server log) and have the Performance tab read it.
2. **`workspace_app.html` is one ~3000-line file**; every UI item edits it, so parallel agents (the planned n8n 7-agent setup) will conflict. Splitting it into modules is the main enabler for parallel work, but also a risk - do it only with Playwright tests in place.
3. **Parameter sprawl**: SIGF_*, TG_*, stars, quality weights, Journal cfg - none tuned on data; adding more filters before any real backtest increases the risk of overfitting later.
4. **Data sources** are many fallbacks (Yahoo, Biquote, Alpha Vantage, FRED, Currents, RSS); Biquote/FRED/Currents were never run against the live services; forex/gold/indices have no real volume, so volume filters silently switch off there - results for those markets are not comparable with crypto.
5. **Order-flow / heat map**: depends on OKX book polling; OKX gives no history, so the heat map time axis starts empty on every new browser (mitigated by browser-saved history).
6. **Streamlit layout changes (header, dropdowns) and the Workspace visual changes were never run on the real deploy** - only Playwright on a mock server.
7. Item 6 (Scanner = state vs Alerts = events) is a proposal still waiting for the owner's OK.

## 5. What works (verified only at code/unit level)
Signal detection pipeline + tests, scorer stars, MTF framework, signal-log settle logic, Journal fill/stop rules, theme system, Signals widget, order-flow column drawing, SMT inverse logic, Telegram message formatting. Run live to confirm.

## 6. Recommended next steps (in this order)
1. Get real candles: run the three backtest modules once with OKX access (or add a GitHub Actions workflow_dispatch job that runs them and uploads the JSON as an artifact - not done yet).
2. Treat the server signal log as the single source of truth; let it accumulate >= 30 closed trades per setup type before any claim.
3. Re-measure the Journal win rate after the fill-awareness fix; report n, expired and no-fill counts next to it, with costs (e.g. 0.1% round trip) deducted.
4. Only then tune/remove filters and weights based on results (walk-forward, not full-sample).
5. Split `workspace_app.html` before running parallel agents.

Open questions for the owner: confirm Scanner-vs-Alerts definition; which journal is the "official" one; whether to add the Actions backtest job.
