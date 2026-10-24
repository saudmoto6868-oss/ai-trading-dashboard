# Radar item C: Finviz-style filters, what we can support with the data we already have (2026-10-24)

Rule: a filter is only listed as supported if it can be computed from data the app ALREADY loads (OHLCV candles from OKX / Hyperliquid / Yahoo) with no new key and no new request. Filters describe candles; a match is not a signal (the lab evidence gate still applies).

## 1. Already in the Radar (modules/fv_screen.py, 18 lists + chart patterns + strategies)
Performance (2 lists), Volatility, RSI(14), Gap, SMA 20 / 50 / 200 position, Change, Change from open, 20d / 50d / 52w / all-time high-low, Pattern (14 chart patterns), Candlestick (14), ATR % of price, Relative volume; plus EMA stack / cross filters, RSI buckets, price move and volume spikes, the strategy flags (Elliott, SMC, ICT, Harmonic, VWAP ...). Since #109 they sit in the grouped dropdowns Trend / Momentum / Volume / Pattern / Market / Symbol.

## 2. Can be added now from candles only (no new data) - proposed order
| Filter (Finviz name) | Computed from | Group | Effort |
|---|---|---|---|
| MACD: cross up / down, above / below zero | close | Momentum | small |
| Bollinger Bands: above upper / below lower / squeeze (width percentile) | close | Volatility -> Market | small |
| Stochastic (14,3): overbought / oversold / cross | HLC | Momentum | small |
| ADX (14): trend strength >20 / >25 / >40, +DI vs -DI | HLC | Trend | small (ADX exists in the chart) |
| CCI, Williams %R, Parabolic SAR flip | HLC | Momentum | small (CCI / SAR exist in the chart) |
| Ichimoku: price vs cloud, TK cross | HLC | Trend | medium |
| Beta vs a reference (BTC for crypto, S&P 500 for TradFi) and correlation | close of 2 symbols already loaded | Market | medium |
| Average volume / turnover (liquidity ranks: top-N by volume) | volume | Volume | small |
| Price (above / below X, within range) and distance to EMA in % | close | Market | small |
| Volume trend (OBV rising / falling, up-volume vs down-volume) | close, volume | Volume | small |
| NR7 / inside bar / N up-down candles in a row | OHLC | Pattern | small |
| Multi-timeframe agreement (daily + weekly + the chosen TF same direction) | modules/mtf.py | Trend | medium (extra TF candles are cached) |
| Exchange / source (OKX, Hyperliquid, Yahoo) and asset class | symbol prefix | Symbol | trivial |

## 3. Possible only with a data source the owner must decide (not "free and already loaded")
| Finviz filter | What it needs | Notes |
|---|---|---|
| Sector / Industry / Country | a static symbol map (stocks, EGX, Tadawul) | item F; crypto sectors need a CoinMarketCap category list (key) |
| Index membership (S&P 500, Nasdaq-100, DJIA) | a membership list | static list per index, refreshed by hand |
| Market cap, Float, Shares | Yahoo quote (unofficial) or CoinMarketCap / Finnhub (key) | crypto: CMC key; stocks: Finnhub free tier |
| Earnings date / Analyst recommendation / Target price | Finnhub (key, free tier rate limits) | stocks only |
| P/E, EPS growth, Sales growth, Margins, ROE, Debt ... (all Fundamental) | Finnhub basic financials (key) | stocks only; 60 calls / min free tier |
| Dividend yield | Finnhub / Yahoo | stocks only |
| Options-based (put/call, IV rank) | OKX options feed has no candles here; Cboe delayed JSON for US options | deferred decision by the owner |

## 4. Impossible for this app, and why
- **Fundamentals, earnings, analyst, dividends for crypto, FX, metals, oil, indices, bonds:** these concepts do not exist for those markets.
- **Insider trading, institutional ownership (13F), short float / short interest, ETF holdings:** only through the Equibles MCP, which works in Claude sessions but NOT in the deployed app ("the deployed app cannot use MCP tools"); no free public API with usable limits (Alpha Vantage free = 25 requests / day, rejected earlier).
- **News sentiment, theme tags, unusual options flow:** need a paid or keyed feed (Unusual Whales key still waiting on the owner).
- **EGX / Tadawul fundamentals and live prices:** no verified free live feed; only Yahoo, delayed and unofficial (item F shows the delay label).
- **True 52-week / all-time high-low on lower timeframes:** limited by the candles loaded (the label already says "all loaded history"); on 1D charts it is exact only for symbols with a year of history.

## 5. Proposal
1. Section 2 first six rows as one PR (MACD, Bollinger, Stochastic, ADX, CCI/Williams/SAR, liquidity + price + distance): small, candle-only, no new fetch.
2. Then beta/correlation and multi-timeframe agreement.
3. Section 3 only after the owner picks the sources (Finnhub key is the first one he already has on his list).
