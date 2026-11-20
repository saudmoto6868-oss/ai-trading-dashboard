"""Gann geometry with a fixed price-per-bar unit (labels and levels only; no signals, no network).

The unit decides everything: one price unit per bar (1x1) only means something once the scale is fixed. Here the
scale is passed in (the Workspace uses ATR per bar). Without a stated scale the angles are arbitrary.

  angle_price(p0, bars, ratio, unit, up)      price of a Gann angle `ratio` (1x1 = 1 unit per bar; 1x2 = 0.5; 2x1 = 2)
  offset_angle_price(p0, bars, deg, unit, up) price on a line `deg` from horizontal (45 deg = 1x1 when unit is 1 per bar)
  offset_from_axis_price(p0, bars, axis_slope, offset_deg, unit, up=True)
                                              line that starts at p0 and is turned `offset_deg` away from a prior
                                              decline axis (our definition, see below)
  square_of_nine_levels(pivot, steps)         re-exported from modules/spot_ind.sq9 (already in the code)

Offset from a prior axis (OUR definition; no published Gann rule was found in the 2026-11-17 search):
  the axis is the price change per bar of the prior decline (axis_slope, price units per bar). Measured in the
  same scaled space as the angles (unit = price per bar for a 45-degree 1x1), its angle is atan(axis_slope / unit).
  The offset line sits offset_deg further from horizontal, so its slope is tan(atan(axis_slope/unit) + offset_deg) * unit.
  offset_deg = 0 returns the axis itself; 45 turns the axis by 45 degrees. Only the chart's own scale makes these comparable.

Not implemented, on purpose: Square of Twelve and Square of 144 tables (the numbers in the reference images have no
published rule that can be tested here) and circles around a pivot. They stay reference only (docs/academy/reference).
"""
import math

RATIOS = {"1x1": 1.0, "1x2": 0.5, "2x1": 2.0}


def angle_price(p0, bars, ratio, unit, up=True):
    """Price `bars` bars after p0 on the Gann angle with `ratio` (price units per bar = ratio * unit)."""
    if ratio not in RATIOS:
        raise ValueError("unknown ratio %r" % ratio)
    step = RATIOS[ratio] * unit * bars
    return p0 + step if up else p0 - step


def offset_angle_price(p0, bars, deg, unit, up=True):
    """Price on a line at `deg` degrees from horizontal, `bars` bars after p0, with `unit` price per bar."""
    if not 0 < deg < 90:
        raise ValueError("deg must be between 0 and 90")
    step = math.tan(math.radians(deg)) * unit * bars
    return p0 + step if up else p0 - step


def offset_from_axis_price(p0, bars, axis_slope, offset_deg, unit, up=True):
    """Price `bars` bars after p0 on a line turned `offset_deg` from a prior decline axis (see module doc)."""
    base = math.atan2(abs(axis_slope), unit)               # axis angle in scaled space, 0..90 deg
    ang = base + math.radians(offset_deg)
    if not 0 < ang < math.pi / 2:
        raise ValueError("offset puts the line outside 0..90 degrees")
    step = math.tan(ang) * unit * bars
    sign = 1 if (up if axis_slope >= 0 else not up) else -1
    return p0 + sign * step


def square_of_nine_levels(pivot, steps=4):
    from modules.spot_ind import sq9
    return sq9(pivot, steps)


# --- Square of 144 (R18 reference): a 144-bar box over the range of those bars, divided at eighths and thirds ---
SQ144_FRACTIONS = (1/8, 1/4, 1/3, 3/8, 1/2, 5/8, 2/3, 3/4, 7/8, 1.0)


def square_of_144(lows, highs, start=None):
    """lows / highs: bar lows and highs (oldest first). The square starts at `start` (default: the lowest low of the
    last 144 bars) and spans 144 bars. Returns {'start', 'lo', 'hi', 'time': [bar index], 'price': [level]}.
    Time lines at 18, 36, 48, 54, 72, 90, 96, 108, 126, 144 bars (the eighths and thirds of 144); price levels at the
    same fractions of the box's range. Geometry only: no signal, no evidence claim."""
    n = len(lows)
    if n == 0:
        return None
    w0 = max(0, n - 144)
    if start is None:
        seg = list(lows[w0:])
        start = w0 + seg.index(min(seg))
    end = min(n, start + 144)
    lo = min(lows[start:end]) if end > start else lows[start]
    hi = max(highs[start:end]) if end > start else highs[start]
    rng = hi - lo
    return {"start": start, "lo": lo, "hi": hi,
            "time": [start + round(144 * f) for f in SQ144_FRACTIONS],
            "price": [lo + rng * f for f in SQ144_FRACTIONS]}
