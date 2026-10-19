"""Elliott school for the strategy lab: impulse candidates at two zig-zag degrees, scored by how many hard rules hold.

Event = the wave-4 pivot has just printed (5 pivots L H L H L for a bull candidate, mirrored for bear); the trade is
wave 5 in the impulse direction. Rules counted (own wording, see docs/ELLIOTT_HARMONIC.md):
  R1  wave 2 does not go beyond the start of wave 1
  R2  wave 4 does not enter the territory of wave 1
  R3  wave 3 is longer than wave 1 (proxy for "wave 3 is not the shortest": wave 5 is still unknown here)
Keys: ew_r3_<degree> (all three rules), ew_r2_<degree> (two of three). The lab decides whether the count matters.
Added 2026-10-19. Candles only; no network."""
from modules.harmonic import zigzag
from modules.signals import BEAR, BULL

DEGREES = {"d1": 0.012, "d2": 0.03}   # swing filter: 1.2 % minor, 3 % intermediate
MAX_AGE = 8                            # zig-zag confirms a pivot 3 bars late; the walk steps every 4 bars


def impulse_rules(px, bull):
    """px = [p0..p4] of an L H L H L (bull) or H L H L H (bear) candidate -> (rules held 0-3, or None if p3 fails to pass p1)."""
    s = 1 if bull else -1
    p0, p1, p2, p3, p4 = px
    if s * (p3 - p1) <= 0:
        return None
    w1, w3 = s * (p1 - p0), s * (p3 - p2)
    return sum([s * (p2 - p0) > 0, s * (p4 - p1) > 0, w3 > w1 > 0])


def elliott_signals(win):
    """Finalized-style signal dicts for one window (same shape as detect_all: family, name, key, direction, vals)."""
    h, l = win["high"].values, win["low"].values
    n = len(win)
    out = []
    for deg, dev in DEGREES.items():
        zz = zigzag(h, l, dev)
        if len(zz) < 5 or n - 1 - zz[-1][0] > MAX_AGE:
            continue
        kinds = [k for _, _, k in zz[-5:]]
        if kinds == ["L", "H", "L", "H", "L"]:
            bull = True
        elif kinds == ["H", "L", "H", "L", "H"]:
            bull = False
        else:
            continue
        rules = impulse_rules([p for _, p, _ in zz[-5:]], bull)
        if rules is None or rules < 2:
            continue
        out.append({"family": "Elliott", "name": f"Impulse wave-4 end ({deg}, {rules}/3 rules)", "key": f"ew_r{rules}_{deg}",
                    "direction": BULL if bull else BEAR, "vals": {"rules": rules, "deg": deg}})
    return out
