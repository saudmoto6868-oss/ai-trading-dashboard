"""HORIZONS: the same confluence idea as the Day plan, for every holding time (owner 2026-11-06: scalp / day / swing / position, every 4 hours, all schools, A+ setups).

Each horizon has its own timeframe chain: the BIAS comes from the two higher timeframes (they must agree), the TRIGGER is a lower timeframe whose scanner direction matches.
  scalp     bias 4H + 1H   triggers 15m / 5m   fixed exits (stop + first target stay)
  day       bias 1D + 4H   triggers 1H / 15m / 5m   partial + trail (day_plan.build, unchanged)
  swing     bias 1W + 1D   triggers 4H / 1D         partial + wide trail (2.5 ATR), days to weeks
  position  bias 1W (+1M not available) + 1D   trigger 1D / 1W   partial + wide trail (3 ATR), weeks to months
GRADE (a count of agreeing evidence, never a probability): A+ = >= 4 distinct schools AND bias agreeing AND R:R to TP1 >= 2 AND not choppy; A = >= 3 schools AND R:R >= 1.5; the rest are B and are not sent.
Honest limits: untested as a whole (n = 0 graded); the grade is evidence counting; the 1W chain depends on the data source returning weekly candles (a missing frame just drops that symbol)."""
from __future__ import annotations

import os

HORIZONS = {
    "scalp":    {"bias": ("4h", "1h"), "triggers": ("15m", "5m"), "chain": ("4h", "1h", "15m", "5m"), "style": "fixed",   "trail": None, "min_agree": 3},
    "swing":    {"bias": ("1w", "1d"), "triggers": ("4h", "1d"),  "chain": ("1w", "1d", "4h"),          "style": "trail",   "trail": 2.5, "min_agree": 3},
    "position": {"bias": ("1w", "1d"), "triggers": ("1d", "1w"),  "chain": ("1w", "1d"),                "style": "trail",   "trail": 3.0, "min_agree": 2},
}
ALL = ("scalp", "day", "swing", "position")


def grade_of(n_schools: int, rr1: float, bias_ok: bool, choppy: bool = False) -> str:
    if bias_ok and n_schools >= 4 and rr1 >= 2 and not choppy:
        return "A+"
    if bias_ok and n_schools >= 3 and rr1 >= 1.5:
        return "A"
    return "B"


def _chain_bias(views: dict, bias_tfs):
    ds = [views[t]["dir"] for t in bias_tfs if views.get(t) and views[t]["dir"] != "neutral"]
    if len(ds) == len(bias_tfs) and len(set(ds)) == 1:
        return ds[0]
    return None


def build(symbol: str, frames: dict, horizon: str, clock=None, choppy: bool = False, min_stars: int = 2) -> list:
    from modules import day_plan as dp
    if horizon == "day":
        plans = dp.build(symbol, frames, mode="conf", clock=clock)
        for p in plans:
            p["horizon"] = "day"
            p["grade"] = grade_of(len(p["schools"]), p["rr1"], True, choppy)
        return plans
    cfg = HORIZONS[horizon]
    views = {tf: dp.tf_view(frames.get(tf), tf) for tf in cfg["chain"]}
    views = {k: v for k, v in views.items() if v}
    bias = _chain_bias(views, cfg["bias"])
    if not bias:
        return []
    out = []
    for tf in cfg["triggers"]:
        v = views.get(tf)
        if not v or v["dir"] != bias or v["stars"] < min_stars:
            continue
        agree = [t for t in cfg["chain"] if views.get(t) and views[t]["dir"] == bias]
        if len(agree) < cfg["min_agree"]:
            continue
        pl = dp._plan(v, bias)
        pt = dp.point_size(symbol, v["price"])
        risk = abs(pl["entry"] - pl["stop_loss"])
        if risk <= 0:
            continue
        tps = pl["take_profits"]
        rr1 = abs(tps[0] - pl["entry"]) / risk
        sch = dp.schools_of(v["signals"])
        if cfg["style"] == "fixed":
            ex = dp.exit_plan(pl, "scalp", v["atr"], pt)
            last = tps[0]
        else:
            ex = dp.exit_plan(pl, "conf", v["atr"], pt)
            if v["atr"]:
                ex["trail_atr"] = cfg["trail"]
                ex["text_en"] = ex["text_en"].replace(str(dp.TRAIL_ATR), str(cfg["trail"]))
                ex["text_ar"] = ex["text_ar"].replace(str(dp.TRAIL_ATR), str(cfg["trail"]))
            last = tps[-1]
        move = abs(last - pl["entry"]) / pt
        out.append({"id": f"plan|{symbol}|{bias}|{tf}|{horizon}", "symbol": symbol, "mode": horizon, "horizon": horizon, "tf": tf, "direction": bias, "stars": v["stars"], "price": v["price"],
                    "entry": pl["entry"], "stop": pl["stop_loss"], "tps": tps, "risk_points": round(risk / pt), "move_points": round(move), "rr1": round(rr1, 2), "point": pt,
                    "confluence": {"bias": bias, "bias_strength": len(cfg["bias"]), "agree": agree, "n": len(agree), "of": len(cfg["chain"]), "views": {t: views[t]["dir"] for t in views}},
                    "schools": sch, "reasons": [f"{s.get('icon', '')} {s['name']}" for s in v["signals"][:6]], "keys": [s.get("key") for s in v["signals"]],
                    "exit": ex, "atr": v["atr"], "session": clock, "t": str(v["time"]), "grade": grade_of(len(sch), rr1, True, choppy)})
    out.sort(key=lambda p: (p["grade"] != "A+", -len(p["schools"]), -p["rr1"]))
    return out


