"""
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
    "CoinGlass Heatmap": "https://www.coinglass.com/pro/futures/LiquidationHeatMap",
    "DEXScreener Trending": "https://dexscreener.com/solana",
}
