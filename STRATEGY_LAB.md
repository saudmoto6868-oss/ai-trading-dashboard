# Strategy lab - real candles (2026-10-28)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 49 | 53.1 | 0.499 | 0.399 | 32.7 | -0.038 |  |
| 2 | turtle55 | Trend (hedge fund) | 79 | 43.0 | 0.213 | 0.113 | 39.2 | 0.122 |  |
| 3 | wavec | Elliott wave | 133 | 42.9 | 0.155 | 0.055 | 35.3 | -0.051 |  |
| 4 | sess_amd | Time (sessions) | 663 | 43.3 | 0.117 | 0.017 | 39.4 | 0.012 |  |
| 5 | ew_r2_d1 | Elliott wave | 537 | 39.1 | 0.06 | -0.04 | 36.1 | -0.017 |  |
| 6 | po3 | Time (sessions) | 149 | 40.9 | 0.058 | -0.042 | 30.9 | -0.197 |  |
| 7 | ew_r2_d2 | Elliott wave | 281 | 36.3 | 0.056 | -0.044 | 37.7 | 0.05 |  |
| 8 | crt | Liquidity | 836 | 39.7 | 0.055 | -0.045 | 36.5 | -0.039 |  |
| 9 | ote | Fibonacci | 849 | 40.4 | 0.053 | -0.047 | 38.5 | 0.017 |  |
| 10 | ew_r3_d2 | Elliott wave | 106 | 35.8 | 0.018 | -0.082 | 33.0 | -0.069 |  |
| 11 | fib | Fibonacci | 2435 | 38.6 | 0.014 | -0.086 | 37.7 | 0.003 |  |
| 12 | sweep | Liquidity | 3661 | 38.1 | 0.005 | -0.095 | 37.3 | -0.017 |  |
| 13 | cisd | SMC / ICT | 1001 | 38.1 | 0.004 | -0.096 | 36.9 | -0.021 |  |
| 14 | rsi_div | Momentum / divergence | 1215 | 37.5 | 0.002 | -0.098 | 38.0 | 0.018 |  |
| 15 | m2022 | SMC / ICT | 781 | 37.8 | 0.002 | -0.098 | 37.9 | 0.004 |  |
| 16 | level | Levels / breakouts | 5098 | 38.3 | -0.003 | -0.103 | 38.2 | -0.006 |  |
| 17 | fvg | SMC / ICT | 3259 | 38.1 | -0.003 | -0.103 | 39.6 | 0.037 |  |
| 18 | msb_ob | SMC / ICT | 1930 | 37.6 | -0.009 | -0.109 | 36.8 | -0.035 |  |
| 19 | liqline | Liquidity | 2589 | 37.9 | -0.01 | -0.11 | 36.4 | -0.047 |  |
| 20 | tlbreak | Levels / breakouts | 2236 | 37.7 | -0.013 | -0.113 | 37.7 | -0.011 |  |
| 21 | ma_cross | Trend (MA) | 2912 | 37.3 | -0.021 | -0.121 | 36.4 | -0.045 |  |
| 22 | kzs | Time (sessions) | 41 | 39.0 | -0.024 | -0.124 | 34.1 | -0.146 |  |
| 23 | breaker | SMC / ICT | 438 | 35.4 | -0.024 | -0.124 | 32.2 | -0.103 |  |
| 24 | ob | SMC / ICT | 1570 | 36.9 | -0.029 | -0.129 | 36.8 | -0.033 |  |
| 25 | macd_div | Momentum / divergence | 1418 | 36.3 | -0.029 | -0.129 | 37.9 | 0.01 |  |
| 26 | ew_r2_v | Elliott wave | 947 | 35.3 | -0.029 | -0.129 | 34.1 | -0.071 |  |
| 27 | donch | Trend (hedge fund) | 2735 | 36.8 | -0.031 | -0.131 | 38.6 | 0.004 |  |
| 28 | zombie | Liquidity | 905 | 36.9 | -0.032 | -0.132 | 35.4 | -0.06 |  |
| 29 | ew5 | Elliott wave | 141 | 34.0 | -0.033 | -0.133 | 27.0 | -0.215 |  |
| 30 | smt | Intermarket (SMT) | 1866 | 36.8 | -0.033 | -0.133 | 38.4 | 0.008 |  |
| 31 | ohl_break | Levels / breakouts | 770 | 37.7 | -0.034 | -0.134 | 37.4 | -0.034 |  |
| 32 | orb | Time (sessions) | 215 | 38.1 | -0.035 | -0.135 | 34.0 | -0.147 |  |
| 33 | breakout | Levels / breakouts | 1001 | 37.5 | -0.038 | -0.138 | 36.7 | -0.049 |  |
| 34 | ohl_open | Levels / breakouts | 3185 | 36.7 | -0.044 | -0.144 | 38.1 | -0.001 |  |
| 35 | ema_stack | Trend (MA) | 4903 | 36.4 | -0.047 | -0.147 | 38.2 | 0.002 |  |
| 36 | vwap | Trend (MA) | 7359 | 36.1 | -0.048 | -0.148 | 37.4 | -0.017 |  |
| 37 | ew_r3_d1 | Elliott wave | 205 | 32.2 | -0.049 | -0.149 | 28.8 | -0.166 |  |
| 38 | ew3 | Elliott wave | 992 | 36.0 | -0.055 | -0.155 | 37.7 | -0.015 |  |
| 39 | ew_r3_v | Elliott wave | 336 | 33.6 | -0.059 | -0.159 | 36.0 | -0.018 |  |
| 40 | judas | Time (sessions) | 2328 | 36.3 | -0.067 | -0.167 | 38.4 | -0.018 |  |
| 41 | abc | Elliott wave | 91 | 34.1 | -0.095 | -0.195 | 35.2 | -0.067 |  |
| 42 | unicorn | SMC / ICT | 474 | 33.1 | -0.098 | -0.198 | 35.2 | -0.032 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Fibonacci | 3284 | 0.024 |
| 2 | Liquidity | 7991 | 0.001 |
| 3 | SMC / ICT | 9453 | -0.013 |
| 4 | Elliott wave | 3769 | -0.015 |
| 5 | Momentum / divergence | 2633 | -0.015 |
| 6 | Trend (hedge fund) | 2863 | -0.015 |
| 7 | Levels / breakouts | 12290 | -0.02 |
| 8 | Time (sessions) | 3396 | -0.023 |
| 9 | Intermarket (SMT) | 1866 | -0.033 |
| 10 | Trend (MA) | 15174 | -0.042 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| breaker | 1m | 48 | 47.9 | 0.227 | 0.127 |
| breakout | 1d | 46 | 45.7 | 0.227 | 0.127 |
| cisd | 1m | 201 | 43.3 | 0.094 | -0.006 |
| crt | 1m | 90 | 50.0 | 0.25 | 0.15 |
| donch | 1d | 150 | 34.7 | 0.042 | -0.058 |
| ema_stack | 1d | 263 | 36.5 | 0.07 | -0.03 |
| ew3 | 1m | 185 | 38.4 | -0.017 | -0.117 |
| ew5 | 15m | 32 | 37.5 | 0.012 | -0.088 |
| ew_r2_d1 | 1h | 161 | 44.1 | 0.165 | 0.065 |
| ew_r2_d2 | 1h | 72 | 40.3 | 0.144 | 0.044 |
| ew_r2_v | 15m | 266 | 38.0 | -0.008 | -0.108 |
| ew_r3_d1 | 4h | 75 | 36.0 | -0.002 | -0.102 |
| ew_r3_d2 | 4h | 53 | 37.7 | -0.002 | -0.102 |
| ew_r3_v | 4h | 82 | 37.8 | 0.031 | -0.069 |
| fib | 15m | 700 | 42.1 | 0.074 | -0.026 |
| fvg | 4h | 518 | 42.7 | 0.146 | 0.046 |
| judas | 1m | 704 | 38.5 | -0.016 | -0.116 |
| level | 4h | 826 | 38.9 | 0.054 | -0.046 |
| liqline | 1d | 140 | 37.9 | 0.176 | 0.076 |
| m2022 | 1d | 71 | 47.9 | 0.339 | 0.239 |
| ma_cross | 1d | 127 | 42.5 | 0.206 | 0.106 |
| macd_div | 1d | 67 | 50.7 | 0.401 | 0.301 |
| msb_ob | 1m | 367 | 44.7 | 0.144 | 0.044 |
| ob | 1m | 284 | 40.8 | 0.033 | -0.067 |
| ohl_break | 1d | 41 | 53.7 | 0.427 | 0.327 |
| ohl_open | 1m | 749 | 39.3 | -0.009 | -0.109 |
| orb | 15m | 197 | 38.6 | -0.028 | -0.128 |
| ote | 1m | 161 | 46.6 | 0.186 | 0.086 |
| po3 | 15m | 77 | 49.4 | 0.241 | 0.141 |
| rsi_div | 4h | 282 | 37.6 | 0.036 | -0.064 |
| sess_amd | 15m | 268 | 48.1 | 0.231 | 0.131 |
| sma1040 | 1d | 49 | 53.1 | 0.499 | 0.399 |
| smt | 4h | 379 | 37.7 | 0.035 | -0.065 |
| sweep | 15m | 981 | 40.4 | 0.046 | -0.054 |
| tlbreak | 4h | 462 | 40.0 | 0.074 | -0.026 |
| turtle55 | 1d | 79 | 43.0 | 0.213 | 0.113 |
| unicorn | 1m | 68 | 44.1 | 0.138 | 0.038 |
| vwap | 1d | 391 | 34.5 | 0.008 | -0.092 |
| wavec | 15m | 30 | 46.7 | 0.167 | 0.067 |
| zombie | 1d | 54 | 42.6 | 0.204 | 0.104 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 43 | -0.247 | 48 | 0.041 |
| breaker | 222 | -0.019 | 216 | -0.03 |
| breakout | 521 | -0.102 | 480 | 0.031 |
| cisd | 507 | -0.049 | 494 | 0.059 |
| crt | 385 | 0.042 | 451 | 0.067 |
| donch | 1322 | -0.05 | 1413 | -0.013 |
| ema_stack | 2436 | -0.075 | 2467 | -0.018 |
| ew3 | 511 | -0.107 | 481 | -0.001 |
| ew5 | 63 | -0.165 | 78 | 0.074 |
| ew_r2_d1 | 246 | 0.041 | 291 | 0.077 |
| ew_r2_d2 | 120 | -0.033 | 161 | 0.123 |
| ew_r2_v | 469 | 0.013 | 478 | -0.071 |
| ew_r3_d1 | 103 | -0.067 | 102 | -0.03 |
| ew_r3_d2 | 43 | 0.027 | 63 | 0.012 |
| ew_r3_v | 165 | -0.134 | 171 | 0.013 |
| fib | 1174 | -0.029 | 1261 | 0.054 |
| fvg | 1777 | -0.018 | 1482 | 0.014 |
| judas | 1273 | -0.127 | 1055 | 0.004 |
| kzs | 22 | -0.091 | 19 | 0.053 |
| level | 3395 | -0.013 | 1703 | 0.018 |
| liqline | 1275 | -0.043 | 1314 | 0.022 |
| m2022 | 395 | -0.009 | 386 | 0.013 |
| ma_cross | 1522 | -0.013 | 1390 | -0.029 |
| macd_div | 754 | -0.038 | 664 | -0.02 |
| msb_ob | 1008 | -0.033 | 922 | 0.017 |
| ob | 793 | -0.099 | 777 | 0.042 |
| ohl_break | 385 | -0.029 | 385 | -0.038 |
| ohl_open | 1570 | -0.053 | 1615 | -0.035 |
| orb | 108 | 0.111 | 107 | -0.183 |
| ote | 407 | -0.005 | 442 | 0.106 |
| po3 | 79 | 0.255 | 70 | -0.163 |
| rsi_div | 624 | -0.069 | 591 | 0.077 |
| sess_amd | 293 | 0.146 | 370 | 0.094 |
| sma1040 | 20 | 0.764 | 29 | 0.317 |
| smt | 974 | -0.044 | 892 | -0.021 |
| sweep | 2027 | -0.011 | 1634 | 0.025 |
| tlbreak | 1127 | -0.05 | 1109 | 0.024 |
| turtle55 | 45 | 0.081 | 34 | 0.388 |
| unicorn | 238 | -0.201 | 236 | 0.006 |
| vwap | 3681 | -0.063 | 3678 | -0.034 |
| wavec | 61 | -0.057 | 72 | 0.335 |
| zombie | 462 | -0.056 | 443 | -0.007 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 37279 | 37.0 | -0.026 | 25112 | 37.7 | -0.009 |
| abc | 32 | 34.4 | -0.064 | 59 | 33.9 | -0.112 |
| breaker | 205 | 31.7 | -0.101 | 233 | 38.6 | 0.044 |
| breakout | 741 | 37.5 | -0.04 | 257 | 37.0 | -0.04 |
| cisd | 383 | 37.6 | -0.013 | 610 | 38.4 | 0.015 |
| crt | 322 | 38.8 | 0.021 | 506 | 40.3 | 0.076 |
| donch | 2379 | 36.7 | -0.03 | 342 | 36.3 | -0.061 |
| ema_stack | 3991 | 37.1 | -0.028 | 886 | 33.1 | -0.131 |
| ew3 | 658 | 36.5 | -0.039 | 330 | 34.8 | -0.091 |
| ew5 | 116 | 34.5 | -0.03 | 24 | 29.2 | -0.111 |
| ew_r2_d1 | 308 | 38.0 | 0.051 | 229 | 40.6 | 0.073 |
| ew_r2_d2 | 143 | 35.0 | 0.072 | 138 | 37.7 | 0.041 |
| ew_r2_v | 566 | 35.2 | -0.014 | 376 | 35.4 | -0.053 |
| ew_r3_d1 | 160 | 32.5 | -0.053 | 45 | 31.1 | -0.033 |
| ew_r3_d2 | 88 | 36.4 | 0.026 | 18 | 33.3 | -0.021 |
| ew_r3_v | 291 | 34.4 | -0.046 | 45 | 28.9 | -0.145 |
| fib | 1249 | 37.1 | -0.024 | 1175 | 40.2 | 0.055 |
| fvg | 1876 | 37.2 | -0.018 | 1348 | 39.5 | 0.024 |
| judas | 1527 | 37.1 | -0.038 | 788 | 34.5 | -0.128 |
| kzs | 11 | 36.4 | -0.091 | 30 | 40.0 | 0.0 |
| level | 2558 | 37.8 | -0.023 | 2504 | 38.8 | 0.021 |
| liqline | 1497 | 36.0 | -0.061 | 1080 | 40.5 | 0.058 |
| m2022 | 460 | 38.7 | 0.024 | 317 | 36.3 | -0.034 |
| ma_cross | 1734 | 36.5 | -0.04 | 1158 | 38.6 | 0.012 |
| macd_div | 303 | 39.3 | 0.054 | 1110 | 35.3 | -0.057 |
| msb_ob | 972 | 38.1 | 0.005 | 942 | 37.3 | -0.017 |
| ob | 800 | 37.9 | -0.005 | 763 | 35.9 | -0.052 |
| ohl_break | 471 | 36.9 | -0.051 | 292 | 38.7 | -0.008 |
| ohl_open | 1756 | 37.5 | -0.026 | 1419 | 35.5 | -0.07 |
| orb | 145 | 38.6 | -0.018 | 70 | 37.1 | -0.071 |
| ote | 387 | 35.7 | -0.057 | 460 | 44.6 | 0.15 |
| po3 | 69 | 43.5 | 0.116 | 78 | 38.5 | 0.002 |
| rsi_div | 337 | 39.2 | 0.06 | 875 | 36.9 | -0.02 |
| sess_amd | 333 | 44.7 | 0.162 | 324 | 41.7 | 0.069 |
| sma1040 | 19 | 42.1 | 0.168 | 30 | 60.0 | 0.708 |
| smt | 963 | 35.8 | -0.059 | 898 | 37.8 | -0.005 |
| sweep | 1639 | 37.6 | 0.002 | 2007 | 38.3 | 0.004 |
| tlbreak | 1074 | 37.2 | -0.045 | 1153 | 38.2 | 0.016 |
| turtle55 | 62 | 41.9 | 0.183 | 17 | 47.1 | 0.321 |
| unicorn | 231 | 33.8 | -0.091 | 242 | 32.2 | -0.112 |
| vwap | 5877 | 36.3 | -0.045 | 1445 | 35.4 | -0.063 |
| wavec | 44 | 36.4 | 0.046 | 89 | 46.1 | 0.21 |
| zombie | 502 | 36.5 | -0.036 | 400 | 37.5 | -0.026 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7402 | 33.3 | -0.021 |
| Mon | 7658 | 38.7 | -0.009 |
| Sat | 6426 | 34.0 | -0.087 |
| Sun | 6697 | 39.6 | 0.01 |
| Thu | 7313 | 37.4 | 0.005 |
| Tue | 7564 | 37.8 | -0.026 |
| Wed | 19659 | 38.3 | -0.017 |
| Asia 00-07 | 16155 | 37.9 | -0.021 |
| Late 20-24 | 6133 | 36.9 | -0.008 |
| London 07-12 | 14532 | 39.1 | 0.001 |
| New York 12-20 | 22608 | 36.3 | -0.04 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 62719 | 37.3 | -0.019 | -0.014 | -0.79 | 26740 | -0.012 | 35979 | -0.024 |  |
| grade A+++ | 485 | 34.6 | -0.04 | -0.122 | +1.25 | 240 | -0.042 | 245 | -0.037 |  |
| grade A+ | 9671 | 36.8 | -0.016 | -0.045 | +1.85 | 3677 | -0.033 | 5994 | -0.006 |  |
| grade A | 21849 | 36.6 | -0.031 | -0.015 | -1.55 | 8995 | -0.015 | 12854 | -0.043 |  |
| grade B | 20534 | 37.7 | -0.013 | -0.012 | -0.08 | 9056 | -0.002 | 11478 | -0.022 |  |
| grade C | 10180 | 38.5 | -0.008 | 0.017 | -1.56 | 4772 | -0.011 | 5408 | -0.005 |  |
| layer htf | 37279 | 37.0 | -0.026 | -0.006 | -2.45 | 15760 | -0.036 | 21519 | -0.019 |  |
| layer loc | 13664 | 38.9 | 0.023 | -0.007 | +2.25 | 5904 | 0.02 | 7760 | 0.026 |  |
| layer vol | 19041 | 37.5 | -0.019 | -0.052 | +2.93 | 7934 | -0.001 | 11107 | -0.033 |  |
| layer reg | 46137 | 36.2 | -0.031 | -0.035 | +0.56 | 19583 | -0.017 | 26554 | -0.042 |  |
| layer time | 40431 | 37.1 | -0.02 | -0.013 | -0.98 | 15948 | -0.012 | 24483 | -0.025 |  |
| no htf | 25440 | 37.7 | -0.009 | -0.026 | +1.74 | 10980 | 0.023 | 14460 | -0.033 |  |
| no loc | 49055 | 36.8 | -0.031 | -0.016 | -2.10 | 20836 | -0.021 | 28219 | -0.038 |  |
| no vol | 43678 | 37.2 | -0.019 | 0.002 | -2.86 | 18806 | -0.017 | 24872 | -0.021 |  |
| no reg | 16582 | 40.2 | 0.015 | 0.045 | -2.41 | 7157 | 0.0 | 9425 | 0.026 |  |
| no time | 22288 | 37.6 | -0.017 | -0.017 | -0.02 | 10792 | -0.012 | 11496 | -0.022 |  |
| grade C / m2022 | 68 | 51.5 | 0.339 | 0.008 | +1.64 | 30 | 0.36 | 38 | 0.323 |  |
| grade C / wavec | 31 | 48.4 | 0.265 | 0.007 | +0.98 | 17 | -0.265 | 14 | 0.907 |  |
| grade A+ / sess_amd | 122 | 45.9 | 0.204 | -0.122 | +2.47 | 62 | 0.245 | 60 | 0.163 |  |
| grade A+++ / ob | 32 | 46.9 | 0.2 | 0.225 | -0.10 | 16 | 0.305 | 16 | 0.094 |  |
| grade B / sess_amd | 176 | 46.0 | 0.183 | 0.008 | +1.43 | 100 | 0.249 | 76 | 0.096 |  |
| grade C / ote | 129 | 46.5 | 0.182 | 0.074 | +0.75 | 55 | 0.291 | 74 | 0.1 |  |
| grade B / wavec | 40 | 45.0 | 0.174 | -0.041 | +0.83 | 23 | 0.341 | 17 | -0.053 |  |
| grade A+ / macd_div | 159 | 44.0 | 0.167 | -0.001 | +1.47 | 70 | 0.399 | 89 | -0.015 |  |
| grade A+ / ew_r2_d1 | 81 | 40.7 | 0.165 | 0.011 | +0.94 | 26 | 0.482 | 55 | 0.015 |  |
| grade A+ / ew_r3_v | 43 | 41.9 | 0.152 | 0.158 | -0.04 | 17 | 0.275 | 26 | 0.071 |  |
| grade C / donch | 294 | 44.9 | 0.14 | -0.009 | +1.54 | 158 | 0.058 | 136 | 0.236 |  |
| grade A+ / ew_r2_d2 | 43 | 34.9 | 0.137 | 0.151 | -0.08 | 12 | 0.179 | 31 | 0.12 |  |
| grade A / po3 | 65 | 44.6 | 0.115 | -0.121 | +1.09 | 28 | 0.161 | 37 | 0.081 |  |
| grade B / ote | 273 | 43.6 | 0.111 | -0.063 | +1.72 | 123 | 0.021 | 150 | 0.185 |  |
| grade A / ew_r3_v | 158 | 40.5 | 0.109 | -0.196 | +2.33 | 70 | 0.225 | 88 | 0.017 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8451 | 4013 | 47.5 |
| sweep | vwap | 6425 | 3867 | 60.2 |
| ema_stack | sweep | 3267 | 2393 | 73.2 |
| ema_stack | level | 4096 | 2050 | 50.0 |
| fvg | vwap | 4775 | 1947 | 40.8 |
| ohl_open | vwap | 4075 | 1753 | 43.0 |
| macd_div | vwap | 2160 | 1679 | 77.7 |
| level | sweep | 3697 | 1586 | 42.9 |
| msb_ob | vwap | 2798 | 1585 | 56.6 |
| fib | vwap | 3079 | 1524 | 49.5 |
| ob | vwap | 2501 | 1484 | 59.3 |
| fvg | level | 3473 | 1453 | 41.8 |
| rsi_div | vwap | 1848 | 1398 | 75.6 |
| ma_cross | sweep | 2094 | 1307 | 62.4 |
| smt | vwap | 3014 | 1307 | 43.4 |
| level | ma_cross | 2668 | 1305 | 48.9 |
| tlbreak | vwap | 2628 | 1239 | 47.1 |
| ma_cross | vwap | 4335 | 1237 | 28.5 |
| level | ohl_open | 2406 | 1214 | 50.5 |
| liqline | vwap | 3397 | 1190 | 35.0 |
| judas | level | 2520 | 1162 | 46.1 |
| judas | vwap | 3776 | 1076 | 28.5 |
| fvg | ohl_open | 1294 | 1060 | 81.9 |
| fvg | sweep | 1775 | 1039 | 58.5 |
| level | liqline | 1873 | 957 | 51.1 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 34 | 50.0 | 0.347 |
| 2 families | 424 | 36.3 | -0.039 |
| 2 families (with opposition) | 1447 | 37.1 | -0.022 |
| 3 families | 1307 | 35.0 | -0.067 |
| 3 families (with opposition) | 4853 | 37.2 | -0.027 |
| 4+ families | 876 | 36.1 | -0.066 |
| 4+ families (with opposition) | 3837 | 36.5 | -0.037 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 81.8 | 27899 | 81.5 | 386335 | +1.2 |
| 1m shapes 120/180/240/360 deg | 77.8 | 12586 | 78.2 | 12332 | -1.1 |
| 15m | 65.0 | 20012 | 64.7 | 277110 | +1.1 |
| 15m shapes 120/180/240/360 deg | 64.2 | 10180 | 63.7 | 10166 | +0.9 |
| 1h | 59.3 | 16713 | 59.1 | 231199 | +0.6 |
| 1h shapes 120/180/240/360 deg | 58.8 | 9132 | 59.6 | 9141 | -1.5 |
| 4h | 56.9 | 11938 | 58.0 | 164451 | -2.5 |
| 4h shapes 120/180/240/360 deg | 56.9 | 6760 | 56.6 | 6758 | +0.4 |
| 1d | 55.9 | 2955 | 56.4 | 39786 | -0.6 |
| 1d shapes 120/180/240/360 deg | 57.6 | 1878 | 57.7 | 1875 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 59 | 10.2 | -0.479 | -0.468 | -0.08 |
| 1d | 47 | 40.4 | -0.006 | +0.352 | -1.31 |
| 1h | 137 | 24.1 | -0.214 | -0.036 | -0.94 |
| 4h | 98 | 29.6 | -0.054 | +0.106 | -0.78 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2133 | -0.088 |
| 15 days around full moon | 2178 | 0.055 |

Difference t = -1.71 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 62719 | 48.4 | -0.032 | -0.132 | -1983.7 | -7.99 |
| rr1.5 | 62719 | 39.8 | -0.019 | -0.119 | -1206.0 | -4.02 |
| rr2.0 | 62719 | 34.7 | -0.006 | -0.106 | -387.3 | -1.13 |
| rr3.0 | 62719 | 29.0 | 0.003 | -0.097 | 183.9 | +0.45 |
| rr1.5_be | 62719 | 33.9 | -0.018 | -0.118 | -1134.0 | -4.07 |
| rr2.0_be | 62719 | 27.1 | -0.001 | -0.101 | -74.6 | -0.24 |
| rr1.5_h16 | 62719 | 41.4 | -0.015 | -0.115 | -937.4 | -3.32 |
| rr2.0_h16 | 62719 | 38.2 | -0.001 | -0.101 | -81.7 | -0.26 |
