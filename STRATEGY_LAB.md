# Strategy lab - real candles (2026-10-19)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | turtle55 | Trend (hedge fund) | 55 | 50.9 | 0.465 | 56.4 | 0.554 |  |
| 2 | sma1040 | Trend (hedge fund) | 52 | 50.0 | 0.376 | 40.4 | 0.131 |  |
| 3 | wavec | Elliott wave | 122 | 49.2 | 0.277 | 34.4 | -0.071 | YES |
| 4 | abc | Elliott wave | 128 | 44.5 | 0.169 | 53.9 | 0.374 |  |
| 5 | ew5 | Elliott wave | 166 | 41.6 | 0.132 | 33.7 | -0.09 |  |
| 6 | ew_r2_d2 | Elliott wave | 270 | 38.9 | 0.105 | 35.2 | -0.006 |  |
| 7 | breakout | Levels / breakouts | 1047 | 42.2 | 0.093 | 42.3 | 0.097 |  |
| 8 | rsi_div | Momentum / divergence | 1206 | 39.9 | 0.063 | 38.6 | 0.019 |  |
| 9 | ote | Fibonacci | 766 | 40.1 | 0.057 | 38.8 | 0.037 |  |
| 10 | po3 | Time (sessions) | 136 | 40.4 | 0.048 | 34.6 | -0.093 |  |
| 11 | macd_div | Momentum / divergence | 1369 | 39.4 | 0.046 | 37.3 | -0.011 |  |
| 12 | ohl_open | Levels / breakouts | 3081 | 40.1 | 0.045 | 38.7 | 0.01 |  |
| 13 | m2022 | SMC / ICT | 671 | 39.6 | 0.04 | 42.2 | 0.093 |  |
| 14 | liqline | Liquidity | 2685 | 39.6 | 0.037 | 40.7 | 0.062 |  |
| 15 | level | Levels / breakouts | 5088 | 39.8 | 0.037 | 38.4 | 0.003 |  |
| 16 | sess_amd | Time (sessions) | 474 | 40.5 | 0.027 | 36.5 | -0.065 |  |
| 17 | ohl_break | Levels / breakouts | 865 | 39.0 | 0.017 | 40.2 | 0.051 |  |
| 18 | orb | Time (sessions) | 188 | 40.4 | 0.017 | 41.0 | 0.024 |  |
| 19 | ma_cross | Trend (MA) | 2875 | 38.3 | 0.013 | 38.8 | 0.019 |  |
| 20 | sweep | Liquidity | 3566 | 38.3 | 0.012 | 38.1 | -0.0 |  |
| 21 | ew_r2_d1 | Elliott wave | 469 | 37.1 | 0.011 | 36.9 | -0.005 |  |
| 22 | fvg | SMC / ICT | 3051 | 38.2 | 0.008 | 37.7 | -0.009 |  |
| 23 | vwap | Trend (MA) | 7267 | 38.2 | 0.003 | 39.3 | 0.032 |  |
| 24 | tlbreak | Levels / breakouts | 2145 | 38.2 | -0.002 | 39.2 | 0.031 |  |
| 25 | zombie | Liquidity | 891 | 38.4 | -0.003 | 41.4 | 0.088 |  |
| 26 | fib | Fibonacci | 2241 | 37.7 | -0.011 | 36.7 | -0.026 |  |
| 27 | smt | Intermarket (SMT) | 1750 | 37.6 | -0.015 | 36.3 | -0.049 |  |
| 28 | donch | Trend (hedge fund) | 2699 | 37.3 | -0.016 | 38.5 | 0.017 |  |
| 29 | ew3 | Elliott wave | 964 | 38.1 | -0.016 | 39.7 | 0.034 |  |
| 30 | ema_stack | Trend (MA) | 4781 | 37.4 | -0.019 | 39.0 | 0.025 |  |
| 31 | msb_ob | SMC / ICT | 1913 | 37.1 | -0.025 | 37.5 | -0.019 |  |
| 32 | judas | Time (sessions) | 2432 | 37.9 | -0.026 | 39.2 | 0.006 |  |
| 33 | cisd | SMC / ICT | 989 | 36.5 | -0.028 | 38.4 | 0.011 |  |
| 34 | crt | Liquidity | 915 | 36.3 | -0.039 | 37.9 | 0.002 |  |
| 35 | ob | SMC / ICT | 1566 | 35.6 | -0.057 | 39.1 | 0.032 |  |
| 36 | breaker | SMC / ICT | 429 | 33.6 | -0.076 | 34.3 | -0.069 |  |
| 37 | ew_r3_d2 | Elliott wave | 100 | 33.0 | -0.084 | 29.0 | -0.201 |  |
| 38 | ew_r3_d1 | Elliott wave | 202 | 31.7 | -0.098 | 26.2 | -0.232 |  |
| 39 | kzs | Time (sessions) | 38 | 34.2 | -0.101 | 42.1 | 0.053 |  |
| 40 | unicorn | SMC / ICT | 451 | 32.8 | -0.119 | 39.9 | 0.043 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Momentum / divergence | 2575 | 0.054 |
| 2 | Levels / breakouts | 12226 | 0.036 |
| 3 | Elliott wave | 2421 | 0.028 |
| 4 | Liquidity | 8057 | 0.013 |
| 5 | Fibonacci | 3007 | 0.006 |
| 6 | Trend (hedge fund) | 2806 | 0.001 |
| 7 | Trend (MA) | 14923 | -0.002 |
| 8 | Time (sessions) | 3268 | -0.014 |
| 9 | Intermarket (SMT) | 1750 | -0.015 |
| 10 | SMC / ICT | 9070 | -0.022 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 15m | 54 | 51.9 | 0.366 |
| breaker | 1h | 168 | 37.5 | 0.044 |
| breakout | 1d | 52 | 50.0 | 0.355 |
| cisd | 1d | 49 | 36.7 | 0.113 |
| crt | 1m | 84 | 41.7 | 0.054 |
| donch | 1d | 138 | 37.7 | 0.141 |
| ema_stack | 1d | 247 | 34.8 | 0.063 |
| ew3 | 15m | 271 | 42.1 | 0.075 |
| ew5 | 15m | 50 | 52.0 | 0.342 |
| ew_r2_d1 | 1d | 69 | 33.3 | 0.059 |
| ew_r2_d2 | 1h | 73 | 49.3 | 0.308 |
| ew_r3_d1 | 15m | 37 | 43.2 | 0.148 |
| ew_r3_d2 | 4h | 54 | 38.9 | 0.004 |
| fib | 1m | 372 | 39.5 | 0.026 |
| fvg | 4h | 540 | 39.8 | 0.083 |
| judas | 1h | 628 | 39.2 | -0.001 |
| level | 1m | 1267 | 41.6 | 0.068 |
| liqline | 1d | 115 | 43.5 | 0.358 |
| m2022 | 1d | 71 | 49.3 | 0.373 |
| ma_cross | 1d | 120 | 39.2 | 0.187 |
| macd_div | 1d | 63 | 46.0 | 0.382 |
| msb_ob | 15m | 505 | 43.4 | 0.113 |
| ob | 1m | 269 | 42.0 | 0.094 |
| ohl_break | 1d | 49 | 46.9 | 0.361 |
| ohl_open | 1d | 123 | 39.0 | 0.138 |
| orb | 15m | 182 | 40.7 | 0.023 |
| ote | 1m | 121 | 47.1 | 0.197 |
| po3 | 1h | 71 | 42.3 | 0.119 |
| rsi_div | 15m | 335 | 45.4 | 0.163 |
| sess_amd | 15m | 244 | 43.9 | 0.109 |
| sma1040 | 1d | 52 | 50.0 | 0.376 |
| smt | 4h | 377 | 37.9 | 0.023 |
| sweep | 1m | 467 | 45.2 | 0.137 |
| tlbreak | 1d | 126 | 43.7 | 0.193 |
| turtle55 | 1d | 55 | 50.9 | 0.465 |
| unicorn | 1h | 159 | 38.4 | 0.036 |
| vwap | 1m | 1308 | 44.5 | 0.134 |
| wavec | 15m | 42 | 57.1 | 0.429 |
| zombie | 1d | 40 | 55.0 | 0.529 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 77 | 0.182 | 51 | 0.148 |
| breaker | 211 | -0.146 | 218 | -0.009 |
| breakout | 530 | 0.063 | 517 | 0.124 |
| cisd | 500 | -0.053 | 489 | -0.003 |
| crt | 430 | -0.108 | 485 | 0.022 |
| donch | 1319 | -0.001 | 1380 | -0.031 |
| ema_stack | 2421 | -0.058 | 2360 | 0.02 |
| ew3 | 509 | -0.05 | 455 | 0.022 |
| ew5 | 73 | 0.025 | 93 | 0.216 |
| ew_r2_d1 | 196 | 0.048 | 273 | -0.016 |
| ew_r2_d2 | 105 | 0.207 | 165 | 0.039 |
| ew_r3_d1 | 82 | -0.126 | 120 | -0.079 |
| ew_r3_d2 | 39 | -0.141 | 61 | -0.048 |
| fib | 1073 | -0.034 | 1168 | 0.01 |
| fvg | 1635 | -0.022 | 1416 | 0.043 |
| judas | 1196 | -0.066 | 1236 | 0.014 |
| kzs | 25 | 0.166 | 13 | -0.615 |
| level | 3447 | 0.025 | 1641 | 0.06 |
| liqline | 1332 | 0.071 | 1353 | 0.004 |
| m2022 | 342 | -0.004 | 329 | 0.085 |
| ma_cross | 1444 | 0.022 | 1431 | 0.004 |
| macd_div | 670 | 0.1 | 699 | -0.006 |
| msb_ob | 1018 | -0.039 | 895 | -0.009 |
| ob | 785 | -0.092 | 781 | -0.022 |
| ohl_break | 429 | -0.02 | 436 | 0.053 |
| ohl_open | 1553 | 0.007 | 1528 | 0.084 |
| orb | 99 | -0.105 | 89 | 0.152 |
| ote | 375 | -0.01 | 391 | 0.12 |
| po3 | 76 | 0.234 | 60 | -0.188 |
| rsi_div | 592 | 0.068 | 614 | 0.058 |
| sess_amd | 193 | -0.01 | 281 | 0.053 |
| sma1040 | 25 | 0.514 | 27 | 0.248 |
| smt | 910 | -0.024 | 840 | -0.006 |
| sweep | 1921 | 0.011 | 1645 | 0.013 |
| tlbreak | 1075 | -0.026 | 1070 | 0.022 |
| turtle55 | 34 | 0.214 | 21 | 0.87 |
| unicorn | 220 | -0.231 | 231 | -0.013 |
| vwap | 3681 | -0.007 | 3586 | 0.014 |
| wavec | 63 | 0.236 | 59 | 0.321 |
| zombie | 469 | -0.058 | 422 | 0.057 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 35547 | 38.1 | -0.0 | 24244 | 38.7 | 0.019 |
| abc | 31 | 41.9 | 0.048 | 97 | 45.4 | 0.207 |
| breaker | 203 | 35.5 | -0.073 | 225 | 31.6 | -0.086 |
| breakout | 752 | 42.3 | 0.093 | 293 | 42.3 | 0.101 |
| cisd | 376 | 35.6 | -0.055 | 607 | 37.2 | -0.007 |
| crt | 351 | 34.2 | -0.093 | 561 | 37.6 | -0.005 |
| donch | 2383 | 37.7 | -0.008 | 309 | 34.3 | -0.075 |
| ema_stack | 3867 | 37.7 | -0.01 | 888 | 36.0 | -0.056 |
| ew3 | 614 | 41.2 | 0.06 | 345 | 33.0 | -0.135 |
| ew5 | 132 | 41.7 | 0.146 | 34 | 41.2 | 0.078 |
| ew_r2_d1 | 282 | 36.2 | -0.014 | 187 | 38.5 | 0.049 |
| ew_r2_d2 | 145 | 35.9 | -0.002 | 125 | 42.4 | 0.229 |
| ew_r3_d1 | 167 | 32.9 | -0.086 | 35 | 25.7 | -0.156 |
| ew_r3_d2 | 85 | 34.1 | -0.062 | 15 | 26.7 | -0.214 |
| fib | 1125 | 36.9 | -0.029 | 1110 | 38.6 | 0.009 |
| fvg | 1784 | 36.8 | -0.02 | 1244 | 40.0 | 0.046 |
| judas | 1533 | 38.0 | -0.02 | 880 | 37.8 | -0.032 |
| kzs | 10 | 20.0 | -0.5 | 28 | 39.3 | 0.041 |
| level | 2607 | 40.5 | 0.049 | 2440 | 39.0 | 0.024 |
| liqline | 1537 | 39.8 | 0.032 | 1134 | 39.3 | 0.044 |
| m2022 | 369 | 40.7 | 0.071 | 300 | 38.3 | -0.0 |
| ma_cross | 1697 | 38.2 | 0.017 | 1154 | 38.6 | 0.015 |
| macd_div | 267 | 38.2 | 0.012 | 1099 | 39.6 | 0.052 |
| msb_ob | 1007 | 35.9 | -0.052 | 888 | 38.0 | -0.005 |
| ob | 886 | 35.3 | -0.074 | 658 | 35.0 | -0.061 |
| ohl_break | 503 | 38.8 | -0.003 | 356 | 39.6 | 0.05 |
| ohl_open | 1695 | 39.8 | 0.034 | 1369 | 40.4 | 0.06 |
| orb | 111 | 38.7 | -0.032 | 77 | 42.9 | 0.086 |
| ote | 342 | 37.7 | 0.01 | 423 | 42.1 | 0.096 |
| po3 | 69 | 31.9 | -0.163 | 65 | 49.2 | 0.265 |
| rsi_div | 298 | 41.3 | 0.114 | 902 | 39.2 | 0.042 |
| sess_amd | 244 | 39.3 | -0.009 | 229 | 41.5 | 0.059 |
| sma1040 | 24 | 41.7 | 0.1 | 28 | 57.1 | 0.612 |
| smt | 895 | 38.5 | 0.006 | 850 | 36.6 | -0.037 |
| sweep | 1585 | 37.0 | -0.019 | 1972 | 39.5 | 0.037 |
| tlbreak | 1033 | 37.9 | -0.016 | 1105 | 38.5 | 0.011 |
| turtle55 | 42 | 50.0 | 0.455 | 13 | 53.8 | 0.496 |
| unicorn | 212 | 31.1 | -0.164 | 238 | 34.0 | -0.085 |
| vwap | 5773 | 37.9 | -0.002 | 1464 | 39.3 | 0.025 |
| wavec | 25 | 40.0 | 0.173 | 97 | 51.5 | 0.304 |
| zombie | 486 | 38.1 | -0.011 | 400 | 38.8 | 0.006 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7202 | 32.1 | -0.042 |
| Mon | 9776 | 40.3 | 0.033 |
| Sat | 6216 | 34.8 | -0.076 |
| Sun | 15323 | 39.8 | 0.019 |
| Thu | 7127 | 38.9 | 0.03 |
| Tue | 7423 | 40.5 | 0.036 |
| Wed | 7036 | 39.3 | 0.019 |
| Asia 00-07 | 16157 | 38.9 | 0.007 |
| Late 20-24 | 11974 | 39.0 | 0.022 |
| London 07-12 | 7686 | 40.2 | 0.015 |
| New York 12-20 | 21361 | 37.4 | -0.009 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 60103 | 38.4 | 0.008 | 0.015 | -1.18 | 26027 | -0.011 | 34076 | 0.022 |  |
| grade A+++ | 544 | 36.0 | -0.01 | -0.087 | +1.21 | 267 | -0.215 | 277 | 0.188 |  |
| grade A+ | 8448 | 38.9 | 0.036 | 0.024 | +0.65 | 3982 | -0.014 | 4466 | 0.08 |  |
| grade A | 18313 | 37.1 | -0.016 | 0.024 | -3.50 | 8475 | -0.016 | 9838 | -0.016 |  |
| grade B | 20975 | 39.1 | 0.028 | 0.011 | +1.57 | 8592 | 0.004 | 12383 | 0.044 |  |
| grade C | 11823 | 38.6 | -0.011 | 0.007 | -1.27 | 4711 | -0.018 | 7112 | -0.006 |  |
| layer htf | 35547 | 38.1 | -0.0 | 0.019 | -2.26 | 15373 | -0.043 | 20174 | 0.033 |  |
| layer loc | 13048 | 39.6 | 0.043 | 0.002 | +3.04 | 5627 | 0.054 | 7421 | 0.035 | YES |
| layer vol | 19558 | 39.8 | 0.04 | 0.062 | -1.96 | 8671 | 0.016 | 10887 | 0.059 |  |
| layer reg | 43260 | 37.4 | -0.0 | -0.002 | +0.25 | 18502 | -0.021 | 24758 | 0.015 |  |
| layer time | 31972 | 37.9 | 0.003 | 0.02 | -2.00 | 15578 | -0.02 | 16394 | 0.024 |  |
| no htf | 24556 | 38.7 | 0.019 | 0.01 | +0.91 | 10654 | 0.034 | 13902 | 0.007 |  |
| no loc | 47055 | 38.0 | -0.002 | 0.019 | -2.93 | 20400 | -0.029 | 26655 | 0.018 |  |
| no vol | 40545 | 37.7 | -0.008 | -0.007 | -0.08 | 17356 | -0.025 | 23189 | 0.005 |  |
| no reg | 16843 | 40.7 | 0.028 | 0.06 | -2.57 | 7525 | 0.013 | 9318 | 0.04 |  |
| no time | 28131 | 38.9 | 0.013 | 0.01 | +0.40 | 10449 | 0.002 | 17682 | 0.02 |  |
| grade A / wavec | 32 | 53.1 | 0.464 | -0.01 | +1.74 | 16 | 0.719 | 16 | 0.209 |  |
| grade B / wavec | 41 | 53.7 | 0.378 | 0.076 | +1.19 | 23 | 0.538 | 18 | 0.172 |  |
| grade B / po3 | 40 | 52.5 | 0.343 | -0.062 | +1.77 | 17 | 0.324 | 23 | 0.358 |  |
| grade C / breakout | 89 | 50.6 | 0.275 | 0.163 | +0.63 | 33 | 0.515 | 56 | 0.134 |  |
| grade B / sess_amd | 122 | 49.2 | 0.244 | -0.068 | +2.20 | 45 | -0.016 | 77 | 0.396 |  |
| grade A+ / macd_div | 123 | 45.5 | 0.231 | 0.032 | +1.30 | 61 | 0.351 | 62 | 0.112 |  |
| grade A / ew5 | 51 | 47.1 | 0.221 | 0.046 | +0.83 | 21 | 0.219 | 30 | 0.223 |  |
| grade A / abc | 41 | 46.3 | 0.216 | 0.22 | -0.01 | 23 | 0.624 | 18 | -0.306 |  |
| grade A+ / m2022 | 123 | 46.3 | 0.215 | 0.132 | +0.58 | 55 | -0.134 | 68 | 0.496 |  |
| grade B / ew5 | 62 | 41.9 | 0.203 | -0.119 | +1.66 | 29 | 0.306 | 33 | 0.112 |  |
| grade A+ / ew_r2_d2 | 44 | 43.2 | 0.186 | 0.079 | +0.40 | 16 | 0.309 | 28 | 0.115 |  |
| grade B / ew_r2_d2 | 107 | 40.2 | 0.184 | -0.015 | +1.22 | 32 | 0.096 | 75 | 0.221 |  |
| grade C / wavec | 41 | 46.3 | 0.159 | -0.329 | +2.24 | 17 | -0.118 | 24 | 0.354 |  |
| grade A+++ / sweep | 66 | 39.4 | 0.156 | -0.004 | +0.81 | 27 | 0.025 | 39 | 0.246 |  |
| grade A+ / smt | 180 | 43.3 | 0.143 | -0.01 | +1.17 | 97 | 0.12 | 83 | 0.17 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8580 | 4022 | 46.9 |
| sweep | vwap | 6313 | 3836 | 60.8 |
| ema_stack | sweep | 3196 | 2386 | 74.7 |
| ema_stack | level | 4199 | 2045 | 48.7 |
| fvg | vwap | 4431 | 1772 | 40.0 |
| ohl_open | vwap | 3976 | 1692 | 42.6 |
| macd_div | vwap | 2084 | 1657 | 79.5 |
| level | sweep | 3703 | 1638 | 44.2 |
| msb_ob | vwap | 2813 | 1575 | 56.0 |
| rsi_div | vwap | 1842 | 1428 | 77.5 |
| fib | vwap | 2848 | 1413 | 49.6 |
| fvg | level | 3242 | 1405 | 43.3 |
| ob | vwap | 2491 | 1360 | 54.6 |
| level | ma_cross | 2684 | 1344 | 50.1 |
| ma_cross | sweep | 2064 | 1319 | 63.9 |
| judas | level | 2734 | 1309 | 47.9 |
| liqline | vwap | 3554 | 1276 | 35.9 |
| smt | vwap | 2845 | 1240 | 43.6 |
| ma_cross | vwap | 4283 | 1229 | 28.7 |
| tlbreak | vwap | 2522 | 1216 | 48.2 |
| level | ohl_open | 2470 | 1195 | 48.4 |
| judas | vwap | 3931 | 1070 | 27.2 |
| judas | sweep | 1713 | 1063 | 62.1 |
| level | liqline | 1990 | 998 | 50.2 |
| fvg | sweep | 1618 | 955 | 59.0 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 24 | 37.5 | 0.046 |
| 2 families | 472 | 35.4 | -0.019 |
| 2 families (with opposition) | 1523 | 36.9 | -0.022 |
| 3 families | 1433 | 42.4 | 0.104 |
| 3 families (with opposition) | 4950 | 37.6 | -0.011 |
| 4+ families | 766 | 37.1 | -0.021 |
| 4+ families (with opposition) | 3479 | 37.1 | -0.029 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 85.5 | 35661 | 85.2 | 493872 | +1.6 |
| 1m shapes 120/180/240/360 deg | 80.8 | 15599 | 81.0 | 15524 | -0.4 |
| 15m | 65.1 | 20858 | 64.7 | 288391 | +1.2 |
| 15m shapes 120/180/240/360 deg | 63.2 | 10780 | 63.0 | 10756 | +0.5 |
| 1h | 60.0 | 16726 | 59.5 | 232201 | +1.3 |
| 1h shapes 120/180/240/360 deg | 59.0 | 9092 | 58.8 | 9174 | +0.3 |
| 4h | 57.1 | 11843 | 57.9 | 163363 | -1.9 |
| 4h shapes 120/180/240/360 deg | 57.1 | 6687 | 57.4 | 6691 | -0.6 |
| 1d | 55.7 | 2740 | 56.0 | 37091 | -0.4 |
| 1d shapes 120/180/240/360 deg | 57.2 | 1714 | 57.3 | 1715 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 68 | 17.6 | -0.280 | +0.062 | -1.66 |
| 1d | 55 | 43.6 | +0.124 | -0.020 | +0.63 |
| 1h | 101 | 24.8 | +0.027 | +0.044 | -0.07 |
| 4h | 109 | 33.9 | +0.088 | -0.064 | +0.85 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2014 | -0.094 |
| 15 days around full moon | 1955 | 0.088 |

Difference t = -2.17 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 60103 | 49.3 | -0.014 | -0.114 | -816.6 | -3.36 |
| rr1.5 | 60103 | 40.8 | 0.008 | -0.092 | 455.1 | +1.54 |
| rr2.0 | 60103 | 35.6 | 0.023 | -0.077 | 1394.0 | +4.13 |
| rr3.0 | 60103 | 29.8 | 0.042 | -0.058 | 2548.8 | +6.29 |
| rr1.5_be | 60103 | 34.7 | 0.005 | -0.095 | 274.1 | +1.00 |
| rr2.0_be | 60103 | 27.6 | 0.019 | -0.081 | 1125.2 | +3.73 |
| rr1.5_h16 | 60103 | 42.6 | 0.011 | -0.089 | 653.9 | +2.36 |
| rr2.0_h16 | 60103 | 39.3 | 0.025 | -0.075 | 1505.8 | +4.89 |
