# Session 2026-11-06 - Spot desk (item 28, phase 1)

**Owner order:** a separate Spot page next to the Radar. Crypto (OKX list 50 / 100 / all like the watchlist, plan from our schools
on monthly / weekly / yearly, staged buys), metals (gold, silver, copper, platinum, palladium in USD + EGP, karats 24 / 21 / 18,
rate at its time), ledger of real spot trades in ounces with invoices, PDF upload, print, Excel, alerts (buy / sell time) to
Telegram later, news + following Instagram / TikTok accounts. Crypto in USD; EGP button only for B2B.

**Done (branch `claude/multi-asset-bot-plan-q8fhg8`):**
- `modules/spot_core.py` units / karats / EGP, average-cost ledger with EGP P&L split (metal move + dollar move), ladder, alerts, Excel, invoice HTML.
- `modules/spot_data.py` OKX spot tickers, metals live from Hyperliquid (copper per lb, checked: 6.23), Yahoo futures for history, USD/EGP (Yahoo) + manual rate.
- `modules/spot_plan.py` long-only votes: trend (mtf), Elliott (elliott_lab + Elliott/Fib families), SMC/ICT (MSB-OB / Unicorn / Liquidity), Gann levels + time cycle, regime; 1M x3 / 1W x2 / 1D x1.
- `modules/spot_page.py` page 11 (5 tabs), `main.py` page bar (after Radar), Yahoo `1mo`, `openpyxl` in requirements, `data/spot/` git-ignored.
- `tests/test_spot.py`: math + plan on synthetic candles + AppTest (network blocked, then mocked data, en + ar). Screenshots checked with mocked data.

**Not done / open:**
- The plan combination is NOT backtested -> not evidence (next: lab run of the spot score on 1W / 1M across many coins + gold).
- Alerts are checked only while the page is open; server-side check in `tg_cron` is next.
- Instagram / TikTok reading: needs a scraping service key + owner decision (their terms block bots). The page stores the account list only.
- Real prices not checked from the sandbox (no access to OKX / Yahoo / Hyperliquid here).
- Records live on the server disk; Streamlit Cloud can wipe it -> backup ZIP button. A durable store (e.g. a private DB) is an owner decision.
