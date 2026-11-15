"""Per-market tools: COT positioning, seasonality, smart bias, timing (entry plan)."""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from ..config import BIAS_WEIGHTS, COT_CODES, GATE, UNIVERSE
from ..data import sources
from .indicators import atr, clip1, ema, rsi, swings, zscore_last
from .macro import rate_score


def _bars(df: pd.DataFrame, n: int, extra: dict[str, pd.Series] | None = None) -> dict:
    d = df.iloc[-n:]
    out = {"t": [int(ts.timestamp()) for ts in d.index],
           "o": d["Open"].round(5).tolist(), "h": d["High"].round(5).tolist(),
           "l": d["Low"].round(5).tolist(), "c": d["Close"].round(5).tolist()}
    for k, s in (extra or {}).items():
        out[k] = s.iloc[-n:].round(5).tolist()
    return out


# ---------------------------------------------------------------- COT
def cot_asset(asset: str) -> dict | None:
    code = COT_CODES.get(asset)
    if not code:
        return None
    df, src = sources.cot(code)
    net = df["long"] - df["short"]
    w = net.iloc[-156:]
    rng = w.max() - w.min()
    idx = float((net.iloc[-1] - w.min()) / rng * 100) if rng else 50.0
    pct_oi = float(net.iloc[-1] / df["oi"].iloc[-1] * 100) if df["oi"].iloc[-1] else 0.0
    return {"asset": asset, "net": int(net.iloc[-1]), "chg_1w": int(net.iloc[-1] - net.iloc[-2]),
            "chg_4w": int(net.iloc[-1] - net.iloc[-5]), "cot_index": round(idx, 1),
            "pct_oi": round(pct_oi, 1), "asof": str(df.index[-1].date()), "source": src,
            "series": {"t": [int(t.timestamp()) for t in net.index[-52:]], "net": net.iloc[-52:].astype(int).tolist()}}


def cot_tool(symbol: str) -> dict:
    m = UNIVERSE[symbol]
    base = cot_asset(m["base"])
    quote = cot_asset(m["quote"]) if m["kind"] == "fx" else None
    parts = []
    s_base = (base["cot_index"] - 50) / 50 if base else 0.0
    s_quote = (quote["cot_index"] - 50) / 50 if quote else 0.0
    score = clip1((s_base - s_quote) / (2 if quote else 1))
    if base:
        parts.append(f"مؤشر COT لـ {m['base']} = {base['cot_index']:.0f}/100 (تغيّر أسبوعي {base['chg_1w']:+,})")
    if quote:
        parts.append(f"ولـ {m['quote']} = {quote['cot_index']:.0f}/100")
    extremes = [a["asset"] for a in (base, quote) if a and (a["cot_index"] >= 90 or a["cot_index"] <= 10)]
    look = "، ".join(parts) + "."
    if extremes:
        look += f" تنبيه: تموضع متطرف على {', '.join(extremes)}، وقد يكون الحشد المؤسسي مزدحماً."
    return {"tool": "cot", "title": f"COT · تموضع المؤسسات · {symbol}",
            "source": sorted({a["source"] for a in (base, quote) if a}),
            "data": {"symbol": symbol, "base": base, "quote": quote, "score": round(score, 2), "extremes": extremes},
            "look_at": look}


# ---------------------------------------------------------------- seasonality
def seasonality_tool(symbol: str) -> dict:
    df, src = sources.prices(UNIVERSE[symbol]["yf"], "1d")
    mclose = df["Close"].resample("ME").last()
    mret = mclose.pct_change().dropna() * 100
    month = datetime.now(timezone.utc).month
    this = mret[mret.index.month == month]
    by_month = {int(k): round(float(v), 2) for k, v in mret.groupby(mret.index.month).mean().items()}
    hit = float((this > 0).mean()) if len(this) else 0.5
    years = len(this)
    score = clip1((hit - 0.5) * 2.5) * min(1.0, years / 8)
    return {"tool": "seasonality", "title": f"Seasonality · الموسمية · {symbol}", "source": [src],
            "data": {"symbol": symbol, "month": month, "avg": round(float(this.mean()), 2) if years else 0.0,
                     "hit_rate": round(hit * 100), "years": years, "by_month": by_month, "score": round(score, 2)},
            "look_at": f"تاريخياً في هذا الشهر: متوسط {float(this.mean()) if years else 0:+.2f}% وصعد في "
                       f"{hit * 100:.0f}% من {years} سنة. الموسمية عامل مساعد فقط (وزنها 10%)."}


