# Stocks and Options listing (team item 4, 2026-10-26)

Report only; no code changed. Names and sectors below are general public facts. Rows marked **CONFIRM** are tickers whose company I am not sure of (many are Hyperliquid xyz names for non-US or pre-IPO companies): the owner should confirm before the app shows them.

## Where stocks come from
- Hyperliquid xyz dex (~100 US / Asian stock perps, 24/7 oracle prices; browser `hlOkx`, server `hl_feed.py`, class "Stocks" = any xyz name not in the metals / oil / index / FX / bond lists).
- OKX stock-token swaps (instCategory 3).
- Yahoo (`Y:` symbols) only for forex / indices / EGX / Tadawul, not US stocks.
- Logos today: `symIcon()` in `modules/workspace_app.html` (~1207) uses Google's favicon service for the company domain (map `SI_STOCK`, 48 tickers) and falls back to a coloured letter. **That is a third-party service, not a licensed or owner-supplied file.** To follow the rule "logos only from licensed or owner files": the owner supplies the files (SVG / PNG) in a folder such as `modules/logos/` with a small manifest, and `symIcon()` reads that first; until then the letter badge is shown, not a guessed logo.

## The 48 tickers the app knows (SI_STOCK)
| Ticker | Name | Sector (broad) | Note |
|---|---|---|---|
| AAPL | Apple | Technology | |
| MSFT | Microsoft | Technology | |
| NVDA | NVIDIA | Technology (semiconductors) | |
| TSLA | Tesla | Consumer discretionary (autos) | |
| AMZN | Amazon | Consumer discretionary | |
| GOOGL / GOOG | Alphabet | Communication services | two share classes |
| META | Meta Platforms | Communication services | |
| AMD | Advanced Micro Devices | Technology (semiconductors) | |
| INTC | Intel | Technology (semiconductors) | |
| MU | Micron | Technology (memory) | |
| MRVL | Marvell | Technology (semiconductors) | |
| NET | Cloudflare | Technology (software) | |
| CRWD | CrowdStrike | Technology (software) | |
| MSTR | Strategy (formerly MicroStrategy) | Technology (software, bitcoin treasury) | |
| COIN | Coinbase | Financials | |
| MRNA | Moderna | Health care | |
| CRCL | Circle Internet Group | Financials | |
| NBIS | Nebius Group | Technology (AI cloud) | |
| CRWV | CoreWeave | Technology (AI cloud) | |
| BE | Bloom Energy | Industrials (energy equipment) | |
| SNDK | Sandisk | Technology (storage) | |
| WDC | Western Digital | Technology (storage) | |
| AAOI | Applied Optoelectronics | Technology (optical) | |
| LITE | Lumentum | Technology (optical) | |
| NFLX | Netflix | Communication services | |
| PLTR | Palantir | Technology (software) | |
| HOOD | Robinhood | Financials | |
| ORCL | Oracle | Technology (software) | |
| AVGO | Broadcom | Technology (semiconductors) | |
| TSM | TSMC (ADR) | Technology (semiconductors) | |
| BABA | Alibaba (ADR) | Consumer discretionary | |
| UBER | Uber | Industrials | |
| SOXL / SOXS | Direxion semiconductor 3x bull / bear ETFs | ETF | leveraged |
| TLT | iShares 20+ Year Treasury Bond ETF | ETF (bonds) | class "Bonds" in the app |
| EWY | iShares MSCI South Korea ETF | ETF | |
| KORU | Direxion South Korea 3x bull ETF | ETF | leveraged |
| SMSN / SAMSUNG | Samsung Electronics? | Technology | **CONFIRM** (two names for one company?) |
| SKHX / SKHY / SKHYNIX | SK hynix? | Technology (memory) | **CONFIRM** (three spellings) |
| UNITREE | Unitree Robotics? | Technology (robotics) | **CONFIRM** (private / pre-IPO) |
| CXMT | ChangXin Memory? | Technology (memory) | **CONFIRM** (private / pre-IPO) |
| ZHIPU | Zhipu AI? | Technology (AI) | **CONFIRM** (private / pre-IPO) |
| DRAM | a memory-related fund? | ? | **CONFIRM** |
| SPCX | ? | ? | **CONFIRM** |

Not listed here: the other ~50 Hyperliquid xyz stock names. The live list needs the browser or the Hyperliquid `metaAndAssetCtxs` call, which the sandbox cannot reach; the Coinversa connector was not used (owner approval pending). Those symbols show a coloured-letter badge now.

## Stocks: what works (mock level)
Price (HL.q from `metaAndAssetCtxs`), chart (`candleSnapshot`, every timeframe, 6H fixed in #127) and the server scan use the same path as gold (see PR #127 and #131): any xyz stock behaves like gold. Per-symbol live status for each stock is NOT tested.

## Options today
| What | Data path | Charts | Status |
|---|---|---|---|
| Watchlist class "Options" | OKX `/market/tickers?instType=OPTION&uly=BTC-USD / ETH-USD` (asset_classes.py `OPTION_ULYS`, browser + server), busiest first | OKX candles for an option contract (sparse, illiquid contracts) | owner decision 2026-10-22: options need no charts; candle source decision deferred until a live probe from his browser |
| Options desk (BTC / ETH) | Deribit public `get_book_summary_by_currency` + DVOL (`modules/options_desk.py`), free, no key | none (tables: put/call, max pain, ATM IV, skew, OI walls, IV rank) | working in mocks; context, not a signal |
| US equity / index chains | Cboe delayed JSON (`modules/cboe_options.py`), free, keyless, ~15 min delayed, unofficial | none | code exists, tested with a mock payload only, not wired into the UI (flow_manual.py says so) |
| Options flow alerts | Unusual Whales API (`modules/options_flow.py`), needs `UNUSUALWHALES_API_KEY` (paid) | none | unverified against the live API; off without a key |
| Scanner / Radar | Options are NOT scanned (asset_classes.py: no candle feed) | none | by design |

**The one fix that makes Options show a chart:** none is needed by the owner's decision; if a chart is wanted, plot the OKX option contract's mark / last price line from `/market/candles` when it exists and say "illiquid: sparse" otherwise. It needs a live probe from the owner's browser first (which contracts return candles), so it is NOT built.
**The one fix that makes every class show a chart:** the class list is covered by hlOkx (metals, oil, indices, forex, stocks, bonds), OKX (crypto) and the Yahoo embed (forex, indices, EGX, Tadawul; 15m / 1H / 4H / 1D only). Remaining gaps: Yahoo classes need 2H / 6H / 1W built from 1H / 1D (#132), and options as above.
