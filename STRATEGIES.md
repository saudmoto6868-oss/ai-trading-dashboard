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

## Group A - quality filters on existing detectors (`modules/sig_filters.py`)
They only REMOVE signals that fail an extra test (never add any). Switch each off with an env var, tune with `SIGF_*` (see the module header).
| Filter | Applies to | Test | Needs |
|---|---|---|---|
| Strict SMC (`SIGF_STRICT_SMC`) | order block, breaker, unicorn | a real structure break exists: close beyond the swing high by >= 0.1 ATR, break/leg body >= 1 ATR, first break of that swing | - |
| OB volume (`SIGF_OB_VOL`) | order block | volume of the OB candle + 2 next >= 1.0x the typical 3-bar volume | real volume |
| Breakout volume delta (`SIGF_BO_VOL`) | breakout, liquidity-line break, OHL break, ORB | best of last 3 bars >= 1.2x 20-bar avg volume AND estimated net buying >= 10% (delta = volume x close-location, a candle ESTIMATE, not tick data) | real volume |
Volume filters switch themselves off for markets whose candles carry no volume (Yahoo forex / indices). Not backtested yet: run `python -m modules.backtest_signals` with the switches on and off on real OKX data before trusting them.

## Group B - new signals (`modules/signals.py`)
| Signal | Detector | Rules |
|---|---|---|
| Kill Zone Sniper | `killzone_sniper_bull` | inside London / NY-AM kill zone (New York time): sweep of the 20-bar low + close back above + bullish displacement body >= 0.9 ATR; with real volume >= 1.5x average; >= 1.5R to the 30-bar swing high |
| Power of Three (restricted) | `power_of_three_bull` | daily open (00:00 NY); price >= 0.5 ATR below it with that low printed INSIDE a kill zone; entry only after a displacement candle closes back above the open (rebound confirmed); target = max(open + 2x depth, yesterday's high); >= 1.5R |
SMT (BTC/ETH/SOL pairs, `modules/smt.py`) and CRT (`crt_bull`) already existed and are unchanged.

## Item 15 - hedge-fund / CTA trend rules (`modules/signals.py`, `modules/momentum.py`)
Daily or weekly bars only (they return nothing on intraday frames). Family MA, so they can confirm but never add a separate family star.
| Signal | Detector / module | Rules |
|---|---|---|
| SMA 10/40 cross | `sma1040_bull` (key `sma1040`) | SMA 10 crossed SMA 40 within the last 3 bars, still on that side, close beyond SMA 40; invalidation = entry -/+ 2N (N = 20-bar ATR) |
| Donchian 55 (Turtle System 2) | `turtle55_bull` (key `turtle55`) | first CLOSE beyond the previous 55-bar high/low within the last 3 bars (the original used an intraday touch; a close avoids repainting); stop 2N; trailing exit = close beyond the 20-bar opposite extreme |
| Cross-sector momentum | `momentum.rank` (Stocks tab expander) | 12-1 month return / 63-day volatility, ranked; LONG candidate = top third + positive 12-1 + above SMA 200; AVOID = bottom third + negative + below SMA 200. Universes: 11 US sector SPDR ETFs (Yahoo), 10 crypto majors (OKX; 252 bars = ~8 calendar months there) |
Evidence: none yet in this project - tested on hand-made candles only (`tests/test_hedge.py`). Both detectors were added to `backtest_filters.KEYS`, so the pending real-data run (item 1) will measure them.

## Operating model (2026-10-17) - how trade quality is raised and kept honest
Evidence ranking used for decisions (strongest first):
1. **Own real results** - journal / signal log (owner, Oct 2026: 1110 trades; 1m = -147R of -150R -> 1m alerts off) and the weekly
   strategy lab (`STRATEGY_LAB.md`, every detector vs a random baseline on real candles).
2. **Peer-reviewed research** - time-series momentum / trend-following works across asset classes (Moskowitz, Ooi, Pedersen 2012;
   in crypto TSMOM strong, cross-sectional weak - Han, Kang, Ryu); volatility-scaled position size is a main source of better
   risk-adjusted returns (Kim, Tse, Wald 2016). -> trade WITH the higher-timeframe trend; size by volatility (already in the plan).
3. **Practitioner / YouTube claims** (SMC / ICT win rates 60-80 %) - no independent, out-of-sample, cost-aware test found; a
   1000-trade mechanical test reported 38-48 %; order blocks only helped with a displacement leg + FVG. -> SMC detectors stay,
   but only enter as "primary" when the lab shows an edge; strict-structure / displacement filters stay on.
Rules for every change: walk-forward only (no look-ahead), random baseline, n >= 50 before ranking, costs make it worse,
win rate is NOT the goal - expectancy (avg R) is; a higher win rate from a smaller target is not an improvement by itself.
Sustainable loop: weekly lab -> tiers (primary / confirmation / off) -> journal + signal log on live trades -> monthly review of the
tiers; a detector moves up only on lab + live evidence, down when its live avg R stays below 0 for 50+ trades.

## Schools ranked (2026-10-17): outside evidence x our lab -> the playbook
| rank | school | outside evidence | our lab (avg R, real candles) | role in the system |
|---|---|---|---|---|
| 1 | Trend-following / time-series momentum (daily+) | strong, peer-reviewed (MOP 2012; crypto TSMOM) | daily detectors positive (sma1040 1d +0.43R) | FRAME: trade on the daily-trend side; size by volatility |
| 2 | Price action - daily levels / breakouts | mixed (Bulkowski: patterns fail 2-4x more than in the 1990s) | ohl_break 1d +0.50R, breakout 1d +0.41R | primary setups, daily |
| 3 | Momentum / divergence (RSI, MACD) | weak-moderate | best school pooled +0.063R; macd_div 1d +0.31R | timing / confirmation |
| 4 | Time & liquidity (sessions, kill zones, sweeps) - the useful part of ICT | no independent study | +0.043 / +0.034R | intraday timing only, with the daily frame |
| 5 | Fibonacci / OTE | Fib ratios ~random (Batchelor & Ramyar 2005, second-hand) | ~0 | levels for targets, not a reason to trade |
| 6 | SMC / ICT zones (OB, breaker, unicorn, FVG) | none independent; mechanical tests 38-48 % win | -0.034R pooled; OB, unicorn, msb_ob OFF; FVG only 1d +0.19R | confirmation at most |
| 7 | Elliott wave | no predictive power found (forex thesis), subjective | worst school -0.079R; ew3 OFF | visual only |
| live | Order book + time & sales (order flow) | no free history -> cannot be backtested here | forward-tested: every journal trade stores the book imbalance (+-0.5 %) and 2-min aggressor delta verdict | execution check in the Setup Card; journal table 'Order flow at entry' measures it |
| context | Fundamental (high-impact news, funding crowding, macro) | news-driven volatility is well documented; funding extremes = crowded side | journal tables 'High-impact news'; lab cannot test (no history) | checklist warning; no entry +-1h around high-impact news for that currency |
| timing | Time analysis (sessions, kill zones, weekday) | intraday seasonality is documented in FX / crypto | lab table 'Time of day' (from the next lab run) + journal 'Session' | timing filter |
| timing | Gann time & price (time cycles 30/45/60/90/120/144/180/360 bars from the last major swing, Square of 9, 1x1 fan, cardinal dates) | no peer-reviewed evidence; Gann's own record is unverified | lab table 'Gann time cycles' (pivot near anchor + Gann count vs ordinary offsets; random-walk self-test -1.2 sigma) - waiting for the real-candle run | visual only (chart indicator 'Gann time & price'); not in signals / stars unless the lab shows > +3 sigma on several timeframes |
Playbook (sustainable, re-checked weekly by the lab): daily trend side (radar) -> daily level / breakout / trend setup -> timing from
momentum divergence or a session liquidity sweep on 4h / 1h -> no opposing signal -> checklist (order book + tape agree, no high-impact news +-1h, funding not crowded on our side) -> stop 1.5 ATR, size by volatility -> journal (stores the checklist).
Every weekly lab run can move a detector up or down; the tables in STRATEGY_LAB.md are the source of truth, this table the summary.

## Lab results 2026-10-17 (first real run: 6 crypto + gold + S&P 500, 1m-1d, ~40k signals; full tables in STRATEGY_LAB.md)
- No detector beats the random baseline with statistical confidence on its own (most average R within +-0.07, no costs).
- Higher timeframes are better: pooled avg R 1d +0.043, 4h +0.019, 1h -0.009, 15m -0.025, 1m -0.019.
- Best detector x timeframe (n >= 50): ohl_break 1d +0.50R (54%), sma1040 1d +0.43R, breakout 1d +0.41R, macd_div 1d +0.31R,
  ma_cross 1d +0.27R, m2022 1d +0.24R, fvg 1d +0.19R - all daily, none significant alone yet.
- Schools (pooled avg R): momentum/divergence +0.063, time/sessions +0.043, liquidity +0.034, Fibonacci +0.005, levels -0.004,
  trend MA -0.018, SMC/ICT -0.034, hedge-fund trend -0.037 (intraday dilutes it; daily is positive), Elliott -0.079.
- Confluence: more agreeing families did NOT help; setups with an OPPOSING family lost about -280R in total -> alerts now
  require no opposing signal. Strength = lab evidence (`modules/lab_tiers.py`), not family count.
- OFF (n >= 300 and avg R <= -0.06, recomputed weekly): donch, ew3, msb_ob, ob, unicorn - still drawn, no longer decide a trade.

## Group C + confirmation-only
- **Elliott OTE boxes** (Workspace, `Elliott waves` indicator): yellow 62-79% retracement boxes of each impulse leg (where wave 2 / 4 / A ends); the newest runs to the right edge. Visual only - no stars.
- **Harmonics** were already built from scratch in the Workspace (`harmFind`, XABCD + PRZ box); unchanged.
- **Confirmation only** (`scorer.CONFIRM_ONLY_KEYS`): the direct buy/sell signal "structure break + order block retest" (`msb_ob`) can no longer start a trade or upgrade a trade's horizon; it adds its star only when another primary family already backs the same side. Plain order blocks (`ob`) are unchanged. Super IndiBot (EMA ribbon) is NOT built as a separate signal - the existing MA family (EMA stack / cross) is the confirmation layer.

## Scanner-only flags (`modules/chart_scan.py`) - NOT in stars / alerts yet
IFVG, Mitigation block, MSS/CHoCH, Premium-Discount (outer 30%), Silver Bullet (FVG in a window), Breakout+volume-delta, Harmonics, channel breaks, double top/bottom.
These are candidates for promotion once a walk-forward test on real candles shows they beat the baseline.

## Item 20 - Finviz-style chart patterns (`modules/patterns.py`, Chart Scanner -> Patterns filter)
14 patterns detected on our own candles for any market / timeframe: channel up / down / horizontal, wedge up / down, triangle
ascending / descending / symmetrical, head & shoulders + inverse, multiple top / bottom (3+ equal zigzag swings), trendline
support / resistance (price on a valid line). Finviz does not publish its rules - these are our own geometric rules (see the
module header). The pattern lines are drawn gold on each mini chart; the Buy / Sell switch uses the textbook bias.
**Honest check:** on 400 random-walk charts (no edge by construction) at least one pattern appeared in **41%** of them
(trendline support/resistance 7-8%, H&S 6-7%, multi top/bottom 4%, channels / wedges / triangles 0-4%). So a pattern alone is
NOT evidence; it only becomes useful if a walk-forward test on real candles shows it beats this chance rate.

## Not built yet
- 5 daily candle types (up / up-reversal / down / down-reversal / accumulation around the 00:00 NY open).
- Order-block respect rate (how often each OB held) - needs real history.
- Options flow (Unusual Whales: ask-side, volume > OI, OTM, single leg, premium) - needs a paid API key.

## Evidence (nothing here is proven until it has been run on real candles)
- `python -m modules.backtest_osma` - RSI(2)+OsMA bar rule vs inverse vs trend-filtered.
- `python -m modules.backtest_signals` - trendline break, CISD, Model 2022 vs a random baseline, plus **context_filters**: does killzone / premium-discount / daily bias raise the hit rate?
- Random-walk checks: all tests report ~50% and no false "edge" flags. Published win-rate claims for SMC/ICT (e.g. 58% filtered) come from unaudited sources - treat as hypotheses.

## Filter on/off backtest (not run yet - needs OKX access)
`python -m modules.backtest_filters [BTC-USDT ETH-USDT ...]` walks every detector (Donchian ensemble, Session AMD, ORB, OB / breaker /
unicorn, breakouts, Kill Zone Sniper, Power of Three) with the Group A filters OFF and ON on real OKX candles, against a random-direction
baseline, and prints a Markdown table (also saved to `data/filter_compare.json`). Paste the table here once it has run.
Direction hit-rate only (no costs, stops or targets). Results: **none yet** - the build sandbox cannot reach OKX (HTTP 403 from the egress proxy).
