"""Asset-class dropdown: Crypto / Forex / Metals / Stocks / Meme coins.

One selection drives the Chart Scanner, the background scan (Ready trades) and the Workspace
watchlist. Everything is an OKX instrument id (OKX lists tokenised stocks, FX and metals
as swaps), so the same candle/scan code works for every class.
"""
import time

import requests

CLASSES = ["Crypto", "Forex", "Metals", "Stocks", "Meme coins"]
MEME_BASES = ["DOGE", "SHIB", "PEPE", "WIF", "BONK", "FLOKI", "TURBO", "NEIRO", "MEME", "BOME", "POPCAT", "MEW", "PNUT", "ACT", "GOAT", "TRUMP", "FARTCOIN", "MOODENG", "PENGU", "1000SATS"]
_CAT = {"3": "Stocks", "4": "Commodities", "5": "Forex"}
_METAL = {"XAU", "XAG", "XPT", "XPD", "XAUT", "PAXG"}
_cache = {"t": 0.0, "rows": []}
OKX = "https://www.okx.com/api/v5"


def category_of(inst_category, base):
    """OKX instCategory + base currency -> our class name."""
    if base in _METAL:
        return "Metals"
    if base in MEME_BASES:
        return "Meme coins"
    return {"3": "Stocks", "4": "Commodities", "5": "Forex"}.get(str(inst_category), "Crypto")


def _load(base_url=OKX):
    """All live USDT swaps with 24h USD volume, cached for 10 minutes."""
    if _cache["rows"] and time.time() - _cache["t"] < 600:
        return _cache["rows"]
    tk = requests.get(f"{base_url}/market/tickers", params={"instType": "SWAP"}, timeout=10).json().get("data", [])
    ins = requests.get(f"{base_url}/public/instruments", params={"instType": "SWAP"}, timeout=10).json().get("data", [])
    meta = {i["instId"]: i for i in ins}
    rows = []
    for x in tk:
        i = meta.get(x["instId"])
        if not i or not x["instId"].endswith("-USDT-SWAP"):
            continue
        base = x["instId"].split("-")[0]
        last = float(x.get("last") or 0)
        rows.append({"id": x["instId"], "cls": category_of(i.get("instCategory"), base), "vol": float(x.get("volCcy24h") or 0) * last})
    _cache.update(t=time.time(), rows=rows)
    return rows


def class_symbols(cls, crypto_symbols, top=30, base_url=OKX):
    """-> (symbols, note). Crypto = the dashboard's own list; the rest is discovered live from OKX, biggest volume first."""
    if cls == "Crypto":
        return list(crypto_symbols), ""
    try:
        rows = _load(base_url)
    except Exception as e:
        return [], f"OKX list unavailable ({type(e).__name__})"
    sel = [r for r in rows if r["cls"] == cls or (cls == "Metals" and r["cls"] == "Commodities")]   # metals also shows other commodities (oil ...)
    sel.sort(key=lambda r: r["vol"], reverse=True)
    syms = [r["id"] for r in sel[:top]]
    return syms, ("" if syms else f"OKX lists no {cls} instruments right now")
