"""Free data sources. Every function returns (data, source_label).

Live sources (all free, no key):
  prices   -> Yahoo Finance via yfinance (delayed; fine for daily / hourly context)
  COT      -> CFTC Public Reporting (Socrata), Legacy Futures-Only dataset 6dca-aqww
  rates    -> FRED CSV download (OECD 3-month interbank series, monthly)
  calendar -> ForexFactory weekly JSON feed (unofficial; forecast/previous only)

If a live call fails, or DESK_DATA_MODE=demo, the function returns synthetic data and
labels it "demo" so the UI can flag it.
"""
from __future__ import annotations

import io
import logging
import os
import threading
import time
from urllib.parse import quote
from typing import Any

import pandas as pd
import requests

from ..config import DATA_MODE
from . import demo
from .cache import cached, last_good

log = logging.getLogger("desk.sources")
UA = {"User-Agent": "ai-desk/0.1 (research prototype)"}

def _live() -> bool:
    return DATA_MODE != "demo"


# How far back each base interval goes (days) and how long a fetch stays fresh (seconds).
_DAYS = {"1d": 3650, "1h": 59, "15m": 29, "5m": 29, "1m": 6}
_TTL = {"1d": 3600, "1h": 600, "15m": 120, "5m": 60, "1m": 30}
# Derived timeframes are resampled from a base one, so they cost no extra request.
_DERIVED = {"30m": ("15m", "30min"), "4h": ("1h", "4h"), "1w": ("1d", "W-SUN")}
TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]

BROWSER_UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept": "application/json"}
# Free hosts throttle bursts; a scan asks for ~50 tickers, so keep only a few requests in flight.
_net = threading.BoundedSemaphore(int(os.getenv("DESK_NET_CONCURRENCY", "4")))
# ticker -> {"interval", "source", "rows", "error", "ts"}: what the Sources pill shows.
STATUS: dict[str, dict] = {}


def _binance_symbol(ticker: str) -> str | None:
    from ..config import UNIVERSE
    for m in UNIVERSE.values():
        if m.get("yf") == ticker and m.get("binance"):
            return m["binance"]
    return None


def _frame(ts, o, h, l, c, v) -> pd.DataFrame:
    df = pd.DataFrame({"Open": o, "High": h, "Low": l, "Close": c, "Volume": v},
                      index=pd.to_datetime(ts, unit="s", utc=True))
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["Open", "High", "Low", "Close"])
    df["Volume"] = df["Volume"].fillna(0)
    return df[~df.index.duplicated(keep="last")].sort_index()


