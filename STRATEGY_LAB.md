# Strategy lab - real candles (2026-10-19)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | turtle55 | Trend (hedge fund) | 55 | 50.9 | 0.465 | 56.4 | 0.554 |  |
| 2 | sma1040 | Trend (hedge fund) | 52 | 50.0 | 0.375 | 40.4 | 0.131 |  |
| 3 | wavec | Elliott wave | 125 | 45.6 | 0.194 | 40.0 | 0.041 |  |
| 4 | ew5 | Elliott wave | 157 | 41.4 | 0.13 | 32.5 | -0.089 |  |
| 5 | abc | Elliott wave | 132 | 41.7 | 0.11 | 48.5 | 0.266 |  |
| 6 | ote | Fibonacci | 784 | 42.5 | 0.107 | 38.5 | 0.014 |  |
| 7 | po3 | Time (sessions) | 129 | 39.5 | 0.041 | 35.7 | -0.074 |  |
| 8 | kzs | Time (sessions) | 39 | 38.5 | 0.033 | 48.7 | 0.257 |  |
| 9 | ohl_open | Levels / breakouts | 3019 | 39.7 | 0.031 | 39.2 | 0.018 |  |
| 10 | sess_amd | Time (sessions) | 475 | 40.4 | 0.026 | 41.9 | 0.07 |  |
| 11 | m2022 | SMC / ICT | 663 | 38.9 | 0.023 | 40.6 | 0.055 |  |
| 12 | level | Levels / breakouts | 5086 | 39.2 | 0.022 | 38.6 | 0.011 |  |
| 13 | rsi_div | Momentum / divergence | 1213 | 37.9 | 0.022 | 35.0 | -0.059 |  |
| 14 | ohl_break | Levels / breakouts | 832 | 38.9 | 0.021 | 41.7 | 0.084 |  |
| 15 | macd_div | Momentum / divergence | 1367 | 38.3 | 0.021 | 34.7 | -0.068 |  |
| 16 | sweep | Liquidity | 3554 | 38.4 | 0.014 | 38.9 | 0.021 |  |
| 17 | liqline | Liquidity | 2672 | 38.2 | 0.005 | 39.5 | 0.034 |  |
| 18 | breakout | Levels / breakouts | 1050 | 38.9 | 0.001 | 40.2 | 0.041 |  |
| 19 | tlbreak | Levels / breakouts | 2143 | 38.3 | 0.001 | 38.8 | 0.019 |  |
| 20 | ma_cross | Trend (MA) | 2862 | 37.5 | -0.008 | 37.0 | -0.02 |  |
| 21 | fvg | SMC / ICT | 3031 | 37.6 | -0.008 | 40.3 | 0.053 |  |
| 22 | msb_ob | SMC / ICT | 1914 | 37.5 | -0.015 | 36.1 | -0.049 |  |
| 23 | vwap | Trend (MA) | 7266 | 37.3 | -0.017 | 39.2 | 0.029 |  |
| 24 | crt | Liquidity | 962 | 37.1 | -0.018 | 38.0 | 0.008 |  |
| 25 | zombie | Liquidity | 893 | 37.3 | -0.02 | 37.0 | -0.017 |  |
| 26 | fib | Fibonacci | 2268 | 37.3 | -0.021 | 37.3 | -0.014 |  |
| 27 | cisd | SMC / ICT | 975 | 36.9 | -0.022 | 37.7 | -0.006 |  |
| 28 | judas | Time (sessions) | 2449 | 37.9 | -0.027 | 40.4 | 0.044 |  |
| 29 | donch | Trend (hedge fund) | 2702 | 37.0 | -0.028 | 39.9 | 0.049 |  |
| 30 | ob | SMC / ICT | 1563 | 35.9 | -0.047 | 38.6 | 0.027 |  |
| 31 | ema_stack | Trend (MA) | 4833 | 36.2 | -0.05 | 39.0 | 0.024 |  |
| 32 | orb | Time (sessions) | 187 | 36.9 | -0.055 | 39.6 | -0.005 |  |
| 33 | ew3 | Elliott wave | 957 | 36.4 | -0.065 | 39.0 | 0.011 |  |
| 34 | breaker | SMC / ICT | 429 | 33.6 | -0.066 | 38.0 | 0.041 |  |
| 35 | unicorn | SMC / ICT | 470 | 32.8 | -0.126 | 39.4 | 0.035 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Momentum / divergence | 2580 | 0.021 |
| 2 | Levels / breakouts | 12130 | 0.019 |
| 3 | Fibonacci | 3052 | 0.012 |
| 4 | Liquidity | 8081 | 0.003 |
| 5 | Elliott wave | 1371 | -0.002 |
| 6 | Trend (hedge fund) | 2809 | -0.011 |
| 7 | Time (sessions) | 3279 | -0.018 |
| 8 | SMC / ICT | 9045 | -0.024 |
| 9 | Trend (MA) | 14961 | -0.026 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 15m | 52 | 51.9 | 0.407 |
| breaker | 1h | 165 | 38.8 | 0.09 |
| breakout | 1d | 52 | 50.0 | 0.357 |
| cisd | 1d | 49 | 36.7 | 0.113 |
| crt | 1m | 80 | 41.2 | 0.074 |
| donch | 1d | 138 | 37.7 | 0.143 |
| ema_stack | 1d | 247 | 34.8 | 0.063 |
| ew3 | 15m | 273 | 38.8 | -0.008 |
| ew5 | 15m | 48 | 58.3 | 0.493 |
| fib | 15m | 618 | 40.9 | 0.048 |
| fvg | 4h | 543 | 40.7 | 0.098 |
| judas | 1m | 708 | 39.3 | -0.007 |
| level | 1m | 1273 | 40.5 | 0.041 |
| liqline | 1d | 115 | 43.5 | 0.359 |
| m2022 | 1d | 71 | 49.3 | 0.374 |
| ma_cross | 1d | 120 | 39.2 | 0.187 |
| macd_div | 1d | 63 | 46.0 | 0.382 |
| msb_ob | 1m | 333 | 42.9 | 0.096 |
| ob | 1m | 258 | 41.5 | 0.088 |
| ohl_break | 1d | 49 | 46.9 | 0.363 |
| ohl_open | 1d | 123 | 39.0 | 0.139 |
| orb | 15m | 181 | 37.0 | -0.052 |
| ote | 1m | 129 | 48.1 | 0.214 |
| po3 | 15m | 66 | 40.9 | 0.069 |
| rsi_div | 15m | 328 | 42.4 | 0.115 |
| sess_amd | 15m | 239 | 45.6 | 0.155 |
| sma1040 | 1d | 52 | 50.0 | 0.375 |
| sweep | 1m | 464 | 44.6 | 0.119 |
| tlbreak | 1d | 126 | 43.7 | 0.193 |
| turtle55 | 1d | 55 | 50.9 | 0.465 |
| unicorn | 1h | 159 | 40.3 | 0.074 |
| vwap | 1m | 1306 | 42.3 | 0.082 |
| wavec | 15m | 42 | 54.8 | 0.369 |
| zombie | 1d | 40 | 55.0 | 0.532 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 77 | 0.085 | 55 | 0.144 |
| breaker | 206 | -0.139 | 223 | 0.001 |
| breakout | 511 | 0.014 | 539 | -0.012 |
| cisd | 490 | -0.064 | 485 | 0.021 |
| crt | 447 | -0.064 | 515 | 0.022 |
| donch | 1322 | -0.014 | 1380 | -0.042 |
| ema_stack | 2447 | -0.065 | 2386 | -0.035 |
| ew3 | 519 | -0.039 | 438 | -0.097 |
| ew5 | 69 | 0.011 | 88 | 0.224 |
| fib | 1071 | -0.032 | 1197 | -0.01 |
| fvg | 1621 | -0.008 | 1410 | -0.008 |
| judas | 1201 | -0.044 | 1248 | -0.01 |
| kzs | 22 | 0.093 | 17 | -0.044 |
| level | 3425 | 0.017 | 1661 | 0.032 |
| liqline | 1280 | 0.052 | 1392 | -0.038 |
| m2022 | 339 | -0.043 | 324 | 0.092 |
| ma_cross | 1450 | 0.023 | 1412 | -0.04 |
| macd_div | 681 | 0.039 | 686 | 0.002 |
| msb_ob | 1023 | -0.001 | 891 | -0.031 |
| ob | 802 | -0.093 | 761 | 0.001 |
| ohl_break | 389 | -0.012 | 443 | 0.05 |
| ohl_open | 1474 | 0.027 | 1545 | 0.034 |
| orb | 100 | -0.259 | 87 | 0.178 |
| ote | 374 | 0.097 | 410 | 0.117 |
| po3 | 69 | 0.205 | 60 | -0.149 |
| rsi_div | 601 | 0.028 | 612 | 0.015 |
| sess_amd | 197 | 0.042 | 278 | 0.014 |
| sma1040 | 25 | 0.514 | 27 | 0.247 |
| sweep | 1909 | 0.017 | 1645 | 0.011 |
| tlbreak | 1045 | -0.046 | 1098 | 0.045 |
| turtle55 | 34 | 0.214 | 21 | 0.87 |
| unicorn | 227 | -0.185 | 243 | -0.07 |
| vwap | 3728 | -0.023 | 3538 | -0.011 |
| wavec | 66 | 0.11 | 59 | 0.289 |
| zombie | 444 | -0.004 | 449 | -0.036 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 34005 | 37.6 | -0.014 | 22870 | 38.2 | 0.004 |
| abc | 30 | 40.0 | 0.0 | 102 | 42.2 | 0.142 |
| breaker | 203 | 36.9 | -0.01 | 221 | 29.9 | -0.13 |
| breakout | 764 | 39.3 | 0.012 | 282 | 37.9 | -0.025 |
| cisd | 373 | 35.9 | -0.063 | 593 | 37.9 | 0.015 |
| crt | 384 | 36.5 | -0.047 | 576 | 37.3 | -0.004 |
| donch | 2364 | 37.0 | -0.027 | 328 | 36.3 | -0.044 |
| ema_stack | 3894 | 36.6 | -0.038 | 907 | 34.7 | -0.088 |
| ew3 | 611 | 38.1 | -0.022 | 337 | 33.2 | -0.142 |
| ew5 | 126 | 43.7 | 0.196 | 31 | 32.3 | -0.138 |
| fib | 1152 | 37.2 | -0.016 | 1105 | 37.3 | -0.028 |
| fvg | 1759 | 36.6 | -0.025 | 1241 | 38.6 | 0.001 |
| judas | 1544 | 38.5 | -0.01 | 881 | 36.9 | -0.054 |
| kzs | 14 | 28.6 | -0.197 | 25 | 44.0 | 0.162 |
| level | 2622 | 38.5 | 0.004 | 2415 | 40.0 | 0.042 |
| liqline | 1544 | 38.3 | 0.002 | 1102 | 38.2 | 0.016 |
| m2022 | 358 | 39.9 | 0.04 | 298 | 37.6 | 0.001 |
| ma_cross | 1702 | 36.5 | -0.028 | 1131 | 38.7 | 0.021 |
| macd_div | 259 | 41.3 | 0.103 | 1098 | 37.7 | 0.006 |
| msb_ob | 1008 | 35.7 | -0.059 | 889 | 38.9 | 0.023 |
| ob | 886 | 35.3 | -0.068 | 658 | 35.4 | -0.049 |
| ohl_break | 503 | 40.0 | 0.037 | 321 | 37.4 | -0.002 |
| ohl_open | 1653 | 39.6 | 0.026 | 1346 | 39.7 | 0.035 |
| orb | 110 | 36.4 | -0.083 | 75 | 37.3 | -0.023 |
| ote | 355 | 39.7 | 0.048 | 424 | 44.6 | 0.149 |
| po3 | 67 | 32.8 | -0.163 | 60 | 48.3 | 0.303 |
| rsi_div | 288 | 38.9 | 0.095 | 917 | 37.6 | -0.001 |
| sess_amd | 250 | 41.2 | 0.037 | 221 | 39.8 | 0.02 |
| sma1040 | 24 | 41.7 | 0.1 | 28 | 57.1 | 0.611 |
| sweep | 1572 | 37.3 | -0.012 | 1965 | 39.4 | 0.038 |
| tlbreak | 1064 | 38.0 | -0.014 | 1071 | 38.7 | 0.02 |
| turtle55 | 42 | 50.0 | 0.455 | 13 | 53.8 | 0.496 |
| unicorn | 230 | 32.6 | -0.124 | 236 | 32.6 | -0.134 |
| vwap | 5727 | 37.4 | -0.014 | 1485 | 37.0 | -0.031 |
| wavec | 27 | 37.0 | 0.109 | 97 | 47.4 | 0.205 |
| zombie | 496 | 37.3 | -0.024 | 391 | 37.6 | -0.006 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 6723 | 32.5 | -0.043 |
| Mon | 8843 | 39.3 | 0.005 |
| Sat | 5813 | 34.9 | -0.067 |
| Sun | 15510 | 39.0 | 0.003 |
| Thu | 6767 | 37.4 | -0.007 |
| Tue | 6992 | 40.3 | 0.031 |
| Wed | 6660 | 38.9 | 0.01 |
| Asia 00-07 | 14324 | 38.7 | 0.003 |
| Late 20-24 | 11702 | 38.5 | 0.015 |
| London 07-12 | 8285 | 37.5 | -0.05 |
| New York 12-20 | 20416 | 37.3 | -0.017 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 57308 | 37.8 | -0.006 | 0.018 | -3.67 | 24815 | -0.016 | 32493 | 0.001 |  |
| grade A+++ | 493 | 40.8 | 0.085 | 0.081 | +0.06 | 233 | 0.031 | 260 | 0.134 |  |
| grade A+ | 8286 | 37.0 | -0.016 | -0.001 | -0.83 | 3743 | -0.012 | 4543 | -0.019 |  |
| grade A | 17627 | 37.6 | -0.006 | 0.024 | -2.49 | 8163 | -0.016 | 9464 | 0.003 |  |
| grade B | 19775 | 38.2 | 0.004 | 0.02 | -1.43 | 8174 | -0.015 | 11601 | 0.017 |  |
| grade C | 11127 | 38.2 | -0.022 | 0.017 | -2.57 | 4502 | -0.024 | 6625 | -0.021 |  |
| layer htf | 34005 | 37.6 | -0.014 | 0.023 | -4.20 | 14703 | -0.028 | 19302 | -0.002 |  |
| layer loc | 12223 | 39.6 | 0.044 | 0.016 | +2.06 | 5229 | 0.062 | 6994 | 0.031 |  |
| layer vol | 18694 | 39.2 | 0.023 | 0.053 | -2.57 | 8082 | 0.015 | 10612 | 0.03 |  |
| layer reg | 41292 | 36.9 | -0.014 | 0.004 | -2.38 | 17773 | -0.028 | 23519 | -0.004 |  |
| layer time | 31282 | 37.2 | -0.018 | 0.009 | -3.08 | 14957 | -0.027 | 16325 | -0.011 |  |
| no htf | 23303 | 38.2 | 0.004 | 0.011 | -0.61 | 10112 | 0.002 | 13191 | 0.006 |  |
| no loc | 45085 | 37.3 | -0.02 | 0.018 | -5.14 | 19586 | -0.037 | 25499 | -0.007 |  |
| no vol | 38614 | 37.2 | -0.02 | 0.001 | -2.68 | 16733 | -0.031 | 21881 | -0.013 |  |
| no reg | 16016 | 40.2 | 0.015 | 0.054 | -3.09 | 7042 | 0.016 | 8974 | 0.014 |  |
| no time | 26026 | 38.6 | 0.008 | 0.029 | -2.07 | 9858 | 0.001 | 16168 | 0.013 |  |
| grade B / sess_amd | 114 | 53.5 | 0.358 | 0.129 | +1.51 | 43 | 0.13 | 71 | 0.495 |  |
| grade A / ew5 | 55 | 49.1 | 0.259 | -0.029 | +1.38 | 21 | -0.048 | 34 | 0.449 |  |
| grade A / abc | 38 | 47.4 | 0.246 | 0.18 | +0.30 | 22 | 0.357 | 16 | 0.094 |  |
| grade A+++ / msb_ob | 41 | 46.3 | 0.236 | -0.275 | +2.28 | 23 | 0.248 | 18 | 0.221 |  |
| grade C / wavec | 37 | 48.6 | 0.216 | -0.122 | +1.30 | 16 | -0.219 | 21 | 0.548 |  |
| grade B / wavec | 47 | 46.8 | 0.21 | -0.07 | +1.46 | 26 | 0.472 | 21 | -0.114 |  |
| grade C / ote | 130 | 46.9 | 0.186 | -0.056 | +1.71 | 45 | 0.167 | 85 | 0.196 |  |
| grade A+ / m2022 | 129 | 45.7 | 0.184 | 0.139 | +0.31 | 55 | 0.095 | 74 | 0.251 |  |
| grade A+++ / sweep | 70 | 42.9 | 0.171 | 0.034 | +0.68 | 31 | 0.106 | 39 | 0.223 |  |
| grade A / ote | 266 | 42.9 | 0.137 | 0.002 | +1.39 | 123 | 0.136 | 143 | 0.138 |  |
| grade B / orb | 43 | 44.2 | 0.13 | -0.186 | +1.25 | 23 | 0.135 | 20 | 0.125 |  |
| grade C / crt | 151 | 43.0 | 0.127 | 0.087 | +0.31 | 53 | -0.009 | 98 | 0.2 |  |
| grade A / rsi_div | 380 | 40.0 | 0.113 | -0.191 | +4.18 | 196 | 0.191 | 184 | 0.03 | YES |
| grade A / macd_div | 385 | 40.5 | 0.108 | -0.09 | +2.57 | 195 | 0.146 | 190 | 0.07 |  |
| grade A / m2022 | 243 | 41.6 | 0.098 | 0.139 | -0.41 | 118 | -0.045 | 125 | 0.233 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8558 | 3966 | 46.3 |
| sweep | vwap | 6280 | 3813 | 60.7 |
| ema_stack | sweep | 3213 | 2389 | 74.4 |
| ema_stack | level | 4202 | 2045 | 48.7 |
| fvg | vwap | 4422 | 1766 | 39.9 |
| macd_div | vwap | 2072 | 1641 | 79.2 |
| ohl_open | vwap | 3903 | 1631 | 41.8 |
| level | sweep | 3665 | 1598 | 43.6 |
| msb_ob | vwap | 2807 | 1554 | 55.4 |
| fib | vwap | 2914 | 1455 | 49.9 |
| rsi_div | vwap | 1841 | 1427 | 77.5 |
| fvg | level | 3269 | 1415 | 43.3 |
| ob | vwap | 2497 | 1353 | 54.2 |
| judas | level | 2768 | 1334 | 48.2 |
| level | ma_cross | 2676 | 1332 | 49.8 |
| ma_cross | sweep | 2052 | 1306 | 63.6 |
| liqline | vwap | 3550 | 1257 | 35.4 |
| level | ohl_open | 2409 | 1231 | 51.1 |
| ma_cross | vwap | 4256 | 1212 | 28.5 |
| tlbreak | vwap | 2523 | 1210 | 48.0 |
| judas | vwap | 3977 | 1083 | 27.2 |
| judas | sweep | 1749 | 1063 | 60.8 |
| level | liqline | 1958 | 1024 | 52.3 |
| liqline | sweep | 1798 | 941 | 52.3 |
| cisd | vwap | 1313 | 931 | 70.9 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 57 | 56.1 | 0.451 |
| 2 families | 612 | 34.8 | -0.047 |
| 2 families (with opposition) | 1784 | 37.8 | 0.003 |
| 3 families | 1507 | 39.7 | 0.058 |
| 3 families (with opposition) | 4884 | 37.2 | -0.023 |
| 4+ families | 748 | 36.1 | -0.051 |
| 4+ families (with opposition) | 3084 | 37.6 | -0.022 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 86.0 | 36828 | 85.8 | 509446 | +1.0 |
| 1m shapes 120/180/240/360 deg | 81.6 | 16047 | 81.8 | 15984 | -0.6 |
| 15m | 65.2 | 20857 | 64.8 | 288453 | +1.2 |
| 15m shapes 120/180/240/360 deg | 63.3 | 10790 | 62.7 | 10757 | +1.3 |
| 1h | 60.0 | 16723 | 59.5 | 232163 | +1.3 |
| 1h shapes 120/180/240/360 deg | 59.0 | 9090 | 58.8 | 9171 | +0.4 |
| 4h | 57.1 | 11841 | 57.9 | 163350 | -1.8 |
| 4h shapes 120/180/240/360 deg | 57.1 | 6685 | 57.4 | 6689 | -0.6 |
| 1d | 55.7 | 2740 | 56.0 | 37091 | -0.4 |
| 1d shapes 120/180/240/360 deg | 57.2 | 1714 | 57.3 | 1715 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 77 | 22.1 | +0.024 | +0.273 | -1.16 |
| 1d | 55 | 43.6 | +0.124 | +0.090 | +0.14 |
| 1h | 93 | 23.7 | -0.056 | -0.038 | -0.06 |
| 4h | 109 | 33.9 | +0.088 | +0.118 | -0.19 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2014 | -0.094 |
| 15 days around full moon | 1955 | 0.088 |

Difference t = -2.16 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

| exit | n | win % | avg R | total R | t |
|---|---|---|---|---|---|
| rr1.0 | 57308 | 48.6 | -0.026 | -1496.9 | -6.31 |
| rr1.5 | 57308 | 40.3 | -0.006 | -355.4 | -1.24 |
| rr2.0 | 57308 | 35.2 | 0.013 | 736.0 | +2.24 |
| rr3.0 | 57308 | 29.6 | 0.033 | 1906.2 | +4.83 |
| rr1.5_be | 57308 | 34.0 | -0.011 | -622.9 | -2.33 |
| rr2.0_be | 57308 | 27.2 | 0.006 | 323.0 | +1.10 |
