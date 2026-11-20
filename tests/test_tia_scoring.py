"""TIA Director track record: scoring, abstain, pending, Wilson interval, not-evidence rule. Synthetic candles, no network.
Run: PYTHONPATH=. python3 tests/test_tia_scoring.py"""
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import pandas as pd  # noqa: E402
from modules import tia_intelligence as T, tia_scoring as S  # noqa: E402

T0 = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)
NOW = datetime(2026, 11, 20, tzinfo=timezone.utc)


def daily(start_px, step, days=30, ms=False):
    ts = [datetime(2026, 11, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(days)]
    t = [int(x.timestamp() * 1000) for x in ts] if ms else ts
    return pd.DataFrame({"time": t, "close": [start_px + step * i for i in range(days)]})


def entry(stance="BULLISH BIAS", px=100.0, when=T0, symbol="BTC-USDT"):
    return {"asof_utc": when.isoformat(), "symbol": symbol, "stance": stance, "price": px}


up = lambda sym, tf, limit: daily(100.0, 1.0)
down = lambda sym, tf, limit: daily(100.0, -1.0)

# 1. direction: a bullish call in a rising market hits, a bearish one misses; the return is signed by the stance
r = S.score_entry(entry("BULLISH BIAS"), up, NOW)
assert r["status"] == "scored" and r["hit"] is True and r["ret_pct"] > 0, r
r = S.score_entry(entry("BEARISH BIAS"), up, NOW)
assert r["status"] == "scored" and r["hit"] is False and r["ret_pct"] < 0, r
print("ok hit / miss follows the stance direction")

# 2. non-directional stances abstain
for st in ("MIXED / WAIT", "UNCONFIRMED", "UNAVAILABLE"):
    assert S.score_entry(entry(st), up, NOW)["status"] == "abstain"
print("ok abstain stances are not scored")

# 3. too early, or the bar does not exist yet -> pending; missing price -> unscorable
assert S.score_entry(entry(when=NOW - timedelta(days=1)), up, NOW)["status"] == "pending"
short = lambda sym, tf, limit: daily(100.0, 1.0, days=3)
assert S.score_entry(entry(), short, NOW)["status"] == "pending"
assert S.score_entry({"asof_utc": T0.isoformat(), "symbol": "X", "stance": "BULLISH BIAS"}, up, NOW)["status"] == "unscorable"
print("ok pending / unscorable")

# 4. millisecond timestamps work too
r = S.score_entry(entry(), lambda s, tf, l: daily(100.0, 1.0, ms=True), NOW)
assert r["status"] == "scored" and r["hit"] is True, r
print("ok millisecond time column")

# 5. a fetch failure is unscorable, never an exception
def boom(*a):
    raise RuntimeError("feed down")
assert S.score_entry(entry(), boom, NOW)["status"] == "unscorable"
print("ok fetch failure")

# 6. Wilson interval sanity
assert S.wilson(0, 0) is None
lo, hi = S.wilson(8, 10)
assert 0 <= lo < 0.8 < hi <= 1.0, (lo, hi)
lo2, hi2 = S.wilson(80, 100)
assert (hi2 - lo2) < (hi - lo), "more samples must give a narrower interval"
print("ok wilson interval", S.wilson(8, 10))

# 7. verdicts: under 30 scored runs it is NOT evidence, even at 100% hits
few = S.summarize([entry(when=T0 + timedelta(hours=i)) for i in range(10)], up, NOW)
assert few["scored"] == 10 and few["hit_rate"] == 1.0 and few["verdict"].startswith("not evidence"), few
many = S.summarize([entry(when=T0 + timedelta(hours=i)) for i in range(40)], up, NOW)
assert many["scored"] == 40 and many["wilson95"][0] > 0.5 and "above 50%" in many["verdict"], many
mix = S.summarize([entry("BULLISH BIAS" if i % 2 else "BEARISH BIAS", when=T0 + timedelta(hours=i)) for i in range(40)], up, NOW)
assert mix["wilson95"][0] <= 0.5 and "no edge" in mix["verdict"], mix
print("ok verdicts: n<30 not evidence;", many["hit_rate"], "->", many["verdict"][:40])

# 8. a half-written log line does not break loading
p = os.path.join(tempfile.mkdtemp(), "log.jsonl")
open(p, "w").write(json.dumps(entry()) + "\n{broken json\n" + json.dumps(entry("BEARISH BIAS")) + "\n")
assert len(S.load_log(p)) == 2 and S.load_log(p + ".missing") == []
print("ok log loading")

# 9. the Director log row now carries the entry price
T.LOG_PATH = p = os.path.join(tempfile.mkdtemp(), "log2.jsonl")
T.log_report({"asof_utc": T0.isoformat(), "symbol": "BTC-USDT", "stance": "BULLISH BIAS",
              "technical": {"1h": {"status": "ok", "last": 123.4}, "1d": {"status": "ok", "last": 120.0}}})
row = json.loads(open(p).read())
assert row["price"] == 123.4, row
T.log_report({"symbol": "X", "stance": "MIXED / WAIT", "technical": {"1h": {"status": "unavailable"}}})
assert json.loads(open(p).read().splitlines()[1])["price"] is None
print("ok Director log row has the entry price")

# 10. track_record reads the log, caches, and returns None for an empty log
lp = os.path.join(tempfile.mkdtemp(), "t.jsonl")
assert S.track_record(lp, up, ttl=0) is None
open(lp, "w").write("\n".join(json.dumps(entry(when=T0 + timedelta(hours=i))) for i in range(5)) + "\n")
tr = S.track_record(lp, up, ttl=0)
assert tr and tr["runs"] == 5 and tr["scored"] == 5 and tr["verdict"].startswith("not evidence"), tr
print("ok track_record from the log file")
print("ALL OK")
