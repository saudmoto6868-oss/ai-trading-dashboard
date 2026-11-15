"""Tools for the Wyckoff, News and Sentiment agents (OmniDesk 10-agent structure)."""
from __future__ import annotations

import logging

import numpy as np
import requests

from ..config import NEWS_API_KEY, UNIVERSE
from ..data import sources
from ..data.cache import cached
from . import macro
from .indicators import atr, rsi, zscore_last

log = logging.getLogger("desk.schools")


def _px(x: float) -> str:
    return f"{x:,.2f}" if abs(x) >= 1000 else f"{x:.5g}"


def wyckoff_tool(symbol: str) -> dict:
    """Trading range of the last 40 daily bars, the trend before it, spring / upthrust,
    sign of strength / weakness, and effort vs result (volume vs spread)."""
    df, src = sources.prices(UNIVERSE[symbol]["yf"], "1d")
    a = float(atr(df).iloc[-1])
    rng = df.iloc[-40:]
    base = rng.iloc[:-10]
    hi, lo = float(base["High"].max()), float(base["Low"].min())
    width = (hi - lo) / a if a else 0
    before = df["Close"].iloc[-100:-40]
    prior = float(np.sign(before.iloc[-1] - before.iloc[0])) if len(before) > 2 else 0.0
    last10 = rng.iloc[-10:]
    last = float(df["Close"].iloc[-1])
    spring = bool((last10["Low"] < lo).any() and last > lo)
    upthrust = bool((last10["High"] > hi).any() and last < hi)
    vol = df["Volume"].astype(float)
    has_vol = bool(vol.iloc[-60:].sum() > 0)
    v_ratio = float(vol.iloc[-5:].mean() / vol.iloc[-60:].mean()) if has_vol and vol.iloc[-60:].mean() else None
    sos = bool(last > hi and (v_ratio is None or v_ratio > 1.2))
    sow = bool(last < lo and (v_ratio is None or v_ratio > 1.2))
    spread = float((rng["High"] - rng["Low"]).iloc[-5:].mean() / ((rng["High"] - rng["Low"]).mean() or 1))
    effort = None
    if v_ratio is not None:
        effort = ("جهد كبير ونتيجة صغيرة (امتصاص)" if v_ratio > 1.3 and spread < 0.8 else
                  "جهد ونتيجة متناسقين" if v_ratio > 1.0 else "حجم ضعيف")
    is_range = width <= 8
    if is_range and prior < 0:
        schematic = "تجميع محتمل (Accumulation)"
    elif is_range and prior > 0:
        schematic = "توزيع محتمل (Distribution)"
    else:
        schematic = "ترند (Markup)" if last > hi else "ترند (Markdown)" if last < lo else "داخل نطاق غير واضح"
    phase = ("C (Spring)" if spring else "C (Upthrust)" if upthrust else "D (SOS)" if sos else
             "D (SOW)" if sow else "B (بناء السبب)" if is_range else "E")
    bias = 1 if (spring or sos) else -1 if (upthrust or sow) else 0
    return {"tool": "wyckoff", "title": f"Wyckoff · {symbol}", "source": [src],
            "data": {"symbol": symbol, "range_high": hi, "range_low": lo, "width_atr": round(width, 1),
                     "prior_trend": int(prior), "schematic": schematic, "phase": phase, "spring": spring,
                     "upthrust": upthrust, "sos": sos, "sow": sow, "volume_ratio": None if v_ratio is None else round(v_ratio, 2),
                     "effort_vs_result": effort, "bias": bias, "has_volume": has_vol},
            "look_at": f"{schematic}، المرحلة {phase}. النطاق {_px(lo)}–{_px(hi)} بعرض {width:.1f} ATR. "
                       + ("Spring: كسر القاع ورجع جوه النطاق. " if spring else "")
                       + ("Upthrust: كسر القمة ورجع جوه. " if upthrust else "")
                       + (f"الحجم آخر 5 أيام {v_ratio:.2f}× المتوسط: {effort}." if v_ratio is not None else
                          "لا يوجد حجم لهذا السوق على ياهو، فقراءة الجهد والنتيجة غير متاحة.")}


