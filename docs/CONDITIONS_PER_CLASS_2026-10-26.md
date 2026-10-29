# Radar / scanner conditions per asset class (team item 5, 2026-10-26)

Method (honest limits): synthetic OHLC series shaped like each class (price level, daily volatility, whether the feed has volume), 40 series per class (random walks + last-bar shocks + gaps), run through every Radar list option (`fv_screen.FILTERS`, 410) and every scanner condition (`chart_scan.ALL_FILTERS`, 96). Not real market data (the sandbox reaches no price site). A condition that never fires on random series is NOT automatically a bug: many are thresholds (perf +50 %, ATR > 10 %) or shapes (channel, wedge). So conditions that fired nowhere were run again on a hand-built stress suite (parabolic move, crash, V and inverted V, +-60 % bar, gaps, volume spikes, candle fixtures). Script: `tests/report_conditions_per_class.py`.

## Result per class (0 crashes anywhere)
| Class (data source) | Radar options that never fired (of 410) | Scanner conditions that never fired (of 96) | Zero ONLY because the feed has no volume |
|---|---|---|---|
| Crypto (OKX) | 72 | 20 | 0 |
| Metals (HL gold) | 148 | 22 | 0 |
| Oil (HL CL) | 97 | 20 | 0 |
| Indices (HL SP500) | 150 | 22 | 0 |
| Forex (HL EUR) | 201 | 21 | 0 |
| Forex (Yahoo EURUSD=X) | 208 | 24 | **10** |
| Stocks (HL) | 105 | 20 | 0 |
| Bonds (HL TLT) | 186 | 23 | 0 |
| EGX / Tadawul (Yahoo) | 147 | 23 | **12** |

The large per-class differences are volatility: a 0.4 % / day forex pair rarely moves +20 % in a month, while crypto does. That is correct behaviour, not a bug.

## Real finding: volume-less feeds
Yahoo forex / indices / EGX / Tadawul candles have volume 0, so these can never fire there (they fire with volume present):
- Forex (Yahoo): relvol (over 1, 1.5, 2, 3; under 1, 2), obv up, vol_2x, vol_3x, st_vwap (10).
- EGX / Tadawul (Yahoo): the same plus turnover over 100K / 1M (12).
**Marked as a bug:** the UI offers these conditions on classes whose feed has no volume and they silently return nothing. Fix (not done): hide or grey them for those classes, with a note "no volume on this feed".

## Fired nowhere, even on the stress suite (unproven, NOT proven failing)
- Radar (11): beta over 1 / over 2, correlation over 0.5 / over 0.8 / under -0.5 (needs a correlated reference series; the fixture reference was random), dark cloud and evening star candles (my fixtures may be imperfect), 20-day low "100 % above" (needs a doubling in 20 days), SMA20 above SMA200 cross / SMA20 above SMA50 cross / SMA50 cross down (needs exact crossing fixtures).
- Scanner (14): channel up, channel horizontal, ascending / descending triangle, rising wedge, MA cross down 20/50, MA cross up 50/200 (shape and exact-cross fixtures not built), and the session strategies st_judas, st_kzs, st_orb, st_po3, st_sessamd, st_silver, st_smt (need intraday time-of-day data and, for SMT, a peer symbol; st_judas does fire on 1h / 15m series).
These need purpose-built fixtures to settle; until then they are "not shown to work", not "bugs".

## Not covered
Real data, live feeds, the Asset class filter counts, presets with real symbols, and per-timeframe differences (all series are daily, except the intraday check on the session strategies).
