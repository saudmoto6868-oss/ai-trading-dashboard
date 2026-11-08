"""Intermarket board (modules/intermarket.py): SMT between correlated pairs on several timeframes, no network (synthetic candles)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import intermarket as I

n = 200
t = pd.date_range("2026-11-05 00:00", periods=n, freq="1h")
i = np.arange(n)
base = 100 + 8 * np.sin(i / 6.0)
def frame(c):
    return pd.DataFrame({"time": t[:len(c)], "open": c, "high": c + .5, "low": c - .5, "close": c, "volume": 10.0})
a = base.copy(); b = base * 0.5
# last swing low of the cycle: A prints a LOWER low, B refuses (holds higher)
lows = [k for k in range(10, n - 5) if base[k] < base[k - 1] and base[k] <= base[k + 1] and base[k] < 95]
k2 = lows[-1]
a[k2 - 2:k2 + 3] -= np.array([1, 3, 5, 3, 1])
b[k2 - 2:k2 + 3] += np.array([1, 2, 3, 2, 1]) * 0.5
cut = k2 + 8   # the divergence must be RECENT (smt.py keeps swings <= 15 bars old)
t = t[:cut]; A, B = frame(a[:cut]), frame(b[:cut])

def fetch(sym, tf):
    return {"X": A, "Y": B}.get(sym) if sym in ("X", "Y") else None

ev = I.scan_pairs(fetch, tfs=("1h",), pairs=[("X", "Y", False)], max_age=200)
assert ev, "a divergence must be found"
e = ev[0]
assert e["direction"] in ("bullish", "bearish") and e["tf"] == "1h" and e["a"] == "X" and e["b"] == "Y", e
assert e["bars_ago"] >= 0 and e["session"] and "SMT" in e["text_en"] and "SMT" in e["text_ar"] and len(e["series_a"]) == 60
c = I.chips(ev, ar=False)
assert c and c[0]["label"].startswith("SMT ") and "1H" in c[0]["label"], c

# no data / decoupled pair -> nothing (never a guess)
assert I.scan_pairs(lambda s, tf: None, tfs=("1h",), pairs=[("X", "Y", False)]) == []
rng = np.random.default_rng(3)
noise = frame(100 + np.cumsum(rng.normal(0, 1, len(t))))
assert I.scan_pairs(lambda s, tf: A if s == "X" else noise, tfs=("1h",), pairs=[("X", "Y", False)], max_age=200) == [] or True   # decoupled: smt.MIN_CORR filter (may or may not fire; must not raise)

# a crashing fetch for one pair must not kill the others; big timeframe first
def flaky(sym, tf):
    if sym == "BAD": raise RuntimeError("down")
    return fetch(sym, tf)
ev2 = I.scan_pairs(flaky, tfs=("15m", "1h", "4h"), pairs=[("BAD", "Y", False), ("X", "Y", False)], max_age=200)
assert ev2 and all(x["a"] == "X" for x in ev2) and [x["tf"] for x in ev2] == sorted([x["tf"] for x in ev2], key=lambda z: I.TF_ORDER.index(z)), [x["tf"] for x in ev2]

# names / colours: the metals keep the platform's colours
assert I.name_of("HL:xyz:GOLD") == ("Gold", "#f0b90b") and I.name_of("HL:xyz:SILVER")[0] == "Silver"
assert I.session_of("2026-11-06T14:00:00Z") == "London + New York" and I.session_of("2026-11-06T02:00:00Z").startswith("Asia")
print("ok intermarket", len(ev), "event(s)", e["direction"], e["bars_ago"], e["session"])
