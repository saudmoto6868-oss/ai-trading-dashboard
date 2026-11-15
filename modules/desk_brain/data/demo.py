"""Deterministic synthetic data so the whole desk runs offline. Every widget fed by
this module is labelled DEMO in the UI: it is for testing the pipeline, never for trading."""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

_START = {"EURUSD=X": 1.08, "GBPUSD=X": 1.27, "USDJPY=X": 150.0, "AUDUSD=X": 0.66,
          "NZDUSD=X": 0.60, "USDCAD=X": 1.36, "USDCHF=X": 0.88, "EURJPY=X": 162.0,
          "GBPJPY=X": 190.0, "AUDJPY=X": 99.0, "EURGBP=X": 0.85, "GC=F": 2400.0,
          "^GSPC": 5600.0, "^NDX": 19500.0, "^VIX": 16.0, "^TNX": 4.2, "DX-Y.NYB": 104.0,
          "SI=F": 30.0, "BTC-USD": 90000.0, "ETH-USD": 3200.0}


def _seed(*parts: str) -> int:
    return int(hashlib.md5("|".join(parts).encode()).hexdigest()[:8], 16)


def _base_price(ticker: str) -> float:
    if ticker in _START:
        return _START[ticker]
    return 1.0 + (_seed(ticker) % 1000) / 500.0


def ohlc(ticker: str, interval: str = "1d", bars: int = 600) -> pd.DataFrame:
    rng = np.random.default_rng(_seed(ticker, interval))
    step = {"1d": timedelta(days=1), "1h": timedelta(hours=1), "15m": timedelta(minutes=15), "5m": timedelta(minutes=5), "1m": timedelta(minutes=1)}[interval]
    vol = {"1d": 0.006, "1h": 0.0018, "15m": 0.0009, "5m": 0.0005, "1m": 0.00025}[interval]
    if ticker == "^VIX":
        vol *= 6
    drift = rng.normal(0, vol / 8)
    # regime switches give the trend tools something to find
    rets = rng.normal(drift, vol, bars)
    for k in range(0, bars, 120):
        rets[k:k + 120] += rng.normal(0, vol / 4)
    close = _base_price(ticker) * np.exp(np.cumsum(rets))
    openp = np.r_[close[0], close[:-1]]
    spread = np.abs(rng.normal(0, vol * 0.6, bars)) * close
    high = np.maximum(openp, close) + spread
    low = np.minimum(openp, close) - spread
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    idx = pd.date_range(end=end, periods=bars, freq=step)
    return pd.DataFrame({"Open": openp, "High": high, "Low": low, "Close": close,
                         "Volume": rng.integers(1000, 5000, bars)}, index=idx)


def cot(code: str, weeks: int = 160) -> pd.DataFrame:
    rng = np.random.default_rng(_seed("cot", code))
    oi = 200_000 + rng.normal(0, 5000, weeks).cumsum()
    net = (rng.normal(0, 6000, weeks)).cumsum()
    longs = np.abs(oi) * 0.3 + np.maximum(net, 0)
    shorts = np.abs(oi) * 0.3 + np.maximum(-net, 0)
    end = pd.Timestamp.now(tz="UTC").normalize()
    idx = pd.date_range(end=end, periods=weeks, freq="7D")
    return pd.DataFrame({"long": longs, "short": shorts, "oi": np.abs(oi)}, index=idx)


def rate(ccy: str) -> pd.Series:
    base = {"USD": 4.5, "EUR": 3.0, "GBP": 4.6, "JPY": 0.3, "AUD": 4.2, "NZD": 4.8,
            "CAD": 3.4, "CHF": 0.8}.get(ccy, 2.0)
    rng = np.random.default_rng(_seed("rate", ccy))
    vals = base + rng.normal(0, 0.08, 24).cumsum()
    idx = pd.date_range(end=pd.Timestamp.now().normalize(), periods=24, freq="MS")
    return pd.Series(vals, index=idx)


def calendar() -> list[dict]:
    now = datetime.now(timezone.utc)
    return [
        {"title": "CPI m/m (DEMO)", "country": "USD", "impact": "High",
         "date": (now + timedelta(hours=30)).isoformat(), "forecast": "0.3%", "previous": "0.2%"},
        {"title": "Cash Rate (DEMO)", "country": "AUD", "impact": "High",
         "date": (now + timedelta(hours=6)).isoformat(), "forecast": "4.10%", "previous": "4.10%"},
        {"title": "PMI (DEMO)", "country": "EUR", "impact": "Medium",
         "date": (now + timedelta(hours=50)).isoformat(), "forecast": "47.1", "previous": "46.8"},
    ]
