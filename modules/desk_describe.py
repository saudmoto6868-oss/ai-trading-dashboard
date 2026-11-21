"""Description only (no lab evidence): what Elliott and harmonic structure the candles show right now.

describe(df) -> {"elliott_shape", "elliott_pivots", "harmonic", "harmonic_forming"}; any part can be None.
Uses the same rules as the chart labels (modules/elliott_shapes.classify_tail, modules/harmonic.find_harmonics).
Labels only: no direction, no entry, no evidence claim. Tests: python3 tests/test_desk_describe.py
"""


def describe(df):
    from modules.elliott_shapes import classify_tail
    from modules.harmonic import zigzag, vol_dev, find_harmonics
    out = {"elliott_shape": None, "elliott_pivots": 0, "harmonic": None, "harmonic_forming": None}
    if df is None or len(df) < 40:
        return out
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    zz = zigzag(h, l, vol_dev(df, 2.5, 0.001, 0.025))
    out["elliott_pivots"] = len(zz)
    out["elliott_shape"] = classify_tail([p for _, p, _ in zz]) if zz else None
    hits = find_harmonics(df, max_age=12)
    if hits:
        out["harmonic"] = hits[0].get("name")
        out["harmonic_forming"] = bool(hits[0].get("forming"))
    return out
