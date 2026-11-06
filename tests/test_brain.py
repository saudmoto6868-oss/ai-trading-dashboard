"""Event clock, Daily Top 7, Brain memory and the brain cron (modules/event_clock.py, daily_top.py, brain.py, brain_cron.py). Synthetic, no network, no Telegram."""
import os, sys, tempfile, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
tmp = Path(tempfile.mkdtemp())
os.environ.update(BRAIN_LOG=str(tmp / "log.jsonl"), BRAIN_GRADED=str(tmp / "graded.json"), BRAIN_SENT=str(tmp / "sent.json"))
from modules import event_clock as E, daily_top as T, brain as B, brain_cron as C, day_plan as D, intermarket as IM

U = lambda *a: datetime(*a, tzinfo=timezone.utc)

# 1) event clock (Nov 2026 = EST, UTC-5)
ids = lambda now, rows=None: [a["id"].split("|")[1] + ("@" + a["id"].split("|")[0]) for a in E.due(now, rows)]
a = E.due(U(2026, 11, 6, 7, 30))                       # 02:30 NY: London opens and its Silver Bullet in 30 min
assert {x["id"].split("|")[1] for x in a} >= {"open_london", "sb_london"} and all(x["in_min"] == 30 for x in a if x["kind"] == "window"), [x["id"] for x in a]
b = E.due(U(2026, 11, 6, 14, 30))                      # 09:30 NY: stocks open now, NY AM Silver Bullet in 30 min, the 15 minute range sets at 09:45
k = {x["id"].split("|")[0] + ":" + x["id"].split("|")[1] for x in b}
assert {"win:open_ny_stocks", "win:sb_ny_am", "or15:open_ny_stocks"} <= k, k
assert not [x for x in E.due(U(2026, 11, 6, 21, 0)) if x["kind"] == "window" and x["id"].split("|")[1].startswith("sb_")]   # 16:00 NY: no Silver Bullet near
# news: a high impact event at 13:30 UTC (08:30 NY): alerts at ~120 / 60 / 30 minutes, each once-per-threshold id, medium impact ignored
ev = {"title": "CPI m/m", "country": "USD", "ts": int(U(2026, 11, 6, 13, 30).timestamp() * 1000), "impact": "High", "forecast": "0.3%", "previous": "0.2%"}
mid = {**ev, "title": "Housing", "impact": "Medium"}
for mins, want in ((125, True), (118, True), (60, True), (32, True), (90, False), (5, False)):
    now = U(2026, 11, 6, 13, 30) - timedelta(minutes=mins)
    got = [x for x in E.due(now, [ev, mid]) if x["kind"] == "news"]
    assert bool(got) == want, (mins, got)
    assert all("CPI" in x["title_en"] and "either way" in x["note_en"] for x in got)
assert len({x["id"] for x in E.due(U(2026, 11, 6, 13, 30) - timedelta(minutes=60), [ev]) if x["kind"] == "news"}) == 1
txt = E.format_alert([x for x in E.due(U(2026, 11, 6, 12, 30), [ev]) if x["kind"] == "news"][0], ar=True)
assert "<b>" in txt and "مش إشارة دخول" in txt
# boundaries: crypto month start / month end, week open
mon = [x for x in E.due(U(2026, 11, 30, 23, 0)) if x["kind"] == "boundary"]
assert {x["id"].split("|")[1] for x in mon} >= {"day_crypto", "month_end", "month_start"}, mon       # 23:00 UTC Nov 30: the new month opens at 00:00 UTC
sun = [x for x in E.due(U(2026, 11, 8, 21, 30)) if x["kind"] == "boundary"]                          # Sunday 16:30 NY: FX week opens 17:00 NY
assert any(x["id"].split("|")[1] == "week_fx" for x in sun), sun

# 2) Daily Top 7: calm first, then confirmation; one idea per symbol
def plan(sym, d="bullish", n=4, stars=3, schools=("Fibonacci", "SMC / ICT"), tf="15m", rr=1.6, kz=None):
    return {"id": f"plan|{sym}|{d}|{tf}|conf", "symbol": sym, "mode": "conf", "tf": tf, "direction": d, "stars": stars, "price": 100.0, "entry": 100.0, "stop": 99.0, "tps": [101.5, 103.0, 105.0], "risk_points": 100,
            "move_points": 500, "rr1": rr, "point": 0.01, "confluence": {"bias": d, "bias_strength": 2, "agree": ["1d", "4h", "1h", "15m"][:n], "n": n, "of": 5, "views": {}}, "schools": list(schools),
            "reasons": [], "keys": ["ote", "ob"], "exit": D.exit_plan({"entry": 100.0, "stop_loss": 99.0, "take_profits": [101.5, 103.0, 105.0]}, "conf", 1.0, 0.01), "atr": 1.0, "session": {"kill_zone": kz, "active": []}, "t": "x"}
