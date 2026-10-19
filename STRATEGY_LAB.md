# Strategy lab - real candles (2026-10-19)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | turtle55 | Trend (hedge fund) | 55 | 50.9 | 0.465 | 56.4 | 0.554 |  |
| 2 | sma1040 | Trend (hedge fund) | 52 | 50.0 | 0.375 | 40.4 | 0.13 |  |
| 3 | ew_r2_d2 | Elliott wave | 267 | 37.8 | 0.082 | 31.8 | -0.102 |  |
| 4 | abc | Elliott wave | 135 | 40.7 | 0.074 | 43.0 | 0.092 |  |
| 5 | wavec | Elliott wave | 127 | 40.2 | 0.066 | 40.2 | 0.047 |  |
| 6 | ew5 | Elliott wave | 171 | 38.6 | 0.05 | 32.2 | -0.115 |  |
| 7 | ohl_break | Levels / breakouts | 814 | 40.3 | 0.041 | 42.6 | 0.104 |  |
| 8 | ote | Fibonacci | 814 | 39.2 | 0.034 | 40.2 | 0.06 |  |
| 9 | ohl_open | Levels / breakouts | 3057 | 39.7 | 0.031 | 38.8 | 0.009 |  |
| 10 | breakout | Levels / breakouts | 1087 | 40.0 | 0.026 | 43.1 | 0.122 |  |
| 11 | rsi_div | Momentum / divergence | 1223 | 37.9 | 0.021 | 36.7 | -0.006 |  |
| 12 | level | Levels / breakouts | 5114 | 38.9 | 0.017 | 38.6 | 0.008 |  |
| 13 | liqline | Liquidity | 2673 | 38.8 | 0.016 | 39.7 | 0.044 |  |
| 14 | tlbreak | Levels / breakouts | 2154 | 38.7 | 0.013 | 39.3 | 0.034 |  |
| 15 | sweep | Liquidity | 3562 | 38.3 | 0.013 | 38.2 | 0.003 |  |
| 16 | m2022 | SMC / ICT | 629 | 38.3 | 0.011 | 40.5 | 0.07 |  |
| 17 | sess_amd | Time (sessions) | 473 | 39.7 | 0.008 | 40.6 | 0.032 |  |
| 18 | orb | Time (sessions) | 180 | 40.0 | 0.006 | 43.3 | 0.091 |  |
| 19 | macd_div | Momentum / divergence | 1388 | 37.6 | 0.006 | 38.7 | 0.032 |  |
| 20 | fib | Fibonacci | 2332 | 38.3 | 0.006 | 38.6 | 0.016 |  |
| 21 | judas | Time (sessions) | 2161 | 38.8 | 0.0 | 38.8 | -0.0 |  |
| 22 | msb_ob | SMC / ICT | 1871 | 37.9 | 0.0 | 38.7 | 0.017 |  |
| 23 | ew_r3_d2 | Elliott wave | 103 | 35.0 | -0.006 | 34.0 | -0.038 |  |
| 24 | zombie | Liquidity | 879 | 37.8 | -0.008 | 40.6 | 0.066 |  |
| 25 | donch | Trend (hedge fund) | 2704 | 37.6 | -0.011 | 37.9 | -0.002 |  |
| 26 | ma_cross | Trend (MA) | 2860 | 37.0 | -0.013 | 38.2 | 0.021 |  |
| 27 | fvg | SMC / ICT | 3053 | 37.4 | -0.013 | 39.2 | 0.035 |  |
| 28 | crt | Liquidity | 950 | 37.1 | -0.013 | 37.6 | 0.001 |  |
| 29 | ob | SMC / ICT | 1568 | 36.9 | -0.015 | 39.5 | 0.042 |  |
| 30 | cisd | SMC / ICT | 963 | 37.1 | -0.018 | 40.0 | 0.043 |  |
| 31 | ew_r2_d1 | Elliott wave | 477 | 35.8 | -0.019 | 37.1 | 0.007 |  |
| 32 | vwap | Trend (MA) | 7275 | 36.9 | -0.023 | 38.6 | 0.02 |  |
| 33 | ew3 | Elliott wave | 985 | 38.0 | -0.032 | 39.2 | 0.003 |  |
| 34 | ew_r3_v | Elliott wave | 290 | 35.5 | -0.035 | 33.8 | -0.06 |  |
| 35 | po3 | Time (sessions) | 128 | 37.5 | -0.038 | 39.1 | 0.041 |  |
| 36 | ema_stack | Trend (MA) | 4806 | 36.5 | -0.039 | 38.4 | 0.012 |  |
| 37 | ew_r2_v | Elliott wave | 884 | 34.3 | -0.042 | 35.9 | -0.027 |  |
| 38 | smt | Intermarket (SMT) | 1787 | 36.3 | -0.045 | 39.7 | 0.047 |  |
| 39 | ew_r3_d1 | Elliott wave | 204 | 32.8 | -0.064 | 31.4 | -0.09 |  |
| 40 | breaker | SMC / ICT | 415 | 34.0 | -0.073 | 37.3 | 0.007 |  |
| 41 | unicorn | SMC / ICT | 427 | 33.7 | -0.098 | 37.5 | 0.002 |  |
| 42 | kzs | Time (sessions) | 35 | 31.4 | -0.167 | 40.0 | 0.047 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Levels / breakouts | 12226 | 0.022 |
| 2 | Fibonacci | 3146 | 0.013 |
| 3 | Momentum / divergence | 2611 | 0.013 |
| 4 | Liquidity | 8064 | 0.009 |
| 5 | Trend (hedge fund) | 2811 | 0.005 |
| 6 | Time (sessions) | 2977 | -0.002 |
| 7 | Elliott wave | 3643 | -0.014 |
| 8 | SMC / ICT | 8926 | -0.016 |
| 9 | Trend (MA) | 14941 | -0.026 |
| 10 | Intermarket (SMT) | 1787 | -0.045 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 15m | 58 | 48.3 | 0.272 |
| breaker | 1h | 164 | 39.6 | 0.094 |
| breakout | 1d | 52 | 50.0 | 0.356 |
| cisd | 1h | 237 | 41.8 | 0.111 |
| crt | 1m | 87 | 42.5 | 0.115 |
| donch | 1d | 138 | 37.7 | 0.142 |
| ema_stack | 1d | 247 | 34.8 | 0.064 |
| ew3 | 15m | 265 | 43.0 | 0.096 |
| ew5 | 15m | 49 | 49.0 | 0.268 |
| ew_r2_d1 | 1h | 150 | 39.3 | 0.062 |
| ew_r2_d2 | 1h | 72 | 43.1 | 0.193 |
| ew_r2_v | 1m | 95 | 45.3 | 0.166 |
| ew_r3_d1 | 15m | 38 | 39.5 | 0.088 |
| ew_r3_d2 | 4h | 56 | 42.9 | 0.167 |
| ew_r3_v | 1h | 71 | 36.6 | -0.015 |
| fib | 1m | 394 | 41.4 | 0.072 |
| fvg | 4h | 515 | 38.4 | 0.039 |
| judas | 1m | 532 | 44.2 | 0.118 |
| level | 15m | 1557 | 40.8 | 0.052 |
| liqline | 1d | 115 | 43.5 | 0.357 |
| m2022 | 1d | 71 | 49.3 | 0.373 |
| ma_cross | 1d | 120 | 39.2 | 0.187 |
| macd_div | 1d | 63 | 46.0 | 0.38 |
| msb_ob | 15m | 505 | 42.6 | 0.105 |
| ob | 4h | 390 | 38.2 | 0.034 |
| ohl_break | 1d | 49 | 46.9 | 0.361 |
| ohl_open | 1d | 123 | 39.0 | 0.138 |
| orb | 15m | 173 | 39.9 | 0.003 |
| ote | 1m | 142 | 45.1 | 0.145 |
| po3 | 1h | 63 | 36.5 | -0.043 |
| rsi_div | 15m | 336 | 43.5 | 0.136 |
| sess_amd | 15m | 243 | 43.6 | 0.104 |
| sma1040 | 1d | 52 | 50.0 | 0.375 |
| smt | 4h | 383 | 37.1 | 0.006 |
| sweep | 1m | 480 | 43.5 | 0.098 |
| tlbreak | 1d | 126 | 43.7 | 0.192 |
| turtle55 | 1d | 55 | 50.9 | 0.465 |
| unicorn | 1h | 159 | 40.3 | 0.089 |
| vwap | 1m | 1315 | 43.1 | 0.102 |
| wavec | 15m | 42 | 54.8 | 0.369 |
| zombie | 1d | 40 | 55.0 | 0.528 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 81 | 0.203 | 54 | -0.12 |
| breaker | 196 | -0.116 | 219 | -0.034 |
| breakout | 545 | -0.011 | 542 | 0.063 |
| cisd | 488 | -0.065 | 475 | 0.03 |
| crt | 448 | -0.049 | 502 | 0.019 |
| donch | 1338 | -0.015 | 1366 | -0.006 |
| ema_stack | 2463 | -0.057 | 2343 | -0.021 |
| ew3 | 526 | -0.026 | 459 | -0.038 |
| ew5 | 80 | -0.068 | 91 | 0.154 |
| ew_r2_d1 | 199 | -0.021 | 278 | -0.017 |
| ew_r2_d2 | 106 | 0.169 | 161 | 0.024 |
| ew_r2_v | 433 | 0.018 | 451 | -0.1 |
| ew_r3_d1 | 85 | -0.094 | 119 | -0.042 |
| ew_r3_d2 | 40 | -0.009 | 63 | -0.004 |
| ew_r3_v | 135 | -0.102 | 155 | 0.024 |
| fib | 1131 | 0.001 | 1201 | 0.01 |
| fvg | 1663 | -0.011 | 1390 | -0.015 |
| judas | 1030 | -0.034 | 1131 | 0.031 |
| kzs | 19 | 0.008 | 16 | -0.375 |
| level | 3430 | 0.019 | 1684 | 0.014 |
| liqline | 1322 | 0.018 | 1351 | 0.014 |
| m2022 | 312 | -0.008 | 317 | 0.029 |
| ma_cross | 1457 | -0.008 | 1403 | -0.018 |
| macd_div | 674 | 0.03 | 714 | -0.018 |
| msb_ob | 993 | 0.039 | 878 | -0.043 |
| ob | 781 | -0.064 | 787 | 0.035 |
| ohl_break | 392 | -0.013 | 422 | 0.09 |
| ohl_open | 1553 | 0.029 | 1504 | 0.032 |
| orb | 98 | -0.172 | 82 | 0.22 |
| ote | 390 | 0.042 | 424 | 0.026 |
| po3 | 69 | 0.081 | 59 | -0.177 |
| rsi_div | 606 | 0.076 | 617 | -0.033 |
| sess_amd | 196 | -0.029 | 277 | 0.034 |
| sma1040 | 25 | 0.514 | 27 | 0.246 |
| smt | 927 | -0.044 | 860 | -0.046 |
| sweep | 1914 | 0.004 | 1648 | 0.023 |
| tlbreak | 1065 | -0.044 | 1089 | 0.069 |
| turtle55 | 34 | 0.214 | 21 | 0.87 |
| unicorn | 206 | -0.208 | 221 | 0.005 |
| vwap | 3741 | -0.028 | 3534 | -0.017 |
| wavec | 66 | -0.003 | 61 | 0.142 |
| zombie | 436 | -0.043 | 443 | 0.025 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 36418 | 37.7 | -0.006 | 24461 | 37.9 | -0.001 |
| abc | 30 | 43.3 | 0.083 | 105 | 40.0 | 0.071 |
| breaker | 200 | 37.5 | 0.012 | 210 | 31.0 | -0.143 |
| breakout | 776 | 39.4 | 0.012 | 308 | 41.2 | 0.055 |
| cisd | 368 | 37.5 | -0.025 | 585 | 36.8 | -0.014 |
| crt | 363 | 35.0 | -0.064 | 583 | 38.3 | 0.017 |
| donch | 2387 | 38.0 | 0.002 | 308 | 33.8 | -0.113 |
| ema_stack | 3904 | 36.9 | -0.024 | 880 | 34.5 | -0.1 |
| ew3 | 641 | 40.4 | 0.026 | 342 | 33.6 | -0.135 |
| ew5 | 142 | 38.0 | 0.038 | 27 | 40.7 | 0.101 |
| ew_r2_d1 | 288 | 34.4 | -0.076 | 189 | 38.1 | 0.068 |
| ew_r2_d2 | 148 | 35.8 | 0.002 | 119 | 40.3 | 0.18 |
| ew_r2_v | 561 | 33.3 | -0.078 | 323 | 35.9 | 0.019 |
| ew_r3_d1 | 168 | 34.5 | -0.054 | 36 | 25.0 | -0.109 |
| ew_r3_d2 | 88 | 35.2 | 0.001 | 15 | 33.3 | -0.046 |
| ew_r3_v | 254 | 36.2 | -0.022 | 36 | 30.6 | -0.122 |
| fib | 1192 | 38.7 | 0.027 | 1138 | 37.7 | -0.019 |
| fvg | 1787 | 36.3 | -0.031 | 1237 | 38.6 | 0.005 |
| judas | 1386 | 39.5 | 0.023 | 766 | 37.9 | -0.036 |
| kzs | 11 | 18.2 | -0.545 | 24 | 37.5 | 0.006 |
| level | 2604 | 38.2 | 0.003 | 2480 | 39.6 | 0.032 |
| liqline | 1569 | 38.8 | 0.004 | 1092 | 38.9 | 0.035 |
| m2022 | 348 | 37.4 | -0.016 | 280 | 39.6 | 0.047 |
| ma_cross | 1708 | 36.1 | -0.027 | 1137 | 38.4 | 0.012 |
| macd_div | 271 | 39.5 | 0.046 | 1113 | 37.2 | -0.003 |
| msb_ob | 970 | 37.1 | -0.019 | 888 | 38.5 | 0.011 |
| ob | 892 | 37.1 | -0.013 | 659 | 35.8 | -0.038 |
| ohl_break | 496 | 41.1 | 0.054 | 315 | 39.4 | 0.029 |
| ohl_open | 1659 | 39.9 | 0.033 | 1392 | 39.4 | 0.026 |
| orb | 107 | 38.3 | -0.042 | 73 | 42.5 | 0.077 |
| ote | 373 | 35.7 | -0.049 | 440 | 42.0 | 0.101 |
| po3 | 68 | 32.4 | -0.175 | 58 | 43.1 | 0.114 |
| rsi_div | 297 | 39.1 | 0.088 | 924 | 37.4 | -0.001 |
| sess_amd | 258 | 39.9 | 0.005 | 215 | 39.5 | 0.012 |
| sma1040 | 24 | 41.7 | 0.1 | 28 | 57.1 | 0.61 |
| smt | 920 | 36.6 | -0.04 | 864 | 35.9 | -0.052 |
| sweep | 1587 | 37.3 | -0.009 | 1968 | 39.2 | 0.03 |
| tlbreak | 1080 | 39.4 | 0.023 | 1068 | 38.2 | 0.006 |
| turtle55 | 42 | 50.0 | 0.455 | 13 | 53.8 | 0.496 |
| unicorn | 198 | 36.9 | -0.013 | 226 | 31.0 | -0.172 |
| vwap | 5734 | 37.1 | -0.015 | 1513 | 36.1 | -0.052 |
| wavec | 28 | 32.1 | 0.02 | 99 | 42.4 | 0.08 |
| zombie | 491 | 38.5 | 0.008 | 385 | 36.9 | -0.028 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7353 | 32.7 | -0.038 |
| Mon | 12183 | 38.6 | -0.001 |
| Sat | 6432 | 33.5 | -0.086 |
| Sun | 13175 | 39.5 | 0.011 |
| Thu | 7360 | 38.5 | 0.017 |
| Tue | 7483 | 40.4 | 0.037 |
| Wed | 7146 | 39.0 | 0.007 |
| Asia 00-07 | 18626 | 37.8 | -0.012 |
| Late 20-24 | 7772 | 39.8 | 0.041 |
| London 07-12 | 11207 | 38.4 | -0.013 |
| New York 12-20 | 20509 | 37.1 | -0.017 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 61132 | 37.8 | -0.004 | 0.021 | -3.97 | 26196 | -0.01 | 34936 | 0.0 |  |
| grade A+++ | 514 | 42.4 | 0.114 | -0.055 | +2.48 | 221 | 0.047 | 293 | 0.165 |  |
| grade A+ | 8607 | 38.0 | 0.01 | 0.016 | -0.33 | 4260 | -0.021 | 4347 | 0.04 |  |
| grade A | 19702 | 37.0 | -0.015 | 0.022 | -3.33 | 9053 | -0.031 | 10649 | -0.001 |  |
| grade B | 21057 | 38.2 | 0.011 | 0.046 | -3.26 | 8316 | 0.025 | 12741 | 0.001 |  |
| grade C | 11252 | 37.9 | -0.028 | -0.018 | -0.66 | 4346 | -0.024 | 6906 | -0.031 |  |
| layer htf | 36418 | 37.7 | -0.006 | 0.029 | -4.23 | 15631 | -0.032 | 20787 | 0.013 |  |
| layer loc | 13216 | 39.3 | 0.037 | 0.007 | +2.27 | 5515 | 0.045 | 7701 | 0.032 |  |
| layer vol | 19238 | 39.4 | 0.022 | 0.068 | -3.93 | 8311 | 0.006 | 10927 | 0.035 |  |
| layer reg | 44193 | 36.9 | -0.011 | 0.013 | -3.21 | 18870 | -0.017 | 25323 | -0.007 |  |
| layer time | 34734 | 37.3 | -0.009 | 0.016 | -3.09 | 17251 | -0.022 | 17483 | 0.003 |  |
| no htf | 24714 | 38.0 | -0.0 | 0.01 | -1.08 | 10565 | 0.024 | 14149 | -0.018 |  |
| no loc | 47916 | 37.4 | -0.015 | 0.025 | -5.65 | 20681 | -0.024 | 27235 | -0.009 |  |
| no vol | 41894 | 37.0 | -0.016 | -0.0 | -2.10 | 17885 | -0.017 | 24009 | -0.015 |  |
| no reg | 16939 | 40.2 | 0.015 | 0.044 | -2.34 | 7326 | 0.008 | 9613 | 0.02 |  |
| no time | 26398 | 38.4 | 0.003 | 0.028 | -2.50 | 8945 | 0.014 | 17453 | -0.002 |  |
| grade B / sess_amd | 119 | 51.3 | 0.297 | 0.193 | +0.77 | 40 | 0.17 | 79 | 0.361 |  |
| grade A+++ / vwap | 35 | 48.6 | 0.214 | 0.395 | -0.79 | 14 | 0.25 | 21 | 0.19 |  |
| grade A / abc | 43 | 44.2 | 0.205 | 0.453 | -0.97 | 26 | 0.32 | 17 | 0.029 |  |
| grade B / wavec | 44 | 45.5 | 0.179 | 0.268 | -0.38 | 23 | 0.447 | 21 | -0.114 |  |
| grade C / ote | 125 | 45.6 | 0.169 | 0.016 | +1.11 | 42 | 0.131 | 83 | 0.189 |  |
| grade A / wavec | 37 | 40.5 | 0.161 | -0.1 | +1.11 | 13 | -0.145 | 24 | 0.327 |  |
| grade A / ew5 | 64 | 42.2 | 0.151 | -0.195 | +1.89 | 27 | 0.113 | 37 | 0.18 |  |
| grade B / ew_r2_d2 | 90 | 38.9 | 0.135 | -0.121 | +1.47 | 32 | 0.187 | 58 | 0.106 |  |
| grade A+ / sess_amd | 110 | 44.5 | 0.128 | 0.026 | +0.70 | 48 | 0.16 | 62 | 0.103 |  |
| grade A / ew_r3_v | 116 | 39.7 | 0.121 | -0.18 | +2.15 | 54 | 0.28 | 62 | -0.018 |  |
| grade B / orb | 46 | 43.5 | 0.111 | -0.153 | +1.05 | 28 | 0.111 | 18 | 0.111 |  |
| grade C / zombie | 153 | 43.1 | 0.109 | 0.127 | -0.14 | 54 | 0.085 | 99 | 0.122 |  |
| grade A+ / cisd | 122 | 41.0 | 0.103 | 0.233 | -0.88 | 50 | -0.116 | 72 | 0.254 |  |
| grade A+++ / sweep | 69 | 40.6 | 0.102 | -0.141 | +1.23 | 31 | 0.1 | 38 | 0.103 |  |
| grade A+ / smt | 188 | 41.5 | 0.094 | -0.105 | +1.68 | 102 | 0.138 | 86 | 0.042 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8607 | 4008 | 46.6 |
| sweep | vwap | 6319 | 3835 | 60.7 |
| ema_stack | sweep | 3192 | 2371 | 74.3 |
| ema_stack | level | 4203 | 2034 | 48.4 |
| fvg | vwap | 4455 | 1799 | 40.4 |
| macd_div | vwap | 2111 | 1683 | 79.7 |
| ohl_open | vwap | 3919 | 1646 | 42.0 |
| level | sweep | 3737 | 1635 | 43.8 |
| msb_ob | vwap | 2742 | 1523 | 55.5 |
| fib | vwap | 2979 | 1497 | 50.3 |
| rsi_div | vwap | 1877 | 1455 | 77.5 |
| fvg | level | 3289 | 1418 | 43.1 |
| ob | vwap | 2503 | 1347 | 53.8 |
| level | ma_cross | 2682 | 1345 | 50.1 |
| ma_cross | sweep | 2053 | 1278 | 62.3 |
| liqline | vwap | 3557 | 1252 | 35.2 |
| judas | level | 2462 | 1240 | 50.4 |
| smt | vwap | 2864 | 1239 | 43.3 |
| ma_cross | vwap | 4257 | 1238 | 29.1 |
| tlbreak | vwap | 2548 | 1226 | 48.1 |
| level | ohl_open | 2416 | 1219 | 50.5 |
| judas | sweep | 1585 | 996 | 62.8 |
| level | liqline | 1981 | 977 | 49.3 |
| fib | level | 1907 | 935 | 49.0 |
| fvg | sweep | 1596 | 933 | 58.5 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 27 | 44.4 | 0.288 |
| 2 families | 461 | 37.5 | 0.027 |
| 2 families (with opposition) | 1444 | 36.9 | -0.013 |
| 3 families | 1381 | 40.2 | 0.055 |
| 3 families (with opposition) | 4802 | 37.6 | -0.012 |
| 4+ families | 828 | 34.1 | -0.112 |
| 4+ families (with opposition) | 3754 | 36.4 | -0.04 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 85.2 | 34892 | 85.0 | 482107 | +0.9 |
| 1m shapes 120/180/240/360 deg | 81.4 | 15220 | 81.4 | 15147 | -0.1 |
| 15m | 65.2 | 20819 | 64.9 | 287801 | +1.0 |
| 15m shapes 120/180/240/360 deg | 63.3 | 10687 | 63.2 | 10675 | +0.1 |
| 1h | 60.1 | 16741 | 59.6 | 232382 | +1.3 |
| 1h shapes 120/180/240/360 deg | 59.1 | 9100 | 59.0 | 9177 | +0.2 |
| 4h | 57.1 | 11849 | 57.9 | 163508 | -1.8 |
| 4h shapes 120/180/240/360 deg | 57.1 | 6699 | 57.4 | 6707 | -0.6 |
| 1d | 55.7 | 2740 | 56.0 | 37091 | -0.4 |
| 1d shapes 120/180/240/360 deg | 57.2 | 1714 | 57.3 | 1715 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 61 | 19.7 | -0.223 | +0.407 | -1.82 |
| 1d | 55 | 43.6 | +0.124 | +0.201 | -0.33 |
| 1h | 103 | 29.1 | +0.140 | +0.121 | +0.07 |
| 4h | 108 | 33.3 | +0.057 | +0.144 | -0.39 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2014 | -0.094 |
| 15 days around full moon | 1955 | 0.088 |

Difference t = -2.16 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 61132 | 48.7 | -0.024 | -0.124 | -1462.0 | -5.97 |
| rr1.5 | 61132 | 40.3 | -0.004 | -0.104 | -240.5 | -0.81 |
| rr2.0 | 61132 | 35.2 | 0.012 | -0.088 | 754.8 | +2.22 |
| rr3.0 | 61132 | 29.9 | 0.04 | -0.06 | 2451.6 | +6.01 |
| rr1.5_be | 61132 | 34.3 | -0.006 | -0.106 | -395.1 | -1.43 |
| rr2.0_be | 61132 | 27.2 | 0.006 | -0.094 | 356.0 | +1.17 |
| rr1.5_h16 | 61132 | 42.1 | -0.003 | -0.103 | -169.7 | -0.61 |
| rr2.0_h16 | 61132 | 39.0 | 0.013 | -0.087 | 794.6 | +2.56 |
