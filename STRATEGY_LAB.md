# Strategy lab - real candles (2026-11-13)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 67 | 47.8 | 0.298 | 0.198 | 32.8 | -0.091 |  |
| 2 | turtle55 | Trend (hedge fund) | 80 | 48.8 | 0.293 | 0.193 | 53.8 | 0.453 |  |
| 3 | wyck | Wyckoff | 177 | 48.0 | 0.27 | 0.17 | 38.4 | 0.046 |  |
| 4 | ew_r3_d2 | Elliott wave | 148 | 40.5 | 0.141 | 0.041 | 37.2 | 0.055 |  |
| 5 | orb | Time (sessions) | 172 | 42.4 | 0.08 | -0.02 | 35.5 | -0.066 |  |
| 6 | ote | Fibonacci | 785 | 41.0 | 0.075 | -0.025 | 37.3 | -0.02 |  |
| 7 | sess_amd | Time (sessions) | 520 | 41.2 | 0.068 | -0.032 | 36.2 | -0.067 |  |
| 8 | ew_r2_d2 | Elliott wave | 288 | 39.2 | 0.066 | -0.034 | 33.7 | -0.036 |  |
| 9 | fvg | SMC / ICT | 3161 | 40.3 | 0.058 | -0.042 | 38.5 | 0.016 |  |
| 10 | ew_r3_v | Elliott wave | 358 | 37.2 | 0.051 | -0.049 | 34.4 | -0.028 |  |
| 11 | breaker | SMC / ICT | 410 | 37.8 | 0.045 | -0.055 | 33.4 | -0.095 |  |
| 12 | msb_ob | SMC / ICT | 1911 | 39.2 | 0.039 | -0.061 | 37.9 | 0.005 |  |
| 13 | ew_r3_d1 | Elliott wave | 233 | 35.2 | 0.037 | -0.063 | 33.9 | 0.012 |  |
| 14 | fib | Fibonacci | 2386 | 38.7 | 0.025 | -0.075 | 38.9 | 0.031 |  |
| 15 | ew_r2_d1 | Elliott wave | 529 | 38.0 | 0.024 | -0.076 | 34.0 | -0.055 |  |
| 16 | ew5 | Elliott wave | 183 | 35.0 | 0.018 | -0.082 | 27.9 | -0.114 |  |
| 17 | wavec | Elliott wave | 141 | 37.6 | 0.018 | -0.082 | 39.7 | 0.054 |  |
| 18 | ob | SMC / ICT | 1604 | 38.0 | 0.015 | -0.085 | 37.5 | 0.007 |  |
| 19 | unicorn | SMC / ICT | 463 | 37.4 | 0.011 | -0.089 | 38.0 | 0.017 |  |
| 20 | donch | Trend (hedge fund) | 2727 | 38.7 | 0.008 | -0.092 | 37.1 | -0.02 |  |
| 21 | rsi_div | Momentum / divergence | 1187 | 37.6 | 0.008 | -0.092 | 40.4 | 0.092 |  |
| 22 | judas | Time (sessions) | 2596 | 39.3 | 0.006 | -0.094 | 38.9 | 0.003 |  |
| 23 | macd_div | Momentum / divergence | 1435 | 37.6 | 0.005 | -0.095 | 36.2 | -0.029 |  |
| 24 | vwap | Trend (MA) | 7392 | 38.2 | 0.003 | -0.097 | 37.6 | -0.008 |  |
| 25 | pa_inside | Price action | 366 | 38.3 | -0.001 | -0.101 | 38.5 | -0.002 |  |
| 26 | ohl_open | Levels / breakouts | 3258 | 37.8 | -0.004 | -0.104 | 37.1 | -0.021 |  |
| 27 | ema_stack | Trend (MA) | 4922 | 37.8 | -0.006 | -0.106 | 38.1 | 0.01 |  |
| 28 | level | Levels / breakouts | 4974 | 38.0 | -0.008 | -0.108 | 37.5 | -0.015 |  |
| 29 | sweep | Liquidity | 3685 | 37.2 | -0.01 | -0.11 | 37.6 | -0.001 |  |
| 30 | cisd | SMC / ICT | 979 | 37.3 | -0.014 | -0.114 | 39.9 | 0.06 |  |
| 31 | ma_cross | Trend (MA) | 2852 | 37.2 | -0.017 | -0.117 | 37.2 | -0.016 |  |
| 32 | pa_pin | Price action | 267 | 36.0 | -0.019 | -0.119 | 32.6 | -0.139 |  |
| 33 | dbl | Chart patterns (range) | 725 | 37.7 | -0.025 | -0.125 | 37.8 | 0.0 |  |
| 34 | ew3 | Elliott wave | 1009 | 37.5 | -0.029 | -0.129 | 38.9 | 0.019 |  |
| 35 | abc | Elliott wave | 101 | 36.6 | -0.032 | -0.132 | 46.5 | 0.236 |  |
| 36 | tlbreak | Levels / breakouts | 2206 | 36.8 | -0.033 | -0.133 | 38.1 | 0.009 |  |
| 37 | breakout | Levels / breakouts | 1041 | 37.3 | -0.034 | -0.134 | 38.0 | -0.001 |  |
| 38 | m2022 | SMC / ICT | 660 | 35.9 | -0.034 | -0.134 | 36.1 | -0.024 |  |
| 39 | liqline | Liquidity | 2693 | 36.6 | -0.038 | -0.138 | 36.6 | -0.03 |  |
| 40 | zombie | Liquidity | 903 | 36.5 | -0.046 | -0.146 | 35.4 | -0.054 |  |
| 41 | pa_engulf | Price action | 300 | 36.7 | -0.049 | -0.149 | 35.3 | -0.069 |  |
| 42 | ew_r2_v | Elliott wave | 943 | 34.8 | -0.058 | -0.158 | 37.3 | 0.023 |  |
| 43 | smt | Intermarket (SMT) | 1851 | 35.7 | -0.066 | -0.166 | 38.2 | 0.014 |  |
| 44 | ohl_break | Levels / breakouts | 765 | 35.7 | -0.076 | -0.176 | 40.5 | 0.068 |  |
| 45 | crt | Liquidity | 969 | 33.0 | -0.111 | -0.211 | 35.5 | -0.045 |  |
| 46 | po3 | Time (sessions) | 124 | 34.7 | -0.115 | -0.215 | 32.3 | -0.168 |  |
| 47 | kzs | Time (sessions) | 30 | 26.7 | -0.333 | -0.433 | 50.0 | 0.25 |  |
| 48 | pa_star | Price action | 47 | 17.0 | -0.542 | -0.642 | 46.8 | 0.18 |  |
| 49 | harm_cypher_tight | Harmonic: Cypher | 5 | 100.0 | 1.5 | 1.4 | 20.0 | -0.5 |  |
| 50 | harm_crab | Harmonic: Crab | 1 | 100.0 | 1.5 | 1.4 | 100.0 | 1.5 |  |
| 51 | harm_vol_cypher_tight | Harmonic: Cypher (vol swings) | 4 | 100.0 | 1.5 | 1.4 | 50.0 | 0.25 |  |
| 52 | harm_butterfly_tight | Harmonic: Butterfly | 3 | 100.0 | 1.5 | 1.4 | 100.0 | 1.5 |  |
| 53 | harm_bat_tight | Harmonic: Bat | 1 | 100.0 | 1.5 | 1.4 | 100.0 | 1.5 |  |
| 54 | harm_cypher | Harmonic: Cypher | 13 | 76.9 | 0.923 | 0.823 | 46.2 | 0.154 |  |
| 55 | harm_butterfly | Harmonic: Butterfly | 20 | 50.0 | 0.277 | 0.177 | 45.0 | 0.212 |  |
| 56 | harm_vol_gartley | Harmonic: Gartley (vol swings) | 6 | 50.0 | 0.25 | 0.15 | 16.7 | -0.583 |  |
| 57 | harm_gartley | Harmonic: Gartley | 6 | 50.0 | 0.25 | 0.15 | 0.0 | -1.0 |  |
| 58 | harm_vol_butterfly | Harmonic: Butterfly (vol swings) | 9 | 44.4 | 0.171 | 0.071 | 33.3 | -0.107 |  |
| 59 | harm_vol_cypher | Harmonic: Cypher (vol swings) | 22 | 45.5 | 0.136 | 0.036 | 54.5 | 0.364 |  |
| 60 | rect | Chart patterns (range) | 27 | 40.7 | 0.019 | -0.081 | 48.1 | 0.317 |  |
| 61 | harm_vol_bat | Harmonic: Bat (vol swings) | 3 | 33.3 | -0.167 | -0.267 | 33.3 | -0.167 |  |
| 62 | harm_bat | Harmonic: Bat | 4 | 25.0 | -0.375 | -0.475 | 75.0 | 0.875 |  |
| 63 | harm_vol_butterfly_tight | Harmonic: Butterfly (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 64 | harm_gartley_tight | Harmonic: Gartley | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 65 | harm_vol_gartley_tight | Harmonic: Gartley (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 66 | harm_vol_crab | Harmonic: Crab (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 100.0 | 1.5 |  |

## Stop study: where should the stop sit? (same entries, target fixed at 2.25 ATR, results in ATR, cost 0.15 ATR)

| group | stop | n | target hit % | stopped % | avg ATR | net ATR | mirror avg ATR | t (net vs 0) |
|---|---|---|---|---|---|---|---|---|
| all | 1.0 ATR | 64751 | 30.3 | 67.5 | 0.017 | -0.133 | 0.046 | -22.67 |
| all | 1.5 ATR | 64751 | 37.8 | 57.7 | -0.004 | -0.154 | 0.024 | -21.75 |
| all | 2.0 ATR | 64751 | 43.2 | 49.9 | -0.022 | -0.172 | 0.015 | -21.26 |
| all | 2.5 ATR | 64751 | 47.1 | 43.3 | -0.038 | -0.188 | -0.004 | -20.98 |
| all | 3.0 ATR | 64751 | 50.1 | 38.0 | -0.05 | -0.2 | -0.016 | -20.59 |
| 1m | 1.0 ATR | 12625 | 32.8 | 66.6 | 0.073 | -0.077 | 0.137 | -5.64 |
| 1m | 1.5 ATR | 12625 | 39.8 | 59.2 | 0.009 | -0.141 | 0.075 | -8.65 |
| 1m | 2.0 ATR | 12625 | 45.4 | 52.9 | -0.032 | -0.182 | 0.066 | -9.71 |
| 1m | 2.5 ATR | 12625 | 49.6 | 47.7 | -0.081 | -0.231 | 0.013 | -11.04 |
| 1m | 3.0 ATR | 12625 | 53.3 | 42.9 | -0.102 | -0.252 | 0.002 | -11.02 |
| 15m | 1.0 ATR | 17669 | 29.8 | 68.1 | -0.0 | -0.15 | 0.062 | -13.46 |
| 15m | 1.5 ATR | 17669 | 37.7 | 58.4 | -0.02 | -0.17 | 0.033 | -12.51 |
| 15m | 2.0 ATR | 17669 | 43.7 | 50.5 | -0.028 | -0.178 | 0.038 | -11.42 |
| 15m | 2.5 ATR | 17669 | 47.8 | 44.5 | -0.05 | -0.2 | 0.014 | -11.61 |
| 15m | 3.0 ATR | 17669 | 51.2 | 39.2 | -0.055 | -0.205 | -0.018 | -10.92 |
| 1h | 1.0 ATR | 17524 | 29.7 | 67.3 | 0.009 | -0.141 | 0.03 | -12.58 |
| 1h | 1.5 ATR | 17524 | 37.1 | 57.7 | -0.019 | -0.169 | 0.024 | -12.53 |
| 1h | 2.0 ATR | 17524 | 42.4 | 50.1 | -0.047 | -0.197 | 0.019 | -12.73 |
| 1h | 2.5 ATR | 17524 | 46.5 | 43.7 | -0.057 | -0.207 | 0.016 | -12.09 |
| 1h | 3.0 ATR | 17524 | 49.4 | 39.2 | -0.09 | -0.24 | 0.019 | -12.86 |
| 4h | 1.0 ATR | 13233 | 29.3 | 68.4 | -0.009 | -0.159 | -0.033 | -12.36 |
| 4h | 1.5 ATR | 13233 | 37.6 | 57.1 | 0.006 | -0.144 | -0.038 | -9.20 |
| 4h | 2.0 ATR | 13233 | 42.8 | 48.0 | 0.014 | -0.136 | -0.06 | -7.68 |
| 4h | 2.5 ATR | 13233 | 46.2 | 39.6 | 0.029 | -0.121 | -0.047 | -6.27 |
| 4h | 3.0 ATR | 13233 | 48.4 | 33.0 | 0.046 | -0.104 | -0.048 | -5.03 |
| 1d | 1.0 ATR | 3700 | 29.9 | 65.8 | 0.04 | -0.11 | 0.014 | -4.52 |
| 1d | 1.5 ATR | 3700 | 36.5 | 52.0 | 0.064 | -0.086 | 0.024 | -2.98 |
| 1d | 2.0 ATR | 3700 | 39.2 | 43.3 | 0.029 | -0.121 | -0.022 | -3.76 |
| 1d | 2.5 ATR | 3700 | 41.4 | 34.3 | 0.028 | -0.122 | -0.086 | -3.52 |
| 1d | 3.0 ATR | 3700 | 42.4 | 27.8 | 0.005 | -0.145 | -0.122 | -3.92 |

| group | question | n | value |
|---|---|---|---|
| all | stopped at 1.5 ATR, target reached later | 47437 | 30.9 % reached it later (mirror direction 31.8 %); 73.3 % of all trades were stopped |
| all | MAE of trades that reached the target (ATR) | 39575 | p50 1.01 · p75 2.31 · p90 4.47 |
| 1m | stopped at 1.5 ATR, target reached later | 9889 | 34.1 % reached it later (mirror direction 36.0 %); 78.3 % of all trades were stopped |
| 1m | MAE of trades that reached the target (ATR) | 8444 | p50 1.04 · p75 2.59 · p90 4.87 |
| 15m | stopped at 1.5 ATR, target reached later | 13286 | 34.8 % reached it later (mirror direction 33.7 %); 75.2 % of all trades were stopped |
| 15m | MAE of trades that reached the target (ATR) | 11387 | p50 1.13 · p75 2.58 · p90 5.09 |
| 1h | stopped at 1.5 ATR, target reached later | 13223 | 32.8 % reached it later (mirror direction 35.5 %); 75.5 % of all trades were stopped |
| 1h | MAE of trades that reached the target (ATR) | 10969 | p50 1.07 · p75 2.57 · p90 4.76 |
| 4h | stopped at 1.5 ATR, target reached later | 8940 | 22.9 % reached it later (mirror direction 23.7 %); 67.6 % of all trades were stopped |
| 4h | MAE of trades that reached the target (ATR) | 7123 | p50 0.87 · p75 1.76 · p90 3.03 |
| 1d | stopped at 1.5 ATR, target reached later | 2099 | 13.5 % reached it later (mirror direction 12.8 %); 56.7 % of all trades were stopped |
| 1d | MAE of trades that reached the target (ATR) | 1652 | p50 0.69 · p75 1.21 · p90 2.16 |

Reading: a stop that is never reached only helps if the AVERAGE (net ATR) goes up, not just the target-hit share; compare with the mirror column (the opposite direction on the same bars).


## Pre-registered tests (signals after the freeze date only; docs/PREREG_2026-11-01.md)

| hypothesis | n | win % | avg R | net avg R | t vs random | net 1st half (n) | net 2nd half (n) | PASS |
|---|---|---|---|---|---|---|---|---|
| H1 sess_amd + loc | 107 | 39.3 | 0.058 | -0.042 | +0.66 | -0.066 (53) | -0.018 (54) |  |
| H2 ohl_open + Late 20-24 | 313 | 42.5 | 0.071 | -0.029 | -1.14 | 0.001 (156) | -0.059 (157) |  |

Gate: n >= 100, t > 3.0, net > 0 overall and in both time halves. Under n = 100 it is not evidence, whatever the numbers say.


## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Harmonic: Crab | 1 | 1.5 |
| 2 | Harmonic: Cypher | 18 | 1.083 |
| 3 | Harmonic: Butterfly | 23 | 0.437 |
| 4 | Harmonic: Cypher (vol swings) | 26 | 0.346 |
| 5 | Wyckoff | 177 | 0.27 |
| 6 | Harmonic: Gartley (vol swings) | 7 | 0.071 |
| 7 | Harmonic: Gartley | 7 | 0.071 |
| 8 | Harmonic: Butterfly (vol swings) | 10 | 0.054 |
| 9 | Fibonacci | 3171 | 0.037 |
| 10 | SMC / ICT | 9188 | 0.029 |
| 11 | Trend (hedge fund) | 2874 | 0.023 |
| 12 | Time (sessions) | 3442 | 0.012 |
| 13 | Momentum / divergence | 2622 | 0.006 |
| 14 | Harmonic: Bat | 5 | 0.0 |
| 15 | Elliott wave | 3933 | -0.0 |
| 16 | Trend (MA) | 15166 | -0.004 |
| 17 | Levels / breakouts | 12244 | -0.018 |
| 18 | Chart patterns (range) | 752 | -0.023 |
| 19 | Liquidity | 8250 | -0.035 |
| 20 | Price action | 980 | -0.047 |
| 21 | Intermarket (SMT) | 1851 | -0.066 |
| 22 | Harmonic: Bat (vol swings) | 3 | -0.167 |
| 23 | Harmonic: Crab (vol swings) | 1 | -1.0 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| breaker | 4h | 106 | 47.2 | 0.275 | 0.175 |
| breakout | 4h | 210 | 40.0 | 0.05 | -0.05 |
| cisd | 4h | 217 | 40.1 | 0.079 | -0.021 |
| crt | 1h | 179 | 34.1 | -0.035 | -0.135 |
| dbl | 1d | 49 | 42.9 | 0.071 | -0.029 |
| donch | 1d | 157 | 40.1 | 0.098 | -0.002 |
| ema_stack | 1d | 278 | 40.6 | 0.167 | 0.067 |
| ew3 | 4h | 218 | 38.5 | 0.019 | -0.081 |
| ew5 | 1h | 33 | 33.3 | 0.041 | -0.059 |
| ew_r2_d1 | 1h | 159 | 49.7 | 0.298 | 0.198 |
| ew_r2_d2 | 1h | 70 | 52.9 | 0.335 | 0.235 |
| ew_r2_v | 1h | 262 | 36.6 | -0.017 | -0.117 |
| ew_r3_d1 | 1d | 35 | 45.7 | 0.413 | 0.313 |
| ew_r3_d2 | 1d | 30 | 53.3 | 0.543 | 0.443 |
| ew_r3_v | 1d | 32 | 50.0 | 0.484 | 0.384 |
| fib | 1m | 467 | 43.0 | 0.097 | -0.003 |
| fvg | 4h | 544 | 41.0 | 0.101 | 0.001 |
| judas | 1m | 928 | 41.8 | 0.051 | -0.049 |
| level | 15m | 1489 | 38.3 | 0.003 | -0.097 |
| liqline | 1d | 147 | 38.1 | 0.11 | 0.01 |
| m2022 | 1d | 90 | 46.7 | 0.348 | 0.248 |
| ma_cross | 1d | 134 | 41.0 | 0.172 | 0.072 |
| macd_div | 1d | 74 | 44.6 | 0.285 | 0.185 |
| msb_ob | 15m | 504 | 43.3 | 0.143 | 0.043 |
| ob | 15m | 438 | 40.9 | 0.089 | -0.011 |
| ohl_break | 1d | 56 | 41.1 | 0.12 | 0.02 |
| ohl_open | 1h | 854 | 40.2 | 0.063 | -0.037 |
| orb | 15m | 166 | 41.0 | 0.044 | -0.056 |
| ote | 4h | 164 | 47.0 | 0.245 | 0.145 |
| pa_engulf | 1m | 54 | 44.4 | 0.111 | 0.011 |
| pa_inside | 4h | 77 | 41.6 | 0.085 | -0.015 |
| pa_pin | 4h | 57 | 45.6 | 0.166 | 0.066 |
| po3 | 15m | 53 | 35.8 | -0.079 | -0.179 |
| rsi_div | 1h | 324 | 39.5 | 0.072 | -0.028 |
| sess_amd | 1m | 69 | 43.5 | 0.1 | 0.0 |
| sma1040 | 1d | 67 | 47.8 | 0.298 | 0.198 |
| smt | 1h | 473 | 37.8 | -0.006 | -0.106 |
| sweep | 4h | 832 | 38.7 | 0.056 | -0.044 |
| tlbreak | 1d | 151 | 42.4 | 0.164 | 0.064 |
| turtle55 | 1d | 80 | 48.8 | 0.293 | 0.193 |
| unicorn | 1m | 67 | 44.8 | 0.119 | 0.019 |
| vwap | 1d | 421 | 36.1 | 0.05 | -0.05 |
| wavec | 1h | 39 | 51.3 | 0.294 | 0.194 |
| wyck | 4h | 36 | 58.3 | 0.496 | 0.396 |
| zombie | 1d | 46 | 41.3 | 0.131 | 0.031 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 55 | -0.002 | 46 | -0.069 |
| breaker | 205 | -0.017 | 205 | 0.107 |
| breakout | 502 | -0.058 | 539 | -0.011 |
| cisd | 502 | -0.067 | 477 | 0.043 |
| crt | 503 | -0.124 | 466 | -0.096 |
| dbl | 349 | -0.064 | 376 | 0.012 |
| donch | 1181 | -0.049 | 1546 | 0.051 |
| ema_stack | 2278 | -0.094 | 2644 | 0.07 |
| ew3 | 505 | -0.13 | 504 | 0.072 |
| ew5 | 61 | -0.043 | 122 | 0.048 |
| ew_r2_d1 | 199 | -0.07 | 330 | 0.082 |
| ew_r2_d2 | 105 | 0.02 | 183 | 0.093 |
| ew_r2_v | 441 | -0.094 | 502 | -0.027 |
| ew_r3_d1 | 96 | -0.067 | 137 | 0.11 |
| ew_r3_d2 | 43 | 0.202 | 105 | 0.116 |
| ew_r3_v | 154 | -0.108 | 204 | 0.17 |
| fib | 1194 | -0.014 | 1192 | 0.065 |
| fvg | 1646 | -0.01 | 1515 | 0.131 |
| harm_bat | 4 | -0.375 | 0 | None |
| harm_bat_tight | 1 | 1.5 | 0 | None |
| harm_butterfly | 11 | 0.185 | 9 | 0.389 |
| harm_butterfly_tight | 2 | 1.5 | 1 | 1.5 |
| harm_crab | 1 | 1.5 | 0 | None |
| harm_cypher | 3 | 0.667 | 10 | 1.0 |
| harm_cypher_tight | 0 | None | 5 | 1.5 |
| harm_gartley | 5 | 0.5 | 1 | -1.0 |
| harm_gartley_tight | 1 | -1.0 | 0 | None |
| harm_vol_bat | 2 | -1.0 | 1 | 1.5 |
| harm_vol_butterfly | 8 | 0.005 | 1 | 1.5 |
| harm_vol_butterfly_tight | 1 | -1.0 | 0 | None |
| harm_vol_crab | 1 | -1.0 | 0 | None |
| harm_vol_cypher | 9 | -0.722 | 13 | 0.731 |
| harm_vol_cypher_tight | 0 | None | 4 | 1.5 |
| harm_vol_gartley | 5 | 0.0 | 1 | 1.5 |
| harm_vol_gartley_tight | 1 | -1.0 | 0 | None |
| judas | 1240 | -0.028 | 1356 | 0.037 |
| kzs | 20 | -0.375 | 10 | -0.25 |
| level | 3299 | -0.037 | 1675 | 0.05 |
| liqline | 1284 | -0.042 | 1409 | -0.034 |
| m2022 | 338 | -0.078 | 322 | 0.013 |
| ma_cross | 1457 | -0.022 | 1395 | -0.012 |
| macd_div | 783 | 0.046 | 652 | -0.044 |
| msb_ob | 1025 | -0.014 | 886 | 0.1 |
| ob | 767 | -0.083 | 837 | 0.105 |
| ohl_break | 371 | -0.102 | 394 | -0.051 |
| ohl_open | 1645 | -0.074 | 1613 | 0.067 |
| orb | 76 | 0.194 | 96 | -0.01 |
| ote | 392 | 0.019 | 393 | 0.131 |
| pa_engulf | 162 | -0.195 | 138 | 0.124 |
| pa_inside | 192 | -0.099 | 174 | 0.107 |
| pa_pin | 153 | 0.012 | 114 | -0.06 |
| pa_star | 26 | -0.845 | 21 | -0.167 |
| po3 | 63 | -0.13 | 61 | -0.098 |
| rect | 11 | 0.364 | 16 | -0.219 |
| rsi_div | 592 | -0.046 | 595 | 0.062 |
| sess_amd | 246 | 0.09 | 274 | 0.049 |
| sma1040 | 34 | 0.396 | 33 | 0.196 |
| smt | 992 | -0.066 | 859 | -0.066 |
| sweep | 2031 | -0.056 | 1654 | 0.046 |
| tlbreak | 1117 | -0.089 | 1089 | 0.025 |
| turtle55 | 43 | 0.198 | 37 | 0.405 |
| unicorn | 224 | -0.123 | 239 | 0.137 |
| vwap | 3470 | -0.05 | 3922 | 0.05 |
| wavec | 71 | -0.301 | 70 | 0.341 |
| wyck | 96 | 0.159 | 81 | 0.401 |
| zombie | 450 | -0.063 | 453 | -0.028 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 37859 | 37.9 | -0.004 | 26626 | 37.9 | 0.0 |
| abc | 35 | 42.9 | 0.128 | 66 | 33.3 | -0.117 |
| breaker | 195 | 36.4 | -0.02 | 214 | 39.3 | 0.109 |
| breakout | 715 | 39.2 | 0.011 | 320 | 33.4 | -0.123 |
| cisd | 366 | 34.2 | -0.101 | 609 | 39.4 | 0.045 |
| crt | 386 | 32.4 | -0.124 | 580 | 33.4 | -0.102 |
| dbl | 443 | 37.2 | -0.05 | 277 | 38.6 | 0.023 |
| donch | 2383 | 38.6 | 0.011 | 337 | 38.9 | -0.013 |
| ema_stack | 3961 | 37.8 | -0.006 | 936 | 38.0 | -0.007 |
| ew3 | 609 | 38.6 | 0.008 | 398 | 35.7 | -0.087 |
| ew5 | 148 | 36.5 | 0.062 | 35 | 28.6 | -0.169 |
| ew_r2_d1 | 328 | 37.2 | 0.014 | 201 | 39.3 | 0.042 |
| ew_r2_d2 | 164 | 37.2 | 0.022 | 124 | 41.9 | 0.124 |
| ew_r2_v | 562 | 34.3 | -0.059 | 379 | 35.4 | -0.058 |
| ew_r3_d1 | 198 | 36.4 | 0.061 | 35 | 28.6 | -0.1 |
| ew_r3_d2 | 119 | 42.9 | 0.222 | 29 | 31.0 | -0.189 |
| ew_r3_v | 307 | 39.7 | 0.115 | 51 | 21.6 | -0.339 |
| fib | 1192 | 39.2 | 0.033 | 1184 | 38.2 | 0.018 |
| fvg | 1830 | 39.5 | 0.044 | 1307 | 41.6 | 0.082 |
| harm_bat | 0 | None | None | 4 | 25.0 | -0.375 |
| harm_bat_tight | 0 | None | None | 1 | 100.0 | 1.5 |
| harm_butterfly | 7 | 71.4 | 0.786 | 13 | 38.5 | 0.003 |
| harm_butterfly_tight | 1 | 100.0 | 1.5 | 2 | 100.0 | 1.5 |
| harm_crab | 0 | None | None | 1 | 100.0 | 1.5 |
| harm_cypher | 5 | 60.0 | 0.5 | 8 | 87.5 | 1.188 |
| harm_cypher_tight | 1 | 100.0 | 1.5 | 4 | 100.0 | 1.5 |
| harm_gartley | 2 | 50.0 | 0.25 | 4 | 50.0 | 0.25 |
| harm_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| harm_vol_bat | 0 | None | None | 3 | 33.3 | -0.167 |
| harm_vol_butterfly | 3 | 66.7 | 0.667 | 6 | 33.3 | -0.077 |
| harm_vol_butterfly_tight | 0 | None | None | 1 | 0.0 | -1.0 |
| harm_vol_crab | 0 | None | None | 1 | 0.0 | -1.0 |
| harm_vol_cypher | 11 | 36.4 | -0.091 | 11 | 54.5 | 0.364 |
| harm_vol_cypher_tight | 2 | 100.0 | 1.5 | 2 | 100.0 | 1.5 |
| harm_vol_gartley | 2 | 0.0 | -1.0 | 4 | 75.0 | 0.875 |
| harm_vol_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| judas | 1689 | 39.1 | 0.003 | 883 | 39.6 | 0.009 |
| kzs | 14 | 28.6 | -0.286 | 16 | 25.0 | -0.375 |
| level | 2435 | 37.6 | -0.024 | 2508 | 38.3 | 0.007 |
| liqline | 1508 | 37.4 | -0.022 | 1173 | 35.7 | -0.055 |
| m2022 | 381 | 35.7 | -0.024 | 278 | 36.0 | -0.052 |
| ma_cross | 1681 | 36.2 | -0.044 | 1151 | 38.3 | 0.016 |
| macd_div | 264 | 37.5 | -0.01 | 1169 | 37.6 | 0.005 |
| msb_ob | 945 | 38.4 | 0.02 | 955 | 40.4 | 0.066 |
| ob | 866 | 37.5 | -0.006 | 728 | 38.7 | 0.043 |
| ohl_break | 451 | 35.7 | -0.08 | 304 | 35.9 | -0.064 |
| ohl_open | 1749 | 37.5 | -0.021 | 1502 | 37.9 | 0.015 |
| orb | 107 | 37.4 | -0.065 | 65 | 50.8 | 0.319 |
| ote | 349 | 41.0 | 0.071 | 432 | 41.2 | 0.082 |
| pa_engulf | 142 | 37.3 | -0.035 | 158 | 36.1 | -0.061 |
| pa_inside | 203 | 38.4 | -0.005 | 163 | 38.0 | 0.005 |
| pa_pin | 109 | 45.0 | 0.186 | 157 | 29.9 | -0.155 |
| pa_star | 18 | 22.2 | -0.444 | 29 | 13.8 | -0.603 |
| po3 | 62 | 33.9 | -0.153 | 61 | 34.4 | -0.102 |
| rect | 19 | 52.6 | 0.316 | 8 | 12.5 | -0.688 |
| rsi_div | 300 | 41.7 | 0.104 | 883 | 36.0 | -0.028 |
| sess_amd | 224 | 40.6 | 0.036 | 294 | 41.5 | 0.092 |
| sma1040 | 28 | 39.3 | 0.032 | 39 | 53.8 | 0.489 |
| smt | 896 | 32.7 | -0.142 | 952 | 38.4 | 0.004 |
| sweep | 1619 | 37.2 | -0.01 | 2056 | 37.2 | -0.009 |
| tlbreak | 1024 | 38.5 | -0.003 | 1178 | 35.5 | -0.055 |
| turtle55 | 61 | 47.5 | 0.262 | 19 | 52.6 | 0.395 |
| unicorn | 240 | 35.8 | -0.048 | 220 | 38.2 | 0.054 |
| vwap | 5907 | 38.3 | 0.007 | 1470 | 37.8 | -0.015 |
| wavec | 44 | 38.6 | 0.127 | 96 | 36.5 | -0.048 |
| wyck | 70 | 50.0 | 0.309 | 107 | 46.7 | 0.244 |
| zombie | 477 | 37.5 | -0.013 | 425 | 35.3 | -0.086 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 15975 | 35.8 | -0.004 |
| Mon | 7535 | 41.4 | 0.059 |
| Sat | 6769 | 35.4 | -0.072 |
| Sun | 7353 | 37.9 | -0.031 |
| Thu | 11827 | 38.0 | 0.004 |
| Tue | 7561 | 38.9 | -0.007 |
| Wed | 7731 | 39.5 | 0.023 |
| Asia 00-07 | 17856 | 38.7 | 0.002 |
| Late 20-24 | 11450 | 37.7 | -0.01 |
| London 07-12 | 13221 | 39.1 | 0.004 |
| New York 12-20 | 18524 | 36.5 | -0.016 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 64751 | 37.9 | -0.002 | -0.002 | +0.02 | 28064 | -0.022 | 36687 | 0.013 |  |
| grade A+++ | 579 | 42.8 | 0.15 | 0.058 | +1.52 | 229 | 0.27 | 350 | 0.072 |  |
| grade A+ | 8806 | 35.9 | -0.038 | -0.02 | -1.11 | 3703 | 0.007 | 5103 | -0.07 |  |
| grade A | 20278 | 36.8 | -0.014 | -0.022 | +0.80 | 8373 | -0.054 | 11905 | 0.015 |  |
| grade B | 22952 | 38.8 | 0.015 | 0.02 | -0.45 | 10020 | -0.013 | 12932 | 0.036 |  |
| grade C | 12136 | 39.0 | 0.002 | -0.001 | +0.22 | 5739 | -0.024 | 6397 | 0.025 |  |
| layer htf | 37859 | 37.9 | -0.004 | 0.001 | -0.62 | 16255 | -0.028 | 21604 | 0.014 |  |
| layer loc | 14087 | 37.9 | 0.006 | 0.01 | -0.27 | 6045 | 0.072 | 8042 | -0.043 |  |
| layer vol | 20642 | 37.6 | -0.015 | -0.025 | +0.88 | 9095 | -0.036 | 11547 | 0.001 |  |
| layer reg | 47223 | 36.9 | -0.011 | -0.013 | +0.25 | 20220 | -0.028 | 27003 | 0.001 |  |
| layer time | 35445 | 37.5 | -0.002 | -0.003 | +0.17 | 14345 | -0.03 | 21100 | 0.017 |  |
| no htf | 26892 | 37.9 | 0.0 | -0.007 | +0.76 | 11809 | -0.015 | 15083 | 0.012 |  |
| no loc | 50664 | 37.9 | -0.005 | -0.006 | +0.16 | 22019 | -0.048 | 28645 | 0.029 |  |
| no vol | 44109 | 38.0 | 0.004 | 0.008 | -0.57 | 18969 | -0.016 | 25140 | 0.018 |  |
| no reg | 17528 | 40.5 | 0.022 | 0.027 | -0.35 | 7844 | -0.008 | 9684 | 0.047 |  |
| no time | 29306 | 38.3 | -0.003 | -0.001 | -0.15 | 13719 | -0.014 | 15587 | 0.007 |  |
| grade A / turtle55 | 34 | 55.9 | 0.475 | 0.665 | -0.70 | 14 | 0.313 | 20 | 0.589 |  |
| no loc / wyck | 69 | 50.7 | 0.351 | -0.075 | +2.56 | 29 | 0.392 | 40 | 0.322 |  |
| no loc / sma1040 | 64 | 50.0 | 0.351 | -0.072 | +2.24 | 17 | 0.324 | 47 | 0.361 |  |
| grade A+++ / ob | 40 | 50.0 | 0.336 | -0.0 | +1.44 | 16 | 0.875 | 24 | -0.024 |  |
| grade A / wyck | 64 | 50.0 | 0.333 | 0.305 | +0.12 | 27 | -0.016 | 37 | 0.587 |  |
| grade C / ote | 137 | 52.6 | 0.323 | 0.05 | +1.82 | 69 | 0.377 | 68 | 0.269 |  |
| no loc / turtle55 | 80 | 48.8 | 0.293 | 0.453 | -0.94 | 30 | 0.31 | 50 | 0.283 |  |
| grade A+++ / msb_ob | 45 | 46.7 | 0.244 | 0.105 | +0.65 | 18 | 0.552 | 27 | 0.038 |  |
| grade A+ / wyck | 35 | 45.7 | 0.229 | 0.028 | +0.75 | 14 | 0.429 | 21 | 0.097 |  |
| grade A+ / ew_r3_d1 | 36 | 47.2 | 0.227 | -0.091 | +1.54 | 13 | 0.238 | 23 | 0.22 |  |
| grade A / ew_r3_d2 | 68 | 41.2 | 0.219 | -0.169 | +2.49 | 21 | -0.004 | 47 | 0.318 |  |
| loc / wyck | 108 | 46.3 | 0.217 | 0.123 | +0.55 | 46 | 0.038 | 62 | 0.351 |  |
| grade A+++ / vwap | 55 | 43.6 | 0.192 | -0.056 | +1.29 | 21 | 0.128 | 34 | 0.232 |  |
| grade A / ew_r3_v | 160 | 41.2 | 0.183 | -0.009 | +1.69 | 63 | 0.13 | 97 | 0.218 |  |
| grade B / breaker | 144 | 43.8 | 0.175 | -0.144 | +2.66 | 50 | 0.279 | 94 | 0.12 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8201 | 4137 | 50.4 |
| sweep | vwap | 6521 | 3953 | 60.6 |
| ema_stack | sweep | 3288 | 2457 | 74.7 |
| ema_stack | level | 3925 | 2132 | 54.3 |
| fvg | vwap | 4543 | 1800 | 39.6 |
| ohl_open | vwap | 4257 | 1796 | 42.2 |
| macd_div | vwap | 2173 | 1754 | 80.7 |
| level | sweep | 3691 | 1573 | 42.6 |
| msb_ob | vwap | 2752 | 1532 | 55.7 |
| fib | vwap | 3041 | 1518 | 49.9 |
| fvg | level | 3228 | 1446 | 44.8 |
| rsi_div | vwap | 1822 | 1445 | 79.3 |
| judas | level | 2894 | 1417 | 49.0 |
| smt | vwap | 3023 | 1401 | 46.3 |
| ob | vwap | 2586 | 1389 | 53.7 |
| ma_cross | sweep | 2082 | 1335 | 64.1 |
| level | ma_cross | 2595 | 1321 | 50.9 |
| tlbreak | vwap | 2578 | 1269 | 49.2 |
| liqline | vwap | 3506 | 1263 | 36.0 |
| ma_cross | vwap | 4228 | 1259 | 29.8 |
| level | ohl_open | 2417 | 1253 | 51.8 |
| judas | sweep | 1893 | 1160 | 61.3 |
| judas | vwap | 4254 | 1135 | 26.7 |
| fvg | ohl_open | 1266 | 1023 | 80.8 |
| fvg | sweep | 1702 | 1000 | 58.8 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 25 | 44.0 | 0.238 |
| 2 families | 416 | 38.0 | 0.02 |
| 2 families (with opposition) | 1395 | 39.4 | 0.031 |
| 3 families | 1138 | 37.3 | -0.009 |
| 3 families (with opposition) | 4702 | 38.4 | 0.015 |
| 4+ families | 916 | 37.4 | -0.014 |
| 4+ families (with opposition) | 4298 | 37.9 | -0.009 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 81.9 | 25890 | 82.0 | 357350 | -0.1 |
| 1m shapes 120/180/240/360 deg | 78.9 | 10940 | 79.2 | 10915 | -0.8 |
| 15m | 65.1 | 20054 | 65.0 | 278068 | +0.4 |
| 15m shapes 120/180/240/360 deg | 63.0 | 10439 | 63.9 | 10329 | -1.9 |
| 1h | 57.9 | 16236 | 57.9 | 225032 | +0.1 |
| 1h shapes 120/180/240/360 deg | 56.7 | 8865 | 57.2 | 8847 | -1.0 |
| 4h | 56.7 | 12057 | 57.8 | 166627 | -2.4 |
| 4h shapes 120/180/240/360 deg | 56.9 | 6784 | 56.9 | 6787 | -0.1 |
| 1d | 55.5 | 3169 | 56.1 | 42490 | -0.7 |
| 1d shapes 120/180/240/360 deg | 57.5 | 2017 | 57.5 | 2020 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 72 | 19.4 | +0.126 | -0.286 | +1.49 |
| 1d | 52 | 42.3 | +0.012 | +0.236 | -0.80 |
| 1h | 155 | 26.5 | -0.003 | -0.011 | +0.05 |
| 4h | 101 | 33.7 | +0.135 | +0.001 | +0.69 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2371 | -0.094 |
| 15 days around full moon | 2331 | 0.033 |

Difference t = -1.58 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 64751 | 49.0 | -0.02 | -0.12 | -1263.7 | -5.02 |
| rr1.5 | 64751 | 40.5 | -0.002 | -0.102 | -152.4 | -0.50 |
| rr2.0 | 64751 | 35.5 | 0.014 | -0.086 | 890.6 | +2.55 |
| rr3.0 | 64751 | 29.8 | 0.031 | -0.069 | 1993.1 | +4.77 |
| rr1.5_be | 64751 | 34.5 | -0.001 | -0.101 | -79.9 | -0.28 |
| rr2.0_be | 64751 | 27.4 | 0.012 | -0.088 | 773.8 | +2.48 |
| rr1.5_h16 | 64751 | 42.1 | 0.003 | -0.097 | 220.5 | +0.77 |
| rr2.0_h16 | 64751 | 38.8 | 0.014 | -0.086 | 924.7 | +2.89 |
| pt_1.5_3 | 64751 | 48.9 | 0.03 | -0.07 | 1973.5 | +6.66 |
| pt_1.0_3 | 64751 | 49.0 | 0.018 | -0.082 | 1159.8 | +4.19 |
| pt_1.5_5 | 64751 | 48.9 | 0.045 | -0.055 | 2903.1 | +9.48 |
| trail_only | 64751 | 48.9 | 0.084 | -0.016 | 5443.1 | +15.42 |
