"""Brain v2: news watch (RSS), level sweeps, horizons grading, experimental school weights, cron wiring. Synthetic, no network."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np, pandas as pd
tmp = Path(tempfile.mkdtemp())
os.environ.update(BRAIN_LOG=str(tmp / "log.jsonl"), BRAIN_GRADED=str(tmp / "graded.json"), BRAIN_SENT=str(tmp / "sent.json"))
from modules import news_watch as N, level_sweeps as LS, horizons as H, brain as B, daily_top as T, brain_cron as C

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)
def rfc(d): return d.strftime("%a, %d %b %Y %H:%M:%S +0000")
RSS = f"""<?xml version="1.0"?><rss><channel>
<item><title>Fed holds rates, signals inflation still sticky</title><link>http://x/1</link><pubDate>{rfc(NOW - timedelta(minutes=30))}</pubDate></item>
<item><title>Fed holds rates, signals inflation still sticky</title><link>http://x/1b</link><pubDate>{rfc(NOW - timedelta(minutes=20))}</pubDate></item>
<item><title>Local bakery wins award</title><link>http://x/2</link><pubDate>{rfc(NOW - timedelta(minutes=10))}</pubDate></item>
<item><title>Old Fed news on rates</title><link>http://x/3</link><pubDate>{rfc(NOW - timedelta(hours=9))}</pubDate></item>
</channel></rss>"""
ATOM = """<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Exchange hack: SEC sues crypto firm</title><link href="http://y/1"/><updated>2026-11-06T11:40:00Z</updated></entry></feed>"""
items = N.parse_feed(RSS, "Fed", "A")
assert len(items) == 4 and items[0]["time"] is not None
assert N.parse_feed("not xml", "x", "A") == []
at = N.parse_feed(ATOM, "CoinDesk", "C")
assert len(at) == 1 and at[0]["url"] == "http://y/1" and at[0]["time"] is not None
al = N.alerts(items, NOW)
assert len(al) == 1 and "Fed holds" in al[0]["title"], al            # dedupe, irrelevant and stale dropped
assert N.classify("Local bakery wins award") is None
# tier C: only its strong topics; a macro-only headline from a crypto site is ignored
assert N.classify("Fed holds rates", "C") is None
assert N.classify("Exchange hack: SEC sues crypto firm", "C") is not None
txt = N.format_news(al[0])
assert "either way" in N.format_news(al[0], ar=False) and "مش إشارة" in txt
items2, dead = N.fetch_all(lambda u: RSS if "federalreserve" in u else (_ for _ in ()).throw(RuntimeError("x")))
assert items2 and dead and len(dead) == len(N.SOURCES) - 1

# 2) level sweeps
def mk1h(n, base=100.0, end=None):
    t = pd.date_range(end=end or "2026-11-06 12:00", periods=n, freq="h")
    c = np.full(n, base)
    return pd.DataFrame({"time": t, "open": c, "high": c + 0.5, "low": c - 0.5, "close": c, "volume": 1.0})
d_t = pd.date_range(end="2026-11-06", periods=60, freq="D")
d1 = pd.DataFrame({"time": d_t, "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1.0})
w_t = pd.date_range(end="2026-11-02", periods=20, freq="W-MON")
w1 = pd.DataFrame({"time": w_t, "open": 100.0, "high": 102.0, "low": 98.0, "close": 100.0, "volume": 1.0})
lv = LS._prior_levels(d1, w1)
assert lv["PDH"] == 101 and lv["PDL"] == 99 and lv["PWH"] == 102 and lv["PWL"] == 98 and "PMH" in lv, lv
h1 = mk1h(80)
assert LS.find("X", h1, d1, w1) == []                    # nothing swept
h1b = h1.copy(); h1b.loc[h1b.index[-2], ["high"]] = 102.4; h1b.loc[h1b.index[-2], ["close"]] = 100.5   # wicks above PWH and PDH, closes back
f = LS.find("X", h1b, d1, w1)
names = {a["level_name"] for a in f}
assert {"PWH", "PDH"} <= names and all(a["direction"] == "bearish" for a in f if a["level_name"] in ("PWH", "PDH")), f
assert f[0]["size"] == "big"                              # big first
h1c = h1.copy(); h1c.loc[h1c.index[-1], ["low"]] = 97.5; h1c.loc[h1c.index[-1], ["close"]] = 99.6    # sweeps PWL and PDL, closes back above
g = LS.find("X", h1c, d1, w1)
assert any(a["level_name"] == "PWL" and a["direction"] == "bullish" for a in g)
h1d = h1.copy(); h1d.loc[h1d.index[-1], ["high"]] = 103; h1d.loc[h1d.index[-1], ["close"]] = 103      # a real breakout (closes above) is NOT a sweep
assert not [a for a in LS.find("X", h1d, d1, w1) if a["level_name"] in ("PWH", "PDH")]
assert "سحب" in LS.format_sweep(f[0]) and "hint" in LS.format_sweep(f[0], ar=False)

# 3) horizons: grading and building
assert H.grade_of(4, 2.0, True) == "A+" and H.grade_of(4, 2.0, True, choppy=True) == "A" and H.grade_of(3, 1.5, True) == "A"
assert H.grade_of(2, 3.0, True) == "B" and H.grade_of(5, 3.0, False) == "B"
assert H.build("X", {}, "swing") == [] and H.build("X", {"1w": None, "1d": None}, "position") == []
assert H.scan(["X"], lambda s, t: None) == []
plan = {"horizon": "swing", "grade": "A+", "direction": "bullish", "symbol": "XAU", "tf": "4h", "entry": 1, "stop": 0.9, "tps": [1.1, 1.2, 1.3], "move_points": 300, "rr1": 2.0, "schools": ["a", "b", "c", "d"],
        "confluence": {"n": 3, "of": 3}, "exit": {"text_ar": "x", "text_en": "y"}}
assert "A+" in H.format_plan(plan) and "سوينج" in H.format_plan(plan) and "swing" in H.format_plan(plan, ar=False)
assert "مفيش" in H.format_digest([]) and "A+" in H.format_digest([plan])

# 4) experimental school weights: bounded, shrunk, off switch, applied to ranking
ents, gr = [], {}
for i in range(40):
    for sc, r in (("Good", 2.0), ("Bad", -1.0), ("Few", 3.0)):
        if sc == "Few" and i >= 4:
            continue
        e = {"id": f"{sc}{i}", "schools": [sc], "keys": []}; ents.append(e); gr[e["id"]] = {"r": r}
w = B.school_weights(ents, gr)
assert 1.0 < w["Good"] <= 1.3 and 0.7 <= w["Bad"] < 1.0 and "Few" not in w, w      # n<10 gets no weight
assert w["Good"] == 1.3 and w["Bad"] == 0.7          # clamped
os.environ["BRAIN_ADAPT"] = "0"
assert B.school_weights(ents, gr) == {}
os.environ.pop("BRAIN_ADAPT")
base = {"symbol": "S", "direction": "bullish", "stars": 3, "schools": ["Good", "Good2", "Bad"], "rr1": 2.0, "confluence": {"n": 3, "of": 5, "agree": ["1d", "4h", "1h"]}}
p0, _ = T.score_plan(base)
p1, why = T.score_plan(base, weights={"Good": 1.3, "Bad": 0.7})
assert p1 - p0 in (0, -0, 0, 1, -1) and isinstance(p1, int)
assert T.score_plan(base, weights={"Bad": 0.7, "Good": 1.3, "Good2": 1.3})[0] >= p0

# 5) cron: sweeps + news + horizons slot, deduped across two passes
assert C.horizon_slot(datetime(2026, 11, 6, 17, 10, tzinfo=timezone.utc)) is not None      # 12:10 NY
assert C.horizon_slot(datetime(2026, 11, 6, 18, 10, tzinfo=timezone.utc)) is None          # 13:10 NY
assert C.horizon_slot(datetime(2026, 11, 6, 17, 40, tzinfo=timezone.utc)) is None          # past the first 30 min
N.default_fetch_text = lambda url: RSS if "federalreserve" in url else ""
os.environ["BRAIN_SYMBOLS"] = "X"
def fetch(s, tf):
    return {"1h": h1b, "1d": d1, "1w": w1}.get(tf)
sent = {}
now = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)
m1 = C.run(now, fetch, lambda t: None, sent, [], dry=False)
assert any("سحب" in m for m in m1) and any("Fed holds" in m for m in m1), m1
m2 = C.run(now + timedelta(minutes=30), fetch, lambda t: None, sent, [], dry=False)
assert not any("سحب سيولة" in m or "Fed holds" in m for m in m2), m2
print("test_brain_v2: ok")

# 6) agent results feed the daily review (contract objects from the brain's own jobs + files dropped by other streams)
import json as _json
from modules import agent_result as AR
AF = tmp / "agents.jsonl"
os.environ["BRAIN_AGENTS"] = str(AF)
C.AGENTS_FILE = AF
drop = tmp / "drop"; drop.mkdir()
C.AGENTS_DIR = str(drop)
day = "2026-11-06"
good = AR.make("level_scanner", "grok", "HL:xyz:GOLD", "bullish", [{"what": "swept PDL"}], "Hyperliquid", "delayed", 12, ts=day + "T10:00:00Z")
badr = {"agent": "x", "stream": "grok", "symbol": "S", "verdict": "buy", "source": "a", "ts": day + "T10:00:00Z", "quality": "live"}
(drop / "grok.jsonl").write_text(_json.dumps(good) + "\n" + _json.dumps(badr) + "\n" + "not json\n")
mine = C._agent_results(sweeps=[{"symbol": "X", "direction": "bearish", "level_name": "PWH", "level": 102.0}], news=[{"title": "Fed holds", "source": "Fed", "topics": ["rates"]}],
                        plans=[{"symbol": "X", "direction": "bullish", "schools": ["Wyckoff"], "horizon": "swing", "tf": "4h", "grade": "A"}])
assert len(mine) == 3 and all(AR.validate(r) == [] for r in mine), [AR.validate(r) for r in mine]
for r in mine:
    r["ts"] = day + "T11:00:00Z"
assert AR.save(mine, AF) == 3
res = AR.load(AF, day) + AR.load_dir(drop, day)
sm = AR.summarize(res)
assert sm["by_agent"]["level_scanner"] == {"bearish": 1, "bullish": 1} and sm["by_agent"]["context_monitor"] == {"info": 1} and len(sm["invalid"]) == 1, sm
txt = AR.text(sm)
assert "level_scanner" in txt and "⚠" in txt
rv = B.review_text([], {}, agents=txt)
assert "مفيش أفكار" in rv or "level_scanner" in rv         # empty brain: the plain message; with graded ideas the agents block is appended
e1 = {"id": "z1", "schools": ["Wyckoff"], "keys": []}
assert "level_scanner" in B.review_text([e1], {"z1": {"r": 1.0}}, agents=txt)
print("test_brain_v2 agents: ok")