def _yahoo_chart(ticker: str, interval: str) -> pd.DataFrame:
    """Yahoo's public chart endpoint, called directly (no cookie/crumb dance like yfinance)."""
    end = int(time.time())
    params = {"period1": end - _DAYS[interval] * 86400, "period2": end, "interval": interval,
              "includePrePost": "false", "events": "div,split"}
    err = None
    for host in ("query1", "query2"):
        try:
            with _net:
                r = requests.get(f"https://{host}.finance.yahoo.com/v8/finance/chart/{quote(ticker)}",
                                 params=params, headers=BROWSER_UA, timeout=12)
            if r.status_code == 429:
                err = "yahoo 429 (rate limit)"
                time.sleep(1.5)
                continue
            r.raise_for_status()
            res = r.json()["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            return _frame(res["timestamp"], q["open"], q["high"], q["low"], q["close"], q.get("volume"))
        except Exception as e:
            err = f"yahoo {host}: {e}"
    raise RuntimeError(err or "yahoo failed")


def _binance(symbol: str, interval: str) -> pd.DataFrame:
    """Binance public market data (the data-api mirror also answers from US cloud regions)."""
    err = None
    for host in ("https://data-api.binance.vision", "https://api.binance.com"):
        try:
            with _net:
                r = requests.get(f"{host}/api/v3/klines", params={"symbol": symbol, "interval": interval, "limit": 1000},
                                 headers=UA, timeout=12)
            r.raise_for_status()
            k = r.json()
            return _frame([x[0] // 1000 for x in k], [x[1] for x in k], [x[2] for x in k],
                          [x[3] for x in k], [x[4] for x in k], [x[5] for x in k])
        except Exception as e:
            err = f"binance: {e}"
    raise RuntimeError(err or "binance failed")


# Hyperliquid "xyz" dex: keyless TradFi perpetuals that track the underlying (24/7, may differ slightly from spot).
# A backup for cloud hosts that Yahoo throttles. Only markets whose quote direction matches our symbol are mapped.
HL_XYZ = {"GC=F": "xyz:GOLD", "SI=F": "xyz:SILVER", "^GSPC": "xyz:SP500", "^NDX": "xyz:XYZ100",
          "EURUSD=X": "xyz:EUR", "GBPUSD=X": "xyz:GBP", "USDJPY=X": "xyz:JPY"}
_HL_MS = {"1d": 86_400_000, "1h": 3_600_000, "15m": 900_000, "5m": 300_000, "1m": 60_000}


def _hyperliquid(coin: str, interval: str) -> pd.DataFrame:
    end = int(time.time() * 1000)
    body = {"type": "candleSnapshot", "req": {"coin": coin, "interval": interval,
                                              "startTime": end - 4900 * _HL_MS[interval], "endTime": end}}
    with _net:
        r = requests.post("https://api.hyperliquid.xyz/info", json=body, headers=UA, timeout=12)
    r.raise_for_status()
    k = r.json() or []
    return _frame([int(x["t"]) // 1000 for x in k], [x["o"] for x in k], [x["h"] for x in k],
                  [x["l"] for x in k], [x["c"] for x in k], [x.get("v") or 0 for x in k])


def _yfinance(ticker: str, interval: str) -> pd.DataFrame:
    import yfinance as yf
    period = {"1d": "10y", "1h": "60d", "15m": "30d", "5m": "30d", "1m": "7d"}[interval]
    with _net:
        df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def _resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
    if rule == "W-SUN":
        out = df.resample(rule, label="left", closed="left").agg(agg)
    else:
        out = df.resample(rule, origin="epoch").agg(agg)
    return out.dropna(subset=["Open", "Close"])


def prices(ticker: str, interval: str = "1d") -> tuple[pd.DataFrame, str]:
    """OHLCV for a ticker. Live chain: Binance (crypto) -> Yahoo chart API -> Hyperliquid xyz (gold, silver, indices, majors) -> yfinance ->
    last good copy on disk -> demo. 4h and 1w are resampled from 1h and 1d."""
    if interval in _DERIVED:
        base, rule = _DERIVED[interval]
        df, src = prices(ticker, base)
        return _resample(df, rule), src

    key = f"px:{ticker}:{interval}:{DATA_MODE}"

    def fetch() -> tuple[pd.DataFrame, str]:
        errors = []
        if _live():
            chain = []
            bsym = _binance_symbol(ticker)
            if bsym:
                chain.append(("binance", lambda: _binance(bsym, interval)))
            chain.append(("yahoo", lambda: _yahoo_chart(ticker, interval)))
            if ticker in HL_XYZ:
                chain.append(("hyperliquid", lambda: _hyperliquid(HL_XYZ[ticker], interval)))
            chain.append(("yfinance", lambda: _yfinance(ticker, interval)))
            for name, fn in chain:
                try:
                    df = fn()
                    if len(df) > 30:
                        STATUS[ticker] = {"interval": interval, "source": name, "rows": len(df), "error": None, "ts": time.time()}
                        return df, name
                    errors.append(f"{name}: {len(df)} rows")
                except Exception as e:
                    errors.append(str(e)[:160])
            old = last_good(key)
            if old is not None:
                STATUS[ticker] = {"interval": interval, "source": "cache", "rows": len(old[0]), "error": "; ".join(errors), "ts": time.time()}
                log.warning("live prices failed for %s %s, using last good copy: %s", ticker, interval, errors)
                return old[0], "cache"
            log.warning("live prices failed for %s %s, using demo: %s", ticker, interval, errors)
        STATUS[ticker] = {"interval": interval, "source": "demo", "rows": 0, "error": "; ".join(errors) or None, "ts": time.time()}
        return demo.ohlc(ticker, interval), "demo"

    return cached(key, _TTL[interval], fetch, keep=lambda v: v[1] not in ("demo", "cache") or not _live())


def source_report() -> dict:
    """Per-ticker data health for the UI."""
    rows = [{"ticker": t, **v} for t, v in sorted(STATUS.items())]
    live = sum(1 for r in rows if r["source"] not in ("demo", "cache"))
    return {"mode": DATA_MODE, "live": live, "total": len(rows), "rows": rows}


def cot(code: str) -> tuple[pd.DataFrame, str]:
    """Non-commercial (large speculator) long/short and open interest, weekly."""
    def fetch() -> tuple[pd.DataFrame, str]:
        if _live():
            try:
                url = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
                params = {"cftc_contract_market_code": code,
                          "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 160}
                r = requests.get(url, params=params, headers=UA, timeout=20)
                r.raise_for_status()
                rows = r.json()
                if rows:
                    df = pd.DataFrame({
                        "long": [float(x["noncomm_positions_long_all"]) for x in rows],
                        "short": [float(x["noncomm_positions_short_all"]) for x in rows],
                        "oi": [float(x["open_interest_all"]) for x in rows],
                    }, index=pd.to_datetime([x["report_date_as_yyyy_mm_dd"] for x in rows], utc=True))
                    return df.sort_index(), "cftc"
            except Exception as e:
                log.warning("cftc failed for %s: %s", code, e)
        return demo.cot(code), "demo"

    return cached(f"cot:{code}:{DATA_MODE}", 6 * 3600, fetch)


def rate(series_id: str, ccy: str) -> tuple[pd.Series, str]:
    def fetch() -> tuple[pd.Series, str]:
        if _live():
            try:
                url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
                r = requests.get(url, headers=UA, timeout=20)
                r.raise_for_status()
                df = pd.read_csv(io.StringIO(r.text))
                s = pd.to_numeric(df.iloc[:, 1], errors="coerce")
                s.index = pd.to_datetime(df.iloc[:, 0])
                s = s.dropna()
                if len(s) > 3:
                    return s.iloc[-36:], "fred"
            except Exception as e:
                log.warning("fred failed for %s: %s", series_id, e)
        return demo.rate(ccy), "demo"

    return cached(f"rate:{series_id}:{DATA_MODE}", 12 * 3600, fetch)


def calendar() -> tuple[list[dict[str, Any]], str]:
    def fetch() -> tuple[list[dict[str, Any]], str]:
        if _live():
            try:
                r = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json",
                                 headers=UA, timeout=20)
                r.raise_for_status()
                return r.json(), "forexfactory"
            except Exception as e:
                log.warning("calendar failed: %s", e)
        return demo.calendar(), "demo"

    return cached(f"cal:{DATA_MODE}", 1800, fetch)
