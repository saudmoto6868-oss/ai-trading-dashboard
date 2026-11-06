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
    """Judged ideas for one symbol + style, best first (same rules as the widget; the server has S/R bounce + breakout / BOS / MSS only:
    no volume profile, SMT, Elliott, harmonic, scanner, news calendar or browser journal). get_klines(sym, tf, limit) -> DataFrame."""
    S = STYLES[style]
    sdf = get_klines(sym, S["setup"], 300)
    setup = rows_of(sdf)
    if len(setup) < 60:
        return []
    notes = []
    try:
        brows = rows_of(get_klines(sym, S["bias"], 120))
    except Exception:
        brows = []
    if len(brows) < 60:
        notes.append(f"no {S['bias']} candles: bias not counted")
    try:
        erows = rows_of(get_klines(sym, S["entry"], 80))
    except Exception:
        erows = []
    if len(erows) < 20:
        erows = setup
    px, a = setup[-1]["c"], atr(setup, 14)
    ps = point_size(sym, px)
    ev = events(setup, hold=S["hold"])
    auto = max(1, nice_pts((stats(ev, 0).get("median") or a) / ps))
    t_pts = target_pts if target_pts > 0 else auto
    T_ = t_pts * ps
    lv = sr_levels(setup)
    ideas = []

    def mk(det, side, entry, stop, now, level, label):
        if not entry > 0 or not abs(entry - stop) > 0 or (stop >= entry if side > 0 else stop <= entry):
            return
        ideas.append({"det": det, "label": label, "side": side, "entry": entry, "stop": stop, "now": now, "level": level, "tps": [entry + side * T_, entry + side * T_ * 1.6]})
    for c in candidates(sym, setup, lv, brows, erows, target_pts=t_pts, ps=ps, hold=S["hold"]):
        mk("bounce", c["side"], c["entry"], c["stop"], c["now"], c["level"], f"Bounce from {'support' if c['side'] > 0 else 'resistance'} {_prec(c['level'])} x{c['touches']}")
    for b in structure(setup, 6):
        d = b["side"] * (px - b["level"])
        now = -a * 0.3 <= d <= a * 0.8
        mk("struct", b["side"], px if now else b["level"] + b["side"] * a * 0.1, b["level"] - b["side"] * a, now, b["level"], f"{b['kind']} {'up' if b['side'] > 0 else 'down'} {_prec(b['level'])}")
    bias_ = bias(brows) if len(brows) >= 60 else {"available": False}
    setup_b = bias(setup)
    try:
        from modules.regime import classify
        reg = classify(sdf).get("regime")
    except Exception:
        reg = None
    ent_struct = structure(erows, 3) if erows is not setup else []
    levels = [{"p": l["p"], "src": "resistance" if l["kind"] == "R" else "support"} for l in lv]
    tf = {"bias": TF_LABEL[S["bias"]], "setup": TF_LABEL[S["setup"]], "entry": TF_LABEL[S["entry"]]}
    names = {"bounce": "S/R bounce", "struct": "Breakout / BOS / MSS"}
    out = []
    for idea in ideas:
        s_ = idea["side"]
        hist = stats([e for e in ev if e["side"] == s_], abs(idea["tps"][0] - idea["entry"]))
        tS = next((b for b in ent_struct if b["side"] == s_), None)
        trig = f"{tS['kind']} {tf['entry']}" if tS else "rejection candle" if rejection(erows, s_) else ""
        confl = sorted({names[o["det"]] for o in ideas if o is not idea and o["side"] == s_ and o["det"] != idea["det"] and abs(o["entry"] - idea["entry"]) <= a})
        late = max(0.0, s_ * (px - idea["level"])) / max(1e-12, abs(idea["tps"][0] - idea["level"])) if idea["now"] else 0
        ctx = {"tf": tf, "ps": ps, "atr": a, "levels": levels, "bias": bias_, "setupB": setup_b, "trig": trig, "confl": confl, "vpAt": "", "hist": hist,
               "late": late if late > 0.4 else 0, "regime": reg, "news": "", "openSame": False, "openOpp": False, "classOpen": 0, "jr": None, "scalp": style == "Scalp", "ses": ""}
        j = judge(idea, ctx)
        out.append(dict(idea, j=j, symbol=sym, style=style, direction="bullish" if s_ > 0 else "bearish", tfk=S["tfk"], ps=ps, notes=notes,
                        stack=f"{tf['bias']} → {tf['setup']} → {tf['entry']}"))
    order = {"TAKE": 2, "WAIT": 1, "SKIP": 0}
    out.sort(key=lambda x: (-order[x["j"]["verdict"]], -x["j"]["score"]))
    return out


