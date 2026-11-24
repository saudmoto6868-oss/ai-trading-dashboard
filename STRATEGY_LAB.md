# Strategy lab - real candles (2026-11-22)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 53 | 60.4 | 0.632 | 0.532 | 28.3 | -0.166 | YES |
| 2 | turtle55 | Trend (hedge fund) | 89 | 47.2 | 0.307 | 0.207 | 42.7 | 0.165 |  |
| 3 | wyck | Wyckoff | 182 | 44.5 | 0.181 | 0.081 | 36.3 | -0.036 |  |
| 4 | ew_r2_d2 | Elliott wave | 299 | 43.8 | 0.181 | 0.081 | 36.8 | 0.022 |  |
| 5 | wavec | Elliott wave | 154 | 42.2 | 0.169 | 0.069 | 33.1 | -0.118 |  |
| 6 | ew_r3_v | Elliott wave | 360 | 41.4 | 0.103 | 0.003 | 36.4 | -0.025 |  |
| 7 | ew_r2_d1 | Elliott wave | 536 | 39.9 | 0.089 | -0.011 | 33.0 | -0.089 |  |
| 8 | pa_inside | Price action | 352 | 41.2 | 0.065 | -0.035 | 38.6 | -0.006 |  |
| 9 | ew_r3_d1 | Elliott wave | 251 | 38.6 | 0.056 | -0.044 | 39.0 | 0.058 |  |
| 10 | sess_amd | Time (sessions) | 498 | 40.6 | 0.052 | -0.048 | 40.6 | 0.06 |  |
| 11 | po3 | Time (sessions) | 125 | 40.8 | 0.047 | -0.053 | 40.8 | 0.091 |  |
| 12 | ote | Fibonacci | 757 | 39.9 | 0.041 | -0.059 | 40.0 | 0.055 |  |
| 13 | judas | Time (sessions) | 2562 | 40.0 | 0.039 | -0.061 | 38.7 | -0.001 |  |
| 14 | ew_r2_v | Elliott wave | 902 | 38.6 | 0.039 | -0.061 | 34.6 | -0.051 |  |
| 15 | ew5 | Elliott wave | 201 | 38.8 | 0.03 | -0.07 | 40.3 | 0.098 |  |
| 16 | vwap | Trend (MA) | 7293 | 39.2 | 0.026 | -0.074 | 37.7 | -0.002 |  |
| 17 | fib | Fibonacci | 2347 | 38.8 | 0.023 | -0.077 | 38.1 | 0.013 |  |
| 18 | fvg | SMC / ICT | 3210 | 38.8 | 0.02 | -0.08 | 38.6 | 0.025 |  |
| 19 | donch | Trend (hedge fund) | 2754 | 39.1 | 0.019 | -0.081 | 38.1 | 0.001 |  |
| 20 | m2022 | SMC / ICT | 691 | 38.1 | 0.019 | -0.081 | 35.2 | -0.051 |  |
| 21 | ob | SMC / ICT | 1685 | 38.5 | 0.017 | -0.083 | 39.5 | 0.052 |  |
| 22 | smt | Intermarket (SMT) | 1756 | 38.7 | 0.014 | -0.086 | 36.6 | -0.03 |  |
| 23 | ew_r3_d2 | Elliott wave | 152 | 34.9 | 0.014 | -0.086 | 36.2 | 0.05 |  |
| 24 | macd_div | Momentum / divergence | 1375 | 38.4 | 0.012 | -0.088 | 37.2 | -0.015 |  |
| 25 | breakout | Levels / breakouts | 1068 | 39.0 | 0.007 | -0.093 | 41.4 | 0.067 |  |
| 26 | unicorn | SMC / ICT | 409 | 37.7 | 0.003 | -0.097 | 34.7 | -0.048 |  |
| 27 | msb_ob | SMC / ICT | 1911 | 37.9 | 0.002 | -0.098 | 39.5 | 0.04 |  |
| 28 | cisd | SMC / ICT | 989 | 37.6 | -0.0 | -0.1 | 41.2 | 0.091 |  |
| 29 | rsi_div | Momentum / divergence | 1169 | 37.2 | -0.001 | -0.101 | 35.8 | -0.036 |  |
| 30 | ohl_open | Levels / breakouts | 3020 | 38.1 | -0.001 | -0.101 | 37.9 | 0.001 |  |
| 31 | dbl | Chart patterns (range) | 647 | 38.9 | -0.001 | -0.101 | 40.2 | 0.037 |  |
| 32 | ma_cross | Trend (MA) | 2804 | 38.1 | -0.003 | -0.103 | 39.3 | 0.037 |  |
| 33 | level | Levels / breakouts | 4941 | 38.0 | -0.008 | -0.108 | 38.6 | 0.008 |  |
| 34 | liqline | Liquidity | 2778 | 38.0 | -0.008 | -0.108 | 37.2 | -0.026 |  |
| 35 | tlbreak | Levels / breakouts | 2172 | 37.6 | -0.012 | -0.112 | 37.5 | -0.018 |  |
| 36 | ema_stack | Trend (MA) | 4899 | 37.2 | -0.027 | -0.127 | 38.3 | 0.008 |  |
| 37 | ohl_break | Levels / breakouts | 917 | 37.5 | -0.028 | -0.128 | 40.2 | 0.051 |  |
| 38 | sweep | Liquidity | 3571 | 36.4 | -0.029 | -0.129 | 37.0 | -0.02 |  |
| 39 | pa_engulf | Price action | 344 | 37.8 | -0.031 | -0.131 | 36.6 | -0.053 |  |
| 40 | ew3 | Elliott wave | 1026 | 37.5 | -0.033 | -0.133 | 39.3 | 0.014 |  |
| 41 | zombie | Liquidity | 903 | 36.8 | -0.033 | -0.133 | 36.0 | -0.039 |  |
| 42 | abc | Elliott wave | 119 | 35.3 | -0.041 | -0.141 | 35.3 | -0.041 |  |
| 43 | breaker | SMC / ICT | 381 | 35.7 | -0.044 | -0.144 | 36.2 | -0.029 |  |
| 44 | crt | Liquidity | 978 | 35.1 | -0.068 | -0.168 | 36.5 | -0.038 |  |
| 45 | pa_star | Price action | 49 | 34.7 | -0.087 | -0.187 | 36.7 | -0.002 |  |
| 46 | kzs | Time (sessions) | 33 | 36.4 | -0.091 | -0.191 | 54.5 | 0.364 |  |
| 47 | pa_pin | Price action | 307 | 33.2 | -0.113 | -0.213 | 37.5 | -0.018 |  |
| 48 | orb | Time (sessions) | 158 | 33.5 | -0.139 | -0.239 | 39.2 | 0.019 |  |
| 49 | rect | Chart patterns (range) | 39 | 30.8 | -0.171 | -0.271 | 23.1 | -0.423 |  |
| 50 | harm_gartley_tight | Harmonic: Gartley | 1 | 100.0 | 1.5 | 1.4 | 100.0 | 1.5 |  |
| 51 | harm_butterfly_tight | Harmonic: Butterfly | 3 | 66.7 | 0.667 | 0.567 | 100.0 | 1.5 |  |
| 52 | harm_cypher_tight | Harmonic: Cypher | 5 | 60.0 | 0.5 | 0.4 | 40.0 | 0.0 |  |
| 53 | harm_vol_butterfly | Harmonic: Butterfly (vol swings) | 17 | 52.9 | 0.46 | 0.36 | 47.1 | 0.208 |  |
| 54 | harm_butterfly | Harmonic: Butterfly | 18 | 55.6 | 0.419 | 0.319 | 55.6 | 0.419 |  |
| 55 | harm_vol_cypher | Harmonic: Cypher (vol swings) | 14 | 50.0 | 0.25 | 0.15 | 42.9 | 0.097 |  |
| 56 | harm_vol_butterfly_tight | Harmonic: Butterfly (vol swings) | 4 | 50.0 | 0.25 | 0.15 | 75.0 | 0.875 |  |
| 57 | harm_vol_cypher_tight | Harmonic: Cypher (vol swings) | 4 | 50.0 | 0.25 | 0.15 | 25.0 | -0.375 |  |
| 58 | harm_vol_gartley | Harmonic: Gartley (vol swings) | 7 | 42.9 | 0.222 | 0.122 | 42.9 | 0.222 |  |
| 59 | harm_cypher | Harmonic: Cypher | 13 | 38.5 | -0.038 | -0.138 | 38.5 | -0.038 |  |
| 60 | harm_gartley | Harmonic: Gartley | 11 | 27.3 | -0.148 | -0.248 | 9.1 | -0.57 |  |
| 61 | harm_vol_bat_tight | Harmonic: Bat (vol swings) | 3 | 33.3 | -0.167 | -0.267 | 33.3 | -0.167 |  |
| 62 | harm_vol_bat | Harmonic: Bat (vol swings) | 8 | 25.0 | -0.375 | -0.475 | 25.0 | -0.375 |  |
| 63 | harm_bat | Harmonic: Bat | 7 | 14.3 | -0.643 | -0.743 | 28.6 | -0.286 |  |
| 64 | harm_vol_crab | Harmonic: Crab (vol swings) | 2 | 0.0 | -1.0 | -1.1 | 100.0 | 1.5 |  |
| 65 | harm_crab | Harmonic: Crab | 2 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 66 | harm_bat_tight | Harmonic: Bat | 2 | 0.0 | -1.0 | -1.1 | 50.0 | 0.25 |  |

