"""Tools that implement Saud's "AI Trading Desk – Framework & Checklist":

  topdown_tool   yearly → monthly → weekly → daily levels (open / high / low / equilibrium)
  fib_tool       last impulse leg: OTE 0.62–0.79, Fibo POP 0.559–0.669, EQ, extensions
  smc_tool       BOS / CHoCH, order block (MSB-OB), fair value gaps, liquidity sweeps,
                 equal highs/lows (stop clusters) and an ICT "Unicorn" candidate check
  tech_tool      EMA 9/21 and session VWAP (fair-value anchor)
  smt_tool       intermarket SMT divergence between correlated markets (incl. DXY)
  scenarios      2–3 pre-planned scenarios at the key level (hold / break / trap-reverse)
  watchlist      departments → reasons → weighted stars; promotes markets with ≥3 reasons

Every formula is written out here so it can be audited. No paid indicator code is copied:
the Elliott Impulse Engine, OHL Results and Liquidity Lines are TradingView products and
are only approximated by the open logic below (prior-period OHL, swing liquidity).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import GATE, SMT_PAIRS, UNIVERSE, WATCH_MIN_REASONS
from ..data import sources
from .indicators import atr, ema, swings

FIB_RETRACE = [0.236, 0.382, 0.5, 0.559, 0.618, 0.669, 0.705, 0.786]
FIB_EXT = [1.272, 1.618, 2.0]


def _px(symbol: str, interval: str) -> tuple[pd.DataFrame, str]:
    yf = UNIVERSE[symbol]["yf"] if symbol in UNIVERSE else {"DXY": "DX-Y.NYB"}.get(symbol, symbol)
    return sources.prices(yf, interval)


def _dec(x: float) -> int:
    return 2 if abs(x) > 20 else 5


def _f(x: float | None) -> str:
    return "–" if x is None else f"{x:.{_dec(x)}f}"


def _ts(t) -> int:
    return int(pd.Timestamp(t).timestamp())


# ------------------------------------------------------------------ top-down
def topdown_tool(symbol: str) -> dict:
    """Prior completed Y/M/W/D ranges + current period opens. Price above the current
    period's open = that timeframe leans up (the 'OHL' read)."""
    df, src = _px(symbol, "1d")
    last = float(df["Close"].iloc[-1])
    a = float(atr(df).iloc[-1])
    rules = {"Y": "YE", "M": "ME", "W": "W-FRI", "D": "D"}
    tfs, levels = {}, []
    for tf, rule in rules.items():
        g = df.resample(rule).agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna()
        if len(g) < 2:
            continue
        prev, cur = g.iloc[-2], g.iloc[-1]
        rng = prev["High"] - prev["Low"]
        eq = (prev["High"] + prev["Low"]) / 2
        pos = (last - prev["Low"]) / rng if rng else 0.5
        lean = 1 if last > cur["Open"] else -1
        tfs[tf] = {"open": float(cur["Open"]), "prev_high": float(prev["High"]), "prev_low": float(prev["Low"]),
                   "eq": float(eq), "lean": lean, "pos": round(float(pos), 2),
                   "zone": "premium" if pos > 0.5 else "discount"}
        for name, v in ((f"P{tf}H", prev["High"]), (f"P{tf}L", prev["Low"]), (f"{tf}O", cur["Open"])):
            levels.append({"name": name, "price": float(v), "tf": tf, "dist_atr": round(abs(last - v) / a, 2) if a else 0})
    leans = [v["lean"] for v in tfs.values()]
    align = int(sum(leans))
    above = sorted((l for l in levels if l["price"] > last), key=lambda l: l["price"])
    below = sorted((l for l in levels if l["price"] <= last), key=lambda l: -l["price"])
    at_level = [l for l in levels if l["dist_atr"] <= 0.25]
    word = {4: "كل الفريمات صاعدة", -4: "كل الفريمات هابطة"}.get(align, f"المحصلة {align:+d} من 4")
    return {"tool": "topdown", "title": f"Top-down · من السنوي للساعة · {symbol}", "source": [src],
            "data": {"symbol": symbol, "last": last, "atr_d": a, "tfs": tfs, "align": align,
                     "levels": sorted(levels, key=lambda l: -l["price"]),
                     "next_above": above[0] if above else None, "next_below": below[0] if below else None,
                     "at_level": at_level},
            "look_at": f"السعر فوق افتتاح {sum(1 for x in leans if x > 0)} من {len(leans)} فريمات ({word}). "
                       + (f"أقرب مستوى فوق: {above[0]['name']} {_f(above[0]['price'])}. " if above else "")
                       + (f"أقرب مستوى تحت: {below[0]['name']} {_f(below[0]['price'])}. " if below else "")
                       + (f"السعر الآن على مستوى رئيسي: {', '.join(l['name'] for l in at_level)}." if at_level else "")}


