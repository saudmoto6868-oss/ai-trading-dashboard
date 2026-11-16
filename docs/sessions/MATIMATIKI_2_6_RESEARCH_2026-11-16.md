# Matimatiki 2.6 — Research & Backtesting Session
**Date:** 2026-11-16  
**Project:** 6868-group/ai-trading-dashboard (88622818)  
**Meeting Room index:** docs/MEETING_ROOM.md  
**Topic:** @gold_.trade / Matimatiki 2.6 / XAUUSD

> Archive fidelity: This document preserves the findings, test definitions, numerical results, caveats, and decisions available in the current working conversation. The chat interface did not expose every earlier message verbatim, so this is a faithful session record from available context, not a byte-for-byte export of the entire chat transcript. Missing dialogue has not been invented.

## Objective
Review @gold_.trade and the supplied videos; separate the three Matimatiki 2.6 videos from the independent 14-candle average strategy; research public explanations; test candidate rules on gold; record findings before any AI Trading Dashboard integration.

Instagram: https://www.instagram.com/gold_.trade/

## User-provided video evidence
Six MP4 uploads were imported into Descript:

| Upload | Duration | Descript project |
|---|---:|---|
| telegram-cloud-document-4-6041731908327448519.mp4 | 37.52 s | 4c09f986-b8b7-4d98-a56a-01a954a53a51 |
| telegram-cloud-document-4-6041731908327448518.mp4 | 28.19 s | 4bfd8ca5-5d71-4df6-a003-dd10ba2d1755 |
| telegram-cloud-document-4-6041731908327448517.mp4 | 23.45 s | 465a1ec3-7adb-4171-b869-80303504f361 |
| telegram-cloud-document-4-6041731908327448506.mp4 | 43.37 s | d1f84315-7806-4248-8fcc-9ee0d315f28d |
| telegram-cloud-document-4-6041731908327448505.mp4 | 26.38 s | 27d9ef96-9069-4dde-b7ad-f4e2e87b300b |
| telegram-cloud-document-4-6041731908327448504.mp4 | 25.17 s | 00dbb2d6-a836-411c-88c0-f2cf16ee3f54 |

Prior classification: exactly three videos concern 2.6; the 14-candle method is separate; other material includes liquidity/price action and a days/time-cycle explanation; one Russian ASR transcript was too garbled for reliable extraction.

A supplied chart reference showed 44 / 2.6 ≈ 16.9, nearby values 44.06 and 16.98, and a SELL ZONE at 4314.50 with target 4286.39. This image alone does not establish the complete method.

### 14-candle strategy — separate
The transcript of the 37.52-second upload was translated approximately:
- The method consists of 14 candles.
- Take each candle's range from minimum to maximum.
- Add the ranges.
- Divide the sum by ten.
The remainder was garbled. This remains separate from 2.6.

### Other video transcript evidence
A separate clip (Descript project 27d9ef96-9069-4dde-b7ad-f4e2e87b300b) appeared to describe a zone, confirmation for sell/buy, a minimum breakout, measuring min-to-max distance, a calculator result, and a zone below the minimum described as a buy zone; the speaker later mentioned 60 points profit. ASR ambiguously rendered the divisor as possibly 2.6, so that interpretation is provisional.

Another clip described liquidity being taken on one side and price moving toward liquidity, warning against assuming a simple break/retest continuation. A separate time-cycle clip mentioned 153, 164 and 155 days, with derived values 58, 63 and 44. It is not merged into the 2.6 price formula.

## External research and attribution
The public Coachli profile for Dilyorjon Kamoldinov advertises a product called “2.6 Mathematical Strategy” for XAUUSD, but the public page did not disclose the complete formula, lesson files, indicator source, or independently verified performance:
- Profile: https://www.coachli.co/@dilyorjon_trades
- Product: https://www.coachli.co/@dilyorjon_trades/product/26-mathematical-strategy?id=15724
- Booking: https://www.coachli.co/%40dilyorjon_trades/session/book-a-1-on-1-session-with-dilyorjon-kamoldinov?id=13890
- Telegram contact: https://t.me/GoldtradeDilyorbek

