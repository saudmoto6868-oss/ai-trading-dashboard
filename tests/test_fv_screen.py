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


def test_extra_candle_only_lists():
    """PR 1 of Radar item C: MACD, Bollinger, Stochastic, ADX, CCI, Williams %R, SAR, distance to EMA 20, price, turnover, OBV, bar patterns."""
    up = F.metrics(_frame(np.linspace(100, 200, 270)))                                           # steady uptrend
    dn = F.metrics(_frame(np.linspace(200, 100, 270)))                                           # steady downtrend
    flat = F.metrics(_frame(100 + ((np.arange(270) % 4) - 1.5) * 0.2))                           # quiet zig-zag range
    hot = F.metrics(_frame(np.linspace(1, 2, 270) ** 3 * 100)); cold = F.metrics(_frame(np.linspace(2, 1, 270) ** 3 * 100))   # accelerating trends: closes pinned at the extreme
    assert F.test("macd", "pos", up) and F.test("macd", "neg", dn) and not F.test("macd", "pos", dn)
    assert F.test("adx", "o25", up) and F.test("adx", "bull", up) and F.test("adx", "bear", dn) and F.test("adx", "u20", flat) and not F.test("adx", "o25", flat)
    assert F.test("sar", "up", up) and F.test("sar", "dn", dn) and not F.test("sar", "flipup", up)
    assert F.test("stoch", "ob", hot) and F.test("stoch", "os", cold) and F.test("willr", "ob", hot) and F.test("willr", "os", cold)
    assert F.test("cci", "o100", up) and F.test("cci", "u100", dn)
    assert F.test("obv", "up", up) and F.test("obv", "dn", dn)
    assert F.test("range", "up5", up) and F.test("range", "dn5", dn) and not F.test("range", "up5", dn)
    assert F.test("dist20", "o5", hot) and F.test("dist20", "u5", cold) and not F.test("dist20", "o5", flat)
    assert F.test("price", "o100", up) and not F.test("price", "u100", up) and F.test("price", "u1", F.metrics(_frame(np.linspace(0.5, 0.9, 60))))
    assert F.test("turnover", "o10M", F.metrics(_frame(np.linspace(100, 200, 270), vol=1e6))) and F.test("turnover", "u100K", F.metrics(_frame(np.linspace(100, 200, 270), vol=1.0)))
    # a squeeze after a wide stretch, a spike above the band, a MACD cross, NR7 / inside bar
    wide = np.concatenate([100 + np.sin(np.linspace(0, 30, 200)) * 8, 100 + np.sin(np.linspace(0, 30, 70)) * 0.3])
    assert F.test("bb", "squeeze", F.metrics(_frame(wide))) and not F.test("bb", "wide", F.metrics(_frame(wide)))
    spike = np.concatenate([np.full(100, 100.0) + np.sin(np.arange(100)) * 0.1, [112.0]])
    assert F.test("bb", "above", F.metrics(_frame(spike))) and not F.test("bb", "inside", F.metrics(_frame(spike)))
    v = np.concatenate([np.linspace(100, 80, 60), np.linspace(80, 95, 12)]); xs = [F.metrics(_frame(v[:k])) for k in range(40, len(v) + 1)]
    assert any(F.test("macd", "xup", x) for x in xs), "a V-shaped recovery must cross the MACD up somewhere"
    # missing history never raises and never matches
    short = F.metrics(_frame(np.linspace(100, 110, 32)))
    for key, opts in [(f[0], f[4]) for f in F.FILTERS if f[0] in ("macd", "bb", "stoch", "adx", "cci", "willr", "sar", "dist20", "price", "turnover", "obv", "range")]:
        for code, _e, _a in opts:
            F.test(key, code, short)
            F.test(key, code, {"price": 1.0})                                                      # an almost empty metrics dict
    print("ok extra lists")


def test_ichimoku_beta_and_correlation():
    up = F.metrics(_frame(np.linspace(100, 200, 270))); dn = F.metrics(_frame(np.linspace(200, 100, 270)))
    assert F.test("ichi", "above", up) and F.test("ichi", "green", up) and not F.test("ichi", "below", up)
    assert F.test("ichi", "below", dn) and F.test("ichi", "red", dn) and not F.test("ichi", "above", dn)
    rng = np.random.default_rng(7); r = rng.normal(0, 0.01, 200); ref = _frame(100 * np.exp(np.cumsum(r)))
    twice = _frame(100 * np.exp(np.cumsum(2 * r))); inv = _frame(100 * np.exp(np.cumsum(-r))); other = _frame(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 200))))
    a = F.relation(twice, ref); b = F.relation(inv, ref); c = F.relation(other, ref)
    assert abs(a["beta"] - 2) < 0.05 and a["corr"] > 0.99 and b["beta"] < -0.95 and b["corr"] < -0.99 and abs(c["corr"]) < 0.45, (a, b, c)
    assert F.relation(twice.head(10), ref) == {} and F.relation(_frame(np.full(100, 5.0)), ref) == {}                    # too short / flat: nothing, no error
    m = dict(up); m.update(a)
    assert F.test("beta", "o1", m) and F.test("beta", "o2", {"beta": 2.4}) and F.test("beta", "neg", dict(up, **b)) and F.test("corr", "o08", m) and F.test("corr", "n05", dict(up, **b))
    assert not F.test("beta", "o1", up) and not F.test("corr", "o08", up)                                                # no reference in the universe: never matches
    print("ok ichimoku beta corr")


if __name__ == "__main__":
    test_metrics_and_filters(); test_cross_and_relvol(); test_candle_set_and_every_filter_has_a_test(); test_similar_finds_the_scaled_copy_and_not_itself(); test_extra_candle_only_lists(); test_ichimoku_beta_and_correlation(); print("ok fv_screen")
