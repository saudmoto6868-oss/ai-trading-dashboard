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
CRYPTO_SYMBOLS = [
    "BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "BNB-USDT", "DOGE-USDT", "ADA-USDT", "AVAX-USDT",
    "LINK-USDT", "DOT-USDT", "TRX-USDT", "LTC-USDT", "TON-USDT", "SUI-USDT", "NEAR-USDT", "APT-USDT",
]  # add more here (OKX "BASE-USDT" names); the Workspace watchlist also has an "add symbol" box

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

# Auto-refresh: how often (seconds) the whole dashboard re-pulls prices,
# watchlist, order book and time & sales. Adjustable from the sidebar.
AUTO_REFRESH_SECONDS = 20

# External quick-link dashboards with no free embeddable API (open in new tab).
# Shown as icon buttons near the top of the page (see QUICK_LINK_ICONS).
EXTERNAL_LINKS = {
    "ForexFactory Calendar": "https://www.forexfactory.com/calendar",
    "Finviz Patterns": "https://finviz.com/screener.ashx?v=211",  # charts view; per-pattern links below
    "TrendVision": "https://trendvision.bot/",
    "CoinGlass Heatmap": "https://www.coinglass.com/pro/futures/LiquidationHeatMap",
    "DEXScreener Trending": "https://dexscreener.com/solana",
}

QUICK_LINK_ICONS = {
    "ForexFactory Calendar": "\U0001F4C5",
    "Finviz Patterns": "\U0001F50E",
    "TrendVision": "\U0001F4C8",
    "CoinGlass Heatmap": "\U0001F525",
    "DEXScreener Trending": "\U0001F9ED",
}

# Finviz chart-pattern screener: v=211 is the "Charts" view, s=ta_p_<pattern>
# is its Chart Pattern signal filter. Edit/extend freely.
FINVIZ_PATTERNS = {
    "Channel Up": "ta_p_channelup",
    "Channel Down": "ta_p_channeldown",
    "Wedge Up": "ta_p_wedgeup",
    "Wedge Down": "ta_p_wedgedown",
    "Triangle Ascending": "ta_p_triangleascending",
    "Triangle Descending": "ta_p_triangledescending",
    "Double Top": "ta_p_doubletop",
    "Double Bottom": "ta_p_doublebottom",
    "Head & Shoulders": "ta_p_headandshoulders",
    "Inverse Head & Shoulders": "ta_p_headandshouldersinv",
    "Support (trendline)": "ta_p_tlsupport",
    "Resistance (trendline)": "ta_p_tlresistance",
}
FINVIZ_PATTERN_URL = "https://finviz.com/screener.ashx?v=211&s={signal}"
