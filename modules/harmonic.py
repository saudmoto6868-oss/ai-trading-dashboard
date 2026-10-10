"""Harmonic pattern finder (XABCD): Gartley, Bat, Butterfly, Crab, Cypher.
Zig-zag pivots -> Fibonacci ratio checks with a tolerance. Mirrors the JS
version in workspace_app.html (keep both in sync)."""
import numpy as np

TOL = 0.06
# name: (B range of XA, C range of AB, D target of XA (or XC for Cypher))
RULES = {
    "Gartley":   dict(b=(0.618, 0.618), c=(0.382, 0.886), d=(0.786, 0.786)),
    "Bat":       dict(b=(0.382, 0.5),   c=(0.382, 0.886), d=(0.886, 0.886)),
    "Butterfly": dict(b=(0.786, 0.786), c=(0.382, 0.886), d=(1.272, 1.618)),
    "Crab":      dict(b=(0.382, 0.618), c=(0.382, 0.886), d=(1.618, 1.618)),
    "Cypher":    dict(b=(0.382, 0.618), cx=(1.13, 1.414), d=(0.786, 0.786)),
}


def zigzag(h, l, dev=0.012, n=3):
    """alternating pivots [(i, price, 'H'|'L')]; swings smaller than dev are ignored."""
    piv = []
    for i in range(n, len(h) - n):
        if h[i] >= h[i - n:i + n + 1].max():
            piv.append((i, float(h[i]), "H"))
        elif l[i] <= l[i - n:i + n + 1].min():
            piv.append((i, float(l[i]), "L"))
    out = []
    for p in piv:
        if out and out[-1][2] == p[2]:
            if (p[2] == "H" and p[1] > out[-1][1]) or (p[2] == "L" and p[1] < out[-1][1]):
                out[-1] = p
            continue
        if out and abs(p[1] - out[-1][1]) / out[-1][1] < dev:
            continue
        out.append(p)
    return out


def _in(v, rng):
    lo, hi = rng
    return lo * (1 - TOL) <= v <= hi * (1 + TOL)


def _check(X, A, B, C, D):
    """-> pattern name or None for 5 prices (direction inferred from X vs A)."""
    xa = abs(A - X)
    ab = abs(A - B)
    if xa <= 0 or ab <= 0:
        return None
    up = A > X  # X low -> bullish pattern
    s = 1 if up else -1
    if not (s * (B - X) > 0 and s * (A - B) > 0):
        return None
    b = ab / xa
    cab = abs(C - B) / ab
    for name, r in RULES.items():
        if not _in(b, r["b"]):
            continue
        if name == "Cypher":
            if not (s * (C - A) > 0):
                continue
            xc = abs(C - X)
            if not _in(xc / xa, r["cx"]) or not _in(abs(C - D) / xc, r["d"]):
                continue
        else:
            if not (s * (A - C) > 0 and s * (C - B) > 0) or not _in(cab, r["c"]):
                continue
            if not _in(abs(A - D) / xa, r["d"]) or s * (D - C) >= 0:
                continue
        return name
    return None


def find_harmonics(df, max_age=12, dev=0.012):
    """Patterns whose D point is recent. -> [{name, dir:'bull'|'bear', pts:[(i,price)]*5, forming:bool}]"""
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    piv = zigzag(h, l, dev)
    n = len(df)
    res = []
    sets = []
    if len(piv) >= 5:
        sets.append(([(p[0], p[1]) for p in piv[-5:]], False))
    if len(piv) >= 4:  # D = the live price (pattern still completing)
        last = piv[-1]
        cand = (n - 1, float(l[-1]) if last[2] == "H" else float(h[-1]))
        sets.append(([(p[0], p[1]) for p in piv[-4:]] + [cand], True))
    for pts, forming in sets:
        if n - 1 - pts[4][0] > max_age:
            continue
        name = _check(*[p[1] for p in pts])
        if name:
            res.append({"name": name, "dir": "bull" if pts[1][1] > pts[0][1] else "bear", "pts": pts, "forming": forming})
    return res