def _av_news(tickers: str) -> tuple[list, str]:
    def go():
        if not NEWS_API_KEY:
            return [], "none"
        try:
            r = requests.get("https://www.alphavantage.co/query",
                             params={"function": "NEWS_SENTIMENT", "tickers": tickers, "limit": 50, "apikey": NEWS_API_KEY}, timeout=20)
            r.raise_for_status()
            return r.json().get("feed", []), "alphavantage"
        except Exception as e:
            log.warning("news failed: %s", e)
            return [], "none"
    return cached(f"news:{tickers}", 1800, go)


def _av_ticker(symbol: str) -> str:
    m = UNIVERSE[symbol]
    if m["kind"] == "crypto":
        return f"CRYPTO:{m['base']}"
    if m["kind"] == "fx":
        return f"FOREX:{m['base']},FOREX:{m['quote']}"
    return {"XAU": "FOREX:XAU", "XAG": "FOREX:XAG", "SPX": "SPY", "NDX": "QQQ"}.get(m["base"], m["base"])


def news_tool(symbol: str) -> dict:
    m = UNIVERSE[symbol]
    cal = macro.calendar_risk()
    events = [e for e in cal["data"]["events"] if e["ccy"] in (m["base"], m["quote"])]
    feed, nsrc = _av_news(_av_ticker(symbol))
    heads = [{"title": f.get("title"), "source": f.get("source"), "time": f.get("time_published"),
              "sentiment": float(f.get("overall_sentiment_score", 0))} for f in feed[:8]]
    avg = round(float(np.mean([h["sentiment"] for h in heads])), 3) if heads else None
    return {"tool": "news", "title": f"News · {symbol}", "source": sorted(set(cal["source"]) | ({nsrc} - {"none"})),
            "data": {"symbol": symbol, "events": events[:6], "blocked": [c for c in (m["base"], m["quote"]) if c in cal["data"]["blocked"]],
                     "headlines": heads, "news_sentiment": avg, "headlines_available": bool(heads)},
            "look_at": (f"{len(events)} حدث قادم على العملتين خلال 48 ساعة. " if events else "لا أحداث قادمة قريبة. ")
                       + (f"متوسط معنويات {len(heads)} عنوان: {avg:+.2f}." if heads else
                          "العناوين غير متاحة: أضف ALPHAVANTAGE_API_KEY (مجاني) لتفعيلها.")}


def sentiment_tool(symbol: str) -> dict:
    """No free retail-positioning feed exists (see README). This is a CROWD PROXY, labelled
    as such: price stretch, RSI, and speculator COT extremes."""
    df, src = sources.prices(UNIVERSE[symbol]["yf"], "1d")
    c = df["Close"]
    r = float(rsi(c).iloc[-1])
    z = zscore_last(c.pct_change(20), 252)
    crowd = float(np.clip((r - 50) / 30 * 0.5 + z / 2 * 0.5, -1, 1))
    label = "حشد شرائي متطرف" if crowd > 0.6 else "حشد بيعي متطرف" if crowd < -0.6 else "محايد"
    return {"tool": "sentiment", "title": f"Sentiment (proxy) · {symbol}", "source": [src],
            "data": {"symbol": symbol, "crowd_proxy": round(crowd, 2), "rsi": round(r, 1), "move_z": round(z, 2),
                     "label": label, "retail_positioning": None},
            "look_at": f"مؤشر الحشد التقريبي {crowd:+.2f} ({label}): RSI {r:.0f} وحركة 20 يوم z={z:+.1f}. "
                       "ده بديل تقريبي، مش نسب مراكز التجزئة الحقيقية (مش متاحة مجاناً). الحشد المتطرف إشارة عكسية."}
