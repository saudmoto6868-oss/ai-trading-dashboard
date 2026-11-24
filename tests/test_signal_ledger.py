"""Signal ledger (modules/signal_ledger.py): replay + lessons + stats + advice on hand-made candles. Mock data only.
Run: python3 tests/test_signal_ledger.py"""
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import signal_ledger as L  # noqa: E402

H = 3_600_000
T0 = 1_700_000_000_000 // H * H
NOW = T0 + 1000 * H


def bars(rows, pad=200, px=None):
    """rows = [(o, h, l, c)] from T0; then `pad` flat candles at px (default: last close)."""
    out = [(T0 + i * H, *r) for i, r in enumerate(rows)]
    p = px if px is not None else rows[-1][3]
    out += [(T0 + (len(rows) + i) * H, p, p, p, p) for i in range(pad)]
    return out


def sig(d="long", entry=100.0, sl=98.0, tps=(102.0, 104.0, 106.0), **kw):
    s = L.normalize(dict(src="test", symbol="X-USDT", tf="1h", dir=d, entry=entry, sl=sl, tps=list(tps), t0=T0, **kw))
    assert s, "normalize"
    return s


def codes(rv):
    return [x["code"] for x in rv["lessons"]]


# 1) straight run to TP3; R = 2 per unit; split = mean(1, 2, 3)
r = L.review(sig(), bars([(100.5, 100.6, 99.9, 100.2), (100.2, 102.1, 100.1, 102), (102, 104.2, 101.8, 104), (104, 106.5, 103.9, 106)], px=106), now_ms=NOW)
assert r["outcome"] == "tp3" and r["r"]["split"] == 2.0 and r["r"]["tp1_all"] == 1.0 and r["r"]["last_all"] == 3.0, r
assert "tp1_fast" in codes(r) and r["mfe_r"] >= 3, r

# 2) stop hunt: stop hit (low 97.5 = 1.25R against), then price goes to TP1 -> needs a ~1.3R stop
r = L.review(sig(), bars([(100.5, 100.6, 99.9, 100), (100, 100.2, 97.5, 98.5), (98.5, 102.5, 98.4, 102.2)], px=102), now_ms=NOW)
assert r["outcome"] == "sl" and r["r"]["split"] == -1.0, r
st = [x for x in r["lessons"] if x["code"] == "stop_hunt"]
assert st and 1.2 <= st[0]["need_r"] <= 1.4 and r["after_exit"]["to_tp1"], r

# 3) early entry: fills, dips 0.75R (98.5) without the stop, then TP1 and TP2 + TP3
r = L.review(sig(), bars([(100.5, 100.6, 100, 100.2), (100.2, 100.3, 98.5, 99), (99, 106.2, 98.9, 106)], px=106), now_ms=NOW)
assert r["outcome"] == "tp3" and "early_entry" in codes(r), r
assert r["best"]["entry"] == 98.5 and r["best"]["move_r"] >= 3.8, r

# 4) late entry: breakout long at 100 after price sat at 99 (0.5R better) before the fill
r = L.review(sig(), bars([(99.2, 99.5, 99, 99.3), (99.3, 99.6, 99, 99.5), (99.5, 100.5, 99.4, 100.4), (100.4, 102.3, 100.3, 102.2)], px=102.2), now_ms=NOW)
late = [x for x in r["lessons"] if x["code"] == "late_entry"]
assert late and late[0]["better_r"] == 0.5 and r["bars_to_fill"] == 2, r

# 5) never filled / ran away
r = L.review(sig(entry=99.0, sl=97.0, tps=(101, 103)), bars([(100, 101.5, 99.5, 101.2)], px=101), now_ms=NOW)
assert r["outcome"] == "ran_away" and not r["filled"] and codes(r) == ["ran_away"], r
r = L.review(sig(entry=99.0, sl=97.0, tps=(101, 103)), bars([(100, 100.5, 99.5, 100)], px=100), now_ms=NOW)
assert r["outcome"] == "no_fill", r