# ------------------------------------------------------------------ fibonacci
def _last_leg(df: pd.DataFrame, direction: int, k: int = 5) -> tuple | None:
    """Impulse leg in `direction`: from the last confirmed opposite swing to the extreme after it."""
    highs, lows = swings(df, k)
    if direction > 0 and lows:
        t0, p0 = lows[-1]
        after = df.loc[t0:]
        t1 = after["High"].idxmax()
        return t0, p0, t1, float(after["High"].max())
    if direction < 0 and highs:
        t0, p0 = highs[-1]
        after = df.loc[t0:]
        t1 = after["Low"].idxmin()
        return t0, p0, t1, float(after["Low"].min())
    return None


def fib_tool(symbol: str, direction: int) -> dict:
    h1, src = _px(symbol, "1h")
    df = h1.resample("4h").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna()
    last = float(h1["Close"].iloc[-1])
    leg = _last_leg(df.iloc[-200:], direction)
    if not leg or leg[1] == leg[3]:
        return {"tool": "fib", "title": f"Fibonacci · {symbol}", "source": [src],
                "data": {"symbol": symbol, "ok": False}, "look_at": "لا توجد موجة دافعة واضحة على فريم 4 ساعات."}
    t0, p0, t1, p1 = leg
    span = p1 - p0  # signed: + for an up leg
    retr = {str(r): p1 - r * span for r in FIB_RETRACE}
    ext = {str(e): p0 + e * span for e in FIB_EXT}
    now_r = (p1 - last) / span if span else 0
    ote = sorted([p1 - 0.62 * span, p1 - 0.79 * span])
    pop = sorted([p1 - 0.559 * span, p1 - 0.669 * span])
    in_ote = ote[0] <= last <= ote[1]
    in_pop = pop[0] <= last <= pop[1]
    zone = "discount" if (now_r > 0.5) else "premium"
    good_side = (zone == "discount")  # for the leg's own direction, buying (selling) below (above) 50%
    side = "صاعدة" if direction > 0 else "هابطة"
    return {"tool": "fib", "title": f"Fibonacci · OTE · {symbol}", "source": [src],
            "data": {"symbol": symbol, "ok": True, "direction": direction, "from": p0, "to": p1,
                     "t0": _ts(t0), "t1": _ts(t1), "retrace_now": round(float(now_r), 3),
                     "retrace": retr, "ext": ext, "ote": ote, "pop": pop, "in_ote": bool(in_ote),
                     "in_pop": bool(in_pop), "zone": zone, "good_side": bool(good_side)},
            "look_at": f"آخر موجة {side} على 4 ساعات من {_f(p0)} إلى {_f(p1)}. السعر عند ارتداد {now_r:.0%} "
                       f"({'خصم' if zone == 'discount' else 'علاوة'} بالنسبة للموجة). "
                       f"منطقة OTE بين {_f(ote[0])} و{_f(ote[1])}"
                       + (" والسعر داخلها الآن." if in_ote else ".")
                       + f" أهداف الامتداد: 1.272 عند {_f(ext['1.272'])} و1.618 عند {_f(ext['1.618'])}."}


