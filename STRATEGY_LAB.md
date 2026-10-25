# Strategy lab - real candles (2026-10-25)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 48 | 54.2 | 0.548 | 0.448 | 37.5 | 0.141 |  |
| 2 | wavec | Elliott wave | 122 | 45.9 | 0.251 | 0.151 | 35.2 | -0.051 |  |
| 3 | turtle55 | Trend (hedge fund) | 76 | 44.7 | 0.242 | 0.142 | 42.1 | 0.17 |  |
| 4 | kzs | Time (sessions) | 37 | 45.9 | 0.149 | 0.049 | 37.8 | -0.054 |  |
| 5 | orb | Time (sessions) | 210 | 43.8 | 0.123 | 0.023 | 44.3 | 0.135 |  |
| 6 | ew_r3_d2 | Elliott wave | 97 | 36.1 | 0.055 | -0.045 | 28.9 | -0.187 |  |
| 7 | ote | Fibonacci | 796 | 39.1 | 0.037 | -0.063 | 38.2 | 0.019 |  |
| 8 | abc | Elliott wave | 108 | 38.0 | 0.03 | -0.07 | 43.5 | 0.136 |  |
| 9 | ew_r2_d2 | Elliott wave | 288 | 36.8 | 0.027 | -0.073 | 34.0 | -0.042 |  |
| 10 | breaker | SMC / ICT | 409 | 38.1 | 0.025 | -0.075 | 37.4 | 0.02 |  |
| 11 | rsi_div | Momentum / divergence | 1163 | 37.4 | 0.014 | -0.086 | 36.1 | -0.017 |  |
| 12 | breakout | Levels / breakouts | 972 | 39.1 | 0.008 | -0.092 | 38.3 | -0.009 |  |
| 13 | msb_ob | SMC / ICT | 1905 | 37.6 | -0.001 | -0.101 | 36.1 | -0.038 |  |
| 14 | ohl_break | Levels / breakouts | 741 | 38.9 | -0.002 | -0.102 | 37.9 | -0.017 |  |
| 15 | ew5 | Elliott wave | 169 | 34.9 | -0.003 | -0.103 | 37.9 | 0.045 |  |
| 16 | fvg | SMC / ICT | 3283 | 37.6 | -0.004 | -0.104 | 38.2 | 0.013 |  |
| 17 | macd_div | Momentum / divergence | 1375 | 36.6 | -0.004 | -0.104 | 36.9 | -0.003 |  |
| 18 | liqline | Liquidity | 2685 | 37.7 | -0.005 | -0.105 | 37.8 | -0.011 |  |
| 19 | sweep | Liquidity | 3451 | 37.3 | -0.007 | -0.107 | 38.2 | 0.013 |  |
| 20 | fib | Fibonacci | 2305 | 36.9 | -0.009 | -0.109 | 37.0 | -0.01 |  |
| 21 | level | Levels / breakouts | 5144 | 37.7 | -0.01 | -0.11 | 37.6 | -0.012 |  |
| 22 | ew_r3_v | Elliott wave | 301 | 35.2 | -0.011 | -0.111 | 30.9 | -0.14 |  |
| 23 | ma_cross | Trend (MA) | 2934 | 37.2 | -0.012 | -0.112 | 36.9 | -0.022 |  |
| 24 | ew_r2_d1 | Elliott wave | 507 | 35.9 | -0.015 | -0.115 | 34.7 | -0.04 |  |
| 25 | vwap | Trend (MA) | 7285 | 36.9 | -0.022 | -0.122 | 37.3 | -0.014 |  |
| 26 | cisd | SMC / ICT | 972 | 36.4 | -0.023 | -0.123 | 36.3 | -0.024 |  |
| 27 | sess_amd | Time (sessions) | 475 | 38.3 | -0.023 | -0.123 | 38.1 | -0.032 |  |
| 28 | ob | SMC / ICT | 1719 | 36.5 | -0.025 | -0.125 | 35.5 | -0.046 |  |
| 29 | crt | Liquidity | 927 | 36.5 | -0.025 | -0.125 | 37.0 | -0.016 |  |
| 30 | ohl_open | Levels / breakouts | 3081 | 37.0 | -0.027 | -0.127 | 37.2 | -0.019 |  |
| 31 | zombie | Liquidity | 856 | 36.7 | -0.028 | -0.128 | 37.6 | 0.005 |  |
| 32 | donch | Trend (hedge fund) | 2704 | 36.6 | -0.033 | -0.133 | 37.3 | -0.017 |  |
| 33 | judas | Time (sessions) | 2520 | 37.5 | -0.033 | -0.133 | 37.9 | -0.027 |  |
| 34 | smt | Intermarket (SMT) | 1718 | 36.4 | -0.037 | -0.137 | 37.9 | -0.002 |  |
| 35 | m2022 | SMC / ICT | 641 | 35.6 | -0.039 | -0.139 | 35.6 | -0.031 |  |
| 36 | po3 | Time (sessions) | 144 | 37.5 | -0.04 | -0.14 | 43.1 | 0.087 |  |
| 37 | unicorn | SMC / ICT | 425 | 34.8 | -0.041 | -0.141 | 41.6 | 0.131 |  |
| 38 | ema_stack | Trend (MA) | 4776 | 36.3 | -0.044 | -0.144 | 38.8 | 0.024 |  |
| 39 | tlbreak | Levels / breakouts | 2130 | 35.5 | -0.054 | -0.154 | 37.4 | -0.005 |  |
| 40 | ew_r2_v | Elliott wave | 894 | 33.0 | -0.079 | -0.179 | 34.8 | -0.035 |  |
| 41 | ew3 | Elliott wave | 935 | 35.3 | -0.085 | -0.185 | 39.7 | 0.034 |  |
| 42 | ew_r3_d1 | Elliott wave | 209 | 30.1 | -0.088 | -0.188 | 34.4 | -0.038 |  |

## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Momentum / divergence | 2538 | 0.004 |
| 2 | Fibonacci | 3101 | 0.003 |
| 3 | Liquidity | 7919 | -0.011 |
| 4 | SMC / ICT | 9354 | -0.012 |
| 5 | Trend (hedge fund) | 2828 | -0.016 |
| 6 | Levels / breakouts | 12068 | -0.02 |
| 7 | Time (sessions) | 3386 | -0.02 |
| 8 | Trend (MA) | 14995 | -0.027 |
| 9 | Elliott wave | 3630 | -0.037 |
| 10 | Intermarket (SMT) | 1718 | -0.037 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| abc | 15m | 33 | 39.4 | 0.011 | -0.089 |
| breaker | 1m | 30 | 50.0 | 0.25 | 0.15 |
| breakout | 1d | 46 | 45.7 | 0.227 | 0.127 |
| cisd | 1h | 250 | 37.6 | 0.02 | -0.08 |
| crt | 1h | 168 | 41.7 | 0.095 | -0.005 |
| donch | 1d | 146 | 35.6 | 0.046 | -0.054 |
| ema_stack | 1d | 262 | 36.6 | 0.073 | -0.027 |
| ew3 | 1m | 149 | 37.6 | -0.051 | -0.151 |
| ew5 | 1h | 31 | 41.9 | 0.198 | 0.098 |
| ew_r2_d1 | 1h | 151 | 40.4 | 0.081 | -0.019 |
| ew_r2_d2 | 1h | 76 | 44.7 | 0.196 | 0.096 |
| ew_r2_v | 1m | 74 | 39.2 | 0.027 | -0.073 |
| ew_r3_d1 | 15m | 40 | 35.0 | -0.003 | -0.103 |
| ew_r3_d2 | 4h | 49 | 42.9 | 0.131 | 0.031 |
| ew_r3_v | 4h | 81 | 38.3 | 0.023 | -0.077 |
| fib | 15m | 664 | 40.8 | 0.054 | -0.046 |
| fvg | 1d | 108 | 39.8 | 0.145 | 0.045 |
| judas | 1h | 624 | 39.9 | 0.021 | -0.079 |
| level | 4h | 842 | 38.6 | 0.032 | -0.068 |
| liqline | 1d | 139 | 38.1 | 0.192 | 0.092 |
| m2022 | 1d | 70 | 48.6 | 0.362 | 0.262 |
| ma_cross | 1d | 128 | 43.0 | 0.222 | 0.122 |
| macd_div | 1d | 67 | 50.7 | 0.409 | 0.309 |
| msb_ob | 1m | 377 | 45.6 | 0.199 | 0.099 |
| ob | 1m | 368 | 42.4 | 0.127 | 0.027 |
| ohl_break | 1d | 41 | 53.7 | 0.448 | 0.348 |
| ohl_open | 1h | 880 | 40.1 | 0.052 | -0.048 |
| orb | 15m | 202 | 43.1 | 0.101 | 0.001 |
| ote | 4h | 174 | 44.8 | 0.198 | 0.098 |
| po3 | 15m | 68 | 39.7 | 0.008 | -0.092 |
| rsi_div | 1m | 141 | 42.6 | 0.122 | 0.022 |
| sess_amd | 15m | 250 | 38.8 | -0.008 | -0.108 |
| sma1040 | 1d | 48 | 54.2 | 0.548 | 0.448 |
| smt | 1m | 249 | 41.8 | 0.087 | -0.013 |
| sweep | 4h | 841 | 40.0 | 0.095 | -0.005 |
| tlbreak | 1m | 285 | 43.2 | 0.101 | 0.001 |
| turtle55 | 1d | 76 | 44.7 | 0.242 | 0.142 |
| unicorn | 1m | 31 | 48.4 | 0.237 | 0.137 |
| vwap | 1d | 390 | 33.6 | 0.022 | -0.078 |
| wavec | 15m | 31 | 51.6 | 0.29 | 0.19 |
| zombie | 1d | 53 | 43.4 | 0.227 | 0.127 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 54 | -0.016 | 54 | 0.075 |
| breaker | 210 | -0.084 | 199 | 0.139 |
| breakout | 482 | -0.005 | 490 | 0.021 |
| cisd | 484 | -0.114 | 488 | 0.067 |
| crt | 444 | -0.1 | 483 | 0.044 |
| donch | 1313 | -0.055 | 1391 | -0.013 |
| ema_stack | 2413 | -0.088 | 2363 | 0.002 |
| ew3 | 479 | -0.06 | 456 | -0.111 |
| ew5 | 78 | -0.109 | 91 | 0.089 |
| ew_r2_d1 | 227 | -0.021 | 280 | -0.01 |
| ew_r2_d2 | 120 | 0.021 | 168 | 0.032 |
| ew_r2_v | 434 | -0.043 | 460 | -0.113 |
| ew_r3_d1 | 93 | -0.072 | 116 | -0.101 |
| ew_r3_d2 | 37 | -0.009 | 60 | 0.095 |
| ew_r3_v | 141 | -0.028 | 160 | 0.004 |
| fib | 1108 | -0.029 | 1197 | 0.009 |
| fvg | 1871 | -0.021 | 1412 | 0.019 |
| judas | 1199 | -0.091 | 1321 | 0.021 |
| kzs | 22 | 0.477 | 15 | -0.333 |
| level | 3483 | -0.011 | 1661 | -0.008 |
| liqline | 1268 | 0.006 | 1417 | -0.014 |
| m2022 | 313 | -0.137 | 328 | 0.055 |
| ma_cross | 1489 | -0.0 | 1445 | -0.025 |
| macd_div | 687 | 0.006 | 688 | -0.014 |
| msb_ob | 1030 | -0.008 | 875 | 0.007 |
| ob | 875 | -0.07 | 844 | 0.022 |
| ohl_break | 339 | 0.028 | 402 | -0.026 |
| ohl_open | 1454 | -0.051 | 1627 | -0.005 |
| orb | 91 | 0.121 | 119 | 0.126 |
| ote | 383 | -0.047 | 413 | 0.114 |
| po3 | 77 | -0.016 | 67 | -0.067 |
| rsi_div | 574 | -0.003 | 589 | 0.03 |
| sess_amd | 195 | -0.034 | 280 | -0.015 |
| sma1040 | 20 | 0.764 | 28 | 0.394 |
| smt | 858 | -0.033 | 860 | -0.041 |
| sweep | 1868 | -0.021 | 1583 | 0.009 |
| tlbreak | 1061 | -0.098 | 1069 | -0.01 |
| turtle55 | 45 | 0.081 | 31 | 0.477 |
| unicorn | 221 | -0.223 | 204 | 0.157 |
| vwap | 3723 | -0.039 | 3562 | -0.003 |
| wavec | 53 | 0.045 | 69 | 0.409 |
| zombie | 416 | -0.072 | 440 | 0.013 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 36035 | 36.7 | -0.026 | 25110 | 37.4 | -0.007 |
| abc | 36 | 41.7 | 0.11 | 72 | 36.1 | -0.011 |
| breaker | 185 | 41.1 | 0.069 | 223 | 35.9 | -0.008 |
| breakout | 664 | 39.3 | 0.006 | 303 | 38.9 | 0.023 |
| cisd | 387 | 35.9 | -0.034 | 579 | 36.8 | -0.014 |
| crt | 357 | 35.9 | -0.031 | 565 | 36.6 | -0.025 |
| donch | 2332 | 36.7 | -0.032 | 361 | 36.8 | -0.036 |
| ema_stack | 3833 | 36.1 | -0.045 | 910 | 37.1 | -0.039 |
| ew3 | 582 | 35.7 | -0.065 | 350 | 34.9 | -0.109 |
| ew5 | 132 | 35.6 | 0.026 | 35 | 34.3 | -0.054 |
| ew_r2_d1 | 297 | 35.0 | -0.013 | 210 | 37.1 | -0.018 |
| ew_r2_d2 | 146 | 34.9 | 0.006 | 142 | 38.7 | 0.05 |
| ew_r2_v | 555 | 32.3 | -0.077 | 337 | 34.1 | -0.085 |
| ew_r3_d1 | 171 | 32.7 | -0.054 | 38 | 18.4 | -0.242 |
| ew_r3_d2 | 81 | 37.0 | 0.076 | 16 | 31.2 | -0.05 |
| ew_r3_v | 256 | 35.9 | 0.002 | 45 | 31.1 | -0.082 |
| fib | 1158 | 36.1 | -0.03 | 1134 | 37.6 | 0.004 |
| fvg | 1857 | 36.2 | -0.037 | 1375 | 39.3 | 0.036 |
| judas | 1535 | 37.4 | -0.029 | 968 | 37.5 | -0.042 |
| kzs | 11 | 18.2 | -0.545 | 26 | 57.7 | 0.442 |
| level | 2555 | 37.7 | -0.021 | 2534 | 37.7 | 0.0 |
| liqline | 1513 | 37.9 | -0.005 | 1152 | 37.8 | 0.006 |
| m2022 | 370 | 37.6 | 0.024 | 268 | 32.8 | -0.124 |
| ma_cross | 1740 | 35.7 | -0.049 | 1165 | 39.6 | 0.046 |
| macd_div | 290 | 39.0 | 0.061 | 1081 | 36.0 | -0.02 |
| msb_ob | 943 | 37.1 | -0.014 | 943 | 37.6 | -0.004 |
| ob | 913 | 36.3 | -0.044 | 783 | 36.7 | -0.012 |
| ohl_break | 436 | 39.7 | 0.011 | 296 | 38.5 | 0.002 |
| ohl_open | 1696 | 35.8 | -0.063 | 1375 | 38.7 | 0.023 |
| orb | 129 | 45.7 | 0.162 | 81 | 40.7 | 0.061 |
| ote | 355 | 34.9 | -0.067 | 436 | 42.2 | 0.113 |
| po3 | 74 | 39.2 | 0.001 | 69 | 34.8 | -0.106 |
| rsi_div | 317 | 38.5 | 0.053 | 843 | 37.0 | -0.0 |
| sess_amd | 225 | 41.3 | 0.05 | 250 | 35.6 | -0.088 |
| sma1040 | 18 | 44.4 | 0.279 | 30 | 60.0 | 0.71 |
| smt | 887 | 33.6 | -0.102 | 829 | 39.6 | 0.035 |
| sweep | 1559 | 36.7 | -0.02 | 1883 | 37.9 | 0.004 |
| tlbreak | 1008 | 37.0 | -0.034 | 1118 | 34.2 | -0.071 |
| turtle55 | 61 | 42.6 | 0.189 | 15 | 53.3 | 0.46 |
| unicorn | 193 | 35.8 | -0.033 | 230 | 33.5 | -0.06 |
| vwap | 5693 | 37.0 | -0.014 | 1551 | 36.4 | -0.052 |
| wavec | 31 | 35.5 | 0.081 | 91 | 49.5 | 0.309 |
| zombie | 454 | 38.3 | 0.017 | 398 | 35.2 | -0.071 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7524 | 32.0 | -0.036 |
| Mon | 7411 | 39.0 | -0.006 |
| Sat | 15038 | 36.4 | -0.044 |
| Sun | 9376 | 37.4 | -0.024 |
| Thu | 7310 | 38.4 | 0.04 |
| Tue | 7568 | 37.6 | -0.035 |
| Wed | 7310 | 39.0 | 0.005 |
| Asia 00-07 | 15064 | 37.4 | -0.02 |
| Late 20-24 | 10875 | 37.6 | -0.009 |
| London 07-12 | 10504 | 37.7 | -0.045 |
| New York 12-20 | 21820 | 36.6 | -0.016 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 61537 | 37.0 | -0.018 | -0.008 | -1.67 | 26746 | -0.018 | 34791 | -0.019 |  |
| grade A+++ | 533 | 34.9 | -0.045 | -0.145 | +1.71 | 288 | -0.082 | 245 | -0.0 |  |
| grade A+ | 8707 | 37.2 | -0.002 | -0.02 | +1.09 | 4075 | 0.031 | 4632 | -0.031 |  |
| grade A | 20097 | 36.6 | -0.014 | -0.021 | +0.62 | 9330 | -0.01 | 10767 | -0.018 |  |
| grade B | 20980 | 36.4 | -0.04 | 0.012 | -4.76 | 8769 | -0.048 | 12211 | -0.034 |  |
| grade C | 11220 | 38.8 | 0.002 | -0.006 | +0.57 | 4284 | -0.015 | 6936 | 0.012 |  |
| layer htf | 36035 | 36.7 | -0.026 | 0.001 | -3.27 | 15578 | -0.032 | 20457 | -0.022 |  |
| layer loc | 13422 | 38.1 | 0.017 | -0.015 | +2.37 | 5984 | 0.002 | 7438 | 0.029 |  |
| layer vol | 19502 | 37.7 | -0.01 | -0.049 | +3.49 | 8502 | 0.007 | 11000 | -0.023 |  |
| layer reg | 44680 | 36.2 | -0.023 | -0.016 | -1.02 | 19518 | -0.007 | 25162 | -0.036 |  |
| layer time | 35598 | 36.7 | -0.021 | 0.0 | -2.53 | 17355 | -0.008 | 18243 | -0.033 |  |
| no htf | 25502 | 37.4 | -0.007 | -0.02 | +1.31 | 11168 | 0.003 | 14334 | -0.015 |  |
| no loc | 48115 | 36.7 | -0.028 | -0.006 | -3.12 | 20762 | -0.023 | 27353 | -0.032 |  |
| no vol | 42035 | 36.7 | -0.022 | 0.011 | -4.39 | 18244 | -0.029 | 23791 | -0.017 |  |
| no reg | 16857 | 39.3 | -0.005 | 0.013 | -1.51 | 7228 | -0.046 | 9629 | 0.025 |  |
| no time | 25939 | 37.5 | -0.015 | -0.019 | +0.37 | 9391 | -0.035 | 16548 | -0.004 |  |
| grade A / wavec | 38 | 47.4 | 0.401 | 0.013 | +1.41 | 15 | 1.0 | 23 | 0.01 |  |
| grade C / wavec | 34 | 52.9 | 0.324 | -0.191 | +2.03 | 20 | 0.375 | 14 | 0.25 |  |
| grade A / ew5 | 56 | 46.4 | 0.302 | 0.016 | +1.48 | 26 | 0.155 | 30 | 0.43 |  |
| grade C / ote | 136 | 50.0 | 0.293 | 0.119 | +1.30 | 44 | 0.193 | 92 | 0.341 |  |
| grade A+ / orb | 68 | 48.5 | 0.235 | 0.235 | +0.00 | 21 | 0.548 | 47 | 0.095 |  |
| grade A+ / ew_r3_v | 36 | 47.2 | 0.227 | -0.12 | +1.22 | 20 | 0.334 | 16 | 0.094 |  |
| grade A / ew_r3_v | 128 | 43.8 | 0.219 | -0.067 | +2.69 | 59 | 0.343 | 69 | 0.114 |  |
| grade A / po3 | 48 | 47.9 | 0.198 | -0.062 | +1.15 | 25 | 0.1 | 23 | 0.304 |  |
| grade C / breakout | 89 | 47.2 | 0.186 | 0.215 | -0.16 | 35 | 0.303 | 54 | 0.111 |  |
| grade B / breaker | 122 | 45.1 | 0.156 | 0.203 | -0.35 | 48 | 0.116 | 74 | 0.182 |  |
| grade A+ / macd_div | 132 | 43.2 | 0.116 | -0.1 | +1.63 | 73 | -0.014 | 59 | 0.277 |  |
| grade B / abc | 32 | 40.6 | 0.114 | -0.226 | +1.39 | 11 | -0.239 | 21 | 0.299 |  |
| grade A / ew_r3_d1 | 81 | 35.8 | 0.107 | -0.034 | +1.11 | 34 | 0.042 | 47 | 0.153 |  |
| grade A+ / fvg | 268 | 40.7 | 0.101 | 0.035 | +0.64 | 128 | 0.107 | 140 | 0.095 |  |
| grade A / orb | 103 | 41.7 | 0.087 | -0.01 | +0.65 | 48 | -0.021 | 55 | 0.182 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8704 | 4049 | 46.5 |
| sweep | vwap | 6093 | 3655 | 60.0 |
| ema_stack | sweep | 3130 | 2308 | 73.7 |
| ema_stack | level | 4274 | 2116 | 49.5 |
| fvg | vwap | 4932 | 2024 | 41.0 |
| macd_div | vwap | 2101 | 1650 | 78.5 |
| ohl_open | vwap | 3953 | 1639 | 41.5 |
| msb_ob | vwap | 2825 | 1600 | 56.6 |
| ob | vwap | 2768 | 1518 | 54.8 |
| fvg | level | 3692 | 1500 | 40.6 |
| judas | level | 2965 | 1497 | 50.5 |
| level | sweep | 3519 | 1494 | 42.5 |
| fib | vwap | 2945 | 1483 | 50.4 |
| level | ma_cross | 2779 | 1371 | 49.3 |
| rsi_div | vwap | 1773 | 1363 | 76.9 |
| level | ohl_open | 2417 | 1273 | 52.7 |
| ma_cross | vwap | 4375 | 1271 | 29.1 |
| judas | vwap | 4172 | 1263 | 30.3 |
| ma_cross | sweep | 2016 | 1255 | 62.3 |
| liqline | vwap | 3522 | 1251 | 35.5 |
| smt | vwap | 2789 | 1217 | 43.6 |
| tlbreak | vwap | 2481 | 1204 | 48.5 |
| fvg | ohl_open | 1289 | 1039 | 80.6 |
| judas | sweep | 1686 | 1038 | 61.6 |
| level | liqline | 1999 | 1032 | 51.6 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 19 | 31.6 | 0.019 |
| 2 families | 408 | 38.5 | 0.028 |
| 2 families (with opposition) | 1416 | 35.3 | -0.051 |
| 3 families | 1268 | 35.0 | -0.072 |
| 3 families (with opposition) | 4885 | 37.4 | -0.015 |
| 4+ families | 862 | 33.3 | -0.118 |
| 4+ families (with opposition) | 3762 | 36.3 | -0.04 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 86.4 | 36960 | 86.3 | 508941 | +0.5 |
| 1m shapes 120/180/240/360 deg | 85.5 | 14457 | 85.7 | 14541 | -0.7 |
| 15m | 65.0 | 20261 | 64.4 | 279634 | +1.8 |
| 15m shapes 120/180/240/360 deg | 63.3 | 10529 | 63.5 | 10439 | -0.4 |
| 1h | 59.6 | 16709 | 59.4 | 231589 | +0.5 |
| 1h shapes 120/180/240/360 deg | 59.3 | 9157 | 59.3 | 9201 | +0.0 |
| 4h | 57.3 | 11844 | 58.2 | 163281 | -2.1 |
| 4h shapes 120/180/240/360 deg | 57.3 | 6710 | 57.7 | 6714 | -0.8 |
| 1d | 56.0 | 2941 | 56.5 | 39563 | -0.5 |
| 1d shapes 120/180/240/360 deg | 57.5 | 1872 | 57.7 | 1874 | -0.2 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 71 | 9.9 | -0.688 | +0.082 | -2.86 |
| 1d | 61 | 44.3 | +0.151 | +0.207 | -0.22 |
| 1h | 135 | 25.2 | +0.090 | -0.179 | +1.46 |
| 4h | 87 | 32.2 | +0.026 | +0.134 | -0.56 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2145 | -0.087 |
| 15 days around full moon | 2151 | 0.053 |

Difference t = -1.67 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 61537 | 48.3 | -0.031 | -0.131 | -1927.8 | -7.86 |
| rr1.5 | 61537 | 39.9 | -0.018 | -0.118 | -1131.7 | -3.82 |
| rr2.0 | 61537 | 35.0 | -0.001 | -0.101 | -85.7 | -0.25 |
| rr3.0 | 61537 | 29.4 | 0.018 | -0.082 | 1137.2 | +2.81 |
| rr1.5_be | 61537 | 34.0 | -0.016 | -0.116 | -965.0 | -3.50 |
| rr2.0_be | 61537 | 27.4 | 0.003 | -0.097 | 162.0 | +0.53 |
| rr1.5_h16 | 61537 | 41.6 | -0.01 | -0.11 | -628.6 | -2.26 |
| rr2.0_h16 | 61537 | 38.5 | 0.004 | -0.096 | 239.0 | +0.77 |
