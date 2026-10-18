# Strategy lab - real candles (2026-10-18)

Symbols: BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, BNB-USDT, DOGE-USDT, HL:xyz:GOLD, HL:xyz:SP500 · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 78 | 46.2 | 0.348 | 43.6 | 0.202 |  |
| 2 | wavec | Elliott wave | 87 | 42.5 | 0.125 | 34.5 | -0.064 |  |
| 3 | zombie | Liquidity | 637 | 42.5 | 0.114 | 38.0 | 0.004 |  |
| 4 | turtle55 | Trend (hedge fund) | 93 | 36.6 | 0.1 | 40.9 | 0.173 |  |
| 5 | macd_div | Momentum / divergence | 972 | 41.3 | 0.094 | 39.3 | 0.043 |  |
| 6 | po3 | Time (sessions) | 94 | 42.6 | 0.088 | 43.6 | 0.186 |  |
| 7 | breakout | Levels / breakouts | 718 | 42.3 | 0.078 | 38.7 | -0.007 |  |
| 8 | abc | Elliott wave | 115 | 39.1 | 0.076 | 28.7 | -0.193 |  |
| 9 | level | Levels / breakouts | 3187 | 41.6 | 0.072 | 38.1 | -0.016 | YES |
| 10 | sess_amd | Time (sessions) | 343 | 42.0 | 0.067 | 42.3 | 0.074 |  |
| 11 | ew5 | Elliott wave | 126 | 38.9 | 0.062 | 32.5 | -0.091 |  |
| 12 | ma_cross | Trend (MA) | 2049 | 39.9 | 0.057 | 38.7 | 0.027 |  |
| 13 | rsi_div | Momentum / divergence | 814 | 38.9 | 0.041 | 37.3 | 0.003 |  |
| 14 | liqline | Liquidity | 1794 | 39.8 | 0.037 | 37.4 | -0.018 |  |
| 15 | judas | Time (sessions) | 1713 | 40.5 | 0.033 | 38.9 | -0.008 |  |
| 16 | vwap | Trend (MA) | 5383 | 39.2 | 0.03 | 36.8 | -0.032 | YES |
| 17 | fvg | SMC / ICT | 2083 | 39.1 | 0.028 | 35.5 | -0.053 | YES |
| 18 | ohl_break | Levels / breakouts | 483 | 39.1 | 0.026 | 35.0 | -0.081 |  |
| 19 | fib | Fibonacci | 1759 | 38.1 | 0.018 | 36.0 | -0.031 |  |
| 20 | cisd | SMC / ICT | 683 | 38.1 | 0.011 | 35.9 | -0.042 |  |
| 21 | ema_stack | Trend (MA) | 3484 | 38.5 | 0.01 | 36.8 | -0.02 |  |
| 22 | tlbreak | Levels / breakouts | 1715 | 38.3 | 0.004 | 39.0 | 0.018 |  |
| 23 | donch | Trend (hedge fund) | 2002 | 38.3 | 0.003 | 37.6 | -0.008 |  |
| 24 | crt | Liquidity | 672 | 37.5 | -0.0 | 36.0 | -0.052 |  |
| 25 | ote | Fibonacci | 616 | 37.3 | -0.001 | 34.6 | -0.07 |  |
| 26 | sweep | Liquidity | 2796 | 37.3 | -0.011 | 37.6 | -0.008 |  |
| 27 | ob | SMC / ICT | 987 | 37.2 | -0.012 | 38.3 | 0.014 |  |
| 28 | m2022 | SMC / ICT | 478 | 36.6 | -0.021 | 40.4 | 0.077 |  |
| 29 | ohl_open | Levels / breakouts | 2425 | 36.7 | -0.025 | 36.6 | -0.032 |  |
| 30 | msb_ob | SMC / ICT | 1356 | 36.9 | -0.029 | 39.6 | 0.03 |  |
| 31 | ew3 | Elliott wave | 759 | 35.8 | -0.063 | 38.6 | 0.022 |  |
| 32 | orb | Time (sessions) | 97 | 37.1 | -0.072 | 33.0 | -0.16 |  |
| 33 | unicorn | SMC / ICT | 325 | 34.2 | -0.088 | 35.1 | -0.048 |  |
| 34 | breaker | SMC / ICT | 258 | 30.6 | -0.145 | 33.3 | -0.069 |  |
| 35 | kzs | Time (sessions) | 20 | 50.0 | 0.332 | 45.0 | 0.125 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Momentum / divergence | 1786 | 0.07 |
| 2 | Time (sessions) | 2267 | 0.039 |
| 3 | Trend (MA) | 10916 | 0.029 |
| 4 | Levels / breakouts | 8528 | 0.029 |
| 5 | Trend (hedge fund) | 2173 | 0.02 |
| 6 | Liquidity | 5899 | 0.018 |
| 7 | Fibonacci | 2375 | 0.013 |
| 8 | SMC / ICT | 6170 | -0.01 |
| 9 | Elliott wave | 1087 | -0.019 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 15m | 48 | 43.8 | 0.29 |
| breaker | 4h | 49 | 42.9 | 0.263 |
| breakout | 1d | 60 | 56.7 | 0.435 |
| cisd | 1h | 156 | 43.6 | 0.126 |
| crt | 1h | 107 | 43.0 | 0.082 |
| donch | 1m | 380 | 44.7 | 0.121 |
| ema_stack | 1m | 702 | 46.7 | 0.175 |
| ew3 | 15m | 193 | 41.5 | 0.079 |
| ew5 | 15m | 38 | 50.0 | 0.334 |
| fib | 1m | 332 | 44.3 | 0.127 |
| fvg | 1m | 614 | 46.1 | 0.158 |
| judas | 1m | 637 | 42.7 | 0.075 |
| level | 1m | 812 | 49.3 | 0.243 |
| liqline | 1d | 164 | 38.4 | 0.127 |
| m2022 | 1d | 105 | 40.0 | 0.133 |
| ma_cross | 1m | 358 | 45.0 | 0.137 |
| macd_div | 1d | 111 | 45.0 | 0.301 |
| msb_ob | 4h | 261 | 38.7 | 0.066 |
| ob | 4h | 210 | 41.4 | 0.101 |
| ohl_break | 1d | 45 | 46.7 | 0.266 |
| ohl_open | 1d | 236 | 31.8 | 0.021 |
| orb | 15m | 95 | 37.9 | -0.053 |
| ote | 4h | 111 | 43.2 | 0.156 |
| po3 | 15m | 46 | 47.8 | 0.218 |
| rsi_div | 1h | 200 | 45.0 | 0.165 |
| sess_amd | 15m | 156 | 44.2 | 0.127 |
| sma1040 | 1d | 78 | 46.2 | 0.348 |
| sweep | 1d | 338 | 34.9 | 0.053 |
| tlbreak | 1d | 214 | 41.1 | 0.214 |
| turtle55 | 1d | 93 | 36.6 | 0.1 |
| unicorn | 1m | 32 | 50.0 | 0.25 |
| vwap | 1m | 1048 | 48.0 | 0.207 |
| zombie | 1d | 75 | 41.3 | 0.215 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 54 | 0.038 | 61 | 0.109 |
| breaker | 116 | -0.327 | 142 | 0.003 |
| breakout | 354 | 0.088 | 364 | 0.067 |
| cisd | 343 | -0.06 | 340 | 0.081 |
| crt | 316 | -0.052 | 356 | 0.046 |
| donch | 909 | 0.022 | 1093 | -0.013 |
| ema_stack | 1715 | -0.008 | 1769 | 0.028 |
| ew3 | 386 | -0.149 | 373 | 0.027 |
| ew5 | 58 | 0.058 | 68 | 0.065 |
| fib | 809 | -0.003 | 950 | 0.035 |
| fvg | 1031 | 0.019 | 1052 | 0.036 |
| judas | 786 | 0.019 | 927 | 0.045 |
| kzs | 14 | 0.546 | 6 | -0.167 |
| level | 2075 | 0.057 | 1112 | 0.102 |
| liqline | 861 | 0.039 | 933 | 0.036 |
| m2022 | 238 | -0.018 | 240 | -0.023 |
| ma_cross | 1022 | 0.032 | 1027 | 0.081 |
| macd_div | 474 | 0.105 | 498 | 0.083 |
| msb_ob | 708 | -0.036 | 648 | -0.022 |
| ob | 517 | -0.015 | 470 | -0.009 |
| ohl_break | 216 | 0.015 | 267 | 0.035 |
| ohl_open | 1266 | -0.026 | 1159 | -0.024 |
| orb | 54 | -0.259 | 43 | 0.163 |
| ote | 290 | -0.039 | 326 | 0.033 |
| po3 | 49 | 0.194 | 45 | -0.029 |
| rsi_div | 409 | 0.009 | 405 | 0.072 |
| sess_amd | 122 | 0.086 | 221 | 0.056 |
| sma1040 | 40 | 0.289 | 38 | 0.409 |
| sweep | 1457 | 0.001 | 1339 | -0.024 |
| tlbreak | 844 | -0.015 | 871 | 0.022 |
| turtle55 | 59 | 0.106 | 34 | 0.089 |
| unicorn | 154 | -0.215 | 171 | 0.026 |
| vwap | 2668 | 0.013 | 2715 | 0.047 |
| wavec | 32 | -0.03 | 55 | 0.215 |
| zombie | 292 | 0.046 | 345 | 0.172 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 24528 | 39.2 | 0.027 | 16596 | 38.3 | 0.013 |
| abc | 29 | 44.8 | 0.182 | 86 | 37.2 | 0.04 |
| breaker | 128 | 35.2 | -0.031 | 130 | 26.2 | -0.258 |
| breakout | 505 | 44.6 | 0.134 | 212 | 37.3 | -0.051 |
| cisd | 254 | 39.8 | 0.041 | 428 | 37.1 | -0.005 |
| crt | 249 | 37.8 | -0.005 | 422 | 37.4 | 0.005 |
| donch | 1768 | 38.7 | 0.015 | 229 | 34.9 | -0.104 |
| ema_stack | 2838 | 38.3 | 0.007 | 639 | 39.3 | 0.03 |
| ew3 | 468 | 38.2 | 0.005 | 289 | 32.2 | -0.166 |
| ew5 | 100 | 42.0 | 0.14 | 26 | 26.9 | -0.237 |
| fib | 903 | 37.2 | -0.006 | 854 | 39.0 | 0.042 |
| fvg | 1253 | 38.5 | 0.007 | 824 | 40.0 | 0.058 |
| judas | 1070 | 43.5 | 0.103 | 634 | 35.5 | -0.087 |
| kzs | 2 | 0.0 | -1.0 | 17 | 52.9 | 0.421 |
| level | 1561 | 42.5 | 0.08 | 1616 | 40.7 | 0.064 |
| liqline | 1041 | 41.1 | 0.068 | 752 | 37.9 | -0.007 |
| m2022 | 237 | 37.1 | -0.018 | 241 | 36.1 | -0.023 |
| ma_cross | 1182 | 41.0 | 0.087 | 864 | 38.5 | 0.019 |
| macd_div | 208 | 40.4 | 0.047 | 762 | 41.5 | 0.106 |
| msb_ob | 682 | 38.7 | 0.02 | 673 | 35.2 | -0.078 |
| ob | 524 | 39.7 | 0.036 | 461 | 34.3 | -0.068 |
| ohl_break | 306 | 38.6 | 0.016 | 176 | 39.8 | 0.035 |
| ohl_open | 1340 | 37.4 | -0.016 | 1077 | 35.8 | -0.036 |
| orb | 44 | 34.1 | -0.148 | 53 | 39.6 | -0.009 |
| ote | 314 | 35.4 | -0.049 | 302 | 39.4 | 0.049 |
| po3 | 48 | 37.5 | -0.037 | 46 | 47.8 | 0.218 |
| rsi_div | 181 | 42.5 | 0.103 | 631 | 38.0 | 0.026 |
| sess_amd | 182 | 40.1 | 0.021 | 161 | 44.1 | 0.119 |
| sma1040 | 36 | 50.0 | 0.373 | 42 | 42.9 | 0.326 |
| sweep | 1273 | 37.9 | -0.006 | 1520 | 36.9 | -0.015 |
| tlbreak | 808 | 37.9 | -0.018 | 907 | 38.6 | 0.023 |
| turtle55 | 72 | 36.1 | 0.099 | 21 | 38.1 | 0.104 |
| unicorn | 172 | 35.5 | -0.056 | 153 | 32.7 | -0.124 |
| vwap | 4381 | 38.6 | 0.014 | 993 | 41.8 | 0.096 |
| wavec | 23 | 52.2 | 0.493 | 64 | 39.1 | -0.007 |
| zombie | 346 | 40.5 | 0.06 | 291 | 45.0 | 0.18 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 4871 | 32.8 | -0.029 |
| Mon | 4940 | 39.0 | 0.01 |
| Sat | 10457 | 39.4 | 0.014 |
| Sun | 6526 | 40.7 | 0.042 |
| Thu | 4610 | 40.8 | 0.092 |
| Tue | 4953 | 36.6 | -0.043 |
| Wed | 4844 | 41.3 | 0.067 |
| Asia 00-07 | 9585 | 40.6 | 0.045 |
| Late 20-24 | 6680 | 37.5 | -0.023 |
| London 07-12 | 6850 | 40.6 | 0.032 |
| New York 12-20 | 13937 | 38.7 | 0.016 |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| sweep | vwap | 4998 | 3051 | 61.0 |
| level | vwap | 5250 | 2544 | 48.5 |
| ema_stack | sweep | 2557 | 1933 | 75.6 |
| ema_stack | level | 2425 | 1300 | 53.6 |
| ohl_open | vwap | 3170 | 1299 | 41.0 |
| macd_div | vwap | 1486 | 1216 | 81.8 |
| fvg | vwap | 3066 | 1093 | 35.6 |
| msb_ob | vwap | 1973 | 1091 | 55.3 |
| fib | vwap | 2270 | 1089 | 48.0 |
| ma_cross | sweep | 1573 | 1049 | 66.7 |
| level | sweep | 2479 | 1028 | 41.5 |
| rsi_div | vwap | 1242 | 993 | 80.0 |
| tlbreak | vwap | 2032 | 944 | 46.5 |
| judas | level | 1839 | 942 | 51.2 |
| ma_cross | vwap | 3110 | 915 | 29.4 |
| ob | vwap | 1551 | 875 | 56.4 |
| level | ma_cross | 1599 | 865 | 54.1 |
| judas | sweep | 1303 | 838 | 64.3 |
| level | ohl_open | 1623 | 832 | 51.3 |
| judas | vwap | 2920 | 806 | 27.6 |
| liqline | vwap | 2296 | 787 | 34.3 |
| fvg | ohl_open | 941 | 777 | 82.6 |
| fvg | level | 1792 | 769 | 42.9 |
| fvg | sweep | 1241 | 750 | 60.4 |
| ohl_open | sweep | 1399 | 731 | 52.3 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 45 | 42.2 | 0.102 |
| 2 families | 511 | 38.7 | 0.055 |
| 2 families (with opposition) | 1262 | 37.6 | -0.013 |
| 3 families | 983 | 41.5 | 0.088 |
| 3 families (with opposition) | 3673 | 38.3 | 0.01 |
| 4+ families | 497 | 36.8 | -0.02 |
| 4+ families (with opposition) | 2267 | 39.9 | 0.036 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 67.6 | 13506 | 67.4 | 186951 | +0.3 |
| 1m shapes 120/180/240/360 deg | 66.1 | 6060 | 65.6 | 6006 | +0.8 |
| 15m | 58.2 | 10634 | 58.1 | 147103 | +0.2 |
| 15m shapes 120/180/240/360 deg | 58.6 | 5758 | 57.9 | 5780 | +1.1 |
| 1h | 56.2 | 9920 | 56.8 | 137515 | -1.2 |
| 1h shapes 120/180/240/360 deg | 56.8 | 5577 | 56.4 | 5573 | +0.6 |
| 4h | 56.1 | 7780 | 57.2 | 107253 | -2.0 |
| 4h shapes 120/180/240/360 deg | 56.4 | 4425 | 56.9 | 4420 | -0.8 |
| 1d | 57.9 | 4438 | 58.3 | 60865 | -0.5 |
| 1d shapes 120/180/240/360 deg | 59.3 | 2604 | 58.6 | 2606 | +0.7 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 90 | 25.6 | +1.079 | +0.863 | +0.90 |
| 1d | 71 | 47.9 | +0.186 | +0.211 | -0.12 |
| 1h | 115 | 25.2 | +0.142 | +0.371 | -1.05 |
| 4h | 108 | 30.6 | -0.053 | +0.173 | -1.06 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2883 | -0.131 |
| 15 days around full moon | 2811 | 0.149 |

Difference t = -3.09 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).