# ------------------------------------------------------------------ SMC / ICT structure
def _structure(df: pd.DataFrame, k: int = 3) -> list[dict]:
    """Walk bars; a swing is usable k bars after it forms. Close beyond the last unbroken
    swing = BOS if with the current trend, CHoCH (market-structure shift) if against it."""
    h, l, c = df["High"].values, df["Low"].values, df["Close"].values
    events, trend = [], 0
    last_hi = last_lo = None  # (index, price)
    for i in range(2 * k, len(df)):
        j = i - k  # candidate swing bar now confirmed
        if h[j] == h[j - k:j + k + 1].max():
            last_hi = (j, h[j])
        if l[j] == l[j - k:j + k + 1].min():
            last_lo = (j, l[j])
        if last_hi and c[i] > last_hi[1]:
            events.append({"i": i, "kind": "BOS" if trend >= 0 else "CHoCH", "dir": 1,
                           "level": float(last_hi[1]), "from_i": last_lo[0] if last_lo else j})
            trend, last_hi = 1, None
        elif last_lo and c[i] < last_lo[1]:
            events.append({"i": i, "kind": "BOS" if trend <= 0 else "CHoCH", "dir": -1,
                           "level": float(last_lo[1]), "from_i": last_hi[0] if last_hi else j})
            trend, last_lo = -1, None
    return events


def _fvgs(df: pd.DataFrame, a: float) -> list[dict]:
    h, l = df["High"].values, df["Low"].values
    out = []
    for i in range(2, len(df)):
        if l[i] > h[i - 2] and l[i] - h[i - 2] >= 0.2 * a:
            out.append({"i": i, "dir": 1, "top": float(l[i]), "bottom": float(h[i - 2])})
        elif h[i] < l[i - 2] and l[i - 2] - h[i] >= 0.2 * a:
            out.append({"i": i, "dir": -1, "top": float(l[i - 2]), "bottom": float(h[i])})
    for g in out:  # mitigated = later price fully traded back through the gap
        later = df.iloc[g["i"] + 1:]
        g["filled"] = bool((later["Low"] <= g["bottom"]).any() if g["dir"] > 0 else (later["High"] >= g["top"]).any())
    return out


