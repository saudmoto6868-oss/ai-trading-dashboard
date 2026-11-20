# Strategy lab - real candles (2026-11-15)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 58 | 53.4 | 0.486 | 0.386 | 27.6 | -0.157 | YES |
| 2 | turtle55 | Trend (hedge fund) | 82 | 45.1 | 0.282 | 0.182 | 43.9 | 0.229 |  |
| 3 | orb | Time (sessions) | 182 | 46.2 | 0.207 | 0.107 | 44.0 | 0.165 |  |
| 4 | wavec | Elliott wave | 152 | 43.4 | 0.153 | 0.053 | 36.2 | -0.051 |  |
| 5 | ew_r3_d2 | Elliott wave | 157 | 40.8 | 0.14 | 0.04 | 36.9 | 0.077 |  |
| 6 | wyck | Wyckoff | 181 | 42.0 | 0.128 | 0.028 | 43.1 | 0.162 |  |
| 7 | ew_r2_d2 | Elliott wave | 286 | 39.9 | 0.103 | 0.003 | 39.2 | 0.088 |  |
| 8 | ote | Fibonacci | 802 | 41.6 | 0.084 | -0.016 | 37.9 | -0.006 |  |
| 9 | breakout | Levels / breakouts | 1022 | 41.7 | 0.071 | -0.029 | 43.0 | 0.106 |  |
| 10 | unicorn | SMC / ICT | 450 | 39.1 | 0.062 | -0.038 | 39.8 | 0.092 |  |
| 11 | po3 | Time (sessions) | 132 | 40.9 | 0.062 | -0.038 | 41.7 | 0.12 |  |
| 12 | ew_r2_d1 | Elliott wave | 589 | 38.7 | 0.056 | -0.044 | 36.7 | 0.015 |  |
| 13 | ohl_break | Levels / breakouts | 892 | 40.5 | 0.052 | -0.048 | 40.6 | 0.059 |  |
| 14 | donch | Trend (hedge fund) | 2722 | 39.3 | 0.034 | -0.066 | 39.5 | 0.039 |  |
| 15 | ew_r3_d1 | Elliott wave | 240 | 37.9 | 0.031 | -0.069 | 35.0 | 0.004 |  |
| 16 | fib | Fibonacci | 2339 | 39.1 | 0.029 | -0.071 | 37.4 | -0.015 |  |
| 17 | m2022 | SMC / ICT | 674 | 39.0 | 0.027 | -0.073 | 40.4 | 0.087 |  |
| 18 | liqline | Liquidity | 2682 | 38.9 | 0.022 | -0.078 | 38.8 | 0.027 |  |
| 19 | msb_ob | SMC / ICT | 1894 | 38.2 | 0.016 | -0.084 | 39.5 | 0.05 |  |
| 20 | ew_r3_v | Elliott wave | 370 | 37.6 | 0.013 | -0.087 | 36.5 | 0.02 |  |
| 21 | fvg | SMC / ICT | 3128 | 37.7 | 0.008 | -0.092 | 38.3 | 0.025 |  |
| 22 | rsi_div | Momentum / divergence | 1194 | 37.4 | 0.005 | -0.095 | 37.1 | -0.001 |  |
| 23 | macd_div | Momentum / divergence | 1414 | 37.6 | 0.005 | -0.095 | 37.3 | -0.005 |  |
| 24 | pa_inside | Price action | 326 | 38.0 | -0.003 | -0.103 | 37.4 | -0.023 |  |
| 25 | ew_r2_v | Elliott wave | 922 | 36.3 | -0.005 | -0.105 | 36.0 | -0.006 |  |
| 26 | ohl_open | Levels / breakouts | 3085 | 37.4 | -0.008 | -0.108 | 38.9 | 0.027 |  |
| 27 | tlbreak | Levels / breakouts | 2224 | 37.6 | -0.008 | -0.108 | 38.4 | 0.02 |  |
| 28 | sess_amd | Time (sessions) | 512 | 38.5 | -0.01 | -0.11 | 39.1 | 0.023 |  |
| 29 | sweep | Liquidity | 3637 | 37.0 | -0.012 | -0.112 | 39.3 | 0.045 |  |
| 30 | vwap | Trend (MA) | 7341 | 37.4 | -0.013 | -0.113 | 39.0 | 0.034 |  |
| 31 | judas | Time (sessions) | 2448 | 37.9 | -0.017 | -0.117 | 39.9 | 0.032 |  |
| 32 | ma_cross | Trend (MA) | 2849 | 37.0 | -0.018 | -0.118 | 38.1 | 0.018 |  |
| 33 | pa_pin | Price action | 281 | 37.0 | -0.018 | -0.118 | 36.7 | -0.048 |  |
| 34 | ema_stack | Trend (MA) | 4908 | 37.1 | -0.02 | -0.12 | 39.6 | 0.053 |  |
| 35 | ob | SMC / ICT | 1655 | 36.9 | -0.021 | -0.121 | 39.0 | 0.033 |  |
| 36 | level | Levels / breakouts | 5030 | 37.0 | -0.023 | -0.123 | 38.1 | -0.001 |  |
| 37 | abc | Elliott wave | 114 | 35.1 | -0.025 | -0.125 | 37.7 | -0.0 |  |
| 38 | dbl | Chart patterns (range) | 659 | 37.2 | -0.03 | -0.13 | 38.2 | 0.007 |  |
| 39 | breaker | SMC / ICT | 401 | 34.9 | -0.031 | -0.131 | 39.7 | 0.104 |  |
| 40 | ew5 | Elliott wave | 183 | 35.5 | -0.034 | -0.134 | 39.3 | 0.067 |  |
| 41 | ew3 | Elliott wave | 1003 | 36.1 | -0.056 | -0.156 | 40.0 | 0.045 |  |
| 42 | cisd | SMC / ICT | 970 | 34.3 | -0.058 | -0.158 | 34.4 | -0.06 |  |
| 43 | crt | Liquidity | 972 | 34.9 | -0.068 | -0.168 | 37.6 | 0.006 |  |
| 44 | pa_star | Price action | 43 | 34.9 | -0.068 | -0.168 | 34.9 | -0.06 |  |
| 45 | smt | Intermarket (SMT) | 1753 | 35.5 | -0.069 | -0.169 | 40.3 | 0.059 |  |
| 46 | pa_engulf | Price action | 303 | 34.3 | -0.087 | -0.187 | 36.3 | -0.038 |  |
| 47 | zombie | Liquidity | 916 | 34.0 | -0.091 | -0.191 | 39.4 | 0.047 |  |
| 48 | kzs | Time (sessions) | 31 | 32.3 | -0.133 | -0.233 | 35.5 | -0.113 |  |
| 49 | harm_cypher_tight | Harmonic: Cypher | 4 | 100.0 | 1.5 | 1.4 | 25.0 | -0.375 |  |
| 50 | harm_vol_cypher_tight | Harmonic: Cypher (vol swings) | 4 | 75.0 | 0.875 | 0.775 | 50.0 | 0.25 |  |
| 51 | harm_butterfly_tight | Harmonic: Butterfly | 3 | 66.7 | 0.667 | 0.567 | 66.7 | 0.929 |  |
| 52 | harm_vol_gartley | Harmonic: Gartley (vol swings) | 8 | 62.5 | 0.562 | 0.462 | 50.0 | 0.25 |  |
| 53 | harm_cypher | Harmonic: Cypher | 16 | 56.2 | 0.448 | 0.348 | 37.5 | -0.021 |  |
| 54 | harm_vol_crab_tight | Harmonic: Crab (vol swings) | 1 | 0.0 | 0.339 | 0.239 | 0.0 | -1.0 |  |
| 55 | harm_crab | Harmonic: Crab | 2 | 50.0 | 0.25 | 0.15 | 0.0 | -1.0 |  |
| 56 | harm_vol_bat_tight | Harmonic: Bat (vol swings) | 2 | 50.0 | 0.25 | 0.15 | 50.0 | 0.25 |  |
| 57 | harm_bat_tight | Harmonic: Bat | 2 | 50.0 | 0.25 | 0.15 | 50.0 | 0.25 |  |
| 58 | harm_butterfly | Harmonic: Butterfly | 21 | 47.6 | 0.216 | 0.116 | 52.4 | 0.373 |  |
| 59 | harm_vol_cypher | Harmonic: Cypher (vol swings) | 19 | 47.4 | 0.184 | 0.084 | 47.4 | 0.184 |  |
| 60 | harm_vol_butterfly | Harmonic: Butterfly (vol swings) | 14 | 35.7 | -0.043 | -0.143 | 35.7 | 0.013 |  |
| 61 | harm_vol_bat | Harmonic: Bat (vol swings) | 6 | 33.3 | -0.167 | -0.267 | 50.0 | 0.25 |  |
| 62 | harm_gartley | Harmonic: Gartley | 6 | 33.3 | -0.167 | -0.267 | 33.3 | -0.167 |  |
| 63 | harm_vol_butterfly_tight | Harmonic: Butterfly (vol swings) | 3 | 33.3 | -0.167 | -0.267 | 33.3 | 0.096 |  |
| 64 | rect | Chart patterns (range) | 29 | 27.6 | -0.31 | -0.41 | 27.6 | -0.264 |  |
| 65 | harm_vol_crab | Harmonic: Crab (vol swings) | 2 | 0.0 | -0.33 | -0.43 | 50.0 | 0.25 |  |
| 66 | harm_bat | Harmonic: Bat | 6 | 16.7 | -0.583 | -0.683 | 50.0 | 0.25 |  |
| 67 | harm_gartley_tight | Harmonic: Gartley | 1 | 0.0 | -1.0 | -1.1 | 100.0 | 1.5 |  |
| 68 | harm_vol_gartley_tight | Harmonic: Gartley (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 100.0 | 1.5 |  |

## Stop study: where should the stop sit? (same entries, target fixed at 2.25 ATR, results in ATR, cost 0.15 ATR)

| group | stop | n | target hit % | stopped % | avg ATR | net ATR | mirror avg ATR | t (net vs 0) |
|---|---|---|---|---|---|---|---|---|
| all | 1.0 ATR | 64358 | 30.1 | 67.4 | 0.015 | -0.135 | 0.048 | -23.03 |
| all | 1.5 ATR | 64358 | 37.6 | 57.6 | -0.005 | -0.155 | 0.015 | -21.91 |
| all | 2.0 ATR | 64358 | 43.1 | 49.5 | -0.014 | -0.164 | -0.005 | -20.22 |
| all | 2.5 ATR | 64358 | 46.9 | 42.7 | -0.026 | -0.176 | -0.017 | -19.72 |
| all | 3.0 ATR | 64358 | 49.8 | 37.3 | -0.033 | -0.183 | -0.019 | -18.95 |
| 1m | 1.0 ATR | 11853 | 31.3 | 67.2 | 0.038 | -0.112 | 0.207 | -8.13 |
| 1m | 1.5 ATR | 11853 | 37.7 | 59.6 | -0.041 | -0.191 | 0.135 | -11.53 |
| 1m | 2.0 ATR | 11853 | 42.3 | 53.1 | -0.108 | -0.258 | 0.093 | -13.55 |
| 1m | 2.5 ATR | 11853 | 45.8 | 47.3 | -0.164 | -0.314 | 0.062 | -14.82 |
| 1m | 3.0 ATR | 11853 | 49.6 | 41.6 | -0.161 | -0.311 | 0.063 | -13.46 |
| 15m | 1.0 ATR | 17799 | 30.0 | 67.9 | 0.006 | -0.144 | 0.035 | -12.88 |
| 15m | 1.5 ATR | 17799 | 37.6 | 58.5 | -0.02 | -0.17 | -0.008 | -12.63 |
| 15m | 2.0 ATR | 17799 | 44.1 | 50.1 | -0.005 | -0.155 | -0.011 | -9.98 |
| 15m | 2.5 ATR | 17799 | 48.3 | 43.7 | -0.016 | -0.166 | -0.019 | -9.64 |
| 15m | 3.0 ATR | 17799 | 51.3 | 39.2 | -0.045 | -0.195 | -0.054 | -10.44 |
| 1h | 1.0 ATR | 17585 | 30.5 | 66.8 | 0.029 | -0.121 | 0.018 | -10.75 |
| 1h | 1.5 ATR | 17585 | 38.1 | 57.1 | 0.009 | -0.141 | 0.014 | -10.37 |
| 1h | 2.0 ATR | 17585 | 43.5 | 49.3 | -0.006 | -0.156 | -0.013 | -10.08 |
| 1h | 2.5 ATR | 17585 | 47.7 | 43.1 | -0.013 | -0.163 | -0.016 | -9.48 |
| 1h | 3.0 ATR | 17585 | 50.9 | 37.8 | -0.018 | -0.168 | 0.002 | -9.05 |
| 4h | 1.0 ATR | 13457 | 28.8 | 68.7 | -0.026 | -0.176 | -0.034 | -13.91 |
| 4h | 1.5 ATR | 13457 | 37.4 | 57.0 | 0.003 | -0.147 | -0.048 | -9.52 |
| 4h | 2.0 ATR | 13457 | 43.1 | 47.9 | 0.024 | -0.126 | -0.062 | -7.18 |
| 4h | 2.5 ATR | 13457 | 46.5 | 39.6 | 0.036 | -0.114 | -0.059 | -5.95 |
| 4h | 3.0 ATR | 13457 | 48.7 | 32.6 | 0.057 | -0.093 | -0.044 | -4.56 |
| 1d | 1.0 ATR | 3664 | 30.2 | 64.1 | 0.067 | -0.083 | 0.037 | -3.40 |
| 1d | 1.5 ATR | 3664 | 36.2 | 50.9 | 0.087 | -0.063 | -0.016 | -2.20 |
| 1d | 2.0 ATR | 3664 | 39.6 | 42.2 | 0.074 | -0.076 | -0.052 | -2.35 |
| 1d | 2.5 ATR | 3664 | 41.3 | 32.8 | 0.076 | -0.074 | -0.105 | -2.14 |
| 1d | 3.0 ATR | 3664 | 42.3 | 27.9 | 0.037 | -0.113 | -0.124 | -3.06 |

| group | question | n | value |
|---|---|---|---|
| all | stopped at 1.5 ATR, target reached later | 46853 | 30.6 % reached it later (mirror direction 31.0 %); 72.8 % of all trades were stopped |
| all | MAE of trades that reached the target (ATR) | 39067 | p50 1.01 · p75 2.29 · p90 4.42 |
| 1m | stopped at 1.5 ATR, target reached later | 9175 | 29.9 % reached it later (mirror direction 33.9 %); 77.4 % of all trades were stopped |
| 1m | MAE of trades that reached the target (ATR) | 7344 | p50 0.97 · p75 2.6 · p90 4.96 |
| 15m | stopped at 1.5 ATR, target reached later | 13507 | 35.5 % reached it later (mirror direction 34.6 %); 75.9 % of all trades were stopped |
| 15m | MAE of trades that reached the target (ATR) | 11618 | p50 1.16 · p75 2.6 · p90 5.2 |
| 1h | stopped at 1.5 ATR, target reached later | 13105 | 33.6 % reached it later (mirror direction 33.8 %); 74.5 % of all trades were stopped |
| 1h | MAE of trades that reached the target (ATR) | 11211 | p50 1.08 · p75 2.52 · p90 4.55 |
| 4h | stopped at 1.5 ATR, target reached later | 9058 | 23.6 % reached it later (mirror direction 23.7 %); 67.3 % of all trades were stopped |
| 4h | MAE of trades that reached the target (ATR) | 7288 | p50 0.92 · p75 1.78 · p90 3.03 |
| 1d | stopped at 1.5 ATR, target reached later | 2008 | 12.8 % reached it later (mirror direction 11.0 %); 54.8 % of all trades were stopped |
| 1d | MAE of trades that reached the target (ATR) | 1606 | p50 0.7 · p75 1.14 · p90 1.96 |

Reading: a stop that is never reached only helps if the AVERAGE (net ATR) goes up, not just the target-hit share; compare with the mirror column (the opposite direction on the same bars).


## Pre-registered tests (signals after the freeze date only; docs/PREREG_2026-11-01.md)

| hypothesis | n | win % | avg R | net avg R | t vs random | net 1st half (n) | net 2nd half (n) | PASS |
|---|---|---|---|---|---|---|---|---|
| H1 sess_amd + loc | 100 | 42.0 | 0.081 | -0.019 | -0.26 | -0.331 (50) | 0.293 (50) |  |
| H2 ohl_open + Late 20-24 | 338 | 37.6 | -0.035 | -0.135 | -1.61 | -0.24 (169) | -0.031 (169) |  |

Gate: n >= 100, t > 3.0, net > 0 overall and in both time halves. Under n = 100 it is not evidence, whatever the numbers say.


## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Harmonic: Cypher | 20 | 0.658 |
| 2 | Harmonic: Gartley (vol swings) | 9 | 0.388 |
| 3 | Harmonic: Cypher (vol swings) | 23 | 0.304 |
| 4 | Harmonic: Butterfly | 24 | 0.272 |
| 5 | Harmonic: Crab | 2 | 0.25 |
| 6 | Wyckoff | 181 | 0.128 |
| 7 | Trend (hedge fund) | 2862 | 0.05 |
| 8 | Fibonacci | 3141 | 0.043 |
| 9 | Elliott wave | 4016 | 0.012 |
| 10 | Momentum / divergence | 2608 | 0.005 |
| 11 | SMC / ICT | 9172 | -0.0 |
| 12 | Time (sessions) | 3305 | -0.002 |
| 13 | Levels / breakouts | 12253 | -0.003 |
| 14 | Trend (MA) | 15098 | -0.016 |
| 15 | Liquidity | 8207 | -0.016 |
| 16 | Price action | 953 | -0.037 |
| 17 | Chart patterns (range) | 688 | -0.042 |
| 18 | Harmonic: Bat (vol swings) | 8 | -0.063 |
| 19 | Harmonic: Butterfly (vol swings) | 17 | -0.065 |
| 20 | Intermarket (SMT) | 1753 | -0.069 |
| 21 | Harmonic: Crab (vol swings) | 3 | -0.107 |
| 22 | Harmonic: Gartley | 7 | -0.286 |
| 23 | Harmonic: Bat | 8 | -0.375 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| abc | 15m | 35 | 22.9 | -0.379 | -0.479 |
| breaker | 4h | 107 | 42.1 | 0.195 | 0.095 |
| breakout | 1d | 54 | 53.7 | 0.403 | 0.303 |
| cisd | 1h | 255 | 38.4 | 0.071 | -0.029 |
| crt | 1m | 74 | 41.9 | 0.095 | -0.005 |
| dbl | 1d | 39 | 48.7 | 0.396 | 0.296 |
| donch | 1d | 157 | 38.2 | 0.104 | 0.004 |
| ema_stack | 1d | 293 | 37.5 | 0.081 | -0.019 |
| ew3 | 1d | 68 | 42.6 | 0.107 | 0.007 |
| ew5 | 1h | 32 | 40.6 | 0.063 | -0.037 |
| ew_r2_d1 | 1h | 173 | 52.0 | 0.364 | 0.264 |
| ew_r2_d2 | 1h | 64 | 57.8 | 0.46 | 0.36 |
| ew_r2_v | 1m | 104 | 41.3 | 0.104 | 0.004 |
| ew_r3_d1 | 1d | 35 | 37.1 | 0.203 | 0.103 |
| ew_r3_d2 | 4h | 54 | 48.1 | 0.225 | 0.125 |
| ew_r3_v | 1d | 31 | 41.9 | 0.234 | 0.134 |
| fib | 15m | 638 | 42.0 | 0.082 | -0.018 |
| fvg | 1d | 128 | 41.4 | 0.21 | 0.11 |
| judas | 1h | 602 | 38.0 | 0.008 | -0.092 |
| level | 1d | 88 | 40.9 | 0.072 | -0.028 |
| liqline | 1d | 124 | 43.5 | 0.263 | 0.163 |
| m2022 | 1d | 82 | 46.3 | 0.322 | 0.222 |
| ma_cross | 1d | 128 | 39.1 | 0.187 | 0.087 |
| macd_div | 1d | 71 | 46.5 | 0.325 | 0.225 |
| msb_ob | 1m | 390 | 44.4 | 0.15 | 0.05 |
| ob | 1m | 301 | 46.8 | 0.195 | 0.095 |
| ohl_break | 1d | 37 | 40.5 | 0.142 | 0.042 |
| ohl_open | 1d | 164 | 37.2 | 0.119 | 0.019 |
| orb | 15m | 175 | 44.6 | 0.17 | 0.07 |
| ote | 4h | 173 | 45.7 | 0.196 | 0.096 |
| pa_engulf | 15m | 91 | 36.3 | -0.003 | -0.103 |
| pa_inside | 1h | 76 | 42.1 | 0.09 | -0.01 |
| pa_pin | 1h | 90 | 41.1 | 0.12 | 0.02 |
| po3 | 1h | 67 | 43.3 | 0.11 | 0.01 |
| rsi_div | 1h | 332 | 38.9 | 0.03 | -0.07 |
| sess_amd | 1m | 59 | 54.2 | 0.371 | 0.271 |
| sma1040 | 1d | 58 | 53.4 | 0.486 | 0.386 |
| smt | 15m | 491 | 37.1 | -0.031 | -0.131 |
| sweep | 4h | 829 | 37.9 | 0.031 | -0.069 |
| tlbreak | 1d | 157 | 42.0 | 0.18 | 0.08 |
| turtle55 | 1d | 82 | 45.1 | 0.282 | 0.182 |
| unicorn | 1m | 65 | 49.2 | 0.244 | 0.144 |
| vwap | 1d | 423 | 36.2 | 0.041 | -0.059 |
| wavec | 1h | 38 | 44.7 | 0.141 | 0.041 |
| wyck | 4h | 49 | 55.1 | 0.425 | 0.325 |
| zombie | 1d | 55 | 41.8 | 0.202 | 0.102 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 68 | -0.097 | 46 | 0.081 |
| breaker | 207 | -0.128 | 194 | 0.072 |
| breakout | 485 | -0.057 | 537 | 0.187 |
| cisd | 501 | -0.127 | 469 | 0.015 |
| crt | 505 | -0.114 | 467 | -0.018 |
| dbl | 336 | -0.112 | 323 | 0.055 |
| donch | 1164 | -0.057 | 1558 | 0.103 |
| ema_stack | 2198 | -0.118 | 2710 | 0.06 |
| ew3 | 508 | -0.158 | 495 | 0.049 |
| ew5 | 72 | -0.173 | 111 | 0.057 |
| ew_r2_d1 | 244 | -0.1 | 345 | 0.166 |
| ew_r2_d2 | 103 | 0.08 | 183 | 0.115 |
| ew_r2_v | 418 | 0.0 | 504 | -0.009 |
| ew_r3_d1 | 94 | -0.087 | 146 | 0.106 |
| ew_r3_d2 | 44 | 0.239 | 113 | 0.101 |
| ew_r3_v | 163 | -0.096 | 207 | 0.1 |
| fib | 1127 | -0.032 | 1212 | 0.084 |
| fvg | 1684 | -0.073 | 1444 | 0.103 |
| harm_bat | 6 | -0.583 | 0 | None |
| harm_bat_tight | 2 | 0.25 | 0 | None |
| harm_butterfly | 12 | -0.122 | 9 | 0.667 |
| harm_butterfly_tight | 2 | 0.25 | 1 | 1.5 |
| harm_crab | 2 | 0.25 | 0 | None |
| harm_cypher | 6 | -0.056 | 10 | 0.75 |
| harm_cypher_tight | 0 | None | 4 | 1.5 |
| harm_gartley | 4 | -0.375 | 2 | 0.25 |
| harm_gartley_tight | 1 | -1.0 | 0 | None |
| harm_vol_bat | 4 | -0.375 | 2 | 0.25 |
| harm_vol_bat_tight | 2 | 0.25 | 0 | None |
| harm_vol_butterfly | 14 | -0.043 | 0 | None |
| harm_vol_butterfly_tight | 3 | -0.167 | 0 | None |
| harm_vol_crab | 1 | -1.0 | 1 | 0.339 |
| harm_vol_crab_tight | 0 | None | 1 | 0.339 |
| harm_vol_cypher | 8 | -0.688 | 11 | 0.818 |
| harm_vol_cypher_tight | 1 | -1.0 | 3 | 1.5 |
| harm_vol_gartley | 6 | 0.25 | 2 | 1.5 |
| harm_vol_gartley_tight | 1 | -1.0 | 0 | None |
| judas | 1297 | -0.064 | 1151 | 0.035 |
| kzs | 19 | -0.243 | 12 | 0.042 |
| level | 3309 | -0.069 | 1721 | 0.066 |
| liqline | 1227 | -0.023 | 1455 | 0.061 |
| m2022 | 338 | -0.089 | 336 | 0.144 |
| ma_cross | 1466 | -0.049 | 1383 | 0.015 |
| macd_div | 789 | 0.029 | 625 | -0.025 |
| msb_ob | 1007 | -0.075 | 887 | 0.118 |
| ob | 818 | -0.138 | 837 | 0.095 |
| ohl_break | 398 | -0.043 | 494 | 0.129 |
| ohl_open | 1509 | -0.113 | 1576 | 0.092 |
| orb | 84 | 0.21 | 98 | 0.205 |
| ote | 408 | 0.013 | 394 | 0.158 |
| pa_engulf | 152 | -0.127 | 151 | -0.048 |
| pa_inside | 163 | -0.038 | 163 | 0.031 |
| pa_pin | 164 | 0.07 | 117 | -0.14 |
| pa_star | 19 | -0.43 | 24 | 0.219 |
| po3 | 66 | 0.045 | 66 | 0.079 |
| rect | 10 | 0.0 | 19 | -0.474 |
| rsi_div | 632 | -0.046 | 562 | 0.063 |
| sess_amd | 243 | -0.053 | 269 | 0.03 |
| sma1040 | 29 | 0.714 | 29 | 0.259 |
| smt | 924 | -0.113 | 829 | -0.02 |
| sweep | 2025 | -0.054 | 1612 | 0.04 |
| tlbreak | 1072 | -0.102 | 1152 | 0.08 |
| turtle55 | 40 | 0.068 | 42 | 0.485 |
| unicorn | 228 | -0.131 | 222 | 0.26 |
| vwap | 3392 | -0.106 | 3949 | 0.066 |
| wavec | 82 | -0.057 | 70 | 0.398 |
| wyck | 89 | 0.176 | 92 | 0.082 |
| zombie | 456 | -0.097 | 460 | -0.086 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 37781 | 37.5 | -0.008 | 26284 | 37.8 | 0.004 |
| abc | 32 | 31.2 | -0.121 | 82 | 36.6 | 0.012 |
| breaker | 189 | 29.6 | -0.179 | 212 | 39.6 | 0.1 |
| breakout | 716 | 42.3 | 0.085 | 304 | 40.1 | 0.038 |
| cisd | 368 | 30.7 | -0.165 | 596 | 36.7 | 0.013 |
| crt | 372 | 32.3 | -0.12 | 598 | 36.5 | -0.036 |
| dbl | 426 | 36.9 | -0.05 | 233 | 37.8 | 0.006 |
| donch | 2377 | 39.7 | 0.045 | 337 | 36.8 | -0.033 |
| ema_stack | 3978 | 37.9 | 0.002 | 905 | 33.7 | -0.109 |
| ew3 | 577 | 37.3 | -0.03 | 422 | 34.6 | -0.088 |
| ew5 | 139 | 39.6 | 0.085 | 44 | 22.7 | -0.408 |
| ew_r2_d1 | 353 | 39.1 | 0.068 | 236 | 38.1 | 0.038 |
| ew_r2_d2 | 156 | 39.1 | 0.057 | 130 | 40.8 | 0.158 |
| ew_r2_v | 535 | 35.3 | -0.033 | 385 | 37.9 | 0.04 |
| ew_r3_d1 | 200 | 39.0 | 0.052 | 40 | 32.5 | -0.076 |
| ew_r3_d2 | 127 | 39.4 | 0.121 | 30 | 46.7 | 0.218 |
| ew_r3_v | 314 | 39.5 | 0.062 | 56 | 26.8 | -0.258 |
| fib | 1158 | 38.5 | 0.015 | 1175 | 39.7 | 0.042 |
| fvg | 1764 | 37.0 | -0.005 | 1335 | 39.0 | 0.036 |
| harm_bat | 2 | 0.0 | -1.0 | 4 | 25.0 | -0.375 |
| harm_bat_tight | 1 | 0.0 | -1.0 | 1 | 100.0 | 1.5 |
| harm_butterfly | 7 | 71.4 | 0.786 | 14 | 35.7 | -0.069 |
| harm_butterfly_tight | 0 | None | None | 3 | 66.7 | 0.667 |
| harm_crab | 0 | None | None | 2 | 50.0 | 0.25 |
| harm_cypher | 9 | 44.4 | 0.185 | 7 | 71.4 | 0.786 |
| harm_cypher_tight | 2 | 100.0 | 1.5 | 2 | 100.0 | 1.5 |
| harm_gartley | 2 | 0.0 | -1.0 | 4 | 50.0 | 0.25 |
| harm_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| harm_vol_bat | 2 | 0.0 | -1.0 | 4 | 50.0 | 0.25 |
| harm_vol_bat_tight | 1 | 0.0 | -1.0 | 1 | 100.0 | 1.5 |
| harm_vol_butterfly | 2 | 50.0 | 0.25 | 12 | 33.3 | -0.092 |
| harm_vol_butterfly_tight | 0 | None | None | 3 | 33.3 | -0.167 |
| harm_vol_crab | 0 | None | None | 2 | 0.0 | -0.33 |
| harm_vol_crab_tight | 0 | None | None | 1 | 0.0 | 0.339 |
| harm_vol_cypher | 12 | 41.7 | 0.042 | 7 | 57.1 | 0.429 |
| harm_vol_cypher_tight | 4 | 75.0 | 0.875 | 0 | None | None |
| harm_vol_gartley | 2 | 0.0 | -1.0 | 6 | 83.3 | 1.083 |
| harm_vol_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| judas | 1585 | 37.9 | -0.02 | 850 | 38.0 | -0.013 |
| kzs | 12 | 25.0 | -0.375 | 19 | 36.8 | 0.02 |
| level | 2497 | 36.4 | -0.045 | 2492 | 37.6 | 0.001 |
| liqline | 1556 | 39.1 | 0.021 | 1113 | 38.6 | 0.025 |
| m2022 | 390 | 39.2 | 0.033 | 282 | 38.7 | 0.016 |
| ma_cross | 1715 | 36.4 | -0.033 | 1114 | 37.9 | 0.01 |
| macd_div | 282 | 37.9 | 0.015 | 1125 | 37.2 | -0.002 |
| msb_ob | 930 | 36.9 | -0.005 | 949 | 39.6 | 0.041 |
| ob | 876 | 36.2 | -0.045 | 762 | 37.5 | 0.003 |
| ohl_break | 532 | 41.5 | 0.07 | 355 | 38.6 | 0.019 |
| ohl_open | 1644 | 37.3 | -0.007 | 1433 | 37.5 | -0.007 |
| orb | 105 | 49.5 | 0.271 | 77 | 41.6 | 0.12 |
| ote | 332 | 42.2 | 0.103 | 467 | 41.5 | 0.078 |
| pa_engulf | 147 | 27.2 | -0.275 | 156 | 41.0 | 0.089 |
| pa_inside | 197 | 35.5 | -0.056 | 126 | 42.9 | 0.103 |
| pa_pin | 114 | 34.2 | -0.088 | 165 | 39.4 | 0.043 |
| pa_star | 14 | 28.6 | -0.286 | 29 | 37.9 | 0.038 |
| po3 | 61 | 44.3 | 0.126 | 70 | 37.1 | -0.015 |
| rect | 16 | 25.0 | -0.375 | 13 | 30.8 | -0.231 |
| rsi_div | 316 | 41.1 | 0.099 | 871 | 35.7 | -0.037 |
| sess_amd | 233 | 39.1 | 0.001 | 273 | 36.6 | -0.051 |
| sma1040 | 25 | 48.0 | 0.256 | 33 | 57.6 | 0.661 |
| smt | 881 | 34.7 | -0.094 | 871 | 36.3 | -0.046 |
| sweep | 1601 | 35.2 | -0.061 | 2025 | 38.5 | 0.029 |
| tlbreak | 1096 | 36.7 | -0.039 | 1123 | 38.5 | 0.023 |
| turtle55 | 59 | 40.7 | 0.176 | 23 | 56.5 | 0.551 |
| unicorn | 230 | 39.1 | 0.038 | 217 | 38.2 | 0.068 |
| vwap | 5887 | 37.9 | 0.001 | 1431 | 35.0 | -0.074 |
| wavec | 42 | 45.2 | 0.312 | 109 | 42.2 | 0.079 |
| wyck | 82 | 31.7 | -0.154 | 99 | 50.5 | 0.362 |
| zombie | 495 | 32.7 | -0.118 | 419 | 35.6 | -0.055 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 7664 | 31.4 | -0.041 |
| Mon | 7652 | 40.1 | 0.029 |
| Sat | 11108 | 37.9 | -0.006 |
| Sun | 14933 | 37.0 | -0.035 |
| Thu | 7627 | 38.7 | 0.031 |
| Tue | 7633 | 37.7 | -0.033 |
| Wed | 7741 | 41.1 | 0.061 |
| Asia 00-07 | 18974 | 37.6 | -0.019 |
| Late 20-24 | 13120 | 38.0 | -0.0 |
| London 07-12 | 9573 | 38.1 | -0.014 |
| New York 12-20 | 19027 | 37.4 | 0.004 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 64358 | 37.6 | -0.003 | 0.029 | -5.24 | 27926 | -0.014 | 36432 | 0.005 |  |
| grade A+++ | 490 | 46.9 | 0.241 | 0.079 | +2.33 | 226 | 0.212 | 264 | 0.266 |  |
| grade A+ | 8464 | 36.4 | -0.02 | 0.04 | -3.53 | 3581 | -0.053 | 4883 | 0.004 |  |
| grade A | 19226 | 37.2 | 0.001 | 0.023 | -1.89 | 8172 | -0.032 | 11054 | 0.026 |  |
| grade B | 23270 | 38.2 | 0.008 | 0.043 | -3.45 | 10264 | -0.007 | 13006 | 0.02 |  |
| grade C | 12908 | 37.7 | -0.03 | 0.002 | -2.35 | 5683 | 0.012 | 7225 | -0.063 |  |
| layer htf | 37781 | 37.5 | -0.008 | 0.029 | -4.55 | 16278 | -0.041 | 21503 | 0.017 |  |
| layer loc | 14223 | 38.3 | 0.017 | 0.011 | +0.50 | 6188 | 0.038 | 8035 | 0.001 |  |
| layer vol | 20913 | 38.4 | 0.009 | 0.046 | -3.39 | 9034 | -0.021 | 11879 | 0.032 |  |
| layer reg | 46387 | 37.0 | -0.001 | 0.026 | -3.82 | 20059 | -0.012 | 26328 | 0.007 |  |
| layer time | 32264 | 37.5 | 0.005 | 0.042 | -4.34 | 13708 | -0.026 | 18556 | 0.027 |  |
| no htf | 26577 | 37.8 | 0.004 | 0.029 | -2.71 | 11648 | 0.023 | 14929 | -0.012 |  |
| no loc | 50135 | 37.4 | -0.009 | 0.034 | -6.21 | 21738 | -0.029 | 28397 | 0.006 |  |
| no vol | 43445 | 37.2 | -0.009 | 0.02 | -4.02 | 18892 | -0.011 | 24553 | -0.008 |  |
| no reg | 17971 | 39.1 | -0.009 | 0.036 | -3.76 | 7867 | -0.021 | 10104 | 0.001 |  |
| no time | 32094 | 37.8 | -0.011 | 0.015 | -3.07 | 14218 | -0.003 | 17876 | -0.018 |  |
| no loc / sma1040 | 56 | 55.4 | 0.54 | -0.127 | +3.08 | 14 | 0.786 | 42 | 0.457 |  |
| grade A+ / ew_r2_d2 | 46 | 52.2 | 0.414 | 0.292 | +0.52 | 17 | 0.176 | 29 | 0.553 |  |
| grade A+ / orb | 58 | 55.2 | 0.409 | 0.147 | +1.23 | 22 | 0.818 | 36 | 0.159 |  |
| loc / ew_r3_d2 | 33 | 51.5 | 0.358 | 0.055 | +1.44 | 17 | -0.067 | 16 | 0.81 |  |
| grade A / turtle55 | 44 | 47.7 | 0.355 | 0.371 | -0.07 | 17 | 0.351 | 27 | 0.357 |  |
| grade B / wavec | 60 | 51.7 | 0.31 | -0.167 | +2.36 | 17 | 0.324 | 43 | 0.305 |  |
| grade A+++ / ob | 40 | 50.0 | 0.282 | 0.136 | +0.69 | 15 | 0.333 | 25 | 0.25 |  |
| no loc / turtle55 | 82 | 45.1 | 0.282 | 0.229 | +0.31 | 30 | 0.131 | 52 | 0.369 |  |
| loc / abc | 54 | 44.4 | 0.245 | 0.171 | +0.33 | 17 | 0.176 | 37 | 0.277 |  |
| loc / unicorn | 115 | 46.1 | 0.235 | 0.196 | +0.27 | 51 | 0.099 | 64 | 0.344 |  |
| grade C / breakout | 95 | 48.4 | 0.234 | 0.023 | +1.38 | 41 | 0.743 | 54 | -0.153 |  |
| grade B / wyck | 57 | 47.4 | 0.232 | 0.275 | -0.22 | 27 | 0.026 | 30 | 0.417 |  |
| grade C / ote | 157 | 48.4 | 0.231 | 0.109 | +0.95 | 78 | 0.177 | 79 | 0.284 |  |
| grade A+ / ew_r3_d1 | 39 | 46.2 | 0.227 | 0.151 | +0.33 | 9 | 0.163 | 30 | 0.246 |  |
| no loc / wavec | 96 | 45.8 | 0.226 | -0.064 | +1.75 | 38 | 0.401 | 58 | 0.111 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8307 | 4130 | 49.7 |
| sweep | vwap | 6421 | 3918 | 61.0 |
| ema_stack | sweep | 3296 | 2450 | 74.3 |
| ema_stack | level | 4031 | 2220 | 55.1 |
| fvg | vwap | 4480 | 1820 | 40.6 |
| ohl_open | vwap | 3975 | 1753 | 44.1 |
| macd_div | vwap | 2108 | 1679 | 79.6 |
| msb_ob | vwap | 2777 | 1604 | 57.8 |
| level | sweep | 3757 | 1586 | 42.2 |
| fib | vwap | 3008 | 1501 | 49.9 |
| ob | vwap | 2632 | 1428 | 54.3 |
| rsi_div | vwap | 1804 | 1421 | 78.8 |
| fvg | level | 3188 | 1376 | 43.2 |
| level | ma_cross | 2669 | 1350 | 50.6 |
| ma_cross | sweep | 2064 | 1335 | 64.7 |
| ma_cross | vwap | 4253 | 1277 | 30.0 |
| smt | vwap | 2834 | 1272 | 44.9 |
| judas | level | 2643 | 1230 | 46.5 |
| tlbreak | vwap | 2587 | 1217 | 47.0 |
| liqline | vwap | 3529 | 1189 | 33.7 |
| level | ohl_open | 2324 | 1175 | 50.6 |
| judas | vwap | 3976 | 1094 | 27.5 |
| judas | sweep | 1742 | 1053 | 60.4 |
| level | liqline | 1904 | 1019 | 53.5 |
| fvg | ohl_open | 1231 | 1005 | 81.6 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 29 | 55.2 | 0.498 |
| 2 families | 420 | 38.1 | 0.037 |
| 2 families (with opposition) | 1352 | 38.3 | 0.016 |
| 3 families | 1156 | 39.4 | 0.044 |
| 3 families (with opposition) | 4616 | 37.7 | -0.007 |
| 4+ families | 937 | 35.4 | -0.047 |
| 4+ families (with opposition) | 4268 | 36.1 | -0.041 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 84.3 | 29110 | 83.8 | 401949 | +2.3 |
| 1m shapes 120/180/240/360 deg | 81.9 | 12269 | 81.7 | 12388 | +0.5 |
| 15m | 65.1 | 20158 | 65.2 | 278789 | -0.0 |
| 15m shapes 120/180/240/360 deg | 63.5 | 10481 | 63.8 | 10388 | -0.7 |
| 1h | 58.1 | 16091 | 57.8 | 222864 | +0.6 |
| 1h shapes 120/180/240/360 deg | 56.7 | 8816 | 56.5 | 8785 | +0.2 |
| 4h | 56.5 | 12022 | 57.6 | 165929 | -2.6 |
| 4h shapes 120/180/240/360 deg | 56.7 | 6770 | 57.0 | 6771 | -0.4 |
| 1d | 55.4 | 3187 | 56.1 | 42716 | -0.7 |
| 1d shapes 120/180/240/360 deg | 57.3 | 2028 | 57.4 | 2031 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 92 | 27.2 | +0.369 | +0.657 | -1.02 |
| 1d | 57 | 43.9 | +0.113 | +0.501 | -1.33 |
| 1h | 112 | 19.6 | -0.197 | -0.208 | +0.05 |
| 4h | 94 | 29.8 | +0.114 | -0.192 | +1.39 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2389 | -0.107 |
| 15 days around full moon | 2325 | 0.034 |

Difference t = -1.75 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 64358 | 48.9 | -0.02 | -0.12 | -1294.0 | -5.16 |
| rr1.5 | 64358 | 40.5 | -0.003 | -0.103 | -216.2 | -0.71 |
| rr2.0 | 64358 | 35.3 | 0.007 | -0.093 | 478.6 | +1.38 |
| rr3.0 | 64358 | 29.8 | 0.024 | -0.076 | 1526.3 | +3.69 |
| rr1.5_be | 64358 | 34.7 | 0.0 | -0.1 | 29.4 | +0.10 |
| rr2.0_be | 64358 | 27.5 | 0.011 | -0.089 | 710.3 | +2.28 |
| rr1.5_h16 | 64358 | 42.1 | 0.003 | -0.097 | 185.8 | +0.65 |
| rr2.0_h16 | 64358 | 39.0 | 0.013 | -0.087 | 867.0 | +2.74 |
| pt_1.5_3 | 64358 | 48.9 | 0.031 | -0.069 | 2016.5 | +6.82 |
| pt_1.0_3 | 64358 | 48.9 | 0.019 | -0.081 | 1218.4 | +4.41 |
| pt_1.5_5 | 64358 | 48.9 | 0.047 | -0.053 | 3049.3 | +9.95 |
| trail_only | 64358 | 48.9 | 0.09 | -0.01 | 5797.4 | +16.35 |

## Exit variant x timeframe x trend (is the htf sign flip caused by the exit? docs/PREREG_2026-11-01.md)

Same entries, every detector pooled. If 'with' stays below 'against' on 1h / 1m under every exit, the exit is not the cause.

| tf | exit | with n | with avg R | with t | against n | against avg R | against t |
|---|---|---|---|---|---|---|---|
| 15m | rr1.0 | 10402 | 0.002 | +0.24 | 7338 | -0.056 | -4.83 |
| 15m | rr1.5 | 10402 | 0.001 | +0.10 | 7338 | -0.032 | -2.33 |
| 15m | rr2.0 | 10402 | 0.026 | +1.87 | 7338 | -0.016 | -1.01 |
| 15m | rr3.0 | 10402 | 0.058 | +3.50 | 7338 | 0.015 | +0.77 |
| 15m | rr1.5_be | 10402 | 0.017 | +1.57 | 7338 | -0.039 | -2.99 |
| 15m | rr2.0_be | 10402 | 0.034 | +2.83 | 7338 | -0.03 | -2.11 |
| 15m | rr1.5_h16 | 10402 | -0.003 | -0.25 | 7338 | -0.035 | -2.69 |
| 15m | rr2.0_h16 | 10402 | 0.019 | +1.51 | 7338 | -0.028 | -1.93 |
| 15m | pt_1.5_3 | 10402 | 0.056 | +4.85 | 7338 | -0.006 | -0.48 |
| 15m | pt_1.0_3 | 10402 | 0.045 | +4.15 | 7338 | -0.018 | -1.45 |
| 15m | pt_1.5_5 | 10402 | 0.079 | +6.55 | 7338 | 0.008 | +0.56 |
| 15m | trail_only | 10402 | 0.134 | +9.36 | 7338 | 0.048 | +2.96 |
| 1d | rr1.0 | 2160 | -0.085 | -4.05 | 1504 | 0.155 | +6.27 |
| 1d | rr1.5 | 2160 | -0.081 | -3.31 | 1504 | 0.256 | +8.44 |
| 1d | rr2.0 | 2160 | -0.09 | -3.37 | 1504 | 0.344 | +9.87 |
| 1d | rr3.0 | 2160 | -0.022 | -0.69 | 1504 | 0.426 | +10.33 |
| 1d | rr1.5_be | 2160 | -0.071 | -3.05 | 1504 | 0.188 | +6.61 |
| 1d | rr2.0_be | 2160 | -0.094 | -3.80 | 1504 | 0.262 | +8.13 |
| 1d | rr1.5_h16 | 2160 | -0.063 | -2.64 | 1504 | 0.221 | +7.45 |
| 1d | rr2.0_h16 | 2160 | -0.059 | -2.23 | 1504 | 0.299 | +8.89 |
| 1d | pt_1.5_3 | 2160 | -0.063 | -2.63 | 1504 | 0.233 | +7.76 |
| 1d | pt_1.0_3 | 2160 | -0.065 | -2.88 | 1504 | 0.214 | +7.70 |
| 1d | pt_1.5_5 | 2160 | -0.065 | -2.70 | 1504 | 0.26 | +8.23 |
| 1d | trail_only | 2160 | -0.049 | -1.86 | 1504 | 0.325 | +8.72 |
| 1h | rr1.0 | 10150 | -0.039 | -3.96 | 7406 | 0.018 | +1.61 |
| 1h | rr1.5 | 10150 | -0.027 | -2.25 | 7406 | 0.049 | +3.46 |
| 1h | rr2.0 | 10150 | -0.015 | -1.08 | 7406 | 0.04 | +2.51 |
| 1h | rr3.0 | 10150 | -0.011 | -0.68 | 7406 | 0.01 | +0.50 |
| 1h | rr1.5_be | 10150 | -0.017 | -1.51 | 7406 | 0.039 | +3.03 |
| 1h | rr2.0_be | 10150 | 0.004 | +0.31 | 7406 | 0.041 | +2.88 |
| 1h | rr1.5_h16 | 10150 | -0.006 | -0.57 | 7406 | 0.041 | +3.18 |
| 1h | rr2.0_h16 | 10150 | 0.011 | +0.91 | 7406 | 0.033 | +2.26 |
| 1h | pt_1.5_3 | 10150 | 0.013 | +1.12 | 7406 | 0.059 | +4.44 |
| 1h | pt_1.0_3 | 10150 | -0.001 | -0.05 | 7406 | 0.048 | +3.83 |
| 1h | pt_1.5_5 | 10150 | 0.029 | +2.45 | 7406 | 0.062 | +4.57 |
| 1h | trail_only | 10150 | 0.071 | +5.11 | 7406 | 0.082 | +5.43 |
| 1m | rr1.0 | 7132 | -0.077 | -6.60 | 4532 | -0.02 | -1.37 |
| 1m | rr1.5 | 7132 | -0.035 | -2.48 | 4532 | -0.008 | -0.47 |
| 1m | rr2.0 | 7132 | -0.014 | -0.88 | 4532 | 0.028 | +1.33 |
| 1m | rr3.0 | 7132 | -0.012 | -0.62 | 4532 | 0.078 | +3.07 |
| 1m | rr1.5_be | 7132 | -0.026 | -1.92 | 4532 | 0.007 | +0.41 |
| 1m | rr2.0_be | 7132 | -0.001 | -0.06 | 4532 | 0.027 | +1.46 |
| 1m | rr1.5_h16 | 7132 | -0.015 | -1.15 | 4532 | 0.011 | +0.63 |
| 1m | rr2.0_h16 | 7132 | 0.0 | +0.00 | 4532 | 0.054 | +2.82 |
| 1m | pt_1.5_3 | 7132 | 0.021 | +1.44 | 4532 | 0.074 | +4.11 |
| 1m | pt_1.0_3 | 7132 | -0.004 | -0.29 | 4532 | 0.054 | +3.18 |
| 1m | pt_1.5_5 | 7132 | 0.049 | +3.20 | 4532 | 0.113 | +5.82 |
| 1m | trail_only | 7132 | 0.125 | +6.89 | 4532 | 0.205 | +8.63 |
| 4h | rr1.0 | 7937 | 0.021 | +1.90 | 5504 | -0.03 | -2.22 |
| 4h | rr1.5 | 7937 | 0.047 | +3.48 | 5504 | -0.064 | -4.02 |
| 4h | rr2.0 | 7937 | 0.052 | +3.41 | 5504 | -0.101 | -5.76 |
| 4h | rr3.0 | 7937 | 0.091 | +5.12 | 5504 | -0.129 | -6.46 |
| 4h | rr1.5_be | 7937 | 0.033 | +2.64 | 5504 | -0.035 | -2.34 |
| 4h | rr2.0_be | 7937 | 0.033 | +2.39 | 5504 | -0.058 | -3.66 |
| 4h | rr1.5_h16 | 7937 | 0.047 | +3.71 | 5504 | -0.046 | -3.09 |
| 4h | rr2.0_h16 | 7937 | 0.042 | +2.97 | 5504 | -0.064 | -3.93 |
| 4h | pt_1.5_3 | 7937 | 0.054 | +4.22 | 5504 | -0.036 | -2.44 |
| 4h | pt_1.0_3 | 7937 | 0.046 | +3.80 | 5504 | -0.033 | -2.39 |
| 4h | pt_1.5_5 | 7937 | 0.059 | +4.48 | 5504 | -0.028 | -1.85 |
| 4h | trail_only | 7937 | 0.079 | +5.39 | 5504 | -0.021 | -1.24 |
