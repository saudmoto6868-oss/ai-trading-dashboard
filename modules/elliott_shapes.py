"""Elliott correction shapes and diagonals as LABELS on a finished zig-zag pivot sequence (no signals, no network).

Input: pivots as (index, price) pairs, already alternating (low/high). Output: a shape name plus the ratios and
flags that decided it, so a chart can say "flat (expanded)" and the lab can count it later.

Rules are our measurable reading of the textbook shapes (Frost & Prechter style). Each threshold is a named
constant so it can be changed in one place and tested. Nothing here is evidence of profit: the lab decides.

Shapes:
  abc_shape(a0, a1, a2, a3)     -> 'zigzag' | 'regular_flat' | 'expanded_flat' | 'running_flat' | None
  impulse_shape(p0..p5)         -> 'impulse' | 'ending_diagonal' | None   (5 legs, 6 pivots)
  triangle_shape(p0..p5)        -> 'contracting' | 'expanding' | None     (5 legs, 6 pivots, A-B-C-D-E)
"""

# --- thresholds (fractions of wave A's length unless said otherwise) ---
ZZ_B_MIN = 0.382            # zigzag: B retraces at least 38.2 % of A
FLAT_B_LO = 0.90            # regular flat: B ends near the start of A (90 % .. 105 %)
FLAT_B_HI = 1.05
FLAT_C_TOL = 0.10           # regular flat: C ends within 10 % of A's length of the end of A
TRI_SHRINK = 0.95           # each triangle leg is at most 95 % of the one before (contracting)
TRI_GROW = 1.05             # ... at least 105 % of the one before (expanding)


def _len(a, b):
    return abs(b - a)


def abc_shape(a0, a1, a2, a3):
    """a0 = price at the start of A, a1 = end of A, a2 = end of B, a3 = end of C (prices).

    Returns (name, info) or (None, info). info holds b_ret (B retrace of A), c_vs_a (C length / A length),
    b_beyond_start (B passes A's start) and c_beyond_a_end (C passes A's end).
    """
    A = a1 - a0
    if A == 0:
        return None, {}
    s = 1 if A > 0 else -1                       # direction of A (mirror works for down-A corrections)
    lenA = abs(A)
    b_ret = s * (a1 - a2) / lenA                 # >0 when B goes back against A
    b_beyond = b_ret > 1.0                       # B passes the start of A
    c_beyond = s * (a3 - a1) > 0                 # C passes the end of A
    c_len_ratio = _len(a2, a3) / lenA            # length of C / length of A
    info = {"b_ret": round(b_ret, 3), "c_vs_a": round(c_len_ratio, 3),
            "b_beyond_start": b_beyond, "c_beyond_a_end": c_beyond}

    if b_ret <= 0 or b_ret > 1.5:                # B must go back against A, not absurdly far
        return None, info
    if not b_beyond and ZZ_B_MIN <= b_ret < FLAT_B_LO and c_beyond:   # zigzag: B shallower than a flat's B
        return "zigzag", info
    if FLAT_B_LO <= b_ret <= FLAT_B_HI and abs(a3 - a1) / lenA <= FLAT_C_TOL:
        return "regular_flat", info
    if b_beyond and c_beyond:
        return "expanded_flat", info
    if b_beyond and not c_beyond:
        return "running_flat", info
    return None, info


def impulse_shape(p0, p1, p2, p3, p4, p5):
    """Five legs p0..p5 in one direction. Returns 'impulse', 'ending_diagonal' or None.

    An impulse keeps wave 4 out of wave 1's price zone. A wedge-shaped (ending) diagonal lets wave 4 enter it
    and makes wave 5 shorter than wave 3 (the lines converge). Direction is taken from p1 vs p0.
    """
    s = 1 if p1 > p0 else -1
    w1, w3, w5 = s * (p1 - p0), s * (p3 - p2), s * (p5 - p4)
    if min(w1, w3, w5) <= 0:
        return None
    if s * (p2 - p0) <= 0 or s * (p3 - p1) <= 0 or s * (p5 - p3) <= 0:   # alternation of structure broken
        return None
    overlap4 = s * (p4 - p1) <= 0                  # wave 4 enters wave 1's price territory
    if not overlap4 and not (w3 < w1 and w3 < w5):
        return "impulse"
    if overlap4 and w5 < w3:                       # converging: each push shorter than the last
        return "ending_diagonal"
    return None


