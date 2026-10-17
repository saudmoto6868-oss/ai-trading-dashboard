"""Item 20: Finviz-style chart patterns on hand-drawn price paths. Run: python tests/test_patterns.py"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import chart_scan, patterns as P  # noqa: E402


def path(points, n):
    """Piecewise-linear closes through (bar, price) points, candles with a small fixed range."""
    xs, ys = zip(*points)
    c = np.interp(np.arange(n), xs, ys)
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": o,
                         "high": np.maximum(o, c) + 0.3, "low": np.minimum(o, c) - 0.3, "close": c, "volume": 100.0})


def zig(upper, lower, n=140, half=8, end_frac=0.5):
    """Swing between two lines (functions of the bar index), a top every 2*half bars; ends end_frac of the way up."""
    pts, i, top = [(0, (upper(0) + lower(0)) / 2)], half, True
    while i < n - 1:
        pts.append((i, upper(i) if top else lower(i))); top = not top; i += half
    last = n - 1
    pts.append((last, lower(last) + (upper(last) - lower(last)) * end_frac))
    return path(pts, n)


def found(df):
    return set(P.find(df))


cases = {
    "cp_channel_up": zig(lambda i: 120 + 0.5 * i, lambda i: 100 + 0.5 * i),
    "cp_channel_dn": zig(lambda i: 220 - 0.5 * i, lambda i: 200 - 0.5 * i),
    "cp_channel_h": zig(lambda i: 120.0, lambda i: 100.0),
    "cp_wedge_up": zig(lambda i: 140 + 0.4 * i, lambda i: 100 + 0.65 * i),
    "cp_wedge_dn": zig(lambda i: 240 - 0.65 * i, lambda i: 200 - 0.4 * i),
    "cp_tri_asc": zig(lambda i: 140.0, lambda i: 100 + 0.25 * i),
    "cp_tri_desc": zig(lambda i: 140 - 0.25 * i, lambda i: 100.0),
    "cp_tri_sym": zig(lambda i: 160 - 0.2 * i, lambda i: 100 + 0.2 * i),
}
for pid, df in cases.items():
    f = found(df)
    assert pid in f, (pid, f)
    others = f & {"cp_channel_up", "cp_channel_dn", "cp_channel_h", "cp_wedge_up", "cp_wedge_dn", "cp_tri_asc", "cp_tri_desc", "cp_tri_sym"}
    assert others == {pid}, (pid, others)   # exactly one shape class per chart
    lines = P.find(df)[pid]
    assert len(lines) == 2 and all(len(x) == 4 for x in lines)

# trendline support: up-channel that ends ON the lower line
f = found(zig(lambda i: 120 + 0.5 * i, lambda i: 100 + 0.5 * i, end_frac=0.03))
assert "cp_tl_support" in f and "cp_tl_resist" not in f, f
f = found(zig(lambda i: 120 + 0.5 * i, lambda i: 100 + 0.5 * i, end_frac=0.97))
assert "cp_tl_resist" in f and "cp_tl_support" not in f, f

# a broken line is not a pattern any more (the screener's breakout flags cover that)
df = zig(lambda i: 120.0, lambda i: 100.0)
brk = pd.concat([df, path([(0, 112), (5, 135)], 6).assign(time=pd.date_range(df.time.iloc[-1], periods=7, freq="1h")[1:])], ignore_index=True)
assert "cp_channel_h" not in found(brk)

# multiple top: three equal highs, price back below them
mt = path([(0, 100), (10, 130), (22, 112), (34, 130), (46, 108), (58, 130), (70, 110), (80, 116)], 81)
mt = pd.concat([path([(0, 105), (40, 100)], 40), mt.assign(close=mt.close)], ignore_index=True)
mt["time"] = pd.date_range("2026-01-01", periods=len(mt), freq="1h")
assert "cp_multi_top" in found(mt), found(mt)
mb = mt.copy()
for k in ("open", "close"):
    mb[k] = 300 - mt[k]
mb["high"], mb["low"] = 300 - mt["low"], 300 - mt["high"]
assert "cp_multi_bottom" in found(mb), found(mb)

# head & shoulders: left shoulder, head, right shoulder over a flat neckline, price just under the right shoulder
hs = path([(0, 95), (20, 100), (35, 120), (50, 100), (65, 135), (80, 100), (95, 120), (108, 104), (112, 106)], 113)
assert "cp_hs" in found(hs) and "cp_ihs" not in found(hs), found(hs)
ihs = hs.copy()
for k in ("open", "close"):
    ihs[k] = 250 - hs[k]
ihs["high"], ihs["low"] = 250 - hs["low"], 250 - hs["high"]
assert "cp_ihs" in found(ihs) and "cp_hs" not in found(ihs), found(ihs)

# random walk: patterns are allowed but the call must never fail; screener integration carries flags + lines
rng = np.random.default_rng(3)
for s in range(20):
    rw = path([(i, v) for i, v in enumerate(100 + np.cumsum(rng.standard_normal(200)))], 200)
    P.find(rw)
feat = chart_scan.features(cases["cp_wedge_dn"])
assert "cp_wedge_dn" in feat["flags"] and feat["lines"], feat
assert chart_scan.flag_side("cp_wedge_dn") == "buy" and chart_scan.flag_side("cp_hs") == "sell" and chart_scan.flag_side("cp_tri_sym") is None
svg = chart_scan.mini_chart_svg(cases["cp_wedge_dn"], lines=feat["lines"])
import base64  # noqa: E402
assert svg.startswith("data:image/svg+xml;base64,") and "#ffd54f" in base64.b64decode(svg.split(",", 1)[1]).decode()
assert "cp_hs" in chart_scan.PATTERN_FILTERS and chart_scan.SHORT["cp_tri_asc"] == "Tri asc"
print("test_patterns: all passed")
