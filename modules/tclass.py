"""TRADE CLASSES on the server: the same engine as the Workspace widget (JS block TCLASS-BEGIN..END in modules/ws/24b_tclass.js,
plus SR.compute), ported line by line so the Telegram job (modules/tclass_cron.py) sends the trades the widget shows.
tests/test_tclass_parity.py runs both on the same candles and needs identical numbers.

Style -> timeframe stack (bias -> setup -> entry). S/R bounce: nearest support / resistance (pivot clusters, >= 2 touches) -> a bounce
trade with a target in POINTS; past bounces measured walk-forward on the setup timeframe (levels only after their pivot was confirmed,
stop first when one bar touches both). Information, not a proven edge: < 30 forward trades = not evidence."""
from __future__ import annotations

import math

STYLES = {
    "Scalp":     {"bias": "1h", "setup": "15m", "entry": "5m",  "tfk": "5m",  "hold": 16},
    "Day Trade": {"bias": "4h", "setup": "1h",  "entry": "15m", "tfk": "15m", "hold": 24},
    "Swing":     {"bias": "1w", "setup": "1d",  "entry": "4h",  "tfk": "4h",  "hold": 20},
    "Position":  {"bias": "1mo", "setup": "1w", "entry": "1d",  "tfk": "1d",  "hold": 16},
}
TF_LABEL = {"5m": "5m", "15m": "15m", "1h": "1H", "4h": "4H", "1d": "1D", "1w": "1W", "1mo": "1M"}


def _round(x: float) -> int:          # JS Math.round (half up), not Python's banker's rounding
    return int(math.floor(x + 0.5))


def rows_of(df) -> list[dict]:
    """DataFrame (open/high/low/close) -> [{'o','h','l','c'}] oldest first."""
    return [{"o": float(o), "h": float(h), "l": float(l), "c": float(c)} for o, h, l, c in zip(df["open"], df["high"], df["low"], df["close"])]


def point_size(sym: str, px: float) -> float:
    import re
    sym = str(sym or "")
    b = re.sub(r"^(HL:xyz:|HL:|FH:|Y:)", "", sym).upper()
    if re.search(r"=X$", b) or re.match(r"^(EUR|GBP|AUD|NZD|USD|CAD|CHF|JPY)[_/]?(EUR|GBP|AUD|NZD|USD|CAD|CHF|JPY)", b):
        return 0.01 if "JPY" in b else 0.0001
    if re.search(r"XAU|GOLD|^GC=F", b):
        return 0.1
    if re.search(r"XAG|SILVER|^SI=F|^CL=F|^BZ=F|OIL|WTI|BRENT|^NG=F|NATGAS", b):
        return 0.01
    if re.search(r"^\^|SP500|SPX|NAS|NDX|US30|DJI|DAX|DE30|UK100|JP225|NIKKEI|US500|USTEC", b):
        return 1
    if sym.startswith("Y:") or sym.startswith("HL:xyz:"):
        return 0.01
    px = abs(float(px or 0))
    return 1 if px >= 1000 else 0.01 if px >= 10 else 0.001 if px >= 1 else 0.00001 if px >= 0.01 else 0.0000001


def atr(rows, n: int = 14, upto: int | None = None) -> float:
    upto = len(rows) - 1 if upto is None else upto
    n = min(n or 14, upto)
    if n < 1:
        return 0.0
    s = 0.0
    for i in range(upto - n + 1, upto + 1):
        r, p = rows[i], rows[i - 1]
        s += max(r["h"] - r["l"], abs(r["h"] - p["c"]), abs(r["l"] - p["c"]))
    return s / n


def ema(vals, span: int):
    a, e, out = 2 / (span + 1), vals[0], []
    for v in vals:
        e = a * v + (1 - a) * e
        out.append(e)
    return out