No reliable independent personal website was established in the available research. Instagram scraping was incomplete; no claim is made that every Reel was reviewed. vidIQ provider was out of credits until 2026-12-13 in the prior record.

Independent YouTube examples (not verified Dilyorjon material):
- ADFX “2.6 STRATEGY BREAKDOWN!!!”: https://www.youtube.com/watch?v=Y9vAo_Jcsfk — swing range divided by 2.6, Fibonacci context such as 0.618, confirmation emphasized. Transcript examples: 185.33 / 2.6 = 71.28; 116.60 / 2.6 = 44.84.
- Independent entry model: https://www.youtube.com/watch?v=rPwKYIf2pPI — HTF trend, BOS, measure a move, divide by 2.6, then wait for liquidity/FVG/CHoCH confirmation and return to the zone.
- Nitish FX: https://www.youtube.com/watch?v=njhA722jKHw — Hindi ASR describes sweep/BOS, internal structure and a measured move divided by 2.6; numeric values are ambiguous.
- Trades By Davis: https://www.youtube.com/watch?v=2MKmTCU_1Ic

These similarities are research leads only, not proof of shared origin or the original creator's exact rules.

## Mathematical clarification
- 1 / 2.6 = 0.384615... = **38.46%**.
- 1 / 2.618 ≈ 0.381971 = **38.20%**.
They are close but not identical. Initial tests found very similar signals; no stable evidence justified replacing 2.6 with 2.618.

## Backtesting — data and assumptions
- XAU/USD daily OHLC: 25 March 2019 to 16 November 2026 (up to 2,000 bars requested).
- XAU/USD 4H OHLC: 1 March 2024 to 16 November 2026 (5,000 bars).
- Additional 1H and 15m samples used for exploratory checks.
- GC=F / COMEX hourly OHLCV retrieved separately. Estimated Value Area distributes each hourly candle's volume evenly across its high-low range; this is an approximation, **not true trades-at-price volume profile data**.
- Cost sensitivity assumed $0.60 and $1.00 per ounce. These are assumptions, not the user's broker's actual spread, commission or slippage.

## Primary candidate: Daily swing → 2.6 touch → 4H BOS → EMA
Rules tested:
1. Detect latest confirmed daily swing using 3 bars left and 3 bars right.
2. Compute range R = H - L.
3. Bullish level = H - R/2.6; bearish level = L + R/2.6.
4. Wait for 4H candle to touch level and close back on expected side.
5. Wait for BOS on 4H within six bars.
6. EMA-filtered version requires price on correct side of EMA20 and EMA200 at entry.
7. Stop beyond the extreme formed from touch through BOS confirmation, with $0.50 buffer.
8. Compare 2R and 3R targets.
9. Deduct assumed $0.60 cost; also test $1.00.
10. Trades are non-overlapping; exit is stop, target, or 48 bars after entry.

Caveats:
- Swing pivots use right-side bars and only become available after confirmation.
- OHLC cannot reveal intrabar order of stop and target; if both touched in one bar, stop is counted first.
- Exploratory results, not broker-specific tick-accurate simulation.

### Results at 2R, assumed $0.60 cost

| Variant | Trades | Win rate | Expectancy | Profit Factor |
|---|---:|---:|---:|---:|
| 2.6 touch only | 88 | 38.6% | +0.095R | 1.15 |
| 2.6 + BOS | 40 | 50.0% | +0.400R | 1.88 |
| 2.6 + BOS + EMA20/200 | 34 | 52.9% | +0.474R | 2.14 |
| 2.6 + FVG + BOS | 19 | 47.4% | +0.445R | 1.90 |
| 2.6 + FVG + BOS + EMA | 15 | 46.7% | +0.438R | 1.89 |

BOS+EMA cumulative net +16.12R; maximum cumulative drawdown 5.05R. At $1.00 assumed cost: +15.80R and PF 2.10.

### Target sensitivity — BOS + EMA

