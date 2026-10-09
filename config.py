
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
[10/9/2026 2:30 PM] Saud 6868: """
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
[10/9/2026 2:43 PM] Saud 6868: تمام، ممتاز! ده بالظبط آخر سطر صحيح للملف (return df[["time", "price", "qty", "side"]])، فالملف شكله كامل ومش ناقص حاجة من الآخر.

يبقى المشكلة في مكان تاني. جرب كده: دوس Ctrl+F في data_fetcher.py وابحث عن كلمة def get_binance_klines، وقولي هل لقيتها، وهي جوه نفس المستوى (نفس المسافة من الشمال) زي def get_mt5_data؟
[10/9/2026 2:50 PM] Saud 6868: آه لقيتها، دي المشكلة بالظبط! سطر 8 المفروض يكون import streamlit.components.v1 as components، مش import streamlit as st. يبدو إن جزء من السطر ضاع أو اتبدل أثناء النسخ.

افتح الملف بالقلم، امسح السطر ده بالكامل، واكتب بدالها بالظبط كده: import streamlit.components.v1 as components
[10/9/2026 3:30 PM] Saud 6868: """
Central configuration: symbol lists, timeframe definitions, trade-type
mapping, and asset tab structure for the AI Trading Desk Dashboard.
"""

# ---- Symbol universe, grouped by tab -------------------------------------

FOREX_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "EURJPY"]
METALS_SYMBOLS = ["XAUUSD", "XAGUSD"]
INDEX_SYMBOLS = ["US100", "US500"]  # broker-dependent CFD naming — verify against your MT5 Market Watch
STOCK_SYMBOLS = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]  # placeholder starter list — edit freely

# OKX symbol style: "BASE-QUOTE" (e.g. "BTC-USDT"), different from Binance's "BTCUSDT"
CRYPTO_SYMBOLS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "BNB-USDT"]

MEMECOIN_CHAIN = "solana"  # default chain for DEXScreener trending/whale lookups

ALL_MT5_SYMBOLS = FOREX_SYMBOLS + METALS_SYMBOLS + INDEX_SYMBOLS + STOCK_SYMBOLS

# ---- TradingView widget symbol mapping ------------------------------------
# TradingView uses its own symbol prefixes (exchange:ticker). Edit the right-hand
# side if your broker/exchange naming differs.

TV_SYMBOL_MAP = {
    "EURUSD": "FX:EURUSD", "GBPUSD": "FX:GBPUSD", "USDJPY": "FX:USDJPY",
    "USDCHF": "FX:USDCHF", "AUDUSD": "FX:AUDUSD", "USDCAD": "FX:USDCAD",
    "NZDUSD": "FX:NZDUSD", "EURJPY": "FX:EURJPY",
    "XAUUSD": "OANDA:XAUUSD", "XAGUSD": "OANDA:XAGUSD",
    "US100": "NASDAQ:NDX", "US500": "SP:SPX",
    "AAPL": "NASDAQ:AAPL", "TSLA": "NASDAQ:TSLA", "NVDA": "NASDAQ:NVDA",
    "MSFT": "NASDAQ:MSFT", "AMZN": "NASDAQ:AMZN",
    "BTC-USDT": "BINANCE:BTCUSDT", "ETH-USDT": "BINANCE:ETHUSDT",
    "SOL-USDT": "BINANCE:SOLUSDT", "XRP-USDT": "BINANCE:XRPUSDT",
    "BNB-USDT": "BINANCE:BNBUSDT",
}

# ---- Timeframe -> trade-type classification --------------------------------
# Mirrors the framework doc's top-down multi-timeframe process: a signal
# firing on a higher timeframe is classified as a longer-horizon trade type.

TRADE_TYPE_BY_TIMEFRAME = {
    "M5": "Scalp", "M15": "Scalp",
    "H1": "Day Trade", "H4": "Day Trade",
    "D1": "Swing", "W1": "Position", "MN1": "Position",
}

TRADE_TYPES = ["Scalp", "Day Trade", "Swing", "Position"]

# ---- Risk/target defaults (from the Risk Management section of the doc) ----

DEFAULT_RISK_PERCENT = 0.5    # % of equity per trade, standing default
HARD_RISK_CEILING_PERCENT = 1.0
RR_TARGETS = [1.5, 2.5, 3.5]  # TP1/TP2/TP3 as multiples of risk (partial-profit-then-runner style)

# ---- External free API endpoints -------------------------------------------
# OKX public market-data endpoints - no API key needed, not geo-blocked for
# US-hosted servers (unlike Binance, which returns HTTP 451 from Streamlit
# Community Cloud). OKX uses "BASE-QUOTE" symbol style, e.g. "BTC-USDT".

OKX_TICKER_URL = "https://www.okx.com/api/v5/market/ticker"
OKX_CANDLES_URL = "https://www.okx.com/api/v5/market/candles"
OKX_BOOK_URL = "https://www.okx.com/api/v5/market/books"
OKX_TRADES_URL = "https://www.okx.com/api/v5/market/trades"
DEXSCREENER_TOKEN_URL = "https://api.dexscreener.com/latest/dex/tokens"
DEXSCREENER_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search"

# Finnhub free tier — user must add their own free API key (finnhub.io) for news.
FINNHUB_API_KEY = ""  # <-- paste your free Finnhub API key here
FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/news"

# External quick-link dashboards with no free embeddable API (open in new tab)
EXTERNAL_LINKS = {
    "ForexFactory Calendar": "https://www.forexfactory.com/calendar",
    "Finviz Screener": "https://finviz.com/screener.ashx",
    "TrendVision": "https://trendvision.bot/",
    "CoinGlass Heatmap": "https://www.coinglass.com/pro/i/LiquidationHeatMap",
    "DEXScreener Trending": "https://dexscreener.com/solana",
}
