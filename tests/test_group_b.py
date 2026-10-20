"""Run: python tests/test_group_b.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from modules import signals as S


def base(start="2026-10-11 04:00", n=200, seed=1, step="15min", vol=100.0):
    r = np.random.default_rng(seed)
    t = pd.date_range(start, periods=n, freq=step)
    c = 100 + r.normal(0, .12, n).cumsum() * 0.2
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + r.random(n) * .15; l = np.minimum(o, c) - r.random(n) * .15
    return pd.DataFrame({"time": t, "open": o, "high": h, "low": l, "close": c, "volume": vol + r.random(n) * 10})


def base_end(end, n=120, **kw):
    start = pd.Timestamp(end) - pd.Timedelta(minutes=15 * (n - 1))
    return base(start=str(start), n=n, **kw)


def set_bar(df, i, o, h, l, c, v=None):
    df.loc[i, ["open", "high", "low", "close"]] = [o, h, l, c]
    if v is not None:
        df.loc[i, "volume"] = v


def test_kzs():
    df = base_end("2026-10-12 06:45")                          # last candle 06:45 UTC = 02:45 New York (EDT) = London kill zone
    n = len(df); j = n - 2                                      # sweep candle 06:45 UTC
    set_bar(df, n - 18, 103, 105.2, 102.6, 103.2)               # a recent swing high to aim at (within the last 30 bars)
    lvl = df["low"].iloc[j - 20:j].min()
    set_bar(df, j, lvl + .1, lvl + 1.7, lvl - .6, lvl + 1.5, v=300)
    set_bar(df, n - 1, lvl + 1.5, lvl + 1.7, lvl + 1.35, lvl + 1.55, v=110)
    out = S.killzone_sniper_bull(df)
    assert out and out[0]["key"] == "kzs", out
    d2 = df.copy(); d2.loc[j, "volume"] = 100                    # displacement but no volume -> rejected (volume is a condition)
    assert not S.killzone_sniper_bull(d2)
    d3 = df.copy(); d3["time"] = d3["time"] + pd.Timedelta(hours=12)   # same candles outside any kill zone (14:45 New York)
    assert not S.killzone_sniper_bull(d3)
    d4 = df.copy(); d4["volume"] = 0.0                           # market without volume: the volume condition is skipped
    assert S.killzone_sniper_bull(d4)


def test_po3():
    # NY midnight = 04:00 UTC. day 2 starts at 2026-10-12 04:00 UTC.
    df = base(start="2026-10-11 04:00", n=96 * 1 + 20)           # 15-min bars, 29 h: previous day complete + 20 bars of day 2 (until 09:00 UTC)
    d2 = df.index[pd.to_datetime(df["time"]) >= pd.Timestamp("2026-10-12 04:00")][0]
    n = len(df)
    op = 100.0
    set_bar(df, d2, op, op + .1, op - .1, op)
    for k in range(d2 + 1, n):
        set_bar(df, k, op - .05, op + .08, op - .12, op - .02)    # quiet under/around the open
    ml_i = d2 + 9                                                 # 06:15 UTC = 02:15 NY, inside London kill zone
    set_bar(df, ml_i, op - .4, op - .3, op - 1.2, op - 1.0)       # manipulation low = op - 1.2
    set_bar(df, ml_i + 1, op - 1.0, op - .2, op - 1.05, op - .3)
    set_bar(df, n - 3, op - .3, op + .55, op - .35, op + .4)      # displacement reclaim above the open
    set_bar(df, n - 2, op + .4, op + .45, op + .32, op + .38)
    set_bar(df, n - 1, op + .38, op + .42, op + .3, op + .35)
    prev = df.index[pd.to_datetime(df["time"]) < pd.Timestamp("2026-10-12 04:00")]
    df.loc[prev[5], "high"] = 103.0                               # yesterday's high -> objective
    out = S.power_of_three_bull(df)
    assert out and out[0]["key"] == "po3", (out, df.tail(3))
    # no rebound yet -> must not fire
    d2f = df.copy(); set_bar(d2f, n - 3, op - .3, op - .1, op - .35, op - .15); set_bar(d2f, n - 2, op - .15, op - .1, op - .2, op - .15); set_bar(d2f, n - 1, op - .15, op - .1, op - .2, op - .12)
    assert not S.power_of_three_bull(d2f)


def test_bearish_mirror():
    df = base_end("2026-10-12 06:45")
    n = len(df); j = n - 2
    set_bar(df, n - 18, 97, 97.4, 94.8, 96.8)
    hi = df["high"].iloc[j - 20:j].max()
    set_bar(df, j, hi - .1, hi + .6, hi - 1.7, hi - 1.5, v=300)
    set_bar(df, n - 1, hi - 1.5, hi - 1.35, hi - 1.7, hi - 1.55, v=110)
    sigs, errs = S.detect_all(df)
    assert not errs, errs
    assert any(s["key"] == "kzs" and s["direction"] == "bearish" for s in sigs), [(s["key"], s["direction"]) for s in sigs]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