| Target | Trades | Win rate | Expectancy | PF |
|---|---:|---:|---:|---:|
| 1.5R | 34 | 52.9% | +0.290R | 1.70 |
| 2R | 34 | 52.9% | +0.474R | 2.14 |
| 3R | 34 | 50.0% | +0.646R | 2.45 |

At 3R total net +21.95R and max drawdown 5.05R. This does not prove 3R is optimal; sample size and simplified exit model limit confidence.

### Chronological split
For BOS+EMA at 2R:
- First 70%: 23 trades, 43.5% win rate, +0.218R expectancy, PF 1.45.
- Last 30%: 11 trades, 72.7% win rate, +1.01R expectancy, PF 4.66.
The holdout has only 11 trades, so this is weak evidence, not robust out-of-sample validation.

### FVG result
- FVG+BOS: 19 trades, +0.445R expectancy, PF 1.90.
- FVG+BOS+EMA: 15 trades, +0.438R expectancy, PF 1.89.
FVG did not convincingly outperform BOS+EMA alone. Keep it optional, not mandatory.

### Value Area / Volume Profile exploratory test
Estimated previous-session GC profile:
- 2.6 baseline: 100 trades, +0.008R expectancy, PF 1.01.
- Level inside previous Value Area: 60 trades, -0.210R, PF 0.72.
- Near VAH/VAL: 20 trades, -0.568R, PF 0.34.
- Near POC: 42 trades, +0.111R, PF 1.18.
Not conclusive because volume distribution was approximated from hourly OHLCV. POC confluence is a research lead only; true trades-at-price data is needed.

### Liquidity expansion variant
A simple breakout/sweep → range divided by 2.6 → projected zone → retest model was tested on 4H with 10, 20, 40 and 60-bar lookbacks and alternative projection anchors. Most simple configurations were negative after assumed costs. Example: 20-bar range-edge projection, 75 trades, 33.3% win rate, -0.078R expectancy, PF 0.89. Do not proceed until original video rules are extracted more accurately.

## Research conclusion
**Best current research candidate:** Daily confirmed swing → 2.6 retracement level → 4H touch/rejection → 4H BOS within six bars → EMA20/EMA200 direction filter.

**Do not call this the original Dilyorjon strategy yet.** Public material does not disclose enough exact rules to prove attribution.

Status:
- BOS: strongest improvement over touch-only entry.
- EMA20/EMA200: promising added filter in this sample.
- FVG: optional, not mandatory.
- Value Area/POC: needs genuine trades-at-price data.
- Simple liquidity-expansion projection: reject for now.
- 14-candle average: keep separate.
- Time-cycle method: keep separate pending independent tests.

## Next research gates before live use
1. Obtain better XAUUSD and COMEX GC intraday data, including bid/ask, spread, commission and slippage.
2. Re-run 1m/5m/15m/1H/4H with exact session boundaries and news filters.
3. Use proper walk-forward / untouched out-of-sample period with enough trades; do not tune on holdout.
4. Resolve intrabar stop/target ordering using lower-timeframe or tick data.
5. Test partial exits, break-even, trailing stops and maximum holding time separately.
6. Reinspect the three original 2.6 videos visually and verify every rule; preserve 14-candle method separately.
7. Only then port candidate into AI Trading Dashboard as a research engine with independent toggles and anti-lookahead checks. No Pine Script or production trading code was changed in this research.

## Source links
- Instagram: https://www.instagram.com/gold_.trade/
- Coachli profile: https://www.coachli.co/@dilyorjon_trades
- Coachli 2.6 product: https://www.coachli.co/@dilyorjon_trades/product/26-mathematical-strategy?id=15724
- Telegram contact: https://t.me/GoldtradeDilyorbek
- ADFX independent video: https://www.youtube.com/watch?v=Y9vAo_Jcsfk
- Independent entry model: https://www.youtube.com/watch?v=rPwKYIf2pPI
- Nitish FX: https://www.youtube.com/watch?v=njhA722jKHw
- Trades By Davis: https://www.youtube.com/watch?v=2MKmTCU_1Ic

**Session decision:** retain BOS+EMA as leading research candidate, not live-trading approval. Continue validation before integration.
