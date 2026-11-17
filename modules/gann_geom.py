"""Gann geometry with a fixed price-per-bar unit (labels and levels only; no signals, no network).

The unit decides everything: one price unit per bar (1x1) only means something once the scale is fixed. Here the
scale is passed in (the Workspace uses ATR per bar). Without a stated scale the angles are arbitrary.

  angle_price(p0, bars, ratio, unit, up)      price of a Gann angle `ratio` (1x1 = 1 unit per bar; 1x2 = 0.5; 2x1 = 2)
  offset_angle_price(p0, bars, deg, unit, up) price on a line `deg` from horizontal (45 deg = 1x1 when unit is 1 per bar)
  square_of_nine_levels(pivot, steps)         re-exported from modules/spot_ind.sq9 (already in the code)

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


def square_of_nine_levels(pivot, steps=4):
    from modules.spot_ind import sq9
    return sq9(pivot, steps)
