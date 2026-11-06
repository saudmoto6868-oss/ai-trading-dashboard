"""DAY PLAN: today's trades by session and by timeframe CONFLUENCE (owner 2026-11-06).

Standard mode "conf": the higher timeframes (1D + 4H) give the BIAS, the trigger timeframes (1H / 15m / 5m) give the entry, and a trade is listed only when several timeframes of the
chain 1D > 4H > 1H > 15m > 5m point the same way. Option mode "scalp": one trigger timeframe you choose (default 5m), fixed stop and target (no trailing, no partials), the higher timeframe
only has to not argue. Both modes can be limited to one school (Elliott, SMC / ICT, Price action, Wyckoff, Harmonic ... whatever the detectors found) and to a minimum expected move in POINTS.

Everything is built from detectors the platform already has (signals.py via scorer.cached_detect / aggregate) and its own trade-plan builder (risk_engine.build_trade_plan). Nothing here is
a win rate: the stars are the scanner's evidence count, new detectors are context only until the lab measures them (n >= 30), and a plan is a plan, not advice.

Exits ("exit_plan" / "simulate_exit"):
  conf  : 50 % off at TP1, stop to break-even once the trade is +min(1R, trail_start_points), then a trailing stop 1.5 ATR behind the best price for the runner, final target TP3.
          "If it passes 100 points and is still running, the stop moves."
  scalp : fixed stop, one target (TP1), nothing moves (optional break-even at 1R).
"""
from __future__ import annotations

import math
from datetime import datetime

import pandas as pd

CHAIN = ("1d", "4h", "1h", "15m", "5m")
CONF_TRIGGERS = ("1h", "15m", "5m")
MIN_CHAIN_AGREE = 3          # of the 5 timeframes (one of them 1D / 4H, one a trigger timeframe)
TRAIL_ATR = 1.5
POINT_CHOICES = (100, 150, 200, 300, 1000)

# 1 point of each instrument in price units (MT5-style: gold 0.1 = one pip, forex pip, indices / BTC = 1). Override with the env POINT_SIZES='{"BTC-USDT": 1}'.
POINTS = {
    "HL:xyz:GOLD": 0.1, "Y:GC=F": 0.1, "HL:xyz:SILVER": 0.01, "Y:SI=F": 0.01, "HL:xyz:CL": 0.01, "HL:xyz:BRENTOIL": 0.01,
    "HL:xyz:SP500": 1.0, "HL:xyz:XYZ100": 1.0, "Y:^GSPC": 1.0, "Y:^IXIC": 1.0, "Y:^NDX": 1.0, "Y:^DJI": 1.0,
    "BTC-USDT": 1.0, "ETH-USDT": 0.1,
}


def point_size(symbol: str, price: float | None = None) -> float:
    try:
        import json
        import os
        ov = json.loads(os.environ.get("POINT_SIZES", "{}") or "{}")
        if symbol in ov:
            return float(ov[symbol])
    except Exception:
        pass
    if symbol in POINTS:
        return POINTS[symbol]
    if symbol.startswith("Y:") and symbol.endswith("=X"):   # forex: a pip (JPY pairs 0.01)
        return 0.01 if "JPY" in symbol else 0.0001
    if price and price > 0:                                 # unknown instrument: 5 significant digits of the price
        return 10 ** (math.floor(math.log10(price)) - 4)
    return 1.0


# ---------------------------------------------------------------- sessions (New York clock: the same bands the Workspace draws)
SESSIONS = {"Asia": (19 * 60, 28 * 60), "London": (3 * 60, 12 * 60), "New York": (8 * 60, 17 * 60)}
KILL_ZONES = {"Asia KZ": (20 * 60, 24 * 60), "London Open KZ": (2 * 60, 5 * 60), "NY AM KZ": (7 * 60, 10 * 60), "NY PM KZ": (13 * 60 + 30, 16 * 60)}


def _ny_minutes(ts) -> tuple[int, pd.Timestamp]:
    t = pd.Timestamp(ts)
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    h = t.tz_convert("America/New_York")
    return h.hour * 60 + h.minute, h


def _inside(m, lo, hi):
    return lo <= m < hi or lo <= m + 1440 < hi


