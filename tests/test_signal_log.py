"""Outcome rules of the server-side signal log on hand-made candles (no network)."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from modules import signal_log as L

T0 = 1_760_000_000          # signal time (unix s)
def candles(rows):          # rows = [(high, low)] one per hour AFTER the signal
    return pd.DataFrame({"time": [pd.Timestamp(T0 + 3600 * (i + 1), unit="s") for i in range(len(rows))], "high": [r[0] for r in rows], "low": [r[1] for r in rows]})
def rec(d="bullish", entry=100, stop=98, tp=104, px0=100):
    return {"t": T0, "key": "k", "symbol": "BTC-USDT", "dir": d, "tf": "1h", "score": 4, "max": 7, "q": 72, "entry": entry, "stop": stop, "tp1": tp, "px0": px0, "sent": True}

assert L.check(rec(), candles([(101, 99.5), (105, 100)])) == {"out": "tp", "r": 2.0}
assert L.check(rec(), candles([(101, 99.5), (101, 97.9)])) == {"out": "sl", "r": -1.0}
assert L.check(rec(), candles([(105, 97)]))["out"] == "sl"                # both in one candle -> loss (pessimistic)
assert L.check(rec(), candles([(100.5, 99.5)])) is None                  # still open
assert L.check(rec(), candles([(100.5, 99.5)] * 48))["out"] == "exp"
# short
assert L.check(rec("bearish", 100, 102, 96), candles([(100.5, 99), (99, 95.5)])) == {"out": "tp", "r": 2.0}
# limit entry far from price: not filled until touched
assert L.check(rec(entry=95, stop=93, tp=99, px0=100), candles([(101, 99), (100, 98)])) is None
assert L.check(rec(entry=95, stop=93, tp=99, px0=100), candles([(101, 99)] * 48))["out"] == "nofill"
assert L.check(rec(entry=95, stop=93, tp=99, px0=100), candles([(101, 99), (97, 94.9), (99.5, 96)])) == {"out": "tp", "r": 2.0}
# candles before the signal are ignored
old = pd.DataFrame({"time": [pd.Timestamp(T0 - 3600, unit="s")], "high": [200], "low": [1]})
assert L.check(rec(), old) is None
# bad plan
assert L.check(rec(stop=100), candles([(101, 99)]))["out"] == "bad"

# log + dedupe + resolve + stats + csv
recs = []
al = {"symbol": "BTC-USDT", "direction": "bullish", "tfk": "1h", "score": 4, "max": 7, "q": 72, "plan": {"entry": 100, "stop": 98, "tps": [104]}}
assert L.log_alerts([al], recs, {"BTC-USDT|bullish|1h"}, now=T0, px={"BTC-USDT": 100}) == 1
assert L.log_alerts([al], recs, set(), now=T0 + 600) == 0                  # same setup within 4 h
assert L.log_alerts([al], recs, set(), now=T0 + 5 * 3600) == 1
assert L.log_alerts([{**al, "plan": {}}], recs, set(), now=T0 + 99999) == 0 # no plan -> not logged
assert L.resolve(recs, lambda s, tf: candles([(105, 99.5)])) == 1 and recs[0]["out"] == "tp"
s = L.stats(recs); assert s["all"]["n"] == 1 and s["all"]["win_pct"] == 100.0 and not s["all"]["enough"] and s["open"] == 1
assert "NOT evidence" in L.format_stats(s)
d = tempfile.mkdtemp(); f = os.path.join(d, "l.jsonl"); L.save(recs, __import__("pathlib").Path(f)); assert len(L.load(__import__("pathlib").Path(f))) == 2
L.to_csv(recs, os.path.join(d, "o.csv")); txt = open(os.path.join(d, "o.csv")).read(); assert txt.splitlines()[0] == "time,symbol,side,tf,r" and ",buy,1h,2.0" in txt
assert L.stats([])["all"]["n"] == 0 and "no statistics" in L.format_stats(L.stats([]))
print("signal_log tests OK")
