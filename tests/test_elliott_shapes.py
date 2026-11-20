"""Elliott correction shapes and diagonals: labels on synthetic pivots (no network, no market data)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import elliott_shapes as es

# --- ABC shapes (A goes up 100 -> 120) ---
name, info = es.abc_shape(100, 120, 108, 130)          # B back 60 %, C past A's end
assert name == "zigzag", (name, info)

name, info = es.abc_shape(100, 120, 101, 119)          # B back 95 % (near start of A), C ends near A's end
assert name == "regular_flat", (name, info)

name, info = es.abc_shape(100, 120, 95, 125)           # B passes start of A, C passes end of A
assert name == "expanded_flat", (name, info)

name, info = es.abc_shape(100, 120, 95, 118)           # B passes start of A, C stops short of A's end
assert name == "running_flat", (name, info)

name, info = es.abc_shape(100, 120, 101, 120.5)       # regression: B 95 % + C just past A's end is a flat, not a zigzag
assert name == "regular_flat", (name, info)

name, info = es.abc_shape(100, 120, 125, 130)          # B goes further up than A: not a correction
assert name is None, (name, info)

# mirror: A goes down 120 -> 100, same zigzag shape flipped
name, info = es.abc_shape(120, 100, 112, 90)
assert name == "zigzag", (name, info)

# --- five-leg impulse vs ending diagonal ---
assert es.impulse_shape(100, 120, 110, 150, 140, 160) == "impulse"
# wave 4 enters wave 1's zone (118 <= 120) and wave 5 is shorter than wave 3: converging wedge
assert es.impulse_shape(100, 120, 112, 150, 118, 152) == "ending_diagonal"
# wave 2 goes beyond the start of wave 1: broken structure
assert es.impulse_shape(100, 120, 99, 150, 140, 160) is None

# --- triangles ---
assert es.triangle_shape(100, 120, 105, 115, 108, 113) == "contracting"   # legs 20,15,10,7,5
assert es.triangle_shape(100, 110, 95, 115, 90, 120) == "expanding"       # legs 10,15,20,25,30
assert es.triangle_shape(100, 120, 90, 130, 100, 110) is None             # legs jump up and down

print("test_elliott_shapes: OK")

# --- W-X-Y (up-going W, X comes back down, Y goes up again) ---
# W: 100 -> 120 (zigzag: B 108, C 130) ; X: 130 -> 110 (50 % of W counter); Y: 110 -> 130 (zigzag) -> 145 -> 125 -> 150
# the test builds pivot tuples by value: p0..p7
name, info = es.wxy_shape(100, 120, 108, 130, 110, 125, 115, 145)
assert name == "double_zigzag", (name, info)
# W flat (B passes start of A... ) and Y flat -> double_three
name, info = es.wxy_shape(100, 120, 95, 125, 110, 130, 111.0, 130.5)
assert name == "double_three", (name, info)
# X too shallow (<38.2 % of W): not a W-X-Y
name, info = es.wxy_shape(100, 120, 108, 130, 125, 135, 128, 145)
assert name is None, (name, info)
# X goes the same way as W: not a W-X-Y
name, info = es.wxy_shape(100, 120, 108, 130, 140, 150, 145, 160)
assert name is None, (name, info)
print("test_elliott_shapes wxy: OK")

# --- triple W-X-Y-X-Z, alternation, Fibonacci zone, triangle convergence ---
name, info = es.triple_shape(100, 120, 108, 130, 110, 125, 115, 145, 128, 150, 140, 165)
assert name == "triple_zigzag", (name, info)
name, info = es.triple_shape(100, 120, 108, 130, 110, 125, 115, 145, 146, 150, 140, 165)   # second X too deep vs ratio? must fail X range
assert name is None, (name, info)
assert es.alternation(100, 120, 110, 150, 140, 160) is True          # wave 2 deep, wave 4 shallow
assert es.alternation(100, 120, 115, 150, 140, 160) is False         # both shallow
assert es.alternation(100, 120, 95, 150, 140, 160) is None           # not an impulse
z = es.fib_zone(100, 120, 110)
assert abs(z[0.5] - 100.0) < 1e-9 and abs(z[0.618] - (110 - 0.618 * 20)) < 1e-9
assert es.triangle_converge(100, 120, 105, 115, 108, 113) == "contracting"
assert es.triangle_converge(100, 110, 95, 115, 90, 120) == "expanding"
assert es.triangle_converge(100, 120, 90, 130, 100, 110) is None
assert es.classify_tail([100, 120, 108, 130, 110, 125, 115, 145, 128, 150, 140, 165]) == "triple_zigzag"
print("test_elliott_shapes triple/alternation/fib/triangle: OK")

# --- leading vs ending diagonal (context: the same-kind pivot before the diagonal) ---
diag = [100, 120, 112, 150, 118, 152]                      # an up wedge: wave 4 overlaps wave 1, wave 5 shorter than wave 3
assert es.impulse_shape(*diag) == "ending_diagonal"
assert es.diagonal_kind(105, *diag) == "leading_diagonal"   # price came down into 100 (lower low): the wedge starts a move
assert es.diagonal_kind(95, *diag) == "ending_diagonal"     # price was rising into 100 (higher low): the wedge ends a move
assert es.classify_tail([125, 140] + diag) == "leading_diagonal"   # context chosen so it is not also a W-X-Y
assert es.classify_tail([95, 130] + diag) == "ending_diagonal"
assert es.classify_tail(diag) == "ending_diagonal"          # no context: stays ending (the old label)
print("test_elliott_shapes diagonals: OK")
