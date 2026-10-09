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
_OKX_INTERVAL_MAP = {
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1h": "1H", "4h": "4H", "1d": "1D", "1w": "1W",
}


def get_binance_klines(symbol: str, interval: str = "1h", limit: int = 300):
    """Fetches OHLCV candles from OKX's public candles endpoint.
    Name kept as get_binance_klines so main.py doesn't need any changes -
    this now talks to OKX, which isn't geo-blocked on Streamlit Cloud."""
    okx_bar = _OKX_INTERVAL_MAP.get(interval, "1H")
    params = {"instId": symbol, "bar": okx_bar, "limit": limit}
    r = requests.get(OKX_CANDLES_URL, params=params, timeout=10)
    r.raise_for_status()
    raw = r.json().get("data", [])

    if not raw:
        return pd.DataFrame(columns=["time", "open", "high", "low", "close", "volume"])

    # OKX candles come newest-first with columns:
    # [ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]
    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "volCcy", "volCcyQuote", "confirm"
    ])
    df["time"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df = df.sort_values("time").reset_index(drop=True)
    return df[["time", "open", "high", "low", "close", "volume"]]


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