## Stop study: where should the stop sit? (same entries, target fixed at 2.25 ATR, results in ATR, cost 0.15 ATR)

| group | stop | n | target hit % | stopped % | avg ATR | net ATR | mirror avg ATR | t (net vs 0) |
|---|---|---|---|---|---|---|---|---|
| all | 1.0 ATR | 64337 | 31.0 | 66.8 | 0.039 | -0.111 | 0.05 | -18.84 |
| all | 1.5 ATR | 64337 | 38.3 | 57.5 | 0.009 | -0.141 | 0.019 | -19.82 |
| all | 2.0 ATR | 64337 | 43.7 | 49.5 | -0.0 | -0.15 | -0.009 | -18.53 |
| all | 2.5 ATR | 64337 | 47.7 | 43.2 | -0.017 | -0.167 | -0.031 | -18.55 |
| all | 3.0 ATR | 64337 | 50.4 | 38.1 | -0.041 | -0.191 | -0.052 | -19.60 |
| 1m | 1.0 ATR | 11874 | 32.8 | 65.8 | 0.084 | -0.066 | 0.169 | -4.70 |
| 1m | 1.5 ATR | 11874 | 39.6 | 58.2 | 0.024 | -0.126 | 0.098 | -7.51 |
| 1m | 2.0 ATR | 11874 | 44.8 | 51.6 | -0.022 | -0.172 | 0.023 | -8.99 |
| 1m | 2.5 ATR | 11874 | 48.7 | 46.2 | -0.063 | -0.213 | -0.025 | -10.00 |
| 1m | 3.0 ATR | 11874 | 51.6 | 42.2 | -0.12 | -0.27 | -0.067 | -11.59 |
| 15m | 1.0 ATR | 17657 | 32.0 | 67.0 | 0.054 | -0.096 | 0.05 | -8.43 |
| 15m | 1.5 ATR | 17657 | 39.5 | 58.4 | 0.018 | -0.132 | 0.02 | -9.62 |
| 15m | 2.0 ATR | 17657 | 45.8 | 50.8 | 0.016 | -0.134 | -0.006 | -8.50 |
| 15m | 2.5 ATR | 17657 | 49.9 | 45.4 | -0.014 | -0.164 | -0.04 | -9.39 |
| 15m | 3.0 ATR | 17657 | 53.1 | 40.6 | -0.041 | -0.191 | -0.078 | -9.99 |
| 1h | 1.0 ATR | 17639 | 31.1 | 66.0 | 0.05 | -0.1 | 0.027 | -8.89 |
| 1h | 1.5 ATR | 17639 | 38.4 | 56.6 | 0.024 | -0.126 | 0.006 | -9.25 |
| 1h | 2.0 ATR | 17639 | 43.7 | 49.0 | 0.005 | -0.145 | -0.016 | -9.37 |
| 1h | 2.5 ATR | 17639 | 48.0 | 42.6 | 0.003 | -0.147 | -0.029 | -8.60 |
| 1h | 3.0 ATR | 17639 | 51.0 | 37.9 | -0.014 | -0.164 | -0.025 | -8.85 |
| 4h | 1.0 ATR | 13435 | 28.2 | 69.3 | -0.045 | -0.195 | 0.0 | -15.45 |
| 4h | 1.5 ATR | 13435 | 35.9 | 58.8 | -0.06 | -0.21 | -0.016 | -13.69 |
| 4h | 2.0 ATR | 13435 | 41.4 | 48.9 | -0.037 | -0.187 | -0.002 | -10.71 |
| 4h | 2.5 ATR | 13435 | 45.1 | 41.3 | -0.031 | -0.181 | 0.001 | -9.41 |
| 4h | 3.0 ATR | 13435 | 47.3 | 34.3 | -0.028 | -0.178 | -0.012 | -8.62 |
| 1d | 1.0 ATR | 3732 | 29.9 | 63.7 | 0.069 | -0.081 | -0.036 | -3.33 |
| 1d | 1.5 ATR | 3732 | 36.1 | 50.5 | 0.095 | -0.055 | -0.048 | -1.92 |
| 1d | 2.0 ATR | 3732 | 39.4 | 40.1 | 0.098 | -0.052 | -0.11 | -1.64 |
| 1d | 2.5 ATR | 3732 | 41.4 | 32.9 | 0.081 | -0.069 | -0.124 | -2.01 |
| 1d | 3.0 ATR | 3732 | 42.3 | 27.5 | 0.037 | -0.113 | -0.151 | -3.08 |

