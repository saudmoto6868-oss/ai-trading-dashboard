# 6868 X

## What this is
A Streamlit dashboard with 5 tabs (Crypto, Forex, Metals, Stocks, Meme Coins).
Each tab has a live TradingView chart plus a scored watchlist built from the
Price Action and Liquidity/OHL departments, plus breakout detection.
Crypto tab adds a Depth-of-Market ladder (bids and asks in one view), a time and
sales feed that flags Smart/Whale prints, and Limit Tracking of big resting orders
(data from OKX public API, no key needed). The page auto-refreshes every ~20s. Alerts fire
with sound plus a full trade plan (entry, stop loss, 3 staged take profits)
when a signal is strong.

## Folder structure
main.py runs the app. config.py holds symbol lists, API keys, risk settings.
requirements.txt lists the Python packages needed.
ARCHITECTURE.py explains the "virtual employees" module design.
The modules folder contains: signals.py (scanner detectors), market_cache.py (parallel cached candles), data_fetcher.py, price_action.py,
liquidity_ohl.py, scorer.py, risk_engine.py, news_feed.py,
crypto_extras.py, dom_panel.py, alerts.py, tv_widget.py.

## Setup (local test first)
1. Make sure MetaTrader 5 is open and logged into your account.
2. Open Command Prompt in this folder and run: pip install -r requirements.txt
3. Get a free Finnhub API key at finnhub.io and paste it into config.py.
4. Run the dashboard with: streamlit run main.py

## Known things to check
INDEX_SYMBOLS in config.py are placeholders, check your broker's MT5
symbol names for Nasdaq and S&P 500 CFDs. STOCK_SYMBOLS is a short
starter list, edit freely. TV_SYMBOL_MAP controls TradingView chart
symbols. CoinGlass heatmap is a quick link only, no free embed available.

## Next steps
Deploy on Streamlit Community Cloud for a permanent online link. Add a
Telegram bot hook in modules/alerts.py. Split modules into independent
scheduled jobs once the single script version is proven stable.

## Scanner (Crypto tab watchlist)
Pick a scan timeframe (1 min / 1 hour / 1 day / 1 week). Each coin is scored 0-7
stars = how many signal families agree: Elliott, Unicorn, MSB-OB, Fib, Liquidity
(primary) and MA, VWAP (confirmation only - worth at most 1 star alone).
Click a coin to see exactly which signals fired, the higher-timeframe
confirmation, a trade plan and three scenarios. Trade type (Scalp / Day / Swing /
Position) comes from which higher timeframe confirms the trigger, not from the
tab. All detectors are own-built from the framework doc; Elliott counting is a
rule-based heuristic, not a guarantee.
