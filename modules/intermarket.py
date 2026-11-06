"""Intermarket board: SMT divergence between CORRELATED pairs (gold / silver, BTC / ETH, S&P / Nasdaq, EUR / GBP, ...), on several timeframes at once.

modules/smt.py already knows how to compare two markets swing by swing; until now the result only appeared as a tag inside one symbol's setup. This module runs every pair on every
timeframe and returns plain EVENTS the Radar, the Workspace strip and the alerts can show: "SMT up on 1H between Gold and Silver".

Honest limits (shown in the UI too): an SMT is a hint that two correlated markets disagree, not a trade by itself; no win rate is claimed here (the lab measures the SMT school separately);
a pair whose recent correlation is below smt.MIN_CORR is skipped, never guessed."""
from __future__ import annotations

import hashlib
from datetime import timezone

import pandas as pd

from modules.smt import SMT_PAIRS, smt_signals

TF_SECONDS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400, "1w": 604800}
TF_ORDER = ["1w", "1d", "4h", "1h", "30m", "15m", "5m", "1m"]   # big first: the big timeframe is the story, the small one the timing
DEFAULT_TFS = ("5m", "15m", "1h", "4h", "1d")

# short name + colour (the colours the platform already uses for metals / majors)
NAMES = {
    "HL:xyz:GOLD": ("Gold", "#f0b90b"), "Y:GC=F": ("Gold", "#f0b90b"), "HL:xyz:SILVER": ("Silver", "#c0c7d0"), "Y:SI=F": ("Silver", "#c0c7d0"),
    "HL:xyz:CL": ("WTI oil", "#9c6b3c"), "HL:xyz:BRENTOIL": ("Brent oil", "#7d5a36"), "HL:xyz:SP500": ("S&P 500", "#4aa3ff"), "HL:xyz:XYZ100": ("Nasdaq 100", "#b57cff"),
    "Y:^GSPC": ("S&P 500", "#4aa3ff"), "Y:^IXIC": ("Nasdaq", "#b57cff"), "Y:^NDX": ("Nasdaq 100", "#b57cff"), "Y:^DJI": ("Dow", "#26c6da"), "Y:DX-Y.NYB": ("Dollar (DXY)", "#2dd4bf"),
    "Y:EURUSD=X": ("EUR/USD", "#4aa3ff"), "Y:GBPUSD=X": ("GBP/USD", "#ef5350"), "Y:AUDUSD=X": ("AUD/USD", "#66bb6a"), "Y:NZDUSD=X": ("NZD/USD", "#26a69a"), "Y:USDJPY=X": ("USD/JPY", "#ffa726"), "Y:USDCHF=X": ("USD/CHF", "#ec407a"),
    "BTC-USDT": ("Bitcoin", "#f7931a"), "ETH-USDT": ("Ethereum", "#8c9eff"), "SOL-USDT": ("Solana", "#14f195"), "BNB-USDT": ("BNB", "#f3ba2f"), "AVAX-USDT": ("Avalanche", "#e84142"),
}
_PALETTE = ["#4aa3ff", "#0ecb81", "#f0b90b", "#b57cff", "#26c6da", "#ff9800", "#ec407a"]
AR = {"Gold": "الذهب", "Silver": "الفضة", "WTI oil": "خام WTI", "Brent oil": "خام برنت", "S&P 500": "S&P 500", "Nasdaq 100": "ناسداك 100", "Nasdaq": "ناسداك", "Dow": "داو جونز", "Dollar (DXY)": "الدولار",
      "Bitcoin": "البيتكوين", "Ethereum": "الإيثيريوم", "Solana": "سولانا"}


def name_of(sym: str):
    if sym in NAMES:
        return NAMES[sym]
    short = sym.replace("-USDT", "").split(":")[-1]
    return short, _PALETTE[int(hashlib.md5(sym.encode()).hexdigest(), 16) % len(_PALETTE)]


def session_of(ts) -> str:
    """Asia / London / New York by New York clock (same bands the Workspace draws): Asia 19-04, London 03-12, New York 08-17; the overlap names both."""
    try:
        t = pd.Timestamp(ts)
        t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
        h = t.tz_convert("America/New_York")
        m = h.hour * 60 + h.minute
    except Exception:
        return ""
    names = []
    if m >= 19 * 60 or m < 4 * 60:
        names.append("Asia")
    if 3 * 60 <= m < 12 * 60:
        names.append("London")
    if 8 * 60 <= m < 17 * 60:
        names.append("New York")
    return " + ".join(names) or "off-hours"