| group | question | n | value |
|---|---|---|---|
| all | stopped at 1.5 ATR, target reached later | 46956 | 31.3 % reached it later (mirror direction 30.7 %); 73.0 % of all trades were stopped |
| all | MAE of trades that reached the target (ATR) | 39814 | p50 1.0 · p75 2.32 · p90 4.51 |
| 1m | stopped at 1.5 ATR, target reached later | 9082 | 33.7 % reached it later (mirror direction 32.2 %); 76.5 % of all trades were stopped |
| 1m | MAE of trades that reached the target (ATR) | 7888 | p50 1.03 · p75 2.68 · p90 5.25 |
| 15m | stopped at 1.5 ATR, target reached later | 13554 | 35.2 % reached it later (mirror direction 34.0 %); 76.8 % of all trades were stopped |
| 15m | MAE of trades that reached the target (ATR) | 11888 | p50 1.09 · p75 2.57 · p90 5.23 |
| 1h | stopped at 1.5 ATR, target reached later | 13143 | 33.4 % reached it later (mirror direction 34.2 %); 74.5 % of all trades were stopped |
| 1h | MAE of trades that reached the target (ATR) | 11264 | p50 1.04 · p75 2.49 · p90 4.55 |
| 4h | stopped at 1.5 ATR, target reached later | 9128 | 24.2 % reached it later (mirror direction 23.4 %); 67.9 % of all trades were stopped |
| 4h | MAE of trades that reached the target (ATR) | 7133 | p50 0.92 · p75 1.82 · p90 3.11 |
| 1d | stopped at 1.5 ATR, target reached later | 2049 | 13.3 % reached it later (mirror direction 11.9 %); 54.9 % of all trades were stopped |
| 1d | MAE of trades that reached the target (ATR) | 1641 | p50 0.68 · p75 1.23 · p90 2.01 |

Reading: a stop that is never reached only helps if the AVERAGE (net ATR) goes up, not just the target-hit share; compare with the mirror column (the opposite direction on the same bars).


## Pre-registered tests (signals after the freeze date only; docs/PREREG_2026-11-01.md)

| hypothesis | n | win % | avg R | net avg R | t vs random | net 1st half (n) | net 2nd half (n) | PASS |
|---|---|---|---|---|---|---|---|---|
| H1 sess_amd + loc | 108 | 41.7 | 0.065 | -0.035 | -0.66 | 0.307 (54) | -0.377 (54) |  |
| H2 ohl_open + Late 20-24 | 342 | 34.8 | -0.109 | -0.209 | -1.84 | -0.222 (171) | -0.196 (171) |  |

Gate: n >= 100, t > 3.0, net > 0 overall and in both time halves. Under n = 100 it is not evidence, whatever the numbers say.


## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Harmonic: Butterfly | 21 | 0.454 |
| 2 | Harmonic: Butterfly (vol swings) | 21 | 0.42 |
| 3 | Harmonic: Cypher (vol swings) | 18 | 0.25 |
| 4 | Harmonic: Gartley (vol swings) | 7 | 0.222 |
| 5 | Wyckoff | 182 | 0.181 |
| 6 | Harmonic: Cypher | 18 | 0.111 |
| 7 | Elliott wave | 4000 | 0.046 |
| 8 | Trend (hedge fund) | 2896 | 0.039 |
| 9 | Time (sessions) | 3376 | 0.032 |
| 10 | Fibonacci | 3104 | 0.027 |
| 11 | Intermarket (SMT) | 1756 | 0.014 |
| 12 | SMC / ICT | 9276 | 0.01 |
| 13 | Momentum / divergence | 2544 | 0.006 |
| 14 | Trend (MA) | 14996 | 0.003 |
| 15 | Levels / breakouts | 12118 | -0.007 |
| 16 | Chart patterns (range) | 686 | -0.011 |
| 17 | Harmonic: Gartley | 12 | -0.011 |
| 18 | Price action | 1052 | -0.025 |
| 19 | Liquidity | 8230 | -0.027 |
| 20 | Harmonic: Bat (vol swings) | 11 | -0.318 |
| 21 | Harmonic: Bat | 9 | -0.722 |
| 22 | Harmonic: Crab (vol swings) | 2 | -1.0 |
| 23 | Harmonic: Crab | 2 | -1.0 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| abc | 15m | 34 | 44.1 | 0.144 | 0.044 |
| breaker | 1m | 37 | 64.9 | 0.637 | 0.537 |
| breakout | 1d | 56 | 48.2 | 0.334 | 0.234 |
| cisd | 4h | 211 | 38.9 | 0.053 | -0.047 |
| crt | 15m | 371 | 39.9 | 0.032 | -0.068 |
| dbl | 1h | 181 | 43.1 | 0.085 | -0.015 |
| donch | 1d | 160 | 38.1 | 0.101 | 0.001 |
| ema_stack | 1d | 289 | 38.8 | 0.127 | 0.027 |
| ew3 | 1d | 64 | 39.1 | 0.096 | -0.004 |
| ew5 | 1h | 43 | 39.5 | 0.09 | -0.01 |
| ew_r2_d1 | 1h | 166 | 53.6 | 0.412 | 0.312 |
| ew_r2_d2 | 1h | 70 | 58.6 | 0.489 | 0.389 |
| ew_r2_v | 1m | 101 | 55.4 | 0.432 | 0.332 |
| ew_r3_d1 | 15m | 55 | 49.1 | 0.227 | 0.127 |
| ew_r3_d2 | 1h | 53 | 34.0 | 0.046 | -0.054 |
| ew_r3_v | 1d | 31 | 38.7 | 0.248 | 0.148 |
| fib | 4h | 502 | 39.6 | 0.057 | -0.043 |
| fvg | 1d | 122 | 41.0 | 0.164 | 0.064 |
| judas | 1m | 848 | 45.5 | 0.158 | 0.058 |
| level | 1m | 1246 | 42.9 | 0.102 | 0.002 |
| liqline | 1d | 157 | 40.8 | 0.234 | 0.134 |
| m2022 | 1d | 83 | 47.0 | 0.348 | 0.248 |
| ma_cross | 1d | 134 | 45.5 | 0.292 | 0.192 |
| macd_div | 1d | 75 | 48.0 | 0.318 | 0.218 |
| msb_ob | 1m | 388 | 42.5 | 0.107 | 0.007 |
| ob | 1m | 354 | 47.2 | 0.221 | 0.121 |
| ohl_break | 1d | 48 | 47.9 | 0.343 | 0.243 |
| ohl_open | 15m | 868 | 40.3 | 0.038 | -0.062 |
| orb | 15m | 152 | 34.2 | -0.128 | -0.228 |
| ote | 15m | 192 | 44.3 | 0.116 | 0.016 |
| pa_engulf | 15m | 88 | 44.3 | 0.108 | 0.008 |
| pa_inside | 1h | 91 | 48.4 | 0.252 | 0.152 |
| pa_pin | 1h | 77 | 41.6 | 0.126 | 0.026 |
| po3 | 15m | 62 | 43.5 | 0.1 | 0.0 |
| rsi_div | 15m | 313 | 42.2 | 0.081 | -0.019 |
| sess_amd | 1m | 68 | 45.6 | 0.191 | 0.091 |
| sma1040 | 1d | 53 | 60.4 | 0.632 | 0.532 |
| smt | 1m | 319 | 42.6 | 0.113 | 0.013 |
| sweep | 1m | 461 | 38.6 | 0.003 | -0.097 |
| tlbreak | 1d | 152 | 38.2 | 0.116 | 0.016 |
| turtle55 | 1d | 89 | 47.2 | 0.307 | 0.207 |
| unicorn | 15m | 86 | 48.8 | 0.266 | 0.166 |
| vwap | 1m | 1253 | 41.7 | 0.065 | -0.035 |
| wavec | 1h | 36 | 58.3 | 0.472 | 0.372 |
| wyck | 1h | 51 | 52.9 | 0.338 | 0.238 |
| zombie | 1d | 55 | 45.5 | 0.264 | 0.164 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 71 | -0.157 | 48 | 0.131 |
| breaker | 194 | -0.034 | 187 | -0.053 |
| breakout | 490 | -0.002 | 578 | 0.014 |
| cisd | 533 | -0.063 | 456 | 0.073 |
| crt | 512 | -0.135 | 466 | 0.006 |
| dbl | 300 | -0.001 | 347 | -0.001 |
| donch | 1075 | -0.056 | 1679 | 0.067 |
| ema_stack | 2184 | -0.135 | 2715 | 0.059 |
| ew3 | 519 | -0.168 | 507 | 0.106 |
| ew5 | 68 | -0.063 | 133 | 0.078 |
| ew_r2_d1 | 195 | -0.023 | 341 | 0.154 |
| ew_r2_d2 | 114 | 0.146 | 185 | 0.203 |
| ew_r2_v | 387 | -0.013 | 515 | 0.078 |
| ew_r3_d1 | 84 | -0.132 | 167 | 0.151 |
| ew_r3_d2 | 44 | -0.095 | 108 | 0.058 |
| ew_r3_v | 138 | -0.1 | 222 | 0.228 |
| fib | 1131 | -0.075 | 1216 | 0.114 |
| fvg | 1679 | -0.002 | 1531 | 0.044 |
| harm_bat | 6 | -0.583 | 1 | -1.0 |
| harm_bat_tight | 1 | -1.0 | 1 | -1.0 |
| harm_butterfly | 11 | 0.185 | 7 | 0.786 |
| harm_butterfly_tight | 2 | 0.25 | 1 | 1.5 |
| harm_crab | 2 | -1.0 | 0 | None |
| harm_cypher | 4 | -1.0 | 9 | 0.389 |
| harm_cypher_tight | 1 | -1.0 | 4 | 0.875 |
| harm_gartley | 5 | -0.5 | 6 | 0.145 |
| harm_gartley_tight | 0 | None | 1 | 1.5 |
| harm_vol_bat | 6 | -1.0 | 2 | 1.5 |
| harm_vol_bat_tight | 2 | -1.0 | 1 | 1.5 |
| harm_vol_butterfly | 14 | 0.237 | 3 | 1.5 |
| harm_vol_butterfly_tight | 3 | -0.167 | 1 | 1.5 |
| harm_vol_crab | 2 | -1.0 | 0 | None |
| harm_vol_cypher | 5 | -0.5 | 9 | 0.667 |
| harm_vol_cypher_tight | 1 | -1.0 | 3 | 0.667 |
| harm_vol_gartley | 4 | -0.375 | 3 | 1.017 |
| judas | 1313 | 0.017 | 1249 | 0.061 |
| kzs | 22 | -0.318 | 11 | 0.364 |
| level | 3364 | -0.041 | 1577 | 0.061 |
| liqline | 1251 | -0.065 | 1527 | 0.039 |
| m2022 | 330 | -0.003 | 361 | 0.04 |
| ma_cross | 1462 | -0.007 | 1342 | 0.001 |
| macd_div | 799 | 0.023 | 576 | -0.004 |
| msb_ob | 1016 | -0.073 | 895 | 0.088 |
| ob | 791 | -0.075 | 894 | 0.1 |
| ohl_break | 436 | -0.076 | 481 | 0.014 |
| ohl_open | 1452 | -0.075 | 1568 | 0.066 |
| orb | 66 | -0.079 | 92 | -0.183 |
| ote | 360 | -0.137 | 397 | 0.204 |
| pa_engulf | 191 | -0.018 | 153 | -0.048 |
| pa_inside | 173 | -0.092 | 179 | 0.217 |
| pa_pin | 191 | -0.218 | 116 | 0.06 |
| pa_star | 21 | -0.405 | 28 | 0.152 |
| po3 | 58 | -0.071 | 67 | 0.15 |
| rect | 15 | -0.5 | 24 | 0.035 |
| rsi_div | 620 | -0.089 | 549 | 0.1 |
| sess_amd | 262 | 0.11 | 236 | -0.013 |
| sma1040 | 24 | 0.782 | 29 | 0.508 |
| smt | 899 | -0.01 | 857 | 0.038 |
| sweep | 2053 | -0.079 | 1518 | 0.038 |
| tlbreak | 1074 | -0.059 | 1098 | 0.034 |
| turtle55 | 42 | 0.217 | 47 | 0.388 |
| unicorn | 200 | -0.098 | 209 | 0.099 |
| vwap | 3298 | -0.044 | 3995 | 0.083 |
| wavec | 86 | 0.013 | 68 | 0.368 |
| wyck | 105 | 0.179 | 77 | 0.182 |
| zombie | 465 | -0.003 | 438 | -0.064 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 38167 | 38.4 | 0.007 | 25920 | 38.1 | 0.004 |
| abc | 34 | 35.3 | 0.002 | 85 | 35.3 | -0.058 |
| breaker | 184 | 33.7 | -0.112 | 196 | 37.2 | 0.013 |
| breakout | 779 | 38.6 | -0.004 | 284 | 39.8 | 0.034 |
| cisd | 393 | 35.9 | -0.049 | 590 | 39.0 | 0.038 |
| crt | 376 | 33.5 | -0.113 | 602 | 36.0 | -0.04 |
| dbl | 424 | 38.2 | -0.036 | 222 | 40.1 | 0.058 |
| donch | 2411 | 39.2 | 0.024 | 334 | 38.9 | -0.014 |
| ema_stack | 3997 | 37.6 | -0.013 | 875 | 34.9 | -0.094 |
| ew3 | 606 | 40.1 | 0.041 | 416 | 33.7 | -0.142 |
| ew5 | 160 | 40.6 | 0.072 | 41 | 31.7 | -0.134 |
| ew_r2_d1 | 334 | 39.2 | 0.071 | 201 | 41.3 | 0.125 |
| ew_r2_d2 | 171 | 40.4 | 0.107 | 128 | 48.4 | 0.28 |
| ew_r2_v | 551 | 38.5 | 0.039 | 349 | 39.0 | 0.044 |
| ew_r3_d1 | 219 | 38.8 | 0.062 | 32 | 37.5 | 0.018 |
| ew_r3_d2 | 134 | 33.6 | 0.0 | 18 | 44.4 | 0.111 |
| ew_r3_v | 312 | 41.3 | 0.112 | 48 | 41.7 | 0.042 |
| fib | 1210 | 39.5 | 0.031 | 1123 | 37.8 | 0.009 |
| fvg | 1853 | 39.9 | 0.057 | 1327 | 37.3 | -0.027 |
| harm_bat | 2 | 0.0 | -1.0 | 5 | 20.0 | -0.5 |
| harm_bat_tight | 1 | 0.0 | -1.0 | 1 | 0.0 | -1.0 |
| harm_butterfly | 8 | 87.5 | 1.188 | 10 | 30.0 | -0.196 |
| harm_butterfly_tight | 2 | 100.0 | 1.5 | 1 | 0.0 | -1.0 |
| harm_crab | 0 | None | None | 2 | 0.0 | -1.0 |
| harm_cypher | 7 | 14.3 | -0.643 | 6 | 66.7 | 0.667 |
| harm_cypher_tight | 3 | 33.3 | -0.167 | 2 | 100.0 | 1.5 |
| harm_gartley | 6 | 33.3 | -0.03 | 5 | 20.0 | -0.29 |
| harm_gartley_tight | 0 | None | None | 1 | 100.0 | 1.5 |
| harm_vol_bat | 3 | 33.3 | -0.167 | 5 | 20.0 | -0.5 |
| harm_vol_bat_tight | 2 | 50.0 | 0.25 | 1 | 0.0 | -1.0 |
| harm_vol_butterfly | 3 | 100.0 | 1.5 | 14 | 42.9 | 0.237 |
| harm_vol_butterfly_tight | 1 | 100.0 | 1.5 | 3 | 33.3 | -0.167 |
| harm_vol_crab | 0 | None | None | 2 | 0.0 | -1.0 |
| harm_vol_cypher | 7 | 28.6 | -0.286 | 7 | 71.4 | 0.786 |
| harm_vol_cypher_tight | 2 | 0.0 | -1.0 | 2 | 100.0 | 1.5 |
| harm_vol_gartley | 4 | 25.0 | -0.375 | 3 | 66.7 | 1.017 |
| judas | 1698 | 41.7 | 0.07 | 851 | 36.8 | -0.022 |
| kzs | 12 | 41.7 | 0.042 | 21 | 33.3 | -0.167 |
| level | 2480 | 37.1 | -0.031 | 2431 | 38.9 | 0.014 |
| liqline | 1568 | 37.9 | -0.012 | 1201 | 38.1 | -0.003 |
| m2022 | 445 | 39.1 | 0.046 | 246 | 36.2 | -0.028 |
| ma_cross | 1660 | 37.2 | -0.024 | 1126 | 39.5 | 0.03 |
| macd_div | 264 | 36.4 | -0.043 | 1109 | 38.9 | 0.024 |
| msb_ob | 963 | 38.4 | 0.02 | 941 | 37.3 | -0.019 |
| ob | 941 | 37.2 | -0.016 | 735 | 40.0 | 0.057 |
| ohl_break | 540 | 37.8 | -0.03 | 372 | 37.1 | -0.03 |
| ohl_open | 1635 | 38.3 | -0.004 | 1378 | 38.0 | 0.004 |
| orb | 102 | 35.3 | -0.108 | 56 | 30.4 | -0.197 |
| ote | 339 | 41.3 | 0.075 | 413 | 38.7 | 0.014 |
| pa_engulf | 147 | 30.6 | -0.212 | 197 | 43.1 | 0.104 |
| pa_inside | 202 | 43.1 | 0.111 | 148 | 38.5 | 0.0 |
| pa_pin | 124 | 30.6 | -0.121 | 183 | 35.0 | -0.107 |
| pa_star | 14 | 35.7 | -0.107 | 35 | 34.3 | -0.078 |
| po3 | 68 | 41.2 | 0.059 | 56 | 39.3 | 0.007 |
| rect | 30 | 33.3 | -0.088 | 9 | 22.2 | -0.444 |
| rsi_div | 294 | 39.5 | 0.063 | 872 | 36.5 | -0.023 |
| sess_amd | 230 | 40.4 | 0.036 | 266 | 40.6 | 0.064 |
| sma1040 | 19 | 52.6 | 0.389 | 34 | 64.7 | 0.768 |
| smt | 925 | 37.0 | -0.027 | 830 | 40.5 | 0.057 |
| sweep | 1503 | 36.6 | -0.024 | 2061 | 36.4 | -0.031 |
| tlbreak | 1023 | 37.9 | -0.017 | 1143 | 37.2 | -0.008 |
| turtle55 | 66 | 43.9 | 0.228 | 23 | 56.5 | 0.536 |
| unicorn | 204 | 34.8 | -0.087 | 203 | 40.4 | 0.091 |
| vwap | 5888 | 39.3 | 0.029 | 1387 | 38.9 | 0.012 |
| wavec | 34 | 44.1 | 0.331 | 118 | 41.5 | 0.122 |
| wyck | 76 | 38.2 | -0.006 | 106 | 49.1 | 0.314 |
| zombie | 474 | 35.2 | -0.079 | 428 | 38.3 | 0.015 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7599 | 33.7 | -0.006 |
| Mon | 7716 | 39.8 | 0.016 |
| Sat | 10549 | 38.9 | 0.016 |
| Sun | 15360 | 37.4 | -0.03 |
| Thu | 7758 | 40.0 | 0.064 |
| Tue | 7665 | 39.1 | -0.005 |
| Wed | 7690 | 39.6 | 0.017 |
| Asia 00-07 | 19145 | 38.7 | -0.003 |
| Late 20-24 | 13000 | 37.2 | -0.022 |
| London 07-12 | 9845 | 39.5 | 0.024 |
| New York 12-20 | 18615 | 38.4 | 0.014 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 64337 | 38.3 | 0.006 | 0.004 | +0.32 | 28086 | -0.003 | 36251 | 0.013 |  |
| grade A+++ | 494 | 43.1 | 0.161 | 0.074 | +1.28 | 245 | 0.235 | 249 | 0.088 |  |
| grade A+ | 8850 | 38.5 | 0.027 | -0.034 | +3.61 | 3710 | 0.007 | 5140 | 0.042 | YES |
| grade A | 19190 | 38.2 | 0.018 | 0.0 | +1.57 | 8128 | -0.019 | 11062 | 0.045 |  |
| grade B | 23187 | 37.8 | -0.011 | 0.015 | -2.47 | 10090 | -0.01 | 13097 | -0.011 |  |
| grade C | 12616 | 38.9 | -0.004 | 0.012 | -1.12 | 5913 | 0.013 | 6703 | -0.018 |  |
| layer htf | 38167 | 38.4 | 0.007 | 0.007 | +0.00 | 16656 | 0.004 | 21511 | 0.009 |  |
| layer loc | 13745 | 38.4 | 0.019 | 0.027 | -0.59 | 5872 | 0.039 | 7873 | 0.004 |  |
| layer vol | 21032 | 38.6 | 0.008 | -0.034 | +3.85 | 9362 | -0.028 | 11670 | 0.037 |  |
| layer reg | 47586 | 37.7 | 0.005 | -0.011 | +2.30 | 20408 | -0.008 | 27178 | 0.016 |  |
| layer time | 32192 | 38.4 | 0.022 | 0.009 | +1.51 | 13414 | 0.0 | 18778 | 0.038 |  |
| no htf | 26170 | 38.1 | 0.004 | -0.001 | +0.49 | 11430 | -0.015 | 14740 | 0.019 |  |
| no loc | 50592 | 38.2 | 0.002 | -0.002 | +0.66 | 22214 | -0.015 | 28378 | 0.015 |  |
| no vol | 43305 | 38.1 | 0.005 | 0.022 | -2.32 | 18724 | 0.009 | 24581 | 0.001 |  |
| no reg | 16751 | 39.8 | 0.006 | 0.046 | -3.18 | 7678 | 0.01 | 9073 | 0.004 |  |
| no time | 32145 | 38.1 | -0.011 | -0.002 | -1.06 | 14672 | -0.007 | 17473 | -0.015 |  |
| no loc / sma1040 | 48 | 62.5 | 0.686 | -0.143 | +3.85 | 16 | 0.875 | 32 | 0.592 |  |
| grade A / wavec | 39 | 48.7 | 0.446 | 0.099 | +1.66 | 16 | 0.719 | 23 | 0.256 |  |
| grade A+ / ew_r3_v | 32 | 53.1 | 0.445 | -0.377 | +3.45 | 15 | 0.368 | 17 | 0.514 |  |
| grade A / wyck | 57 | 54.4 | 0.409 | 0.11 | +1.52 | 25 | 0.33 | 32 | 0.47 |  |
| grade A+ / ew_r2_d2 | 59 | 49.2 | 0.344 | 0.057 | +1.39 | 21 | 0.864 | 38 | 0.057 |  |
| no loc / turtle55 | 89 | 47.2 | 0.307 | 0.165 | +0.98 | 34 | 0.269 | 55 | 0.331 |  |
| no loc / wyck | 79 | 48.1 | 0.265 | 0.011 | +1.47 | 33 | 0.311 | 46 | 0.231 |  |
| grade A+ / po3 | 32 | 50.0 | 0.25 | 0.308 | -0.23 | 17 | 0.471 | 15 | 0.0 |  |
| loc / wavec | 54 | 46.3 | 0.235 | -0.052 | +1.41 | 21 | 0.071 | 33 | 0.338 |  |
| grade A+++ / sweep | 64 | 45.3 | 0.225 | 0.109 | +0.60 | 39 | 0.435 | 25 | -0.102 |  |
| grade A+++ / msb_ob | 36 | 41.7 | 0.214 | 0.091 | +0.52 | 16 | 0.672 | 20 | -0.152 |  |
| grade A+ / ew_r2_d1 | 88 | 44.3 | 0.214 | -0.006 | +1.25 | 33 | 0.112 | 55 | 0.275 |  |
| grade A / turtle55 | 40 | 45.0 | 0.214 | 0.17 | +0.20 | 15 | 0.385 | 25 | 0.111 |  |
| loc / ew_r2_d2 | 113 | 46.0 | 0.206 | -0.127 | +2.45 | 45 | 0.444 | 68 | 0.048 |  |
| grade C / breakout | 102 | 47.1 | 0.199 | 0.052 | +0.95 | 47 | 0.383 | 55 | 0.042 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| sweep | vwap | 6328 | 3939 | 62.2 |
| level | vwap | 8056 | 3817 | 47.4 |
| ema_stack | sweep | 3227 | 2417 | 74.9 |
| ema_stack | level | 3966 | 2010 | 50.7 |
| fvg | vwap | 4584 | 1845 | 40.2 |
| macd_div | vwap | 2061 | 1631 | 79.1 |
| ohl_open | vwap | 3840 | 1629 | 42.4 |
| level | sweep | 3548 | 1525 | 43.0 |
| msb_ob | vwap | 2718 | 1521 | 56.0 |
| fib | vwap | 2964 | 1413 | 47.7 |
| fvg | level | 3284 | 1411 | 43.0 |
| ob | vwap | 2657 | 1409 | 53.0 |
| judas | level | 2871 | 1363 | 47.5 |
| liqline | vwap | 3707 | 1354 | 36.5 |
| rsi_div | vwap | 1767 | 1342 | 75.9 |
| ma_cross | sweep | 2000 | 1274 | 63.7 |
| level | ma_cross | 2527 | 1260 | 49.9 |
| smt | vwap | 2839 | 1219 | 42.9 |
| ma_cross | vwap | 4096 | 1203 | 29.4 |
| tlbreak | vwap | 2582 | 1203 | 46.6 |
| judas | sweep | 1873 | 1159 | 61.9 |
| judas | vwap | 4214 | 1140 | 27.1 |
| level | ohl_open | 2177 | 1104 | 50.7 |
| level | liqline | 2030 | 1080 | 53.2 |
| liqline | sweep | 1888 | 1009 | 53.4 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 27 | 44.4 | 0.177 |
| 2 families | 408 | 35.3 | -0.061 |
| 2 families (with opposition) | 1350 | 41.0 | 0.076 |
| 3 families | 1114 | 37.5 | -0.002 |
| 3 families (with opposition) | 4608 | 39.2 | 0.023 |
| 4+ families | 1017 | 39.2 | 0.021 |
| 4+ families (with opposition) | 4248 | 38.5 | 0.015 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 85.3 | 33264 | 85.1 | 459998 | +0.8 |
| 1m shapes 120/180/240/360 deg | 83.2 | 14130 | 83.5 | 14059 | -0.8 |
| 15m | 65.3 | 19829 | 65.3 | 274569 | -0.1 |
| 15m shapes 120/180/240/360 deg | 64.1 | 10311 | 64.2 | 10313 | -0.3 |
| 1h | 58.0 | 16035 | 57.8 | 222264 | +0.6 |
| 1h shapes 120/180/240/360 deg | 57.0 | 8831 | 57.5 | 8803 | -0.9 |
| 4h | 56.8 | 12073 | 57.9 | 166709 | -2.3 |
| 4h shapes 120/180/240/360 deg | 57.2 | 6810 | 57.3 | 6818 | -0.1 |
| 1d | 55.0 | 3217 | 55.7 | 43188 | -0.9 |
| 1d shapes 120/180/240/360 deg | 56.9 | 2050 | 56.6 | 2055 | +0.3 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 71 | 19.7 | +0.263 | +0.402 | -0.51 |
| 1d | 56 | 37.5 | -0.055 | +0.043 | -0.41 |
| 1h | 120 | 23.3 | -0.059 | -0.179 | +0.98 |
| 4h | 94 | 34.0 | +0.105 | +0.133 | -0.12 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2386 | -0.115 |
| 15 days around full moon | 2370 | 0.016 |

