"""Run: python tests/test_sig_filters.py   (plain asserts, no pytest needed)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from modules import sig_filters as F


def frame(n=160, seed=0, vol=100.0):
    r = np.random.default_rng(seed)
    c = 100 + np.cumsum(r.normal(0, .3, n)); o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + r.random(n) * .2; l = np.minimum(o, c) - r.random(n) * .2
    return pd.DataFrame({"time": pd.date_range("2025-01-01", periods=n, freq="h"), "open": o, "high": h, "low": l, "close": c,
                         "volume": np.full(n, vol) + r.random(n)})


def with_break(strong=True):
    """range, swing high at bar 120, then a break candle at bar 130: big body (strong) or a weak poke over the level."""
    df = frame(); n = len(df)
    for i in range(100, 121):                       # a hill whose top is a clean fractal swing high
        p = 100 + (10 - abs(i - 120) * .5) if i <= 120 else 100
        df.loc[i, ["open", "high", "low", "close"]] = [p - .1, p + .15, p - .2, p]
    for i in range(121, 130):                       # pullback / range under the swing
        df.loc[i, ["open", "high", "low", "close"]] = [104, 104.3 + i * .001, 103.6 - i * .001, 104.1]
    lvl = df.loc[120, "high"]
    if strong:
        df.loc[130, ["open", "high", "low", "close"]] = [104.1, lvl + 3.2, 104.0, lvl + 3.0]   # displacement close well above
    else:
        df.loc[130, ["open", "high", "low", "close"]] = [lvl - .05, lvl + .03, lvl - .1, lvl + .01]   # barely above
    for i in range(131, n):
        df.loc[i, ["open", "high", "low", "close"]] = [lvl + 2.9, lvl + 3.3, lvl + 2.6, lvl + 3.0]
    return df, lvl


def test_strict_breaks():
    df, lvl = with_break(True)
    b = F.strict_breaks(df)
    assert any(abs(x["level"] - lvl) < 1e-9 for x in b), b
    df2, _ = with_break(False)
    assert not F.strict_breaks(df2), "a barely-over close must not count"


def test_ob_volume():
    df = frame(vol=100.0)
    k = 90
    df.loc[k:k + 2, "volume"] = 400.0
    r = F.ob_volume_ratio(df, k)
    assert r is not None and r > 3, r
    df.loc[k:k + 2, "volume"] = 40.0
    assert F.ob_volume_ratio(df, k) < 0.7


def test_apply_ob_volume_and_strict():
    df, lvl = with_break(True)
    k = 125
    zone = (float(df.loc[k, "low"]), float(df.loc[k, "high"]))
    mk = lambda: [{"key": "ob", "zone": zone, "_v": {}}]
    os.environ.update({"SIGF_STRICT_SMC": "1", "SIGF_OB_VOL": "1", "SIGF_BO_VOL": "1"})
    df.loc[k:k + 2, "volume"] = 500.0
    assert len(F.apply(df, mk())) == 1                                 # strong break + heavy volume -> kept
    df.loc[k:k + 2, "volume"] = 30.0
    assert len(F.apply(df, mk())) == 0                                 # light volume -> dropped
    os.environ["SIGF_OB_VOL"] = "0"
    assert len(F.apply(df, mk())) == 1                                 # volume filter off -> kept
    df_w, _ = with_break(False)
    assert len(F.apply(df_w, [{"key": "ob", "zone": zone, "_v": {}}])) == 0   # weak break -> dropped by strict SMC
    os.environ["SIGF_STRICT_SMC"] = "0"
    assert len(F.apply(df_w, [{"key": "ob", "zone": zone, "_v": {}}])) == 1


def test_breakout_volume_delta():
    os.environ.update({"SIGF_STRICT_SMC": "1", "SIGF_OB_VOL": "1", "SIGF_BO_VOL": "1"})
    df = frame(vol=100.0); n = len(df)
    df.loc[n - 1, ["open", "high", "low", "close", "volume"]] = [100, 103, 99.9, 102.9, 400]     # big green bar closing near the high
    s = [{"key": "breakout", "zone": None, "_v": {}}]
    out = F.apply(df, s)
    assert len(out) == 1 and out[0]["_v"]["bovol"] >= 3, out
    df.loc[n - 1, ["open", "close", "volume"]] = [102.9, 100.0, 400]                              # same volume but sold off (closes at the low)
    assert len(F.apply(df, [{"key": "breakout", "zone": None, "_v": {}}])) == 0
    df.loc[n - 1, ["open", "close", "volume"]] = [100, 102.9, 90]                                  # buying but no volume
    assert len(F.apply(df, [{"key": "breakout", "zone": None, "_v": {}}])) == 0


def test_no_volume_market_untouched():
    df = frame(); df["volume"] = 0.0
    assert not F.has_volume(df)
    os.environ.update({"SIGF_STRICT_SMC": "0", "SIGF_OB_VOL": "1", "SIGF_BO_VOL": "1"})
    s = [{"key": "breakout", "zone": None, "_v": {}}, {"key": "ob", "zone": (1, 2), "_v": {}}]
    assert len(F.apply(df, s)) == 2                                    # forex / indices: volume filters switch off


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
