# Strategy lab - real candles (2026-11-17)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | turtle55 | Trend (hedge fund) | 81 | 49.4 | 0.308 | 0.208 | 49.4 | 0.329 |  |
| 2 | sma1040 | Trend (hedge fund) | 67 | 47.8 | 0.304 | 0.204 | 35.8 | 0.136 |  |
| 3 | wavec | Elliott wave | 156 | 45.5 | 0.211 | 0.111 | 41.7 | 0.09 |  |
| 4 | wyck | Wyckoff | 194 | 43.3 | 0.142 | 0.042 | 40.7 | 0.084 |  |
| 5 | ew_r3_d2 | Elliott wave | 161 | 40.4 | 0.135 | 0.035 | 37.9 | 0.115 |  |
| 6 | ew_r2_d2 | Elliott wave | 295 | 40.3 | 0.119 | 0.019 | 31.9 | -0.087 |  |
| 7 | ew_r3_v | Elliott wave | 351 | 39.9 | 0.099 | -0.001 | 31.3 | -0.088 |  |
| 8 | ote | Fibonacci | 796 | 40.8 | 0.073 | -0.027 | 36.9 | -0.029 |  |
| 9 | macd_div | Momentum / divergence | 1400 | 40.5 | 0.072 | -0.028 | 40.1 | 0.057 |  |
| 10 | fvg | SMC / ICT | 3166 | 40.4 | 0.067 | -0.033 | 36.8 | -0.025 | YES |
| 11 | ew_r2_d1 | Elliott wave | 552 | 38.9 | 0.066 | -0.034 | 35.3 | -0.016 |  |
| 12 | rsi_div | Momentum / divergence | 1180 | 39.5 | 0.057 | -0.043 | 37.5 | 0.007 |  |
| 13 | liqline | Liquidity | 2698 | 39.9 | 0.047 | -0.053 | 37.8 | -0.014 |  |
| 14 | orb | Time (sessions) | 169 | 39.6 | 0.037 | -0.063 | 41.4 | 0.083 |  |
| 15 | unicorn | SMC / ICT | 463 | 37.8 | 0.034 | -0.066 | 40.2 | 0.084 |  |
| 16 | ew5 | Elliott wave | 209 | 37.8 | 0.022 | -0.078 | 37.3 | 0.045 |  |
| 17 | fib | Fibonacci | 2344 | 38.5 | 0.02 | -0.08 | 37.0 | -0.01 |  |
| 18 | breakout | Levels / breakouts | 1108 | 39.4 | 0.019 | -0.081 | 39.2 | 0.02 |  |
| 19 | ma_cross | Trend (MA) | 2845 | 38.7 | 0.018 | -0.082 | 37.0 | -0.019 |  |
| 20 | po3 | Time (sessions) | 127 | 39.4 | 0.015 | -0.085 | 37.8 | 0.043 |  |
| 21 | tlbreak | Levels / breakouts | 2233 | 38.7 | 0.013 | -0.087 | 37.0 | -0.021 |  |
| 22 | ew_r2_v | Elliott wave | 948 | 37.3 | 0.01 | -0.09 | 34.7 | -0.052 |  |
| 23 | judas | Time (sessions) | 2745 | 39.0 | 0.009 | -0.091 | 38.3 | -0.011 |  |
| 24 | ohl_open | Levels / breakouts | 3131 | 38.2 | 0.004 | -0.096 | 37.9 | -0.002 |  |
| 25 | donch | Trend (hedge fund) | 2759 | 38.2 | 0.003 | -0.097 | 37.8 | -0.005 |  |
| 26 | m2022 | SMC / ICT | 696 | 37.8 | 0.002 | -0.098 | 36.8 | -0.008 |  |
| 27 | pa_pin | Price action | 267 | 36.7 | 0.002 | -0.098 | 35.2 | -0.076 |  |
| 28 | ohl_break | Levels / breakouts | 898 | 38.5 | 0.001 | -0.099 | 39.5 | 0.019 |  |
| 29 | cisd | SMC / ICT | 999 | 37.3 | 0.001 | -0.099 | 37.7 | 0.02 |  |
| 30 | sweep | Liquidity | 3680 | 37.7 | 0.0 | -0.1 | 37.9 | -0.001 |  |
| 31 | vwap | Trend (MA) | 7353 | 37.8 | -0.006 | -0.106 | 37.4 | -0.009 |  |
| 32 | ema_stack | Trend (MA) | 4899 | 37.7 | -0.007 | -0.107 | 38.9 | 0.029 |  |
| 33 | level | Levels / breakouts | 4934 | 37.7 | -0.01 | -0.11 | 37.9 | -0.003 |  |
| 34 | ew_r3_d1 | Elliott wave | 238 | 34.5 | -0.013 | -0.113 | 28.2 | -0.109 |  |
| 35 | breaker | SMC / ICT | 390 | 35.4 | -0.023 | -0.123 | 33.6 | -0.063 |  |
| 36 | msb_ob | SMC / ICT | 1882 | 36.7 | -0.025 | -0.125 | 36.6 | -0.026 |  |
| 37 | pa_inside | Price action | 371 | 36.9 | -0.028 | -0.128 | 40.4 | 0.047 |  |
| 38 | dbl | Chart patterns (range) | 698 | 37.5 | -0.028 | -0.128 | 38.0 | -0.0 |  |
| 39 | abc | Elliott wave | 115 | 35.7 | -0.029 | -0.129 | 37.4 | 0.02 |  |
| 40 | ew3 | Elliott wave | 976 | 37.1 | -0.038 | -0.138 | 38.1 | -0.007 |  |
| 41 | ob | SMC / ICT | 1552 | 35.1 | -0.059 | -0.159 | 37.6 | 0.011 |  |
| 42 | smt | Intermarket (SMT) | 1803 | 35.7 | -0.067 | -0.167 | 37.3 | -0.009 |  |
| 43 | crt | Liquidity | 985 | 35.2 | -0.067 | -0.167 | 35.9 | -0.05 |  |
| 44 | pa_engulf | Price action | 301 | 34.9 | -0.077 | -0.177 | 35.2 | -0.068 |  |
| 45 | zombie | Liquidity | 927 | 35.0 | -0.078 | -0.178 | 36.2 | -0.037 |  |
| 46 | sess_amd | Time (sessions) | 479 | 35.3 | -0.079 | -0.179 | 36.5 | -0.044 |  |
| 47 | pa_star | Price action | 39 | 35.9 | -0.103 | -0.203 | 43.6 | 0.09 |  |
| 48 | harm_cypher_tight | Harmonic: Cypher | 3 | 100.0 | 1.5 | 1.4 | 33.3 | -0.167 |  |
| 49 | harm_vol_cypher_tight | Harmonic: Cypher (vol swings) | 3 | 100.0 | 1.5 | 1.4 | 66.7 | 0.667 |  |
| 50 | harm_butterfly_tight | Harmonic: Butterfly | 3 | 100.0 | 1.5 | 1.4 | 66.7 | 0.667 |  |
| 51 | harm_vol_bat_tight | Harmonic: Bat (vol swings) | 1 | 100.0 | 1.5 | 1.4 | 100.0 | 1.5 |  |
| 52 | harm_bat_tight | Harmonic: Bat | 1 | 100.0 | 1.5 | 1.4 | 0.0 | -1.0 |  |
| 53 | harm_vol_bat | Harmonic: Bat (vol swings) | 4 | 75.0 | 0.875 | 0.775 | 25.0 | -0.375 |  |
| 54 | harm_cypher | Harmonic: Cypher | 9 | 66.7 | 0.74 | 0.64 | 44.4 | 0.185 |  |
| 55 | harm_vol_cypher | Harmonic: Cypher (vol swings) | 11 | 63.6 | 0.591 | 0.491 | 45.5 | 0.136 |  |
| 56 | harm_gartley | Harmonic: Gartley | 6 | 50.0 | 0.398 | 0.298 | 16.7 | -0.436 |  |
| 57 | harm_butterfly | Harmonic: Butterfly | 22 | 54.5 | 0.388 | 0.288 | 50.0 | 0.275 |  |
| 58 | harm_vol_butterfly | Harmonic: Butterfly (vol swings) | 13 | 46.2 | 0.363 | 0.263 | 15.4 | -0.401 |  |
| 59 | harm_crab | Harmonic: Crab | 2 | 50.0 | 0.25 | 0.15 | 50.0 | 0.25 |  |
| 60 | harm_vol_gartley | Harmonic: Gartley (vol swings) | 4 | 50.0 | 0.25 | 0.15 | 75.0 | 0.875 |  |
| 61 | rect | Chart patterns (range) | 29 | 24.1 | -0.327 | -0.427 | 44.8 | 0.167 |  |
| 62 | harm_bat | Harmonic: Bat | 4 | 25.0 | -0.375 | -0.475 | 25.0 | -0.375 |  |
| 63 | kzs | Time (sessions) | 28 | 21.4 | -0.397 | -0.497 | 25.0 | -0.308 |  |
| 64 | harm_vol_butterfly_tight | Harmonic: Butterfly (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 65 | harm_vol_crab | Harmonic: Crab (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 66 | harm_gartley_tight | Harmonic: Gartley | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 67 | harm_vol_gartley_tight | Harmonic: Gartley (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |

## Stop study: where should the stop sit? (same entries, target fixed at 2.25 ATR, results in ATR, cost 0.15 ATR)

| group | stop | n | target hit % | stopped % | avg ATR | net ATR | mirror avg ATR | t (net vs 0) |
|---|---|---|---|---|---|---|---|---|
| all | 1.0 ATR | 64807 | 30.4 | 67.4 | 0.02 | -0.13 | 0.031 | -22.16 |
| all | 1.5 ATR | 64807 | 38.1 | 57.4 | 0.009 | -0.141 | 0.029 | -19.94 |
| all | 2.0 ATR | 64807 | 43.5 | 49.7 | -0.012 | -0.162 | -0.001 | -19.98 |
| all | 2.5 ATR | 64807 | 47.4 | 43.1 | -0.024 | -0.174 | -0.015 | -19.44 |
| all | 3.0 ATR | 64807 | 50.2 | 37.8 | -0.042 | -0.192 | -0.023 | -19.78 |
| 1m | 1.0 ATR | 12121 | 34.6 | 64.8 | 0.133 | -0.017 | 0.124 | -1.20 |
| 1m | 1.5 ATR | 12121 | 41.6 | 57.4 | 0.076 | -0.074 | 0.107 | -4.44 |
| 1m | 2.0 ATR | 12121 | 46.3 | 52.3 | -0.006 | -0.156 | 0.025 | -8.15 |
| 1m | 2.5 ATR | 12121 | 50.3 | 47.7 | -0.065 | -0.215 | -0.007 | -10.04 |
| 1m | 3.0 ATR | 12121 | 53.5 | 43.5 | -0.114 | -0.264 | -0.031 | -11.29 |
| 15m | 1.0 ATR | 17842 | 29.1 | 69.0 | -0.024 | -0.174 | 0.026 | -15.71 |
| 15m | 1.5 ATR | 17842 | 37.4 | 58.7 | -0.026 | -0.176 | 0.025 | -13.03 |
| 15m | 2.0 ATR | 17842 | 43.7 | 50.9 | -0.029 | -0.179 | 0.01 | -11.54 |
| 15m | 2.5 ATR | 17842 | 48.1 | 44.5 | -0.036 | -0.186 | -0.01 | -10.79 |
| 15m | 3.0 ATR | 17842 | 51.2 | 39.4 | -0.049 | -0.199 | -0.031 | -10.63 |
| 1h | 1.0 ATR | 17637 | 30.0 | 67.0 | 0.015 | -0.135 | 0.025 | -12.03 |
| 1h | 1.5 ATR | 17637 | 37.6 | 57.2 | -0.003 | -0.153 | 0.029 | -11.30 |
| 1h | 2.0 ATR | 17637 | 42.8 | 49.5 | -0.025 | -0.175 | 0.013 | -11.38 |
| 1h | 2.5 ATR | 17637 | 46.8 | 42.9 | -0.033 | -0.183 | 0.013 | -10.75 |
| 1h | 3.0 ATR | 17637 | 49.8 | 38.1 | -0.055 | -0.205 | 0.017 | -11.05 |
| 4h | 1.0 ATR | 13481 | 28.8 | 68.7 | -0.025 | -0.175 | -0.038 | -13.83 |
| 4h | 1.5 ATR | 13481 | 37.2 | 57.3 | -0.007 | -0.157 | -0.039 | -10.14 |
| 4h | 2.0 ATR | 13481 | 42.9 | 48.0 | 0.015 | -0.135 | -0.051 | -7.71 |
| 4h | 2.5 ATR | 13481 | 46.2 | 39.5 | 0.03 | -0.12 | -0.046 | -6.26 |
| 4h | 3.0 ATR | 13481 | 48.4 | 32.9 | 0.04 | -0.11 | -0.033 | -5.39 |
| 1d | 1.0 ATR | 3726 | 29.8 | 65.2 | 0.048 | -0.102 | 0.029 | -4.20 |
| 1d | 1.5 ATR | 3726 | 36.2 | 51.8 | 0.067 | -0.083 | 0.032 | -2.91 |
| 1d | 2.0 ATR | 3726 | 39.0 | 43.2 | 0.025 | -0.125 | -0.024 | -3.89 |
| 1d | 2.5 ATR | 3726 | 41.1 | 34.7 | 0.019 | -0.131 | -0.08 | -3.79 |
| 1d | 3.0 ATR | 3726 | 42.2 | 28.3 | -0.001 | -0.151 | -0.116 | -4.10 |

| group | question | n | value |
|---|---|---|---|
| all | stopped at 1.5 ATR, target reached later | 47420 | 30.8 % reached it later (mirror direction 31.3 %); 73.2 % of all trades were stopped |
| all | MAE of trades that reached the target (ATR) | 39779 | p50 1.02 · p75 2.3 · p90 4.38 |
| 1m | stopped at 1.5 ATR, target reached later | 9472 | 32.5 % reached it later (mirror direction 36.6 %); 78.1 % of all trades were stopped |
| 1m | MAE of trades that reached the target (ATR) | 8209 | p50 0.94 · p75 2.55 · p90 4.85 |
| 15m | stopped at 1.5 ATR, target reached later | 13516 | 35.1 % reached it later (mirror direction 32.8 %); 75.8 % of all trades were stopped |
| 15m | MAE of trades that reached the target (ATR) | 11558 | p50 1.2 · p75 2.59 · p90 5.04 |
| 1h | stopped at 1.5 ATR, target reached later | 13235 | 33.0 % reached it later (mirror direction 34.6 %); 75.0 % of all trades were stopped |
| 1h | MAE of trades that reached the target (ATR) | 11093 | p50 1.06 · p75 2.58 · p90 4.65 |
| 4h | stopped at 1.5 ATR, target reached later | 9095 | 23.3 % reached it later (mirror direction 23.4 %); 67.5 % of all trades were stopped |
| 4h | MAE of trades that reached the target (ATR) | 7252 | p50 0.91 · p75 1.78 · p90 2.99 |
| 1d | stopped at 1.5 ATR, target reached later | 2102 | 14.3 % reached it later (mirror direction 12.1 %); 56.4 % of all trades were stopped |
| 1d | MAE of trades that reached the target (ATR) | 1667 | p50 0.7 · p75 1.23 · p90 2.25 |

Reading: a stop that is never reached only helps if the AVERAGE (net ATR) goes up, not just the target-hit share; compare with the mirror column (the opposite direction on the same bars).


## Pre-registered tests (signals after the freeze date only; docs/PREREG_2026-11-01.md)

| hypothesis | n | win % | avg R | net avg R | t vs random | net 1st half (n) | net 2nd half (n) | PASS |
|---|---|---|---|---|---|---|---|---|
| H1 sess_amd + loc | 93 | 44.1 | 0.13 | 0.03 | +1.30 | -0.209 (46) | 0.265 (47) |  |
| H2 ohl_open + Late 20-24 | 349 | 37.5 | -0.023 | -0.123 | -0.21 | -0.098 (174) | -0.148 (175) |  |

Gate: n >= 100, t > 3.0, net > 0 overall and in both time halves. Under n = 100 it is not evidence, whatever the numbers say.


## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Harmonic: Bat (vol swings) | 5 | 1.0 |
| 2 | Harmonic: Cypher | 12 | 0.93 |
| 3 | Harmonic: Cypher (vol swings) | 14 | 0.786 |
| 4 | Harmonic: Butterfly | 25 | 0.521 |
| 5 | Harmonic: Butterfly (vol swings) | 14 | 0.266 |
| 6 | Harmonic: Crab | 2 | 0.25 |
| 7 | Harmonic: Gartley | 7 | 0.198 |
| 8 | Wyckoff | 194 | 0.142 |
| 9 | Momentum / divergence | 2580 | 0.065 |
| 10 | Fibonacci | 3140 | 0.033 |
| 11 | Elliott wave | 4001 | 0.033 |
| 12 | Trend (hedge fund) | 2907 | 0.018 |
| 13 | SMC / ICT | 9148 | 0.009 |
| 14 | Levels / breakouts | 12304 | 0.001 |
| 15 | Harmonic: Bat | 5 | 0.0 |
| 16 | Harmonic: Gartley (vol swings) | 5 | 0.0 |
| 17 | Liquidity | 8290 | -0.001 |
| 18 | Trend (MA) | 15097 | -0.002 |
| 19 | Time (sessions) | 3548 | -0.005 |
| 20 | Price action | 978 | -0.038 |
| 21 | Chart patterns (range) | 727 | -0.04 |
| 22 | Intermarket (SMT) | 1803 | -0.067 |
| 23 | Harmonic: Crab (vol swings) | 1 | -1.0 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| abc | 15m | 30 | 26.7 | -0.235 | -0.335 |
| breaker | 4h | 112 | 42.9 | 0.187 | 0.087 |
| breakout | 1m | 217 | 41.5 | 0.054 | -0.046 |
| cisd | 4h | 216 | 39.4 | 0.088 | -0.012 |
| crt | 1m | 98 | 41.8 | 0.063 | -0.037 |
| dbl | 1d | 49 | 42.9 | 0.071 | -0.029 |
| donch | 1d | 159 | 39.6 | 0.111 | 0.011 |
| ema_stack | 1d | 283 | 39.6 | 0.158 | 0.058 |
| ew3 | 4h | 212 | 41.5 | 0.082 | -0.018 |
| ew5 | 1h | 39 | 43.6 | 0.163 | 0.063 |
| ew_r2_d1 | 1h | 162 | 53.1 | 0.401 | 0.301 |
| ew_r2_d2 | 1h | 67 | 53.7 | 0.379 | 0.279 |
| ew_r2_v | 1m | 148 | 44.6 | 0.126 | 0.026 |
| ew_r3_d1 | 1d | 35 | 45.7 | 0.413 | 0.313 |
| ew_r3_d2 | 1d | 30 | 53.3 | 0.543 | 0.443 |
| ew_r3_v | 1d | 32 | 50.0 | 0.484 | 0.384 |
| fib | 1m | 436 | 45.6 | 0.155 | 0.055 |
| fvg | 1m | 853 | 45.1 | 0.141 | 0.041 |
| judas | 1m | 970 | 41.5 | 0.047 | -0.053 |
| level | 1m | 1156 | 40.2 | 0.021 | -0.079 |
| liqline | 1d | 148 | 37.8 | 0.116 | 0.016 |
| m2022 | 1d | 90 | 46.7 | 0.345 | 0.245 |
| ma_cross | 1d | 135 | 40.7 | 0.179 | 0.079 |
| macd_div | 1m | 211 | 52.1 | 0.303 | 0.203 |
| msb_ob | 1m | 359 | 40.4 | 0.02 | -0.08 |
| ob | 15m | 411 | 36.3 | -0.019 | -0.119 |
| ohl_break | 1m | 132 | 47.0 | 0.191 | 0.091 |
| ohl_open | 1m | 719 | 42.1 | 0.06 | -0.04 |
| orb | 15m | 163 | 39.3 | 0.029 | -0.071 |
| ote | 4h | 176 | 46.6 | 0.23 | 0.13 |
| pa_engulf | 1m | 52 | 42.3 | 0.103 | 0.003 |
| pa_inside | 1h | 93 | 46.2 | 0.171 | 0.071 |
| pa_pin | 1h | 82 | 42.7 | 0.18 | 0.08 |
| po3 | 15m | 66 | 40.9 | 0.058 | -0.042 |
| rsi_div | 1m | 200 | 45.0 | 0.142 | 0.042 |
| sess_amd | 1h | 212 | 36.3 | -0.058 | -0.158 |
| sma1040 | 1d | 67 | 47.8 | 0.304 | 0.204 |
| smt | 1h | 479 | 37.2 | -0.011 | -0.111 |
| sweep | 1m | 543 | 43.3 | 0.091 | -0.009 |
| tlbreak | 1m | 366 | 47.3 | 0.184 | 0.084 |
| turtle55 | 1d | 81 | 49.4 | 0.308 | 0.208 |
| unicorn | 15m | 91 | 42.9 | 0.179 | 0.079 |
| vwap | 1d | 426 | 35.4 | 0.035 | -0.065 |
| wavec | 1h | 38 | 60.5 | 0.526 | 0.426 |
| wyck | 4h | 47 | 55.3 | 0.432 | 0.332 |
| zombie | 1d | 47 | 40.4 | 0.137 | 0.037 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 72 | -0.002 | 43 | -0.074 |
| breaker | 206 | -0.123 | 184 | 0.088 |
| breakout | 504 | -0.041 | 604 | 0.069 |
| cisd | 529 | -0.064 | 470 | 0.074 |
| crt | 517 | -0.094 | 468 | -0.037 |
| dbl | 335 | -0.063 | 363 | 0.005 |
| donch | 1124 | -0.071 | 1635 | 0.053 |
| ema_stack | 2135 | -0.113 | 2764 | 0.075 |
| ew3 | 474 | -0.189 | 502 | 0.106 |
| ew5 | 79 | -0.05 | 130 | 0.065 |
| ew_r2_d1 | 208 | -0.051 | 344 | 0.136 |
| ew_r2_d2 | 103 | 0.022 | 192 | 0.171 |
| ew_r2_v | 413 | -0.042 | 535 | 0.051 |
| ew_r3_d1 | 88 | -0.134 | 150 | 0.058 |
| ew_r3_d2 | 43 | 0.144 | 118 | 0.132 |
| ew_r3_v | 133 | -0.027 | 218 | 0.175 |
| fib | 1176 | -0.066 | 1168 | 0.106 |
| fvg | 1648 | -0.013 | 1518 | 0.154 |
| harm_bat | 4 | -0.375 | 0 | None |
| harm_bat_tight | 1 | 1.5 | 0 | None |
| harm_butterfly | 13 | 0.195 | 9 | 0.667 |
| harm_butterfly_tight | 2 | 1.5 | 1 | 1.5 |
| harm_crab | 2 | 0.25 | 0 | None |
| harm_cypher | 3 | -0.779 | 6 | 1.5 |
| harm_cypher_tight | 0 | None | 3 | 1.5 |
| harm_gartley | 3 | 0.667 | 3 | 0.129 |
| harm_gartley_tight | 1 | -1.0 | 0 | None |
| harm_vol_bat | 3 | 0.667 | 1 | 1.5 |
| harm_vol_bat_tight | 1 | 1.5 | 0 | None |
| harm_vol_butterfly | 12 | 0.268 | 1 | 1.5 |
| harm_vol_butterfly_tight | 1 | -1.0 | 0 | None |
| harm_vol_crab | 1 | -1.0 | 0 | None |
| harm_vol_cypher | 2 | -1.0 | 9 | 0.944 |
| harm_vol_cypher_tight | 0 | None | 3 | 1.5 |
| harm_vol_gartley | 2 | 0.25 | 2 | 0.25 |
| harm_vol_gartley_tight | 1 | -1.0 | 0 | None |
| judas | 1382 | -0.034 | 1363 | 0.053 |
| kzs | 20 | -0.531 | 8 | -0.062 |
| level | 3221 | -0.058 | 1713 | 0.082 |
| liqline | 1259 | 0.017 | 1439 | 0.073 |
| m2022 | 343 | -0.101 | 353 | 0.102 |
| ma_cross | 1459 | -0.015 | 1386 | 0.053 |
| macd_div | 782 | 0.096 | 618 | 0.043 |
| msb_ob | 990 | -0.107 | 892 | 0.066 |
| ob | 748 | -0.178 | 804 | 0.053 |
| ohl_break | 417 | -0.075 | 481 | 0.067 |
| ohl_open | 1505 | -0.091 | 1626 | 0.092 |
| orb | 72 | 0.062 | 97 | 0.019 |
| ote | 408 | -0.056 | 388 | 0.209 |
| pa_engulf | 151 | -0.125 | 150 | -0.028 |
| pa_inside | 185 | -0.178 | 186 | 0.122 |
| pa_pin | 152 | 0.078 | 115 | -0.097 |
| pa_star | 19 | -0.211 | 20 | 0.0 |
| po3 | 64 | -0.055 | 63 | 0.085 |
| rect | 11 | -0.091 | 18 | -0.471 |
| rsi_div | 621 | 0.036 | 559 | 0.08 |
| sess_amd | 226 | -0.129 | 253 | -0.035 |
| sma1040 | 34 | 0.396 | 33 | 0.21 |
| smt | 944 | -0.102 | 859 | -0.028 |
| sweep | 2075 | -0.036 | 1605 | 0.048 |
| tlbreak | 1107 | -0.043 | 1126 | 0.069 |
| turtle55 | 43 | 0.198 | 38 | 0.433 |
| unicorn | 249 | -0.135 | 214 | 0.23 |
| vwap | 3307 | -0.082 | 4046 | 0.056 |
| wavec | 87 | 0.004 | 69 | 0.472 |
| wyck | 97 | 0.002 | 97 | 0.282 |
| zombie | 466 | -0.042 | 461 | -0.114 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 37826 | 37.3 | -0.016 | 26810 | 39.2 | 0.036 |
| abc | 29 | 27.6 | -0.243 | 86 | 38.4 | 0.043 |
| breaker | 177 | 34.5 | -0.055 | 212 | 36.3 | 0.008 |
| breakout | 773 | 40.0 | 0.03 | 330 | 38.2 | -0.008 |
| cisd | 361 | 31.9 | -0.152 | 633 | 40.1 | 0.08 |
| crt | 393 | 31.8 | -0.159 | 592 | 37.5 | -0.005 |
| dbl | 441 | 37.0 | -0.049 | 257 | 38.5 | 0.008 |
| donch | 2386 | 38.0 | -0.001 | 367 | 39.2 | 0.013 |
| ema_stack | 3920 | 37.7 | -0.006 | 959 | 37.9 | -0.01 |
| ew3 | 569 | 38.8 | 0.016 | 405 | 34.3 | -0.12 |
| ew5 | 160 | 41.9 | 0.141 | 49 | 24.5 | -0.366 |
| ew_r2_d1 | 337 | 38.0 | 0.052 | 215 | 40.5 | 0.087 |
| ew_r2_d2 | 166 | 38.0 | 0.059 | 129 | 43.4 | 0.196 |
| ew_r2_v | 564 | 35.6 | -0.028 | 383 | 39.9 | 0.069 |
| ew_r3_d1 | 204 | 34.8 | 0.007 | 34 | 32.4 | -0.13 |
| ew_r3_d2 | 133 | 39.1 | 0.122 | 28 | 46.4 | 0.198 |
| ew_r3_v | 302 | 42.1 | 0.158 | 49 | 26.5 | -0.265 |
| fib | 1156 | 38.6 | 0.016 | 1183 | 38.4 | 0.021 |
| fvg | 1792 | 39.7 | 0.056 | 1358 | 41.4 | 0.081 |
| harm_bat | 0 | None | None | 4 | 25.0 | -0.375 |
| harm_bat_tight | 0 | None | None | 1 | 100.0 | 1.5 |
| harm_butterfly | 7 | 71.4 | 0.786 | 15 | 46.7 | 0.203 |
| harm_butterfly_tight | 1 | 100.0 | 1.5 | 2 | 100.0 | 1.5 |
| harm_crab | 0 | None | None | 2 | 50.0 | 0.25 |
| harm_cypher | 2 | 50.0 | 0.582 | 7 | 71.4 | 0.786 |
| harm_cypher_tight | 1 | 100.0 | 1.5 | 2 | 100.0 | 1.5 |
| harm_gartley | 4 | 50.0 | 0.471 | 2 | 50.0 | 0.25 |
| harm_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| harm_vol_bat | 0 | None | None | 4 | 75.0 | 0.875 |
| harm_vol_bat_tight | 0 | None | None | 1 | 100.0 | 1.5 |
| harm_vol_butterfly | 3 | 66.7 | 0.667 | 10 | 40.0 | 0.272 |
| harm_vol_butterfly_tight | 0 | None | None | 1 | 0.0 | -1.0 |
| harm_vol_crab | 0 | None | None | 1 | 0.0 | -1.0 |
| harm_vol_cypher | 4 | 50.0 | 0.25 | 7 | 71.4 | 0.786 |
| harm_vol_cypher_tight | 2 | 100.0 | 1.5 | 1 | 100.0 | 1.5 |
| harm_vol_gartley | 2 | 0.0 | -1.0 | 2 | 100.0 | 1.5 |
| harm_vol_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| judas | 1811 | 38.9 | 0.001 | 922 | 38.8 | 0.017 |
| kzs | 12 | 8.3 | -0.792 | 16 | 31.2 | -0.101 |
| level | 2303 | 36.1 | -0.056 | 2605 | 39.1 | 0.031 |
| liqline | 1517 | 39.3 | 0.023 | 1176 | 40.7 | 0.079 |
| m2022 | 417 | 39.3 | 0.037 | 276 | 35.1 | -0.059 |
| ma_cross | 1686 | 37.2 | -0.017 | 1145 | 40.6 | 0.063 |
| macd_div | 314 | 38.5 | 0.005 | 1084 | 41.1 | 0.091 |
| msb_ob | 940 | 34.9 | -0.069 | 937 | 38.6 | 0.021 |
| ob | 851 | 33.4 | -0.108 | 697 | 37.0 | 0.001 |
| ohl_break | 496 | 38.5 | -0.008 | 398 | 38.7 | 0.016 |
| ohl_open | 1678 | 36.8 | -0.038 | 1449 | 39.8 | 0.053 |
| orb | 104 | 37.5 | -0.062 | 65 | 43.1 | 0.197 |
| ote | 343 | 40.8 | 0.077 | 452 | 40.9 | 0.073 |
| pa_engulf | 137 | 30.7 | -0.185 | 164 | 38.4 | 0.013 |
| pa_inside | 221 | 36.2 | -0.056 | 150 | 38.0 | 0.013 |
| pa_pin | 104 | 37.5 | 0.005 | 161 | 36.6 | 0.013 |
| pa_star | 12 | 16.7 | -0.583 | 27 | 44.4 | 0.111 |
| po3 | 63 | 39.7 | 0.006 | 63 | 38.1 | 0.0 |
| rect | 18 | 27.8 | -0.193 | 11 | 18.2 | -0.545 |
| rsi_div | 324 | 41.0 | 0.077 | 855 | 38.8 | 0.048 |
| sess_amd | 224 | 34.8 | -0.104 | 253 | 36.0 | -0.051 |
| sma1040 | 28 | 39.3 | 0.032 | 39 | 53.8 | 0.5 |
| smt | 920 | 32.6 | -0.147 | 883 | 38.8 | 0.016 |
| sweep | 1596 | 35.2 | -0.063 | 2081 | 39.7 | 0.049 |
| tlbreak | 1072 | 37.7 | -0.016 | 1159 | 39.6 | 0.04 |
| turtle55 | 61 | 47.5 | 0.262 | 20 | 55.0 | 0.45 |
| unicorn | 231 | 35.1 | -0.048 | 229 | 39.7 | 0.097 |
| vwap | 5841 | 37.5 | -0.011 | 1498 | 38.7 | 0.007 |
| wavec | 45 | 46.7 | 0.327 | 110 | 44.5 | 0.152 |
| wyck | 90 | 37.8 | -0.016 | 103 | 48.5 | 0.292 |
| zombie | 476 | 34.7 | -0.076 | 451 | 35.3 | -0.079 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7658 | 31.2 | -0.047 |
| Mon | 11529 | 40.6 | 0.043 |
| Sat | 6596 | 37.5 | -0.011 |
| Sun | 7534 | 35.6 | -0.073 |
| Thu | 7576 | 39.0 | 0.039 |
| Tue | 16173 | 39.9 | 0.02 |
| Wed | 7741 | 40.0 | 0.035 |
| Asia 00-07 | 19235 | 37.8 | -0.019 |
| Late 20-24 | 12641 | 38.0 | -0.004 |
| London 07-12 | 10556 | 40.1 | 0.029 |
| New York 12-20 | 18649 | 37.8 | 0.018 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 64807 | 38.1 | 0.006 | -0.005 | +1.76 | 27952 | -0.025 | 36855 | 0.03 |  |
| grade A+++ | 534 | 41.4 | 0.135 | 0.02 | +1.63 | 223 | 0.238 | 311 | 0.06 |  |
| grade A+ | 8778 | 38.8 | 0.037 | 0.006 | +1.82 | 3598 | 0.052 | 5180 | 0.027 |  |
| grade A | 19575 | 36.9 | -0.01 | -0.004 | -0.53 | 8112 | -0.067 | 11463 | 0.03 |  |
| grade B | 23354 | 38.3 | 0.004 | -0.015 | +1.89 | 10381 | -0.025 | 12973 | 0.027 |  |
| grade C | 12566 | 39.2 | 0.008 | 0.005 | +0.22 | 5638 | -0.027 | 6928 | 0.036 |  |
| layer htf | 37826 | 37.3 | -0.016 | -0.003 | -1.59 | 16208 | -0.059 | 21618 | 0.016 |  |
| layer loc | 14109 | 38.5 | 0.019 | -0.005 | +1.84 | 5930 | 0.047 | 8179 | -0.001 |  |
| layer vol | 21107 | 39.0 | 0.025 | -0.024 | +4.51 | 9129 | -0.01 | 11978 | 0.051 |  |
| layer reg | 48089 | 37.7 | 0.008 | -0.009 | +2.43 | 20744 | -0.015 | 27345 | 0.026 |  |
| layer time | 32931 | 38.4 | 0.024 | 0.017 | +0.83 | 13401 | -0.012 | 19530 | 0.049 |  |
| no htf | 26981 | 39.3 | 0.037 | -0.007 | +4.65 | 11744 | 0.021 | 15237 | 0.05 | YES |
| no loc | 50698 | 38.0 | 0.003 | -0.005 | +1.02 | 22022 | -0.045 | 28676 | 0.039 |  |
| no vol | 43700 | 37.7 | -0.003 | 0.005 | -0.99 | 18823 | -0.033 | 24877 | 0.02 |  |
| no reg | 16718 | 39.5 | -0.001 | 0.007 | -0.65 | 7208 | -0.055 | 9510 | 0.04 |  |
| no time | 31876 | 37.9 | -0.013 | -0.027 | +1.66 | 14551 | -0.038 | 17325 | 0.008 |  |
| grade A / turtle55 | 34 | 58.8 | 0.549 | 0.533 | +0.05 | 14 | 0.492 | 20 | 0.589 |  |
| loc / ew_r3_d2 | 36 | 55.6 | 0.447 | 0.063 | +1.35 | 16 | 0.148 | 20 | 0.687 |  |
| grade A+ / ew_r3_v | 38 | 52.6 | 0.364 | 0.12 | +0.83 | 17 | 0.324 | 21 | 0.396 |  |
| no loc / sma1040 | 64 | 50.0 | 0.358 | 0.166 | +0.92 | 18 | 0.25 | 46 | 0.4 |  |
| no loc / turtle55 | 81 | 49.4 | 0.308 | 0.329 | -0.11 | 31 | 0.348 | 50 | 0.283 |  |
| grade A+ / ew_r2_d2 | 57 | 45.6 | 0.29 | -0.11 | +1.79 | 20 | 0.5 | 37 | 0.176 |  |
| grade C / wavec | 50 | 50.0 | 0.287 | 0.037 | +1.15 | 17 | 0.618 | 33 | 0.117 |  |
| grade A / ew_r3_d2 | 69 | 44.9 | 0.261 | 0.061 | +0.99 | 23 | 0.024 | 46 | 0.38 |  |
| no loc / wyck | 77 | 46.8 | 0.24 | 0.116 | +0.70 | 34 | 0.412 | 43 | 0.105 |  |
| grade A / ew_r3_v | 152 | 43.4 | 0.238 | -0.116 | +2.66 | 51 | 0.011 | 101 | 0.353 |  |
| loc / abc | 47 | 44.7 | 0.233 | 0.075 | +0.72 | 11 | 0.591 | 36 | 0.124 |  |
| loc / wavec | 59 | 47.5 | 0.215 | 0.271 | -0.29 | 20 | 0.25 | 39 | 0.197 |  |
| grade C / breakout | 97 | 48.5 | 0.211 | 0.126 | +0.52 | 37 | 0.486 | 60 | 0.042 |  |
| grade C / ote | 143 | 46.2 | 0.21 | -0.079 | +2.13 | 71 | 0.152 | 72 | 0.267 |  |
| no loc / wavec | 97 | 44.3 | 0.208 | -0.02 | +1.46 | 36 | 0.201 | 61 | 0.213 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8037 | 4164 | 51.8 |
| sweep | vwap | 6544 | 3998 | 61.1 |
| ema_stack | sweep | 3311 | 2451 | 74.0 |
| ema_stack | level | 3848 | 2115 | 55.0 |
| fvg | vwap | 4548 | 1818 | 40.0 |
| ohl_open | vwap | 4081 | 1768 | 43.3 |
| macd_div | vwap | 2092 | 1652 | 79.0 |
| level | sweep | 3695 | 1568 | 42.4 |
| msb_ob | vwap | 2732 | 1514 | 55.4 |
| fib | vwap | 2977 | 1489 | 50.0 |
| judas | level | 2944 | 1470 | 49.9 |
| rsi_div | vwap | 1824 | 1419 | 77.8 |
| fvg | level | 3162 | 1388 | 43.9 |
| ma_cross | sweep | 2105 | 1350 | 64.1 |
| smt | vwap | 2934 | 1331 | 45.4 |
| level | ma_cross | 2566 | 1326 | 51.7 |
| ob | vwap | 2496 | 1320 | 52.9 |
| liqline | vwap | 3538 | 1271 | 35.9 |
| ma_cross | vwap | 4234 | 1250 | 29.5 |
| tlbreak | vwap | 2641 | 1244 | 47.1 |
| judas | sweep | 2014 | 1211 | 60.1 |
| judas | vwap | 4537 | 1199 | 26.4 |
| level | ohl_open | 2265 | 1192 | 52.6 |
| fvg | ohl_open | 1236 | 1015 | 82.1 |
| liqline | sweep | 1852 | 998 | 53.9 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 24 | 50.0 | 0.393 |
| 2 families | 424 | 40.3 | 0.076 |
| 2 families (with opposition) | 1331 | 38.5 | 0.016 |
| 3 families | 1134 | 39.5 | 0.06 |
| 3 families (with opposition) | 4696 | 37.8 | -0.004 |
| 4+ families | 970 | 38.1 | 0.006 |
| 4+ families (with opposition) | 4222 | 37.8 | -0.004 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 83.1 | 27731 | 83.3 | 383252 | -0.9 |
| 1m shapes 120/180/240/360 deg | 80.7 | 11768 | 80.5 | 11753 | +0.3 |
| 15m | 65.1 | 19524 | 65.2 | 270320 | -0.1 |
| 15m shapes 120/180/240/360 deg | 63.9 | 9908 | 64.0 | 9905 | -0.2 |
| 1h | 58.2 | 16082 | 58.0 | 222574 | +0.5 |
| 1h shapes 120/180/240/360 deg | 57.0 | 8823 | 57.3 | 8801 | -0.6 |
| 4h | 56.6 | 12020 | 57.7 | 166096 | -2.5 |
| 4h shapes 120/180/240/360 deg | 56.9 | 6772 | 56.7 | 6776 | +0.4 |
| 1d | 55.4 | 3196 | 56.0 | 42940 | -0.7 |
| 1d shapes 120/180/240/360 deg | 57.3 | 2034 | 57.3 | 2039 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 55 | 16.4 | +0.203 | -0.787 | +1.86 |
| 1d | 57 | 43.9 | +0.113 | +0.338 | -0.85 |
| 1h | 87 | 31.0 | +0.465 | +0.457 | +0.03 |
| 4h | 87 | 27.6 | -0.004 | +0.047 | -0.18 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2401 | -0.108 |
| 15 days around full moon | 2325 | 0.034 |

Difference t = -1.75 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 64807 | 48.9 | -0.022 | -0.122 | -1397.0 | -5.54 |
| rr1.5 | 64807 | 40.8 | 0.006 | -0.094 | 395.0 | +1.29 |
| rr2.0 | 64807 | 35.5 | 0.016 | -0.084 | 1059.4 | +3.03 |
| rr3.0 | 64807 | 30.0 | 0.039 | -0.061 | 2506.6 | +5.99 |
| rr1.5_be | 64807 | 34.9 | 0.003 | -0.097 | 170.2 | +0.60 |
| rr2.0_be | 64807 | 27.8 | 0.017 | -0.083 | 1102.3 | +3.51 |
| rr1.5_h16 | 64807 | 42.4 | 0.009 | -0.091 | 568.4 | +1.97 |
| rr2.0_h16 | 64807 | 39.0 | 0.018 | -0.082 | 1160.4 | +3.62 |
| pt_1.5_3 | 64807 | 48.8 | 0.037 | -0.063 | 2370.6 | +7.93 |
| pt_1.0_3 | 64807 | 48.9 | 0.022 | -0.078 | 1457.8 | +5.23 |
| pt_1.5_5 | 64807 | 48.8 | 0.055 | -0.045 | 3552.3 | +11.43 |
| trail_only | 64807 | 48.8 | 0.103 | 0.003 | 6674.2 | +18.41 |

## Exit variant x timeframe x trend (is the htf sign flip caused by the exit? docs/PREREG_2026-11-01.md)

Same entries, every detector pooled. If 'with' stays below 'against' on 1h / 1m under every exit, the exit is not the cause.

| tf | exit | with n | with avg R | with t | against n | against avg R | against t |
|---|---|---|---|---|---|---|---|
| 15m | rr1.0 | 10463 | -0.042 | -4.35 | 7345 | -0.026 | -2.28 |
| 15m | rr1.5 | 10463 | -0.028 | -2.41 | 7345 | 0.002 | +0.17 |
| 15m | rr2.0 | 10463 | -0.016 | -1.22 | 7345 | 0.011 | +0.69 |
| 15m | rr3.0 | 10463 | 0.03 | +1.83 | 7345 | 0.025 | +1.33 |
| 15m | rr1.5_be | 10463 | -0.023 | -2.13 | 7345 | -0.023 | -1.77 |
| 15m | rr2.0_be | 10463 | -0.01 | -0.85 | 7345 | -0.016 | -1.13 |
| 15m | rr1.5_h16 | 10463 | -0.02 | -1.82 | 7345 | -0.004 | -0.29 |
| 15m | rr2.0_h16 | 10463 | -0.017 | -1.35 | 7345 | 0.016 | +1.10 |
| 15m | pt_1.5_3 | 10463 | 0.016 | +1.43 | 7345 | 0.004 | +0.32 |
| 15m | pt_1.0_3 | 10463 | 0.003 | +0.25 | 7345 | 0.003 | +0.27 |
| 15m | pt_1.5_5 | 10463 | 0.041 | +3.41 | 7345 | 0.019 | +1.38 |
| 15m | trail_only | 10463 | 0.097 | +6.75 | 7345 | 0.063 | +3.92 |
| 1d | rr1.0 | 2200 | -0.076 | -3.69 | 1526 | 0.096 | +3.85 |
| 1d | rr1.5 | 2200 | -0.051 | -2.10 | 1526 | 0.182 | +5.99 |
| 1d | rr2.0 | 2200 | -0.027 | -0.98 | 1526 | 0.267 | +7.68 |
| 1d | rr3.0 | 2200 | -0.007 | -0.22 | 1526 | 0.363 | +8.73 |
| 1d | rr1.5_be | 2200 | -0.059 | -2.56 | 1526 | 0.159 | +5.52 |
| 1d | rr2.0_be | 2200 | -0.031 | -1.23 | 1526 | 0.226 | +6.95 |
| 1d | rr1.5_h16 | 2200 | -0.044 | -1.86 | 1526 | 0.155 | +5.22 |
| 1d | rr2.0_h16 | 2200 | -0.008 | -0.32 | 1526 | 0.218 | +6.50 |
| 1d | pt_1.5_3 | 2200 | -0.033 | -1.36 | 1526 | 0.202 | +6.58 |
| 1d | pt_1.0_3 | 2200 | -0.044 | -1.96 | 1526 | 0.169 | +5.96 |
| 1d | pt_1.5_5 | 2200 | -0.035 | -1.46 | 1526 | 0.219 | +6.92 |
| 1d | trail_only | 2200 | -0.017 | -0.65 | 1526 | 0.277 | +7.47 |
| 1h | rr1.0 | 10070 | -0.038 | -3.86 | 7536 | 0.002 | +0.20 |
| 1h | rr1.5 | 10070 | -0.045 | -3.81 | 7536 | 0.054 | +3.85 |
| 1h | rr2.0 | 10070 | -0.038 | -2.79 | 7536 | 0.056 | +3.52 |
| 1h | rr3.0 | 10070 | -0.064 | -4.05 | 7536 | 0.044 | +2.34 |
| 1h | rr1.5_be | 10070 | -0.036 | -3.32 | 7536 | 0.031 | +2.42 |
| 1h | rr2.0_be | 10070 | -0.023 | -1.94 | 7536 | 0.048 | +3.36 |
| 1h | rr1.5_h16 | 10070 | -0.025 | -2.25 | 7536 | 0.038 | +2.95 |
| 1h | rr2.0_h16 | 10070 | -0.026 | -2.09 | 7536 | 0.041 | +2.85 |
| 1h | pt_1.5_3 | 10070 | -0.014 | -1.27 | 7536 | 0.053 | +3.95 |
| 1h | pt_1.0_3 | 10070 | -0.018 | -1.66 | 7536 | 0.038 | +3.03 |
| 1h | pt_1.5_5 | 10070 | -0.002 | -0.20 | 7536 | 0.054 | +4.03 |
| 1h | trail_only | 10070 | 0.027 | +2.03 | 7536 | 0.077 | +5.09 |
| 1m | rr1.0 | 7162 | -0.074 | -6.30 | 4867 | 0.049 | +3.41 |
| 1m | rr1.5 | 7162 | 0.0 | +0.01 | 4867 | 0.118 | +6.64 |
| 1m | rr2.0 | 7162 | 0.026 | +1.53 | 4867 | 0.148 | +7.13 |
| 1m | rr3.0 | 7162 | 0.098 | +4.74 | 4867 | 0.186 | +7.25 |
| 1m | rr1.5_be | 7162 | -0.008 | -0.62 | 4867 | 0.129 | +7.72 |
| 1m | rr2.0_be | 7162 | 0.023 | +1.50 | 4867 | 0.166 | +8.84 |
| 1m | rr1.5_h16 | 7162 | -0.004 | -0.32 | 4867 | 0.125 | +7.33 |
| 1m | rr2.0_h16 | 7162 | 0.023 | +1.49 | 4867 | 0.153 | +7.98 |
| 1m | pt_1.5_3 | 7162 | 0.056 | +3.78 | 4867 | 0.212 | +11.54 |
| 1m | pt_1.0_3 | 7162 | 0.022 | +1.58 | 4867 | 0.166 | +9.84 |
| 1m | pt_1.5_5 | 7162 | 0.098 | +6.20 | 4867 | 0.262 | +13.22 |
| 1m | trail_only | 7162 | 0.202 | +10.37 | 4867 | 0.385 | +15.61 |
| 4h | rr1.0 | 7931 | 0.008 | +0.73 | 5536 | -0.029 | -2.14 |
| 4h | rr1.5 | 7931 | 0.031 | +2.31 | 5536 | -0.056 | -3.53 |
| 4h | rr2.0 | 7931 | 0.037 | +2.42 | 5536 | -0.091 | -5.18 |
| 4h | rr3.0 | 7931 | 0.088 | +4.94 | 5536 | -0.113 | -5.66 |
| 4h | rr1.5_be | 7931 | 0.023 | +1.85 | 5536 | -0.036 | -2.42 |
| 4h | rr2.0_be | 7931 | 0.026 | +1.89 | 5536 | -0.057 | -3.59 |
| 4h | rr1.5_h16 | 7931 | 0.031 | +2.48 | 5536 | -0.04 | -2.71 |
| 4h | rr2.0_h16 | 7931 | 0.028 | +1.97 | 5536 | -0.057 | -3.48 |
| 4h | pt_1.5_3 | 7931 | 0.046 | +3.59 | 5536 | -0.035 | -2.34 |
| 4h | pt_1.0_3 | 7931 | 0.036 | +2.98 | 5536 | -0.03 | -2.16 |
| 4h | pt_1.5_5 | 7931 | 0.051 | +3.89 | 5536 | -0.027 | -1.76 |
| 4h | trail_only | 7931 | 0.073 | +4.98 | 5536 | -0.016 | -0.95 |