def smc_tool(symbol: str, direction: int) -> dict:
    h1, src = _px(symbol, "1h")
    df = h1.iloc[-300:]
    a = float(atr(df).iloc[-1])
    last = float(df["Close"].iloc[-1])
    o, c = df["Open"].values, df["Close"].values
    ev = _structure(df)
    last_ev = ev[-1] if ev else None
    # Order block for the last break in `direction`: last opposite candle before the impulse.
    ob = None
    brk = next((e for e in reversed(ev) if e["dir"] == direction), None)
    if brk:
        for i in range(brk["i"], max(brk["from_i"] - 1, 0), -1):
            if (direction > 0 and c[i] < o[i]) or (direction < 0 and c[i] > o[i]):
                ob = {"i": i, "top": float(df["High"].iloc[i]), "bottom": float(df["Low"].iloc[i]),
                      "kind": brk["kind"]}
                break
        if ob:
            after = df.iloc[ob["i"] + 1:]
            ob["tested"] = bool(((after["Low"] <= ob["top"]) & (after.index > df.index[brk["i"]])).any()) if direction > 0 \
                else bool(((after["High"] >= ob["bottom"]) & (after.index > df.index[brk["i"]])).any())
            ob["inside"] = ob["bottom"] <= last <= ob["top"]
    gaps = _fvgs(df, a)
    open_gaps = [g for g in gaps if not g["filled"]][-6:]
    # Liquidity sweeps in the last 30 bars: wick through a prior swing, close back inside.
    highs, lows = swings(df.iloc[:-1], 3)
    sweeps = []
    for i in range(len(df) - 12, len(df)):
        bar = df.iloc[i]
        prior_l = [p for t, p in lows if t < df.index[i] - pd.Timedelta(hours=3)]
        prior_h = [p for t, p in highs if t < df.index[i] - pd.Timedelta(hours=3)]
        if prior_l and bar["Low"] < prior_l[-1] < bar["Close"]:
            sweeps.append({"i": i, "dir": 1, "level": prior_l[-1]})
        if prior_h and bar["High"] > prior_h[-1] > bar["Close"]:
            sweeps.append({"i": i, "dir": -1, "level": prior_h[-1]})
    # Equal highs / lows = resting liquidity (where stops cluster): the draw on liquidity.
    def pools(pts, side):
        out = []
        for x in range(len(pts)):
            for y in range(x + 1, len(pts)):
                if abs(pts[x][1] - pts[y][1]) <= 0.1 * a:
                    out.append({"side": side, "price": float(max(pts[x][1], pts[y][1]) if side == "buy" else min(pts[x][1], pts[y][1]))})
        return out
    liq = pools(highs[-8:], "buy") + pools(lows[-8:], "sell")
    draw = None
    if direction > 0:
        tgt = sorted([p["price"] for p in liq if p["side"] == "buy" and p["price"] > last] + [p for _, p in highs[-6:] if p > last])
        draw = tgt[0] if tgt else None
    else:
        tgt = sorted([p["price"] for p in liq if p["side"] == "sell" and p["price"] < last] + [p for _, p in lows[-6:] if p < last], reverse=True)
        draw = tgt[0] if tgt else None
    recent_sweep = next((s for s in reversed(sweeps) if s["dir"] == direction), None)
    mss = brk is not None and brk["kind"] == "CHoCH" and brk["i"] >= len(df) - 40
    fvg_dir = [g for g in open_gaps if g["dir"] == direction]
    unicorn = bool(mss and recent_sweep and ob and any(g["bottom"] <= ob["top"] and g["top"] >= ob["bottom"] for g in fvg_dir))
    in_fvg = any(g["bottom"] <= last <= g["top"] for g in fvg_dir)

    t = [int(x.timestamp()) for x in df.index]
    markers = [{"time": t[e["i"]], "kind": e["kind"], "dir": e["dir"], "level": e["level"]} for e in ev[-6:]]
    markers += [{"time": t[s["i"]], "kind": "Sweep", "dir": s["dir"], "level": s["level"]} for s in sweeps[-4:]]
    e9, e21 = ema(df["Close"], 9), ema(df["Close"], 21)
    chart = {"t": t[-160:], "o": df["Open"].iloc[-160:].tolist(), "h": df["High"].iloc[-160:].tolist(),
             "l": df["Low"].iloc[-160:].tolist(), "c": df["Close"].iloc[-160:].tolist(),
             "ema9": e9.iloc[-160:].tolist(), "ema21": e21.iloc[-160:].tolist()}
    trend_word = {1: "صاعد", -1: "هابط"}.get(last_ev["dir"] if last_ev else 0, "غير محدد")
    look = (f"الهيكل الساعي {trend_word}" + (f"، آخر حدث {last_ev['kind']} عند {_f(last_ev['level'])}" if last_ev else "") + ". ")
    if ob:
        look += f"Order Block ({ob['kind']}) بين {_f(ob['bottom'])} و{_f(ob['top'])}{' والسعر داخله' if ob['inside'] else ''}. "
    if fvg_dir:
        look += f"{len(fvg_dir)} فجوة FVG مفتوحة في اتجاهنا. "
    if recent_sweep:
        look += f"سحب سيولة عند {_f(recent_sweep['level'])}. "
    if draw is not None:
        look += f"هدف السيولة التالي (Draw on Liquidity) عند {_f(draw)}. "
    if unicorn:
        look += "نموذج Unicorn مكتمل: سحب سيولة + تغيّر هيكل + FVG فوق Order Block."
    return {"tool": "smc", "title": f"Structure · SMC/ICT · {symbol}", "source": [src],
            "data": {"symbol": symbol, "direction": direction, "atr": a, "last": last,
                     "last_event": last_ev and {k: last_ev[k] for k in ("kind", "dir", "level")},
                     "with_trend": bool(last_ev and last_ev["dir"] == direction),
                     "mss": bool(mss), "order_block": ob, "fvgs": [{k: g[k] for k in ("dir", "top", "bottom")} | {"time": t[g["i"]]} for g in open_gaps],
                     "in_fvg": bool(in_fvg), "sweep": recent_sweep and {"level": recent_sweep["level"], "time": t[recent_sweep["i"]]},
                     "liquidity": liq[-6:], "draw": draw, "unicorn": unicorn, "markers": markers, "chart": chart},
            "look_at": look.strip()}


