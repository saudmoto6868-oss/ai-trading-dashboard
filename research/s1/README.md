# S1 scalp scanner (experimental)

Live scan of GOLD, SILVER, NDX, SPX, EURUSD, BTC, ETH on dashboard data only
(`modules.market_cache`: Hyperliquid TradFi, OKX crypto). No yfinance. No broker orders.

```
python3 research/s1/scalp_now.py all --send
```

- `--send` : one Telegram media group (caption only) to the owner. State is recorded only after HTTP 200.
- `--force` : also package the best non-qualified candidate (watch only).
- `--ignore-state` : skip 90-minute cooldown / session cap / same-zone (debug/replay only).

Core triggers that may send: `sweep_rej`, `kzs`.
Confluence tags (never sent alone): `psar_trend`, `lvl_sweep`, `zn`, `vwap2`.
Dashboard tools wired as scored agree/against/veto: Harmonic PRZ, X77, 15m OB+FVG, MSB/BOS, Elliott, Gann, EMA 9/21, kill zones, volume/displacement proxy.

Runtime state: `research/s1/state/sent.json` (gitignored).
Set `XPIX_REPO` to the dashboard repo root so `modules.harmonic` and friends import.
