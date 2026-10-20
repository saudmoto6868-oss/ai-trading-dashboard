"""
AI Trading Desk Dashboard - Architecture Overview
===================================================

Built as a "virtual desk of employees" from day one, even though v1 runs as
a single Streamlit script. Each employee is its own module with ONE job and
a clean input/output, so later this can be split into real independent
agents/processes without rewriting logic - only the orchestration layer
(main.py) would change.

THE EMPLOYEES (modules/):

  data_fetcher.py     - "The Data Clerk"
                         Pulls raw price candles from MT5 (forex/metals/
                         indices/stocks) and Binance (crypto). Only job:
                         return clean OHLCV dataframes. Knows nothing about
                         analysis.

  price_action.py      - "The Chart Analyst"
                         Department 1 signals: support/resistance, VWAP,
                         EMA trend bias, breakout detection.

  liquidity_ohl.py      - "The Liquidity Reader"
                         Department 2 signals: own liquidity-line
                         approximation plus OHL bias (independent logic,
                         not copying any paid indicator).

  scorer.py             - "The Head Analyst"
                         Combines every department's signals into one
                         strength score, reasons list, and trade-type
                         classification (scalp/day/swing/position) based on
                         which timeframe fired.

  risk_engine.py         - "The Risk Manager"
                         Turns a scored signal into a full trade plan:
                         entry, stop loss, and 3 staged take-profits, using
                         the Fibonacci/liquidity levels and RR rules from
                         the framework doc.

  news_feed.py           - "The News Desk"
                         Pulls headlines from Finnhub (free tier), tags each
                         with the relevant asset icon.

  crypto_extras.py       - "The Crypto Desk"
                         Binance order book and time and sales, CoinGlass
                         heatmap links, DEXScreener whale/meme-coin tracking.

  alerts.py               - "The Alert Officer"
                         Watches scored signals; when one crosses the alert
                         threshold, fires a sound plus colored banner plus
                         full trade plan. Also the hook point for the future
                         Telegram bot.

  tv_widget.py             - "The Chart Vendor"
                         Builds the embedded TradingView widget HTML per
                         symbol/tab.

  main.py                  - "The Floor Manager"
                         Orchestrates all employees above, lays out the
                         tabs, and renders the final dashboard. Contains NO
                         analysis logic of its own.

FUTURE UPGRADE PATH: each module above can later run as its own scheduled
job/process writing to a shared store (file or small database), with
main.py (or a future Telegram bot) just reading the latest results instead
of calling functions directly. The module boundaries were chosen so that
split is a refactor, not a rewrite.
"""