# ------------------------------------------------------------------ technical confirmation
def tech_tool(symbol: str, direction: int) -> dict:
    h1, src = _px(symbol, "1h")
    df = h1.iloc[-400:].copy()
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    vol = df["Volume"].astype(float)
    real_vol = bool(vol.sum() > 0)
    w = vol if real_vol else pd.Series(1.0, index=df.index)  # FX on Yahoo has no volume → TWAP proxy
    day = df.index.floor("D")
    vwap = (tp * w).groupby(day).cumsum() / w.groupby(day).cumsum()
    e9, e21 = ema(df["Close"], 9), ema(df["Close"], 21)
    last = float(df["Close"].iloc[-1])
    v_side = 1 if last > vwap.iloc[-1] else -1
    e_side = 1 if e9.iloc[-1] > e21.iloc[-1] else -1
    p_side = 1 if last > e9.iloc[-1] else -1
    agree = sum(1 for s in (v_side, e_side, p_side) if s == direction)
    name = "VWAP" if real_vol else "VWAP≈TWAP"
    return {"tool": "tech", "title": f"Technical · EMA9/21 + {name} · {symbol}", "source": [src],
            "data": {"symbol": symbol, "direction": direction, "vwap": float(vwap.iloc[-1]), "ema9": float(e9.iloc[-1]),
                     "ema21": float(e21.iloc[-1]), "vwap_side": v_side, "ema_side": e_side, "price_side": p_side,
                     "agree": agree, "real_volume": real_vol},
            "look_at": f"السعر {'فوق' if v_side > 0 else 'تحت'} {name} اليومي ({_f(float(vwap.iloc[-1]))}) "
                       f"و EMA9 {'فوق' if e_side > 0 else 'تحت'} EMA21. {agree} من 3 إشارات توافق الاتجاه. "
                       + ("" if real_vol else "ياهو لا يعطي حجماً للعملات، فالـ VWAP هنا متوسط زمني تقريبي.")}


# ------------------------------------------------------------------ intermarket SMT
def _hl_pair(df: pd.DataFrame) -> tuple:
    highs, lows = swings(df.iloc[-120:], 3)
    return highs[-2:], lows[-2:]


def smt_tool() -> dict:
    rows, srcs = [], set()
    for a, b, sign in SMT_PAIRS:
        da, sa = _px(a, "1h")
        db, sb = _px(b, "1h")
        srcs |= {sa, sb}
        (ha, la), (hb, lb) = _hl_pair(da), _hl_pair(db)
        if len(ha) < 2 or len(hb) < 2 or len(la) < 2 or len(lb) < 2:
            continue
        near = lambda x, y: abs((x[1][0] - y[1][0]).total_seconds()) <= 5 * 3600  # same swing on both charts
        a_hh, a_ll = ha[1][1] > ha[0][1], la[1][1] < la[0][1]
        b_hh, b_ll = hb[1][1] > hb[0][1], lb[1][1] < lb[0][1]
        if sign < 0:  # inverse pair: B's lows behave like A's highs
            b_hh, b_ll = lb[1][1] < lb[0][1], hb[1][1] > hb[0][1]
        sig = 0
        hi_pair, lo_pair = (ha, hb) if sign > 0 else (ha, lb), (la, lb) if sign > 0 else (la, hb)
        if a_hh != b_hh and near(*hi_pair):
            sig = -1  # one makes a higher high, the other fails: bearish SMT
        elif a_ll != b_ll and near(*lo_pair):
            sig = 1   # one makes a lower low, the other holds: bullish SMT
        rows.append({"a": a, "b": b, "sign": sign, "signal": sig,
                     "text": {1: "SMT صاعد: واحد كسر القاع والآخر لم يكسر", -1: "SMT هابط: واحد كسر القمة والآخر فشل",
                              0: "متوافقان، لا تباعد"}[sig]})
    hits = [r for r in rows if r["signal"]]
    return {"tool": "smt", "title": "Intermarket · SMT Divergence", "source": sorted(srcs),
            "data": {"rows": rows},
            "look_at": ("تباعد SMT على: " + "، ".join(f"{r['a']}/{r['b']} ({'صاعد' if r['signal'] > 0 else 'هابط'})" for r in hits)
                        + ". التباعد يحذر من أن الكسر الأخير قد يكون مصيدة سيولة.") if hits else
                       "لا تباعد SMT بين الأسواق المترابطة الآن."}


