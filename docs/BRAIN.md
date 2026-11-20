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

## Brain v2 (2026-11-06)
- **News outside the calendar** (`modules/news_watch.py`): RSS/Atom from central banks and agencies (tier A), business press (B), crypto press (C, strong topics only). Keyword classification, impact >= 2, de-duplicated by title, max 3 hours old. It says "can move either way"; the hawkish/dovish tag is a reading of the words, not a forecast. Feed reachability from GitHub Actions is NOT verified; `/news` shows how many sources did not answer. `BRAIN_NEWS=0` turns it off.
- **Liquidity sweeps** (`modules/level_sweeps.py`): previous day / week / month high-low and the Asian range, fresh within 3 hourly candles; a hint of reversal, not an entry. `/sweeps`.
- **Horizons** (`modules/horizons.py`): scalp / day / swing / position, each with its own timeframe chain and exit style; grade A+ (>= 4 schools, bias agrees, R:R >= 2, not choppy) or A (>= 3 schools, R:R >= 1.5). Digest at every 4-hour mark of the New York clock (00/04/08/12/16/20), only when something qualifies. `/horizons [name]`. Logged into the brain for grading.
- **Adaptive school weights** (`brain.school_weights`): EXPERIMENTAL multiplier 0.7-1.3 on the Top-7 school points, from graded average R, needs n >= 10 per school and shrinks small samples toward 1. Never touches the scanner or lab. `BRAIN_ADAPT=0` turns it off.
- Not tested: live feeds, real Telegram, real data for 1W candles on every source; the horizons builder has only been run on empty/synthetic input.

## 2.6 journal + learning loop (2026-11-20, owner order)
- **Every 2.6 setup is a journal row** (`modules/two_six_journal.py`, file `data/two_six/journal.jsonl`, git-ignored). Button "Save these setups to the journal" on the 2.6 page (inside Lab). One row per setup, updated in place as its status changes; the owner's note is kept.
- **Each row says:** why it was taken / rejected (rule-based, only what was known at the time), the review (won / lost / unresolved / live), the **best live setup now** (nearest waiting or open setup to the last price, expired never), the strategy used, and the follow-up.
- **Learning loop (the rule):** review the journal every week. A change to the stop / target / entry rule is made only after n >= 30 closed setups, with costs, and only through the lab. One losing trade is logged, not used to change the rule.
- **Not built yet / open:** (1) the 2.6 rules themselves (stop, TP1 after partial, TP2) are still PROVISIONAL, waiting for the owner's answers in `research/strategies/2.6/docs/RULEBOOK.md`; (2) "TP1 then stop" has no confirmed outcome, so it stays unresolved; (3) no costs; (4) no broker XAUUSD data yet: GC=F is a proxy only, so the journal on gold is not XAUUSD evidence; (5) the higher-timeframe agreement shown on the chart (1H / 4H ✓ ✗) is NOT in the journal rows yet.
- **Best 2.6 setting:** NOT known yet. It needs real XAUUSD M1/M5 OHLC with spread and timezone, then walk-forward and holdout (see the 2.6 evaluation). Until then no setting is "best".
- Tested: `tests/test_two_six_journal.py` (synthetic only; logic, not the strategy). The lab page itself is not run in the sandbox (no streamlit / no price feed).
