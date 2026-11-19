"""Gann angle levels with a fixed unit (synthetic numbers, no market data)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import math
from modules import gann_geom as g

assert g.angle_price(100, 10, "1x1", 1.0, up=True) == 110          # 1 unit per bar
assert g.angle_price(100, 10, "1x2", 1.0, up=True) == 105          # half a unit per bar
assert g.angle_price(100, 10, "2x1", 1.0, up=False) == 80          # two units per bar, down
assert abs(g.offset_angle_price(100, 10, 45, 1.0) - 110) < 1e-9   # 45 deg with unit 1 = 1x1
assert abs(g.offset_angle_price(100, 10, 63.4349, 1.0) - (100 + 10 * 2)) < 1e-3   # ~2x1 angle
try:
    g.angle_price(100, 10, "3x1", 1.0); raise SystemExit("unknown ratio accepted")
except ValueError:
    pass
try:
    g.offset_angle_price(100, 10, 90, 1.0); raise SystemExit("90 deg accepted")
except ValueError:
    pass
levels = g.square_of_nine_levels(100, 2)
assert len(levels) >= 2 and all(isinstance(x, float) for x in levels), levels
# offset from a prior axis (our definition): offset 0 = the axis itself
axis = 2.0                                   # axis rises 2 price units per bar, unit 1 -> axis angle atan(2) ~ 63.4 deg
assert abs(g.offset_from_axis_price(100, 10, axis, 0, 1.0) - (100 + 2.0 * 10)) < 1e-9
# 45 deg offset from a 45-deg axis (1x1, unit 1) -> 90 deg, not allowed (must stay under 90)
try:
    g.offset_from_axis_price(100, 10, 1.0, 45, 1.0); raise SystemExit("90 deg offset accepted")
except ValueError:
    pass
# 15 deg offset from a 45-deg axis -> 60 deg line
got = g.offset_from_axis_price(100, 10, 1.0, 15, 1.0)
assert abs(got - (100 + math.tan(math.radians(60)) * 10)) < 1e-9, got
print("test_gann_geom: OK")