def session_clock(now=None) -> dict:
    """{'active': [...], 'kill_zone': name|None, 'next_kz': name, 'next_kz_in_min': int} for a moment (default now)."""
    m, h = _ny_minutes(now or datetime.utcnow())
    active = [n for n, (a, b) in SESSIONS.items() if _inside(m, a, b)]
    kz = next((n for n, (a, b) in KILL_ZONES.items() if _inside(m, a, b)), None)
    best = None
    for n, (a, _b) in KILL_ZONES.items():
        wait = (a - m) % 1440
        if wait and (best is None or wait < best[1]):
            best = (n, wait)
    return {"active": active, "kill_zone": kz, "next_kz": best[0] if best else None, "next_kz_in_min": best[1] if best else None, "ny_time": h.strftime("%H:%M")}


def session_label(clock: dict, ar: bool = False) -> str:
    if clock["kill_zone"]:
        return ("الآن: " if ar else "NOW: ") + clock["kill_zone"]
    nxt = clock.get("next_kz")
    if nxt is None:
        return "-"
    mins = clock["next_kz_in_min"]
    return (f"التالي: {nxt} بعد {mins // 60}س {mins % 60}د" if ar else f"NEXT: {nxt} in {mins // 60}h {mins % 60}m")


# ---------------------------------------------------------------- analysis
_SCHOOL_BY_FAMILY = {"Elliott": "Elliott wave", "MA": "Trend (MA)", "VWAP": "Trend (MA)", "TL": "Levels / breakouts", "Unicorn": "SMC / ICT", "MSB-OB": "SMC / ICT", "Fib": "Fibonacci", "Liquidity": "Liquidity"}


def schools_of(signals) -> list:
    try:
        from modules.strategy_lab import SCHOOL
    except Exception:
        SCHOOL = {}
    out = []
    for s in signals:
        nm = SCHOOL.get(s.get("key")) or _SCHOOL_BY_FAMILY.get(s.get("family"))
        if nm and nm not in out:
            out.append(nm)
    return out


def tf_view(df, tf):
    """One timeframe: the scanner's direction, stars and the signals on that side (never raises)."""
    from modules.scorer import aggregate, cached_detect
    from modules.signals import atr_series, sr_levels
    if df is None or len(df) < 60:
        return None
    sigs, _ = cached_detect(df)
    agg = aggregate(sigs)
    d = agg["direction"]
    mine = [s for s in sigs if s["direction"] == d] if d != "neutral" else []
    res, sup = sr_levels(df)
    a = float(atr_series(df, 14).iloc[-1])
    return {"tf": tf, "dir": d, "stars": agg["stars"], "signals": mine, "price": float(df["close"].iloc[-1]), "atr": a if a == a and a > 0 else None,
            "supports": sup, "resistances": res, "time": df["time"].iloc[-1]}


def htf_bias(views: dict):
    """(direction or None, strength 0-2) from 1D and 4H: both agree = 2, one of them with the other undecided = 1, conflict or nothing = (None, 0)."""
    ds = [views[t]["dir"] for t in ("1d", "4h") if views.get(t) and views[t]["dir"] != "neutral"]
    if not ds or len(set(ds)) > 1:
        return None, 0
    return ds[0], len(ds)


def _plan(view, direction):
    from modules.risk_engine import build_trade_plan
    pl = build_trade_plan({"price": view["price"], "trend_bias": direction, "supports": view["supports"], "resistances": view["resistances"], "signals": view["signals"], "atr": view["atr"]})
    return pl


def exit_plan(plan: dict, mode: str, atr: float | None, point: float, trail_start_points: float = 100, be_at_1r_scalp: bool = False) -> dict:
    r = abs(plan["entry"] - plan["stop_loss"])
    if mode == "scalp":
        return {"style": "fixed", "stop": plan["stop_loss"], "targets": [plan["take_profits"][0]], "partial": None, "be_at": (r if be_at_1r_scalp else None), "trail_atr": None,
                "text_en": "Fixed: stop and the first target stay where they are." + (" Stop to break-even at +1R." if be_at_1r_scalp else ""),
                "text_ar": "ثابت: الوقف والهدف الأول زي ما هم." + (" الوقف للتعادل عند +1R." if be_at_1r_scalp else "")}
    be_at = min(r, trail_start_points * point) if r > 0 else None
    return {"style": "partial+trail", "stop": plan["stop_loss"], "targets": list(plan["take_profits"]), "partial": {"at": plan["take_profits"][0], "fraction": 0.5}, "be_at": be_at,
            "trail_atr": TRAIL_ATR if atr else None,
            "text_en": f"50% off at TP1 ({plan['take_profits'][0]}). Stop to break-even once +{round((be_at or 0) / point)} points (or +1R, whichever comes first), then a trailing stop {TRAIL_ATR} ATR behind the best price for the runner; final target TP3.",
            "text_ar": f"نص الكمية عند TP1 ({plan['take_profits'][0]}). الوقف للتعادل أول ما الصفقة تعدي +{round((be_at or 0) / point)} نقطة (أو +1R أيهما الأول)، وبعدها وقف متحرك {TRAIL_ATR} ATR ورا أحسن سعر للجزء الباقي، والهدف الأخير TP3."}