Difference t = -1.62 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 64337 | 49.0 | -0.019 | -0.119 | -1232.1 | -4.90 |
| rr1.5 | 64337 | 40.8 | 0.006 | -0.094 | 368.6 | +1.21 |
| rr2.0 | 64337 | 35.9 | 0.028 | -0.072 | 1798.0 | +5.14 |
| rr3.0 | 64337 | 30.4 | 0.058 | -0.042 | 3720.4 | +8.84 |
| rr1.5_be | 64337 | 34.9 | 0.004 | -0.096 | 256.1 | +0.90 |
| rr2.0_be | 64337 | 28.1 | 0.026 | -0.074 | 1683.2 | +5.35 |
| rr1.5_h16 | 64337 | 42.3 | 0.008 | -0.092 | 539.6 | +1.88 |
| rr2.0_h16 | 64337 | 39.2 | 0.026 | -0.074 | 1697.1 | +5.31 |
| pt_1.5_3 | 64337 | 49.0 | 0.04 | -0.06 | 2543.1 | +8.54 |
| pt_1.0_3 | 64337 | 49.0 | 0.024 | -0.076 | 1572.8 | +5.66 |
| pt_1.5_5 | 64337 | 49.0 | 0.056 | -0.044 | 3587.9 | +11.63 |
| trail_only | 64337 | 49.0 | 0.101 | 0.001 | 6466.2 | +18.07 |