def fmt(c: dict) -> str:
    """Telegram message (HTML), Arabic: the decision, the plan, why take it, why not, the second look."""
    import html
    e = html.escape
    up, j = c["direction"] == "bullish", c["j"]
    pl = j["plan"]
    V = {"TAKE": "ادخل ✅", "WAIT": "استنى ⏳", "SKIP": "ماتدخلش ⛔"}
    lines = [f"🎯 <b>TRADE CLASSES</b> {'🟢' if up else '🔴'} <b>{e(c['symbol'])}</b> {'شراء ▲' if up else 'بيع ▼'} · {e(c['style'])} · {e(c['stack'])}",
             f"القرار: <b>{V[j['verdict']]}</b> · {e(c['label'])} · النتيجة {j['score']}",
             f"\n<b>الخطة</b>\nدخول {_prec(pl['entry'])} · وقف {_prec(pl['stop'])}\nهدف {_prec(pl['tps'][0])} ({j['pts']} نقطة) / {_prec(pl['tps'][1])} · R:R 1:{_fix(j['rr'])}"]
    if j["pros"]:
        lines.append("\n<b>ليه أدخل</b>\n" + "\n".join("✔ " + e(p[2]) for p in j["pros"]))
    if j["cons"]:
        lines.append("\n<b>ليه ماادخلش</b>\n" + "\n".join("✘ " + e(p[2]) for p in j["cons"]))
    if j["second"]:
        lines.append("\n<b>مراجعة تانية</b>\n" + "\n".join("↻ " + e(p[1]) for p in j["second"]))
    lines.append("\n<i>من السيرفر: ارتداد + كسر هيكل بس (الفوليوم بروفايل / SMT / إليوت / الهارمونيك في الويدجت). معلومة مش نسبة نجاح مثبتة. مش نصيحة مالية.</i>")
    return "\n".join(lines)[:3900]


# ---- deliberation (port of TCE.swings / structure / obstacle / judge in modules/ws/24b_tclass.js; tests/test_tclass_parity.py) ----
def _prec(x: float, p: int = 6) -> str:
    """JS Number.prototype.toPrecision."""
    s = f"{x:#.{p}g}"
    if "e" in s:
        m, e = s.split("e")
        s = m + "e" + ("+" if int(e) >= 0 else "-") + str(abs(int(e)))
    return s


def _fix(x: float, d: int = 1) -> str:     # JS toFixed
    return f"{x:.{d}f}"


def _num(x: float) -> str:                 # JS default number -> string for small decimals like a weight 2.5
    return str(int(x)) if float(x).is_integer() else repr(float(x))


def swings(rows, k: int = 3) -> list[dict]:
    out = []
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
            out.append({"i": i, "p": rows[i]["h"], "k": "H"})
        if L:
            out.append({"i": i, "p": rows[i]["l"], "k": "L"})
    return out


def structure(rows, fresh: int = 6) -> list[dict]:
    n, out = len(rows), []
    if n < 40:
        return out
    sw = swings(rows, 3)
    for k, s in (("H", 1), ("L", -1)):
        L_ = [x for x in sw if x["k"] == k]
        if len(L_) < 2:
            continue
        q, prev = L_[-1], L_[-2]
        brk = -1
        for i in range(q["i"] + 4, n):
            if (rows[i]["c"] > q["p"]) if s > 0 else (rows[i]["c"] < q["p"]):
                brk = i
                break
        if brk < 0 or n - 1 - brk > fresh:
            continue
        was = q["p"] > prev["p"] if s > 0 else q["p"] < prev["p"]
        out.append({"side": s, "level": q["p"], "i": brk, "kind": "BOS" if was else "MSS"})
    return out


def obstacle(entry, target, side, levels, a):
    best = None
    for l in levels or []:
        d = side * (l["p"] - entry)
        if d > a * 0.25 and side * (target - l["p"]) > 0 and (best is None or d < side * (best["p"] - entry)):
            best = l
    return best