def bias(rows) -> dict:
    if not rows or len(rows) < 60:
        return {"available": False}
    k, hs, ls = 3, [], []
    for i in range(k, len(rows) - k):
        H = L = True
        for j in range(i - k, i + k + 1):
            if j == i:
                continue
            if rows[j]["h"] >= rows[i]["h"]:
                H = False
            if rows[j]["l"] <= rows[i]["l"]:
                L = False
        if H:
            hs.append(rows[i]["h"])
        if L:
            ls.append(rows[i]["l"])
    h2, l2, trend = hs[-2:], ls[-2:], "range"
    if len(h2) == 2 and len(l2) == 2:
        if h2[1] > h2[0] and l2[1] > l2[0]:
            trend = "up"
        elif h2[1] < h2[0] and l2[1] < l2[0]:
            trend = "down"
    e = ema([r["c"] for r in rows], 50)
    side = "above" if rows[-1]["c"] > e[-1] else "below"
    sc = (1 if trend == "up" else -1 if trend == "down" else 0) + (1 if side == "above" else -1)
    return {"available": True, "trend": trend, "ema": side, "bias": "bull" if sc > 0 else "bear" if sc < 0 else "neutral", "strength": abs(sc)}


def sr_levels(rows, k: int = 3) -> list[dict]:
    """Port of SR.compute in the Workspace: pivot highs / lows clustered within max(0.6 ATR, 0.2 %), >= 2 touches."""
    n = len(rows)
    if n < 2 * k + 5:
        return []
    cp = rows[-1]["c"]
    m = min(14, n - 1)
    a = sum(max(rows[i]["h"] - rows[i]["l"], abs(rows[i]["h"] - rows[i - 1]["c"]), abs(rows[i]["l"] - rows[i - 1]["c"])) for i in range(n - m, n)) / m
    tol = max(a * 0.6, cp * 0.002)
    pv = []
    for i in range(k, n - k):
        hh = ll = True
        for j in range(i - k, i + k + 1):
            if j == i:
                continue
            if rows[j]["h"] >= rows[i]["h"]:
                hh = False
            if rows[j]["l"] <= rows[i]["l"]:
                ll = False
        w = 0.5 + 0.5 * i / n
        if hh:
            pv.append({"p": rows[i]["h"], "w": w, "i": i})
        if ll:
            pv.append({"p": rows[i]["l"], "w": w, "i": i})
    pv.sort(key=lambda q: q["p"])
    cl = []
    for q in pv:
        c = cl[-1] if cl else None
        if c and q["p"] - c["max"] <= tol:
            c["s"] += q["p"]; c["n"] += 1; c["w"] += q["w"]; c["max"] = q["p"]; c["last"] = max(c["last"], q["i"])
        else:
            cl.append({"s": q["p"], "n": 1, "w": q["w"], "max": q["p"], "last": q["i"]})
    out = []
    for c in cl:
        if c["n"] < 2:
            continue
        p = c["s"] / c["n"]
        out.append({"p": p, "touches": c["n"], "strength": max(1, min(5, _round(c["w"] * 1.1))), "kind": "R" if p > cp else "S", "dist": (p - cp) / cp * 100})
    out.sort(key=lambda x: abs(x["dist"]))
    return out


def events(rows, hold: int = 16, stop_atr: float = 0.6, tol_atr: float = 0.35, k: int = 3, start: int = 30) -> list[dict]:
    n, out, piv = len(rows), [], []
    if n < start + 10:
        return out
    next_piv, last_ev = k, -99
    for i in range(start, n - 1):
        while next_piv <= i - k - 1:
            j = next_piv
            next_piv += 1
            if j < k or j + k >= n:
                continue
            H = L = True
            for q in range(j - k, j + k + 1):
                if q == j:
                    continue
                if rows[q]["h"] >= rows[j]["h"]:
                    H = False
                if rows[q]["l"] <= rows[j]["l"]:
                    L = False
            if H:
                piv.append(rows[j]["h"])
            if L:
                piv.append(rows[j]["l"])
        if not piv or i - last_ev < 3:
            continue
        a = atr(rows, 14, i)
        if not a > 0:
            continue
        r, p0 = rows[i], rows[i - 1]
        tol = max(a * tol_atr, r["c"] * 0.0005)
        best = None
        for Lv in piv:
            if p0["l"] > Lv + tol and r["l"] <= Lv + tol and r["l"] >= Lv - tol * 2 and r["c"] > Lv:
                d = abs(r["l"] - Lv)
                if not best or d < best[0]:
                    best = (d, 1, Lv)
            if p0["h"] < Lv - tol and r["h"] >= Lv - tol and r["h"] <= Lv + tol * 2 and r["c"] < Lv:
                d = abs(r["h"] - Lv)
                if not best or d < best[0]:
                    best = (d, -1, Lv)
        if not best:
            continue
        s, Lv = best[1], best[2]
        entry = r["c"]
        stop = Lv - s * a * stop_atr
        risk = abs(entry - stop)
        if not risk > 0:
            continue
        mfe, stopped = 0.0, False
        for q in range(i + 1, min(n, i + 1 + hold)):
            c = rows[q]
            if (c["l"] <= stop) if s > 0 else (c["h"] >= stop):
                stopped = True
                break
            mfe = max(mfe, c["h"] - entry if s > 0 else entry - c["l"])
        out.append({"i": i, "side": s, "level": Lv, "entry": entry, "stop": stop, "risk": risk, "mfe": mfe, "stopped": stopped})
        last_ev = i
    return out


