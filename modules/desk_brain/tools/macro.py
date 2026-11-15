"""Context tools: risk regime, currency strength, rate differentials, event calendar."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from ..config import CURRENCIES, FRED_RATE_SERIES, GATE, REGIME_TICKERS, all_fx_pairs
from ..data import sources
from .indicators import clip1, ema, zscore_last


def _sources(*labels: str) -> list[str]:
    return sorted(set(labels))


def risk_regime() -> dict:
    """Risk-on / risk-off score in [-1, +1] from cross-asset behaviour."""
    with ThreadPoolExecutor(6) as ex:
        res = dict(zip(REGIME_TICKERS, ex.map(lambda t: sources.prices(t, "1d"), REGIME_TICKERS.values())))
    comp, notes = {}, []
    vix = res["VIX"][0]["Close"]
    comp["vix"] = clip1(-zscore_last(vix, 252) / 2)
    spx = res["SPX"][0]["Close"]
    comp["equities"] = clip1((spx.iloc[-1] / ema(spx, 50).iloc[-1] - 1) * 20)
    aj = res["AUDJPY"][0]["Close"]
    comp["audjpy"] = clip1((aj.iloc[-1] / aj.iloc[-21] - 1) * 25)
    gold = res["GOLD"][0]["Close"]
    comp["gold"] = clip1(-(gold.iloc[-1] / gold.iloc[-21] - 1) * 15)
    score = float(np.mean(list(comp.values())))
    label = "Risk-On" if score > 0.2 else "Risk-Off" if score < -0.2 else "Mixed"
    if comp["vix"] < -0.5:
        notes.append("VIX مرتفع مقارنة بسنته الأخيرة")
    if comp["audjpy"] > 0.4:
        notes.append("AUDJPY يصعد: شهية مخاطرة")
    if comp["audjpy"] < -0.4:
        notes.append("AUDJPY يهبط: هروب من المخاطرة")
    snap = {k: round(float(v[0]["Close"].iloc[-1]), 4) for k, v in res.items()}
    return {
        "tool": "risk_regime", "title": "Risk Regime · مزاج المخاطرة",
        "source": _sources(*[v[1] for v in res.values()]),
        "data": {"score": round(score, 2), "label": label,
                 "components": {k: round(v, 2) for k, v in comp.items()}, "snapshot": snap},
        "look_at": f"المزاج العام {label} بدرجة {score:+.2f}. " + ("، ".join(notes) if notes else
                   "لا توجد إشارة متطرفة من VIX أو AUDJPY."),
    }


def currency_strength() -> dict:
    """Strength of each major = average % move vs the other 7, over 1, 5 and 20 days."""
    pairs = all_fx_pairs()
    tickers = [f"{a}{b}=X" for a, b in pairs]
    with ThreadPoolExecutor(8) as ex:
        data = list(ex.map(lambda t: sources.prices(t, "1d"), tickers))
    srcs = {d[1] for d in data}
    out = {}
    for n in (1, 5, 20):
        acc = {c: [] for c in CURRENCIES}
        for (a, b), (df, _) in zip(pairs, data):
            c = df["Close"]
            if len(c) <= n:
                continue
            ch = (c.iloc[-1] / c.iloc[-1 - n] - 1) * 100
            acc[a].append(ch)
            acc[b].append(-ch)
        out[n] = {c: round(float(np.mean(v)), 3) if v else 0.0 for c, v in acc.items()}
    rank = sorted(CURRENCIES, key=lambda c: out[5][c], reverse=True)
    strongest, weakest = rank[:2], rank[-2:]
    return {
        "tool": "currency_strength", "title": "Currency Strength · قوة العملات",
        "source": _sources(*srcs),
        "data": {"d1": out[1], "d5": out[5], "d20": out[20], "rank": rank},
        "look_at": f"الأقوى على 5 أيام: {', '.join(strongest)}. الأضعف: {', '.join(weakest)}. "
                   f"أفضل الأزواج المرشحة تجمع قوياً مع ضعيف، مثل {strongest[0]}/{weakest[-1]}.",
    }


def rate_differentials() -> dict:
    with ThreadPoolExecutor(8) as ex:
        res = dict(zip(FRED_RATE_SERIES, ex.map(lambda kv: sources.rate(kv[1], kv[0]), FRED_RATE_SERIES.items())))
    table = {}
    for c, (s, _) in res.items():
        chg = float(s.iloc[-1] - s.iloc[-4]) if len(s) >= 4 else 0.0
        table[c] = {"rate": round(float(s.iloc[-1]), 2), "chg_3m": round(chg, 2),
                    "asof": str(s.index[-1].date())}
    hikers = sorted(table, key=lambda c: table[c]["chg_3m"], reverse=True)
    return {
        "tool": "rate_differentials", "title": "Rates · الفائدة والفروقات",
        "source": _sources(*[v[1] for v in res.values()]),
        "data": table,
        "look_at": f"أكثر عملة ارتفعت فائدتها خلال 3 أشهر: {hikers[0]}، وأكثرها انخفاضاً: {hikers[-1]}. "
                   "البيانات شهرية ومتأخرة، فهي للاتجاه العام وليست للتوقيت.",
    }


def rate_score(table: dict, base: str, quote: str) -> tuple[float, str]:
    if base in table and quote in table:
        diff = table[base]["rate"] - table[quote]["rate"]
        dchg = table[base]["chg_3m"] - table[quote]["chg_3m"]
        return clip1(0.6 * clip1(dchg / 0.5) + 0.4 * clip1(diff / 4)), f"فرق الفائدة {diff:+.2f}% وتغيّره {dchg:+.2f}%"
    if base == "XAU" and "USD" in table:
        return clip1(-table["USD"]["chg_3m"] / 0.5), "الذهب عكس اتجاه فائدة الدولار"
    return 0.0, "لا ينطبق"


def calendar_risk() -> dict:
    events, src = sources.calendar()
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(hours=48)
    upcoming = []
    for e in events:
        try:
            t = pd.Timestamp(e["date"])
            t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
        except Exception:
            continue
        if now <= t <= horizon and e.get("impact") in ("High", "Medium"):
            upcoming.append({"title": e.get("title"), "ccy": e.get("country"), "impact": e.get("impact"),
                             "time": t.isoformat(), "hours": round((t - now).total_seconds() / 3600, 1),
                             "forecast": e.get("forecast"), "previous": e.get("previous")})
    upcoming.sort(key=lambda x: x["hours"])
    blocked = sorted({e["ccy"] for e in upcoming if e["impact"] == "High" and e["hours"] <= GATE["event_block_hours"]})
    return {
        "tool": "calendar_risk", "title": "Calendar · الأحداث القادمة",
        "source": [src], "data": {"events": upcoming, "blocked": blocked},
        "look_at": (f"أحداث عالية التأثير خلال {GATE['event_block_hours']} ساعة على: {', '.join(blocked)}. "
                    "لا دخول جديد على هذه العملات قبل الخبر." if blocked else
                    "لا توجد أحداث عالية التأثير قريبة جداً."),
    }
