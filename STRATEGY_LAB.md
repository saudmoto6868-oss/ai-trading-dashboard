# Strategy lab - real candles (2026-10-18)

Symbols: BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, BNB-USDT, DOGE-USDT, HL:xyz:GOLD, HL:xyz:SP500 · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 78 | 46.2 | 0.351 | 43.6 | 0.205 |  |
| 2 | sess_amd | Time (sessions) | 360 | 45.8 | 0.182 | 41.9 | 0.086 |  |
| 3 | wavec | Elliott wave | 88 | 42.0 | 0.1 | 42.0 | 0.109 |  |
| 4 | turtle55 | Trend (hedge fund) | 93 | 36.6 | 0.1 | 40.9 | 0.173 |  |
| 5 | zombie | Liquidity | 655 | 41.1 | 0.088 | 39.1 | 0.04 |  |
| 6 | level | Levels / breakouts | 3154 | 41.9 | 0.083 | 37.8 | -0.024 | YES |
| 7 | abc | Elliott wave | 103 | 39.8 | 0.066 | 30.1 | -0.195 |  |
| 8 | breakout | Levels / breakouts | 753 | 40.9 | 0.052 | 40.5 | 0.038 |  |
| 9 | rsi_div | Momentum / divergence | 824 | 39.6 | 0.047 | 38.1 | 0.025 |  |
| 10 | macd_div | Momentum / divergence | 988 | 39.6 | 0.046 | 39.5 | 0.047 |  |
| 11 | m2022 | SMC / ICT | 438 | 38.8 | 0.036 | 42.7 | 0.135 |  |
| 12 | po3 | Time (sessions) | 89 | 40.4 | 0.033 | 41.6 | 0.145 |  |
| 13 | ew5 | Elliott wave | 106 | 37.7 | 0.029 | 46.2 | 0.208 |  |
| 14 | liqline | Liquidity | 1843 | 38.9 | 0.023 | 40.3 | 0.054 |  |
| 15 | judas | Time (sessions) | 1708 | 40.2 | 0.02 | 39.6 | 0.008 |  |
| 16 | ma_cross | Trend (MA) | 2038 | 38.4 | 0.019 | 38.4 | 0.013 |  |
| 17 | fvg | SMC / ICT | 2067 | 38.4 | 0.014 | 36.5 | -0.029 |  |
| 18 | vwap | Trend (MA) | 5383 | 38.5 | 0.013 | 37.7 | -0.013 |  |
| 19 | ote | Fibonacci | 645 | 37.8 | 0.006 | 37.4 | -0.002 |  |
| 20 | cisd | SMC / ICT | 710 | 37.7 | 0.004 | 37.5 | -0.003 |  |
| 21 | ohl_open | Levels / breakouts | 2410 | 38.0 | 0.002 | 36.8 | -0.038 |  |
| 22 | fib | Fibonacci | 1812 | 37.5 | -0.002 | 34.7 | -0.071 |  |
| 23 | tlbreak | Levels / breakouts | 1727 | 37.9 | -0.004 | 39.1 | 0.016 |  |
| 24 | ema_stack | Trend (MA) | 3490 | 37.5 | -0.009 | 37.4 | -0.013 |  |
| 25 | donch | Trend (hedge fund) | 2040 | 36.9 | -0.023 | 38.4 | 0.011 |  |
| 26 | sweep | Liquidity | 2780 | 36.7 | -0.024 | 38.7 | 0.017 |  |
| 27 | crt | Liquidity | 651 | 35.5 | -0.035 | 35.0 | -0.07 |  |
| 28 | ohl_break | Levels / breakouts | 483 | 36.0 | -0.061 | 42.0 | 0.088 |  |
| 29 | msb_ob | SMC / ICT | 1346 | 35.1 | -0.073 | 38.0 | -0.01 |  |
| 30 | ob | SMC / ICT | 967 | 33.8 | -0.098 | 37.2 | -0.012 |  |
| 31 | ew3 | Elliott wave | 775 | 33.3 | -0.131 | 38.8 | 0.015 |  |
| 32 | unicorn | SMC / ICT | 341 | 32.0 | -0.133 | 36.4 | -0.033 |  |
| 33 | breaker | SMC / ICT | 257 | 30.4 | -0.141 | 34.2 | -0.053 |  |
| 34 | orb | Time (sessions) | 98 | 32.7 | -0.175 | 39.8 | 0.037 |  |
| 35 | kzs | Time (sessions) | 18 | 38.9 | 0.058 | 44.4 | 0.111 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Momentum / divergence | 1812 | 0.046 |
| 2 | Time (sessions) | 2273 | 0.038 |
| 3 | Levels / breakouts | 8527 | 0.032 |
| 4 | Trend (MA) | 10911 | 0.007 |
| 5 | Liquidity | 5929 | 0.002 |
| 6 | Fibonacci | 2457 | 0.0 |
| 7 | Trend (hedge fund) | 2211 | -0.005 |
| 8 | SMC / ICT | 6126 | -0.037 |
| 9 | Elliott wave | 1072 | -0.077 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 15m | 43 | 51.2 | 0.408 |
| breaker | 4h | 53 | 41.5 | 0.234 |
| breakout | 1d | 60 | 56.7 | 0.435 |
| cisd | 4h | 143 | 37.8 | 0.035 |
| crt | 4h | 129 | 41.1 | 0.111 |
| donch | 1m | 383 | 43.9 | 0.124 |
| ema_stack | 1m | 703 | 46.7 | 0.186 |
| ew3 | 15m | 197 | 38.1 | -0.033 |
| ew5 | 15m | 32 | 65.6 | 0.711 |
| fib | 1h | 463 | 39.7 | 0.027 |
| fvg | 1m | 609 | 44.3 | 0.126 |
| judas | 15m | 563 | 40.5 | 0.04 |
| level | 1m | 811 | 48.0 | 0.217 |
| liqline | 1d | 164 | 38.4 | 0.129 |
| m2022 | 15m | 86 | 45.3 | 0.221 |
| ma_cross | 1d | 196 | 35.7 | 0.137 |
| macd_div | 1d | 111 | 45.0 | 0.302 |
| msb_ob | 4h | 259 | 38.2 | 0.066 |
| ob | 4h | 208 | 38.5 | 0.043 |
| ohl_break | 1d | 45 | 46.7 | 0.266 |
| ohl_open | 15m | 647 | 40.5 | 0.035 |
| orb | 15m | 94 | 34.0 | -0.14 |
| ote | 4h | 112 | 40.2 | 0.102 |
| po3 | 1h | 37 | 43.2 | 0.11 |
| rsi_div | 1h | 209 | 43.5 | 0.137 |
| sess_amd | 15m | 157 | 49.7 | 0.278 |
| sma1040 | 1d | 78 | 46.2 | 0.351 |
| sweep | 1d | 338 | 34.9 | 0.053 |
| tlbreak | 1d | 214 | 41.1 | 0.217 |
| turtle55 | 1d | 93 | 36.6 | 0.1 |
| unicorn | 4h | 70 | 35.7 | -0.013 |
| vwap | 1m | 1048 | 47.0 | 0.192 |
| zombie | 1d | 75 | 41.3 | 0.215 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 46 | 0.044 | 57 | 0.084 |
| breaker | 119 | -0.181 | 138 | -0.106 |
| breakout | 400 | 0.034 | 353 | 0.073 |
| cisd | 355 | -0.052 | 355 | 0.06 |
| crt | 305 | -0.111 | 346 | 0.032 |
| donch | 959 | -0.041 | 1081 | -0.006 |
| ema_stack | 1698 | -0.047 | 1792 | 0.026 |
| ew3 | 384 | -0.173 | 391 | -0.089 |
| ew5 | 46 | -0.219 | 60 | 0.22 |
| fib | 863 | -0.106 | 949 | 0.092 |
| fvg | 1057 | -0.016 | 1010 | 0.046 |
| judas | 799 | -0.073 | 909 | 0.102 |
| kzs | 13 | 0.272 | 5 | -0.5 |
| level | 2071 | 0.076 | 1083 | 0.096 |
| liqline | 900 | -0.01 | 943 | 0.055 |
| m2022 | 238 | 0.007 | 200 | 0.07 |
| ma_cross | 1020 | -0.011 | 1018 | 0.049 |
| macd_div | 486 | 0.06 | 502 | 0.033 |
| msb_ob | 712 | -0.083 | 634 | -0.06 |
| ob | 499 | -0.112 | 468 | -0.083 |
| ohl_break | 228 | -0.124 | 255 | -0.005 |
| ohl_open | 1252 | -0.011 | 1158 | 0.016 |
| orb | 55 | -0.439 | 43 | 0.163 |
| ote | 297 | -0.113 | 348 | 0.107 |
| po3 | 44 | -0.128 | 45 | 0.19 |
| rsi_div | 423 | -0.012 | 401 | 0.109 |
| sess_amd | 116 | 0.195 | 244 | 0.176 |
| sma1040 | 40 | 0.289 | 38 | 0.415 |
| sweep | 1455 | -0.035 | 1325 | -0.013 |
| tlbreak | 843 | -0.039 | 884 | 0.03 |
| turtle55 | 59 | 0.106 | 34 | 0.089 |
| unicorn | 165 | -0.181 | 176 | -0.087 |
| vwap | 2642 | -0.014 | 2741 | 0.04 |
| wavec | 34 | 0.103 | 54 | 0.099 |
| zombie | 298 | -0.021 | 357 | 0.179 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 24757 | 38.2 | 0.003 | 16499 | 38.0 | 0.008 |
| abc | 26 | 57.7 | 0.511 | 76 | 34.2 | -0.072 |
| breaker | 123 | 28.5 | -0.157 | 134 | 32.1 | -0.126 |
| breakout | 555 | 44.1 | 0.129 | 195 | 31.8 | -0.164 |
| cisd | 260 | 39.6 | 0.022 | 449 | 36.7 | -0.004 |
| crt | 244 | 34.8 | -0.081 | 405 | 35.8 | -0.009 |
| donch | 1812 | 37.1 | -0.015 | 225 | 35.1 | -0.083 |
| ema_stack | 2856 | 37.4 | -0.015 | 628 | 38.1 | 0.012 |
| ew3 | 486 | 32.1 | -0.154 | 289 | 35.3 | -0.091 |
| ew5 | 86 | 37.2 | 0.026 | 20 | 40.0 | 0.043 |
| fib | 921 | 36.6 | -0.023 | 889 | 38.4 | 0.017 |
| fvg | 1250 | 37.9 | -0.005 | 816 | 39.1 | 0.041 |
| judas | 1092 | 42.7 | 0.079 | 610 | 35.6 | -0.088 |
| kzs | 3 | 0.0 | -1.0 | 15 | 46.7 | 0.269 |
| level | 1585 | 41.8 | 0.07 | 1561 | 42.2 | 0.099 |
| liqline | 1067 | 40.2 | 0.047 | 774 | 37.1 | -0.009 |
| m2022 | 226 | 39.4 | 0.023 | 212 | 38.2 | 0.049 |
| ma_cross | 1219 | 38.6 | 0.025 | 817 | 38.2 | 0.012 |
| macd_div | 212 | 40.6 | 0.05 | 776 | 39.3 | 0.045 |
| msb_ob | 662 | 36.1 | -0.049 | 682 | 34.3 | -0.093 |
| ob | 509 | 35.8 | -0.066 | 456 | 31.6 | -0.135 |
| ohl_break | 305 | 36.7 | -0.055 | 178 | 34.8 | -0.071 |
| ohl_open | 1341 | 37.9 | -0.009 | 1061 | 38.1 | 0.013 |
| orb | 54 | 35.2 | -0.105 | 44 | 29.5 | -0.261 |
| ote | 296 | 35.5 | -0.039 | 348 | 39.7 | 0.039 |
| po3 | 44 | 40.9 | 0.023 | 45 | 40.0 | 0.043 |
| rsi_div | 186 | 48.4 | 0.236 | 638 | 37.0 | -0.008 |
| sess_amd | 204 | 45.1 | 0.171 | 156 | 46.8 | 0.196 |
| sma1040 | 36 | 50.0 | 0.373 | 42 | 42.9 | 0.331 |
| sweep | 1254 | 36.0 | -0.041 | 1524 | 37.3 | -0.011 |
| tlbreak | 836 | 36.6 | -0.058 | 891 | 39.2 | 0.047 |
| turtle55 | 72 | 36.1 | 0.099 | 21 | 38.1 | 0.104 |
| unicorn | 175 | 34.3 | -0.087 | 166 | 29.5 | -0.181 |
| vwap | 4371 | 38.0 | -0.001 | 1002 | 40.3 | 0.068 |
| wavec | 25 | 40.0 | 0.173 | 63 | 42.9 | 0.071 |
| zombie | 364 | 40.1 | 0.071 | 291 | 42.3 | 0.11 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 4903 | 33.1 | -0.046 |
| Mon | 5098 | 39.5 | 0.022 |
| Sat | 9726 | 38.8 | 0.007 |
| Sun | 7222 | 39.4 | 0.017 |
| Thu | 4651 | 38.2 | 0.034 |
| Tue | 4896 | 35.9 | -0.059 |
| Wed | 4822 | 40.9 | 0.055 |
| Asia 00-07 | 11450 | 38.1 | -0.012 |
| Late 20-24 | 5020 | 38.8 | 0.007 |
| London 07-12 | 6767 | 40.7 | 0.041 |
| New York 12-20 | 13932 | 37.9 | -0.008 |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| sweep | vwap | 4908 | 2973 | 60.6 |
| level | vwap | 5178 | 2518 | 48.6 |
| ema_stack | sweep | 2502 | 1883 | 75.3 |
| ohl_open | vwap | 3153 | 1348 | 42.8 |
| ema_stack | level | 2385 | 1283 | 53.8 |
| macd_div | vwap | 1517 | 1247 | 82.2 |
| fib | vwap | 2331 | 1141 | 48.9 |
| msb_ob | vwap | 1954 | 1077 | 55.1 |
| fvg | vwap | 3031 | 1073 | 35.4 |
| rsi_div | vwap | 1278 | 1045 | 81.8 |
| ma_cross | sweep | 1537 | 1001 | 65.1 |
| level | sweep | 2412 | 971 | 40.3 |
| tlbreak | vwap | 2036 | 964 | 47.3 |
| ma_cross | vwap | 3083 | 907 | 29.4 |
| judas | level | 1825 | 902 | 49.4 |
| ob | vwap | 1535 | 857 | 55.8 |
| level | ohl_open | 1599 | 836 | 52.3 |
| judas | vwap | 2937 | 836 | 28.5 |
| liqline | vwap | 2358 | 821 | 34.8 |
| level | ma_cross | 1535 | 821 | 53.5 |
| judas | sweep | 1234 | 790 | 64.0 |
| fvg | level | 1751 | 788 | 45.0 |
| fvg | ohl_open | 944 | 764 | 80.9 |
| ohl_open | sweep | 1374 | 718 | 52.3 |
| liqline | sweep | 1281 | 712 | 55.6 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 50 | 42.0 | 0.113 |
| 2 families | 492 | 39.4 | 0.061 |
| 2 families (with opposition) | 1269 | 37.1 | -0.019 |
| 3 families | 1006 | 38.3 | 0.009 |
| 3 families (with opposition) | 3651 | 38.8 | 0.021 |
| 4+ families | 527 | 35.1 | -0.057 |
| 4+ families (with opposition) | 2246 | 37.8 | -0.012 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 67.8 | 13245 | 67.6 | 182249 | +0.5 |
| 1m shapes 120/180/240/360 deg | 67.4 | 5870 | 67.4 | 5859 | +0.1 |
| 15m | 58.1 | 10631 | 58.0 | 147296 | +0.3 |
| 15m shapes 120/180/240/360 deg | 58.7 | 5761 | 58.5 | 5781 | +0.3 |
| 1h | 56.3 | 9911 | 56.8 | 137358 | -1.2 |
| 1h shapes 120/180/240/360 deg | 56.8 | 5571 | 56.9 | 5569 | -0.1 |
| 4h | 56.1 | 7780 | 57.2 | 107301 | -2.0 |
| 4h shapes 120/180/240/360 deg | 56.4 | 4426 | 57.0 | 4422 | -0.8 |
| 1d | 57.9 | 4438 | 58.3 | 60865 | -0.5 |
| 1d shapes 120/180/240/360 deg | 59.3 | 2604 | 58.6 | 2606 | +0.7 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 90 | 26.7 | +1.118 | -0.219 | +1.55 |
| 1d | 72 | 47.2 | +0.169 | +0.241 | -0.41 |
| 1h | 89 | 28.1 | +0.393 | +0.381 | +0.05 |
| 4h | 108 | 30.6 | -0.053 | +0.355 | -1.92 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2883 | -0.133 |
| 15 days around full moon | 2811 | 0.149 |

Difference t = -3.09 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).