def smt_for(symbol: str, smt: dict) -> int:
    """SMT signal relevant to `symbol` (sign-adjusted for the B leg of inverse pairs)."""
    for r in smt["data"]["rows"]:
        if symbol == r["a"]:
            return r["signal"]
        if symbol == r["b"]:
            return r["signal"] * r["sign"]
    return 0


# ------------------------------------------------------------------ scenarios
def scenarios(symbol: str, direction: int, td: dict, smc: dict, fib: dict) -> dict:
    """Two or three concrete if/then plans at the key level, decided before price gets there."""
    d = smc["data"]
    a, last = d["atr"], d["last"]
    cands = []
    if d.get("order_block"):
        cands.append(("Order Block", (d["order_block"]["top"] + d["order_block"]["bottom"]) / 2))
    if fib["data"].get("ok"):
        cands.append(("OTE", sum(fib["data"]["ote"]) / 2))
    lv = td["data"]["next_below"] if direction > 0 else td["data"]["next_above"]
    if lv:
        cands.append((lv["name"], lv["price"]))
    if not cands:
        cands.append(("EMA21", last - direction * a))
    name, level = min(cands, key=lambda x: abs(x[1] - last))
    buf = 0.25 * a
    tgt = d.get("draw") or (last + direction * 2 * a)
    s = "شراء" if direction > 0 else "بيع"
    opp = "بيع" if direction > 0 else "شراء"
    under = "تحت" if direction > 0 else "فوق"
    over = "فوق" if direction > 0 else "تحت"
    plans = [
        {"name": "يصمد ويرتد", "if": f"السعر يلمس {name} ({_f(level)}) ويغلق شمعة ساعة {over}ه مع امتصاص واضح",
         "then": f"{s} عند تأكيد الشمعة، وقف {under} {_f(level - direction * buf)}، هدف السيولة {_f(tgt)}",
         "invalid": f"إغلاق ساعة {under} {_f(level - direction * buf)}"},
        {"name": "يكسر ويكمل", "if": f"إغلاق ساعة {under} {_f(level - direction * buf)} بزخم وحجم",
         "then": f"لا {s}. الفكرة الأصلية سقطت. ننتظر إعادة اختبار المستوى من الجهة الأخرى لفكرة {opp} أو نقف جانباً",
         "invalid": "—"},
        {"name": "مصيدة ثم انعكاس", "if": f"ذيل يخترق {name} لسحب الوقف ثم يغلق {over}ه مرة أخرى (Sweep + Reclaim)",
         "then": f"أقوى دخول {s}: الوقف {under} طرف الذيل، الهدف {_f(tgt)} ثم السيولة التالية",
         "invalid": f"إغلاق ثاني {under} طرف الذيل"},
    ]
    return {"tool": "scenarios", "title": f"Scenarios · السيناريوهات · {symbol}", "source": smc["source"],
            "data": {"symbol": symbol, "direction": direction, "level_name": name, "level": level, "target": tgt, "plans": plans},
            "look_at": f"المستوى المحوري الآن هو {name} عند {_f(level)}. حدد مسبقاً ماذا ستفعل في كل سيناريو، "
                       "ولا تدخل إلا بعد أن يؤكد الشارت واحداً منها."}


