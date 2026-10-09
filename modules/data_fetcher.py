
THE DATA CLERK
Only job: fetch raw OHLCV candles from MT5 (forex/metals/indices/stocks)
and Binance (crypto). Returns clean pandas DataFrames. No analysis here.

MetaTrader5 is Windows-only, so it is imported lazily inside the function
that needs it, not at the top of the file. This way the whole dashboard
still runs fine on Streamlit Cloud (Linux) for the Binance/crypto side.
"""

import pandas as pd
import requests
from config import BINANCE_KLINES_URL, BINANCE_DEPTH_URL, BINANCE_TRADES_URL


def get_mt5_data(symbol: str, timeframe, bars: int = 300):
    try:
        import MetaTrader5 as mt5
    except ImportError:
        raise RuntimeError(
            "MetaTrader5 is not available on this server (Windows-only library). "
            "Run this dashboard locally on Windows with MT5 open to see forex/metals/stocks data."
        )

    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize() failed: {mt5.last_error()}")

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        return None

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.rename(columns={"tick_volume": "volume"}, inplace=True)
    return df[["time", "open", "high", "low", "close", "volume"]]


def get_binance_klines(symbol: str, interval: str = "1h", limit: int = 300):
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
    r.raise_for_status()
    raw = r.json()

    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])
    df["time"] = pd.to_datetime(df["open_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df[["time", "open", "high", "low", "close", "volume"]]


def get_binance_order_book(symbol: str, limit: int = 20):
    params = {"symbol": symbol, "limit": limit}
    r = requests.get(BINANCE_DEPTH_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    bids = pd.DataFrame(data["bids"], columns=["price", "qty"]).astype(float)
    asks = pd.DataFrame(data["asks"], columns=["price", "qty"]).astype(float)
    return bids, asks


def get_binance_time_and_sales(symbol: str, limit: int = 30):
    params = {"symbol": symbol, "limit": limit}
    r = requests.get(BINANCE_TRADES_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["price"] = df["price"].astype(float)
    df["qty"] = df["qty"].astype(float)
    df["side"] = df["isBuyerMaker"].apply(lambda x: "Sell" if x else "Buy")
    return df[["time", "price", "qty", "side"]]
[10/9/2026 3:30 PM] Saud 6868: """
THE DATA CLERK
Only job: fetch raw OHLCV candles from MT5 (forex/metals/indices/stocks)
and Binance (crypto). Returns clean pandas DataFrames. No analysis here.
"""

import pandas as pd
import requests
from config import BINANCE_KLINES_URL, BINANCE_DEPTH_URL, BINANCE_TRADES_URL

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
            "MetaTrader5 is not available on this server. Run this dashboard "
            "locally on Windows with MT5 open to see forex/metals/stocks data."
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


def get_binance_klines(symbol: str, interval: str = "1h", limit: int = 300):
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
    r.raise_for_status()
    raw = r.json()

    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])
    df["time"] = pd.to_datetime(df["open_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df[["time", "open", "high", "low", "close", "volume"]]


def get_binance_order_book(symbol: str, limit: int = 20):
    params = {"symbol": symbol, "limit": limit}
    r = requests.get(BINANCE_DEPTH_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    bids = pd.DataFrame(data["bids"], columns=["price", "qty"]).astype(float)
    asks = pd.DataFrame(data["asks"], columns=["price", "qty"]).astype(float)
    return bids, asks


def get_binance_time_and_sales(symbol: str, limit: int = 30):
    params = {"symbol": symbol, "limit": limit}
    r = requests.get(BINANCE_TRADES_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["price"] = df["price"].astype(float)
    df["qty"] = df["qty"].astype(float)
    df["side"] = df["isBuyerMaker"].apply(lambda x: "Sell" if x else "Buy")
    return df[["time", "price", "qty", "side"]]
`