def stats(ev, target: float) -> dict:
    n = len(ev)
    if not n:
        return {"n": 0}
    m = sorted(e["mfe"] for e in ev)
    q = lambda p: m[min(n - 1, int(math.floor(p * (n - 1))))]
    hit = sum(1 for e in ev if e["mfe"] >= target) if target > 0 else None
    return {"n": n, "median": q(0.5), "p25": q(0.25), "p75": q(0.75), "hit": hit, "hitPct": None if hit is None else hit / n,
            "medRisk": sorted(e["risk"] for e in ev)[(n - 1) // 2]}


def nice_pts(x: float) -> float:
    if not x > 0:
        return 0
    p = 10 ** math.floor(math.log10(x))
    f = x / p
    return (1 if f < 1.5 else 2 if f < 2.25 else 2.5 if f < 3.5 else 5 if f < 7.5 else 10) * p


def rejection(rows, side: int) -> bool:
    if not rows or len(rows) < 3:
        return False
    c = rows[-2]
    rg = c["h"] - c["l"]
    if not rg > 0:
        return False
    if side > 0:
        return (min(c["o"], c["c"]) - c["l"]) / rg >= 0.45 and c["c"] >= c["o"] - rg * 0.1
    return (c["h"] - max(c["o"], c["c"])) / rg >= 0.45 and c["c"] <= c["o"] + rg * 0.1


def candidates(sym, setup_rows, levels, bias_rows, entry_rows, target_pts: float = 0, ps: float = 0, hold: int = 16,
               zone_atr: float = 0.5, near_atr: float = 1.5, stop_atr: float = 0.6) -> list[dict]:
    n = len(setup_rows) if setup_rows else 0
    if n < 60 or not levels:
        return []
    px, a = setup_rows[-1]["c"], atr(setup_rows, 14)
    if not a > 0:
        return []
    ps = ps if ps > 0 else point_size(sym, px)
    ev, b = events(setup_rows, hold=hold, stop_atr=stop_atr), bias(bias_rows)
    auto_pts = max(1, nice_pts((stats(ev, 0).get("median") or a) / ps))
    t_pts = target_pts if target_pts > 0 else auto_pts
    T_ = t_pts * ps
    st, out = stats(ev, T_), []
    for kind, s in (("S", 1), ("R", -1)):
        lvs = sorted([x for x in levels if x["kind"] == kind], key=lambda x: abs(x["p"] - px))
        if not lvs:
            continue
        lv = lvs[0]
        dist = px - lv["p"] if s > 0 else lv["p"] - px
        if dist < -a * 0.25 or dist > a * near_atr:
            continue
        now = dist <= a * zone_atr
        entry = px if now else lv["p"] + s * a * 0.15
        stop = lv["p"] - s * a * stop_atr
        risk = abs(entry - stop)
        if not risk > 0:
            continue
        opp = sorted([x for x in levels if x["kind"] == ("R" if s > 0 else "S") and s * (x["p"] - entry) > T_ * 1.2], key=lambda x: abs(x["p"] - entry))
        tps = [entry + s * T_, opp[0]["p"] - s * a * 0.1 if opp else entry + s * T_ * 1.6]
        rr, rej, want = T_ / risk, rejection(entry_rows, s), "bull" if s > 0 else "bear"
        agree = (1 if b["bias"] == want else 0 if b["bias"] == "neutral" else -1) if b.get("available") else 0
        why, score = [], 0
        if lv["touches"] >= 3:
            score += 1; why.append(f"level touched {lv['touches']}x")
        if now:
            score += 1; why.append("price is at the zone now")
        else:
            why.append("limit order at the zone")
        if agree > 0:
            score += 1; why.append(f"higher timeframe agrees ({b['bias']})")
        elif agree < 0:
            why.append(f"COUNTER-TREND: higher timeframe is {b['bias']}")
        if st["n"] >= 10 and st["hitPct"] >= 0.5:
            score += 1; why.append(f"target reached in {_round(st['hitPct'] * 100)}% of {st['n']} past bounces")
        if rr >= 1.5:
            score += 1; why.append(f"R:R {rr:.1f}")
        if rej:
            score += 1; why.append("rejection candle on the entry timeframe")
        out.append({"side": s, "level": lv["p"], "touches": lv["touches"], "entry": entry, "stop": stop, "tps": tps, "now": now, "pts": t_pts,
                    "autoPts": auto_pts, "ps": ps, "rr": rr, "st": st, "agree": agree, "rej": rej, "score": score, "max": 6, "why": why, "atr": a})
    return out


def scan(sym: str, style: str, get_klines, target_pts: float = 0) -> list[dict]:
    """Live trades for one symbol + style. get_klines(sym, tf, limit) -> DataFrame (modules.market_cache.get_klines)."""
    S = STYLES[style]
    setup = rows_of(get_klines(sym, S["setup"], 300))
    try:
        brows = rows_of(get_klines(sym, S["bias"], 120))
    except Exception:
        brows = []
    lv = sr_levels(setup)
    cs = candidates(sym, setup, lv, brows, None, target_pts=target_pts, hold=S["hold"])
    if cs:
        try:
            cs = candidates(sym, setup, lv, brows, rows_of(get_klines(sym, S["entry"], 60)), target_pts=target_pts, hold=S["hold"])
        except Exception:
            pass
    for c in cs:
        c.update({"symbol": sym, "style": style, "direction": "bullish" if c["side"] > 0 else "bearish", "tfk": S["tfk"],
                  "stack": f"{TF_LABEL[S['bias']]} → {TF_LABEL[S['setup']]} → {TF_LABEL[S['entry']]}"})
    return cs


def fmt(c: dict) -> str:
    """Telegram message (HTML), Arabic like the Setup Card."""
    import html
    up = c["direction"] == "bullish"
    st = c.get("st") or {}
    ps = c["ps"]
    lines = [f"🎯 <b>TRADE CLASSES</b> {'🟢' if up else '🔴'} <b>{html.escape(c['symbol'])}</b> {'شراء ▲' if up else 'بيع ▼'} · {html.escape(c['style'])} · {c['stack']}",
             f"ارتداد من {'دعم' if up else 'مقاومة'} {c['level']:.6g} (اتلمس {c['touches']} مرات) · القوة {c['score']}/{c['max']}",
             f"\n<b>الخطة</b>\nدخول {c['entry']:.6g} · وقف {c['stop']:.6g}\nهدف {c['tps'][0]:.6g} ({c['pts']:g} نقطة) / {c['tps'][1]:.6g} · R:R 1:{c['rr']:.1f}"]
    if st.get("n"):
        hp = "–" if st.get("hitPct") is None else f"{_round(st['hitPct'] * 100)}%"
        lines.append(f"\nتاريخيًا: متوسط الارتداد ~{_round(st['median'] / ps)} نقطة، الهدف اتضرب {hp} من {st['n']} مرة" + (" (أقل من 30 = مش دليل)" if st["n"] < 30 else ""))
    lines.append("ترابط الفريمات: " + ("متوافق" if c["agree"] > 0 else "عكس الاتجاه (حذر)" if c["agree"] < 0 else "محايد"))
    lines.append("\n" + html.escape(" · ".join(c["why"])))
    lines.append("\n<i>معلومة مش نسبة نجاح مثبتة. مش نصيحة مالية.</i>")
    return "\n".join(lines)[:3900]