## Exit variant x timeframe x trend (is the htf sign flip caused by the exit? docs/PREREG_2026-11-01.md)

Same entries, every detector pooled. If 'with' stays below 'against' on 1h / 1m under every exit, the exit is not the cause.

| tf | exit | with n | with avg R | with t | against n | against avg R | against t |
|---|---|---|---|---|---|---|---|
| 15m | rr1.0 | 10404 | -0.048 | -4.95 | 7213 | 0.019 | +1.65 |
| 15m | rr1.5 | 10404 | -0.004 | -0.35 | 7213 | 0.032 | +2.23 |
| 15m | rr2.0 | 10404 | 0.045 | +3.28 | 7213 | 0.037 | +2.25 |
| 15m | rr3.0 | 10404 | 0.124 | +7.22 | 7213 | 0.026 | +1.34 |
| 15m | rr1.5_be | 10404 | -0.011 | -0.99 | 7213 | 0.017 | +1.33 |
| 15m | rr2.0_be | 10404 | 0.015 | +1.20 | 7213 | 0.033 | +2.27 |
| 15m | rr1.5_h16 | 10404 | -0.016 | -1.41 | 7213 | 0.042 | +3.15 |
| 15m | rr2.0_h16 | 10404 | 0.013 | +1.05 | 7213 | 0.057 | +3.89 |
| 15m | pt_1.5_3 | 10404 | 0.015 | +1.34 | 7213 | 0.044 | +3.22 |
| 15m | pt_1.0_3 | 10404 | -0.005 | -0.43 | 7213 | 0.043 | +3.36 |
| 15m | pt_1.5_5 | 10404 | 0.032 | +2.65 | 7213 | 0.049 | +3.58 |
| 15m | trail_only | 10404 | 0.071 | +5.17 | 7213 | 0.078 | +4.96 |
| 1d | rr1.0 | 2212 | -0.033 | -1.58 | 1520 | 0.112 | +4.51 |
| 1d | rr1.5 | 2212 | -0.017 | -0.72 | 1520 | 0.181 | +5.98 |
| 1d | rr2.0 | 2212 | -0.024 | -0.88 | 1520 | 0.238 | +6.95 |
| 1d | rr3.0 | 2212 | 0.033 | +1.05 | 1520 | 0.345 | +8.41 |
| 1d | rr1.5_be | 2212 | -0.042 | -1.84 | 1520 | 0.14 | +4.96 |
| 1d | rr2.0_be | 2212 | -0.034 | -1.36 | 1520 | 0.206 | +6.44 |
| 1d | rr1.5_h16 | 2212 | -0.004 | -0.16 | 1520 | 0.174 | +5.86 |
| 1d | rr2.0_h16 | 2212 | 0.011 | +0.41 | 1520 | 0.224 | +6.74 |
| 1d | pt_1.5_3 | 2212 | -0.02 | -0.84 | 1520 | 0.194 | +6.39 |
| 1d | pt_1.0_3 | 2212 | -0.017 | -0.77 | 1520 | 0.177 | +6.29 |
| 1d | pt_1.5_5 | 2212 | -0.02 | -0.84 | 1520 | 0.205 | +6.60 |
| 1d | trail_only | 2212 | -0.002 | -0.06 | 1520 | 0.265 | +7.32 |
| 1h | rr1.0 | 10107 | -0.013 | -1.32 | 7505 | 0.002 | +0.21 |
| 1h | rr1.5 | 10107 | -0.003 | -0.27 | 7505 | 0.041 | +2.92 |
| 1h | rr2.0 | 10107 | 0.021 | +1.51 | 7505 | 0.038 | +2.41 |
| 1h | rr3.0 | 10107 | 0.004 | +0.26 | 7505 | 0.019 | +1.00 |
| 1h | rr1.5_be | 10107 | 0.002 | +0.22 | 7505 | 0.025 | +1.92 |
| 1h | rr2.0_be | 10107 | 0.023 | +1.90 | 7505 | 0.036 | +2.52 |
| 1h | rr1.5_h16 | 10107 | 0.017 | +1.49 | 7505 | 0.023 | +1.78 |
| 1h | rr2.0_h16 | 10107 | 0.024 | +1.96 | 7505 | 0.023 | +1.57 |
| 1h | pt_1.5_3 | 10107 | 0.025 | +2.21 | 7505 | 0.046 | +3.48 |
| 1h | pt_1.0_3 | 10107 | 0.015 | +1.40 | 7505 | 0.033 | +2.69 |
| 1h | pt_1.5_5 | 10107 | 0.038 | +3.20 | 7505 | 0.049 | +3.67 |
| 1h | trail_only | 10107 | 0.068 | +5.05 | 7505 | 0.071 | +4.70 |
| 1m | rr1.0 | 7460 | 0.003 | +0.29 | 4241 | -0.105 | -6.92 |
| 1m | rr1.5 | 7460 | 0.064 | +4.52 | 4241 | -0.065 | -3.52 |
| 1m | rr2.0 | 7460 | 0.119 | +7.15 | 4241 | -0.043 | -2.03 |
| 1m | rr3.0 | 7460 | 0.208 | +10.01 | 4241 | 0.022 | +0.86 |
| 1m | rr1.5_be | 7460 | 0.068 | +5.11 | 4241 | -0.057 | -3.28 |
| 1m | rr2.0_be | 7460 | 0.121 | +7.99 | 4241 | -0.033 | -1.69 |
| 1m | rr1.5_h16 | 7460 | 0.069 | +5.12 | 4241 | -0.06 | -3.51 |
| 1m | rr2.0_h16 | 7460 | 0.13 | +8.47 | 4241 | -0.033 | -1.73 |
| 1m | pt_1.5_3 | 7460 | 0.157 | +10.63 | 4241 | 0.018 | +0.96 |
| 1m | pt_1.0_3 | 7460 | 0.119 | +8.69 | 4241 | -0.012 | -0.68 |
| 1m | pt_1.5_5 | 7460 | 0.206 | +12.92 | 4241 | 0.067 | +3.23 |
| 1m | trail_only | 7460 | 0.333 | +16.74 | 4241 | 0.178 | +6.94 |
| 4h | rr1.0 | 7984 | -0.018 | -1.65 | 5441 | -0.049 | -3.65 |
| 4h | rr1.5 | 7984 | -0.013 | -0.94 | 5441 | -0.08 | -5.03 |
| 4h | rr2.0 | 7984 | 0.013 | +0.85 | 5441 | -0.109 | -6.17 |
| 4h | rr3.0 | 7984 | 0.067 | +3.78 | 5441 | -0.142 | -7.15 |
| 4h | rr1.5_be | 7984 | -0.006 | -0.47 | 5441 | -0.057 | -3.87 |
| 4h | rr2.0_be | 7984 | 0.015 | +1.11 | 5441 | -0.068 | -4.24 |
| 4h | rr1.5_h16 | 7984 | -0.006 | -0.51 | 5441 | -0.076 | -5.07 |
| 4h | rr2.0_h16 | 7984 | 0.007 | +0.51 | 5441 | -0.102 | -6.29 |
| 4h | pt_1.5_3 | 7984 | 0.028 | +2.12 | 5441 | -0.05 | -3.37 |
| 4h | pt_1.0_3 | 7984 | 0.015 | +1.24 | 5441 | -0.052 | -3.68 |
| 4h | pt_1.5_5 | 7984 | 0.033 | +2.49 | 5441 | -0.044 | -2.94 |
| 4h | trail_only | 7984 | 0.059 | +3.99 | 5441 | -0.043 | -2.58 |
