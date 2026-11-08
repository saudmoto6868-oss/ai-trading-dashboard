# Strategy lab - real candles (2026-11-01)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | turtle55 | Trend (hedge fund) | 77 | 49.4 | 0.324 | 0.224 | 45.5 | 0.247 |  |
| 2 | sma1040 | Trend (hedge fund) | 65 | 47.7 | 0.276 | 0.176 | 36.9 | 0.026 |  |
| 3 | ew_r3_d2 | Elliott wave | 116 | 37.9 | 0.091 | -0.009 | 32.8 | -0.038 |  |
| 4 | sess_amd | Time (sessions) | 485 | 41.4 | 0.079 | -0.021 | 41.4 | 0.077 |  |
| 5 | kzs | Time (sessions) | 35 | 42.9 | 0.071 | -0.029 | 42.9 | 0.071 |  |
| 6 | abc | Elliott wave | 84 | 40.5 | 0.068 | -0.032 | 47.6 | 0.246 |  |
| 7 | ew_r2_d2 | Elliott wave | 273 | 37.7 | 0.067 | -0.033 | 37.0 | 0.033 |  |
| 8 | ew_r2_d1 | Elliott wave | 514 | 38.3 | 0.044 | -0.056 | 33.3 | -0.081 |  |
| 9 | crt | Liquidity | 863 | 39.3 | 0.043 | -0.057 | 39.4 | 0.041 |  |
| 10 | wavec | Elliott wave | 119 | 36.1 | 0.034 | -0.066 | 37.8 | 0.06 |  |
| 11 | msb_ob | SMC / ICT | 1992 | 38.6 | 0.024 | -0.076 | 37.0 | -0.015 |  |
| 12 | ob | SMC / ICT | 1703 | 38.3 | 0.016 | -0.084 | 38.8 | 0.037 |  |
| 13 | ohl_open | Levels / breakouts | 3128 | 38.9 | 0.011 | -0.089 | 38.9 | 0.022 |  |
| 14 | ote | Fibonacci | 821 | 38.1 | 0.005 | -0.095 | 38.9 | 0.036 |  |
| 15 | level | Levels / breakouts | 5062 | 38.2 | 0.004 | -0.096 | 37.9 | -0.004 |  |
| 16 | fvg | SMC / ICT | 3165 | 37.6 | 0.004 | -0.096 | 38.2 | 0.017 |  |
| 17 | fib | Fibonacci | 2404 | 37.4 | 0.001 | -0.099 | 37.7 | 0.017 |  |
| 18 | orb | Time (sessions) | 211 | 39.3 | -0.001 | -0.101 | 40.8 | 0.028 |  |
| 19 | sweep | Liquidity | 3473 | 37.6 | -0.003 | -0.103 | 37.8 | 0.0 |  |
| 20 | vwap | Trend (MA) | 7265 | 37.5 | -0.01 | -0.11 | 37.2 | -0.012 |  |
| 21 | ew_r3_d1 | Elliott wave | 191 | 33.5 | -0.014 | -0.114 | 37.7 | 0.041 |  |
| 22 | tlbreak | Levels / breakouts | 2077 | 37.4 | -0.02 | -0.12 | 39.2 | 0.029 |  |
| 23 | cisd | SMC / ICT | 971 | 37.2 | -0.021 | -0.121 | 40.3 | 0.057 |  |
| 24 | m2022 | SMC / ICT | 662 | 36.9 | -0.024 | -0.124 | 41.1 | 0.086 |  |
| 25 | liqline | Liquidity | 2604 | 37.2 | -0.026 | -0.126 | 38.6 | 0.007 |  |
| 26 | rsi_div | Momentum / divergence | 1166 | 35.9 | -0.033 | -0.133 | 37.0 | -0.009 |  |
| 27 | smt | Intermarket (SMT) | 1717 | 36.8 | -0.033 | -0.133 | 38.6 | 0.032 |  |
| 28 | ew_r2_v | Elliott wave | 841 | 35.1 | -0.034 | -0.134 | 34.1 | -0.069 |  |
| 29 | ma_cross | Trend (MA) | 2908 | 36.6 | -0.035 | -0.135 | 39.1 | 0.038 |  |
| 30 | breakout | Levels / breakouts | 993 | 37.5 | -0.035 | -0.135 | 38.7 | -0.007 |  |
| 31 | macd_div | Momentum / divergence | 1359 | 35.8 | -0.04 | -0.14 | 37.8 | 0.0 |  |
| 32 | breaker | SMC / ICT | 419 | 34.8 | -0.04 | -0.14 | 37.2 | 0.027 |  |
| 33 | donch | Trend (hedge fund) | 2628 | 36.2 | -0.041 | -0.141 | 38.5 | 0.02 |  |
| 34 | ew5 | Elliott wave | 156 | 34.0 | -0.041 | -0.141 | 29.5 | -0.132 |  |
| 35 | ew_r3_v | Elliott wave | 314 | 33.8 | -0.041 | -0.141 | 41.4 | 0.13 |  |
| 36 | po3 | Time (sessions) | 145 | 36.6 | -0.047 | -0.147 | 38.6 | 0.009 |  |
| 37 | zombie | Liquidity | 882 | 36.5 | -0.049 | -0.149 | 37.0 | -0.03 |  |
| 38 | ema_stack | Trend (MA) | 4867 | 36.0 | -0.052 | -0.152 | 38.9 | 0.028 |  |
| 39 | judas | Time (sessions) | 2523 | 36.7 | -0.055 | -0.155 | 40.3 | 0.042 |  |
| 40 | ohl_break | Levels / breakouts | 719 | 35.3 | -0.083 | -0.183 | 42.8 | 0.116 |  |
| 41 | unicorn | SMC / ICT | 456 | 33.1 | -0.093 | -0.193 | 42.5 | 0.134 |  |
| 42 | ew3 | Elliott wave | 932 | 34.3 | -0.108 | -0.208 | 41.6 | 0.092 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Fibonacci | 3225 | 0.002 |
| 2 | SMC / ICT | 9368 | -0.001 |
| 3 | Levels / breakouts | 11979 | -0.007 |
| 4 | Liquidity | 7822 | -0.011 |
| 5 | Trend (hedge fund) | 2770 | -0.023 |
| 6 | Elliott wave | 3540 | -0.025 |
| 7 | Trend (MA) | 15040 | -0.028 |
| 8 | Time (sessions) | 3399 | -0.031 |
| 9 | Intermarket (SMT) | 1717 | -0.033 |
| 10 | Momentum / divergence | 2525 | -0.037 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| breaker | 15m | 105 | 39.0 | 0.012 | -0.088 |
| breakout | 4h | 181 | 38.7 | 0.033 | -0.067 |
| cisd | 4h | 215 | 40.0 | 0.071 | -0.029 |
| crt | 1h | 164 | 44.5 | 0.149 | 0.049 |
| donch | 1d | 151 | 41.7 | 0.159 | 0.059 |
| ema_stack | 1d | 272 | 39.7 | 0.165 | 0.065 |
| ew3 | 1d | 60 | 36.7 | -0.007 | -0.107 |
| ew5 | 1m | 31 | 41.9 | 0.099 | -0.001 |
| ew_r2_d1 | 1h | 152 | 40.8 | 0.097 | -0.003 |
| ew_r2_d2 | 4h | 122 | 41.0 | 0.128 | 0.028 |
| ew_r2_v | 4h | 200 | 34.5 | -0.003 | -0.103 |
| ew_r3_d1 | 1d | 32 | 43.8 | 0.39 | 0.29 |
| ew_r3_d2 | 4h | 53 | 35.8 | -0.036 | -0.136 |
| ew_r3_v | 15m | 90 | 34.4 | -0.047 | -0.147 |
| fib | 15m | 703 | 41.1 | 0.054 | -0.046 |
| fvg | 4h | 514 | 43.2 | 0.155 | 0.055 |
| judas | 1m | 795 | 38.2 | -0.022 | -0.122 |
| level | 1m | 1300 | 42.3 | 0.094 | -0.006 |
| liqline | 1d | 141 | 39.0 | 0.14 | 0.04 |
| m2022 | 1d | 86 | 46.5 | 0.332 | 0.232 |
| ma_cross | 1d | 134 | 40.3 | 0.145 | 0.045 |
| macd_div | 1d | 71 | 45.1 | 0.331 | 0.231 |
| msb_ob | 1m | 395 | 48.4 | 0.234 | 0.134 |
| ob | 1m | 386 | 43.0 | 0.111 | 0.011 |
| ohl_break | 1d | 52 | 44.2 | 0.184 | 0.084 |
| ohl_open | 1h | 825 | 39.2 | 0.031 | -0.069 |
| orb | 15m | 199 | 40.7 | 0.029 | -0.071 |
| ote | 15m | 242 | 43.4 | 0.102 | 0.002 |
| po3 | 15m | 75 | 42.7 | 0.091 | -0.009 |
| rsi_div | 4h | 283 | 38.2 | 0.035 | -0.065 |
| sess_amd | 15m | 242 | 44.6 | 0.132 | 0.032 |
| sma1040 | 1d | 65 | 47.7 | 0.276 | 0.176 |
| smt | 15m | 482 | 42.3 | 0.098 | -0.002 |
| sweep | 1m | 334 | 43.1 | 0.093 | -0.007 |
| tlbreak | 1d | 147 | 42.9 | 0.167 | 0.067 |
| turtle55 | 1d | 77 | 49.4 | 0.324 | 0.224 |
| unicorn | 1m | 34 | 44.1 | 0.103 | 0.003 |
| vwap | 15m | 2013 | 40.8 | 0.052 | -0.048 |
| wavec | 1h | 33 | 36.4 | 0.005 | -0.095 |
| zombie | 1d | 45 | 42.2 | 0.156 | 0.056 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 44 | -0.121 | 40 | 0.275 |
| breaker | 217 | -0.057 | 202 | -0.021 |
| breakout | 493 | -0.104 | 500 | 0.033 |
| cisd | 494 | -0.034 | 477 | -0.007 |
| crt | 408 | 0.058 | 455 | 0.029 |
| donch | 1238 | -0.045 | 1390 | -0.038 |
| ema_stack | 2336 | -0.08 | 2531 | -0.027 |
| ew3 | 490 | -0.219 | 442 | 0.016 |
| ew5 | 62 | -0.252 | 94 | 0.098 |
| ew_r2_d1 | 224 | -0.059 | 290 | 0.124 |
| ew_r2_d2 | 114 | 0.002 | 159 | 0.113 |
| ew_r2_v | 397 | -0.063 | 444 | -0.007 |
| ew_r3_d1 | 93 | -0.089 | 98 | 0.056 |
| ew_r3_d2 | 43 | -0.088 | 73 | 0.196 |
| ew_r3_v | 147 | -0.063 | 167 | -0.022 |
| fib | 1171 | -0.02 | 1233 | 0.022 |
| fvg | 1767 | -0.036 | 1398 | 0.054 |
| judas | 1378 | -0.08 | 1145 | -0.026 |
| kzs | 23 | 0.087 | 12 | 0.042 |
| level | 3447 | -0.014 | 1615 | 0.04 |
| liqline | 1276 | -0.033 | 1328 | -0.019 |
| m2022 | 333 | 0.019 | 329 | -0.068 |
| ma_cross | 1485 | -0.045 | 1423 | -0.024 |
| macd_div | 697 | -0.035 | 662 | -0.044 |
| msb_ob | 1036 | -0.041 | 956 | 0.095 |
| ob | 852 | -0.068 | 851 | 0.099 |
| ohl_break | 343 | -0.098 | 376 | -0.069 |
| ohl_open | 1552 | -0.029 | 1576 | 0.051 |
| orb | 102 | 0.185 | 109 | -0.175 |
| ote | 418 | -0.009 | 403 | 0.019 |
| po3 | 77 | -0.076 | 68 | -0.015 |
| rsi_div | 568 | -0.087 | 598 | 0.02 |
| sess_amd | 252 | 0.062 | 233 | 0.098 |
| sma1040 | 33 | 0.363 | 32 | 0.187 |
| smt | 837 | -0.039 | 880 | -0.028 |
| sweep | 1905 | -0.016 | 1568 | 0.013 |
| tlbreak | 1011 | -0.069 | 1066 | 0.028 |
| turtle55 | 44 | 0.227 | 33 | 0.452 |
| unicorn | 238 | -0.19 | 218 | 0.013 |
| vwap | 3600 | -0.034 | 3665 | 0.014 |
| wavec | 60 | -0.255 | 59 | 0.327 |
| zombie | 427 | -0.087 | 455 | -0.013 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 36512 | 36.6 | -0.03 | 24479 | 38.3 | 0.006 |
| abc | 19 | 47.4 | 0.237 | 65 | 38.5 | 0.018 |
| breaker | 189 | 33.3 | -0.083 | 229 | 36.2 | 0.001 |
| breakout | 736 | 36.8 | -0.058 | 254 | 38.6 | 0.011 |
| cisd | 376 | 36.2 | -0.058 | 587 | 38.2 | 0.01 |
| crt | 318 | 37.4 | -0.013 | 538 | 40.5 | 0.078 |
| donch | 2288 | 36.1 | -0.041 | 329 | 36.8 | -0.039 |
| ema_stack | 3985 | 35.9 | -0.051 | 858 | 36.7 | -0.053 |
| ew3 | 599 | 34.7 | -0.09 | 325 | 34.5 | -0.121 |
| ew5 | 134 | 34.3 | -0.014 | 22 | 31.8 | -0.205 |
| ew_r2_d1 | 310 | 37.7 | 0.037 | 204 | 39.2 | 0.055 |
| ew_r2_d2 | 147 | 36.1 | 0.042 | 126 | 39.7 | 0.096 |
| ew_r2_v | 535 | 35.0 | -0.028 | 302 | 34.8 | -0.056 |
| ew_r3_d1 | 153 | 34.0 | 0.01 | 38 | 31.6 | -0.112 |
| ew_r3_d2 | 97 | 37.1 | 0.088 | 19 | 42.1 | 0.107 |
| ew_r3_v | 271 | 35.8 | 0.014 | 43 | 20.9 | -0.391 |
| fib | 1212 | 36.3 | -0.017 | 1171 | 38.6 | 0.021 |
| fvg | 1828 | 36.1 | -0.022 | 1299 | 40.1 | 0.052 |
| judas | 1673 | 36.3 | -0.062 | 831 | 37.2 | -0.049 |
| kzs | 15 | 20.0 | -0.5 | 20 | 60.0 | 0.5 |
| level | 2580 | 38.1 | -0.005 | 2440 | 38.6 | 0.019 |
| liqline | 1510 | 35.7 | -0.064 | 1078 | 39.2 | 0.025 |
| m2022 | 392 | 34.7 | -0.065 | 268 | 40.3 | 0.043 |
| ma_cross | 1736 | 35.7 | -0.054 | 1148 | 38.2 | 0.003 |
| macd_div | 285 | 37.2 | -0.013 | 1070 | 35.6 | -0.046 |
| msb_ob | 1021 | 38.1 | 0.011 | 948 | 39.3 | 0.041 |
| ob | 892 | 39.2 | 0.035 | 791 | 37.5 | -0.004 |
| ohl_break | 454 | 34.8 | -0.109 | 257 | 36.2 | -0.038 |
| ohl_open | 1712 | 38.6 | 0.001 | 1397 | 39.2 | 0.021 |
| orb | 147 | 40.8 | 0.037 | 63 | 34.9 | -0.113 |
| ote | 353 | 34.8 | -0.067 | 459 | 41.2 | 0.068 |
| po3 | 65 | 35.4 | -0.067 | 79 | 36.7 | -0.051 |
| rsi_div | 318 | 34.6 | -0.05 | 845 | 36.6 | -0.023 |
| sess_amd | 202 | 42.6 | 0.112 | 279 | 40.9 | 0.062 |
| sma1040 | 28 | 39.3 | 0.032 | 37 | 54.1 | 0.461 |
| smt | 884 | 34.0 | -0.101 | 832 | 39.8 | 0.039 |
| sweep | 1553 | 36.6 | -0.027 | 1908 | 38.6 | 0.021 |
| tlbreak | 959 | 36.1 | -0.066 | 1109 | 38.5 | 0.019 |
| turtle55 | 60 | 48.3 | 0.299 | 17 | 52.9 | 0.412 |
| unicorn | 228 | 34.6 | -0.065 | 226 | 31.9 | -0.118 |
| vwap | 5743 | 37.4 | -0.007 | 1476 | 37.9 | -0.019 |
| wavec | 35 | 37.1 | 0.1 | 83 | 36.1 | 0.004 |
| zombie | 470 | 36.0 | -0.046 | 409 | 37.4 | -0.045 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7230 | 31.7 | -0.028 |
| Mon | 7461 | 37.5 | -0.034 |
| Sat | 14828 | 36.1 | -0.058 |
| Sun | 9426 | 40.0 | 0.038 |
| Thu | 7296 | 38.6 | 0.016 |
| Tue | 7596 | 38.3 | -0.013 |
| Wed | 7548 | 38.6 | -0.008 |
| Asia 00-07 | 13734 | 38.0 | -0.004 |
| Late 20-24 | 8448 | 38.3 | 0.006 |
| London 07-12 | 13936 | 38.7 | -0.004 |
| New York 12-20 | 21812 | 35.6 | -0.05 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 61385 | 37.2 | -0.016 | 0.017 | -5.31 | 26655 | -0.024 | 34730 | -0.011 |  |
| grade A+++ | 494 | 43.7 | 0.151 | 0.104 | +0.67 | 251 | 0.159 | 243 | 0.142 |  |
| grade A+ | 9180 | 34.8 | -0.061 | 0.023 | -5.31 | 4138 | -0.076 | 5042 | -0.049 |  |
| grade A | 21277 | 36.7 | -0.021 | 0.032 | -4.95 | 10011 | -0.016 | 11266 | -0.026 |  |
| grade B | 20562 | 38.2 | 0.001 | -0.009 | +0.99 | 8506 | -0.019 | 12056 | 0.016 |  |
| grade C | 9872 | 38.3 | -0.01 | 0.03 | -2.51 | 3749 | -0.01 | 6123 | -0.009 |  |
| layer htf | 36512 | 36.6 | -0.03 | 0.022 | -6.39 | 15719 | -0.028 | 20793 | -0.031 |  |
| layer loc | 13216 | 38.5 | 0.02 | 0.005 | +1.12 | 5821 | 0.041 | 7395 | 0.004 |  |
| layer vol | 18842 | 37.7 | -0.013 | 0.03 | -3.88 | 8039 | -0.031 | 10803 | -0.0 |  |
| layer reg | 44962 | 36.3 | -0.027 | 0.017 | -6.11 | 19602 | -0.033 | 25360 | -0.023 |  |
| layer time | 39203 | 36.7 | -0.025 | 0.02 | -5.75 | 18927 | -0.045 | 20276 | -0.007 |  |
| no htf | 24873 | 38.1 | 0.003 | 0.009 | -0.58 | 10936 | -0.018 | 13937 | 0.02 |  |
| no loc | 48169 | 36.9 | -0.026 | 0.02 | -6.58 | 20834 | -0.042 | 27335 | -0.015 |  |
| no vol | 42543 | 37.0 | -0.018 | 0.011 | -3.80 | 18616 | -0.021 | 23927 | -0.015 |  |
| no reg | 16423 | 39.9 | 0.014 | 0.017 | -0.24 | 7053 | 0.001 | 9370 | 0.024 |  |
| no time | 22182 | 38.1 | -0.001 | 0.012 | -1.22 | 7728 | 0.027 | 14454 | -0.016 |  |
| grade A / turtle55 | 31 | 61.3 | 0.618 | 0.416 | +0.85 | 13 | 0.414 | 18 | 0.765 |  |
| grade A+++ / ob | 46 | 58.7 | 0.467 | -0.076 | +2.22 | 27 | 0.759 | 19 | 0.053 |  |
| grade C / m2022 | 47 | 53.2 | 0.33 | 0.214 | +0.49 | 22 | 0.477 | 25 | 0.2 |  |
| no loc / sma1040 | 62 | 50.0 | 0.33 | 0.068 | +1.38 | 16 | 0.406 | 46 | 0.304 |  |
| no loc / turtle55 | 77 | 49.4 | 0.324 | 0.247 | +0.46 | 29 | 0.269 | 48 | 0.357 |  |
| grade A+ / sess_amd | 83 | 47.0 | 0.206 | 0.189 | +0.10 | 50 | 0.251 | 33 | 0.136 |  |
| grade A / ew_r3_d1 | 91 | 38.5 | 0.196 | 0.2 | -0.03 | 32 | 0.135 | 59 | 0.229 |  |
| grade A / ew_r3_v | 146 | 41.8 | 0.191 | 0.108 | +0.65 | 69 | 0.092 | 77 | 0.28 |  |
| loc / sess_amd | 157 | 45.9 | 0.187 | 0.17 | +0.13 | 81 | 0.231 | 76 | 0.14 |  |
| grade A+++ / level | 60 | 46.7 | 0.18 | 0.263 | -0.42 | 28 | 0.339 | 32 | 0.04 |  |
| grade C / msb_ob | 319 | 43.9 | 0.158 | -0.033 | +2.21 | 99 | 0.144 | 220 | 0.164 |  |
| grade C / ote | 118 | 45.8 | 0.156 | -0.11 | +1.81 | 55 | 0.091 | 63 | 0.213 |  |
| grade A / abc | 31 | 45.2 | 0.155 | 0.236 | -0.33 | 12 | 0.108 | 19 | 0.184 |  |
| grade A / ew_r3_d2 | 61 | 37.7 | 0.154 | -0.05 | +1.01 | 23 | -0.022 | 38 | 0.261 |  |
| grade A+ / unicorn | 73 | 41.1 | 0.14 | 0.058 | +0.40 | 26 | -0.135 | 47 | 0.291 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8525 | 3828 | 44.9 |
| sweep | vwap | 6129 | 3677 | 60.0 |
| ema_stack | sweep | 3128 | 2273 | 72.7 |
| ema_stack | level | 4226 | 1995 | 47.2 |
| fvg | vwap | 4676 | 1906 | 40.8 |
| msb_ob | vwap | 2917 | 1621 | 55.6 |
| macd_div | vwap | 2088 | 1617 | 77.4 |
| ohl_open | vwap | 3979 | 1597 | 40.1 |
| fib | vwap | 3057 | 1556 | 50.9 |
| ob | vwap | 2713 | 1541 | 56.8 |
| fvg | level | 3478 | 1535 | 44.1 |
| level | sweep | 3505 | 1480 | 42.2 |
| level | ma_cross | 2724 | 1354 | 49.7 |
| rsi_div | vwap | 1791 | 1345 | 75.1 |
| judas | level | 2942 | 1312 | 44.6 |
| ma_cross | sweep | 1981 | 1226 | 61.9 |
| judas | vwap | 4184 | 1215 | 29.0 |
| smt | vwap | 2746 | 1203 | 43.8 |
| liqline | vwap | 3420 | 1196 | 35.0 |
| ma_cross | vwap | 4286 | 1190 | 27.8 |
| level | ohl_open | 2388 | 1184 | 49.6 |
| tlbreak | vwap | 2433 | 1151 | 47.3 |
| judas | sweep | 1700 | 1007 | 59.2 |
| fvg | ohl_open | 1222 | 1006 | 82.3 |
| fib | level | 1953 | 1006 | 51.5 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 28 | 46.4 | 0.233 |
| 2 families | 414 | 37.4 | -0.006 |
| 2 families (with opposition) | 1369 | 35.1 | -0.07 |
| 3 families | 1370 | 35.8 | -0.039 |
| 3 families (with opposition) | 4910 | 37.7 | -0.01 |
| 4+ families | 812 | 35.7 | -0.057 |
| 4+ families (with opposition) | 3788 | 36.4 | -0.035 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 88.0 | 40537 | 88.1 | 558496 | -0.6 |
| 1m shapes 120/180/240/360 deg | 87.9 | 15418 | 87.9 | 15448 | +0.3 |
| 15m | 66.0 | 20475 | 65.3 | 282735 | +2.1 |
| 15m shapes 120/180/240/360 deg | 64.3 | 10569 | 64.4 | 10550 | -0.1 |
| 1h | 59.1 | 16583 | 59.0 | 230090 | +0.2 |
| 1h shapes 120/180/240/360 deg | 58.3 | 9102 | 58.4 | 9087 | -0.2 |
| 4h | 57.1 | 11987 | 58.0 | 165115 | -2.0 |
| 4h shapes 120/180/240/360 deg | 57.0 | 6766 | 57.5 | 6777 | -0.9 |
| 1d | 55.4 | 3114 | 56.1 | 41872 | -0.8 |
| 1d shapes 120/180/240/360 deg | 57.3 | 1998 | 57.5 | 1999 | -0.2 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 61 | 9.8 | -0.632 | -0.452 | -0.61 |
| 1d | 55 | 41.8 | +0.031 | -0.075 | +0.49 |
| 1h | 122 | 26.2 | +0.037 | -0.054 | +0.45 |
| 4h | 89 | 36.0 | +0.204 | +0.186 | +0.08 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2272 | -0.075 |
| 15 days around full moon | 2358 | 0.050 |

Difference t = -1.53 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 61385 | 47.9 | -0.036 | -0.136 | -2221.8 | -9.07 |
| rr1.5 | 61385 | 39.8 | -0.016 | -0.116 | -1004.5 | -3.39 |
| rr2.0 | 61385 | 34.8 | -0.0 | -0.1 | -15.1 | -0.04 |
| rr3.0 | 61385 | 28.9 | 0.005 | -0.095 | 332.5 | +0.82 |
| rr1.5_be | 61385 | 33.8 | -0.019 | -0.119 | -1152.1 | -4.18 |
| rr2.0_be | 61385 | 27.0 | -0.004 | -0.104 | -245.0 | -0.81 |
| rr1.5_h16 | 61385 | 41.2 | -0.014 | -0.114 | -867.2 | -3.12 |
| rr2.0_h16 | 61385 | 38.0 | -0.005 | -0.105 | -306.6 | -0.99 |
