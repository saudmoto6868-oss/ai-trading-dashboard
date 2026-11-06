# The brain (2026-11-06): alerts, Top 7, daily review

Runs on GitHub Actions every 30 minutes (`.github/workflows/telegram-alerts.yml` > "Brain", `python -m modules.brain_cron`), without the dashboard open. Needs the Telegram secrets already set.

## What it sends (each message once)
- **Event heads-ups** (`modules/event_clock.py`, New York clock): high-impact news 2 h / 1 h / 30 min before (it can move either way: do not open trades the last 30 min, wait 15 min after);
  Silver Bullet windows (03-04, 10-11, 14-15 NY) and session opens (Asia, London, NY FX, US stocks, NY close) up to 75 min ahead; the 15- and 30-minute opening-range marks; crypto day / week / month starts
  and ends (UTC), FX / metals week open (Sunday 17:00 NY).
- **Setup alerts** (`day_plan.setup_alerts`): CISD, CRT, Kill Zone Sniper, sweeps, Model 2022, Elliott wave 3 / 5 / C, SMT, Power of 3, Judas, session AMD, ORB, Unicorn, breaker, MSB-OB, rectangle, double
  top / bottom, Wyckoff spring, price-action candles at a level, trendline / liquidity-line breaks. Each with its OWN plan (entry / stop / targets) and the possible move in points (default >= 100, `BRAIN_MIN_POINTS`),
  marked with / against the 1D + 4H bias. At most 5 per pass (`BRAIN_MAX_SETUPS`).
- **SMT** between correlated pairs (fresh, <= 3 bars old, 15m and above).
- **Top 7 of the day** (`modules/daily_top.py`) at the London pre-open (03:00 NY) and the NY pre-open (08:00 NY): forex, metals, crypto, indices, stocks (`BRAIN_SYMBOLS`). **Calm movers first** (low ATR % and a high
  efficiency ratio); choppy ones go last. Within each group, more agreeing evidence ranks higher: timeframes in the chain, distinct schools, SMT on the same side, context watch items, the kill zone, R:R >= 1.5.
  "Points" count agreeing evidence; they are not a win rate.
- **Daily review** (`modules/brain.py`) after the NY close: how the logged ideas did, per school (n, average R, win %), with a loud "not evidence" under n = 30.

## How it learns (and what it does NOT do)
Every Top 7 is logged (`.brain_log.jsonl`), graded 6 h or more later by replaying the candles after the idea with the plan's own exit rules (`day_plan.simulate_arrays`), and summarised per school and per detector key.
It only REPORTS and SUGGESTS. It never changes weights, thresholds or the live scanner by itself: a promotion goes through the weekly lab (`docs/academy/DEVELOPMENT_NOTES.md`, n >= 30 and real costs).
Memory is the Actions cache (like `.tg_sent.json`): a cache eviction loses the history, not the code.

## Not built yet (honest)
- **News research outside the calendar**: the job only reads the public economic calendar (ForexFactory mirror). Headlines / web research need a connected tool; the deployed app has none.
- Automatic weight adaptation from the review (deliberately off until the lab agrees).
- Silver Bullet / session-open *setups* (the heads-up exists; a detector that grades the FVG-after-sweep inside the window is the Kill Zone Sniper / Silver Bullet keys already in the scanner).
- Previous day / week / month high-low sweeps as their own alert (the generic `sweep`, `crt`, `kzs` keys cover part of it).
- Real Telegram sending and live data were NOT tested here (mock-tested only).
