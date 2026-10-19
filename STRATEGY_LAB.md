# Strategy lab - real candles (2026-10-19)

Symbols: BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, BNB-USDT, DOGE-USDT, HL:xyz:GOLD, HL:xyz:SP500 · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | turtle55 | Trend (hedge fund) | 77 | 45.5 | 0.387 | 53.2 | 0.532 |  |
| 2 | sma1040 | Trend (hedge fund) | 87 | 44.8 | 0.3 | 44.8 | 0.289 |  |
| 3 | abc | Elliott wave | 104 | 42.3 | 0.164 | 40.4 | 0.073 |  |
| 4 | po3 | Time (sessions) | 94 | 44.7 | 0.128 | 37.2 | -0.024 |  |
| 5 | sess_amd | Time (sessions) | 360 | 43.9 | 0.12 | 42.5 | 0.079 |  |
| 6 | orb | Time (sessions) | 104 | 44.2 | 0.106 | 51.0 | 0.274 |  |
| 7 | macd_div | Momentum / divergence | 1037 | 39.6 | 0.066 | 37.1 | 0.003 |  |
| 8 | zombie | Liquidity | 628 | 40.6 | 0.059 | 36.6 | -0.026 |  |
| 9 | wavec | Elliott wave | 93 | 39.8 | 0.058 | 46.2 | 0.196 |  |
| 10 | rsi_div | Momentum / divergence | 864 | 39.0 | 0.057 | 35.4 | -0.046 |  |
| 11 | m2022 | SMC / ICT | 488 | 38.9 | 0.039 | 44.3 | 0.166 |  |
| 12 | breakout | Levels / breakouts | 769 | 40.4 | 0.038 | 38.0 | -0.007 |  |
| 13 | liqline | Liquidity | 1872 | 39.5 | 0.037 | 37.9 | -0.004 |  |
| 14 | ohl_break | Levels / breakouts | 572 | 39.3 | 0.024 | 38.5 | 0.029 |  |
| 15 | ma_cross | Trend (MA) | 2068 | 38.3 | 0.022 | 38.4 | 0.014 |  |
| 16 | ohl_open | Levels / breakouts | 2325 | 38.8 | 0.019 | 38.8 | 0.018 |  |
| 17 | vwap | Trend (MA) | 5383 | 38.6 | 0.016 | 39.0 | 0.028 |  |
| 18 | sweep | Liquidity | 2789 | 37.9 | 0.008 | 37.9 | -0.004 |  |
| 19 | crt | Liquidity | 662 | 36.7 | 0.008 | 38.8 | 0.035 |  |
| 20 | cisd | SMC / ICT | 709 | 38.2 | 0.006 | 36.7 | -0.022 |  |
| 21 | level | Levels / breakouts | 3285 | 38.8 | 0.003 | 38.3 | -0.004 |  |
| 22 | judas | Time (sessions) | 1704 | 39.1 | -0.001 | 37.1 | -0.05 |  |
| 23 | tlbreak | Levels / breakouts | 1722 | 37.7 | -0.012 | 37.0 | -0.018 |  |
| 24 | ote | Fibonacci | 612 | 37.4 | -0.016 | 35.5 | -0.064 |  |
| 25 | fib | Fibonacci | 1740 | 37.3 | -0.019 | 35.8 | -0.056 |  |
| 26 | ema_stack | Trend (MA) | 3457 | 36.7 | -0.03 | 37.7 | -0.002 |  |
| 27 | donch | Trend (hedge fund) | 2048 | 36.8 | -0.035 | 39.0 | 0.03 |  |
| 28 | fvg | SMC / ICT | 1995 | 36.0 | -0.043 | 38.8 | 0.027 |  |
| 29 | ob | SMC / ICT | 993 | 35.9 | -0.048 | 36.0 | -0.049 |  |
| 30 | msb_ob | SMC / ICT | 1363 | 36.0 | -0.053 | 38.1 | -0.009 |  |
| 31 | ew5 | Elliott wave | 126 | 34.1 | -0.07 | 27.8 | -0.244 |  |
| 32 | ew3 | Elliott wave | 762 | 34.1 | -0.106 | 36.9 | -0.031 |  |
| 33 | unicorn | SMC / ICT | 358 | 29.6 | -0.204 | 36.3 | -0.037 |  |
| 34 | breaker | SMC / ICT | 262 | 28.2 | -0.219 | 39.3 | 0.049 |  |
| 35 | kzs | Time (sessions) | 25 | 32.0 | -0.134 | 44.0 | 0.166 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Momentum / divergence | 1901 | 0.062 |
| 2 | Time (sessions) | 2287 | 0.027 |
| 3 | Liquidity | 5951 | 0.023 |
| 4 | Levels / breakouts | 8673 | 0.009 |
| 5 | Trend (MA) | 10908 | 0.003 |
| 6 | Trend (hedge fund) | 2212 | -0.007 |
| 7 | Fibonacci | 2352 | -0.018 |
| 8 | SMC / ICT | 6168 | -0.051 |
| 9 | Elliott wave | 1085 | -0.062 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 15m | 47 | 46.8 | 0.372 |
| breaker | 4h | 52 | 36.5 | 0.018 |
| breakout | 1d | 81 | 54.3 | 0.435 |
| cisd | 1d | 67 | 37.3 | 0.132 |
| crt | 15m | 265 | 42.6 | 0.083 |
| donch | 1d | 218 | 36.7 | 0.103 |
| ema_stack | 1d | 382 | 35.1 | 0.067 |
| ew3 | 15m | 184 | 39.7 | 0.031 |
| ew5 | 15m | 36 | 44.4 | 0.184 |
| fib | 1m | 302 | 42.1 | 0.068 |
| fvg | 4h | 381 | 39.9 | 0.066 |
| judas | 15m | 603 | 40.5 | 0.038 |
| level | 1d | 97 | 37.1 | 0.048 |
| liqline | 1d | 174 | 46.6 | 0.407 |
| m2022 | 1d | 111 | 44.1 | 0.256 |
| ma_cross | 1d | 197 | 36.0 | 0.143 |
| macd_div | 1d | 118 | 42.4 | 0.279 |
| msb_ob | 15m | 343 | 42.3 | 0.077 |
| ob | 1m | 143 | 42.0 | 0.107 |
| ohl_break | 1d | 79 | 49.4 | 0.348 |
| ohl_open | 1d | 215 | 40.5 | 0.2 |
| orb | 15m | 97 | 43.3 | 0.082 |
| ote | 1m | 108 | 45.4 | 0.134 |
| po3 | 15m | 48 | 47.9 | 0.219 |
| rsi_div | 15m | 224 | 44.2 | 0.194 |
| sess_amd | 15m | 162 | 46.9 | 0.194 |
| sma1040 | 1d | 87 | 44.8 | 0.3 |
| sweep | 1m | 371 | 42.6 | 0.089 |
| tlbreak | 1d | 212 | 42.0 | 0.206 |
| turtle55 | 1d | 77 | 45.5 | 0.387 |
| unicorn | 4h | 78 | 34.6 | -0.052 |
| vwap | 1m | 1048 | 42.9 | 0.101 |
| zombie | 1d | 62 | 50.0 | 0.416 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 51 | 0.002 | 53 | 0.32 |
| breaker | 125 | -0.348 | 137 | -0.102 |
| breakout | 391 | 0.011 | 378 | 0.065 |
| cisd | 365 | -0.113 | 344 | 0.132 |
| crt | 339 | -0.099 | 323 | 0.12 |
| donch | 883 | -0.106 | 1165 | 0.019 |
| ema_stack | 1568 | -0.102 | 1889 | 0.029 |
| ew3 | 366 | -0.21 | 396 | -0.009 |
| ew5 | 61 | -0.341 | 65 | 0.184 |
| fib | 823 | -0.089 | 917 | 0.044 |
| fvg | 944 | -0.129 | 1051 | 0.034 |
| judas | 720 | -0.113 | 984 | 0.081 |
| kzs | 16 | 0.197 | 9 | -0.722 |
| level | 2099 | -0.029 | 1186 | 0.061 |
| liqline | 900 | -0.024 | 972 | 0.093 |
| m2022 | 247 | -0.034 | 241 | 0.113 |
| ma_cross | 1026 | -0.028 | 1042 | 0.07 |
| macd_div | 539 | 0.04 | 498 | 0.093 |
| msb_ob | 716 | -0.165 | 647 | 0.07 |
| ob | 480 | -0.154 | 513 | 0.052 |
| ohl_break | 262 | -0.075 | 310 | 0.108 |
| ohl_open | 1174 | -0.01 | 1151 | 0.048 |
| orb | 52 | -0.231 | 52 | 0.442 |
| ote | 303 | -0.11 | 309 | 0.076 |
| po3 | 48 | 0.167 | 46 | 0.087 |
| rsi_div | 459 | 0.017 | 405 | 0.101 |
| sess_amd | 125 | 0.1 | 235 | 0.13 |
| sma1040 | 38 | 0.136 | 49 | 0.427 |
| sweep | 1453 | -0.05 | 1336 | 0.071 |
| tlbreak | 854 | -0.133 | 868 | 0.108 |
| turtle55 | 49 | 0.214 | 28 | 0.689 |
| unicorn | 168 | -0.329 | 190 | -0.093 |
| vwap | 2500 | -0.057 | 2883 | 0.08 |
| wavec | 35 | 0.071 | 58 | 0.05 |
| zombie | 277 | -0.026 | 351 | 0.125 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 24652 | 38.2 | 0.003 | 16797 | 37.5 | -0.008 |
| abc | 27 | 44.4 | 0.211 | 77 | 41.6 | 0.147 |
| breaker | 126 | 28.6 | -0.217 | 136 | 27.9 | -0.222 |
| breakout | 551 | 40.7 | 0.045 | 216 | 39.8 | 0.018 |
| cisd | 260 | 41.5 | 0.082 | 448 | 36.2 | -0.042 |
| crt | 261 | 36.4 | -0.019 | 401 | 36.9 | 0.025 |
| donch | 1816 | 37.5 | -0.017 | 229 | 30.6 | -0.195 |
| ema_stack | 2841 | 36.7 | -0.031 | 605 | 36.7 | -0.03 |
| ew3 | 472 | 36.0 | -0.054 | 290 | 31.0 | -0.189 |
| ew5 | 100 | 35.0 | -0.047 | 26 | 30.8 | -0.162 |
| fib | 875 | 35.5 | -0.067 | 862 | 39.1 | 0.03 |
| fvg | 1191 | 37.0 | -0.015 | 800 | 34.4 | -0.09 |
| judas | 1078 | 40.6 | 0.035 | 619 | 36.2 | -0.072 |
| kzs | 5 | 0.0 | -1.0 | 20 | 40.0 | 0.082 |
| level | 1593 | 39.7 | 0.03 | 1683 | 37.7 | -0.025 |
| liqline | 1099 | 39.8 | 0.038 | 770 | 39.2 | 0.038 |
| m2022 | 270 | 38.5 | 0.027 | 216 | 39.4 | 0.051 |
| ma_cross | 1221 | 38.9 | 0.04 | 842 | 37.5 | -0.005 |
| macd_div | 207 | 42.0 | 0.12 | 828 | 39.1 | 0.055 |
| msb_ob | 692 | 34.2 | -0.087 | 670 | 37.6 | -0.021 |
| ob | 550 | 38.2 | 0.012 | 439 | 33.0 | -0.12 |
| ohl_break | 357 | 38.7 | 0.011 | 215 | 40.5 | 0.046 |
| ohl_open | 1242 | 40.9 | 0.053 | 1073 | 36.2 | -0.023 |
| orb | 60 | 41.7 | 0.042 | 44 | 47.7 | 0.193 |
| ote | 273 | 33.3 | -0.106 | 338 | 40.5 | 0.053 |
| po3 | 44 | 40.9 | 0.023 | 50 | 48.0 | 0.221 |
| rsi_div | 184 | 44.6 | 0.205 | 678 | 37.6 | 0.019 |
| sess_amd | 199 | 42.2 | 0.07 | 161 | 46.0 | 0.181 |
| sma1040 | 39 | 46.2 | 0.188 | 48 | 43.8 | 0.39 |
| sweep | 1261 | 37.7 | 0.001 | 1526 | 38.0 | 0.014 |
| tlbreak | 816 | 36.0 | -0.054 | 906 | 39.3 | 0.027 |
| turtle55 | 59 | 49.2 | 0.488 | 18 | 33.3 | 0.054 |
| unicorn | 173 | 30.1 | -0.21 | 185 | 29.2 | -0.198 |
| vwap | 4356 | 38.6 | 0.015 | 1012 | 38.0 | 0.007 |
| wavec | 28 | 39.3 | 0.193 | 65 | 40.0 | 0.0 |
| zombie | 326 | 39.6 | 0.025 | 301 | 41.5 | 0.09 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 4930 | 33.3 | -0.053 |
| Mon | 5551 | 38.8 | -0.002 |
| Sat | 4312 | 34.9 | -0.073 |
| Sun | 12314 | 38.8 | 0.003 |
| Thu | 4637 | 38.8 | 0.033 |
| Tue | 4998 | 37.0 | -0.026 |
| Wed | 4795 | 42.3 | 0.103 |
| Asia 00-07 | 8511 | 37.2 | -0.039 |
| Late 20-24 | 8009 | 39.4 | 0.033 |
| London 07-12 | 6799 | 39.3 | -0.003 |
| New York 12-20 | 14086 | 37.6 | -0.018 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 41537 | 37.9 | -0.001 | 0.003 | -0.47 | 17736 | 0.016 | 23801 | -0.013 |  |
| grade A+++ | 332 | 40.7 | 0.08 | -0.053 | +1.44 | 125 | -0.16 | 207 | 0.225 |  |
| grade A+ | 6181 | 39.9 | 0.06 | 0.042 | +0.94 | 2916 | 0.023 | 3265 | 0.093 |  |
| grade A | 14111 | 37.3 | -0.006 | -0.002 | -0.30 | 6219 | 0.031 | 7892 | -0.035 |  |
| grade B | 13763 | 37.7 | -0.004 | -0.009 | +0.33 | 5609 | -0.018 | 8154 | 0.005 |  |
| grade C | 7150 | 37.8 | -0.038 | 0.005 | -2.29 | 2867 | 0.051 | 4283 | -0.098 |  |
| layer htf | 24652 | 38.2 | 0.003 | 0.006 | -0.27 | 10560 | -0.008 | 14092 | 0.011 |  |
| layer loc | 8447 | 39.5 | 0.047 | 0.006 | +2.44 | 3553 | 0.039 | 4894 | 0.052 |  |
| layer vol | 13560 | 39.2 | 0.023 | 0.003 | +1.56 | 5729 | 0.041 | 7831 | 0.01 |  |
| layer reg | 30623 | 37.4 | 0.003 | -0.021 | +2.64 | 13175 | 0.014 | 17448 | -0.006 |  |
| layer time | 25017 | 37.7 | 0.002 | 0.04 | -3.96 | 11511 | 0.015 | 13506 | -0.01 |  |
| no htf | 16885 | 37.6 | -0.006 | -0.001 | -0.42 | 7176 | 0.051 | 9709 | -0.048 |  |
| no loc | 33090 | 37.5 | -0.013 | 0.002 | -1.74 | 14183 | 0.01 | 18907 | -0.03 |  |
| no vol | 27977 | 37.3 | -0.012 | 0.003 | -1.64 | 12007 | 0.004 | 15970 | -0.024 |  |
| no reg | 10914 | 39.4 | -0.009 | 0.07 | -5.22 | 4561 | 0.022 | 6353 | -0.032 |  |
| no time | 16520 | 38.3 | -0.004 | -0.053 | +3.96 | 6225 | 0.018 | 10295 | -0.017 |  |
| grade A+ / turtle55 | 30 | 56.7 | 0.569 | 0.683 | -0.43 | 13 | 0.06 | 17 | 0.957 |  |
| grade C / ohl_break | 32 | 62.5 | 0.562 | -0.297 | +2.98 | 20 | 0.75 | 12 | 0.25 |  |
| grade B / sma1040 | 38 | 50.0 | 0.528 | 0.334 | +0.73 | 15 | 0.69 | 23 | 0.422 |  |
| grade A+ / macd_div | 98 | 50.0 | 0.337 | 0.089 | +1.60 | 43 | 0.4 | 55 | 0.288 |  |
| grade A / turtle55 | 34 | 38.2 | 0.332 | 0.322 | +0.05 | 18 | 0.355 | 16 | 0.306 |  |
| grade B / po3 | 35 | 51.4 | 0.315 | 0.172 | +0.63 | 18 | 0.389 | 17 | 0.237 |  |
| grade C / m2022 | 47 | 48.9 | 0.256 | 0.637 | -1.51 | 24 | 0.583 | 23 | -0.084 |  |
| grade A+ / ohl_open | 268 | 48.5 | 0.25 | 0.04 | +2.31 | 130 | 0.411 | 138 | 0.099 |  |
| grade A / abc | 36 | 41.7 | 0.227 | 0.083 | +0.66 | 23 | 0.434 | 13 | -0.139 |  |
| grade B / sess_amd | 99 | 47.5 | 0.207 | 0.136 | +0.45 | 42 | -0.15 | 57 | 0.47 |  |
| grade A+ / tlbreak | 222 | 45.5 | 0.205 | 0.14 | +0.63 | 105 | 0.144 | 117 | 0.261 |  |
| grade A+ / m2022 | 100 | 46.0 | 0.189 | 0.091 | +0.70 | 47 | -0.007 | 53 | 0.363 |  |
| grade A / rsi_div | 288 | 42.0 | 0.152 | -0.04 | +2.18 | 139 | 0.253 | 149 | 0.058 |  |
| grade C / breakout | 61 | 45.9 | 0.148 | -0.139 | +1.31 | 29 | 0.379 | 32 | -0.062 |  |
| grade A+ / donch | 399 | 42.9 | 0.13 | 0.102 | +0.39 | 185 | 0.03 | 214 | 0.216 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| sweep | vwap | 4943 | 3060 | 61.9 |
| level | vwap | 5409 | 2705 | 50.0 |
| ema_stack | sweep | 2467 | 1879 | 76.2 |
| ema_stack | level | 2521 | 1404 | 55.7 |
| macd_div | vwap | 1597 | 1284 | 80.4 |
| ohl_open | vwap | 2994 | 1282 | 42.8 |
| level | sweep | 2540 | 1098 | 43.2 |
| fvg | vwap | 2922 | 1069 | 36.6 |
| rsi_div | vwap | 1330 | 1065 | 80.1 |
| fib | vwap | 2222 | 1051 | 47.3 |
| msb_ob | vwap | 1962 | 1048 | 53.4 |
| ma_cross | sweep | 1565 | 1030 | 65.8 |
| judas | level | 1811 | 988 | 54.6 |
| tlbreak | vwap | 2016 | 935 | 46.4 |
| ma_cross | vwap | 3126 | 913 | 29.2 |
| level | ma_cross | 1664 | 912 | 54.8 |
| judas | sweep | 1320 | 851 | 64.5 |
| liqline | vwap | 2409 | 839 | 34.8 |
| level | ohl_open | 1609 | 827 | 51.4 |
| ob | vwap | 1560 | 824 | 52.8 |
| fvg | level | 1713 | 788 | 46.0 |
| judas | vwap | 2809 | 734 | 26.1 |
| fvg | sweep | 1167 | 713 | 61.1 |
| fvg | ohl_open | 840 | 701 | 83.5 |
| cisd | vwap | 973 | 697 | 71.6 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 63 | 52.4 | 0.35 |
| 2 families | 525 | 36.4 | -0.024 |
| 2 families (with opposition) | 1327 | 37.8 | 0.009 |
| 3 families | 1013 | 36.8 | -0.007 |
| 3 families (with opposition) | 3527 | 37.3 | -0.02 |
| 4+ families | 507 | 34.9 | -0.056 |
| 4+ families (with opposition) | 2258 | 35.4 | -0.074 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 75.7 | 15397 | 75.2 | 213428 | +1.4 |
| 1m shapes 120/180/240/360 deg | 72.2 | 7186 | 72.8 | 7126 | -1.3 |
| 15m | 57.7 | 10682 | 57.6 | 147782 | +0.3 |
| 15m shapes 120/180/240/360 deg | 58.4 | 5760 | 58.0 | 5795 | +0.5 |
| 1h | 56.2 | 9869 | 56.7 | 136747 | -1.2 |
| 1h shapes 120/180/240/360 deg | 56.7 | 5531 | 56.5 | 5543 | +0.3 |
| 4h | 55.8 | 7755 | 57.0 | 106941 | -2.1 |
| 4h shapes 120/180/240/360 deg | 56.0 | 4415 | 56.4 | 4402 | -0.6 |
| 1d | 57.8 | 4430 | 58.3 | 60755 | -0.6 |
| 1d shapes 120/180/240/360 deg | 59.1 | 2601 | 58.2 | 2607 | +0.9 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 93 | 26.9 | +0.111 | +0.068 | +0.19 |
| 1d | 76 | 47.4 | +0.170 | +0.197 | -0.13 |
| 1h | 66 | 22.7 | +0.124 | +0.434 | -1.03 |
| 4h | 112 | 30.4 | -0.099 | -0.050 | -0.24 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2883 | -0.137 |
| 15 days around full moon | 2812 | 0.149 |

Difference t = -3.15 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

| exit | n | win % | avg R | total R | t |
|---|---|---|---|---|---|
| rr1.0 | 41537 | 49.5 | -0.008 | -347.7 | -1.72 |
| rr1.5 | 41537 | 40.6 | -0.001 | -22.9 | -0.09 |
| rr2.0 | 41537 | 35.3 | 0.008 | 319.6 | +1.15 |
| rr3.0 | 41537 | 29.9 | 0.033 | 1357.9 | +4.06 |
| rr1.5_be | 41537 | 34.0 | -0.004 | -159.2 | -0.70 |
| rr2.0_be | 41537 | 26.8 | 0.004 | 165.0 | +0.67 |
