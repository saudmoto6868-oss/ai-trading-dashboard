"""Spot brain learning loop: record / score / summary (modules/spot_learn.py). Synthetic data, no network. Plain script."""
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import spot_learn as L

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def bars(start, closes, highs=None, lows=None, step=1):
    out = []
    for i, c in enumerate(closes):
        t = (start + timedelta(days=i * step)).isoformat()
        out.append({"time": t, "close": c, "high": (highs[i] if highs else c), "low": (lows[i] if lows else c)})
    return out


# 1. record: one row per horizon, appended to JSONL, read back
brain = {"asset": "GOLD", "price": 100.0, "horizons": {
    "day": {"verdict": "buy", "score": 45, "entry": (99, 101), "stop": 95, "target": 110},
    "week": {"verdict": "wait", "score": 0, "entry": None, "stop": None, "target": None}}}
tmp = Path(tempfile.mkdtemp()) / "log.jsonl"
assert L.record(brain, tmp, when=T0) == 2
rows = L.load(tmp)
assert len(rows) == 2 and {r["horizon"] for r in rows} == {"day", "week"} and rows[0]["asset"] == "GOLD"
with open(tmp, "a", encoding="utf8") as f:
    f.write("{torn line\n")                       # a torn line must not break the log
assert len(L.load(tmp)) == 2

# 2. score: pending until the horizon has passed (no early scoring)
buy = {"time": T0.isoformat(), "asset": "GOLD", "horizon": "day", "verdict": "buy", "price": 100.0, "target": 110.0, "stop": 95.0}
flat = bars(T0 + timedelta(days=1), [101, 102, 101])
assert L.score([buy], {"GOLD": flat}, now=T0 + timedelta(days=2)) == []          # 3-day horizon not over yet

# 3. target hit first -> ret = target / price - 1, outcome target
hit = bars(T0 + timedelta(days=1), [101, 105, 112], highs=[101, 105, 112], lows=[100, 104, 105])
s = L.score([buy], {"GOLD": hit}, now=T0 + timedelta(days=4))
assert len(s) == 1 and s[0]["outcome"] == "target" and abs(s[0]["ret"] - 0.10) < 1e-9

# 4. stop hit first -> outcome stop, ret at the stop
stop = bars(T0 + timedelta(days=1), [99, 94, 96], highs=[100, 99, 97], lows=[98, 94, 95])
s = L.score([buy], {"GOLD": stop}, now=T0 + timedelta(days=4))
assert s[0]["outcome"] == "stop" and abs(s[0]["ret"] - (-0.05)) < 1e-9

# 5. no look-ahead: bars before the record time are ignored
before = bars(T0 - timedelta(days=5), [200, 200, 200], highs=[300, 300, 300], lows=[1, 1, 1])
s = L.score([buy], {"GOLD": before + flat}, now=T0 + timedelta(days=4))
assert s[0]["outcome"] == "time" and abs(s[0]["ret"] - 0.01) < 1e-9

# 6. sell side: the sign flips, a drop helps
sell = {"time": T0.isoformat(), "asset": "GOLD", "horizon": "day", "verdict": "sell", "price": 100.0, "target": None, "stop": None}
drop = bars(T0 + timedelta(days=1), [95, 90, 90])
s = L.score([sell], {"GOLD": drop}, now=T0 + timedelta(days=4))
assert s[0]["ret"] > 0.09, s[0]

# 7. wait verdict is not scored
assert L.score([{**buy, "verdict": "wait"}], {"GOLD": hit}, now=T0 + timedelta(days=4)) == []

# 8. summary: n < 30 is never called evidence; a strong, consistent group gets the label; noise does not
few = [{"horizon": "day", "verdict": "buy", "ret": 0.02, "outcome": "time"}] * 5
assert L.summary(few)["day|buy"]["label"].startswith("مش دليل")
strong = [{"horizon": "day", "verdict": "buy", "ret": 0.02 + 0.001 * (i % 3), "outcome": "target"} for i in range(40)]
assert L.summary(strong)["day|buy"]["label"].startswith("اشتغل"), L.summary(strong)
noise = [{"horizon": "day", "verdict": "buy", "ret": (0.03 if i % 2 else -0.03), "outcome": "time"} for i in range(40)]
assert L.summary(noise)["day|buy"]["label"].startswith("مفيش"), L.summary(noise)
worse = [{"horizon": "week", "verdict": "accumulate", "ret": -0.02 - 0.001 * (i % 3), "outcome": "stop"} for i in range(40)]
assert L.summary(worse)["week|accumulate"]["label"].startswith("كان أسوأ")
# 9. every live setup is logged (options kept side by side), scored by its own id, never by a verdict
br2 = {"asset": "GOLD", "price": 100.0, "horizons": {}, "setups": [
    {"id": "ew_w2", "tf": "1w", "side": "buy", "entry": (99, 101), "stop": 95, "target": 110},
    {"id": "cl_death", "tf": "1d", "side": "exit", "entry": None, "stop": None, "target": None}]}
tmp2 = Path(tempfile.mkdtemp()) / "setups.jsonl"
assert L.record_setups(br2, tmp2, when=T0) == 2
srows = L.load(tmp2)
assert {r["id"] for r in srows} == {"ew_w2", "cl_death"} and {r["verdict"] for r in srows} == {"buy", "sell"}
sc = L.score(srows, {"GOLD": bars(T0 + timedelta(days=1), [100] * 60)}, now=T0 + timedelta(days=200))
assert {r["id"] for r in sc} == {"ew_w2", "cl_death"}
assert set(L.summary(sc)) == {"ew_w2", "cl_death"}
assert L.summary(sc)["ew_w2"]["n"] == 1

# 10. stability: a group that keeps its sign in both halves 'holds'; a sign flip 'flips'; too few rows 'not yet'
hold = [{"id": "x", "time": (T0 + timedelta(days=i)).isoformat(), "ret": 0.01 + 0.001 * i} for i in range(24)]
flip = [{"id": "y", "time": (T0 + timedelta(days=i)).isoformat(), "ret": (0.02 if i < 12 else -0.02)} for i in range(24)]
few = [{"id": "z", "time": (T0 + timedelta(days=i)).isoformat(), "ret": 0.01} for i in range(5)]
st = L.stability(hold + flip + few)
assert st == {"x": "holds", "y": "flips", "z": "not yet"}, st
print("test_spot_learn OK")