def _text(a: str, b: str, tf: str, side: str, p1, p2, ar: bool):
    na, nb = name_of(a)[0], name_of(b)[0]
    if ar:
        x, y = AR.get(na, na), AR.get(nb, nb)
        up = side == "bullish"
        return (f"SMT {'صاعد' if up else 'هابط'} على فريم {tf.upper()} بين {x} و{y}: "
                f"{'أحدهما عمل قاع جديد' if up else 'أحدهما عمل قمة جديدة'} والتاني ما أكدش. الأسواق المرتبطة مش متفقة = احتمال انعكاس {'صاعد' if up else 'هابط'}، مش صفقة لوحده.")
    up = side == "bullish"
    return (f"SMT {'up' if up else 'down'} on {tf.upper()} between {na} and {nb}: one made a new {'low' if up else 'high'} and the other refused. "
            f"Correlated markets disagree = a possible {'bullish' if up else 'bearish'} reversal hint, not a trade by itself.")


def scan_pairs(fetch, tfs=DEFAULT_TFS, pairs=None, max_age: int = 15, series_n: int = 60):
    """fetch(symbol, tf) -> DataFrame(time, open, high, low, close) or None. Returns events, biggest timeframe first, newest first.

    Event keys: id, a, b, inverse, tf, direction, bars_ago, t (ISO of the 2nd swing), session, p1, p2, a_name, b_name, a_color, b_color, text_en, text_ar, series_a, series_b."""
    out, cache = [], {}

    def get(sym, tf):
        k = (sym, tf)
        if k not in cache:
            try:
                cache[k] = fetch(sym, tf)
            except Exception:
                cache[k] = None
        return cache[k]

    for tf in tfs:
        for a, b, inv in (pairs if pairs is not None else SMT_PAIRS):
            da, db = get(a, tf), get(b, tf)
            if da is None or db is None or len(da) < 60 or len(db) < 60:
                continue
            try:
                sigs = smt_signals(da, db, b, inv)
            except Exception:
                continue
            seen = set()
            for s in sigs:
                if s.get("key") != "smt" or s["direction"] in seen:
                    continue
                age = int((s.get("vals") or {}).get("age", 0))
                if age > max_age:
                    continue
                seen.add(s["direction"])
                last = pd.Timestamp(da["time"].iloc[-1])
                t2 = last - pd.Timedelta(seconds=TF_SECONDS.get(tf, 3600) * age)
                (na, ca), (nb, cb) = name_of(a), name_of(b)
                pr = s.get("prices") or {}
                out.append({
                    "id": f"smt|{a}|{b}|{tf}|{s['direction']}|{int(t2.timestamp())}", "a": a, "b": b, "inverse": bool(inv), "tf": tf, "direction": s["direction"], "bars_ago": age,
                    "t": t2.isoformat(), "session": session_of(t2), "p1": pr.get("p1"), "p2": pr.get("p2"), "a_name": na, "b_name": nb, "a_color": ca, "b_color": cb,
                    "text_en": _text(a, b, tf, s["direction"], pr.get("p1"), pr.get("p2"), False), "text_ar": _text(a, b, tf, s["direction"], pr.get("p1"), pr.get("p2"), True),
                    "series_a": [round(float(x), 6) for x in da["close"].tail(series_n)], "series_b": [round(float(x), 6) for x in db["close"].tail(series_n)],
                })
    out.sort(key=lambda e: (TF_ORDER.index(e["tf"]) if e["tf"] in TF_ORDER else 99, e["bars_ago"]))
    return out


def chips(events, ar: bool = False, limit: int = 12):
    """The short lines the Workspace strip / ribbon show: [{id, a, b, tf, direction, label}]"""
    res = []
    for e in events[:limit]:
        arrow = "▲" if e["direction"] == "bullish" else "▼"
        na = AR.get(e["a_name"], e["a_name"]) if ar else e["a_name"]
        nb = AR.get(e["b_name"], e["b_name"]) if ar else e["b_name"]
        res.append({"id": e["id"], "a": e["a"], "b": e["b"], "tf": e["tf"], "direction": e["direction"], "bars_ago": e["bars_ago"], "session": e["session"],
                    "label": f"SMT {arrow} {na}/{nb} {e['tf'].upper()}", "text": e["text_ar" if ar else "text_en"], "a_color": e["a_color"], "b_color": e["b_color"]})
    return res