# 6) TP1, peak 1.6R (TP2 needs 2R), back to the break-even stop -> missed TP2 with 80 %
r = L.review(sig(), bars([(100.5, 100.6, 100, 100.2), (100.2, 103.2, 100.1, 103), (103, 103.1, 99.9, 100.1)], px=100), now_ms=NOW)
m = [x for x in r["lessons"] if x["code"] == "missed_tp"]
assert r["outcome"] == "tp1" and m and m[0]["level"] == "tp2" and m[0]["pct"] == 80 and m[0]["then"] == "be_stop", r
assert abs(r["r"]["split"] - 1 / 3) < 1e-3 and r["r"]["tp1_all"] == 1.0 and r["r"]["last_all"] == 0.0, r
assert "80%" in L.lesson_text(m[0]) and "80%" in L.lesson_text(m[0], ar=True)

# 7) one candle touches the stop and TP1: the stop counts
r = L.review(sig(), bars([(100.5, 100.6, 100, 100.2), (100.2, 102.5, 97.9, 100)], px=100), now_ms=NOW)
assert r["outcome"] == "sl", r

# 8) short side mirror of 1)
r = L.review(sig("short", 100, 102, (98, 96, 94)), bars([(99.5, 100.1, 99.4, 99.8), (99.8, 99.9, 97.9, 98), (98, 98.2, 95.8, 96), (96, 96.1, 93.5, 94)], px=94), now_ms=NOW)
assert r["outcome"] == "tp3" and r["r"]["split"] == 2.0, r

# 9) pending: inside the fill window / the look-after window is not complete
assert L.review(sig(entry=99.0, sl=97.0, tps=(101,)), [(T0, 100, 100.5, 99.5, 100)], now_ms=T0 + 2 * H) is None
assert L.review(sig(), [(T0, 100.5, 100.6, 100, 100.2), (T0 + H, 100.2, 106.5, 100.1, 106)], now_ms=T0 + 3 * H) is None

# 10) grid: the same trade with a 1.5x stop survives the hunt of 2)
r = L.review(sig(), bars([(100.5, 100.6, 99.9, 100), (100, 100.2, 97.5, 98.5), (98.5, 102.5, 98.4, 102.2)], px=102), now_ms=NOW)
assert r["grid"]["1|1"] == -1.0 and r["grid"]["1.5|1"] > 0, r["grid"]

# 11) normalize: wrong-side stop rejected; the same plan on the same candle is one signal
assert L.normalize(dict(src="t", symbol="X", tf="1h", dir="long", entry=100, sl=101, tps=[102], t0=T0)) is None
assert L.normalize(dict(src="t", symbol="X", tf="1h", dir="long", entry=100, sl=99, tps=[98], t0=T0)) is None
a = L.normalize(dict(src="t", symbol="X", tf="1h", dir="bullish", entry=100, stop=99, tp1=101, t0=T0 + 5))
b = L.normalize(dict(src="t", symbol="X", tf="1h", dir="long", entry=100, sl=99, tps=[101], t0=T0 + 1000))
assert a and b and a["id"] == b["id"]

# 11b) the same plan re-sent on the next candles is one signal; a new plan (other entry) is a new one; after the fill window it may come back
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "s.json"
    base = dict(src="scan", symbol="X", tf="1h", dir="long", entry=100, sl=99, tps=[102])
    for k in range(5):
        L.record(dict(base, t0=T0 + k * H), p)
    L.record(dict(base, entry=100.5, t0=T0 + 2 * H), p)
    L.record(dict(base, t0=T0 + (L.FILL_BARS + 1) * H), p)
    assert len(L.all_signals(p)) == 3, [s_["t0"] for s_ in L.all_signals(p)]
    a1 = L.normalize(dict(base, tf="1M", t0=T0))
    assert a1["tf"] == "1mo" and L.tf_ms("1mo") > L.tf_ms("1w")