# ---------------------------------------------------------------- smart bias
def bias_tool(symbol: str, rates_table: dict, cot_res: dict, seas_res: dict) -> dict:
    m = UNIVERSE[symbol]
    df, src = sources.prices(m["yf"], "1d")
    c = df["Close"]
    e50, e200 = ema(c, 50), ema(c, 200)
    trend = clip1((np.sign(c.iloc[-1] - e50.iloc[-1]) + np.sign(c.iloc[-1] - e200.iloc[-1])
                   + np.sign(e50.iloc[-1] - e50.iloc[-6])) / 3)
    roc = c.pct_change(20)
    momentum = clip1(zscore_last(roc, 252) / 2)
    rscore, rnote = rate_score(rates_table, m["base"], m["quote"]) if m["kind"] != "index" else (0.0, "لا ينطبق")
    comp = {"trend": trend, "cot": cot_res["data"]["score"], "momentum": momentum,
            "rates": rscore, "seasonality": seas_res["data"]["score"]}
    score = sum(BIAS_WEIGHTS[k] * v for k, v in comp.items())
    agree = sum(1 for v in comp.values() if np.sign(v) == np.sign(score) and abs(v) > 0.1)
    confidence = round(100 * agree / len(comp))
    label = ("Strong Bullish" if score > 0.5 else "Bullish" if score > GATE["min_bias"] else
             "Strong Bearish" if score < -0.5 else "Bearish" if score < -GATE["min_bias"] else "Neutral")
    r = float(rsi(c).iloc[-1])
    return {"tool": "smart_bias", "title": f"Smart Bias · الانحياز · {symbol}", "source": [src],
            "data": {"symbol": symbol, "score": round(score, 2), "label": label, "confidence": confidence,
                     "components": {k: round(v, 2) for k, v in comp.items()}, "weights": BIAS_WEIGHTS,
                     "rsi": round(r, 1), "rates_note": rnote,
                     "chart": _bars(df, 160, {"ema50": e50, "ema200": e200})},
            "look_at": f"الانحياز {label} بدرجة {score:+.2f} وثقة {confidence}% "
                       f"(اتجاه {comp['trend']:+.2f}، COT {comp['cot']:+.2f}، زخم {comp['momentum']:+.2f}، "
                       f"فائدة {comp['rates']:+.2f}، موسمية {comp['seasonality']:+.2f}). "
                       "انظر إلى موقع السعر من EMA50 وEMA200 على الشارت اليومي."}


# ---------------------------------------------------------------- timing
def timing_tool(symbol: str, direction: int) -> dict:
    """Hourly structure → entry plan. direction: +1 long, -1 short."""
    df, src = sources.prices(UNIVERSE[symbol]["yf"], "1h")
    c = df["Close"]
    e20, e50 = ema(c, 20), ema(c, 50)
    a = float(atr(df).iloc[-1])
    last = float(c.iloc[-1])
    highs, lows = swings(df.iloc[-300:], 3)
    aligned = (e20.iloc[-1] - e50.iloc[-1]) * direction > 0 and (last - e50.iloc[-1]) * direction > 0
    near = abs(last - e20.iloc[-1]) <= 0.5 * a
    stretched = abs(last - e20.iloc[-1]) / a if a else 0
    bos = False
    if direction > 0 and len(highs) >= 2:
        bos = last > highs[-2][1]
    if direction < 0 and len(lows) >= 2:
        bos = last < lows[-2][1]

    entry = last if near else float(e20.iloc[-1])
    if direction > 0:
        below = [p for _, p in lows if p < entry - 0.3 * a]
        stop = (below[-1] if below else entry - 1.5 * a) - 0.2 * a
        stop = min(max(stop, entry - 3 * a), entry - 0.8 * a)
    else:
        above = [p for _, p in highs if p > entry + 0.3 * a]
        stop = (above[-1] if above else entry + 1.5 * a) + 0.2 * a
        stop = max(min(stop, entry + 3 * a), entry + 0.8 * a)
    risk = abs(entry - stop)
    # Obstacle = nearest opposing major swing (k=5) in the last 120 bars: where stops and
    # resting liquidity sit. "room" = how many R the trade has before hitting it.
    mh, ml = swings(df.iloc[-120:], 5)
    if direction > 0:
        obs = sorted(p for _, p in mh if p > entry)
    else:
        obs = sorted((p for _, p in ml if p < entry), reverse=True)
    obstacle = obs[0] if obs else None
    room = min(abs(obstacle - entry) / risk, 3.0) if (obstacle is not None and risk) else 3.0
    t1 = entry + direction * 2 * risk
    t2 = entry + direction * 3 * risk
    rr = 2.0
    state = ("في منطقة الدخول الآن" if aligned and near else
             "متوافق لكن ممتد، انتظر ارتداداً إلى EMA20" if aligned else
             "الهيكل الساعي غير متوافق بعد مع الانحياز")
    side = "شراء" if direction > 0 else "بيع"
    dec = 3 if last > 20 else 5
    fmt = lambda x: f"{x:.{dec}f}"
    return {"tool": "timing", "title": f"Timing · التوقيت (ساعة) · {symbol}", "source": [src],
            "data": {"symbol": symbol, "direction": direction, "aligned": bool(aligned), "in_zone": bool(near),
                     "bos": bool(bos), "stretch_atr": round(stretched, 2), "atr": a,
                     "entry": entry, "stop": stop, "t1": t1, "t2": t2, "rr": rr,
                     "obstacle": obstacle, "room_r": round(room, 2),
                     "order": "market" if near else "limit", "state": state,
                     "chart": _bars(df, 150, {"ema20": e20, "ema50": e50})},
            "look_at": f"{state}. خطة {side}: دخول {fmt(entry)} ({'سوق' if near else 'أمر معلق'})، وقف {fmt(stop)}، "
                       f"هدف أول {fmt(t1)} (2R) وثانٍ {fmt(t2)} (3R). "
                       + (f"أقرب عائق (قمة/قاع سابق) عند {fmt(obstacle)} أي بعد {room:.1f}R. " if obstacle is not None else "لا عائق هيكلي قريب. ")
                       + f"{'كسر هيكل مؤكد. ' if bos else ''}راقب الإغلاق الساعي حول EMA20."}
