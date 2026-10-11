# 6868 X - خريطة الاستراتيجيات والمفاهيم (Strategy map)

Single source of truth for *what concept lives where*. Layers, from "where/when" down to "how I enter":

| Layer | Question | Counts in stars? |
|---|---|---|
| **A. Context** | Which side is favoured, where in the range, what time? | No - shown with a tick / cross |
| **B. Liquidity** | What was taken / what is the target? | Yes (family *Liquidity*) |
| **C. Structure** | Did the structure shift? | Yes (MSB-OB, TL) / scanner-only (MSS) |
| **D. Zones (PD arrays)** | Where do I enter? | Yes (OB, FVG, Breaker, Unicorn, Fib) |
| **E. Entry models** | Complete step-by-step setups | Yes (CISD, Model 2022 under *Liquidity*) |
| **F. Confirmations** | Does anything else agree? | Yes (MA, VWAP, TL) |
| **G. Order flow** | Is the book / tape agreeing right now? | No - chart column |

Stars = number of distinct *families* aligned (max 8: Elliott, Unicorn, MSB-OB, Fib, Liquidity | MA, VWAP, TL); a confirmation alone is 1 star.
Context is deliberately **not** a star: it is evidence about the setting, not a second signal.

## A. Context  (`modules/context.py`, shown in the alert popup "السياق")
- **Daily bias** - previous completed NY day closed above the day-before's high -> longs only; below its low -> shorts only; back inside -> none. *(ICT course; unverified edge)*
- **Accumulation / stand aside** - two inside days in a row.
- **Premium / Discount** - position in the dealing range (latest major swing low->high, extended by any new extreme). Longs in discount, shorts in premium. A filter, not a signal.
- **Time window** - NY killzones (London 02-05, NY AM 07-10) and Silver Bullet hours (03-04, 10-11, 14-15), DST-correct.
- Also on the chart: KZ boxes, open levels (4H/D/W/M), SMT, session AMD.

## B/C/D/E. Signals (`modules/signals.py`)
| Concept | Detector | Layer | Status |
|---|---|---|---|
| Sell/buy-side sweep | `sweep_signal_bull`, `zombie_bull`, `liq_break_bull`, `crt_bull` | B | in stars |
| Structure break + order block | `msb_ob_bull`, `order_block_bull` | C/D | in stars |
| FVG, Breaker, Unicorn, OTE/Fib | `fvg_bull`, `breaker_bull`, `unicorn_bull`, `ote_bull`, `fib_bull` | D | in stars |
| **Sweep + CISD** (enter *before* the structure break) | `cisd_bull` | E | **new**, in stars (Liquidity) |
| **Model 2022** (raid -> MSS+displacement -> FVG, killzone only) | `model2022_bull` | E | **new**, in stars (Liquidity) |
| **Trendline break** (close through a swing line, volume/strong close/retest) | `trendbreak_bull` | C/F | **new**, family TL |
| Judas, Session AMD, ORB | `judas_bull`, `session_amd_bull`, `session_orb_bull` | E | in stars |
| RSI / MACD divergence, Donchian | `rsi_div_bull`, `macd_div_bull`, `donchian_bull` | F | in stars |
| Elliott 3/5 | `elliott_bull` | - | in stars |

CISD vs Model 2022: CISD fires first (body close through the open of the last down-candle run, structure not yet broken); Model 2022 is the confirmed version (structure broke with displacement, entry in the gap).

## Scanner-only flags (`modules/chart_scan.py`) - NOT in stars / alerts yet
IFVG, Mitigation block, MSS/CHoCH, Premium-Discount (outer 30%), Silver Bullet (FVG in a window), Breakout+volume-delta, Harmonics, channel breaks, double top/bottom.
These are candidates for promotion once a walk-forward test on real candles shows they beat the baseline.

## Not built yet
- 5 daily candle types (up / up-reversal / down / down-reversal / accumulation around the 00:00 NY open).
- Order-block respect rate (how often each OB held) - needs real history.
- Options flow (Unusual Whales: ask-side, volume > OI, OTM, single leg, premium) - needs a paid API key.

## Evidence (nothing here is proven until it has been run on real candles)
- `python -m modules.backtest_osma` - RSI(2)+OsMA bar rule vs inverse vs trend-filtered.
- `python -m modules.backtest_signals` - trendline break, CISD, Model 2022 vs a random baseline, plus **context_filters**: does killzone / premium-discount / daily bias raise the hit rate?
- Random-walk checks: all tests report ~50% and no false "edge" flags. Published win-rate claims for SMC/ICT (e.g. 58% filtered) come from unaudited sources - treat as hypotheses.