# 12) store + grade_pending (fake fetch) + stats + advice
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "s.json"
    rows = {"hunt": [(100.5, 100.6, 99.9, 100), (100, 100.2, 97.5, 98.5), (98.5, 102.5, 98.4, 102.2)],
            "run": [(100.5, 100.6, 99.9, 100.2), (100.2, 102.1, 100.1, 102), (102, 104.2, 101.8, 104), (104, 106.5, 103.9, 106)]}
    for i in range(12):   # 12 different symbols, 6 stop hunts + 6 runs
        kind = "hunt" if i % 2 else "run"
        L.record(dict(src="hunter" if kind == "hunt" else "runner", sub="k", symbol="S%d" % i, tf="1h", dir="long", entry=100, sl=98, tps=[102, 104, 106], t0=T0), p)
    assert L.record(dict(src="runner", sub="k", symbol="S0", tf="1h", dir="long", entry=100, sl=98, tps=[102, 104, 106], t0=T0 + 10), p)   # duplicate
    assert len(L.all_signals(p)) == 12

    def fetch(sym, tf, n):
        k = "hunt" if int(sym[1:]) % 2 else "run"
        b = bars(rows[k], px=rows[k][-1][3])
        return pd.DataFrame({"time": pd.to_datetime([x[0] for x in b], unit="ms"), "open": [x[1] for x in b], "high": [x[2] for x in b],
                             "low": [x[3] for x in b], "close": [x[4] for x in b]})

    assert L.grade_pending(fetch, p, now_ms=NOW) == 12
    assert L.grade_pending(fetch, p, now_ms=NOW) == 0   # nothing left
    S = L.stats(p)
    assert S["runner"]["n"] == 6 and S["runner"]["level"] == "collecting" and S["runner"]["split"]["avg_r"] == round(2 - L.COST_R, 3), S["runner"]
    assert S["hunter"]["lessons"]["stop_hunt"] == 100.0, S["hunter"]
    adv = L.advice(S["hunter"])
    assert any("Stops too tight" in a for a in adv) and adv[0].startswith("[n=6 · watch only]"), adv
    assert any("الستوب ضيق" in a for a in L.advice(S["hunter"], ar=True))
    assert L.ranking(p)[0][0] in ("runner", "hunter")
    assert "test" not in S and set(L.stats(p, "src_sub")) == {"runner · k", "hunter · k"}
    bl = L.brain_lines(p)
    assert len(bl) == 2 and bl[0].startswith("ledger ") and "n=6" in bl[0], bl

# 13) candles that do not reach back to the signal -> "lost", not a guess
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "s.json"
    L.record(dict(src="t", symbol="Z", tf="1h", dir="long", entry=100, sl=98, tps=[102], t0=T0), p)
    late_df = pd.DataFrame({"time": pd.to_datetime([T0 + 50 * H], unit="ms"), "open": [1.0], "high": [1.0], "low": [1.0], "close": [1.0]})
    L.grade_pending(lambda *a: late_df, p, now_ms=NOW)
    assert L.all_signals(p)[0]["status"] == "lost"

# 14) the brain's setup detectors -> one strategy per detector key, t0 after the last candle, bias -> ctx.htf
from modules import day_plan  # noqa: E402
_orig = day_plan.scan_setups
day_plan.scan_setups = lambda syms, fetch: [
    {"symbol": "BTC-USDT", "key": "cisd", "tf": "1h", "direction": "bullish", "names": ["CISD"], "schools": ["ICT"], "entry": 100, "stop": 98, "tps": [102, 104], "with_bias": True},
    {"symbol": "BTC-USDT", "key": "crt", "tf": "1h", "direction": "bearish", "names": ["CRT"], "schools": [], "entry": 100, "stop": 102, "tps": [97], "with_bias": False}]
try:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.json"
        one = pd.DataFrame({"time": pd.to_datetime([T0, T0 + H], unit="ms"), "open": [1.0, 1.0], "high": [1.0, 1.0], "low": [1.0, 1.0], "close": [1.0, 1.0]})
        assert L.record_setups(["BTC-USDT"], lambda s_, t_: one, p) == 2
        S = {x["src"]: x for x in L.all_signals(p)}
        assert set(S) == {"setup:cisd", "setup:crt"} and S["setup:cisd"]["t0"] == T0 + 2 * H, S
        assert S["setup:cisd"]["ctx"]["htf"] == "with" and S["setup:crt"]["ctx"]["htf"] == "against" and S["setup:cisd"]["why"] == ["ICT"]
finally:
    day_plan.scan_setups = _orig

print("ok signal_ledger")
