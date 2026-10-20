"""Hyperliquid public API (no key) for the server side: candles + market list of the "xyz" builder dex, which lists TradFi
perpetuals - gold / silver / platinum / palladium / copper, WTI / Brent / natural gas / heating oil, S&P 500 / Nasdaq 100 /
Nikkei / KOSPI, EUR / GBP / JPY, TLT and ~100 US / Asian stocks. Symbols are written "HL:xyz:GOLD".
These are PERPETUAL contracts: their price tracks the underlying through an oracle and trades 24/7 (also when the real market
is closed), so it can differ slightly from spot / futures. Request bodies follow Hyperliquid's documented /info types
(metaAndAssetCtxs with a "dex" field, candleSnapshot). NOT reached from the build sandbox (egress proxy) - tested with mocks;
the market list and prices were cross-checked against the Coinversa Pulse connector (Hyperliquid data) on 2026-10-17."""
from __future__ import annotations

import threading
import time

import pandas as pd
import requests

API = "https://api.hyperliquid.xyz/info"
PREFIX = "HL:"
DEX = "xyz"
CAT = {"GOLD": "Metals", "SILVER": "Metals", "PLATINUM": "Metals", "PALLADIUM": "Metals", "COPPER": "Metals",
       "CL": "Oil & Gas", "BRENTOIL": "Oil & Gas", "NATGAS": "Oil & Gas", "HO": "Oil & Gas",
       "SP500": "Indices", "XYZ100": "Indices", "JP225": "Indices", "KR200": "Indices",
       "EUR": "Forex", "GBP": "Forex", "JPY": "Forex", "AUD": "Forex", "CAD": "Forex", "CHF": "Forex", "TLT": "Bonds"}
TV = {"GOLD": "OANDA:XAUUSD", "SILVER": "OANDA:XAGUSD", "PLATINUM": "OANDA:XPTUSD", "PALLADIUM": "OANDA:XPDUSD", "COPPER": "COMEX:HG1!",
      "CL": "TVC:USOIL", "BRENTOIL": "TVC:UKOIL", "NATGAS": "NYMEX:NG1!", "HO": "NYMEX:HO1!", "SP500": "SP:SPX", "XYZ100": "NASDAQ:NDX",
      "JP225": "TVC:NI225", "KR200": "KRX:KOSPI200", "EUR": "FX:EURUSD", "GBP": "FX:GBPUSD", "JPY": "FX:USDJPY", "TLT": "NASDAQ:TLT"}
IV = {"1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h", "2h": "2h", "4h": "4h", "8h": "8h", "12h": "12h",
      "1d": "1d", "3d": "3d", "1w": "1w", "1mo": "1M"}
MS = {"1m": 6e4, "3m": 18e4, "5m": 3e5, "15m": 9e5, "30m": 18e5, "1h": 36e5, "2h": 72e5, "4h": 144e5, "8h": 288e5, "12h": 432e5,
      "1d": 864e5, "3d": 2592e5, "1w": 6048e5, "1M": 2592e6}
_cache: dict = {}
_lock = threading.Lock()


def is_hl(sym: str) -> bool:
    return isinstance(sym, str) and sym.startswith(PREFIX)


def base(sym: str) -> str:
    return sym.split(":")[-1]


def category(sym: str) -> str:
    return CAT.get(base(sym), "Stocks")


def tv_symbol(sym: str) -> str:
    """Best TradingView equivalent of the underlying (the perp itself is not on TradingView under a stable name)."""
    b = base(sym)
    return TV.get(b, b)


def _post(body: dict, timeout: int = 12):
    r = requests.post(API, json=body, timeout=timeout)
    if r.status_code == 429:
        raise RuntimeError("Hyperliquid rate limit (429)")
    if r.status_code != 200:
        raise RuntimeError(f"Hyperliquid HTTP {r.status_code}")
    return r.json()


def markets(dex: str = DEX, ttl: int = 60) -> list[dict]:
    """[{id, cls, vol, px, prev}] of live markets (delisted or no volume and no open interest left out), biggest 24h volume first."""
    now = time.time()
    with _lock:
        hit = _cache.get(("m", dex))
    if hit and now - hit[0] < ttl:
        return hit[1]
    meta, ctxs = _post({"type": "metaAndAssetCtxs", "dex": dex})
    rows = []
    for u, c in zip(meta.get("universe", []), ctxs):
        px = float(c.get("midPx") or c.get("markPx") or 0)
        vol, oi = float(c.get("dayNtlVlm") or 0), float(c.get("openInterest") or 0)
        if u.get("isDelisted") or px <= 0 or (not vol and not oi):
            continue
        sid = PREFIX + u["name"]
        rows.append({"id": sid, "cls": category(sid), "vol": vol, "px": px, "prev": float(c.get("prevDayPx") or 0)})
    rows.sort(key=lambda r: r["vol"], reverse=True)
    with _lock:
        _cache[("m", dex)] = (now, rows)
    return rows


def symbols(cls: str, top: int = 12) -> list[str]:
    """Hyperliquid TradFi markets of one asset class (empty on any error, so callers can fall back)."""
    try:
        return [r["id"] for r in markets() if r["cls"] == cls][:top]
    except Exception:
        return []


def parse_candles(rows) -> pd.DataFrame:
    df = pd.DataFrame([{"time": pd.to_datetime(int(k["t"]), unit="ms"), "open": float(k["o"]), "high": float(k["h"]), "low": float(k["l"]),
                        "close": float(k["c"]), "volume": float(k.get("v") or 0)} for k in rows or []])
    if df.empty:
        raise ValueError("Hyperliquid: no candles")
    return df.sort_values("time").drop_duplicates("time").reset_index(drop=True)


def get_klines(sym: str, tf: str, limit: int = 300) -> pd.DataFrame:
    if tf not in IV:
        raise ValueError(f"Hyperliquid: timeframe {tf} not available")
    iv = IV[tf]
    end = int(time.time() * 1000)
    rows = _post({"type": "candleSnapshot", "req": {"coin": sym[len(PREFIX):], "interval": iv, "startTime": int(end - (limit + 1) * MS[iv]), "endTime": end}})
    return parse_candles(rows).tail(limit).reset_index(drop=True)
