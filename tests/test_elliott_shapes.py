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
