# Strategy lab - real candles (2026-10-17)

Symbols: BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, BNB-USDT, DOGE-USDT, HL:xyz:GOLD, HL:xyz:SP500 · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 78 | 46.2 | 0.35 | 43.6 | 0.204 |  |
| 2 | wavec | Elliott wave | 88 | 44.3 | 0.17 | 35.2 | -0.065 |  |
| 3 | sess_amd | Time (sessions) | 399 | 45.4 | 0.155 | 41.1 | 0.043 |  |
| 4 | turtle55 | Trend (hedge fund) | 93 | 36.6 | 0.1 | 40.9 | 0.173 |  |
| 5 | macd_div | Momentum / divergence | 970 | 40.8 | 0.087 | 40.4 | 0.075 |  |
| 6 | liqline | Liquidity | 1769 | 41.0 | 0.075 | 38.3 | 0.0 |  |
| 7 | rsi_div | Momentum / divergence | 809 | 40.0 | 0.074 | 38.9 | 0.048 |  |
| 8 | abc | Elliott wave | 101 | 39.6 | 0.054 | 40.6 | 0.071 |  |
| 9 | zombie | Liquidity | 626 | 39.6 | 0.052 | 36.6 | -0.028 |  |
| 10 | level | Levels / breakouts | 3163 | 40.8 | 0.051 | 37.7 | -0.025 | YES |
| 11 | breakout | Levels / breakouts | 704 | 40.8 | 0.043 | 39.3 | 0.01 |  |
| 12 | ma_cross | Trend (MA) | 2005 | 39.1 | 0.04 | 37.6 | -0.003 |  |
| 13 | ew5 | Elliott wave | 120 | 38.3 | 0.029 | 35.0 | -0.066 |  |
| 14 | vwap | Trend (MA) | 5227 | 39.0 | 0.024 | 37.5 | -0.015 |  |
| 15 | ohl_break | Levels / breakouts | 453 | 38.9 | 0.022 | 38.0 | -0.018 |  |
| 16 | m2022 | SMC / ICT | 503 | 38.4 | 0.02 | 35.6 | -0.068 |  |
| 17 | fib | Fibonacci | 1762 | 38.6 | 0.019 | 37.6 | -0.004 |  |
| 18 | ote | Fibonacci | 569 | 38.0 | 0.017 | 39.5 | 0.055 |  |
| 19 | fvg | SMC / ICT | 2017 | 38.3 | 0.01 | 36.3 | -0.036 |  |
| 20 | po3 | Time (sessions) | 106 | 39.6 | 0.01 | 34.0 | -0.126 |  |
| 21 | sweep | Liquidity | 2711 | 37.3 | -0.006 | 36.7 | -0.026 |  |
| 22 | ema_stack | Trend (MA) | 3336 | 37.8 | -0.006 | 37.3 | -0.016 |  |
| 23 | judas | Time (sessions) | 1482 | 38.9 | -0.008 | 37.0 | -0.059 |  |
| 24 | ohl_open | Levels / breakouts | 2453 | 37.5 | -0.01 | 35.9 | -0.053 |  |
| 25 | tlbreak | Levels / breakouts | 1661 | 37.6 | -0.011 | 37.4 | -0.016 |  |
| 26 | crt | Liquidity | 683 | 35.7 | -0.037 | 30.6 | -0.179 |  |
| 27 | donch | Trend (hedge fund) | 1935 | 36.3 | -0.046 | 36.4 | -0.037 |  |
| 28 | cisd | SMC / ICT | 695 | 35.1 | -0.049 | 35.5 | -0.031 |  |
| 29 | msb_ob | SMC / ICT | 1361 | 35.6 | -0.063 | 41.2 | 0.071 |  |
| 30 | unicorn | SMC / ICT | 343 | 33.8 | -0.095 | 32.7 | -0.13 |  |
| 31 | ob | SMC / ICT | 1014 | 33.8 | -0.108 | 37.2 | -0.02 |  |
| 32 | breaker | SMC / ICT | 264 | 31.8 | -0.133 | 39.8 | 0.055 |  |
| 33 | ew3 | Elliott wave | 783 | 32.2 | -0.152 | 37.3 | -0.032 |  |
| 34 | orb | Time (sessions) | 103 | 32.0 | -0.191 | 45.6 | 0.152 |  |
| 35 | kzs | Time (sessions) | 23 | 47.8 | 0.263 | 43.5 | 0.154 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Momentum / divergence | 1779 | 0.081 |
| 2 | Liquidity | 5789 | 0.021 |
| 3 | Levels / breakouts | 8434 | 0.019 |
| 4 | Fibonacci | 2331 | 0.019 |
| 5 | Time (sessions) | 2113 | 0.018 |
| 6 | Trend (MA) | 10568 | 0.018 |
| 7 | Trend (hedge fund) | 2106 | -0.025 |
| 8 | SMC / ICT | 6197 | -0.043 |
| 9 | Elliott wave | 1092 | -0.087 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 15m | 41 | 53.7 | 0.454 |
| breaker | 4h | 51 | 41.2 | 0.104 |
| breakout | 1d | 60 | 56.7 | 0.435 |
| cisd | 1h | 155 | 43.9 | 0.136 |
| crt | 4h | 137 | 36.5 | 0.046 |
| donch | 4h | 361 | 37.1 | -0.006 |
| ema_stack | 1m | 686 | 43.0 | 0.081 |
| ew3 | 15m | 183 | 35.5 | -0.095 |
| fib | 4h | 362 | 40.6 | 0.081 |
| fvg | 1m | 606 | 44.7 | 0.124 |
| judas | 4h | 63 | 39.7 | 0.093 |
| level | 1d | 97 | 41.2 | 0.136 |
| liqline | 1d | 164 | 38.4 | 0.13 |
| m2022 | 1d | 105 | 40.0 | 0.135 |
| ma_cross | 1d | 196 | 35.7 | 0.138 |
| macd_div | 1d | 111 | 45.0 | 0.302 |
| msb_ob | 1m | 259 | 40.2 | 0.017 |
| ob | 4h | 224 | 39.3 | 0.043 |
| ohl_break | 1d | 45 | 46.7 | 0.266 |
| ohl_open | 15m | 627 | 42.9 | 0.087 |
| orb | 15m | 92 | 33.7 | -0.148 |
| ote | 4h | 118 | 42.4 | 0.146 |
| po3 | 1h | 46 | 41.3 | 0.059 |
| rsi_div | 1h | 199 | 43.2 | 0.132 |
| sess_amd | 15m | 155 | 51.0 | 0.311 |
| sma1040 | 1d | 78 | 46.2 | 0.35 |
| sweep | 4h | 574 | 39.7 | 0.077 |
| tlbreak | 1d | 214 | 41.1 | 0.218 |
| turtle55 | 1d | 93 | 36.6 | 0.1 |
| unicorn | 1m | 34 | 44.1 | 0.103 |
| vwap | 1m | 1048 | 44.0 | 0.108 |
| zombie | 1d | 75 | 41.3 | 0.215 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 54 | 0.058 | 47 | 0.049 |
| breaker | 125 | -0.317 | 139 | 0.032 |
| breakout | 308 | 0.061 | 396 | 0.029 |
| cisd | 355 | -0.09 | 340 | -0.005 |
| crt | 335 | -0.09 | 348 | 0.014 |
| donch | 846 | -0.057 | 1089 | -0.038 |
| ema_stack | 1547 | -0.058 | 1789 | 0.039 |
| ew3 | 380 | -0.187 | 403 | -0.118 |
| ew5 | 51 | -0.118 | 69 | 0.138 |
| fib | 833 | -0.075 | 929 | 0.103 |
| fvg | 1002 | -0.038 | 1015 | 0.058 |
| judas | 601 | -0.13 | 881 | 0.076 |
| kzs | 14 | 0.36 | 9 | 0.111 |
| level | 2046 | 0.024 | 1117 | 0.101 |
| liqline | 830 | 0.068 | 939 | 0.081 |
| m2022 | 253 | -0.002 | 250 | 0.042 |
| ma_cross | 972 | -0.009 | 1033 | 0.086 |
| macd_div | 488 | 0.111 | 482 | 0.063 |
| msb_ob | 709 | -0.125 | 652 | 0.004 |
| ob | 534 | -0.166 | 480 | -0.044 |
| ohl_break | 199 | 0.045 | 254 | 0.003 |
| ohl_open | 1224 | -0.023 | 1229 | 0.002 |
| orb | 60 | -0.402 | 43 | 0.105 |
| ote | 262 | -0.117 | 307 | 0.132 |
| po3 | 55 | -0.12 | 51 | 0.151 |
| rsi_div | 421 | 0.03 | 388 | 0.121 |
| sess_amd | 110 | 0.091 | 289 | 0.18 |
| sma1040 | 40 | 0.289 | 38 | 0.414 |
| sweep | 1427 | -0.041 | 1284 | 0.034 |
| tlbreak | 823 | -0.063 | 838 | 0.039 |
| turtle55 | 59 | 0.106 | 34 | 0.089 |
| unicorn | 157 | -0.288 | 186 | 0.068 |
| vwap | 2426 | -0.036 | 2801 | 0.076 |
| wavec | 37 | -0.122 | 51 | 0.382 |
| zombie | 286 | -0.055 | 340 | 0.142 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 23761 | 37.9 | -0.006 | 16578 | 38.9 | 0.029 |
| abc | 28 | 42.9 | 0.135 | 73 | 38.4 | 0.022 |
| breaker | 114 | 34.2 | -0.067 | 150 | 30.0 | -0.183 |
| breakout | 484 | 41.9 | 0.077 | 219 | 38.4 | -0.026 |
| cisd | 262 | 34.7 | -0.071 | 431 | 35.5 | -0.031 |
| crt | 268 | 34.0 | -0.099 | 414 | 37.0 | 0.006 |
| donch | 1708 | 36.1 | -0.05 | 224 | 37.9 | -0.015 |
| ema_stack | 2690 | 37.7 | -0.009 | 638 | 38.6 | 0.01 |
| ew3 | 494 | 31.2 | -0.172 | 286 | 34.3 | -0.107 |
| ew5 | 97 | 41.2 | 0.093 | 23 | 26.1 | -0.237 |
| fib | 871 | 38.6 | 0.026 | 889 | 38.7 | 0.014 |
| fvg | 1187 | 36.6 | -0.04 | 825 | 40.8 | 0.086 |
| judas | 888 | 41.3 | 0.055 | 592 | 35.5 | -0.099 |
| kzs | 1 | 0.0 | -1.0 | 22 | 50.0 | 0.32 |
| level | 1576 | 40.5 | 0.036 | 1580 | 41.1 | 0.07 |
| liqline | 980 | 41.1 | 0.063 | 789 | 40.9 | 0.09 |
| m2022 | 270 | 40.0 | 0.044 | 232 | 36.6 | -0.003 |
| ma_cross | 1191 | 38.3 | 0.017 | 810 | 40.2 | 0.076 |
| macd_div | 220 | 41.4 | 0.079 | 750 | 40.7 | 0.09 |
| msb_ob | 692 | 35.1 | -0.07 | 668 | 36.2 | -0.054 |
| ob | 545 | 36.0 | -0.065 | 466 | 31.3 | -0.158 |
| ohl_break | 254 | 39.4 | 0.034 | 199 | 38.2 | 0.006 |
| ohl_open | 1302 | 35.5 | -0.067 | 1142 | 40.0 | 0.057 |
| orb | 60 | 28.3 | -0.277 | 43 | 37.2 | -0.07 |
| ote | 271 | 39.5 | 0.059 | 297 | 36.7 | -0.018 |
| po3 | 54 | 42.6 | 0.087 | 52 | 36.5 | -0.069 |
| rsi_div | 192 | 46.4 | 0.212 | 617 | 38.1 | 0.031 |
| sess_amd | 214 | 43.0 | 0.099 | 184 | 47.8 | 0.214 |
| sma1040 | 36 | 50.0 | 0.373 | 42 | 42.9 | 0.33 |
| sweep | 1231 | 35.2 | -0.064 | 1477 | 39.1 | 0.045 |
| tlbreak | 777 | 37.8 | -0.02 | 882 | 37.4 | -0.002 |
| turtle55 | 72 | 36.1 | 0.099 | 21 | 38.1 | 0.104 |
| unicorn | 174 | 33.3 | -0.098 | 169 | 34.3 | -0.091 |
| vwap | 4187 | 38.4 | 0.007 | 1031 | 41.6 | 0.094 |
| wavec | 27 | 48.1 | 0.406 | 61 | 42.6 | 0.066 |
| zombie | 344 | 37.5 | -0.006 | 280 | 42.5 | 0.13 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 4831 | 33.8 | -0.025 |
| Mon | 4811 | 39.0 | 0.007 |
| Sat | 12486 | 38.5 | -0.008 |
| Sun | 3998 | 36.3 | -0.072 |
| Thu | 4707 | 39.7 | 0.065 |
| Tue | 4836 | 37.8 | -0.004 |
| Wed | 4740 | 42.2 | 0.099 |
| Asia 00-07 | 8879 | 38.9 | 0.006 |
| Late 20-24 | 4960 | 38.1 | -0.014 |
| London 07-12 | 8868 | 39.5 | 0.004 |
| New York 12-20 | 13555 | 38.3 | 0.009 |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| sweep | vwap | 4801 | 2895 | 60.3 |
| level | vwap | 5285 | 2487 | 47.1 |
| ema_stack | sweep | 2388 | 1816 | 76.0 |
| ohl_open | vwap | 3307 | 1444 | 43.7 |
| ema_stack | level | 2411 | 1196 | 49.6 |
| macd_div | vwap | 1465 | 1186 | 81.0 |
| fib | vwap | 2249 | 1118 | 49.7 |
| msb_ob | vwap | 1976 | 1089 | 55.1 |
| fvg | vwap | 3003 | 1072 | 35.7 |
| level | sweep | 2479 | 1040 | 42.0 |
| ma_cross | sweep | 1518 | 1004 | 66.1 |
| rsi_div | vwap | 1215 | 981 | 80.7 |
| tlbreak | vwap | 1957 | 956 | 48.9 |
| level | ohl_open | 1780 | 930 | 52.2 |
| ob | vwap | 1609 | 901 | 56.0 |
| ma_cross | vwap | 3055 | 897 | 29.4 |
| judas | level | 1604 | 857 | 53.4 |
| liqline | vwap | 2314 | 828 | 35.8 |
| level | ma_cross | 1587 | 826 | 52.0 |
| fvg | level | 1809 | 806 | 44.6 |
| fvg | ohl_open | 982 | 773 | 78.7 |
| ohl_open | sweep | 1426 | 738 | 51.8 |
| fvg | sweep | 1214 | 735 | 60.5 |
| judas | vwap | 2432 | 726 | 29.9 |
| judas | sweep | 1093 | 689 | 63.0 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 53 | 34.0 | -0.091 |
| 2 families | 429 | 42.0 | 0.13 |
| 2 families (with opposition) | 1212 | 36.6 | -0.02 |
| 3 families | 958 | 41.4 | 0.082 |
| 3 families (with opposition) | 3552 | 37.6 | -0.01 |
| 4+ families | 501 | 35.7 | -0.039 |
| 4+ families (with opposition) | 2174 | 37.8 | -0.017 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 69.7 | 14483 | 70.0 | 200471 | -0.7 |
| 1m shapes 120/180/240/360 deg | 67.6 | 6501 | 67.5 | 6411 | +0.2 |
| 15m | 58.7 | 10155 | 58.5 | 140615 | +0.4 |
| 15m shapes 120/180/240/360 deg | 59.0 | 5507 | 58.7 | 5531 | +0.4 |
| 1h | 56.2 | 9403 | 56.8 | 130311 | -1.1 |
| 1h shapes 120/180/240/360 deg | 56.9 | 5290 | 56.3 | 5285 | +0.8 |
| 4h | 56.1 | 7773 | 57.2 | 107114 | -2.0 |
| 4h shapes 120/180/240/360 deg | 56.4 | 4418 | 57.0 | 4414 | -0.8 |
| 1d | 57.9 | 4438 | 58.3 | 60852 | -0.5 |
| 1d shapes 120/180/240/360 deg | 59.3 | 2604 | 58.6 | 2606 | +0.7 |
Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (grid fitted on the first 60 % of each series, traded on the last 40 %; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 1d | 30 | 20.0 | -0.452 | -0.281 | -0.54 |
| 1h | 52 | 32.7 | +0.022 | -0.195 | +0.89 |
| 4h | 56 | 30.4 | +0.122 | -0.108 | +1.08 |
Random-walk self-test: rule +0.16R (1.6 standard errors, 265 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2882 | -0.133 |
| 15 days around full moon | 2811 | 0.149 |
Difference t = -3.11 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).
