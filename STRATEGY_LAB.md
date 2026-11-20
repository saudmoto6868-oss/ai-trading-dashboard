# Strategy lab - real candles (2026-11-17)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | turtle55 | Trend (hedge fund) | 81 | 49.4 | 0.308 | 0.208 | 49.4 | 0.329 |  |
| 2 | sma1040 | Trend (hedge fund) | 67 | 47.8 | 0.302 | 0.202 | 35.8 | 0.134 |  |
| 3 | wavec | Elliott wave | 154 | 45.5 | 0.238 | 0.138 | 48.7 | 0.258 |  |
| 4 | wyck | Wyckoff | 168 | 42.9 | 0.147 | 0.047 | 41.7 | 0.129 |  |
| 5 | ew_r2_d2 | Elliott wave | 295 | 40.3 | 0.142 | 0.042 | 33.9 | -0.028 |  |
| 6 | pa_star | Price action | 45 | 44.4 | 0.139 | 0.039 | 42.2 | 0.084 |  |
| 7 | ew_r3_d2 | Elliott wave | 166 | 39.2 | 0.103 | 0.003 | 42.2 | 0.189 |  |
| 8 | ew_r3_v | Elliott wave | 362 | 38.7 | 0.073 | -0.027 | 35.1 | -0.027 |  |
| 9 | ew5 | Elliott wave | 207 | 39.6 | 0.073 | -0.027 | 30.9 | -0.114 |  |
| 10 | fvg | SMC / ICT | 3132 | 39.8 | 0.049 | -0.051 | 39.4 | 0.041 |  |
| 11 | orb | Time (sessions) | 168 | 39.9 | 0.043 | -0.057 | 48.8 | 0.274 |  |
| 12 | m2022 | SMC / ICT | 696 | 39.7 | 0.035 | -0.065 | 39.9 | 0.066 |  |
| 13 | fib | Fibonacci | 2394 | 39.0 | 0.032 | -0.068 | 38.1 | 0.014 |  |
| 14 | ote | Fibonacci | 826 | 39.1 | 0.03 | -0.07 | 37.0 | -0.017 |  |
| 15 | unicorn | SMC / ICT | 437 | 37.5 | 0.03 | -0.07 | 39.8 | 0.08 |  |
| 16 | liqline | Liquidity | 2725 | 38.8 | 0.024 | -0.076 | 38.0 | -0.0 |  |
| 17 | pa_inside | Price action | 360 | 38.9 | 0.019 | -0.081 | 35.6 | -0.069 |  |
| 18 | breaker | SMC / ICT | 407 | 37.1 | 0.015 | -0.085 | 36.6 | 0.007 |  |
| 19 | sess_amd | Time (sessions) | 541 | 38.3 | 0.012 | -0.088 | 37.7 | 0.006 |  |
| 20 | ew_r2_d1 | Elliott wave | 564 | 37.1 | 0.006 | -0.094 | 36.9 | 0.007 |  |
| 21 | ob | SMC / ICT | 1544 | 37.6 | 0.004 | -0.096 | 39.9 | 0.061 |  |
| 22 | macd_div | Momentum / divergence | 1398 | 37.8 | 0.004 | -0.096 | 37.3 | -0.013 |  |
| 23 | breakout | Levels / breakouts | 1116 | 39.2 | 0.003 | -0.097 | 40.1 | 0.041 |  |
| 24 | level | Levels / breakouts | 4920 | 38.2 | -0.003 | -0.103 | 39.5 | 0.034 |  |
| 25 | tlbreak | Levels / breakouts | 2250 | 37.9 | -0.004 | -0.104 | 38.9 | 0.021 |  |
| 26 | msb_ob | SMC / ICT | 1838 | 37.5 | -0.007 | -0.107 | 39.9 | 0.054 |  |
| 27 | rsi_div | Momentum / divergence | 1208 | 36.8 | -0.009 | -0.109 | 37.7 | 0.013 |  |
| 28 | sweep | Liquidity | 3698 | 37.3 | -0.009 | -0.109 | 39.0 | 0.037 |  |
| 29 | donch | Trend (hedge fund) | 2747 | 37.7 | -0.012 | -0.112 | 38.7 | 0.019 |  |
| 30 | ema_stack | Trend (MA) | 4914 | 37.6 | -0.013 | -0.113 | 39.2 | 0.034 |  |
| 31 | cisd | SMC / ICT | 1001 | 37.1 | -0.013 | -0.113 | 38.9 | 0.034 |  |
| 32 | judas | Time (sessions) | 2482 | 38.1 | -0.015 | -0.115 | 39.0 | 0.011 |  |
| 33 | ew_r2_v | Elliott wave | 948 | 36.8 | -0.015 | -0.115 | 36.3 | -0.02 |  |
| 34 | crt | Liquidity | 881 | 36.8 | -0.02 | -0.12 | 37.7 | 0.003 |  |
| 35 | ew_r3_d1 | Elliott wave | 245 | 34.3 | -0.02 | -0.12 | 38.8 | 0.099 |  |
| 36 | ma_cross | Trend (MA) | 2814 | 37.2 | -0.021 | -0.121 | 37.8 | 0.004 |  |
| 37 | vwap | Trend (MA) | 7338 | 37.0 | -0.027 | -0.127 | 38.3 | 0.013 |  |
| 38 | ohl_open | Levels / breakouts | 3168 | 36.8 | -0.027 | -0.127 | 38.4 | 0.011 |  |
| 39 | zombie | Liquidity | 903 | 36.3 | -0.035 | -0.135 | 37.3 | -0.007 |  |
| 40 | ohl_break | Levels / breakouts | 834 | 37.2 | -0.038 | -0.138 | 40.6 | 0.056 |  |
| 41 | pa_engulf | Price action | 272 | 36.8 | -0.045 | -0.145 | 34.6 | -0.102 |  |
| 42 | dbl | Chart patterns (range) | 674 | 37.1 | -0.049 | -0.149 | 37.5 | -0.031 |  |
| 43 | abc | Elliott wave | 110 | 34.5 | -0.049 | -0.149 | 40.9 | 0.079 |  |
| 44 | ew3 | Elliott wave | 1009 | 36.5 | -0.051 | -0.151 | 41.3 | 0.08 |  |
| 45 | smt | Intermarket (SMT) | 1864 | 35.3 | -0.069 | -0.169 | 38.8 | 0.029 |  |
| 46 | po3 | Time (sessions) | 156 | 34.0 | -0.077 | -0.177 | 35.3 | -0.026 |  |
| 47 | pa_pin | Price action | 258 | 32.9 | -0.098 | -0.198 | 38.0 | 0.021 |  |
| 48 | kzs | Time (sessions) | 36 | 19.4 | -0.461 | -0.561 | 33.3 | -0.167 |  |
| 49 | harm_crab | Harmonic: Crab | 1 | 100.0 | 1.5 | 1.4 | 0.0 | -1.0 |  |
| 50 | harm_butterfly_tight | Harmonic: Butterfly | 2 | 100.0 | 1.5 | 1.4 | 50.0 | 0.25 |  |
| 51 | harm_bat_tight | Harmonic: Bat | 1 | 100.0 | 1.5 | 1.4 | 0.0 | -1.0 |  |
| 52 | harm_cypher_tight | Harmonic: Cypher | 4 | 75.0 | 0.875 | 0.775 | 50.0 | 0.25 |  |
| 53 | harm_vol_cypher_tight | Harmonic: Cypher (vol swings) | 4 | 75.0 | 0.875 | 0.775 | 75.0 | 0.875 |  |
| 54 | harm_vol_cypher | Harmonic: Cypher (vol swings) | 12 | 58.3 | 0.458 | 0.358 | 75.0 | 0.875 |  |
| 55 | harm_gartley | Harmonic: Gartley | 7 | 42.9 | 0.26 | 0.16 | 42.9 | 0.071 |  |
| 56 | harm_gartley_tight | Harmonic: Gartley | 2 | 50.0 | 0.25 | 0.15 | 50.0 | 0.25 |  |
| 57 | harm_vol_bat | Harmonic: Bat (vol swings) | 2 | 50.0 | 0.25 | 0.15 | 0.0 | -1.0 |  |
| 58 | harm_vol_butterfly | Harmonic: Butterfly (vol swings) | 11 | 36.4 | 0.124 | 0.024 | 45.5 | 0.185 |  |
| 59 | harm_butterfly | Harmonic: Butterfly | 19 | 36.8 | -0.051 | -0.151 | 42.1 | 0.081 |  |
| 60 | harm_cypher | Harmonic: Cypher | 11 | 36.4 | -0.052 | -0.152 | 54.5 | 0.403 |  |
| 61 | harm_vol_gartley | Harmonic: Gartley (vol swings) | 7 | 28.6 | -0.131 | -0.231 | 42.9 | 0.202 |  |
| 62 | harm_vol_butterfly_tight | Harmonic: Butterfly (vol swings) | 3 | 33.3 | -0.167 | -0.267 | 66.7 | 0.667 |  |
| 63 | harm_bat | Harmonic: Bat | 3 | 33.3 | -0.167 | -0.267 | 33.3 | -0.167 |  |
| 64 | rect | Chart patterns (range) | 29 | 24.1 | -0.327 | -0.427 | 41.4 | 0.098 |  |
| 65 | harm_vol_crab | Harmonic: Crab (vol swings) | 2 | 0.0 | -1.0 | -1.1 | 50.0 | 0.25 |  |
| 66 | harm_vol_gartley_tight | Harmonic: Gartley (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |

## Stop study: where should the stop sit? (same entries, target fixed at 2.25 ATR, results in ATR, cost 0.15 ATR)

| group | stop | n | target hit % | stopped % | avg ATR | net ATR | mirror avg ATR | t (net vs 0) |
|---|---|---|---|---|---|---|---|---|
| all | 1.0 ATR | 64542 | 29.9 | 67.9 | 0.003 | -0.147 | 0.037 | -25.07 |
| all | 1.5 ATR | 64542 | 37.7 | 57.8 | -0.008 | -0.158 | 0.021 | -22.30 |
| all | 2.0 ATR | 64542 | 43.1 | 49.9 | -0.024 | -0.174 | 0.005 | -21.48 |
| all | 2.5 ATR | 64542 | 47.3 | 43.2 | -0.028 | -0.178 | -0.0 | -19.94 |
| all | 3.0 ATR | 64542 | 50.2 | 37.7 | -0.036 | -0.186 | -0.014 | -19.20 |
| 1m | 1.0 ATR | 12257 | 33.9 | 65.5 | 0.11 | -0.04 | 0.137 | -2.87 |
| 1m | 1.5 ATR | 12257 | 40.8 | 58.1 | 0.049 | -0.101 | 0.089 | -6.10 |
| 1m | 2.0 ATR | 12257 | 45.8 | 52.7 | -0.024 | -0.174 | 0.047 | -9.14 |
| 1m | 2.5 ATR | 12257 | 50.2 | 47.6 | -0.065 | -0.215 | 0.017 | -10.12 |
| 1m | 3.0 ATR | 12257 | 53.1 | 43.7 | -0.131 | -0.281 | -0.034 | -12.04 |
| 15m | 1.0 ATR | 17863 | 29.1 | 68.9 | -0.025 | -0.175 | 0.023 | -15.83 |
| 15m | 1.5 ATR | 17863 | 37.4 | 58.7 | -0.027 | -0.177 | 0.024 | -13.13 |
| 15m | 2.0 ATR | 17863 | 43.7 | 50.9 | -0.031 | -0.181 | 0.001 | -11.70 |
| 15m | 2.5 ATR | 17863 | 48.3 | 44.5 | -0.032 | -0.182 | -0.013 | -10.58 |
| 15m | 3.0 ATR | 17863 | 51.6 | 39.2 | -0.037 | -0.187 | -0.027 | -10.01 |
| 1h | 1.0 ATR | 17537 | 28.4 | 68.8 | -0.04 | -0.19 | 0.031 | -17.19 |
| 1h | 1.5 ATR | 17537 | 36.6 | 58.1 | -0.04 | -0.19 | 0.014 | -14.09 |
| 1h | 2.0 ATR | 17537 | 42.4 | 49.6 | -0.039 | -0.189 | 0.032 | -12.27 |
| 1h | 2.5 ATR | 17537 | 46.4 | 43.5 | -0.058 | -0.208 | 0.033 | -12.14 |
| 1h | 3.0 ATR | 17537 | 49.9 | 38.1 | -0.049 | -0.199 | 0.042 | -10.73 |
| 4h | 1.0 ATR | 13159 | 29.2 | 68.4 | -0.013 | -0.163 | -0.028 | -12.64 |
| 4h | 1.5 ATR | 13159 | 37.1 | 57.5 | -0.013 | -0.163 | -0.042 | -10.48 |
| 4h | 2.0 ATR | 13159 | 42.1 | 48.2 | -0.007 | -0.157 | -0.054 | -8.87 |
| 4h | 2.5 ATR | 13159 | 46.2 | 39.3 | 0.036 | -0.114 | -0.022 | -5.90 |
| 4h | 3.0 ATR | 13159 | 48.5 | 32.2 | 0.06 | -0.09 | -0.023 | -4.35 |
| 1d | 1.0 ATR | 3726 | 29.8 | 65.2 | 0.049 | -0.101 | 0.029 | -4.17 |
| 1d | 1.5 ATR | 3726 | 36.2 | 51.8 | 0.067 | -0.083 | 0.032 | -2.89 |
| 1d | 2.0 ATR | 3726 | 39.0 | 43.2 | 0.026 | -0.124 | -0.025 | -3.87 |
| 1d | 2.5 ATR | 3726 | 41.1 | 34.7 | 0.019 | -0.131 | -0.081 | -3.79 |
| 1d | 3.0 ATR | 3726 | 42.2 | 28.3 | -0.0 | -0.15 | -0.118 | -4.09 |

| group | question | n | value |
|---|---|---|---|
| all | stopped at 1.5 ATR, target reached later | 47353 | 31.7 % reached it later (mirror direction 31.5 %); 73.4 % of all trades were stopped |
| all | MAE of trades that reached the target (ATR) | 39758 | p50 1.05 · p75 2.35 · p90 4.48 |
| 1m | stopped at 1.5 ATR, target reached later | 9678 | 34.6 % reached it later (mirror direction 36.5 %); 79.0 % of all trades were stopped |
| 1m | MAE of trades that reached the target (ATR) | 8421 | p50 1.03 · p75 2.7 · p90 4.99 |
| 15m | stopped at 1.5 ATR, target reached later | 13531 | 35.4 % reached it later (mirror direction 33.0 %); 75.7 % of all trades were stopped |
| 15m | MAE of trades that reached the target (ATR) | 11612 | p50 1.21 · p75 2.59 · p90 4.99 |
| 1h | stopped at 1.5 ATR, target reached later | 13176 | 34.0 % reached it later (mirror direction 35.3 %); 75.1 % of all trades were stopped |
| 1h | MAE of trades that reached the target (ATR) | 11000 | p50 1.18 · p75 2.58 · p90 4.68 |
| 4h | stopped at 1.5 ATR, target reached later | 8866 | 23.6 % reached it later (mirror direction 23.4 %); 67.4 % of all trades were stopped |
| 4h | MAE of trades that reached the target (ATR) | 7058 | p50 0.88 · p75 1.78 · p90 2.92 |
| 1d | stopped at 1.5 ATR, target reached later | 2102 | 14.3 % reached it later (mirror direction 12.1 %); 56.4 % of all trades were stopped |
| 1d | MAE of trades that reached the target (ATR) | 1667 | p50 0.7 · p75 1.23 · p90 2.25 |

Reading: a stop that is never reached only helps if the AVERAGE (net ATR) goes up, not just the target-hit share; compare with the mirror column (the opposite direction on the same bars).


## Pre-registered tests (signals after the freeze date only; docs/PREREG_2026-11-01.md)

| hypothesis | n | win % | avg R | net avg R | t vs random | net 1st half (n) | net 2nd half (n) | PASS |
|---|---|---|---|---|---|---|---|---|
| H1 sess_amd + loc | 102 | 43.1 | 0.117 | 0.017 | +1.43 | -0.225 (51) | 0.259 (51) |  |
| H2 ohl_open + Late 20-24 | 333 | 36.0 | -0.038 | -0.138 | +1.46 | -0.113 (166) | -0.163 (167) |  |

Gate: n >= 100, t > 3.0, net > 0 overall and in both time halves. Under n = 100 it is not evidence, whatever the numbers say.


## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Harmonic: Crab | 1 | 1.5 |
| 2 | Harmonic: Cypher (vol swings) | 16 | 0.562 |
| 3 | Harmonic: Gartley | 9 | 0.258 |
| 4 | Harmonic: Bat (vol swings) | 2 | 0.25 |
| 5 | Harmonic: Bat | 4 | 0.25 |
| 6 | Harmonic: Cypher | 15 | 0.195 |
| 7 | Wyckoff | 168 | 0.147 |
| 8 | Harmonic: Butterfly | 21 | 0.097 |
| 9 | Harmonic: Butterfly (vol swings) | 14 | 0.062 |
| 10 | Fibonacci | 3220 | 0.031 |
| 11 | SMC / ICT | 9055 | 0.02 |
| 12 | Elliott wave | 4060 | 0.016 |
| 13 | Trend (hedge fund) | 2895 | 0.004 |
| 14 | Momentum / divergence | 2606 | -0.002 |
| 15 | Liquidity | 8207 | -0.002 |
| 16 | Levels / breakouts | 12288 | -0.011 |
| 17 | Time (sessions) | 3383 | -0.015 |
| 18 | Trend (MA) | 15066 | -0.021 |
| 19 | Price action | 935 | -0.026 |
| 20 | Chart patterns (range) | 703 | -0.06 |
| 21 | Intermarket (SMT) | 1864 | -0.069 |
| 22 | Harmonic: Gartley (vol swings) | 8 | -0.24 |
| 23 | Harmonic: Crab (vol swings) | 2 | -1.0 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| abc | 15m | 30 | 26.7 | -0.235 | -0.335 |
| breaker | 4h | 114 | 42.1 | 0.167 | 0.067 |
| breakout | 1m | 228 | 42.5 | 0.064 | -0.036 |
| cisd | 4h | 207 | 41.1 | 0.126 | 0.026 |
| crt | 1m | 103 | 46.6 | 0.193 | 0.093 |
| dbl | 1d | 49 | 42.9 | 0.071 | -0.029 |
| donch | 1d | 159 | 39.6 | 0.113 | 0.013 |
| ema_stack | 1d | 283 | 39.6 | 0.16 | 0.06 |
| ew3 | 1d | 62 | 37.1 | 0.026 | -0.074 |
| ew5 | 1m | 49 | 59.2 | 0.48 | 0.38 |
| ew_r2_d1 | 1h | 173 | 47.4 | 0.238 | 0.138 |
| ew_r2_d2 | 1h | 71 | 53.5 | 0.472 | 0.372 |
| ew_r2_v | 1m | 152 | 44.1 | 0.104 | 0.004 |
| ew_r3_d1 | 1d | 35 | 45.7 | 0.413 | 0.313 |
| ew_r3_d2 | 1d | 30 | 53.3 | 0.543 | 0.443 |
| ew_r3_v | 1m | 46 | 60.9 | 0.522 | 0.422 |
| fib | 1m | 439 | 44.0 | 0.118 | 0.018 |
| fvg | 1m | 855 | 44.1 | 0.122 | 0.022 |
| judas | 1m | 902 | 41.0 | 0.037 | -0.063 |
| level | 1m | 1147 | 41.7 | 0.054 | -0.046 |
| liqline | 1d | 148 | 37.8 | 0.117 | 0.017 |
| m2022 | 1d | 90 | 46.7 | 0.346 | 0.246 |
| ma_cross | 1d | 135 | 40.7 | 0.179 | 0.079 |
| macd_div | 1d | 74 | 44.6 | 0.285 | 0.185 |
| msb_ob | 1m | 349 | 44.7 | 0.123 | 0.023 |
| ob | 4h | 389 | 39.3 | 0.049 | -0.051 |
| ohl_break | 1d | 57 | 42.1 | 0.15 | 0.05 |
| ohl_open | 4h | 602 | 37.0 | 0.004 | -0.096 |
| orb | 15m | 161 | 39.1 | 0.027 | -0.073 |
| ote | 4h | 174 | 41.4 | 0.103 | 0.003 |
| pa_engulf | 1m | 34 | 41.2 | 0.029 | -0.071 |
| pa_inside | 1h | 82 | 43.9 | 0.118 | 0.018 |
| pa_pin | 15m | 75 | 34.7 | -0.058 | -0.158 |
| po3 | 1h | 81 | 33.3 | -0.044 | -0.144 |
| rsi_div | 15m | 320 | 40.9 | 0.076 | -0.024 |
| sess_amd | 1h | 277 | 40.4 | 0.071 | -0.029 |
| sma1040 | 1d | 67 | 47.8 | 0.302 | 0.202 |
| smt | 1h | 497 | 36.4 | -0.028 | -0.128 |
| sweep | 1m | 562 | 42.9 | 0.096 | -0.004 |
| tlbreak | 1d | 152 | 42.1 | 0.154 | 0.054 |
| turtle55 | 1d | 81 | 49.4 | 0.308 | 0.208 |
| unicorn | 1m | 70 | 60.0 | 0.515 | 0.415 |
| vwap | 1d | 426 | 35.4 | 0.036 | -0.064 |
| wavec | 1h | 39 | 61.5 | 0.611 | 0.511 |
| wyck | 1m | 30 | 63.3 | 0.583 | 0.483 |
| zombie | 1d | 47 | 40.4 | 0.14 | 0.04 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 66 | -0.077 | 44 | -0.007 |
| breaker | 216 | -0.058 | 191 | 0.097 |
| breakout | 502 | -0.077 | 614 | 0.069 |
| cisd | 534 | -0.028 | 467 | 0.005 |
| crt | 457 | -0.064 | 424 | 0.029 |
| dbl | 321 | -0.086 | 353 | -0.015 |
| donch | 1144 | -0.099 | 1603 | 0.05 |
| ema_stack | 2215 | -0.131 | 2699 | 0.083 |
| ew3 | 476 | -0.191 | 533 | 0.074 |
| ew5 | 77 | -0.055 | 130 | 0.149 |
| ew_r2_d1 | 215 | -0.064 | 349 | 0.05 |
| ew_r2_d2 | 106 | 0.086 | 189 | 0.173 |
| ew_r2_v | 410 | -0.039 | 538 | 0.003 |
| ew_r3_d1 | 90 | -0.105 | 155 | 0.029 |
| ew_r3_d2 | 44 | 0.091 | 122 | 0.108 |
| ew_r3_v | 142 | -0.03 | 220 | 0.14 |
| fib | 1221 | -0.03 | 1173 | 0.097 |
| fvg | 1657 | -0.022 | 1475 | 0.129 |
| harm_bat | 3 | -0.167 | 0 | None |
| harm_bat_tight | 1 | 1.5 | 0 | None |
| harm_butterfly | 12 | -0.122 | 7 | 0.071 |
| harm_butterfly_tight | 1 | 1.5 | 1 | 1.5 |
| harm_crab | 1 | 1.5 | 0 | None |
| harm_cypher | 5 | -0.914 | 6 | 0.667 |
| harm_cypher_tight | 1 | -1.0 | 3 | 1.5 |
| harm_gartley | 5 | 0.0 | 2 | 0.911 |
| harm_gartley_tight | 1 | -1.0 | 1 | 1.5 |
| harm_vol_bat | 1 | -1.0 | 1 | 1.5 |
| harm_vol_butterfly | 9 | 0.374 | 2 | -1.0 |
| harm_vol_butterfly_tight | 2 | 0.25 | 1 | -1.0 |
| harm_vol_crab | 2 | -1.0 | 0 | None |
| harm_vol_cypher | 5 | -0.5 | 7 | 1.143 |
| harm_vol_cypher_tight | 1 | -1.0 | 3 | 1.5 |
| harm_vol_gartley | 5 | -0.283 | 2 | 0.25 |
| harm_vol_gartley_tight | 1 | -1.0 | 0 | None |
| judas | 1284 | -0.08 | 1198 | 0.053 |
| kzs | 21 | -0.553 | 15 | -0.333 |
| level | 3204 | -0.049 | 1716 | 0.084 |
| liqline | 1326 | -0.054 | 1399 | 0.099 |
| m2022 | 338 | -0.033 | 358 | 0.1 |
| ma_cross | 1421 | -0.046 | 1393 | 0.003 |
| macd_div | 759 | 0.015 | 639 | -0.01 |
| msb_ob | 992 | -0.062 | 846 | 0.057 |
| ob | 762 | -0.124 | 782 | 0.127 |
| ohl_break | 385 | -0.101 | 449 | 0.015 |
| ohl_open | 1590 | -0.094 | 1578 | 0.04 |
| orb | 70 | 0.056 | 98 | 0.034 |
| ote | 417 | -0.06 | 409 | 0.121 |
| pa_engulf | 146 | -0.175 | 126 | 0.105 |
| pa_inside | 179 | -0.11 | 181 | 0.145 |
| pa_pin | 132 | -0.103 | 126 | -0.092 |
| pa_star | 22 | -0.091 | 23 | 0.36 |
| po3 | 85 | -0.186 | 71 | 0.053 |
| rect | 12 | -0.167 | 17 | -0.44 |
| rsi_div | 626 | -0.02 | 582 | 0.003 |
| sess_amd | 262 | -0.016 | 279 | 0.038 |
| sma1040 | 34 | 0.396 | 33 | 0.206 |
| smt | 963 | -0.114 | 901 | -0.022 |
| sweep | 2077 | -0.058 | 1621 | 0.054 |
| tlbreak | 1145 | -0.042 | 1105 | 0.034 |
| turtle55 | 43 | 0.198 | 38 | 0.433 |
| unicorn | 242 | -0.062 | 195 | 0.143 |
| vwap | 3381 | -0.095 | 3957 | 0.031 |
| wavec | 81 | 0.052 | 73 | 0.445 |
| wyck | 89 | 0.163 | 79 | 0.129 |
| zombie | 452 | -0.09 | 451 | 0.02 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 37872 | 36.9 | -0.026 | 26471 | 38.8 | 0.026 |
| abc | 28 | 35.7 | -0.077 | 82 | 34.1 | -0.04 |
| breaker | 176 | 37.5 | 0.018 | 230 | 37.0 | 0.017 |
| breakout | 790 | 38.6 | -0.014 | 324 | 41.0 | 0.05 |
| cisd | 381 | 34.4 | -0.107 | 616 | 38.6 | 0.044 |
| crt | 352 | 34.4 | -0.081 | 527 | 38.5 | 0.025 |
| dbl | 425 | 35.8 | -0.086 | 248 | 39.1 | 0.009 |
| donch | 2384 | 37.3 | -0.018 | 355 | 39.4 | 0.015 |
| ema_stack | 3952 | 37.7 | -0.008 | 943 | 37.5 | -0.025 |
| ew3 | 601 | 38.1 | -0.003 | 406 | 34.2 | -0.117 |
| ew5 | 172 | 41.3 | 0.114 | 35 | 31.4 | -0.129 |
| ew_r2_d1 | 354 | 35.6 | -0.019 | 210 | 39.5 | 0.049 |
| ew_r2_d2 | 174 | 39.1 | 0.13 | 121 | 42.1 | 0.16 |
| ew_r2_v | 573 | 34.2 | -0.077 | 373 | 41.0 | 0.085 |
| ew_r3_d1 | 210 | 33.8 | -0.032 | 35 | 37.1 | 0.054 |
| ew_r3_d2 | 137 | 38.0 | 0.092 | 29 | 44.8 | 0.156 |
| ew_r3_v | 315 | 38.7 | 0.079 | 47 | 38.3 | 0.036 |
| fib | 1162 | 38.5 | 0.015 | 1225 | 39.3 | 0.044 |
| fvg | 1750 | 39.1 | 0.035 | 1360 | 40.7 | 0.066 |
| harm_bat | 0 | None | None | 3 | 33.3 | -0.167 |
| harm_bat_tight | 0 | None | None | 1 | 100.0 | 1.5 |
| harm_butterfly | 7 | 42.9 | 0.071 | 12 | 33.3 | -0.122 |
| harm_butterfly_tight | 1 | 100.0 | 1.5 | 1 | 100.0 | 1.5 |
| harm_crab | 0 | None | None | 1 | 100.0 | 1.5 |
| harm_cypher | 3 | 0.0 | -0.856 | 8 | 50.0 | 0.25 |
| harm_cypher_tight | 1 | 0.0 | -1.0 | 3 | 100.0 | 1.5 |
| harm_gartley | 3 | 33.3 | 0.274 | 4 | 50.0 | 0.25 |
| harm_gartley_tight | 1 | 0.0 | -1.0 | 1 | 100.0 | 1.5 |
| harm_vol_bat | 0 | None | None | 2 | 50.0 | 0.25 |
| harm_vol_butterfly | 4 | 25.0 | -0.375 | 7 | 42.9 | 0.409 |
| harm_vol_butterfly_tight | 1 | 0.0 | -1.0 | 2 | 50.0 | 0.25 |
| harm_vol_crab | 0 | None | None | 2 | 0.0 | -1.0 |
| harm_vol_cypher | 4 | 50.0 | 0.25 | 8 | 62.5 | 0.562 |
| harm_vol_cypher_tight | 1 | 0.0 | -1.0 | 3 | 100.0 | 1.5 |
| harm_vol_gartley | 4 | 0.0 | -0.729 | 3 | 66.7 | 0.667 |
| harm_vol_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| judas | 1667 | 37.9 | -0.026 | 805 | 38.4 | 0.003 |
| kzs | 16 | 18.8 | -0.531 | 20 | 20.0 | -0.406 |
| level | 2304 | 37.2 | -0.038 | 2589 | 39.0 | 0.029 |
| liqline | 1571 | 38.5 | 0.012 | 1147 | 39.2 | 0.043 |
| m2022 | 414 | 40.8 | 0.063 | 278 | 37.8 | -0.01 |
| ma_cross | 1670 | 35.3 | -0.065 | 1134 | 40.0 | 0.043 |
| macd_div | 304 | 35.2 | -0.061 | 1090 | 38.6 | 0.025 |
| msb_ob | 882 | 35.8 | -0.059 | 947 | 39.1 | 0.042 |
| ob | 834 | 35.5 | -0.061 | 706 | 39.9 | 0.075 |
| ohl_break | 479 | 36.3 | -0.064 | 353 | 38.5 | 0.002 |
| ohl_open | 1726 | 36.4 | -0.04 | 1435 | 37.2 | -0.01 |
| orb | 107 | 37.4 | -0.065 | 61 | 44.3 | 0.234 |
| ote | 348 | 36.8 | -0.025 | 476 | 40.8 | 0.069 |
| pa_engulf | 131 | 35.1 | -0.095 | 141 | 38.3 | 0.001 |
| pa_inside | 216 | 40.7 | 0.043 | 144 | 36.1 | -0.018 |
| pa_pin | 112 | 33.0 | -0.117 | 146 | 32.9 | -0.083 |
| pa_star | 17 | 47.1 | 0.251 | 28 | 42.9 | 0.071 |
| po3 | 71 | 39.4 | 0.106 | 83 | 30.1 | -0.212 |
| rect | 17 | 23.5 | -0.292 | 12 | 25.0 | -0.375 |
| rsi_div | 325 | 37.2 | -0.002 | 878 | 36.7 | -0.009 |
| sess_amd | 260 | 36.5 | -0.02 | 278 | 40.3 | 0.053 |
| sma1040 | 28 | 39.3 | 0.032 | 39 | 53.8 | 0.497 |
| smt | 970 | 31.2 | -0.165 | 892 | 39.8 | 0.037 |
| sweep | 1612 | 35.4 | -0.059 | 2080 | 38.8 | 0.032 |
| tlbreak | 1087 | 37.4 | -0.03 | 1162 | 38.4 | 0.021 |
| turtle55 | 61 | 47.5 | 0.262 | 20 | 55.0 | 0.45 |
| unicorn | 206 | 37.4 | 0.006 | 230 | 37.4 | 0.045 |
| vwap | 5853 | 36.9 | -0.03 | 1464 | 37.6 | -0.02 |
| wavec | 48 | 43.8 | 0.276 | 106 | 46.2 | 0.221 |
| wyck | 75 | 40.0 | 0.07 | 92 | 45.7 | 0.223 |
| zombie | 494 | 35.8 | -0.034 | 408 | 37.0 | -0.033 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7586 | 31.7 | -0.041 |
| Mon | 10279 | 41.2 | 0.064 |
| Sat | 6679 | 35.7 | -0.042 |
| Sun | 7171 | 34.3 | -0.107 |
| Thu | 7676 | 38.0 | 0.008 |
| Tue | 17573 | 39.7 | 0.015 |
| Wed | 7578 | 39.0 | 0.005 |
| Asia 00-07 | 19493 | 37.8 | -0.024 |
| Late 20-24 | 8071 | 37.4 | -0.009 |
| London 07-12 | 14686 | 40.1 | 0.027 |
| New York 12-20 | 18566 | 36.2 | -0.019 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 64542 | 37.7 | -0.005 | 0.024 | -4.71 | 27886 | -0.021 | 36656 | 0.007 |  |
| grade A+++ | 492 | 36.6 | -0.027 | -0.172 | +2.11 | 199 | -0.038 | 293 | -0.02 |  |
| grade A+ | 8970 | 38.1 | 0.021 | 0.028 | -0.44 | 3593 | 0.033 | 5377 | 0.012 |  |
| grade A | 21418 | 37.1 | -0.007 | 0.035 | -4.01 | 8589 | -0.044 | 12829 | 0.018 |  |
| grade B | 22349 | 37.3 | -0.022 | 0.031 | -5.01 | 10010 | -0.034 | 12339 | -0.012 |  |
| grade C | 11313 | 39.3 | 0.012 | -0.007 | +1.29 | 5495 | 0.006 | 5818 | 0.017 |  |
| layer htf | 37872 | 36.9 | -0.026 | 0.023 | -6.13 | 16327 | -0.048 | 21545 | -0.01 |  |
| layer loc | 13893 | 37.6 | -0.005 | 0.035 | -3.10 | 5876 | 0.028 | 8017 | -0.029 |  |
| layer vol | 20494 | 38.7 | 0.012 | 0.021 | -0.83 | 9048 | -0.014 | 11446 | 0.033 |  |
| layer reg | 47909 | 37.3 | -0.001 | 0.021 | -3.09 | 20647 | -0.016 | 27262 | 0.011 |  |
| layer time | 36978 | 37.7 | 0.005 | 0.036 | -3.75 | 14008 | -0.022 | 22970 | 0.022 |  |
| no htf | 26670 | 38.8 | 0.025 | 0.025 | +0.04 | 11559 | 0.018 | 15111 | 0.031 |  |
| no loc | 50649 | 37.7 | -0.005 | 0.02 | -3.70 | 22010 | -0.034 | 28639 | 0.017 |  |
| no vol | 44048 | 37.3 | -0.013 | 0.025 | -5.13 | 18838 | -0.024 | 25210 | -0.005 |  |
| no reg | 16633 | 38.8 | -0.018 | 0.031 | -4.01 | 7239 | -0.034 | 9394 | -0.006 |  |
| no time | 27564 | 37.6 | -0.019 | 0.007 | -2.86 | 13878 | -0.019 | 13686 | -0.02 |  |
| grade A / turtle55 | 34 | 58.8 | 0.549 | 0.533 | +0.05 | 14 | 0.492 | 20 | 0.589 |  |
| grade C / ew_r2_d1 | 54 | 57.4 | 0.435 | 0.019 | +2.13 | 25 | 0.4 | 29 | 0.466 |  |
| no loc / wavec | 98 | 51.0 | 0.381 | 0.32 | +0.38 | 38 | 0.365 | 60 | 0.392 |  |
| loc / ew_r3_d2 | 32 | 53.1 | 0.364 | 0.354 | +0.04 | 14 | -0.107 | 18 | 0.731 |  |
| no loc / sma1040 | 64 | 50.0 | 0.356 | 0.164 | +0.92 | 18 | 0.25 | 46 | 0.397 |  |
| grade A / ew_r3_d2 | 77 | 45.5 | 0.321 | 0.23 | +0.51 | 29 | 0.229 | 48 | 0.376 |  |
| grade C / wavec | 39 | 48.7 | 0.316 | 0.349 | -0.12 | 15 | 0.5 | 24 | 0.202 |  |
| no loc / turtle55 | 81 | 49.4 | 0.308 | 0.329 | -0.11 | 31 | 0.348 | 50 | 0.283 |  |
| grade C / pa_engulf | 33 | 51.5 | 0.288 | 0.364 | -0.37 | 16 | 0.406 | 17 | 0.176 |  |
| grade A+ / ew_r3_v | 46 | 50.0 | 0.284 | 0.121 | +0.68 | 17 | -0.026 | 29 | 0.466 |  |
| grade B / wavec | 56 | 50.0 | 0.284 | 0.264 | +0.09 | 18 | 0.156 | 38 | 0.345 |  |
| grade C / ohl_break | 86 | 48.8 | 0.259 | 0.145 | +0.74 | 40 | 0.181 | 46 | 0.326 |  |
| grade A+ / pa_inside | 67 | 47.8 | 0.248 | -0.002 | +1.26 | 25 | 0.3 | 42 | 0.217 |  |
| no loc / wyck | 64 | 46.9 | 0.225 | 0.228 | -0.02 | 29 | 0.152 | 35 | 0.286 |  |
| grade A / ew_r3_v | 170 | 41.2 | 0.19 | 0.012 | +1.46 | 61 | 0.095 | 109 | 0.243 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8017 | 4101 | 51.2 |
| sweep | vwap | 6557 | 3986 | 60.8 |
| ema_stack | sweep | 3341 | 2492 | 74.6 |
| ema_stack | level | 3871 | 2131 | 55.1 |
| fvg | vwap | 4451 | 1799 | 40.4 |
| ohl_open | vwap | 4142 | 1743 | 42.1 |
| macd_div | vwap | 2151 | 1702 | 79.1 |
| level | sweep | 3737 | 1626 | 43.5 |
| fib | vwap | 3029 | 1565 | 51.7 |
| msb_ob | vwap | 2666 | 1481 | 55.6 |
| rsi_div | vwap | 1881 | 1476 | 78.5 |
| fvg | level | 3089 | 1380 | 44.7 |
| smt | vwap | 3041 | 1377 | 45.3 |
| judas | level | 2711 | 1349 | 49.8 |
| ob | vwap | 2494 | 1321 | 53.0 |
| ma_cross | sweep | 2067 | 1309 | 63.3 |
| level | ma_cross | 2514 | 1300 | 51.7 |
| tlbreak | vwap | 2672 | 1275 | 47.7 |
| ma_cross | vwap | 4187 | 1253 | 29.9 |
| liqline | vwap | 3564 | 1242 | 34.8 |
| level | ohl_open | 2301 | 1212 | 52.7 |
| judas | sweep | 1873 | 1128 | 60.2 |
| judas | vwap | 4145 | 1034 | 24.9 |
| liqline | sweep | 1855 | 977 | 52.7 |
| cisd | vwap | 1353 | 974 | 72.0 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 30 | 33.3 | 0.041 |
| 2 families | 404 | 40.3 | 0.067 |
| 2 families (with opposition) | 1348 | 37.6 | -0.009 |
| 3 families | 1187 | 39.3 | 0.054 |
| 3 families (with opposition) | 4665 | 37.7 | -0.006 |
| 4+ families | 951 | 36.5 | -0.057 |
| 4+ families (with opposition) | 4167 | 37.4 | -0.014 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 83.6 | 27677 | 83.9 | 382168 | -1.3 |
| 1m shapes 120/180/240/360 deg | 81.2 | 11852 | 81.1 | 11861 | +0.2 |
| 15m | 65.1 | 19490 | 65.1 | 269871 | +0.0 |
| 15m shapes 120/180/240/360 deg | 63.9 | 9909 | 63.8 | 9893 | +0.3 |
| 1h | 58.2 | 16102 | 58.0 | 222787 | +0.5 |
| 1h shapes 120/180/240/360 deg | 57.0 | 8833 | 57.1 | 8808 | -0.2 |
| 4h | 56.6 | 12024 | 57.7 | 166143 | -2.4 |
| 4h shapes 120/180/240/360 deg | 56.9 | 6768 | 56.9 | 6775 | -0.0 |
| 1d | 55.4 | 3196 | 56.0 | 42940 | -0.7 |
| 1d shapes 120/180/240/360 deg | 57.3 | 2034 | 57.3 | 2039 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 48 | 12.5 | +0.053 | -0.782 | +1.38 |
| 1d | 57 | 43.9 | +0.113 | +0.258 | -0.52 |
| 1h | 84 | 29.8 | +0.243 | +0.200 | +0.16 |
| 4h | 87 | 27.6 | -0.004 | +0.503 | -2.04 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2401 | -0.107 |
| 15 days around full moon | 2325 | 0.034 |

Difference t = -1.75 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 64542 | 48.9 | -0.021 | -0.121 | -1348.7 | -5.37 |
| rr1.5 | 64542 | 40.4 | -0.005 | -0.105 | -336.0 | -1.10 |
| rr2.0 | 64542 | 35.0 | 0.004 | -0.096 | 264.8 | +0.76 |
| rr3.0 | 64542 | 29.5 | 0.024 | -0.076 | 1531.5 | +3.68 |
| rr1.5_be | 64542 | 34.7 | -0.001 | -0.101 | -43.4 | -0.15 |
| rr2.0_be | 64542 | 27.7 | 0.015 | -0.085 | 998.6 | +3.19 |
| rr1.5_h16 | 64542 | 42.0 | -0.001 | -0.101 | -80.4 | -0.28 |
| rr2.0_h16 | 64542 | 38.6 | 0.01 | -0.09 | 622.3 | +1.95 |
| pt_1.5_3 | 64542 | 48.9 | 0.036 | -0.064 | 2311.8 | +7.77 |
| pt_1.0_3 | 64542 | 48.9 | 0.022 | -0.078 | 1416.9 | +5.10 |
| pt_1.5_5 | 64542 | 48.9 | 0.053 | -0.047 | 3420.0 | +11.07 |
| trail_only | 64542 | 48.9 | 0.099 | -0.001 | 6394.5 | +17.80 |

## Exit variant x timeframe x trend (is the htf sign flip caused by the exit? docs/PREREG_2026-11-01.md)

Same entries, every detector pooled. If 'with' stays below 'against' on 1h / 1m under every exit, the exit is not the cause.

| tf | exit | with n | with avg R | with t | against n | against avg R | against t |
|---|---|---|---|---|---|---|---|
| 15m | rr1.0 | 10500 | -0.044 | -4.54 | 7328 | -0.024 | -2.04 |
| 15m | rr1.5 | 10500 | -0.027 | -2.34 | 7328 | -0.0 | -0.03 |
| 15m | rr2.0 | 10500 | -0.011 | -0.83 | 7328 | -0.001 | -0.05 |
| 15m | rr3.0 | 10500 | 0.037 | +2.27 | 7328 | 0.008 | +0.40 |
| 15m | rr1.5_be | 10500 | -0.027 | -2.48 | 7328 | -0.021 | -1.64 |
| 15m | rr2.0_be | 10500 | -0.01 | -0.82 | 7328 | -0.016 | -1.16 |
| 15m | rr1.5_h16 | 10500 | -0.019 | -1.70 | 7328 | -0.006 | -0.49 |
| 15m | rr2.0_h16 | 10500 | -0.01 | -0.79 | 7328 | 0.01 | +0.72 |
| 15m | pt_1.5_3 | 10500 | 0.016 | +1.38 | 7328 | 0.008 | +0.58 |
| 15m | pt_1.0_3 | 10500 | 0.003 | +0.27 | 7328 | 0.006 | +0.48 |
| 15m | pt_1.5_5 | 10500 | 0.04 | +3.28 | 7328 | 0.022 | +1.61 |
| 15m | trail_only | 10500 | 0.097 | +6.76 | 7328 | 0.065 | +4.04 |
| 1d | rr1.0 | 2200 | -0.075 | -3.63 | 1526 | 0.094 | +3.79 |
| 1d | rr1.5 | 2200 | -0.049 | -2.03 | 1526 | 0.18 | +5.93 |
| 1d | rr2.0 | 2200 | -0.025 | -0.91 | 1526 | 0.266 | +7.65 |
| 1d | rr3.0 | 2200 | -0.004 | -0.14 | 1526 | 0.362 | +8.71 |
| 1d | rr1.5_be | 2200 | -0.058 | -2.50 | 1526 | 0.158 | +5.47 |
| 1d | rr2.0_be | 2200 | -0.03 | -1.17 | 1526 | 0.225 | +6.92 |
| 1d | rr1.5_h16 | 2200 | -0.042 | -1.78 | 1526 | 0.153 | +5.17 |
| 1d | rr2.0_h16 | 2200 | -0.007 | -0.25 | 1526 | 0.217 | +6.47 |
| 1d | pt_1.5_3 | 2200 | -0.031 | -1.31 | 1526 | 0.2 | +6.53 |
| 1d | pt_1.0_3 | 2200 | -0.043 | -1.90 | 1526 | 0.167 | +5.90 |
| 1d | pt_1.5_5 | 2200 | -0.034 | -1.41 | 1526 | 0.217 | +6.86 |
| 1d | trail_only | 2200 | -0.016 | -0.60 | 1526 | 0.274 | +7.42 |
| 1h | rr1.0 | 10112 | -0.066 | -6.76 | 7399 | 0.035 | +3.07 |
| 1h | rr1.5 | 10112 | -0.072 | -6.14 | 7399 | 0.036 | +2.58 |
| 1h | rr2.0 | 10112 | -0.068 | -5.12 | 7399 | 0.034 | +2.10 |
| 1h | rr3.0 | 10112 | -0.085 | -5.44 | 7399 | 0.006 | +0.31 |
| 1h | rr1.5_be | 10112 | -0.062 | -5.66 | 7399 | 0.038 | +2.93 |
| 1h | rr2.0_be | 10112 | -0.039 | -3.21 | 7399 | 0.042 | +3.00 |
| 1h | rr1.5_h16 | 10112 | -0.054 | -4.91 | 7399 | 0.039 | +3.02 |
| 1h | rr2.0_h16 | 10112 | -0.037 | -3.01 | 7399 | 0.033 | +2.30 |
| 1h | pt_1.5_3 | 10112 | -0.036 | -3.17 | 7399 | 0.062 | +4.70 |
| 1h | pt_1.0_3 | 10112 | -0.041 | -3.83 | 7399 | 0.059 | +4.78 |
| 1h | pt_1.5_5 | 10112 | -0.027 | -2.30 | 7399 | 0.066 | +4.87 |
| 1h | trail_only | 10112 | 0.003 | +0.26 | 7399 | 0.09 | +5.95 |
| 1m | rr1.0 | 7294 | -0.055 | -4.70 | 4828 | 0.041 | +2.88 |
| 1m | rr1.5 | 7294 | -0.004 | -0.30 | 4828 | 0.087 | +4.88 |
| 1m | rr2.0 | 7294 | 0.043 | +2.58 | 4828 | 0.091 | +4.40 |
| 1m | rr3.0 | 7294 | 0.081 | +3.96 | 4828 | 0.147 | +5.77 |
| 1m | rr1.5_be | 7294 | 0.013 | +0.97 | 4828 | 0.102 | +6.14 |
| 1m | rr2.0_be | 7294 | 0.062 | +4.07 | 4828 | 0.127 | +6.85 |
| 1m | rr1.5_h16 | 7294 | -0.008 | -0.59 | 4828 | 0.088 | +5.23 |
| 1m | rr2.0_h16 | 7294 | 0.038 | +2.46 | 4828 | 0.088 | +4.66 |
| 1m | pt_1.5_3 | 7294 | 0.09 | +6.11 | 4828 | 0.168 | +9.38 |
| 1m | pt_1.0_3 | 7294 | 0.05 | +3.64 | 4828 | 0.132 | +7.97 |
| 1m | pt_1.5_5 | 7294 | 0.134 | +8.42 | 4828 | 0.204 | +10.71 |
| 1m | trail_only | 7294 | 0.242 | +12.36 | 4828 | 0.295 | +12.72 |
| 4h | rr1.0 | 7766 | 0.0 | +0.03 | 5390 | -0.015 | -1.09 |
| 4h | rr1.5 | 7766 | 0.02 | +1.44 | 5390 | -0.052 | -3.20 |
| 4h | rr2.0 | 7766 | 0.026 | +1.68 | 5390 | -0.091 | -5.08 |
| 4h | rr3.0 | 7766 | 0.071 | +3.96 | 5390 | -0.101 | -4.93 |
| 4h | rr1.5_be | 7766 | 0.019 | +1.51 | 5390 | -0.022 | -1.45 |
| 4h | rr2.0_be | 7766 | 0.017 | +1.24 | 5390 | -0.036 | -2.26 |
| 4h | rr1.5_h16 | 7766 | 0.015 | +1.19 | 5390 | -0.037 | -2.41 |
| 4h | rr2.0_h16 | 7766 | 0.01 | +0.74 | 5390 | -0.06 | -3.65 |
| 4h | pt_1.5_3 | 7766 | 0.043 | +3.31 | 5390 | -0.017 | -1.10 |
| 4h | pt_1.0_3 | 7766 | 0.028 | +2.29 | 5390 | -0.017 | -1.20 |
| 4h | pt_1.5_5 | 7766 | 0.051 | +3.86 | 5390 | -0.012 | -0.77 |
| 4h | trail_only | 7766 | 0.072 | +4.81 | 5390 | -0.01 | -0.58 |
