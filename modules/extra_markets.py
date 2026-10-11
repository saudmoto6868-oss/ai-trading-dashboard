"""Free extra quote sources. Only endpoints I could confirm the shape of are used:
  - gold-api.com  GET /price/XAU  (keyless)        -> {"price": 2xxx.x, ...}
  - Finnhub       GET /quote?symbol=AAPL&token=KEY -> {"c": last, "dp": % change, "t": unix}   (free: 60 calls/min, US stocks)
Egyptian (EGX) and Saudi (Tadawul) feeds are NOT wired: no verified free endpoint yet."""
import requests

GOLD_URL = "https://api.gold-api.com/price/XAU"
FINNHUB_QUOTE = "https://finnhub.io/api/v1/quote"


def parse_gold(d):
    p = float(d["price"])
    if p <= 0:
        raise ValueError("bad price")
    return {"name": "Gold XAU", "symbol": "XAU/USD", "price": p, "pct": None, "ok": True}


def gold_spot(timeout=8):
    r = requests.get(GOLD_URL, timeout=timeout)
    r.raise_for_status()
    return parse_gold(r.json())


def parse_finnhub(sym, d):
    if not d or not d.get("c"):      # Finnhub answers {"c":0,...} for unknown symbols
        raise ValueError("no data")
    return {"name": sym, "symbol": sym, "price": float(d["c"]), "pct": float(d.get("dp") or 0), "ok": True}


def finnhub_quote(sym, key, timeout=8):
    r = requests.get(FINNHUB_QUOTE, params={"symbol": sym, "token": key}, timeout=timeout)
    r.raise_for_status()
    return parse_finnhub(sym, r.json())
