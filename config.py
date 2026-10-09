"""
Central configuration: symbol lists, timeframe definitions, trade-type
mapping, and asset tab structure for the AI Trading Desk Dashboard.
"""

FOREX_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "EURJPY"]
METALS_SYMBOLS = ["XAUUSD", "XAGUSD"]
INDEX_SYMBOLS = ["US100", "US500"]
STOCK_SYMBOLS = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]

CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]

MEMECOIN_CHAIN = "solana"

ALL_MT5_SYMBOLS = FOREX_SYMBOLS + METALS_SYMBOLS + INDEX_SYMBOLS + STOCK_SYMBOLS

TV_SYMBOL_MAP = {
    "EURUSD": "FX:EURUSD", "GBPUSD": "FX:GBPUSD", "USDJPY": "FX:USDJPY",
    "USDCHF": "FX:USDCHF", "AUDUSD": "FX:AUDUSD", "USDCAD": "FX:USDCAD",
    "NZDUSD": "FX:NZDUSD", "EURJPY": "FX:EURJPY",
    "XAUUSD": "OANDA:XAUUSD", "XAGUSD": "OANDA:XAGUSD",
    "US100": "NASDAQ:NDX", "US500": "SP:SPX",
    "AAPL": "NASDAQ:AAPL", "TSLA": "NASDAQ:TSLA", "NVDA": "NASDAQ:NVDA",
    "MSFT": "NASDAQ:MSFT", "AMZN": "NASDAQ:AMZN",
    "BTCUSDT": "BINANCE:BTCUSDT", "ETHUSDT": "BINANCE:ETHUSDT",
    "SOLUSDT": "BINANCE:SOLUSDT", "XRPUSDT": "BINANCE:XRPUSDT",
    "BNBUSDT": "BINANCE:BNBUSDT",
}

TRADE_TYPE_BY_TIMEFRAME = {
    "M5": "Scalp", "M15": "Scalp",
    "H1": "Day Trade", "H4": "Day Trade",
    "D1": "Swing", "W1": "Position", "MN1": "Position",
}

TRADE_TYPES = ["Scalp", "Day Trade", "Swing", "Position"]

DEFAULT_RISK_PERCENT = 0.5
HARD_RISK_CEILING_PERCENT = 1.0
RR_TARGETS = [1.5, 2.5, 3.5]

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
BINANCE_DEPTH_URL = "https://api.binance.com/api/v3/depth"
BINANCE_TRADES_URL = "https://api.binance.com/api/v3/trades"
DEXSCREENER_TOKEN_URL = "https://api.dexscreener.com/latest/dex/tokens"
DEXSCREENER_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search"

FINNHUB_API_KEY = ""
FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/news"

EXTERNAL_LINKS = {
    "ForexFactory Calendar": "https://www.forexfactory.com/calendar",
    "Finviz Screener": "https://finviz.com/screener.ashx",
    "TrendVision": "https://trendvision.bot/",
    "CoinGlass Heatmap": "https://www.coinglass.com/pro/i/LiquidationHeatMap",
    "DEXScreener Trending": "https://dexscreener.com/solana",
}