plans = [plan("CALM-A", n=3, schools=("Fibonacci",)), plan("CALM-B", n=5, schools=("Fibonacci", "SMC / ICT", "Elliott wave")), plan("CHOP-C", n=5, schools=("Fibonacci", "SMC / ICT", "Elliott wave", "Price action")), plan("CALM-A", tf="1h", n=4)]
calm = {"CALM-A": {"atr_pct": .002, "er": .6}, "CALM-B": {"atr_pct": .003, "er": .5}, "CHOP-C": {"atr_pct": .004, "er": .1}, "X": {"atr_pct": .002, "er": .5}, "Y": {"atr_pct": .002, "er": .5}}
smt = [{"a": "CALM-B", "b": "Z", "direction": "bullish", "tf": "1h"}, {"a": "CALM-A", "b": "Z", "direction": "bearish", "tf": "1h"}]
top = T.rank(plans, smt, [{"symbol": "CALM-B", "direction": "bullish", "schools": ["Price action"]}], calm, top=7)
assert [r["symbol"] for r in top] == ["CALM-B", "CALM-A", "CHOP-C"], [r["symbol"] for r in top]          # one per symbol; choppy last even with the most schools; SMT / context lift CALM-B
assert top[2]["choppy"] and not top[0]["choppy"] and top[0]["points"] > top[1]["points"], [(r["symbol"], r["points"], r["choppy"]) for r in top]
assert any("SMT agrees" in w for w in top[0]["why"]) and not any("SMT" in w for w in top[1]["why"])          # the bearish SMT does not count for a bullish idea
assert T.calm_stats(pd.DataFrame({"high": np.linspace(101, 130, 60), "low": np.linspace(99, 128, 60), "close": np.linspace(100, 129, 60)}))["er"] > 0.9
rng = np.random.default_rng(2); c = 100 + np.cumsum(rng.normal(0, 1, 80)) * 0 + rng.normal(0, 1, 80)
assert T.calm_stats(pd.DataFrame({"high": c + .5, "low": c - .5, "close": c}))["er"] < 0.25
t7 = T.format_top(top, D.session_clock("2026-11-06T07:00:00Z"), ar=True)
assert "أحسن 7" in t7 and "CALM-B" in t7 and "هادي" in t7 and "متذبذب" in t7 and "مش نسبة نجاح" in t7 and len(t7) < 3900
assert "Nothing confirmed" in T.format_top([], None, ar=False)

# 3) brain memory: record -> grade with the plan's own exit rules -> stats / review
now = 1_800_000_000.0
n = B.record(top, now)
assert n == 3 and B.record(top, now + 5) == 0                                                     # no duplicates on the same day
entries = B.load()
assert len(entries) == 3 and entries[0]["exit"]["style"] == "partial+trail"
def fetch_after(sym, tf):                                                                           # price runs up 5R after the entry: every bullish idea wins big
    t = pd.date_range(pd.Timestamp(now, unit="s") + pd.Timedelta(minutes=15), periods=20, freq="15min")
    base = 100 + np.arange(20) * 0.5
    return pd.DataFrame({"time": t, "open": base, "high": base + 0.4, "low": base - 0.2, "close": base + 0.3, "volume": 1.0})
graded = B.load_graded()
assert B.grade(entries, graded, fetch_after, now + 3600) == 0                                      # too young (< 6 h)
assert B.grade(entries, graded, fetch_after, now + 7 * 3600) == 3 and all(v["r"] > 1.5 for v in graded.values())
assert B.grade(entries, graded, fetch_after, now + 8 * 3600) == 0                                  # graded once
st = B.stats(entries, graded)
assert st["all"]["n"] == 3 and st["all"]["win"] == 100.0 and not st["all"]["evidence"] and st["school"]["Fibonacci"]["n"] == 3
rv = B.review_text(entries, graded)
assert "مراجعة المخ" in rv and "Fibonacci" in rv and "n<30" in rv
B.save_graded(graded); assert B.load_graded() == graded

# 4) the cron pass: heads-ups + the Top 7 slot + once-only sending + dry mode
sent_msgs, state = [], {}
D.scan = lambda syms, fetch, mode="conf", **kw: plans
D.scan_watch = lambda syms, fetch: []
IM.scan_pairs = lambda fetch, **kw: smt
T.calm_stats = lambda df, n=20: calm["CALM-A"]
slot_now = U(2026, 11, 6, 13, 0)                                                                    # 08:00 NY = the New York pre-open slot; CPI at 13:30 UTC is 30 minutes away
(tmp / "log.jsonl").unlink(); (tmp / "graded.json").unlink()
m = C.run(slot_now, fetch_after, lambda t: sent_msgs.append(t) or None, state, [ev], dry=False)
assert any("أحسن 7" in x for x in m) and any("CPI" in x for x in m), m
assert len(B.load()) >= 1 and any(k.startswith("top7|2026-11-06|newyork") for k in state), state
m2 = C.run(slot_now + timedelta(minutes=10), fetch_after, lambda t: sent_msgs.append(t) or None, state, [ev], dry=False)
assert not any("أحسن 7" in x for x in m2) and not any("CPI" in x for x in m2), m2                  # same slot / same news: nothing is sent twice
sent_dry = []
m3 = C.run(U(2026, 11, 6, 8, 0), fetch_after, lambda t: sent_dry.append(t), {}, [], dry=True)
assert m3 and not sent_dry, "dry mode must not send"                                                 # 03:00 NY = London slot
slot = C.digest_slot(U(2026, 11, 6, 8, 30)); assert slot == ("london", "2026-11-06") and C.digest_slot(U(2026, 11, 6, 3, 0)) is None
assert C.review_due(U(2026, 11, 6, 22, 45)) == "2026-11-06" and C.review_due(U(2026, 11, 6, 20, 0)) is None
print("ok brain: events, top 7, memory, cron")
