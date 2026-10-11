"""Candles for markets OKX does not list (forex majors, Nasdaq / US indices, EGX, Tadawul) from Yahoo Finance's
public chart endpoint. UNOFFICIAL and keyless: it can change or throttle without notice, and EGX / Tadawul quotes may be
delayed ~15 min. Symbols are written "Y:<yahoo symbol>" so the rest of the code can tell them from OKX instrument ids.
Frames match the OKX ones: columns time (naive UTC), open, high, low, close, volume."""
from __future__ import annotations

import pandas as pd
import requests

from modules.data_fetcher import aggregate_frame

PREFIX = "Y:"
URL = "https://{host}/v8/finance/chart/{sym}"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept": "application/json"}
HOSTS = ["query1.finance.yahoo.com", "query2.finance.yahoo.com"]
# our tf -> (yahoo interval, range, bars to merge)
TF = {"1m": ("1m", "7d", 1), "5m": ("5m", "60d", 1), "15m": ("15m", "60d", 1), "30m": ("30m", "60d", 1),
      "1h": ("60m", "730d", 1), "4h": ("60m", "730d", 4), "1d": ("1d", "5y", 1), "1w": ("1wk", "10y", 1)}

FOREX = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X", "USDEGP=X", "USDSAR=X"]
INDICES = ["^IXIC", "^NDX", "^GSPC", "^DJI", "^RUT", "^VIX", "^GDAXI", "^FTSE", "^N225", "^HSI"]
EGX = ["^CASE30", "COMI.CA", "HRHO.CA", "TMGH.CA", "SWDY.CA", "EAST.CA", "ORAS.CA", "ABUK.CA", "FWRY.CA", "ETEL.CA", "EKHO.CA", "PHDC.CA"]
TADAWUL = ["^TASI.SR", "2222.SR", "1120.SR", "2010.SR", "7010.SR", "1180.SR", "2380.SR", "1211.SR", "4030.SR", "2350.SR", "5110.SR", "1150.SR"]
BY_CLASS = {"Forex": FOREX, "Indices": INDICES, "Egypt (EGX)": EGX, "Saudi (Tadawul)": TADAWUL}


def symbols(cls: str) -> list[str]:
    return [PREFIX + s for s in BY_CLASS.get(cls, [])]


def is_yahoo(sym: str) -> bool:
    return isinstance(sym, str) and sym.startswith(PREFIX)


def parse_chart(d: dict) -> pd.DataFrame:
    """Yahoo v8 chart JSON -> OHLCV frame (rows with a missing OHLC value are dropped)."""
    res = ((d or {}).get("chart") or {}).get("result") or []
    if not res:
        err = ((d or {}).get("chart") or {}).get("error") or {}
        raise ValueError(err.get("description") or "no data")
    r = res[0]
    ts, q = r.get("timestamp") or [], ((r.get("indicators") or {}).get("quote") or [{}])[0]
    if not ts or not q.get("close"):
        raise ValueError("no candles")
    df = pd.DataFrame({"time": pd.to_datetime(pd.Series(ts, dtype="int64"), unit="s"), "open": q.get("open"), "high": q.get("high"),
                       "low": q.get("low"), "close": q.get("close"), "volume": q.get("volume") or [0] * len(ts)})
    df = df.dropna(subset=["open", "high", "low", "close"]).copy()
    df["volume"] = df["volume"].fillna(0).astype(float)
    for c in ("open", "high", "low", "close"):
        df[c] = df[c].astype(float)
    return df.reset_index(drop=True)


def get_yahoo_klines(sym: str, tf: str, limit: int = 300) -> pd.DataFrame:
    if tf not in TF:
        raise ValueError(f"Yahoo feed: timeframe {tf} not supported")
    iv, rg, n = TF[tf]
    ysym = requests.utils.quote(sym[len(PREFIX):] if is_yahoo(sym) else sym, safe="")
    r = None
    for host in HOSTS:   # second host as a fallback when one is throttled
        try:
            r = requests.get(URL.format(host=host, sym=ysym), params={"interval": iv, "range": rg}, headers=HDR, timeout=12)
        except requests.RequestException as e:
            r = None
            err = type(e).__name__
            continue
        if r.status_code == 200:
            break
    if r is None:
        raise RuntimeError(f"Yahoo unreachable ({err})")
    if r.status_code == 429:
        raise RuntimeError("Yahoo rate limit (429)")
    if r.status_code == 404:
        raise ValueError("Yahoo: unknown symbol")
    if r.status_code != 200:
        raise RuntimeError(f"Yahoo HTTP {r.status_code}")
    df = parse_chart(r.json())
    if n > 1:
        df = aggregate_frame(df, n, 60)
    return df.tail(limit).reset_index(drop=True)


_TV = {"^IXIC": "NASDAQ:IXIC", "^NDX": "NASDAQ:NDX", "^GSPC": "SP:SPX", "^DJI": "DJ:DJI", "^RUT": "TVC:RUT", "^VIX": "CBOE:VIX",
       "^GDAXI": "XETR:DAX", "^FTSE": "TVC:UKX", "^N225": "TVC:NI225", "^HSI": "TVC:HSI", "^CASE30": "EGX:EGX30", "^TASI.SR": "TADAWUL:TASI"}


def tv_symbol(sym: str) -> str:
    """"Y:..." -> TradingView symbol for the embedded chart."""
    y = sym[len(PREFIX):]
    if y in _TV:
        return _TV[y]
    if y.endswith("=X"):
        return "FX:" + y[:-2]
    if y.endswith(".CA"):
        return "EGX:" + y[:-3]
    if y.endswith(".SR"):
        return "TADAWUL:" + y[:-3]
    return y


EMBED_TFS = ("15m", "1h", "4h", "1d")


def embed(symbols, bars: int = 200) -> dict:
    """{ "Y:SYM": {"15m": [[ms,o,h,l,c,v], ...oldest first], "1h": ..., "4h": ..., "1d": ...} } for the browser Workspace
    (its page cannot call Yahoo itself - CORS - so the candles are handed over inside the page). Failed symbols are left out."""
    from modules.market_cache import fetch_frames
    ys = [x for x in symbols if is_yahoo(x)]
    if not ys:
        return {}
    frames, _errs = fetch_frames(ys, list(EMBED_TFS), limit=bars, workers=8)
    out = {}
    for sym in ys:
        d = {}
        for tf, df in (frames.get(sym) or {}).items():
            if df is not None and len(df):
                d[tf] = [[int(t.timestamp() * 1000), round(o, 6), round(h, 6), round(l, 6), round(c, 6), round(v, 2)]
                         for t, o, h, l, c, v in zip(df["time"], df["open"], df["high"], df["low"], df["close"], df["volume"])]
        if d:
            out[sym] = d
    return out
