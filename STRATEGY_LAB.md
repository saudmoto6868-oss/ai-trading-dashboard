# Strategy lab - real candles (2026-10-17)

Symbols: BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, BNB-USDT, DOGE-USDT, HL:xyz:GOLD, HL:xyz:SP500 · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · no costs (real results are worse) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 75 | 50.7 | 0.431 | 46.7 | 0.281 |  |
| 2 | zombie | Liquidity | 614 | 42.8 | 0.129 | 43.0 | 0.127 |  |
| 3 | turtle55 | Trend (hedge fund) | 103 | 39.8 | 0.128 | 46.6 | 0.303 |  |
| 4 | abc | Elliott wave | 115 | 41.7 | 0.093 | 45.2 | 0.166 |  |
| 5 | cisd | SMC / ICT | 716 | 39.8 | 0.068 | 37.4 | 0.011 |  |
| 6 | rsi_div | Momentum / divergence | 798 | 39.7 | 0.064 | 35.6 | -0.032 |  |
| 7 | ohl_break | Levels / breakouts | 472 | 40.5 | 0.064 | 38.1 | 0.005 |  |
| 8 | macd_div | Momentum / divergence | 974 | 40.0 | 0.063 | 37.0 | -0.008 |  |
| 9 | judas | Time (sessions) | 1555 | 41.4 | 0.059 | 40.6 | 0.04 |  |
| 10 | liqline | Liquidity | 1821 | 40.1 | 0.059 | 38.1 | 0.009 |  |
| 11 | po3 | Time (sessions) | 91 | 41.8 | 0.057 | 30.8 | -0.108 |  |
| 12 | breakout | Levels / breakouts | 730 | 40.8 | 0.051 | 38.1 | 0.0 |  |
| 13 | ma_cross | Trend (MA) | 2049 | 39.1 | 0.038 | 38.6 | 0.031 |  |
| 14 | ew5 | Elliott wave | 126 | 38.9 | 0.038 | 32.5 | -0.102 |  |
| 15 | level | Levels / breakouts | 3186 | 39.3 | 0.018 | 39.9 | 0.043 |  |
| 16 | m2022 | SMC / ICT | 455 | 37.8 | 0.016 | 36.0 | -0.029 |  |
| 17 | ote | Fibonacci | 612 | 37.9 | 0.014 | 39.1 | 0.037 |  |
| 18 | sweep | Liquidity | 2770 | 37.8 | 0.01 | 39.6 | 0.052 |  |
| 19 | fib | Fibonacci | 1790 | 37.8 | 0.002 | 36.9 | -0.01 |  |
| 20 | wavec | Elliott wave | 118 | 36.4 | -0.005 | 44.9 | 0.167 |  |
| 21 | vwap | Trend (MA) | 5227 | 37.0 | -0.017 | 37.6 | 0.002 |  |
| 22 | crt | Liquidity | 666 | 36.5 | -0.019 | 37.4 | 0.011 |  |
| 23 | fvg | SMC / ICT | 2008 | 36.8 | -0.023 | 39.1 | 0.047 |  |
| 24 | tlbreak | Levels / breakouts | 1714 | 36.9 | -0.023 | 38.6 | 0.018 |  |
| 25 | sess_amd | Time (sessions) | 310 | 37.4 | -0.032 | 38.4 | -0.028 |  |
| 26 | breaker | SMC / ICT | 282 | 35.1 | -0.048 | 37.2 | 0.012 |  |
| 27 | ohl_open | Levels / breakouts | 2399 | 35.7 | -0.051 | 36.9 | -0.012 |  |
| 28 | ema_stack | Trend (MA) | 3303 | 36.0 | -0.055 | 37.6 | -0.003 |  |
| 29 | msb_ob | SMC / ICT | 1344 | 35.3 | -0.062 | 39.2 | 0.042 |  |
| 30 | donch | Trend (hedge fund) | 1895 | 35.7 | -0.064 | 41.3 | 0.086 |  |
| 31 | ob | SMC / ICT | 1011 | 34.7 | -0.075 | 37.6 | 0.006 |  |
| 32 | orb | Time (sessions) | 104 | 35.6 | -0.097 | 41.3 | 0.062 |  |
| 33 | unicorn | SMC / ICT | 343 | 31.8 | -0.131 | 37.6 | 0.013 |  |
| 34 | ew3 | Elliott wave | 755 | 33.1 | -0.137 | 37.9 | -0.003 |  |
| 35 | kzs | Time (sessions) | 22 | 63.6 | 0.591 | 27.3 | -0.318 |  |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R |
|---|---|---|---|---|
| abc | 1m | 33 | 51.5 | 0.288 |
| breaker | 1m | 50 | 46.0 | 0.15 |
| breakout | 1d | 64 | 53.1 | 0.408 |
| cisd | 1m | 161 | 49.1 | 0.244 |
| crt | 1m | 61 | 41.0 | 0.056 |
| donch | 4h | 358 | 37.4 | -0.01 |
| ema_stack | 1d | 390 | 33.1 | -0.02 |
| ew3 | 15m | 188 | 36.2 | -0.077 |
| ew5 | 1m | 33 | 45.5 | 0.136 |
| fib | 4h | 361 | 39.9 | 0.074 |
| fvg | 1d | 172 | 39.0 | 0.191 |
| judas | 4h | 63 | 39.7 | 0.118 |
| level | 4h | 519 | 40.7 | 0.067 |
| liqline | 1d | 199 | 37.2 | 0.149 |
| m2022 | 1d | 104 | 43.3 | 0.244 |
| ma_cross | 1d | 199 | 43.7 | 0.266 |
| macd_div | 1d | 114 | 45.6 | 0.307 |
| msb_ob | 4h | 257 | 37.4 | 0.002 |
| ob | 4h | 224 | 38.8 | 0.031 |
| ohl_break | 1d | 59 | 54.2 | 0.495 |
| ohl_open | 4h | 398 | 36.2 | -0.007 |
| orb | 15m | 100 | 36.0 | -0.086 |
| ote | 4h | 117 | 41.0 | 0.134 |
| po3 | 15m | 43 | 44.2 | 0.105 |
| rsi_div | 1h | 200 | 43.0 | 0.127 |
| sess_amd | 15m | 147 | 38.1 | -0.01 |
| sma1040 | 1d | 75 | 50.7 | 0.431 |
| sweep | 1m | 426 | 41.8 | 0.08 |
| tlbreak | 1d | 213 | 34.7 | 0.066 |
| turtle55 | 1d | 103 | 39.8 | 0.128 |
| unicorn | 1h | 106 | 35.8 | 0.044 |
| vwap | 15m | 1274 | 40.5 | 0.041 |
| wavec | 1m | 35 | 40.0 | 0.057 |
| zombie | 1m | 104 | 51.0 | 0.282 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| abc | 61 | 0.175 | 54 | -0.0 |
| breaker | 143 | -0.122 | 139 | 0.028 |
| breakout | 360 | 0.009 | 370 | 0.093 |
| cisd | 365 | 0.06 | 351 | 0.076 |
| crt | 327 | -0.038 | 339 | -0.002 |
| donch | 871 | -0.122 | 1024 | -0.015 |
| ema_stack | 1582 | -0.152 | 1721 | 0.035 |
| ew3 | 368 | -0.204 | 387 | -0.073 |
| ew5 | 55 | -0.273 | 71 | 0.278 |
| fib | 840 | -0.057 | 950 | 0.054 |
| fvg | 976 | -0.131 | 1032 | 0.079 |
| judas | 672 | -0.083 | 883 | 0.167 |
| kzs | 15 | 0.833 | 7 | 0.071 |
| level | 2063 | -0.016 | 1123 | 0.081 |
| liqline | 879 | 0.061 | 942 | 0.056 |
| m2022 | 222 | -0.012 | 233 | 0.043 |
| ma_cross | 1033 | -0.016 | 1016 | 0.092 |
| macd_div | 492 | 0.098 | 482 | 0.028 |
| msb_ob | 702 | -0.096 | 642 | -0.024 |
| ob | 521 | -0.108 | 490 | -0.039 |
| ohl_break | 240 | 0.041 | 232 | 0.088 |
| ohl_open | 1190 | -0.038 | 1209 | -0.064 |
| orb | 67 | -0.307 | 37 | 0.284 |
| ote | 285 | 0.003 | 327 | 0.024 |
| po3 | 48 | 0.042 | 43 | 0.075 |
| rsi_div | 414 | 0.021 | 384 | 0.111 |
| sess_amd | 115 | 0.022 | 195 | -0.063 |
| sma1040 | 33 | 0.457 | 42 | 0.41 |
| sweep | 1477 | -0.017 | 1293 | 0.04 |
| tlbreak | 883 | -0.057 | 831 | 0.013 |
| turtle55 | 63 | 0.169 | 40 | 0.065 |
| unicorn | 165 | -0.175 | 178 | -0.091 |
| vwap | 2503 | -0.073 | 2724 | 0.035 |
| wavec | 59 | -0.161 | 59 | 0.15 |
| zombie | 298 | 0.059 | 316 | 0.195 |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| sweep | vwap | 4897 | 2972 | 60.7 |
| level | vwap | 5307 | 2537 | 47.8 |
| ema_stack | sweep | 2396 | 1838 | 76.7 |
| ohl_open | vwap | 3219 | 1415 | 44.0 |
| ema_stack | level | 2345 | 1231 | 52.5 |
| macd_div | vwap | 1493 | 1215 | 81.4 |
| fvg | vwap | 2956 | 1151 | 38.9 |
| fib | vwap | 2291 | 1115 | 48.7 |
| level | sweep | 2551 | 1070 | 41.9 |
| msb_ob | vwap | 1939 | 1067 | 55.0 |
| ma_cross | sweep | 1582 | 1033 | 65.3 |
| rsi_div | vwap | 1220 | 987 | 80.9 |
| judas | level | 1794 | 969 | 54.0 |
| tlbreak | vwap | 2019 | 955 | 47.3 |
| level | ohl_open | 1709 | 909 | 53.2 |
| ma_cross | vwap | 3113 | 897 | 28.8 |
| level | ma_cross | 1665 | 888 | 53.3 |
| liqline | vwap | 2390 | 864 | 36.2 |
| ob | vwap | 1603 | 855 | 53.3 |
| judas | vwap | 2663 | 831 | 31.2 |
| fvg | level | 1792 | 821 | 45.8 |
| fvg | ohl_open | 911 | 752 | 82.5 |
| fvg | sweep | 1215 | 748 | 61.6 |
| judas | sweep | 1191 | 747 | 62.7 |
| ohl_open | sweep | 1463 | 711 | 48.6 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 60 | 31.7 | -0.109 |
| 2 families | 430 | 37.9 | 0.026 |
| 2 families (with opposition) | 1248 | 37.5 | 0.003 |
| 3 families | 898 | 38.1 | 0.019 |
| 3 families (with opposition) | 3588 | 36.0 | -0.048 |
| 4+ families | 488 | 36.1 | -0.051 |
| 4+ families (with opposition) | 2200 | 36.2 | -0.051 |
