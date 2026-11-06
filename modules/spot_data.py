"""Spot desk data (page 11): live prices + high-timeframe candles. Public APIs only, no keys.

- Crypto: OKX spot tickers (USDT pairs, stablecoins left out), biggest 24h volume first; candles via market_cache.
- Metals: live price from Hyperliquid xyz perps (GOLD / SILVER / PLATINUM / PALLADIUM per troy oz, COPPER per lb);
  long history (weekly / monthly / yearly) from Yahoo futures (GC=F, SI=F, PL=F, PA=F, HG=F) because the xyz
  markets are young. Perp and futures prices differ slightly from spot.
- USD/EGP: Yahoo USDEGP=X (unofficial, delayed); the time of the rate is returned with it.
- Yearly candles are built from monthly ones (context only: BTC has ~9 yearly bars)."""
from __future__ import annotations

import time

import pandas as pd
import requests

OKX = "https://www.okx.com/api/v5"
STABLES = {"USDC", "USDT", "DAI", "TUSD", "FDUSD", "USDD", "PYUSD", "EURT", "USDG", "USDE", "USDP", "BUSD", "EURC"}
METAL_HL = {"GOLD": "HL:xyz:GOLD", "SILVER": "HL:xyz:SILVER", "PLATINUM": "HL:xyz:PLATINUM", "PALLADIUM": "HL:xyz:PALLADIUM", "COPPER": "HL:xyz:COPPER"}
METAL_Y = {"GOLD": "Y:GC=F", "SILVER": "Y:SI=F", "PLATINUM": "Y:PL=F", "PALLADIUM": "Y:PA=F", "COPPER": "Y:HG=F"}
FX_SYM = "Y:USDEGP=X"
_cache: dict = {}


def _cached(key, ttl, fn):
    hit = _cache.get(key)
    now = time.time()
    if hit and now - hit[0] < ttl:
        return hit[1]
    v = fn()
    _cache[key] = (now, v)
    return v


def crypto_tickers(base_url: str = OKX) -> list[dict]:
    """[{sym 'BTC-USDT', base, last, chg24 %, vol_usd}] biggest volume first (cached 60 s)."""
    def load():
        d = requests.get(f"{base_url}/market/tickers", params={"instType": "SPOT"}, timeout=10).json().get("data", [])
        rows = []
        for x in d:
            iid = x.get("instId", "")
            b, _, q = iid.partition("-")
            if q != "USDT" or b in STABLES:
                continue
            last, op = float(x.get("last") or 0), float(x.get("sodUtc0") or x.get("open24h") or 0)
            if last <= 0:
                continue
            rows.append({"sym": iid, "base": b, "last": last, "chg24": (last / op - 1) * 100 if op else None,
                         "vol_usd": float(x.get("volCcy24h") or 0)})
        rows.sort(key=lambda r: r["vol_usd"], reverse=True)
        return rows
    return _cached(("ct", base_url), 60, load)


def metal_prices() -> dict:
    """{asset: {px, prev, src}} live from Hyperliquid; Yahoo daily close when Hyperliquid is unreachable."""
    def load():
        out = {}
        try:
            from modules import hl_feed
            by = {r["id"]: r for r in hl_feed.markets()}
            for a, s in METAL_HL.items():
                r = by.get(s)
                if r:
                    out[a] = {"px": r["px"], "prev": r["prev"], "src": "Hyperliquid (perp, live)"}
        except Exception:
            pass
        for a, s in METAL_Y.items():
            if a in out:
                continue
            try:
                df = candles(s, "1d", 5)
                out[a] = {"px": float(df["close"].iloc[-1]), "prev": float(df["close"].iloc[-2]) if len(df) > 1 else 0.0, "src": "Yahoo futures (delayed)"}
            except Exception:
                pass
        return out
    return _cached(("mp",), 20, load)


def usd_egp() -> dict:
    """{rate, time, src} or {} when unreachable."""
    def load():
        try:
            df = candles(FX_SYM, "1d", 5)
            return {"rate": float(df["close"].iloc[-1]), "time": str(df["time"].iloc[-1])[:16], "src": "Yahoo USDEGP=X (delayed)"}
        except Exception as e:
            return {"error": type(e).__name__}
    return _cached(("fx",), 300, load)


def candles(sym: str, tf: str, limit: int = 300) -> pd.DataFrame:
    """tf in 1d / 1w / 1mo / 1y (yearly = monthly bars grouped by calendar year)."""
    from modules.market_cache import get_klines
    if tf == "1y":
        m = get_klines(sym, "1mo", 300)
        return yearly(m)
    return get_klines(sym, tf, limit)


def yearly(m: pd.DataFrame) -> pd.DataFrame:
    if m is None or m.empty:
        return m
    y = pd.to_datetime(m["time"]).dt.year
    out = m.groupby(y).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), volume=("volume", "sum"))
    out["time"] = pd.to_datetime(out.index.astype(str) + "-01-01")
    return out.reset_index(drop=True)[["time", "open", "high", "low", "close", "volume"]]


def history_symbol(asset: str) -> str:
    """Symbol used for the high-timeframe analysis of an asset: metals -> Yahoo futures, crypto -> OKX spot pair."""
    a = asset.upper()
    return METAL_Y.get(a, a if "-" in a else f"{a}-USDT")
