"""Weekly/Daily/4H framework on synthetic frames: structure + EMA bias, coherence verdicts, scorer + quality integration."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from modules import mtf, scorer, telegram_alerts as T

def frame(kind, n=140, seed=0, freq="1D"):
    rng = np.random.RandomState(seed); t = np.arange(n)
    base = {"up": 100 + t * .5, "down": 170 - t * .5, "flat": 100 + 0 * t}[kind]
    c = base + 3 * np.sin(t / 3.0) + rng.randn(n) * .15          # trend + zig-zag swings
    o = np.r_[c[0], c[:-1]]; h = np.maximum(o, c) + .3; l = np.minimum(o, c) - .3
    return pd.DataFrame({"time": pd.date_range("2025-01-01", periods=n, freq=freq), "open": o, "high": h, "low": l, "close": c, "volume": 1.0})

up, down = mtf.tf_state(frame("up")), mtf.tf_state(frame("down"))
assert up["available"] and up["trend"] == "up" and up["bias"] == "bull" and up["strength"] == 2, up
assert down["trend"] == "down" and down["bias"] == "bear", down
assert mtf.tf_state(frame("up", n=30))["available"] is False and mtf.tf_state(None)["available"] is False

fr_up = {"1w": frame("up", freq="7D"), "1d": frame("up"), "4h": frame("up", freq="4h")}
m = mtf.analyse(fr_up, "bullish", "1d")
assert m["status"] == "aligned" and m["agree"] == 3 and m["of"] == 3, m
assert mtf.analyse(fr_up, "bearish", "1d")["status"] == "conflict"                       # weekly+daily against a short
fr_mix = {"1w": frame("up", freq="7D"), "1d": frame("up"), "4h": frame("down", freq="4h")}
assert mtf.analyse(fr_mix, "bullish", "1d")["status"] == "partial"                        # only the 4H disagrees -> not a conflict
assert mtf.analyse({"1w": frame("up", freq="7D")}, "bullish", "1w") is None              # < 2 frames -> nothing invented
# the trigger frame stands in for its own tf
only = {"1w": frame("up", freq="7D")}; d1 = frame("up")
assert mtf.analyse(only, "bullish", "1d", d1)["of"] == 2
en = mtf.lines_ar(m); assert len(en) == 4 and "aligned" in en[-1] and not any("؀" <= ch <= "ۿ" for ch in "".join(en)), en   # default language = English
ar = mtf.lines_ar(m, True); assert len(ar) == 4 and "متوافقة" in ar[-1] and "صاعد" in ar[0], ar

# scorer: fetch plan + result carries mtf
assert scorer.fetch_tfs("1d") == ["1d", "1w", "4h"] and scorer.fetch_tfs("1h") == ["1h", "1d", "1w"] and "4h" not in scorer.fetch_tfs("1m")
# quality: swing aligned +8 / conflict -12; day trade untouched
r = {"score": 4, "max_score": 7, "trade_type": "Swing", "context": {}, "against": [], "mtf": {"status": "aligned"}}
e = {"plan": {"entry": 100, "stop": 98, "tps": [104]}}
q_al, w_al = T.quality(r, e); r["mtf"]["status"] = "conflict"; q_co, w_co = T.quality(r, e)
assert q_al - q_co == 20 and any("متوافقة" in w for w in w_al) and any("ضد" in w for w in w_co)
r["trade_type"] = "Day Trade"; assert T.quality(r, e)[0] == T.quality({**r, "mtf": {"status": "aligned"}}, e)[0]
print("mtf tests OK")