def simulate_exit(bars: pd.DataFrame, direction: str, entry: float, stop: float, ex: dict, atr: float | None = None) -> dict:
    """Walk `bars` (candles AFTER the entry) with the exit rules of `ex` (exit_plan). Conservative: a candle that touches the stop and a target uses the stop first.
    -> {'r': total R of the whole position, 'events': [...], 'closed': bool}"""
    long = direction in ("bullish", "Long", "long")
    sg = 1 if long else -1
    r0 = abs(entry - stop)
    if r0 <= 0:
        return {"r": 0.0, "events": [], "closed": False}
    tps = ex["targets"]
    part = ex.get("partial")
    pos, real, stop_cur, extreme = 1.0, 0.0, stop, entry
    be_done, tp1_done, events = False, False, []
    for i, row in enumerate(bars.itertuples(index=False)):
        hi, lo, cl = float(row.high), float(row.low), float(row.close)
        if (lo <= stop_cur) if long else (hi >= stop_cur):
            real += pos * sg * (stop_cur - entry) / r0
            events.append((i, "stop", round(stop_cur, 6)))
            return {"r": round(real, 4), "events": events, "closed": True}
        extreme = max(extreme, hi) if long else min(extreme, lo)
        fav = sg * (extreme - entry)
        if ex.get("be_at") and not be_done and fav >= ex["be_at"]:
            stop_cur = entry
            be_done = True
            events.append((i, "breakeven", entry))
        if part and not tp1_done and ((hi >= part["at"]) if long else (lo <= part["at"])):
            real += part["fraction"] * sg * (part["at"] - entry) / r0
            pos -= part["fraction"]
            tp1_done = True
            stop_cur = max(stop_cur, entry) if long else min(stop_cur, entry)
            events.append((i, "partial", part["at"]))
        if ex.get("trail_atr") and atr and (tp1_done or be_done):
            tr = extreme - sg * ex["trail_atr"] * atr
            stop_cur = max(stop_cur, tr) if long else min(stop_cur, tr)
        last = tps[-1]
        if (hi >= last) if long else (lo <= last):
            real += pos * sg * (last - entry) / r0
            events.append((i, "target", last))
            return {"r": round(real, 4), "events": events, "closed": True}
    if len(bars):
        real += pos * sg * (float(bars["close"].iloc[-1]) - entry) / r0
    return {"r": round(real, 4), "events": events, "closed": False}


def build(symbol: str, frames: dict, mode: str = "conf", trigger_tfs=None, schools=None, min_points: float = 0, min_stars: int = 2, min_rr: float = 1.0,
          trail_start_points: float = 100, clock: dict | None = None) -> list:
    """Plans for ONE symbol. frames = {tf: DataFrame}. Returns a list (possibly empty) of plan dicts, best first."""
    views = {tf: tf_view(frames.get(tf), tf) for tf in CHAIN}
    views = {k: v for k, v in views.items() if v}
    if not views:
        return []
    bias, strength = htf_bias(views)
    trigs = tuple(trigger_tfs) if trigger_tfs else (CONF_TRIGGERS if mode == "conf" else ("5m",))
    clock = clock or session_clock()
    out = []
    for tf in trigs:
        v = views.get(tf)
        if not v or v["dir"] == "neutral" or v["stars"] < min_stars:
            continue
        d = v["dir"]
        agree = [t for t in CHAIN if views.get(t) and views[t]["dir"] == d]
        if mode == "conf":
            if bias != d or len(agree) < MIN_CHAIN_AGREE or not (set(agree) & {"1d", "4h"}):
                continue
        elif bias is not None and bias != d:   # scalp: the higher timeframe may be undecided, it may not argue
            continue
        sch = schools_of(v["signals"])
        if schools and not (set(schools) & set(sch)):
            continue
        pl = _plan(v, d)
        pt = point_size(symbol, v["price"])
        risk = abs(pl["entry"] - pl["stop_loss"])
        if risk <= 0:
            continue
        tps = pl["take_profits"]
        rr1 = abs(tps[0] - pl["entry"]) / risk
        if rr1 < min_rr:
            continue
        last_tp = tps[0] if mode == "scalp" else tps[-1]
        move = abs(last_tp - pl["entry"]) / pt
        if move < min_points:
            continue
        ex = exit_plan(pl, mode, v["atr"], pt, trail_start_points)
        out.append({
            "id": f"plan|{symbol}|{d}|{tf}|{mode}", "symbol": symbol, "mode": mode, "tf": tf, "direction": d, "stars": v["stars"], "price": v["price"],
            "entry": pl["entry"], "stop": pl["stop_loss"], "tps": tps, "book": pl.get("book"), "risk_points": round(risk / pt), "move_points": round(move), "rr1": round(rr1, 2),
            "point": pt, "confluence": {"bias": bias, "bias_strength": strength, "agree": agree, "n": len(agree), "of": len(CHAIN), "views": {t: views[t]["dir"] for t in CHAIN if t in views}},
            "schools": sch, "reasons": [f"{s.get('icon', '')} {s['name']}" for s in v["signals"][:6]], "keys": [s.get("key") for s in v["signals"]],
            "exit": ex, "session": clock, "t": str(v["time"]),
        })
    out.sort(key=lambda p: (-p["confluence"]["n"], -p["stars"], -p["rr1"]))
    return out


