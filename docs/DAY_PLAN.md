# Day plan (Radar > Day plan, `modules/day_plan.py`) — 2026-11-06

**What it is.** Today's trades, by session and by timeframe confluence. Higher timeframes (1D + 4H) give the bias; the trigger timeframes (1H / 15m / 5m) give the entry; a plan is listed only when
at least 3 of the 5 timeframes (1D 4H 1H 15m 5m) point the same way, one of them 1D/4H and one a trigger. Built from the detectors the platform already has (all schools: SMC/ICT, Elliott, Fibonacci,
Liquidity, Trend, Levels, Time, Momentum, plus Price action, Chart patterns, Wyckoff as CONTEXT) and `risk_engine.build_trade_plan` for entry / stop / 3 targets.

**Options** (Radar > Day plan): mode (standard = timeframe confluence; Scalp = one trigger timeframe you choose, fixed stop + target), schools filter, minimum possible move (100 / 150 / 200 / 300 / 1000
points), minimum stars, universe (day-plan list or the current Radar universe), "stop starts moving after N points" (default 100).

**Points.** 1 point = `day_plan.POINTS` (gold 0.1 = one MT5 pip, silver 0.01, oil 0.01, indices 1.0, BTC 1.0, ETH 0.1, forex = pip, unknown = 5 significant digits). Override: env `POINT_SIZES='{"BTC-USDT": 1}'`.
The card also shows the prices, so a wrong point size is visible.

**Exits.** Standard: 50 % off at TP1; the stop goes to break-even once the trade is +min(1R, 100 points); then a trailing stop 1.5 ATR behind the best price for the runner; final target TP3.
Scalp: fixed stop, one target, nothing moves. `simulate_exit()` replays candles with these rules (conservative: a candle touching the stop and a target uses the stop first); the lab can use it to measure them.

**Sessions** (New York clock, same bands as the Workspace): Asia 19-04, London 03-12, New York 08-17; kill zones Asia 20-24, London Open 02-05, NY AM 07-10, NY PM 13:30-16. The page shows the active session
and the next kill zone.

**Telegram.** Standard plans are scanned in the background every 15 min and the best new ones are sent (one message each, not repeated for 4 h) when Telegram alerts are on. The bot (`scripts/xpix_bot.py`):
`/plan [scalp|conf] [5m|15m|1h] [SYMBOL ...]`, `/smt`, `/help`; any other text goes to Claude (read-only).

**Exits are measured.** The weekly lab (`strategy_lab.VARIANTS`, rows `pt_1.5_3`, `pt_1.0_3`, `pt_1.5_5`, `trail_only` in the "Exit variants" table) replays the same entries with the partial + trailing exit through `day_plan.simulate_arrays` next to the fixed-RR variants; read the net-R column there (one `LAB_COST_R` per trade) before trusting "the stop moves" over a fixed target. Until the first weekly run reports n >= 30 per row, the standard exit is a design choice, not evidence.

**Watch alerts.** Context setups (price action, rectangle / double bottom, Wyckoff, Elliott) that agree with the 1D + 4H bias are sent to Telegram as "👀 Watch" (at most 2, not repeated for 2 h) and via the bot `/watch`. They are not trades: no plan, no star.

**Honest limits.** Stars are the scanner's evidence count, not a win rate. New detectors are context until the weekly lab has n >= 30 per key. No plan was checked against live prices or backtested as a whole here
(`simulate_exit` is a replay tool, not a result). Nothing here places orders. Not financial advice.
