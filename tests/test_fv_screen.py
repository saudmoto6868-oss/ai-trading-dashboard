"""modules/fv_screen.py: Finviz-style metrics, the drop-down filters, candlestick set and 'find similar charts' on synthetic candles."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import fv_screen as F  # noqa: E402


def _frame(closes, vol=100.0, spread=0.01):
    c = np.asarray(closes, float)
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) * (1 + spread), "low": np.minimum(o, c) * (1 - spread), "close": c, "volume": vol})


def test_metrics_and_filters():
    c = np.concatenate([np.linspace(100, 200, 270)])            # a steady uptrend to 200
    m = F.metrics(_frame(c))
    assert m["price"] == 200 and m["n"] == 270 and m["perf_Week"] > 0 and m["perf_Year"] > 40
    assert m["sma20_rel"] > 0 and m["sma200_rel"] > 0 and m["newhi_52w"] and m["from_hi_52w"] > -2
    assert F.test("sma20", "above", m) and not F.test("sma20", "below", m)
    assert F.test("sma20", "sma50a", m) and F.test("sma50", "sma200a", m)                      # SMA20 > SMA50 > SMA200 in an uptrend
    assert F.test("perf", "Quarter|+10", m) and not F.test("perf", "Quarter|-5", m) and F.test("perf", "Week|up", m)
    assert F.test("hl52", "newhi", m) and F.test("hl52", "hi0_3", m) and not F.test("hl52", "hi20", m)
    assert F.test("rsi", "ob70", m) and not F.test("rsi", "os30", m) and F.test("rsi", "nos", m)
    assert F.test("chg", "up", m) and F.test("gap", "dn1", m) is False
    assert F.test("atr", "u3", m) and not F.test("atr", "o3", m)
    assert F.apply({"sma20": "above", "rsi": "ob70", "chg": ""}, {"A": m, "B": None}) == ["A"]   # '' = Any; a symbol with no metrics never passes
    assert F.metrics(_frame(c[:20])) is None


def test_cross_and_relvol():
    c = np.concatenate([np.full(60, 100.0), np.linspace(100, 90, 20), [104.0]])               # long flat, a dip, then a jump above SMA20
    m = F.metrics(_frame(c))
    assert F.test("sma20", "crossup", m) and not F.test("sma20", "crossdn", m)
    df = _frame(c); df.loc[len(df) - 1, "volume"] = 450.0
    assert abs(F.metrics(df)["relvol"] - 4.5) < 0.2 and F.test("relvol", "o3", F.metrics(df)) and not F.test("relvol", "o10", F.metrics(df))


def test_candle_set_and_every_filter_has_a_test():
    rng = np.random.default_rng(0)
    c = 100 + np.cumsum(rng.normal(0, 1, 120))
    df = _frame(c)
    s = F.candle_set(df)
    assert s <= {x[0] for x in F.CANDLES}
    # a doji on the last candle
    d2 = df.copy(); d2.loc[len(d2) - 1, ["open", "close"]] = [100.0, 100.01]; d2.loc[len(d2) - 1, "high"] = 102; d2.loc[len(d2) - 1, "low"] = 98
    assert "doji" in F.candle_set(d2)
    m = F.metrics(_frame(np.linspace(100, 200, 300)))
    for key, _g, _e, _a, opts in F.FILTERS:
        for code, _el, _al in opts:
            F.test(key, code, m, {"flags": {"x"}, "candles": set()})                          # no option may raise


def test_similar_finds_the_scaled_copy_and_not_itself():
    rng = np.random.default_rng(1)
    base = 100 + np.cumsum(rng.normal(0, 1, 200))
    frames = {"A": _frame(base), "B": _frame(base * 3 + 50), "C": _frame(100 + np.cumsum(rng.normal(0, 1, 200))), "D": _frame(250 - base)}
    r = F.similar(frames, "A", window=40)
    assert r[0]["symbol"] == "B" and r[0]["corr"] > 0.999 and r[0]["offset"] == 0
    assert [x["symbol"] for x in r].count("A") <= 1
    a = [x for x in r if x["symbol"] == "A"]
    assert not a or a[0]["offset"] >= 40                                                       # the target's own present is excluded
    d = [x for x in r if x["symbol"] == "D"][0]
    assert d["corr_now"] < -0.99 and r[0]["corr_now"] > 0.999                                   # the mirror image is the opposite shape NOW; the copy matches NOW
    assert d["corr"] > d["corr_now"]                                                            # best-of-many windows is always >= the present window (that inflation is why corr_now is shown)
    assert F.similar({"A": _frame(base[:20])}, "A") == [] and F.similar(frames, "ZZ") == []


if __name__ == "__main__":
    test_metrics_and_filters(); test_cross_and_relvol(); test_candle_set_and_every_filter_has_a_test(); test_similar_finds_the_scaled_copy_and_not_itself(); print("ok fv_screen")
