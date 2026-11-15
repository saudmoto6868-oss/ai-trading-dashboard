"""The brain's server job (GitHub Actions, every 30 minutes, next to tg_cron / tclass_cron; runs without the dashboard open).

    python -m modules.brain_cron          # do the work and send to Telegram
    python -m modules.brain_cron --dry    # print what WOULD be sent

What it sends (each message once; the sent memory is .brain_sent.json):
  * EVENT heads-ups (modules/event_clock.py): news 2 h / 1 h / 30 min before, Silver Bullet and session opens (up to 75 min ahead), opening-range marks, day / week / month starts and ends.
  * the TOP 7 of the day (modules/daily_top.py) at the London pre-open and the New York pre-open, across forex / metals / crypto / indices / stocks, calm movers first.
  * a daily REVIEW (modules/brain.py) after the New York close: how the graded ideas did, per school, with the n < 30 warning.
Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID; BRAIN_SYMBOLS (comma list; default below); BRAIN_TOP (7)."""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

STATE = Path(os.environ.get("BRAIN_SENT", ".brain_sent.json"))
DEFAULT_SYMBOLS = ("BTC-USDT,ETH-USDT,SOL-USDT,HL:xyz:GOLD,HL:xyz:SILVER,HL:xyz:CL,HL:xyz:SP500,HL:xyz:XYZ100,"
                   "Y:EURUSD=X,Y:GBPUSD=X,Y:USDJPY=X,Y:AUDUSD=X,Y:AAPL,Y:NVDA,Y:TSLA,Y:MSFT")
DIGEST_SLOTS = {"london": (3, 0), "newyork": (8, 0)}   # NY clock: the Top 7 goes out within an hour after these
REVIEW_AFTER = (17, 30)


def symbols() -> list:
    return [x.strip() for x in os.environ.get("BRAIN_SYMBOLS", DEFAULT_SYMBOLS).split(",") if x.strip()]


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def save_state(sent: dict):
    now = time.time()
    STATE.write_text(json.dumps({k: v for k, v in sent.items() if now - v < 5 * 86400}))


def digest_slot(now_utc: datetime):
    """'london' / 'newyork' + the NY date when `now` is within 60 minutes after that pre-open, else None."""
    from modules.event_clock import NY
    loc = now_utc.astimezone(NY)
    for name, (hh, mm) in DIGEST_SLOTS.items():
        start = loc.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if 0 <= (loc - start).total_seconds() / 60 < 60:
            return name, loc.strftime("%Y-%m-%d")
    return None


AGENTS_FILE = Path(os.environ.get("BRAIN_AGENTS", ".brain_agents.jsonl"))
AGENTS_DIR = os.environ.get("AGENT_RESULTS_DIR", "data/agent_results")   # Grok / TIA drop *.jsonl files here (docs/AGENT_CONTRACT.md)


def _agent_results(sweeps=(), news=(), plans=()) -> list:
    """This pass's findings as contract objects (modules/agent_result.py). Candle data is fetched on a 30-minute cron, so its quality is 'delayed', never 'live'; n = 0 (no graded sample)."""
    from modules import agent_result as AR
    out = []
    for a in sweeps:
        out.append(AR.make("level_scanner", "claude", a["symbol"], a["direction"], [{"what": f"swept {a['level_name']}", "value": a["level"], "unit": "price"}], "exchange candles", "delayed", 0, coverage="last 3 hourly candles", note="reversal hint, not an entry"))
    for a in news:
        out.append(AR.make("context_monitor", "claude", "*", "info", [{"what": a["title"]}], a["source"], "delayed", 0, coverage="RSS, last 3 h", note=", ".join(a.get("topics", []))))
    for p in plans:
        out.append(AR.make("confluence_confirmer", "claude", p["symbol"], p["direction"], [{"what": s} for s in p["schools"]] or [{"what": "chain agreement"}], "scanner", "delayed", 0, coverage=f"{p['horizon']} {p['tf']}", note=f"grade {p['grade']}"))
    return out


def horizon_slot(now_utc: datetime):
    """The 4-hour mark (NY clock 00/04/08/12/16/20) this pass falls in, within the first 30 minutes; None otherwise. Returns 'YYYY-MM-DD-HH'."""
    from modules.event_clock import NY
    loc = now_utc.astimezone(NY)
    if loc.hour % 4 == 0 and loc.minute < 30:
        return loc.strftime("%Y-%m-%d-%H")
    return None


def review_due(now_utc: datetime):
    from modules.event_clock import NY
    loc = now_utc.astimezone(NY)
    if (loc.hour, loc.minute) >= REVIEW_AFTER:
        return loc.strftime("%Y-%m-%d")
    return None


def build_top(fetch, syms, top: int = 7):
    from modules import daily_top, day_plan, intermarket
    plans = day_plan.scan(syms, fetch, mode="conf")
    watch = day_plan.scan_watch(syms, fetch)
    try:
        smt = intermarket.scan_pairs(fetch, tfs=("15m", "1h", "4h"))
    except Exception:
        smt = []
    calm = {}
    for s in syms:
        try:
            calm[s] = daily_top.calm_stats(fetch(s, "1h"))
        except Exception:
            calm[s] = None
    from modules import brain
    try:
        weights = brain.school_weights(brain.load(), brain.load_graded())
    except Exception:
        weights = {}
    items = daily_top.rank(plans, smt, watch, calm, top=top, weights=weights)
    return items, plans, watch, smt


