# Strategy lab - real candles (2026-11-14)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 53 | 58.5 | 0.612 | 0.512 | 30.2 | -0.076 | YES |
| 2 | turtle55 | Trend (hedge fund) | 88 | 46.6 | 0.272 | 0.172 | 48.9 | 0.31 |  |
| 3 | pa_star | Price action | 51 | 41.2 | 0.142 | 0.042 | 29.4 | -0.138 |  |
| 4 | orb | Time (sessions) | 175 | 41.7 | 0.1 | 0.0 | 44.6 | 0.192 |  |
| 5 | ew_r2_d2 | Elliott wave | 293 | 40.3 | 0.099 | -0.001 | 36.2 | 0.019 |  |
| 6 | wavec | Elliott wave | 149 | 39.6 | 0.079 | -0.021 | 38.3 | 0.016 |  |
| 7 | ew_r3_d2 | Elliott wave | 157 | 36.9 | 0.055 | -0.045 | 38.2 | 0.075 |  |
| 8 | fib | Fibonacci | 2397 | 39.7 | 0.047 | -0.053 | 37.4 | -0.005 |  |
| 9 | ew_r2_d1 | Elliott wave | 542 | 37.5 | 0.035 | -0.065 | 37.8 | 0.071 |  |
| 10 | breakout | Levels / breakouts | 1035 | 40.1 | 0.034 | -0.066 | 37.8 | -0.016 |  |
| 11 | ote | Fibonacci | 835 | 39.4 | 0.031 | -0.069 | 35.4 | -0.066 |  |
| 12 | msb_ob | SMC / ICT | 1834 | 38.3 | 0.026 | -0.074 | 37.5 | 0.003 |  |
| 13 | fvg | SMC / ICT | 3146 | 38.3 | 0.02 | -0.08 | 38.4 | 0.023 |  |
| 14 | pa_engulf | Price action | 327 | 38.8 | 0.016 | -0.084 | 33.3 | -0.124 |  |
| 15 | wyck | Wyckoff | 192 | 35.9 | 0.01 | -0.09 | 34.9 | -0.008 |  |
| 16 | ob | SMC / ICT | 1676 | 37.6 | 0.009 | -0.091 | 39.1 | 0.048 |  |
| 17 | zombie | Liquidity | 921 | 38.3 | 0.007 | -0.093 | 40.7 | 0.071 |  |
| 18 | m2022 | SMC / ICT | 649 | 37.8 | 0.006 | -0.094 | 41.0 | 0.107 |  |
| 19 | ew_r3_v | Elliott wave | 345 | 35.4 | 0.001 | -0.099 | 37.4 | 0.028 |  |
| 20 | sess_amd | Time (sessions) | 533 | 38.1 | -0.009 | -0.109 | 40.9 | 0.069 |  |
| 21 | level | Levels / breakouts | 4970 | 37.5 | -0.012 | -0.112 | 38.0 | 0.003 |  |
| 22 | donch | Trend (hedge fund) | 2721 | 37.3 | -0.015 | -0.115 | 37.2 | -0.012 |  |
| 23 | judas | Time (sessions) | 2523 | 37.8 | -0.019 | -0.119 | 40.1 | 0.036 |  |
| 24 | smt | Intermarket (SMT) | 1861 | 37.3 | -0.02 | -0.12 | 39.9 | 0.055 |  |
| 25 | sweep | Liquidity | 3626 | 36.7 | -0.02 | -0.12 | 36.7 | -0.019 |  |
| 26 | vwap | Trend (MA) | 7321 | 36.9 | -0.024 | -0.124 | 38.0 | 0.012 |  |
| 27 | liqline | Liquidity | 2668 | 36.7 | -0.027 | -0.127 | 38.3 | 0.018 |  |
| 28 | ma_cross | Trend (MA) | 2815 | 36.8 | -0.029 | -0.129 | 39.4 | 0.044 |  |
| 29 | ema_stack | Trend (MA) | 4847 | 36.7 | -0.031 | -0.131 | 37.8 | 0.007 |  |
| 30 | ew_r3_d1 | Elliott wave | 241 | 33.2 | -0.031 | -0.131 | 41.1 | 0.15 |  |
| 31 | ohl_open | Levels / breakouts | 3059 | 36.6 | -0.032 | -0.132 | 38.2 | 0.021 |  |
| 32 | ew_r2_v | Elliott wave | 918 | 35.5 | -0.034 | -0.134 | 37.4 | 0.017 |  |
| 33 | crt | Liquidity | 931 | 36.5 | -0.037 | -0.137 | 35.1 | -0.072 |  |
| 34 | rsi_div | Momentum / divergence | 1188 | 35.2 | -0.039 | -0.139 | 36.3 | -0.016 |  |
| 35 | tlbreak | Levels / breakouts | 2261 | 36.2 | -0.044 | -0.144 | 37.5 | -0.007 |  |
| 36 | macd_div | Momentum / divergence | 1396 | 35.5 | -0.05 | -0.15 | 37.5 | -0.004 |  |
| 37 | breaker | SMC / ICT | 401 | 34.4 | -0.051 | -0.151 | 32.9 | -0.092 |  |
| 38 | ew3 | Elliott wave | 982 | 36.4 | -0.055 | -0.155 | 37.7 | -0.008 |  |
| 39 | ohl_break | Levels / breakouts | 846 | 36.1 | -0.056 | -0.156 | 35.5 | -0.071 |  |
| 40 | cisd | SMC / ICT | 972 | 34.9 | -0.06 | -0.16 | 35.6 | -0.047 |  |
| 41 | abc | Elliott wave | 108 | 35.2 | -0.06 | -0.16 | 43.5 | 0.131 |  |
| 42 | unicorn | SMC / ICT | 426 | 34.7 | -0.06 | -0.16 | 36.4 | 0.005 |  |
| 43 | pa_inside | Price action | 347 | 35.2 | -0.061 | -0.161 | 32.0 | -0.136 |  |
| 44 | ew5 | Elliott wave | 199 | 33.2 | -0.091 | -0.191 | 34.2 | -0.035 |  |
| 45 | dbl | Chart patterns (range) | 663 | 34.5 | -0.107 | -0.207 | 39.4 | 0.037 |  |
| 46 | po3 | Time (sessions) | 132 | 34.1 | -0.11 | -0.21 | 39.4 | 0.03 |  |
| 47 | pa_pin | Price action | 297 | 30.0 | -0.196 | -0.296 | 39.7 | 0.05 |  |
| 48 | rect | Chart patterns (range) | 33 | 27.3 | -0.211 | -0.311 | 30.3 | -0.196 |  |
| 49 | kzs | Time (sessions) | 38 | 18.4 | -0.457 | -0.557 | 39.5 | 0.02 |  |
| 50 | harm_vol_butterfly_tight | Harmonic: Butterfly (vol swings) | 3 | 66.7 | 0.667 | 0.567 | 0.0 | -1.0 |  |
| 51 | harm_crab | Harmonic: Crab | 2 | 50.0 | 0.25 | 0.15 | 0.0 | -1.0 |  |
| 52 | harm_gartley_tight | Harmonic: Gartley | 2 | 50.0 | 0.25 | 0.15 | 100.0 | 1.5 |  |
| 53 | harm_vol_cypher_tight | Harmonic: Cypher (vol swings) | 4 | 50.0 | 0.25 | 0.15 | 75.0 | 0.875 |  |
| 54 | harm_vol_butterfly | Harmonic: Butterfly (vol swings) | 13 | 30.8 | 0.188 | 0.088 | 23.1 | -0.178 |  |
| 55 | harm_vol_cypher | Harmonic: Cypher (vol swings) | 20 | 40.0 | 0.0 | -0.1 | 40.0 | 0.018 |  |
| 56 | harm_cypher_tight | Harmonic: Cypher | 5 | 40.0 | 0.0 | -0.1 | 60.0 | 0.5 |  |
| 57 | harm_butterfly | Harmonic: Butterfly | 19 | 36.8 | -0.051 | -0.151 | 47.4 | 0.276 |  |
| 58 | harm_butterfly_tight | Harmonic: Butterfly | 3 | 33.3 | -0.167 | -0.267 | 66.7 | 0.667 |  |
| 59 | harm_vol_gartley | Harmonic: Gartley (vol swings) | 8 | 25.0 | -0.24 | -0.34 | 50.0 | 0.385 |  |
| 60 | harm_cypher | Harmonic: Cypher | 18 | 27.8 | -0.269 | -0.369 | 61.1 | 0.602 |  |
| 61 | harm_gartley | Harmonic: Gartley | 8 | 25.0 | -0.375 | -0.475 | 50.0 | 0.25 |  |
| 62 | harm_bat | Harmonic: Bat | 5 | 20.0 | -0.5 | -0.6 | 60.0 | 0.5 |  |
| 63 | harm_vol_bat | Harmonic: Bat (vol swings) | 5 | 20.0 | -0.5 | -0.6 | 20.0 | -0.5 |  |
| 64 | harm_vol_crab | Harmonic: Crab (vol swings) | 3 | 0.0 | -1.0 | -1.1 | 33.3 | -0.167 |  |
| 65 | harm_vol_gartley_tight | Harmonic: Gartley (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 100.0 | 1.5 |  |
| 66 | harm_vol_crab_tight | Harmonic: Crab (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 100.0 | 1.5 |  |
| 67 | harm_vol_bat_tight | Harmonic: Bat (vol swings) | 2 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 68 | harm_bat_tight | Harmonic: Bat | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |

## Stop study: where should the stop sit? (same entries, target fixed at 2.25 ATR, results in ATR, cost 0.15 ATR)

| group | stop | n | target hit % | stopped % | avg ATR | net ATR | mirror avg ATR | t (net vs 0) |
|---|---|---|---|---|---|---|---|---|
| all | 1.0 ATR | 64311 | 29.5 | 67.8 | -0.004 | -0.154 | 0.048 | -26.40 |
| all | 1.5 ATR | 64311 | 37.1 | 58.0 | -0.026 | -0.176 | 0.022 | -24.90 |
| all | 2.0 ATR | 64311 | 42.6 | 49.8 | -0.033 | -0.183 | 0.011 | -22.61 |
| all | 2.5 ATR | 64311 | 46.6 | 43.3 | -0.046 | -0.196 | 0.007 | -21.88 |
| all | 3.0 ATR | 64311 | 49.6 | 37.8 | -0.056 | -0.206 | -0.009 | -21.24 |
| 1m | 1.0 ATR | 11917 | 32.6 | 65.5 | 0.084 | -0.066 | 0.15 | -4.78 |
| 1m | 1.5 ATR | 11917 | 39.0 | 58.2 | 0.007 | -0.143 | 0.095 | -8.58 |
| 1m | 2.0 ATR | 11917 | 44.1 | 51.9 | -0.047 | -0.197 | 0.055 | -10.33 |
| 1m | 2.5 ATR | 11917 | 48.2 | 45.9 | -0.071 | -0.221 | 0.022 | -10.45 |
| 1m | 3.0 ATR | 11917 | 51.8 | 40.5 | -0.077 | -0.227 | -0.004 | -9.83 |
| 15m | 1.0 ATR | 17828 | 29.5 | 68.3 | -0.011 | -0.161 | 0.039 | -14.49 |
| 15m | 1.5 ATR | 17828 | 37.3 | 58.7 | -0.032 | -0.182 | 0.01 | -13.50 |
| 15m | 2.0 ATR | 17828 | 43.8 | 50.5 | -0.024 | -0.174 | 0.012 | -11.26 |
| 15m | 2.5 ATR | 17828 | 47.8 | 44.5 | -0.048 | -0.198 | -0.0 | -11.51 |
| 15m | 3.0 ATR | 17828 | 51.1 | 39.9 | -0.07 | -0.22 | -0.017 | -11.75 |
| 1h | 1.0 ATR | 17420 | 28.4 | 68.4 | -0.033 | -0.183 | 0.041 | -16.56 |
| 1h | 1.5 ATR | 17420 | 36.7 | 58.0 | -0.033 | -0.183 | 0.021 | -13.53 |
| 1h | 2.0 ATR | 17420 | 42.4 | 50.1 | -0.044 | -0.194 | 0.011 | -12.51 |
| 1h | 2.5 ATR | 17420 | 46.7 | 43.8 | -0.052 | -0.202 | 0.02 | -11.75 |
| 1h | 3.0 ATR | 17420 | 50.1 | 38.7 | -0.057 | -0.207 | 0.008 | -11.03 |
| 4h | 1.0 ATR | 13447 | 28.0 | 69.4 | -0.048 | -0.198 | -0.003 | -15.77 |
| 4h | 1.5 ATR | 13447 | 35.7 | 59.0 | -0.064 | -0.214 | -0.013 | -13.95 |
| 4h | 2.0 ATR | 13447 | 41.1 | 49.2 | -0.047 | -0.197 | -0.003 | -11.23 |
| 4h | 2.5 ATR | 13447 | 44.8 | 41.4 | -0.038 | -0.188 | 0.016 | -9.78 |
| 4h | 3.0 ATR | 13447 | 47.0 | 34.3 | -0.038 | -0.188 | 0.005 | -9.11 |
| 1d | 1.0 ATR | 3699 | 29.5 | 64.4 | 0.048 | -0.102 | -0.024 | -4.20 |
| 1d | 1.5 ATR | 3699 | 35.7 | 51.2 | 0.068 | -0.082 | -0.03 | -2.87 |
| 1d | 2.0 ATR | 3699 | 39.0 | 40.6 | 0.076 | -0.074 | -0.09 | -2.32 |
| 1d | 2.5 ATR | 3699 | 40.9 | 33.4 | 0.052 | -0.098 | -0.104 | -2.84 |
| 1d | 3.0 ATR | 3699 | 42.0 | 27.8 | 0.016 | -0.134 | -0.128 | -3.66 |

| group | question | n | value |
|---|---|---|---|
| all | stopped at 1.5 ATR, target reached later | 46999 | 31.5 % reached it later (mirror direction 31.4 %); 73.1 % of all trades were stopped |
| all | MAE of trades that reached the target (ATR) | 39088 | p50 1.05 · p75 2.35 · p90 4.44 |
| 1m | stopped at 1.5 ATR, target reached later | 9123 | 32.5 % reached it later (mirror direction 33.5 %); 76.6 % of all trades were stopped |
| 1m | MAE of trades that reached the target (ATR) | 7689 | p50 0.97 · p75 2.52 · p90 4.67 |
| 15m | stopped at 1.5 ATR, target reached later | 13563 | 35.8 % reached it later (mirror direction 34.5 %); 76.1 % of all trades were stopped |
| 15m | MAE of trades that reached the target (ATR) | 11642 | p50 1.2 · p75 2.64 · p90 5.31 |
| 1h | stopped at 1.5 ATR, target reached later | 13091 | 34.4 % reached it later (mirror direction 35.1 %); 75.1 % of all trades were stopped |
| 1h | MAE of trades that reached the target (ATR) | 11034 | p50 1.19 · p75 2.61 · p90 4.76 |
| 4h | stopped at 1.5 ATR, target reached later | 9163 | 24.1 % reached it later (mirror direction 23.7 %); 68.1 % of all trades were stopped |
| 4h | MAE of trades that reached the target (ATR) | 7108 | p50 0.92 · p75 1.82 · p90 3.12 |
| 1d | stopped at 1.5 ATR, target reached later | 2059 | 13.3 % reached it later (mirror direction 12.4 %); 55.7 % of all trades were stopped |
| 1d | MAE of trades that reached the target (ATR) | 1615 | p50 0.7 · p75 1.24 · p90 2.02 |

Reading: a stop that is never reached only helps if the AVERAGE (net ATR) goes up, not just the target-hit share; compare with the mirror column (the opposite direction on the same bars).


## Pre-registered tests (signals after the freeze date only; docs/PREREG_2026-11-01.md)

| hypothesis | n | win % | avg R | net avg R | t vs random | net 1st half (n) | net 2nd half (n) | PASS |
|---|---|---|---|---|---|---|---|---|
| H1 sess_amd + loc | 94 | 40.4 | 0.033 | -0.067 | +2.04 | -0.31 (47) | 0.177 (47) |  |
| H2 ohl_open + Late 20-24 | 325 | 34.5 | -0.099 | -0.199 | -0.96 | -0.236 (162) | -0.162 (163) |  |

Gate: n >= 100, t > 3.0, net > 0 overall and in both time halves. Under n = 100 it is not evidence, whatever the numbers say.


## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Harmonic: Butterfly (vol swings) | 16 | 0.278 |
| 2 | Harmonic: Crab | 2 | 0.25 |
| 3 | Fibonacci | 3232 | 0.043 |
| 4 | Harmonic: Cypher (vol swings) | 24 | 0.042 |
| 5 | Wyckoff | 192 | 0.01 |
| 6 | Trend (hedge fund) | 2862 | 0.005 |
| 7 | SMC / ICT | 9104 | 0.003 |
| 8 | Elliott wave | 3934 | -0.012 |
| 9 | Time (sessions) | 3401 | -0.02 |
| 10 | Intermarket (SMT) | 1861 | -0.02 |
| 11 | Liquidity | 8146 | -0.021 |
| 12 | Levels / breakouts | 12171 | -0.022 |
| 13 | Trend (MA) | 14983 | -0.027 |
| 14 | Momentum / divergence | 2584 | -0.045 |
| 15 | Price action | 1022 | -0.065 |
| 16 | Harmonic: Butterfly | 22 | -0.067 |
| 17 | Chart patterns (range) | 696 | -0.112 |
| 18 | Harmonic: Cypher | 23 | -0.211 |
| 19 | Harmonic: Gartley | 10 | -0.25 |
| 20 | Harmonic: Gartley (vol swings) | 9 | -0.324 |
| 21 | Harmonic: Bat | 6 | -0.583 |
| 22 | Harmonic: Bat (vol swings) | 7 | -0.643 |
| 23 | Harmonic: Crab (vol swings) | 4 | -1.0 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| breaker | 4h | 107 | 35.5 | -0.005 | -0.105 |
| breakout | 1d | 54 | 48.1 | 0.298 | 0.198 |
| cisd | 1m | 198 | 40.9 | 0.062 | -0.038 |
| crt | 1m | 86 | 44.2 | 0.116 | 0.016 |
| dbl | 1d | 48 | 39.6 | 0.048 | -0.052 |
| donch | 1d | 158 | 36.1 | 0.052 | -0.048 |
| ema_stack | 1d | 282 | 37.9 | 0.094 | -0.006 |
| ew3 | 1d | 63 | 38.1 | 0.047 | -0.053 |
| ew5 | 1m | 41 | 39.0 | -0.024 | -0.124 |
| ew_r2_d1 | 1h | 168 | 44.6 | 0.208 | 0.108 |
| ew_r2_d2 | 1h | 69 | 52.2 | 0.381 | 0.281 |
| ew_r2_v | 1m | 125 | 44.0 | 0.155 | 0.055 |
| ew_r3_d1 | 1d | 34 | 32.4 | 0.156 | 0.056 |
| ew_r3_d2 | 4h | 57 | 38.6 | 0.044 | -0.056 |
| ew_r3_v | 1m | 40 | 55.0 | 0.375 | 0.275 |
| fib | 15m | 665 | 42.0 | 0.087 | -0.013 |
| fvg | 1d | 121 | 41.3 | 0.168 | 0.068 |
| judas | 1m | 844 | 41.9 | 0.069 | -0.031 |
| level | 1m | 1220 | 39.5 | 0.018 | -0.082 |
| liqline | 1d | 155 | 40.0 | 0.207 | 0.107 |
| m2022 | 1d | 81 | 48.1 | 0.375 | 0.275 |
| ma_cross | 1d | 130 | 45.4 | 0.268 | 0.168 |
| macd_div | 1d | 74 | 48.6 | 0.336 | 0.236 |
| msb_ob | 15m | 490 | 42.4 | 0.119 | 0.019 |
| ob | 1m | 307 | 39.4 | 0.077 | -0.023 |
| ohl_break | 1d | 46 | 47.8 | 0.296 | 0.196 |
| ohl_open | 4h | 527 | 39.7 | 0.06 | -0.04 |
| orb | 15m | 169 | 41.4 | 0.095 | -0.005 |
| ote | 1m | 167 | 41.9 | 0.062 | -0.038 |
| pa_engulf | 1m | 50 | 50.0 | 0.254 | 0.154 |
| pa_inside | 1h | 81 | 38.3 | 0.036 | -0.064 |
| pa_pin | 1h | 79 | 32.9 | -0.105 | -0.205 |
| po3 | 15m | 62 | 38.7 | -0.015 | -0.115 |
| rsi_div | 1h | 325 | 37.5 | 0.036 | -0.064 |
| sess_amd | 1h | 277 | 40.4 | 0.059 | -0.041 |
| sma1040 | 1d | 53 | 58.5 | 0.612 | 0.512 |
| smt | 1m | 333 | 42.3 | 0.059 | -0.041 |
| sweep | 1m | 502 | 42.0 | 0.087 | -0.013 |
| tlbreak | 1d | 152 | 38.2 | 0.123 | 0.023 |
| turtle55 | 1d | 88 | 46.6 | 0.272 | 0.172 |
| unicorn | 15m | 81 | 44.4 | 0.175 | 0.075 |
| vwap | 1d | 422 | 36.3 | 0.032 | -0.068 |
| wavec | 1h | 38 | 47.4 | 0.229 | 0.129 |
| wyck | 4h | 57 | 45.6 | 0.226 | 0.126 |
| zombie | 1d | 54 | 44.4 | 0.241 | 0.141 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 67 | -0.119 | 41 | 0.036 |
| breaker | 194 | -0.099 | 207 | -0.007 |
| breakout | 478 | -0.032 | 557 | 0.09 |
| cisd | 515 | -0.1 | 457 | -0.015 |
| crt | 464 | -0.066 | 467 | -0.007 |
| dbl | 315 | -0.144 | 348 | -0.074 |
| donch | 1136 | -0.104 | 1585 | 0.049 |
| ema_stack | 2226 | -0.121 | 2621 | 0.046 |
| ew3 | 502 | -0.18 | 480 | 0.076 |
| ew5 | 67 | -0.071 | 132 | -0.101 |
| ew_r2_d1 | 203 | -0.037 | 339 | 0.078 |
| ew_r2_d2 | 106 | 0.06 | 187 | 0.121 |
| ew_r2_v | 370 | -0.031 | 548 | -0.037 |
| ew_r3_d1 | 99 | -0.181 | 142 | 0.074 |
| ew_r3_d2 | 49 | -0.257 | 108 | 0.196 |
| ew_r3_v | 149 | -0.158 | 196 | 0.121 |
| fib | 1123 | -0.072 | 1274 | 0.152 |
| fvg | 1659 | -0.051 | 1487 | 0.098 |
| harm_bat | 5 | -0.5 | 0 | None |
| harm_bat_tight | 1 | -1.0 | 0 | None |
| harm_butterfly | 11 | -0.042 | 8 | -0.062 |
| harm_butterfly_tight | 3 | -0.167 | 0 | None |
| harm_crab | 2 | 0.25 | 0 | None |
| harm_cypher | 7 | -0.905 | 11 | 0.136 |
| harm_cypher_tight | 1 | -1.0 | 4 | 0.25 |
| harm_gartley | 6 | -0.583 | 2 | 0.25 |
| harm_gartley_tight | 1 | -1.0 | 1 | 1.5 |
| harm_vol_bat | 4 | -1.0 | 1 | 1.5 |
| harm_vol_bat_tight | 2 | -1.0 | 0 | None |
| harm_vol_butterfly | 11 | 0.177 | 2 | 0.25 |
| harm_vol_butterfly_tight | 2 | 0.25 | 1 | 1.5 |
| harm_vol_crab | 3 | -1.0 | 0 | None |
| harm_vol_crab_tight | 1 | -1.0 | 0 | None |
| harm_vol_cypher | 9 | -0.444 | 11 | 0.364 |
| harm_vol_cypher_tight | 1 | -1.0 | 3 | 0.667 |
| harm_vol_gartley | 7 | -0.488 | 1 | 1.5 |
| harm_vol_gartley_tight | 1 | -1.0 | 0 | None |
| judas | 948 | -0.129 | 1575 | 0.046 |
| kzs | 22 | -0.573 | 16 | -0.297 |
| level | 3363 | -0.06 | 1607 | 0.088 |
| liqline | 1256 | -0.106 | 1412 | 0.043 |
| m2022 | 324 | -0.065 | 325 | 0.078 |
| ma_cross | 1462 | -0.084 | 1353 | 0.03 |
| macd_div | 749 | -0.072 | 647 | -0.025 |
| msb_ob | 969 | -0.04 | 865 | 0.1 |
| ob | 819 | -0.13 | 857 | 0.142 |
| ohl_break | 409 | -0.129 | 437 | 0.013 |
| ohl_open | 1536 | -0.117 | 1523 | 0.055 |
| orb | 80 | 0.112 | 95 | 0.09 |
| ote | 382 | -0.127 | 453 | 0.164 |
| pa_engulf | 166 | -0.144 | 161 | 0.18 |
| pa_inside | 166 | -0.235 | 181 | 0.1 |
| pa_pin | 163 | -0.25 | 134 | -0.13 |
| pa_star | 28 | -0.048 | 23 | 0.375 |
| po3 | 73 | -0.212 | 59 | 0.017 |
| rect | 12 | -0.167 | 21 | -0.236 |
| rsi_div | 608 | -0.102 | 580 | 0.027 |
| sess_amd | 235 | -0.001 | 298 | -0.016 |
| sma1040 | 24 | 0.782 | 29 | 0.471 |
| smt | 978 | -0.104 | 883 | 0.073 |
| sweep | 2025 | -0.097 | 1601 | 0.078 |
| tlbreak | 1114 | -0.086 | 1147 | -0.002 |
| turtle55 | 44 | 0.162 | 44 | 0.381 |
| unicorn | 201 | -0.243 | 225 | 0.104 |
| vwap | 3474 | -0.104 | 3847 | 0.048 |
| wavec | 79 | -0.182 | 70 | 0.373 |
| wyck | 100 | 0.019 | 92 | -0.001 |
| zombie | 436 | -0.074 | 485 | 0.079 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 37779 | 37.4 | -0.01 | 26273 | 36.6 | -0.026 |
| abc | 30 | 40.0 | 0.117 | 78 | 33.3 | -0.129 |
| breaker | 205 | 35.1 | -0.047 | 195 | 33.3 | -0.064 |
| breakout | 738 | 40.9 | 0.054 | 293 | 38.6 | -0.004 |
| cisd | 388 | 33.0 | -0.119 | 580 | 36.4 | -0.013 |
| crt | 374 | 33.7 | -0.103 | 557 | 38.4 | 0.008 |
| dbl | 406 | 33.5 | -0.144 | 256 | 35.9 | -0.055 |
| donch | 2361 | 37.1 | -0.017 | 350 | 38.9 | 0.009 |
| ema_stack | 3903 | 37.4 | -0.011 | 915 | 34.1 | -0.104 |
| ew3 | 592 | 38.0 | -0.002 | 388 | 34.0 | -0.131 |
| ew5 | 152 | 33.6 | -0.081 | 47 | 31.9 | -0.122 |
| ew_r2_d1 | 339 | 35.1 | -0.013 | 202 | 41.6 | 0.12 |
| ew_r2_d2 | 165 | 37.6 | 0.049 | 128 | 43.8 | 0.164 |
| ew_r2_v | 550 | 35.1 | -0.048 | 366 | 36.3 | -0.01 |
| ew_r3_d1 | 205 | 33.2 | -0.022 | 36 | 33.3 | -0.082 |
| ew_r3_d2 | 128 | 34.4 | 0.02 | 29 | 48.3 | 0.207 |
| ew_r3_v | 296 | 35.1 | 0.01 | 49 | 36.7 | -0.055 |
| fib | 1179 | 39.4 | 0.031 | 1206 | 40.0 | 0.063 |
| fvg | 1787 | 39.5 | 0.053 | 1333 | 37.1 | -0.018 |
| harm_bat | 2 | 0.0 | -1.0 | 3 | 33.3 | -0.167 |
| harm_bat_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| harm_butterfly | 6 | 66.7 | 0.667 | 13 | 23.1 | -0.382 |
| harm_butterfly_tight | 1 | 100.0 | 1.5 | 2 | 0.0 | -1.0 |
| harm_crab | 0 | None | None | 2 | 50.0 | 0.25 |
| harm_cypher | 11 | 9.1 | -0.712 | 7 | 57.1 | 0.429 |
| harm_cypher_tight | 3 | 33.3 | -0.167 | 2 | 50.0 | 0.25 |
| harm_gartley | 3 | 33.3 | -0.167 | 5 | 20.0 | -0.5 |
| harm_gartley_tight | 1 | 0.0 | -1.0 | 1 | 100.0 | 1.5 |
| harm_vol_bat | 2 | 0.0 | -1.0 | 3 | 33.3 | -0.167 |
| harm_vol_bat_tight | 1 | 0.0 | -1.0 | 1 | 0.0 | -1.0 |
| harm_vol_butterfly | 3 | 66.7 | 0.667 | 10 | 20.0 | 0.044 |
| harm_vol_butterfly_tight | 1 | 100.0 | 1.5 | 2 | 50.0 | 0.25 |
| harm_vol_crab | 0 | None | None | 3 | 0.0 | -1.0 |
| harm_vol_crab_tight | 0 | None | None | 1 | 0.0 | -1.0 |
| harm_vol_cypher | 12 | 16.7 | -0.583 | 8 | 75.0 | 0.875 |
| harm_vol_cypher_tight | 2 | 0.0 | -1.0 | 2 | 100.0 | 1.5 |
| harm_vol_gartley | 4 | 0.0 | -0.729 | 4 | 50.0 | 0.25 |
| harm_vol_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| judas | 1633 | 39.5 | 0.02 | 870 | 34.6 | -0.095 |
| kzs | 15 | 20.0 | -0.417 | 23 | 17.4 | -0.483 |
| level | 2416 | 37.7 | -0.017 | 2525 | 37.4 | -0.005 |
| liqline | 1527 | 38.2 | 0.013 | 1134 | 34.7 | -0.079 |
| m2022 | 375 | 38.4 | 0.029 | 271 | 36.5 | -0.032 |
| ma_cross | 1687 | 37.4 | -0.015 | 1113 | 36.0 | -0.05 |
| macd_div | 273 | 38.5 | 0.031 | 1119 | 34.9 | -0.067 |
| msb_ob | 910 | 38.0 | 0.015 | 913 | 38.6 | 0.036 |
| ob | 896 | 37.9 | 0.014 | 770 | 37.1 | -0.0 |
| ohl_break | 537 | 37.4 | -0.024 | 305 | 33.4 | -0.115 |
| ohl_open | 1658 | 37.2 | -0.017 | 1393 | 35.8 | -0.049 |
| orb | 102 | 45.1 | 0.149 | 73 | 37.0 | 0.031 |
| ote | 367 | 37.3 | -0.029 | 462 | 41.1 | 0.081 |
| pa_engulf | 149 | 35.6 | -0.072 | 177 | 41.8 | 0.095 |
| pa_inside | 209 | 36.4 | -0.047 | 137 | 33.6 | -0.074 |
| pa_pin | 131 | 27.5 | -0.227 | 166 | 31.9 | -0.172 |
| pa_star | 16 | 37.5 | -0.062 | 35 | 42.9 | 0.236 |
| po3 | 62 | 37.1 | -0.036 | 69 | 31.9 | -0.163 |
| rect | 18 | 27.8 | -0.108 | 15 | 26.7 | -0.333 |
| rsi_div | 324 | 38.6 | 0.058 | 862 | 33.9 | -0.076 |
| sess_amd | 239 | 40.2 | 0.038 | 293 | 36.5 | -0.044 |
| sma1040 | 19 | 52.6 | 0.389 | 34 | 61.8 | 0.737 |
| smt | 918 | 35.6 | -0.067 | 941 | 38.9 | 0.026 |
| sweep | 1596 | 37.2 | -0.012 | 2018 | 36.4 | -0.025 |
| tlbreak | 1096 | 35.8 | -0.069 | 1159 | 36.8 | -0.015 |
| turtle55 | 67 | 43.3 | 0.194 | 21 | 57.1 | 0.519 |
| unicorn | 216 | 37.0 | -0.024 | 209 | 32.5 | -0.092 |
| vwap | 5838 | 37.2 | -0.016 | 1461 | 35.9 | -0.055 |
| wavec | 50 | 44.0 | 0.273 | 99 | 37.4 | -0.019 |
| wyck | 87 | 34.5 | -0.061 | 105 | 37.1 | 0.068 |
| zombie | 496 | 39.5 | 0.047 | 424 | 37.0 | -0.038 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 13478 | 33.7 | -0.043 |
| Mon | 7563 | 39.5 | 0.015 |
| Sat | 12907 | 36.5 | -0.033 |
| Sun | 7374 | 36.8 | -0.056 |
| Thu | 7646 | 37.7 | 0.021 |
| Tue | 7673 | 38.2 | -0.026 |
| Wed | 7670 | 40.1 | 0.031 |
| Asia 00-07 | 17788 | 38.0 | -0.007 |
| Late 20-24 | 12902 | 36.0 | -0.042 |
| London 07-12 | 9577 | 39.7 | 0.016 |
| New York 12-20 | 20345 | 35.9 | -0.037 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 64311 | 37.1 | -0.017 | 0.009 | -4.35 | 27817 | -0.029 | 36494 | -0.008 |  |
| grade A+++ | 479 | 43.8 | 0.154 | 0.048 | +1.49 | 229 | 0.026 | 250 | 0.27 |  |
| grade A+ | 8708 | 36.5 | -0.012 | 0.022 | -2.08 | 3851 | -0.01 | 4857 | -0.013 |  |
| grade A | 19156 | 36.7 | -0.016 | 0.016 | -2.96 | 8507 | -0.066 | 10649 | 0.023 |  |
| grade B | 22856 | 37.2 | -0.015 | 0.001 | -1.53 | 10130 | -0.009 | 12726 | -0.019 |  |
| grade C | 13112 | 37.4 | -0.033 | 0.003 | -2.66 | 5100 | -0.023 | 8012 | -0.039 |  |
| layer htf | 37779 | 37.4 | -0.01 | 0.015 | -3.04 | 16276 | -0.023 | 21503 | 0.001 |  |
| layer loc | 13959 | 37.4 | -0.004 | 0.004 | -0.58 | 5989 | 0.002 | 7970 | -0.009 |  |
| layer vol | 20562 | 37.3 | -0.016 | 0.021 | -3.41 | 8975 | -0.03 | 11587 | -0.005 |  |
| layer reg | 45637 | 36.4 | -0.018 | 0.011 | -4.05 | 19827 | -0.032 | 25810 | -0.007 |  |
| layer time | 33621 | 37.0 | -0.013 | 0.01 | -2.72 | 15594 | -0.045 | 18027 | 0.015 |  |
| no htf | 26532 | 36.5 | -0.028 | 0.002 | -3.15 | 11541 | -0.037 | 14991 | -0.021 |  |
| no loc | 50352 | 37.0 | -0.021 | 0.011 | -4.61 | 21828 | -0.037 | 28524 | -0.008 |  |
| no vol | 43749 | 36.9 | -0.018 | 0.004 | -2.95 | 18842 | -0.028 | 24907 | -0.01 |  |
| no reg | 18674 | 38.8 | -0.016 | 0.005 | -1.77 | 7990 | -0.021 | 10684 | -0.012 |  |
| no time | 30690 | 37.2 | -0.022 | 0.008 | -3.46 | 12223 | -0.008 | 18467 | -0.031 |  |
| no loc / sma1040 | 48 | 60.4 | 0.664 | -0.113 | +3.65 | 15 | 0.833 | 33 | 0.587 |  |
| grade A+ / orb | 53 | 56.6 | 0.438 | 0.222 | +0.82 | 19 | 0.974 | 34 | 0.139 |  |
| grade A / wavec | 54 | 48.1 | 0.326 | 0.053 | +1.41 | 28 | 0.339 | 26 | 0.311 |  |
| grade C / ew_r2_d2 | 31 | 51.6 | 0.29 | 0.048 | +0.83 | 13 | 0.154 | 18 | 0.389 |  |
| no loc / turtle55 | 88 | 46.6 | 0.272 | 0.31 | -0.25 | 32 | 0.114 | 56 | 0.362 |  |
| grade C / pa_pin | 43 | 48.8 | 0.221 | 0.105 | +0.44 | 19 | 0.316 | 24 | 0.146 |  |
| grade A+++ / msb_ob | 37 | 45.9 | 0.217 | 0.076 | +0.61 | 15 | 0.167 | 22 | 0.251 |  |
| grade A / pa_engulf | 122 | 45.9 | 0.213 | -0.127 | +2.84 | 51 | 0.102 | 71 | 0.293 |  |
| no loc / wavec | 100 | 44.0 | 0.187 | -0.071 | +1.74 | 41 | 0.341 | 59 | 0.079 |  |
| grade A+ / ew_r3_v | 46 | 41.3 | 0.178 | 0.326 | -0.59 | 18 | 0.556 | 28 | -0.065 |  |
| grade A+ / breakout | 336 | 44.0 | 0.164 | 0.033 | +1.47 | 155 | 0.179 | 181 | 0.15 |  |
| grade A+ / ew_r2_d1 | 92 | 40.2 | 0.158 | 0.01 | +0.91 | 37 | 0.141 | 55 | 0.169 |  |
| grade A / turtle55 | 39 | 43.6 | 0.155 | 0.31 | -0.65 | 14 | 0.127 | 25 | 0.171 |  |
| loc / ew_r2_d2 | 107 | 43.0 | 0.129 | -0.074 | +1.40 | 36 | 0.152 | 71 | 0.117 |  |
| grade C / ote | 155 | 43.2 | 0.125 | -0.071 | +1.69 | 61 | 0.156 | 94 | 0.105 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8247 | 4041 | 49.0 |
| sweep | vwap | 6456 | 3883 | 60.1 |
| ema_stack | sweep | 3249 | 2369 | 72.9 |
| ema_stack | level | 3942 | 2132 | 54.1 |
| fvg | vwap | 4576 | 1785 | 39.0 |
| macd_div | vwap | 2127 | 1707 | 80.3 |
| ohl_open | vwap | 3953 | 1666 | 42.1 |
| fib | vwap | 3078 | 1600 | 52.0 |
| judas | level | 2759 | 1557 | 56.4 |
| level | sweep | 3673 | 1549 | 42.2 |
| msb_ob | vwap | 2676 | 1517 | 56.7 |
| ob | vwap | 2662 | 1456 | 54.7 |
| fvg | level | 3250 | 1453 | 44.7 |
| rsi_div | vwap | 1805 | 1399 | 77.5 |
| smt | vwap | 3002 | 1346 | 44.8 |
| level | ma_cross | 2552 | 1337 | 52.4 |
| ma_cross | sweep | 2049 | 1288 | 62.9 |
| ma_cross | vwap | 4184 | 1263 | 30.2 |
| tlbreak | vwap | 2671 | 1259 | 47.1 |
| liqline | vwap | 3516 | 1214 | 34.5 |
| judas | vwap | 4144 | 1203 | 29.0 |
| level | ohl_open | 2297 | 1158 | 50.4 |
| judas | sweep | 1793 | 1096 | 61.1 |
| fvg | ohl_open | 1218 | 997 | 81.9 |
| level | liqline | 1880 | 989 | 52.6 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 36 | 52.8 | 0.369 |
| 2 families | 434 | 39.4 | 0.051 |
| 2 families (with opposition) | 1380 | 37.4 | -0.003 |
| 3 families | 1054 | 37.1 | -0.006 |
| 3 families (with opposition) | 4614 | 36.6 | -0.03 |
| 4+ families | 933 | 38.4 | -0.005 |
| 4+ families (with opposition) | 4221 | 35.8 | -0.046 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 83.8 | 29018 | 83.6 | 399379 | +0.9 |
| 1m shapes 120/180/240/360 deg | 80.8 | 11552 | 81.4 | 11774 | -1.6 |
| 15m | 65.0 | 19967 | 65.0 | 276663 | +0.2 |
| 15m shapes 120/180/240/360 deg | 63.0 | 10417 | 63.5 | 10307 | -1.0 |
| 1h | 58.0 | 16117 | 57.9 | 223245 | +0.3 |
| 1h shapes 120/180/240/360 deg | 56.7 | 8800 | 57.3 | 8766 | -1.1 |
| 4h | 56.6 | 12033 | 57.7 | 166416 | -2.5 |
| 4h shapes 120/180/240/360 deg | 56.9 | 6774 | 56.6 | 6785 | +0.6 |
| 1d | 55.5 | 3175 | 56.1 | 42604 | -0.7 |
| 1d shapes 120/180/240/360 deg | 57.5 | 2020 | 57.6 | 2024 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 87 | 25.3 | +0.314 | +0.078 | +0.52 |
| 1d | 55 | 41.8 | +0.031 | +0.397 | -1.19 |
| 1h | 130 | 23.1 | -0.053 | -0.121 | +0.39 |
| 4h | 99 | 33.3 | +0.157 | +0.049 | +0.59 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2380 | -0.101 |
| 15 days around full moon | 2328 | 0.035 |

Difference t = -1.69 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 64311 | 48.6 | -0.027 | -0.127 | -1705.1 | -6.81 |
| rr1.5 | 64311 | 39.9 | -0.017 | -0.117 | -1103.7 | -3.64 |
| rr2.0 | 64311 | 34.9 | -0.002 | -0.102 | -98.6 | -0.29 |
| rr3.0 | 64311 | 29.3 | 0.01 | -0.09 | 656.9 | +1.60 |
| rr1.5_be | 64311 | 34.2 | -0.01 | -0.11 | -647.4 | -2.30 |
| rr2.0_be | 64311 | 27.5 | 0.008 | -0.092 | 539.3 | +1.73 |
| rr1.5_h16 | 64311 | 41.5 | -0.012 | -0.112 | -748.9 | -2.63 |
| rr2.0_h16 | 64311 | 38.3 | 0.001 | -0.099 | 37.0 | +0.12 |
| pt_1.5_3 | 64311 | 48.5 | 0.025 | -0.075 | 1578.6 | +5.35 |
| pt_1.0_3 | 64311 | 48.6 | 0.013 | -0.087 | 830.0 | +3.01 |
| pt_1.5_5 | 64311 | 48.5 | 0.043 | -0.057 | 2767.2 | +9.01 |
| trail_only | 64311 | 48.5 | 0.089 | -0.011 | 5743.3 | +16.06 |

## Exit variant x timeframe x trend (is the htf sign flip caused by the exit? docs/PREREG_2026-11-01.md)

Same entries, every detector pooled. If 'with' stays below 'against' on 1h / 1m under every exit, the exit is not the cause.

| tf | exit | with n | with avg R | with t | against n | against avg R | against t |
|---|---|---|---|---|---|---|---|
| 15m | rr1.0 | 10397 | -0.011 | -1.18 | 7372 | -0.044 | -3.80 |
| 15m | rr1.5 | 10397 | -0.015 | -1.27 | 7372 | -0.026 | -1.86 |
| 15m | rr2.0 | 10397 | 0.003 | +0.20 | 7372 | -0.022 | -1.39 |
| 15m | rr3.0 | 10397 | 0.044 | +2.63 | 7372 | 0.021 | +1.09 |
| 15m | rr1.5_be | 10397 | -0.002 | -0.21 | 7372 | -0.032 | -2.46 |
| 15m | rr2.0_be | 10397 | 0.009 | +0.76 | 7372 | -0.03 | -2.12 |
| 15m | rr1.5_h16 | 10397 | -0.015 | -1.39 | 7372 | -0.034 | -2.63 |
| 15m | rr2.0_h16 | 10397 | -0.002 | -0.13 | 7372 | -0.035 | -2.46 |
| 15m | pt_1.5_3 | 10397 | 0.037 | +3.19 | 7372 | 0.005 | +0.37 |
| 15m | pt_1.0_3 | 10397 | 0.028 | +2.60 | 7372 | -0.003 | -0.24 |
| 15m | pt_1.5_5 | 10397 | 0.06 | +5.00 | 7372 | 0.023 | +1.62 |
| 15m | trail_only | 10397 | 0.114 | +8.05 | 7372 | 0.073 | +4.45 |
| 1d | rr1.0 | 2181 | -0.042 | -2.02 | 1518 | 0.095 | +3.82 |
| 1d | rr1.5 | 2181 | -0.038 | -1.56 | 1518 | 0.165 | +5.45 |
| 1d | rr2.0 | 2181 | -0.048 | -1.79 | 1518 | 0.223 | +6.52 |
| 1d | rr3.0 | 2181 | -0.004 | -0.12 | 1518 | 0.31 | +7.71 |
| 1d | rr1.5_be | 2181 | -0.054 | -2.38 | 1518 | 0.124 | +4.39 |
| 1d | rr2.0_be | 2181 | -0.048 | -1.95 | 1518 | 0.185 | +5.81 |
| 1d | rr1.5_h16 | 2181 | -0.024 | -1.00 | 1518 | 0.157 | +5.31 |
| 1d | rr2.0_h16 | 2181 | -0.012 | -0.46 | 1518 | 0.208 | +6.29 |
| 1d | pt_1.5_3 | 2181 | -0.032 | -1.35 | 1518 | 0.168 | +5.63 |
| 1d | pt_1.0_3 | 2181 | -0.029 | -1.31 | 1518 | 0.151 | +5.42 |
| 1d | pt_1.5_5 | 2181 | -0.031 | -1.31 | 1518 | 0.184 | +5.96 |
| 1d | trail_only | 2181 | -0.015 | -0.57 | 1518 | 0.237 | +6.65 |
| 1h | rr1.0 | 10078 | -0.051 | -5.24 | 7285 | 0.014 | +1.21 |
| 1h | rr1.5 | 10078 | -0.051 | -4.32 | 7285 | 0.017 | +1.19 |
| 1h | rr2.0 | 10078 | -0.048 | -3.61 | 7285 | 0.053 | +3.24 |
| 1h | rr3.0 | 10078 | -0.061 | -3.87 | 7285 | 0.019 | +1.00 |
| 1h | rr1.5_be | 10078 | -0.039 | -3.59 | 7285 | 0.021 | +1.59 |
| 1h | rr2.0_be | 10078 | -0.025 | -2.09 | 7285 | 0.048 | +3.36 |
| 1h | rr1.5_h16 | 10078 | -0.033 | -3.00 | 7285 | 0.028 | +2.17 |
| 1h | rr2.0_h16 | 10078 | -0.021 | -1.70 | 7285 | 0.048 | +3.27 |
| 1h | pt_1.5_3 | 10078 | -0.012 | -1.02 | 7285 | 0.045 | +3.34 |
| 1h | pt_1.0_3 | 10078 | -0.021 | -1.93 | 7285 | 0.04 | +3.19 |
| 1h | pt_1.5_5 | 10078 | 0.002 | +0.20 | 7285 | 0.046 | +3.43 |
| 1h | trail_only | 10078 | 0.038 | +2.82 | 7285 | 0.069 | +4.60 |
| 1m | rr1.0 | 7132 | -0.003 | -0.27 | 4652 | -0.093 | -6.39 |
| 1m | rr1.5 | 7132 | 0.074 | +5.08 | 4652 | -0.092 | -5.32 |
| 1m | rr2.0 | 7132 | 0.126 | +7.44 | 4652 | -0.083 | -4.16 |
| 1m | rr3.0 | 7132 | 0.146 | +7.06 | 4652 | -0.121 | -5.19 |
| 1m | rr1.5_be | 7132 | 0.077 | +5.64 | 4652 | -0.066 | -4.02 |
| 1m | rr2.0_be | 7132 | 0.133 | +8.57 | 4652 | -0.039 | -2.14 |
| 1m | rr1.5_h16 | 7132 | 0.063 | +4.60 | 4652 | -0.058 | -3.53 |
| 1m | rr2.0_h16 | 7132 | 0.101 | +6.44 | 4652 | -0.039 | -2.14 |
| 1m | pt_1.5_3 | 7132 | 0.14 | +9.41 | 4652 | -0.007 | -0.39 |
| 1m | pt_1.0_3 | 7132 | 0.101 | +7.32 | 4652 | -0.028 | -1.69 |
| 1m | pt_1.5_5 | 7132 | 0.194 | +11.96 | 4652 | 0.028 | +1.50 |
| 1m | trail_only | 7132 | 0.312 | +15.47 | 4652 | 0.107 | +4.73 |
| 4h | rr1.0 | 7991 | -0.016 | -1.44 | 5446 | -0.049 | -3.64 |
| 4h | rr1.5 | 7991 | -0.017 | -1.26 | 5446 | -0.08 | -5.02 |
| 4h | rr2.0 | 7991 | 0.002 | +0.11 | 5446 | -0.106 | -6.00 |
| 4h | rr3.0 | 7991 | 0.046 | +2.60 | 5446 | -0.138 | -6.93 |
| 4h | rr1.5_be | 7991 | -0.013 | -1.09 | 5446 | -0.056 | -3.75 |
| 4h | rr2.0_be | 7991 | 0.001 | +0.05 | 5446 | -0.065 | -4.04 |
| 4h | rr1.5_h16 | 7991 | -0.011 | -0.87 | 5446 | -0.08 | -5.32 |
| 4h | rr2.0_h16 | 7991 | -0.006 | -0.42 | 5446 | -0.103 | -6.38 |
| 4h | pt_1.5_3 | 7991 | 0.013 | +1.02 | 5446 | -0.05 | -3.37 |
| 4h | pt_1.0_3 | 7991 | 0.005 | +0.42 | 5446 | -0.052 | -3.71 |
| 4h | pt_1.5_5 | 7991 | 0.019 | +1.47 | 5446 | -0.044 | -2.94 |
| 4h | trail_only | 7991 | 0.038 | +2.64 | 5446 | -0.044 | -2.65 |