def scan(symbols, fetch, horizons=ALL, min_grade: str = "A", calm: dict | None = None) -> list:
    """Every horizon for every symbol, only plans graded >= min_grade (A+ > A). calm = {symbol: calm_stats} to mark choppy."""
    from modules import day_plan as dp
    from modules.daily_top import CALM_ER
    need = {"A+": ("A+",), "A": ("A+", "A"), "B": ("A+", "A", "B")}[min_grade]
    tfs = sorted({t for h in horizons for t in (("1d", "4h", "1h", "15m", "5m") if h == "day" else HORIZONS[h]["chain"])})
    clock = dp.session_clock()
    res = []
    for sym in symbols:
        frames = {}
        for tf in tfs:
            try:
                frames[tf] = fetch(sym, tf)
            except Exception:
                frames[tf] = None
        c = (calm or {}).get(sym)
        choppy = bool(c and c["er"] < CALM_ER)
        for h in horizons:
            try:
                res += [p for p in build(sym, frames, h, clock, choppy) if p["grade"] in need]
            except Exception:
                continue
    res.sort(key=lambda p: (p["grade"] != "A+", -len(p["schools"]), -p["rr1"]))
    return res


def sizing(p: dict, equity: float | None = None) -> dict | None:
    """Position size under the shared desk policy: 0.25% base; 0.50% only for validated A+ with >=30 OOS trades.
    Equity = env / secret DESK_EQUITY (default 10 000). Units = the instrument's price units (spot coins, perp contracts in USD);
    futures with a point value other than 1 need their own multiplier. None when the plan has no usable stop."""
    from modules import desk_risk as DR
    try:
        eq = float(equity if equity is not None else os.environ.get("DESK_EQUITY") or 10000)
        s = DR.position_size(eq, float(p["entry"]), float(p["stop"]),
                             grade=p.get("grade"), validation_n=p.get("validation_n", 0),
                             validation_passed=p.get("validation_passed") is True)
    except (KeyError, TypeError, ValueError):
        return None
    return {"equity": eq, "risk_pct": s["risk_pct"], "qty": s["qty"], "risk_amount": s["risk_amount"]}


HNAME = {"scalp": ("scalp", "سكالب"), "day": ("day trade", "دي تريد"), "swing": ("swing", "سوينج"), "position": ("position", "بوزيشن")}


def format_plan(p: dict, ar: bool = True) -> str:
    import html
    esc = html.escape
    up = p["direction"] == "bullish"
    h = HNAME[p["horizon"]][1 if ar else 0]
    ex = p["exit"]
    sz = sizing(p)
    szl = (f"{'الحجم' if ar else 'Size'} {sz['qty']:.4g} · {'مخاطرة' if ar else 'risk'} {sz['risk_amount']:,.0f}$ = {sz['risk_pct']}% {'من' if ar else 'of'} {sz['equity']:,.0f}$\n") if sz and sz["qty"] > 0 else ""
    return (f"{'⭐' if p['grade'] == 'A+' else '✅'} <b>{p['grade']} · {h}</b> {'🟢' if up else '🔴'} <b>{esc(p['symbol'])}</b> {('شراء' if up else 'بيع') if ar else ('BUY' if up else 'SELL')} · {p['tf'].upper()}\n"
            f"{'دخول' if ar else 'Entry'} {p['entry']} · {'وقف' if ar else 'Stop'} {p['stop']} · {'أهداف' if ar else 'Targets'} {' / '.join(str(x) for x in p['tps'])} · {'حركة' if ar else 'move'} {p['move_points']} {'نقطة' if ar else 'pts'} · R:R 1:{p['rr1']}\n"
            f"{len(p['schools'])} {'مدارس' if ar else 'schools'}: {esc(', '.join(p['schools'][:5]))} · {p['confluence']['n']}/{p['confluence']['of']} {'فريمات متفقة' if ar else 'timeframes agree'}\n"
            + szl +
            f"<i>{esc(ex['text_ar'] if ar else ex['text_en'])}</i>")


def format_digest(plans, ar: bool = True, limit: int = 8) -> str:
    head = f"🔭 <b>{'مسح كل الآفاق (كل 4 ساعات)' if ar else 'All-horizon scan (every 4 h)'}</b>"
    if not plans:
        return head + ("\nمفيش A أو A+ دلوقتي." if ar else "\nNo A or A+ right now.")
    body = "\n\n".join(format_plan(p, ar) for p in plans[:limit])
    foot = "\n\n<i>الدرجة = عدد أدلة متفقة (مدارس + فريمات + R:R) مش نسبة نجاح. غير مختبرة ككل. مش نصيحة مالية.</i>" if ar else "\n\n<i>Grade = count of agreeing evidence, not a win rate. Untested as a whole. Not financial advice.</i>"
    return (head + "\n\n" + body + foot)[:3900]