def scan(symbols, fetch, mode: str = "conf", **kw) -> list:
    """fetch(symbol, tf) -> DataFrame | None. Plans for every symbol, best first (a failing symbol is skipped)."""
    clock = session_clock()
    plans = []
    for sym in symbols:
        frames = {}
        for tf in CHAIN:
            try:
                frames[tf] = fetch(sym, tf)
            except Exception:
                frames[tf] = None
        try:
            plans += build(sym, frames, mode=mode, clock=clock, **kw)
        except Exception:
            continue
    plans.sort(key=lambda p: (-p["confluence"]["n"], -p["stars"], -p["rr1"]))
    return plans


# ---------------------------------------------------------------- Telegram
def format_telegram(plans, ar: bool = True, limit: int = 6) -> str:
    import html
    esc = html.escape
    if not plans:
        return "📅 <b>خطة اليوم</b>\nمفيش صفقة بترابط فريمات كفاية دلوقتي." if ar else "📅 <b>Day plan</b>\nNothing with enough timeframe confluence right now."
    clk = plans[0]["session"]
    lines = [f"📅 <b>{'خطة اليوم' if ar else 'Day plan'}</b> · {esc(session_label(clk, ar))} · NY {clk['ny_time']}"]
    for p in plans[:limit]:
        up = p["direction"] == "bullish"
        cf = p["confluence"]
        chain = " ".join(f"{t.upper()}{'▲' if cf['views'].get(t) == 'bullish' else '▼' if cf['views'].get(t) == 'bearish' else '·'}" for t in CHAIN)
        tp = " / ".join(str(x) for x in p["tps"])
        lines.append(f"\n{'🟢' if up else '🔴'} <b>{esc(p['symbol'])}</b> {'شراء' if (up and ar) else 'بيع' if ar else ('BUY' if up else 'SELL')} · {p['tf'].upper()} · {p['mode']}\n"
                     f"{chain}  ({cf['n']}/{cf['of']})\n"
                     f"{'دخول' if ar else 'Entry'} {p['entry']} · {'وقف' if ar else 'Stop'} {p['stop']} ({p['risk_points']} {'نقطة' if ar else 'pts'})\n"
                     f"{'أهداف' if ar else 'Targets'} {tp} · {'حركة محتملة' if ar else 'move'} {p['move_points']} {'نقطة' if ar else 'pts'} · R:R 1:{p['rr1']}\n"
                     f"{esc(', '.join(p['schools'][:4]))}\n<i>{esc(p['exit']['text_ar' if ar else 'text_en'])}</i>")
    lines.append("\n<i>ترتيب بالأدلة مش نسبة نجاح مثبتة. مش نصيحة مالية.</i>" if ar else "\n<i>Ranked by evidence, not a proven win rate. Not financial advice.</i>")
    return "\n".join(lines)[:3900]


def dispatch(plans, sent: dict, send_fn, top_n: int = 3, resend_after_s: int = 4 * 3600, now: float | None = None) -> tuple[int, str | None]:
    """Send the best plans not sent recently: one message per plan. -> (how many, last error)."""
    import time
    now = now or time.time()
    n, err = 0, None
    for p in plans[:top_n]:
        old = sent.get(p["id"])
        if old and now - old < resend_after_s:
            continue
        err = send_fn(format_telegram([p]))
        if err:
            break
        sent[p["id"]] = now
        n += 1
    return n, err
