"""
THE DATA CLERK
Only job: fetch raw OHLCV candles from MT5 (forex/metals/indices/stocks)
and Binance (crypto). Returns clean pandas DataFrames. No analysis here.

MetaTrader5 is Windows-only, so it is imported lazily inside the function
that needs it, not at the top of the file. This way the whole dashboard
still runs fine on Streamlit Cloud (Linux) for the Binance/crypto side.
Timeframe is passed as a simple string ("H1", "M15", etc.) so main.py
never needs to import MetaTrader5 itself.
"""

import pandas as pd
import requests
from config import OKX_CANDLES_URL, OKX_BOOK_URL, OKX_TRADES_URL

_TIMEFRAME_MAP_NAMES = {
    "M5": "TIMEFRAME_M5", "M15": "TIMEFRAME_M15",
    "H1": "TIMEFRAME_H1", "H4": "TIMEFRAME_H4",
    "D1": "TIMEFRAME_D1", "W1": "TIMEFRAME_W1", "MN1": "TIMEFRAME_MN1",
}


def get_mt5_data(symbol: str, timeframe_label: str = "H1", bars: int = 300):
    try:
        import MetaTrader5 as mt5
    except ImportError:
        raise RuntimeError(
            "MetaTrader5 is not available on this server (Windows-only library). "
            "Run this dashboard locally on Windows with MT5 open to see forex/metals/stocks data."
        )

    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize() failed: {mt5.last_error()}")

    tf_attr = _TIMEFRAME_MAP_NAMES.get(timeframe_label, "TIMEFRAME_H1")
    timeframe = getattr(mt5, tf_attr)

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        return None

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.rename(columns={"tick_volume": "volume"}, inplace=True)
    return df[["time", "open", "high", "low", "close", "volume"]]


# OKX interval codes differ from Binance's ("1h" -> "1H", "15m" -> "15m", etc.)
# 2h is native on OKX; 6h / 12h / 3d / 1M use its UTC variants. 13m, 3h, 7h and 8h are NOT OKX bar sizes: they are built
# from 1m / 1h candles (buckets aligned to the UTC epoch).
_OKX_INTERVAL_MAP = {
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1h": "1H", "2h": "2H", "4h": "4H", "6h": "6Hutc", "12h": "12Hutc", "1d": "1D", "3d": "3Dutc", "1w": "1W", "1mo": "1Mutc",
}
AGG_INTERVALS = {"13m": ("1m", 13), "3h": ("1h", 3), "7h": ("1h", 7), "8h": ("1h", 8)}


def _okx_frame(symbol: str, okx_bar: str, limit: int, after_ms=None, history=False):
    url = OKX_CANDLES_URL.replace("/candles", "/history-candles") if history else OKX_CANDLES_URL
    params = {"instId": symbol, "bar": okx_bar, "limit": limit}
    if after_ms:
        params["after"] = after_ms
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    raw = r.json().get("data", [])
    cols = ["time", "open", "high", "low", "close", "volume"]
    if not raw:
        return pd.DataFrame(columns=cols)
    # OKX candles come newest-first with columns: [ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]
    df = pd.DataFrame([x[:6] for x in raw], columns=["open_time", "open", "high", "low", "close", "volume"])
    df["time"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df.sort_values("time").reset_index(drop=True)[cols]


def aggregate_frame(df, n: int, base_minutes: int):
    """Resample candles into n-times-longer buckets aligned to the UTC epoch; the oldest (usually incomplete) bucket is dropped."""
    if df.empty:
        return df
    w = n * base_minutes * 60
    t = (df["time"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)
    g = (t // w) * w
    out = df.groupby(g).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), volume=("volume", "sum"))
    out["time"] = pd.Timestamp("1970-01-01") + pd.to_timedelta(out.index.values, unit="s")
    out = out.reset_index(drop=True)[["time", "open", "high", "low", "close", "volume"]]
    return out.iloc[1:].reset_index(drop=True)


def get_binance_klines(symbol: str, interval: str = "1h", limit: int = 300):
    """Fetches OHLCV candles from OKX's public candles endpoint.
    Name kept as get_binance_klines so main.py doesn't need any changes -
    this now talks to OKX, which isn't geo-blocked on Streamlit Cloud."""
    if interval in AGG_INTERVALS:
        base, n = AGG_INTERVALS[interval]
        want = min(limit, 90) * n + n          # base candles needed (history is paged 100 at a time)
        df = _okx_frame(symbol, _OKX_INTERVAL_MAP[base], min(300, want))
        guard = 0
        while len(df) < want and guard < 40 and not df.empty:
            guard += 1
            more = _okx_frame(symbol, _OKX_INTERVAL_MAP[base], 100, after_ms=int(df["time"].iloc[0].timestamp() * 1000), history=True)
            if more.empty:
                break
            df = pd.concat([more, df], ignore_index=True)
        return aggregate_frame(df, n, 1 if base == "1m" else 60)
    return _okx_frame(symbol, _OKX_INTERVAL_MAP.get(interval, "1H"), limit)


def get_binance_order_book(symbol: str, limit: int = 20):
    """Fetches live order book depth from OKX's public books endpoint.
    Name kept as get_binance_order_book so main.py/crypto_extras.py don't
    need any changes - this now talks to OKX instead of Binance."""
    params = {"instId": symbol, "sz": limit}
    r = requests.get(OKX_BOOK_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("data", [])
    if not data:
        empty = pd.DataFrame(columns=["price", "qty"])
        return empty, empty
    book = data[0]
    # OKX format per level: [price, size, liquidated_orders, num_orders]
    bids = pd.DataFrame(book["bids"], columns=["price", "qty", "_liq", "_n"])[["price", "qty"]].astype(float)
    asks = pd.DataFrame(book["asks"], columns=["price", "qty", "_liq", "_n"])[["price", "qty"]].astype(float)
    return bids, asks


def get_binance_time_and_sales(symbol: str, limit: int = 30):
    """Fetches recent trades (time & sales) from OKX's public trades endpoint.
    Name kept as get_binance_time_and_sales so main.py/crypto_extras.py don't
    need any changes - this now talks to OKX instead of Binance."""
    params = {"instId": symbol, "limit": limit}
    r = requests.get(OKX_TRADES_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("data", [])
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms")
    df["price"] = df["px"].astype(float)
    df["qty"] = df["sz"].astype(float)
    df["side"] = df["side"].apply(lambda x: "Buy" if x == "buy" else "Sell")
    return df[["time", "price", "qty", "side"]]