def triangle_shape(p0, p1, p2, p3, p4, p5):
    """Five legs A-B-C-D-E (p0..p5): leg lengths shrink (contracting) or grow (expanding) step by step.

    Only the leg-length rule is checked here; the trendline test is a later step.
    """
    legs = [abs(p1 - p0), abs(p2 - p1), abs(p3 - p2), abs(p4 - p3), abs(p5 - p4)]
    if min(legs) <= 0:
        return None
    if all(legs[k + 1] <= legs[k] * TRI_SHRINK for k in range(4)):
        return "contracting"
    if all(legs[k + 1] >= legs[k] * TRI_GROW for k in range(4)):
        return "expanding"
    return None


# --- double / triple structures: W-X-Y (X is the connecting counter-leg) ---
X_RET_MIN = 0.382           # X retraces at least 38.2 % of W (connector must be a real counter-move)
X_RET_MAX = 1.0             # ... and does not go past the start of W


def wxy_shape(p0, p1, p2, p3, p4, p5, p6, p7):
    """Eight pivots: W = p0..p3 (three legs), X = p3->p4 (one leg back), Y = p4..p7 (three legs).

    Returns (name, info). name:
      'double_zigzag' - W and Y are both zig-zags
      'double_three'  - W and Y are both flats
      'double_combo'  - one zig-zag, one flat
      None            - not a W-X-Y in this sense
    W's direction is taken from p1 vs p0; Y must continue it, X must go against it.
    """
    s = 1 if p1 > p0 else -1
    w_len = abs(p3 - p0)
    if w_len == 0:
        return None, {}
    x_len = abs(p4 - p3)
    x_ret = x_len / w_len
    info = {"x_ret": round(x_ret, 3)}
    if s * (p4 - p3) >= 0 or s * (p7 - p4) <= 0:                 # X must go back, Y must go on
        return None, info
    if not (X_RET_MIN <= x_ret <= X_RET_MAX):
        return None, info
    if s * (p3 - p0) <= 0:                                        # W must move in its own direction
        return None, info
    w_name, w_info = abc_shape(p0, p1, p2, p3)
    y_name, y_info = abc_shape(p4, p5, p6, p7)
    info.update({"w": w_name, "y": y_name})
    if w_name is None or y_name is None:
        return None, info
    w_zz, y_zz = w_name == "zigzag", y_name == "zigzag"
    if w_zz and y_zz:
        return "double_zigzag", info
    if not w_zz and not y_zz:
        return "double_three", info
    return "double_combo", info


def classify_tail(prices):
    """Label the newest pivots of an alternating price list: W-X-Y (last 8), triangle / impulse (last 6), ABC (last 4).

    Same order as the JS port (EWSHAPE block in the Workspace). Returns a shape name or None.
    """
    p = list(prices)
    n = len(p)
    if n >= 8:
        name, _ = wxy_shape(*p[-8:])
        if name:
            return name
    if n >= 6:
        q = p[-6:]
        name = triangle_shape(*q) or impulse_shape(*q)
        if name:
            return name
    if n >= 4:
        name, _ = abc_shape(*p[-4:])
        if name:
            return name
    return None


SHAPE_AR = {"zigzag": "تصحيح زيجزاج (ABC)", "regular_flat": "فلات عادي", "expanded_flat": "فلات ممتد",
            "running_flat": "فلات جاري", "impulse": "دافعة 1-5", "ending_diagonal": "دياجونال نهائي",
            "contracting": "مثلث متقارب", "expanding": "مثلث متسع", "double_zigzag": "زيجزاج مزدوج (W-X-Y)",
            "double_three": "ثلاثي مزدوج (W-X-Y)", "double_combo": "مركب (W-X-Y)"}