# ------------------------------------------------------------------ watchlist engine
def _reasons(symbol: str, direction: int, td: dict, fib: dict, smc: dict, tech: dict,
             smt_sig: int, blocked: list[str], bias: dict | None, of: dict | None) -> list[dict]:
    """Each reason: department, text, weight. Confluence (2–3 tools agreeing) weighs more."""
    R = []
    add = lambda dept, text, w=1.0: R.append({"dept": dept, "text": text, "w": w})
    tdd, fd, sd, te = td["data"], fib["data"], smc["data"], tech["data"]
    m = UNIVERSE[symbol]
    # 1 price action & structure
    if tdd["align"] * direction >= 2:
        add("price_action", f"Top-down متوافق ({tdd['align']:+d}/4)", 1.0 if tdd["align"] * direction >= 4 else 0.5)
    if tdd["at_level"]:
        add("price_action", f"على مستوى فريم أعلى: {', '.join(l['name'] for l in tdd['at_level'])}")
    if fd.get("ok") and fd["in_ote"]:
        w = 1.5 if (tdd["at_level"] or (sd.get("order_block") or {}).get("inside")) else 1.0
        add("price_action", "داخل منطقة OTE" + (" ومتداخلة مع مستوى/OB" if w > 1 else ""), w)
    elif fd.get("ok") and fd["good_side"]:
        add("price_action", "السعر في منطقة الخصم من الموجة", 0.5)
    if sd["with_trend"]:
        add("price_action", f"هيكل الساعة {sd['last_event']['kind']} في اتجاهنا")
    if (sd.get("order_block") or {}).get("inside"):
        add("price_action", "السعر داخل Order Block")
    if sd["sweep"]:
        add("price_action", "سحب سيولة ثم عودة (Sweep)", 1.5 if sd["mss"] else 1.0)
    if sd["unicorn"]:
        add("price_action", "نموذج ICT Unicorn مكتمل", 2.0)
    if smt_sig == direction:
        add("price_action", "تباعد SMT يدعم الاتجاه")
    # 2 technical (confirmation only)
    if te["agree"] == 3:
        add("technical", "EMA9/21 والـ VWAP كلها متوافقة", 1.5)
    elif te["agree"] == 2:
        add("technical", "إشارتان فنيتان من 3 متوافقتان", 0.5)
    # macro desk (the Prime-style layer we already have)
    if bias and bias["score"] * direction >= GATE["min_bias"]:
        add("macro", f"الانحياز المركب {bias['label']} ({bias['score']:+.2f})", 1.5 if abs(bias["score"]) > 0.5 else 1.0)
    elif bias and bias["score"] * direction <= -GATE["min_bias"]:
        add("macro", f"الانحياز المركب ضد الاتجاه ({bias['score']:+.2f})", -1.0)
    # 3 news & catalysts
    if any(c in blocked for c in (m["base"], m["quote"])):
        add("news", "خبر عالي التأثير خلال 12 ساعة: لا دخول قبله", -2.0)
    # order flow (crypto only, counts inside the departments, per the framework)
    if of and of["data"].get("ok"):
        o = of["data"]
        if o["delta_bias"] * direction > 0:
            add("order_flow", f"الـ Delta التراكمي في اتجاهنا ({o['cvd_pct']:+.0f}%)")
        if o.get("absorption") and o["absorption"]["dir"] == direction:
            add("order_flow", "امتصاص عند المستوى (Absorption)", 1.5)
    return R


def score_direction(symbol: str, direction: int, smt: dict, blocked: list[str], bias: dict | None,
                    of: dict | None = None, td: dict | None = None) -> dict:
    td = td or topdown_tool(symbol)
    fib, smc, tech = fib_tool(symbol, direction), smc_tool(symbol, direction), tech_tool(symbol, direction)
    R = _reasons(symbol, direction, td, fib, smc, tech, smt_for(symbol, smt), blocked, bias, of)
    pos = [r for r in R if r["w"] > 0]
    score = sum(r["w"] for r in R)
    depts = sorted({r["dept"] for r in pos})
    stars = sum(score >= t for t in (1, 2.5, 4, 5.5, 7))
    tools = {"topdown": td, "fib": fib, "smc": smc, "tech": tech}
    return {"symbol": symbol, "direction": direction, "score": round(score, 2), "stars": stars,
            "reasons": R, "departments": depts, "count": len(pos),
            "promoted": len(pos) >= WATCH_MIN_REASONS and len(depts) >= 2 and score >= 4 and "price_action" in depts,
            "blocked": any(r["w"] < 0 for r in R), "last": smc["data"]["last"], "_tools": tools,
            "source": sorted({x for t in tools.values() for x in t["source"]} | set((of or {}).get("source", [])))}


def watchlist_row(symbol: str, smt: dict, blocked: list[str], bias: dict | None, of: dict | None = None) -> dict:
    """Score both directions and keep the stronger one."""
    td = topdown_tool(symbol)
    rows = [score_direction(symbol, d, smt, blocked, bias, of, td) for d in (1, -1)]
    return max(rows, key=lambda r: r["score"])