def run(now_utc: datetime, fetch, send, sent: dict, calendar_rows=None, dry: bool = False, log: list | None = None) -> list:
    """Do one pass; returns the list of messages (also sent through send(text) unless dry). `sent` is mutated."""
    from modules import brain, daily_top, day_plan, event_clock
    now = now_utc.timestamp()
    msgs = []
    agent_log = []   # contract objects found in this pass (saved below, summarised in the daily review)

    def out(key, text):
        if key in sent:
            return
        msgs.append(text)
        if not dry:
            err = send(text)
            if err:
                msgs.append("ERR " + err)
                return
        sent[key] = now

    for a in event_clock.due(now_utc, calendar_rows):
        out(a["id"], event_clock.format_alert(a))
    syms = symbols()
    # setup alerts: each key that fired (CISD, CRT, SMT, ICT, Elliott wave 3, chart patterns ...) with its own plan and a possible move >= BRAIN_MIN_POINTS (default 100 points); at most BRAIN_MAX_SETUPS per pass
    try:
        cap = int(os.environ.get("BRAIN_MAX_SETUPS", "5"))
        day = now_utc.strftime("%Y-%m-%d")
        sent_n = 0
        for a in day_plan.scan_setups(syms, fetch, min_points=float(os.environ.get("BRAIN_MIN_POINTS", "100"))):
            if sent_n >= cap:
                break
            k = f"{a['id']}|{day}"
            if k in sent:
                continue
            out(k, day_plan.format_setup(a))
            sent_n += 1
    except Exception as e:
        msgs.append(f"(setup alerts skipped: {type(e).__name__})")
    # SMT between correlated pairs: fresh divergences (<= 3 bars old) on 15m and above
    try:
        from modules import intermarket
        for e in intermarket.scan_pairs(fetch, tfs=("15m", "1h", "4h")):
            if e["bars_ago"] <= 3:
                out(f"smt|{e['id']}", f"🔔 <b>SMT</b> {intermarket.chips([e], ar=True)[0]['label']} · {e['session']}\n{e['text_ar']}")
    except Exception:
        pass
    # liquidity sweeps of previous day / week / month highs and lows and the Asian range (fresh: last 3 hourly candles)
    try:
        from modules import level_sweeps
        found = level_sweeps.scan(syms, fetch)[:int(os.environ.get("BRAIN_MAX_SWEEPS", "4"))]
        agent_log.extend(_agent_results(sweeps=found))
        for a in found:
            out(a["id"], level_sweeps.format_sweep(a))
    except Exception as e:
        msgs.append(f"(sweeps skipped: {type(e).__name__})")
    # news from outside the calendar (RSS, tiers A / B / C); dedupe by normalized title
    if os.environ.get("BRAIN_NEWS", "1") != "0":
        try:
            from modules import news_watch
            items, _dead = news_watch.fetch_all(news_watch.default_fetch_text)
            fresh = news_watch.alerts(items, now_utc)[:int(os.environ.get("BRAIN_MAX_NEWS", "3"))]
            agent_log.extend(_agent_results(news=fresh))
            for a in fresh:
                out(a["id"], news_watch.format_news(a))
        except Exception as e:
            msgs.append(f"(news skipped: {type(e).__name__})")
    # all-horizon scan (scalp / day / swing / position), A+ and A only, at the 4-hour marks of the New York clock
    hs = horizon_slot(now_utc)
    if hs and f"hz|{hs}" not in sent:
        try:
            from modules import horizons
            plans = horizons.scan(syms, fetch)
            agent_log.extend(_agent_results(plans=plans))
            if plans or os.environ.get("BRAIN_HZ_EMPTY", "0") == "1":
                out(f"hz|{hs}", horizons.format_digest(plans))
            else:
                sent[f"hz|{hs}"] = now
            if plans and not dry:
                brain.record([dict(p, points=len(p["schools"])) for p in plans], now)
        except Exception as e:
            msgs.append(f"(horizons skipped: {type(e).__name__})")
    slot = digest_slot(now_utc)
    if slot and f"top7|{slot[1]}|{slot[0]}" not in sent:
        items, _p, _w, _s = build_top(fetch, syms, int(os.environ.get("BRAIN_TOP", "7")))
        out(f"top7|{slot[1]}|{slot[0]}", daily_top.format_top(items, day_plan.session_clock(now_utc)))
        if not dry and items:
            brain.record(items, now)
    if agent_log and not dry:
        try:
            from modules import agent_result
            agent_result.save(agent_log, AGENTS_FILE)
        except Exception as e:
            msgs.append(f"(agent results not saved: {type(e).__name__})")
    # grade what is old enough, and review once after the New York close
    entries = brain.load()
    graded = brain.load_graded()
    if entries:
        n = brain.grade(entries, graded, fetch, now)
        if n and not dry:
            brain.save_graded(graded)
        rd = review_due(now_utc)
        if rd and entries and f"review|{rd}" not in sent:
            try:
                from modules import agent_result
                res = agent_result.load(AGENTS_FILE, rd) + agent_result.load_dir(AGENTS_DIR, rd)
                block = agent_result.text(agent_result.summarize(res))
            except Exception:
                block = ""   # the review must go out even when the agents block cannot be built
            out(f"review|{rd}", brain.review_text(entries, graded, agents=block))
    if log is not None:
        log.append(f"{len(msgs)} message(s)")
    return msgs


def main(argv):
    dry = "--dry" in argv
    from modules import telegram_alerts as TA
    from modules.market_cache import get_klines
    rows = []
    try:
        from modules.calendar_feed import fetch_calendar
        rows = fetch_calendar()
    except Exception:
        rows = []
    sent = load_state()
    msgs = run(datetime.now(timezone.utc), lambda s, t: get_klines(s, t, 300), TA.send, sent, rows, dry)
    if not dry:
        save_state(sent)
    for m in msgs:
        print((m.replace("\n", " | "))[:200])
    print(f"brain_cron: {len(msgs)} message(s){' (dry)' if dry else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
