"""Asset-class dropdown: Crypto / Forex / Metals / Stocks / Meme coins.

One selection drives the Chart Scanner, the background scan (Ready trades) and the Workspace
watchlist. Everything is an OKX instrument id (OKX lists tokenised stocks, FX and metals
as swaps), so the same candle/scan code works for every class.
"""
import time

import requests

CLASSES = ["Crypto", "Forex", "Metals", "Stocks", "Meme coins", "Egypt (EGX)", "Saudi (Tadawul)"]
MARKET_TYPES = {"Spot": "SPOT", "Perp (swap)": "SWAP", "Futures": "FUTURES"}
NO_FEED = {"Egypt (EGX)", "Saudi (Tadawul)"}   # no verified free live feed yet (needs an API key); never show invented numbers
MEME_BASES = ["DOGE", "SHIB", "PEPE", "WIF", "BONK", "FLOKI", "TURBO", "NEIRO", "MEME", "BOME", "POPCAT", "MEW", "PNUT", "ACT", "GOAT", "TRUMP", "FARTCOIN", "MOODENG", "PENGU", "1000SATS"]
_CAT = {"3": "Stocks", "4": "Commodities", "5": "Forex"}
_METAL = {"XAU", "XAG", "XPT", "XPD", "XAUT", "PAXG"}
_cache = {}
OKX = "https://www.okx.com/api/v5"


def category_of(inst_category, base):
    """OKX instCategory + base currency -> our class name."""
    if base in _METAL:
        return "Metals"
    if base in MEME_BASES:
        return "Meme coins"
    return {"3": "Stocks", "4": "Commodities", "5": "Forex"}.get(str(inst_category), "Crypto")


def _load(inst_type="SWAP", base_url=OKX):
    """All live instruments of one OKX type with 24h USD volume, cached 10 min per type."""
    c = _cache.get(inst_type)
    if c and time.time() - c[0] < 600:
        return c[1]
    tk = requests.get(f"{base_url}/market/tickers", params={"instType": inst_type}, timeout=10).json().get("data", [])
    ins = requests.get(f"{base_url}/public/instruments", params={"instType": inst_type}, timeout=10).json().get("data", [])
    meta = {i["instId"]: i for i in ins}
    rows = []
    for x in tk:
        i = meta.get(x["instId"])
        parts = x["instId"].split("-")
        if not i or len(parts) < 2 or parts[1] not in ("USDT", "USD"):
            continue
        last = float(x.get("last") or 0)
        rows.append({"id": x["instId"], "cls": category_of(i.get("instCategory"), parts[0]), "vol": float(x.get("volCcy24h") or 0) * (last if inst_type != "SPOT" else 1)})
    _cache[inst_type] = (time.time(), rows)
    return rows


def class_symbols(cls, crypto_symbols, top=30, mtype="SPOT", base_url=OKX):
    """-> (symbols, note). Crypto + Spot = the dashboard's own list; everything else is discovered live from OKX,
    biggest volume first. Forex / Metals / Stocks only exist as swaps on OKX, so they use Perp even when Spot is picked."""
    if cls in NO_FEED:
        return [], f"{cls}: no verified free live feed yet (needs an API key)"
    if cls == "Crypto" and mtype == "SPOT":
        return list(crypto_symbols), ""
    inst = mtype if (cls in ("Crypto", "Meme coins") or mtype != "SPOT") else "SWAP"
    try:
        rows = _load(inst, base_url)
    except Exception as e:
        return [], f"OKX list unavailable ({type(e).__name__})"
    sel = [r for r in rows if r["cls"] == cls or (cls == "Metals" and r["cls"] == "Commodities")]
    sel.sort(key=lambda r: r["vol"], reverse=True)
    syms = [r["id"] for r in sel[:top]]
    return syms, ("" if syms else f"OKX lists no {cls} {inst} instruments right now")