def judge(idea: dict, c: dict) -> dict:
    s = idea["side"]
    pros, cons, vetoes, second = [], [], [], []
    P = lambda w, en, ar: pros.append([w, en, ar])
    C = lambda w, en, ar: cons.append([w, en, ar])
    entry, stop = idea["entry"], idea["stop"]
    risk = abs(entry - stop) or 1e-12
    tps = list(idea["tps"])
    want = "bull" if s > 0 else "bear"
    ps = c.get("ps") or 1
    pt = lambda x: _round(abs(x) / ps)
    tf = c["tf"]
    ob = obstacle(entry, tps[0], s, c.get("levels"), c["atr"])
    blocked = False
    if ob:
        cut = ob["p"] - s * c["atr"] * 0.1
        rr_cut = abs(cut - entry) / risk
        if rr_cut >= 1.5:
            second.append([f"Target cut from {pt(tps[0] - entry)} to {pt(cut - entry)} pts: {ob['src']} at {_prec(ob['p'])} stands in the way",
                           f"الهدف اتقص من {pt(tps[0] - entry)} لـ{pt(cut - entry)} نقطة: فيه {ob['src']} عند {_prec(ob['p'])} في السكة"])
            tps[0] = cut
            if s * (tps[1] - cut) <= 0:
                tps[1] = ob["p"] + s * c["atr"] * 0.3
        else:
            blocked = True
            C(2, f"{ob['src']} at {_prec(ob['p'])} before the target; cutting the target leaves R:R {_fix(rr_cut)}",
              f"فيه {ob['src']} عند {_prec(ob['p'])} قبل الهدف؛ لو قصيت الهدف الـR:R يبقى {_fix(rr_cut)}")
    if s * (tps[1] - tps[0]) <= 0:
        tps[1] = tps[0] + s * abs(tps[0] - entry) * 0.6
    rr = abs(tps[0] - entry) / risk
    b, sb, h, jr = c.get("bias") or {}, c.get("setupB") or {}, c.get("hist") or {}, c.get("jr") or {}
    if b.get("available") and b.get("bias") == want:
        P(2, f"Bias timeframe {tf['bias']} agrees ({b['bias']})", f"فريم الاتجاه {tf['bias']} موافق ({b['bias']})")
    if sb.get("available") and sb.get("bias") == want:
        P(1, f"Setup timeframe {tf['setup']} trend agrees", f"ترند فريم الإعداد {tf['setup']} موافق")
    if c.get("trig"):
        P(1.5, f"Entry timeframe {tf['entry']} trigger: {c['trig']}", f"إشارة على فريم الدخول {tf['entry']}: {c['trig']}")
    if c.get("confl"):
        P(min(3, len(c["confl"])), "Other schools at the same zone: " + ", ".join(c["confl"]), "مدارس تانية في نفس المنطقة: " + "، ".join(c["confl"]))
    if c.get("vpAt"):
        P(1, f"Volume-profile node at the entry ({c['vpAt']})", f"نقطة فوليوم بروفايل عند الدخول ({c['vpAt']})")
    if h.get("n", 0) >= 10 and h["hitPct"] >= 0.55:
        P(1.5, f"Past bounces here reached this target {_round(h['hitPct'] * 100)}% of {h['n']}", f"الارتدادات اللي فاتت هنا وصلت للهدف ده {_round(h['hitPct'] * 100)}% من {h['n']} مرة")
    if rr >= 2 and not blocked:
        P(1, f"R:R {_fix(rr)}", f"R:R {_fix(rr)}")
    if jr.get("done", 0) >= 10 and (jr.get("avgR") or 0) > 0:
        P(1, f"This idea type is positive in your journal ({jr['done']} trades, {_fix(jr['avgR'], 2)}R)", f"النوع ده كسبان في الجورنال بتاعك ({jr['done']} صفقة، {_fix(jr['avgR'], 2)}R)")
    ses = c.get("ses") or ""
    if c.get("scalp") and ses and ses != "off-KZ" and "KZ" in ses:
        P(0.5, f"Inside a kill zone ({ses})", f"جوه كيل زون ({ses})")
    if b.get("available") and b.get("bias") not in (want, "neutral"):
        C(2.5, f"Bias timeframe {tf['bias']} is against ({b['bias']})", f"فريم الاتجاه {tf['bias']} ضدك ({b['bias']})")
    if not b.get("available"):
        C(0.5, f"No bias timeframe data ({tf['bias']})", f"مفيش بيانات لفريم الاتجاه ({tf['bias']})")
    if sb.get("available") and sb.get("bias") not in (want, "neutral"):
        C(1, "Setup timeframe trend is against", "ترند فريم الإعداد ضدك")
    if not c.get("trig"):
        C(0.5, f"No trigger yet on the entry timeframe {tf['entry']}", f"لسه مفيش إشارة على فريم الدخول {tf['entry']}")
    if rr < 1.5:
        C(1.5, f"R:R only {_fix(rr)}", f"الـR:R {_fix(rr)} بس")
    if c.get("late"):
        C(1.5, f"Late: price already went {_round(c['late'] * 100)}% of the way to the target", f"متأخر: السعر مشي {_round(c['late'] * 100)}% من المسافة للهدف")
    if h.get("n", 0) >= 10 and h["hitPct"] < 0.4:
        C(1.5, f"Past bounces reached this target only {_round(h['hitPct'] * 100)}% of {h['n']}", f"الارتدادات اللي فاتت وصلت للهدف ده {_round(h['hitPct'] * 100)}% بس من {h['n']}")
    if h.get("n", 0) >= 10 and (h.get("p75") or 0) > 0 and abs(tps[0] - entry) > h["p75"]:
        C(1, f"Target is bigger than 3 of 4 past moves on {tf['setup']} ({pt(h['p75'])} pts)", f"الهدف أكبر من 3 من كل 4 حركات فاتت على {tf['setup']} ({pt(h['p75'])} نقطة)")
    if not h or h.get("n", 0) < 10:
        hn = h.get("n", 0) or 0
        C(0.5, f"Too little history to measure ({hn} past cases)", f"تاريخ قليل للقياس ({hn} حالة)")
    if c.get("regime") == "chop":
        C(1, "Market regime: chop (moves die quickly)", "حالة السوق: تذبذب (الحركات بتموت بسرعة)")
    if c.get("regime") in ("hivol", "crash"):
        C(1, f"Market regime: {c['regime']} (stops get hit by noise)", f"حالة السوق: {c['regime']} (الستوب بيتضرب من الضوضاء)")
    if (c.get("classOpen") or 0) >= 2:
        C(1, f"{c['classOpen']} open trades already in the same class and direction", f"فيه {c['classOpen']} صفقات مفتوحة في نفس الفئة والاتجاه")
    if jr.get("done", 0) >= 10 and (jr.get("avgR") or 0) < 0:
        C(1.5, f"This idea type loses in your journal ({jr['done']} trades, {_fix(jr['avgR'], 2)}R)", f"النوع ده خسران في الجورنال بتاعك ({jr['done']} صفقة، {_fix(jr['avgR'], 2)}R)")
    if c.get("scalp") and ses == "off-KZ":
        C(0.5, "Scalp outside the kill zones", "سكالب برة الكيل زون")
    if c.get("news"):
        vetoes.append([f"High-impact news within the hour: {c['news']}", f"خبر قوي خلال ساعة: {c['news']}"])
    if c.get("openSame"):
        vetoes.append(["You already have this trade open (journal)", "الصفقة دي مفتوحة عندك أصلًا (الجورنال)"])
    if c.get("openOpp"):
        vetoes.append(["An OPPOSITE trade on this symbol is open", "فيه صفقة عكسها مفتوحة على نفس الرمز"])
    if rr < 1:
        vetoes.append(["R:R below 1", "R:R أقل من 1"])
    score = _round((sum(x[0] for x in pros) - sum(x[0] for x in cons)) * 10) / 10
    verdict = "SKIP" if vetoes else ("TAKE" if idea["now"] else "WAIT") if score >= 3 and rr >= 1.5 else "WAIT" if score >= 1 else "SKIP"
    worst = sorted(cons, key=lambda x: -x[0])[0] if cons else None
    if verdict == "TAKE" and worst and worst[0] >= 2:
        verdict = "WAIT"
        second.append([f"Downgraded to WAIT: the strongest objection is heavy ({worst[1]})", f"نزلت لـ«استنى»: أقوى اعتراض تقيل ({worst[2]})"])
    if verdict == "WAIT" and not idea["now"]:
        second.append([f"Limit order at {_prec(entry)}: price has not reached the zone", f"أمر معلّق عند {_prec(entry)}: السعر لسه ماوصلش للمنطقة"])
    pct = max(0, min(100, _round((score + 4) / 12 * 100)))
    return {"pros": pros, "cons": cons, "vetoes": vetoes, "second": second, "score": score, "pct": pct, "verdict": verdict,
            "plan": {"entry": entry, "stop": stop, "tps": tps}, "rr": rr, "pts": pt(tps[0] - entry), "blocked": ob if blocked else None}
