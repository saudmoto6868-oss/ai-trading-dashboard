"""Where else a signal shows up, and what to watch out for (owner 2026-11-20).

The Radar is wider (spot, perpetual futures, Hyperliquid TradFi, Yahoo); the Spot desk board is spot only. Each board
saves a small index of its live signals in the session; the other board reads it and shows, per market:
  where: "Radar 4h: buy (Double bottom) · Spot 1d: buy (Discount)"
  watch: short notes such as "Radar says sell, Spot says buy: wait".
Pure functions, no network, no Streamlit. Nothing here places an order."""
from __future__ import annotations

import re

RADAR_KEY, SPOT_KEY = "xs_radar", "xs_spot"   # session_state keys


def base_of(sym: str) -> str:
    """BTC-USDT / BTC-USDT-SWAP / HL:xyz:GOLD / Y:GC=F / BTC -> BTC / BTC / GOLD / GC=F / BTC."""
    s = str(sym or "").upper().strip()
    s = s.split(":")[-1]
    return re.split(r"-(?=[A-Z])", s)[0] if "-" in s else s


def market_of(sym: str) -> str:
    s = str(sym or "").upper()
    if s.endswith("-SWAP") or s.startswith("HL:"):
        return "futures"
    if s.startswith(("Y:", "FH:")):
        return "other"
    return "spot"


def _side(x) -> str:
    x = str(x or "").lower()
    return "buy" if x in ("buy", "long", "bull", "bullish") else "sell" if x in ("sell", "short", "exit", "bear", "bearish") else ""


def radar_index(items, tf: str) -> dict:
    """items: iterable of (symbol, what, side, extra dict). -> {base: [entry]}"""
    out: dict = {}
    for sym, what, side, extra in items:
        e = {"sym": sym, "market": market_of(sym), "what": str(what)[:40], "side": _side(side), "tf": tf}
        e.update({k: v for k, v in (extra or {}).items() if k in ("rsi", "regime", "trend")})
        out.setdefault(base_of(sym), []).append(e)
    return out


def spot_index(rows) -> dict:
    """Spot board rows (asset, name, side, tf, school, ev_label) -> {base: [entry]}"""
    out: dict = {}
    for r in rows or []:
        out.setdefault(base_of(r.get("asset")), []).append({
            "what": str(r.get("name", ""))[:40], "side": _side(r.get("side")), "tf": r.get("tf", ""),
            "school": str(r.get("school", ""))[:30], "lab_bad": str(r.get("ev_label", "")).startswith("كان أسوأ")})
    return out


def _sides(entries) -> set:
    return {e["side"] for e in entries if e.get("side")}


def _tx(en: str, ar: str, lang: str) -> str:
    return ar if lang == "ar" else en


def notes(base: str, radar: dict | None, spot: dict | None, lang: str = "en", here: str = "radar") -> dict:
    """-> {"where": text, "watch": [text, ...]} for one market. `here` = the board showing it ('radar' or 'spot')."""
    r_ = (radar or {}).get(base, []) if radar is not None else None
    s_ = (spot or {}).get(base, []) if spot is not None else None
    where, watch = [], []
    if r_:
        tf = r_[0].get("tf", "")
        txt = ", ".join(f"{e['side'] or '?'} ({e['what']})" for e in r_[:3])
        where.append(_tx(f"Radar {tf}: {txt}", f"الرادار {tf}: {txt}", lang))
    if s_:
        txt = ", ".join(f"{e['side'] or '?'} {e['tf']} ({e['what']})" for e in s_[:3])
        where.append(_tx(f"Spot: {txt}", f"السبوت: {txt}", lang))
    rs, ss = _sides(r_ or []), _sides(s_ or [])
    if "buy" in rs and "sell" in rs:
        watch.append(_tx("Radar has buy and sell signals at once: no clear side", "الرادار فيه شراء وبيع في نفس الوقت: مفيش اتجاه واضح", lang))
    if rs and ss and rs != ss and (rs | ss) >= {"buy", "sell"}:
        watch.append(_tx("Radar and Spot disagree: wait for them to agree", "الرادار والسبوت مختلفين: استنى لما يتفقوا", lang))
    elif rs and ss and rs == ss:
        watch.append(_tx("Radar and Spot agree", "الرادار والسبوت متفقين", lang))
    if r_ and all(e["market"] == "futures" for e in r_) and ss:
        watch.append(_tx("Radar signal is on the futures chart: on spot use no leverage and a spot stop",
                         "إشارة الرادار على شارت الفيوتشر: في السبوت من غير رافعة ووقف على السبوت", lang))
    if any(e.get("lab_bad") for e in (s_ or [])):
        watch.append(_tx("The lab found this spot setup worse than normal", "المعمل لقى السيت أب ده أسوأ من العادي", lang))
    rsi = next((e.get("rsi") for e in (r_ or []) if e.get("rsi") is not None), None)
    want_buy = "buy" in rs or "buy" in ss
    try:
        if rsi is not None and want_buy and float(rsi) >= 70:
            watch.append(_tx(f"RSI {float(rsi):.0f} on the Radar timeframe: buying into overbought", f"RSI {float(rsi):.0f} على فريم الرادار: شراء في تشبع شرائي", lang))
    except (TypeError, ValueError):
        pass
    if want_buy and any(str(e.get("regime", "")).lower().startswith(("down", "bear")) for e in (r_ or [])):
        watch.append(_tx("Buy signal inside a down regime", "إشارة شراء جوه سوق هابط", lang))
    if here == "radar" and spot is None:
        watch.append(_tx("Spot board not scanned in this session", "لوحة السبوت لسه ماتمسحتش في الجلسة دي", lang))
    if here == "spot" and radar is None:
        watch.append(_tx("Radar Signal list not opened in this session", "قايمة إشارات الرادار لسه ماتفتحتش في الجلسة دي", lang))
    return {"where": " · ".join(where), "watch": watch}
