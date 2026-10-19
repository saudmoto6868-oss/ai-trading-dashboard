# Strategy lab - real candles (2026-10-18)

Symbols: BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, BNB-USDT, DOGE-USDT, HL:xyz:GOLD, HL:xyz:SP500 · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | turtle55 | Trend (hedge fund) | 77 | 45.5 | 0.387 | 53.2 | 0.532 |  |
| 2 | sma1040 | Trend (hedge fund) | 87 | 44.8 | 0.305 | 44.8 | 0.294 |  |
| 3 | abc | Elliott wave | 106 | 42.5 | 0.131 | 42.5 | 0.107 |  |
| 4 | wavec | Elliott wave | 96 | 42.7 | 0.129 | 37.5 | -0.0 |  |
| 5 | orb | Time (sessions) | 121 | 42.1 | 0.107 | 47.1 | 0.186 |  |
| 6 | zombie | Liquidity | 606 | 41.7 | 0.098 | 40.4 | 0.048 |  |
| 7 | ohl_break | Levels / breakouts | 477 | 41.9 | 0.085 | 40.7 | 0.064 |  |
| 8 | rsi_div | Momentum / divergence | 832 | 40.4 | 0.083 | 38.9 | 0.044 |  |
| 9 | macd_div | Momentum / divergence | 1015 | 40.4 | 0.076 | 40.4 | 0.081 |  |
| 10 | liqline | Liquidity | 1804 | 40.0 | 0.053 | 39.0 | 0.024 |  |
| 11 | ma_cross | Trend (MA) | 2059 | 39.3 | 0.048 | 38.3 | 0.007 |  |
| 12 | m2022 | SMC / ICT | 501 | 39.1 | 0.038 | 41.1 | 0.076 |  |
| 13 | breakout | Levels / breakouts | 745 | 39.5 | 0.035 | 39.2 | 0.032 |  |
| 14 | po3 | Time (sessions) | 99 | 40.4 | 0.029 | 20.2 | -0.428 | YES |
| 15 | cisd | SMC / ICT | 722 | 38.4 | 0.017 | 36.8 | -0.031 |  |
| 16 | sweep | Liquidity | 2780 | 38.4 | 0.016 | 38.2 | 0.007 |  |
| 17 | judas | Time (sessions) | 1633 | 39.7 | 0.013 | 39.7 | 0.016 |  |
| 18 | tlbreak | Levels / breakouts | 1694 | 38.1 | 0.006 | 38.7 | 0.015 |  |
| 19 | sess_amd | Time (sessions) | 443 | 39.5 | 0.006 | 39.7 | 0.02 |  |
| 20 | vwap | Trend (MA) | 5383 | 38.1 | 0.005 | 37.9 | 0.002 |  |
| 21 | ote | Fibonacci | 586 | 37.4 | 0.002 | 38.4 | 0.02 |  |
| 22 | crt | Liquidity | 672 | 37.2 | 0.001 | 35.4 | -0.06 |  |
| 23 | fib | Fibonacci | 1775 | 37.2 | -0.012 | 38.6 | 0.019 |  |
| 24 | level | Levels / breakouts | 3242 | 38.1 | -0.013 | 38.2 | -0.003 |  |
| 25 | ohl_open | Levels / breakouts | 2413 | 37.4 | -0.015 | 38.3 | 0.009 |  |
| 26 | msb_ob | SMC / ICT | 1380 | 36.9 | -0.019 | 38.8 | 0.019 |  |
| 27 | ema_stack | Trend (MA) | 3420 | 37.1 | -0.02 | 39.6 | 0.049 |  |
| 28 | breaker | SMC / ICT | 281 | 35.9 | -0.024 | 35.6 | -0.047 |  |
| 29 | donch | Trend (hedge fund) | 2004 | 36.9 | -0.025 | 40.1 | 0.058 |  |
| 30 | ew5 | Elliott wave | 128 | 36.7 | -0.027 | 27.3 | -0.258 |  |
| 31 | fvg | SMC / ICT | 1960 | 36.8 | -0.03 | 39.0 | 0.027 |  |
| 32 | ob | SMC / ICT | 985 | 36.4 | -0.03 | 38.4 | 0.007 |  |
| 33 | ew3 | Elliott wave | 754 | 33.8 | -0.113 | 38.7 | 0.018 |  |
| 34 | unicorn | SMC / ICT | 339 | 33.0 | -0.117 | 33.3 | -0.115 |  |
| 35 | kzs | Time (sessions) | 25 | 52.0 | 0.3 | 32.0 | -0.2 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Momentum / divergence | 1847 | 0.079 |
| 2 | Liquidity | 5862 | 0.034 |
| 3 | Time (sessions) | 2321 | 0.02 |
| 4 | Trend (MA) | 10862 | 0.005 |
| 5 | Trend (hedge fund) | 2168 | 0.003 |
| 6 | Levels / breakouts | 8571 | -0.0 |
| 7 | Fibonacci | 2361 | -0.009 |
| 8 | SMC / ICT | 6168 | -0.021 |
| 9 | Elliott wave | 1084 | -0.058 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 15m | 44 | 54.5 | 0.419 |
| breaker | 1m | 32 | 53.1 | 0.328 |
| breakout | 1d | 81 | 54.3 | 0.435 |
| cisd | 1d | 67 | 37.3 | 0.135 |
| crt | 4h | 130 | 41.5 | 0.126 |
| donch | 1d | 218 | 36.7 | 0.102 |
| ema_stack | 1d | 382 | 35.1 | 0.067 |
| ew3 | 1m | 147 | 36.7 | -0.046 |
| ew5 | 15m | 31 | 58.1 | 0.482 |
| fib | 1d | 190 | 33.2 | 0.023 |
| fvg | 4h | 344 | 41.6 | 0.091 |
| judas | 1h | 387 | 42.9 | 0.088 |
| level | 1d | 97 | 37.1 | 0.047 |
| liqline | 1d | 174 | 46.6 | 0.408 |
| m2022 | 1d | 111 | 44.1 | 0.257 |
| ma_cross | 1d | 197 | 36.0 | 0.144 |
| macd_div | 1d | 118 | 42.4 | 0.28 |
| msb_ob | 1m | 239 | 47.7 | 0.209 |
| ob | 1m | 144 | 52.8 | 0.373 |
| ohl_break | 1d | 79 | 49.4 | 0.348 |
| ohl_open | 1d | 215 | 40.5 | 0.2 |
| orb | 15m | 110 | 43.6 | 0.14 |
| ote | 1m | 101 | 50.5 | 0.262 |
| po3 | 1h | 47 | 40.4 | 0.037 |
| rsi_div | 1m | 153 | 43.1 | 0.138 |
| sess_amd | 15m | 166 | 43.4 | 0.117 |
| sma1040 | 1d | 87 | 44.8 | 0.305 |
| sweep | 1m | 362 | 46.7 | 0.186 |
| tlbreak | 1d | 212 | 42.0 | 0.207 |
| turtle55 | 1d | 77 | 45.5 | 0.387 |
| unicorn | 1h | 111 | 36.9 | 0.002 |
| vwap | 15m | 1352 | 40.9 | 0.049 |
| zombie | 1d | 62 | 50.0 | 0.416 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 54 | 0.035 | 52 | 0.232 |
| breaker | 135 | -0.188 | 146 | 0.127 |
| breakout | 370 | -0.017 | 375 | 0.086 |
| cisd | 367 | -0.066 | 355 | 0.103 |
| crt | 337 | -0.094 | 335 | 0.097 |
| donch | 855 | -0.09 | 1149 | 0.023 |
| ema_stack | 1565 | -0.106 | 1855 | 0.053 |
| ew3 | 376 | -0.25 | 378 | 0.024 |
| ew5 | 57 | -0.36 | 71 | 0.24 |
| fib | 820 | -0.107 | 955 | 0.07 |
| fvg | 922 | -0.173 | 1038 | 0.098 |
| judas | 635 | -0.135 | 998 | 0.108 |
| kzs | 19 | 0.579 | 6 | -0.583 |
| level | 2092 | -0.056 | 1150 | 0.066 |
| liqline | 874 | -0.009 | 930 | 0.112 |
| m2022 | 244 | -0.023 | 257 | 0.096 |
| ma_cross | 1046 | 0.001 | 1013 | 0.096 |
| macd_div | 533 | 0.082 | 482 | 0.069 |
| msb_ob | 710 | -0.124 | 670 | 0.091 |
| ob | 476 | -0.123 | 509 | 0.056 |
| ohl_break | 234 | 0.012 | 243 | 0.155 |
| ohl_open | 1218 | -0.026 | 1195 | -0.003 |
| orb | 68 | -0.148 | 53 | 0.434 |
| ote | 263 | -0.038 | 323 | 0.034 |
| po3 | 47 | 0.024 | 52 | 0.033 |
| rsi_div | 440 | 0.012 | 392 | 0.162 |
| sess_amd | 213 | -0.061 | 230 | 0.068 |
| sma1040 | 38 | 0.136 | 49 | 0.436 |
| sweep | 1472 | -0.056 | 1308 | 0.097 |
| tlbreak | 859 | -0.102 | 835 | 0.117 |
| turtle55 | 49 | 0.214 | 28 | 0.689 |
| unicorn | 150 | -0.334 | 189 | 0.055 |
| vwap | 2464 | -0.067 | 2919 | 0.065 |
| wavec | 39 | 0.026 | 57 | 0.2 |
| zombie | 286 | -0.015 | 320 | 0.199 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 24309 | 38.3 | 0.009 | 16792 | 37.8 | 0.001 |
| abc | 31 | 41.9 | 0.131 | 73 | 41.1 | 0.094 |
| breaker | 124 | 37.9 | 0.04 | 156 | 34.6 | -0.069 |
| breakout | 497 | 41.6 | 0.077 | 246 | 35.0 | -0.053 |
| cisd | 275 | 40.4 | 0.06 | 445 | 37.3 | -0.004 |
| crt | 257 | 36.6 | -0.023 | 414 | 37.7 | 0.019 |
| donch | 1771 | 37.4 | -0.01 | 229 | 33.2 | -0.137 |
| ema_stack | 2804 | 37.2 | -0.017 | 606 | 36.6 | -0.033 |
| ew3 | 471 | 34.4 | -0.083 | 280 | 32.5 | -0.171 |
| ew5 | 99 | 38.4 | 0.025 | 29 | 31.0 | -0.203 |
| fib | 855 | 35.6 | -0.056 | 912 | 39.0 | 0.036 |
| fvg | 1168 | 37.2 | -0.022 | 779 | 36.1 | -0.048 |
| judas | 1026 | 40.7 | 0.045 | 593 | 38.4 | -0.025 |
| kzs | 3 | 33.3 | -0.167 | 22 | 54.5 | 0.364 |
| level | 1562 | 38.3 | -0.006 | 1664 | 37.7 | -0.021 |
| liqline | 1033 | 41.1 | 0.071 | 767 | 38.6 | 0.031 |
| m2022 | 266 | 41.7 | 0.106 | 234 | 36.3 | -0.035 |
| ma_cross | 1185 | 39.3 | 0.05 | 869 | 39.1 | 0.042 |
| macd_div | 203 | 39.9 | 0.041 | 811 | 40.6 | 0.086 |
| msb_ob | 712 | 36.9 | -0.004 | 662 | 36.6 | -0.042 |
| ob | 564 | 38.7 | 0.021 | 420 | 33.3 | -0.103 |
| ohl_break | 258 | 44.2 | 0.138 | 219 | 39.3 | 0.022 |
| ohl_open | 1322 | 37.1 | -0.037 | 1076 | 37.5 | 0.005 |
| orb | 63 | 47.6 | 0.206 | 58 | 36.2 | -0.001 |
| ote | 271 | 33.2 | -0.103 | 312 | 41.3 | 0.103 |
| po3 | 53 | 45.3 | 0.155 | 46 | 34.8 | -0.117 |
| rsi_div | 176 | 40.3 | 0.076 | 656 | 40.4 | 0.085 |
| sess_amd | 240 | 39.6 | 0.011 | 203 | 39.4 | 0.0 |
| sma1040 | 39 | 46.2 | 0.188 | 48 | 43.8 | 0.399 |
| sweep | 1235 | 39.4 | 0.041 | 1542 | 37.6 | -0.002 |
| tlbreak | 794 | 38.0 | -0.006 | 894 | 38.4 | 0.021 |
| turtle55 | 59 | 49.2 | 0.488 | 18 | 33.3 | 0.054 |
| unicorn | 168 | 33.9 | -0.094 | 170 | 32.4 | -0.135 |
| vwap | 4382 | 37.9 | 0.001 | 981 | 38.3 | 0.011 |
| wavec | 25 | 40.0 | 0.236 | 70 | 42.9 | 0.071 |
| zombie | 318 | 43.7 | 0.146 | 288 | 39.6 | 0.045 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 4907 | 32.4 | -0.058 |
| Mon | 4971 | 39.3 | 0.003 |
| Sat | 4238 | 37.3 | -0.007 |
| Sun | 12663 | 38.7 | 0.003 |
| Thu | 4601 | 41.0 | 0.093 |
| Tue | 4991 | 37.6 | -0.018 |
| Wed | 4873 | 39.7 | 0.035 |
| Asia 00-07 | 9270 | 37.9 | -0.026 |
| Late 20-24 | 4534 | 40.4 | 0.05 |
| London 07-12 | 9234 | 38.6 | -0.005 |
| New York 12-20 | 14074 | 38.0 | -0.001 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 41244 | 38.1 | 0.006 | 0.018 | -1.55 | 17841 | 0.016 | 23403 | -0.002 |  |
| grade A+++ | 344 | 40.1 | 0.102 | -0.076 | +2.17 | 119 | -0.151 | 225 | 0.236 |  |
| grade A+ | 6233 | 39.1 | 0.042 | 0.046 | -0.22 | 2821 | 0.013 | 3412 | 0.066 |  |
| grade A | 14996 | 37.6 | 0.01 | 0.033 | -1.82 | 6496 | 0.007 | 8500 | 0.012 |  |
| grade B | 13283 | 38.4 | 0.004 | -0.001 | +0.35 | 5683 | 0.044 | 7600 | -0.027 |  |
| grade C | 6388 | 37.8 | -0.039 | -0.0 | -2.00 | 2722 | -0.007 | 3666 | -0.062 |  |
| layer htf | 24309 | 38.3 | 0.009 | 0.019 | -1.02 | 10477 | -0.017 | 13832 | 0.029 |  |
| layer loc | 8487 | 40.3 | 0.067 | 0.003 | +3.74 | 3577 | 0.081 | 4910 | 0.057 | YES |
| layer vol | 12928 | 39.0 | 0.024 | 0.024 | -0.06 | 5647 | 0.044 | 7281 | 0.008 |  |
| layer reg | 30509 | 37.5 | 0.005 | 0.017 | -1.34 | 13353 | 0.016 | 17156 | -0.003 |  |
| layer time | 27440 | 37.8 | 0.009 | 0.041 | -3.43 | 11990 | 0.009 | 15450 | 0.009 |  |
| no htf | 16935 | 37.9 | 0.001 | 0.016 | -1.20 | 7364 | 0.064 | 9571 | -0.046 |  |
| no loc | 32757 | 37.6 | -0.01 | 0.022 | -3.69 | 14264 | 0.0 | 18493 | -0.018 |  |
| no vol | 28316 | 37.7 | -0.002 | 0.015 | -1.84 | 12194 | 0.004 | 16122 | -0.007 |  |
| no reg | 10735 | 39.9 | 0.007 | 0.019 | -0.78 | 4488 | 0.018 | 6247 | -0.0 |  |
| no time | 13804 | 38.7 | -0.001 | -0.029 | +2.12 | 5851 | 0.031 | 7953 | -0.025 |  |
| grade A+ / turtle55 | 30 | 56.7 | 0.569 | 0.683 | -0.43 | 13 | 0.06 | 17 | 0.957 |  |
| grade B / sma1040 | 38 | 50.0 | 0.54 | 0.345 | +0.73 | 15 | 0.69 | 23 | 0.441 |  |
| grade B / wavec | 37 | 56.8 | 0.419 | 0.284 | +0.53 | 23 | 0.63 | 14 | 0.071 |  |
| grade A+ / macd_div | 110 | 50.9 | 0.351 | 0.188 | +1.16 | 55 | 0.513 | 55 | 0.188 |  |
| grade A / orb | 47 | 48.9 | 0.339 | -0.096 | +1.72 | 18 | 0.389 | 29 | 0.308 |  |
| grade A / turtle55 | 34 | 38.2 | 0.332 | 0.322 | +0.05 | 18 | 0.355 | 16 | 0.306 |  |
| grade A+ / m2022 | 98 | 48.0 | 0.278 | 0.064 | +1.34 | 47 | 0.116 | 51 | 0.427 |  |
| grade A+ / breaker | 48 | 43.8 | 0.264 | 0.043 | +0.97 | 19 | -0.079 | 29 | 0.489 |  |
| grade A / ew5 | 53 | 45.3 | 0.217 | -0.272 | +2.66 | 19 | -0.076 | 34 | 0.38 |  |
| grade B / abc | 41 | 46.3 | 0.18 | 0.119 | +0.30 | 23 | 0.413 | 18 | -0.118 |  |
| grade A+ / cisd | 94 | 44.7 | 0.174 | -0.1 | +1.60 | 49 | 0.201 | 45 | 0.145 |  |
| grade B / sess_amd | 104 | 46.2 | 0.168 | 0.178 | -0.07 | 50 | -0.071 | 54 | 0.389 |  |
| grade A / zombie | 219 | 42.0 | 0.151 | 0.09 | +0.58 | 83 | 0.027 | 136 | 0.227 |  |
| grade A+ / sweep | 468 | 42.5 | 0.142 | 0.075 | +0.87 | 223 | 0.121 | 245 | 0.16 |  |
| grade A / po3 | 45 | 44.4 | 0.138 | -0.357 | +2.46 | 19 | 0.316 | 26 | 0.008 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| sweep | vwap | 4918 | 3024 | 61.5 |
| level | vwap | 5340 | 2601 | 48.7 |
| ema_stack | sweep | 2441 | 1866 | 76.4 |
| ohl_open | vwap | 3206 | 1369 | 42.7 |
| ema_stack | level | 2457 | 1286 | 52.3 |
| macd_div | vwap | 1553 | 1248 | 80.4 |
| fib | vwap | 2253 | 1116 | 49.5 |
| msb_ob | vwap | 1968 | 1090 | 55.4 |
| fvg | vwap | 2846 | 1076 | 37.8 |
| level | sweep | 2496 | 1066 | 42.7 |
| ma_cross | sweep | 1560 | 1037 | 66.5 |
| rsi_div | vwap | 1277 | 1027 | 80.4 |
| judas | level | 1765 | 987 | 55.9 |
| tlbreak | vwap | 1995 | 919 | 46.1 |
| ma_cross | vwap | 3115 | 889 | 28.5 |
| level | ohl_open | 1691 | 866 | 51.2 |
| ob | vwap | 1559 | 820 | 52.6 |
| level | ma_cross | 1581 | 819 | 51.8 |
| liqline | vwap | 2350 | 800 | 34.0 |
| judas | sweep | 1219 | 792 | 65.0 |
| fvg | level | 1637 | 782 | 47.8 |
| judas | vwap | 2697 | 745 | 27.6 |
| fvg | ohl_open | 872 | 713 | 81.8 |
| liqline | sweep | 1278 | 708 | 55.4 |
| ohl_open | sweep | 1451 | 707 | 48.7 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 52 | 40.4 | 0.043 |
| 2 families | 493 | 36.7 | -0.011 |
| 2 families (with opposition) | 1337 | 37.2 | -0.01 |
| 3 families | 982 | 38.0 | 0.002 |
| 3 families (with opposition) | 3639 | 36.2 | -0.046 |
| 4+ families | 503 | 39.0 | 0.054 |
| 4+ families (with opposition) | 2187 | 37.1 | -0.027 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 77.1 | 15928 | 76.5 | 220929 | +1.8 |
| 1m shapes 120/180/240/360 deg | 74.0 | 7299 | 74.1 | 7202 | -0.2 |
| 15m | 58.0 | 10662 | 57.9 | 147624 | +0.4 |
| 15m shapes 120/180/240/360 deg | 58.7 | 5753 | 57.3 | 5782 | +2.1 |
| 1h | 56.2 | 9862 | 56.7 | 136585 | -1.1 |
| 1h shapes 120/180/240/360 deg | 56.6 | 5520 | 56.4 | 5528 | +0.4 |
| 4h | 55.8 | 7754 | 57.0 | 106840 | -2.1 |
| 4h shapes 120/180/240/360 deg | 56.0 | 4412 | 56.4 | 4400 | -0.6 |
| 1d | 57.8 | 4429 | 58.2 | 60742 | -0.6 |
| 1d shapes 120/180/240/360 deg | 59.1 | 2601 | 58.2 | 2607 | +0.9 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 94 | 29.8 | +0.111 | -0.348 | +1.90 |
| 1d | 76 | 47.4 | +0.170 | +0.029 | +0.70 |
| 1h | 66 | 22.7 | +0.124 | -0.230 | +1.18 |
| 4h | 107 | 33.6 | -0.034 | +0.000 | -0.21 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2883 | -0.138 |
| 15 days around full moon | 2811 | 0.149 |

Difference t = -3.17 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

| exit | n | win % | avg R | total R | t |
|---|---|---|---|---|---|
| rr1.0 | 41244 | 49.7 | -0.004 | -181.4 | -0.90 |
| rr1.5 | 41244 | 40.8 | 0.006 | 242.6 | +0.99 |
| rr2.0 | 41244 | 35.5 | 0.015 | 614.1 | +2.20 |
| rr3.0 | 41244 | 30.1 | 0.033 | 1349.1 | +4.06 |
| rr1.5_be | 41244 | 34.8 | 0.011 | 437.1 | +1.93 |
| rr2.0_be | 41244 | 27.5 | 0.019 | 768.2 | +3.09 |
