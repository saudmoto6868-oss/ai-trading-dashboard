# Strategy lab - real candles (2026-11-14)

Symbols: HL:xyz:GOLD, HL:xyz:SILVER, HL:xyz:CL, HL:xyz:BRENTOIL, HL:xyz:EUR, HL:xyz:JPY, HL:xyz:GBP, HL:xyz:SP500, HL:xyz:XYZ100, BTC-USDT, ETH-USDT, SOL-USDT · timeframes: 1m, 15m, 1h, 4h, 1d · stop 1.5 ATR, target 1.5R, break-even win rate 40% · avg R has no costs; the net column takes 0.1R per trade off (planning estimate) · n < 30 = not evidence.

## Every detector on its own (all timeframes)

| rank | key | school | n | win % | avg R | net avg R | random win % | random avg R | edge |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sma1040 | Trend (hedge fund) | 53 | 58.5 | 0.612 | 0.512 | 30.2 | -0.076 | YES |
| 2 | turtle55 | Trend (hedge fund) | 88 | 46.6 | 0.272 | 0.172 | 48.9 | 0.31 |  |
| 3 | ew_r2_d2 | Elliott wave | 294 | 41.8 | 0.135 | 0.035 | 38.8 | 0.066 |  |
| 4 | ew_r3_d2 | Elliott wave | 153 | 38.6 | 0.116 | 0.016 | 34.0 | -0.009 |  |
| 5 | wyck | Wyckoff | 171 | 40.4 | 0.097 | -0.003 | 40.4 | 0.087 |  |
| 6 | pa_inside | Price action | 363 | 39.9 | 0.058 | -0.042 | 39.1 | 0.033 |  |
| 7 | po3 | Time (sessions) | 138 | 39.9 | 0.056 | -0.044 | 42.0 | 0.134 |  |
| 8 | ote | Fibonacci | 799 | 40.1 | 0.054 | -0.046 | 34.9 | -0.063 |  |
| 9 | ohl_break | Levels / breakouts | 809 | 40.7 | 0.048 | -0.052 | 40.0 | 0.038 |  |
| 10 | ew_r2_d1 | Elliott wave | 557 | 38.1 | 0.036 | -0.064 | 35.2 | -0.029 |  |
| 11 | cisd | SMC / ICT | 945 | 38.4 | 0.03 | -0.07 | 38.5 | 0.02 |  |
| 12 | ew_r2_v | Elliott wave | 939 | 37.9 | 0.029 | -0.071 | 39.5 | 0.065 |  |
| 13 | msb_ob | SMC / ICT | 1824 | 38.6 | 0.027 | -0.073 | 37.1 | -0.01 |  |
| 14 | ew_r3_v | Elliott wave | 350 | 37.7 | 0.027 | -0.073 | 35.4 | -0.031 |  |
| 15 | ew_r3_d1 | Elliott wave | 238 | 37.0 | 0.026 | -0.074 | 34.9 | -0.001 |  |
| 16 | fvg | SMC / ICT | 3149 | 38.6 | 0.021 | -0.079 | 38.0 | 0.004 |  |
| 17 | fib | Fibonacci | 2382 | 38.8 | 0.021 | -0.079 | 37.2 | -0.015 |  |
| 18 | breaker | SMC / ICT | 397 | 36.5 | 0.014 | -0.086 | 35.0 | -0.044 |  |
| 19 | breakout | Levels / breakouts | 1093 | 39.1 | 0.006 | -0.094 | 37.0 | -0.038 |  |
| 20 | ma_cross | Trend (MA) | 2832 | 38.0 | 0.003 | -0.097 | 37.6 | -0.001 |  |
| 21 | unicorn | SMC / ICT | 416 | 37.0 | 0.002 | -0.098 | 38.0 | 0.041 |  |
| 22 | macd_div | Momentum / divergence | 1417 | 37.6 | 0.001 | -0.099 | 36.3 | -0.035 |  |
| 23 | orb | Time (sessions) | 178 | 38.2 | -0.001 | -0.101 | 31.5 | -0.14 |  |
| 24 | ohl_open | Levels / breakouts | 3146 | 37.5 | -0.003 | -0.103 | 37.3 | -0.008 |  |
| 25 | ob | SMC / ICT | 1667 | 37.1 | -0.005 | -0.105 | 38.6 | 0.039 |  |
| 26 | sweep | Liquidity | 3631 | 37.3 | -0.005 | -0.105 | 36.4 | -0.03 |  |
| 27 | level | Levels / breakouts | 4992 | 37.7 | -0.006 | -0.106 | 37.4 | -0.018 |  |
| 28 | m2022 | SMC / ICT | 656 | 37.5 | -0.011 | -0.111 | 38.3 | 0.033 |  |
| 29 | pa_star | Price action | 47 | 36.2 | -0.011 | -0.111 | 29.8 | -0.165 |  |
| 30 | judas | Time (sessions) | 2295 | 38.2 | -0.012 | -0.112 | 39.7 | 0.024 |  |
| 31 | donch | Trend (hedge fund) | 2758 | 37.6 | -0.013 | -0.113 | 37.8 | -0.002 |  |
| 32 | rsi_div | Momentum / divergence | 1196 | 36.4 | -0.02 | -0.12 | 37.0 | -0.013 |  |
| 33 | liqline | Liquidity | 2704 | 36.6 | -0.026 | -0.126 | 38.2 | 0.017 |  |
| 34 | pa_engulf | Price action | 307 | 36.8 | -0.026 | -0.126 | 43.3 | 0.116 |  |
| 35 | pa_pin | Price action | 304 | 35.9 | -0.035 | -0.135 | 36.8 | -0.002 |  |
| 36 | ema_stack | Trend (MA) | 4927 | 36.6 | -0.036 | -0.136 | 38.0 | 0.005 |  |
| 37 | smt | Intermarket (SMT) | 1865 | 36.5 | -0.036 | -0.136 | 39.7 | 0.054 |  |
| 38 | zombie | Liquidity | 904 | 36.5 | -0.037 | -0.137 | 36.2 | -0.046 |  |
| 39 | sess_amd | Time (sessions) | 465 | 37.4 | -0.039 | -0.139 | 37.2 | -0.041 |  |
| 40 | vwap | Trend (MA) | 7341 | 36.3 | -0.04 | -0.14 | 37.9 | 0.006 |  |
| 41 | wavec | Elliott wave | 145 | 35.2 | -0.04 | -0.14 | 37.2 | -0.024 |  |
| 42 | tlbreak | Levels / breakouts | 2215 | 36.1 | -0.044 | -0.144 | 36.3 | -0.033 |  |
| 43 | crt | Liquidity | 938 | 34.8 | -0.073 | -0.173 | 33.9 | -0.104 |  |
| 44 | ew3 | Elliott wave | 1004 | 35.5 | -0.081 | -0.181 | 38.6 | -0.0 |  |
| 45 | dbl | Chart patterns (range) | 685 | 35.5 | -0.084 | -0.184 | 36.2 | -0.054 |  |
| 46 | ew5 | Elliott wave | 191 | 33.0 | -0.096 | -0.196 | 34.0 | -0.055 |  |
| 47 | abc | Elliott wave | 108 | 31.5 | -0.131 | -0.231 | 41.7 | 0.101 |  |
| 48 | kzs | Time (sessions) | 35 | 28.6 | -0.232 | -0.332 | 40.0 | 0.0 |  |
| 49 | harm_crab | Harmonic: Crab | 1 | 100.0 | 1.5 | 1.4 | 0.0 | -1.0 |  |
| 50 | harm_cypher_tight | Harmonic: Cypher | 7 | 85.7 | 1.143 | 1.043 | 71.4 | 0.786 |  |
| 51 | harm_vol_cypher_tight | Harmonic: Cypher (vol swings) | 6 | 66.7 | 0.667 | 0.567 | 50.0 | 0.25 |  |
| 52 | harm_butterfly_tight | Harmonic: Butterfly | 3 | 66.7 | 0.667 | 0.567 | 33.3 | -0.167 |  |
| 53 | harm_gartley_tight | Harmonic: Gartley | 2 | 50.0 | 0.25 | 0.15 | 50.0 | 0.25 |  |
| 54 | harm_bat_tight | Harmonic: Bat | 2 | 50.0 | 0.25 | 0.15 | 0.0 | -1.0 |  |
| 55 | harm_cypher | Harmonic: Cypher | 19 | 47.4 | 0.219 | 0.119 | 68.4 | 0.781 |  |
| 56 | harm_vol_cypher | Harmonic: Cypher (vol swings) | 22 | 45.5 | 0.136 | 0.036 | 40.9 | 0.023 |  |
| 57 | harm_vol_gartley | Harmonic: Gartley (vol swings) | 6 | 33.3 | 0.079 | -0.021 | 33.3 | 0.079 |  |
| 58 | harm_butterfly | Harmonic: Butterfly | 18 | 38.9 | 0.002 | -0.098 | 38.9 | 0.084 |  |
| 59 | harm_vol_butterfly | Harmonic: Butterfly (vol swings) | 11 | 27.3 | -0.172 | -0.272 | 18.2 | -0.278 |  |
| 60 | rect | Chart patterns (range) | 29 | 31.0 | -0.224 | -0.324 | 48.3 | 0.207 |  |
| 61 | harm_gartley | Harmonic: Gartley | 7 | 28.6 | -0.286 | -0.386 | 42.9 | 0.071 |  |
| 62 | harm_vol_bat | Harmonic: Bat (vol swings) | 4 | 25.0 | -0.375 | -0.475 | 25.0 | -0.375 |  |
| 63 | harm_vol_butterfly_tight | Harmonic: Butterfly (vol swings) | 5 | 20.0 | -0.5 | -0.6 | 20.0 | -0.206 |  |
| 64 | harm_bat | Harmonic: Bat | 5 | 20.0 | -0.5 | -0.6 | 40.0 | 0.0 |  |
| 65 | harm_vol_crab | Harmonic: Crab (vol swings) | 2 | 0.0 | -1.0 | -1.1 | 100.0 | 1.5 |  |
| 66 | harm_vol_gartley_tight | Harmonic: Gartley (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |
| 67 | harm_vol_crab_tight | Harmonic: Crab (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 100.0 | 1.5 |  |
| 68 | harm_vol_bat_tight | Harmonic: Bat (vol swings) | 1 | 0.0 | -1.0 | -1.1 | 0.0 | -1.0 |  |

## Stop study: where should the stop sit? (same entries, target fixed at 2.25 ATR, results in ATR, cost 0.15 ATR)

| group | stop | n | target hit % | stopped % | avg ATR | net ATR | mirror avg ATR | t (net vs 0) |
|---|---|---|---|---|---|---|---|---|
| all | 1.0 ATR | 64263 | 29.8 | 67.7 | 0.003 | -0.147 | 0.041 | -25.07 |
| all | 1.5 ATR | 64263 | 37.4 | 57.8 | -0.015 | -0.165 | 0.022 | -23.37 |
| all | 2.0 ATR | 64263 | 42.8 | 49.8 | -0.028 | -0.178 | 0.001 | -22.00 |
| all | 2.5 ATR | 64263 | 46.9 | 42.9 | -0.031 | -0.181 | 0.001 | -20.19 |
| all | 3.0 ATR | 64263 | 49.7 | 37.6 | -0.044 | -0.194 | -0.015 | -20.06 |
| 1m | 1.0 ATR | 11977 | 32.6 | 65.7 | 0.081 | -0.069 | 0.153 | -5.00 |
| 1m | 1.5 ATR | 11977 | 38.6 | 58.8 | -0.01 | -0.16 | 0.09 | -9.69 |
| 1m | 2.0 ATR | 11977 | 44.2 | 51.8 | -0.043 | -0.193 | 0.058 | -10.16 |
| 1m | 2.5 ATR | 11977 | 48.3 | 46.2 | -0.078 | -0.228 | 0.017 | -10.76 |
| 1m | 3.0 ATR | 11977 | 51.1 | 41.3 | -0.124 | -0.274 | -0.045 | -11.85 |
| 15m | 1.0 ATR | 17861 | 28.9 | 69.0 | -0.031 | -0.181 | 0.051 | -16.42 |
| 15m | 1.5 ATR | 17861 | 37.5 | 58.5 | -0.026 | -0.176 | 0.047 | -13.09 |
| 15m | 2.0 ATR | 17861 | 43.1 | 51.2 | -0.053 | -0.203 | 0.038 | -13.10 |
| 15m | 2.5 ATR | 17861 | 47.4 | 45.0 | -0.067 | -0.217 | 0.036 | -12.62 |
| 15m | 3.0 ATR | 17861 | 50.9 | 40.0 | -0.074 | -0.224 | 0.008 | -11.99 |
| 1h | 1.0 ATR | 17591 | 29.3 | 67.8 | -0.009 | -0.159 | 0.019 | -14.33 |
| 1h | 1.5 ATR | 17591 | 37.1 | 58.0 | -0.026 | -0.176 | 0.012 | -13.03 |
| 1h | 2.0 ATR | 17591 | 42.8 | 50.0 | -0.033 | -0.183 | -0.011 | -11.86 |
| 1h | 2.5 ATR | 17591 | 47.1 | 43.3 | -0.032 | -0.182 | 0.0 | -10.63 |
| 1h | 3.0 ATR | 17591 | 50.1 | 38.6 | -0.056 | -0.206 | 0.015 | -11.04 |
| 4h | 1.0 ATR | 13135 | 29.1 | 68.7 | -0.017 | -0.167 | -0.029 | -12.93 |
| 4h | 1.5 ATR | 13135 | 37.0 | 57.8 | -0.015 | -0.165 | -0.047 | -10.53 |
| 4h | 2.0 ATR | 13135 | 42.1 | 48.2 | -0.003 | -0.153 | -0.06 | -8.60 |
| 4h | 2.5 ATR | 13135 | 46.2 | 39.4 | 0.04 | -0.11 | -0.028 | -5.66 |
| 4h | 3.0 ATR | 13135 | 48.6 | 32.3 | 0.067 | -0.083 | -0.024 | -4.04 |
| 1d | 1.0 ATR | 3699 | 29.5 | 64.4 | 0.048 | -0.102 | -0.024 | -4.20 |
| 1d | 1.5 ATR | 3699 | 35.7 | 51.2 | 0.068 | -0.082 | -0.03 | -2.87 |
| 1d | 2.0 ATR | 3699 | 39.0 | 40.6 | 0.076 | -0.074 | -0.09 | -2.32 |
| 1d | 2.5 ATR | 3699 | 40.9 | 33.4 | 0.052 | -0.098 | -0.104 | -2.84 |
| 1d | 3.0 ATR | 3699 | 42.0 | 27.8 | 0.016 | -0.134 | -0.127 | -3.66 |

| group | question | n | value |
|---|---|---|---|
| all | stopped at 1.5 ATR, target reached later | 46913 | 31.4 % reached it later (mirror direction 31.0 %); 73.0 % of all trades were stopped |
| all | MAE of trades that reached the target (ATR) | 39172 | p50 1.04 · p75 2.33 · p90 4.44 |
| 1m | stopped at 1.5 ATR, target reached later | 9109 | 32.2 % reached it later (mirror direction 33.0 %); 76.1 % of all trades were stopped |
| 1m | MAE of trades that reached the target (ATR) | 7647 | p50 0.97 · p75 2.42 · p90 4.67 |
| 15m | stopped at 1.5 ATR, target reached later | 13579 | 35.7 % reached it later (mirror direction 33.9 %); 76.0 % of all trades were stopped |
| 15m | MAE of trades that reached the target (ATR) | 11646 | p50 1.22 · p75 2.67 · p90 5.3 |
| 1h | stopped at 1.5 ATR, target reached later | 13262 | 34.2 % reached it later (mirror direction 34.9 %); 75.4 % of all trades were stopped |
| 1h | MAE of trades that reached the target (ATR) | 11186 | p50 1.15 · p75 2.57 · p90 4.83 |
| 4h | stopped at 1.5 ATR, target reached later | 8904 | 23.9 % reached it later (mirror direction 23.3 %); 67.8 % of all trades were stopped |
| 4h | MAE of trades that reached the target (ATR) | 7078 | p50 0.9 · p75 1.81 · p90 2.97 |
| 1d | stopped at 1.5 ATR, target reached later | 2059 | 13.3 % reached it later (mirror direction 12.4 %); 55.7 % of all trades were stopped |
| 1d | MAE of trades that reached the target (ATR) | 1615 | p50 0.7 · p75 1.24 · p90 2.02 |

Reading: a stop that is never reached only helps if the AVERAGE (net ATR) goes up, not just the target-hit share; compare with the mirror column (the opposite direction on the same bars).


## Pre-registered tests (signals after the freeze date only; docs/PREREG_2026-11-01.md)

| hypothesis | n | win % | avg R | net avg R | t vs random | net 1st half (n) | net 2nd half (n) | PASS |
|---|---|---|---|---|---|---|---|---|
| H1 sess_amd + loc | 77 | 45.5 | 0.149 | 0.049 | +0.35 | 0.044 (38) | 0.054 (39) |  |
| H2 ohl_open + Late 20-24 | 338 | 33.1 | -0.098 | -0.198 | -0.27 | -0.232 (169) | -0.164 (169) |  |

Gate: n >= 100, t > 3.0, net > 0 overall and in both time halves. Under n = 100 it is not evidence, whatever the numbers say.


## Schools of analysis (all their detectors pooled)

| rank | school | n | avg R |
|---|---|---|---|
| 1 | Harmonic: Crab | 1 | 1.5 |
| 2 | Harmonic: Cypher | 26 | 0.468 |
| 3 | Harmonic: Cypher (vol swings) | 28 | 0.25 |
| 4 | Harmonic: Butterfly | 21 | 0.097 |
| 5 | Wyckoff | 171 | 0.097 |
| 6 | Fibonacci | 3181 | 0.029 |
| 7 | SMC / ICT | 9054 | 0.015 |
| 8 | Trend (hedge fund) | 2899 | 0.007 |
| 9 | Price action | 1021 | 0.002 |
| 10 | Elliott wave | 3979 | 0.0 |
| 11 | Levels / breakouts | 12255 | -0.007 |
| 12 | Momentum / divergence | 2613 | -0.009 |
| 13 | Time (sessions) | 3111 | -0.015 |
| 14 | Liquidity | 8177 | -0.023 |
| 15 | Trend (MA) | 15100 | -0.031 |
| 16 | Intermarket (SMT) | 1865 | -0.036 |
| 17 | Harmonic: Gartley (vol swings) | 7 | -0.075 |
| 18 | Chart patterns (range) | 714 | -0.09 |
| 19 | Harmonic: Gartley | 9 | -0.167 |
| 20 | Harmonic: Butterfly (vol swings) | 16 | -0.274 |
| 21 | Harmonic: Bat | 7 | -0.286 |
| 22 | Harmonic: Bat (vol swings) | 5 | -0.5 |
| 23 | Harmonic: Crab (vol swings) | 3 | -1.0 |

## Best timeframe per detector (n >= 30)

| key | tf | n | win % | avg R | net avg R |
|---|---|---|---|---|---|
| breaker | 4h | 110 | 42.7 | 0.21 | 0.11 |
| breakout | 1d | 54 | 48.1 | 0.297 | 0.197 |
| cisd | 1m | 203 | 44.8 | 0.155 | 0.055 |
| crt | 1m | 86 | 39.5 | 0.0 | -0.1 |
| dbl | 1d | 48 | 39.6 | 0.048 | -0.052 |
| donch | 1d | 158 | 36.1 | 0.052 | -0.048 |
| ema_stack | 1d | 282 | 37.9 | 0.094 | -0.006 |
| ew3 | 1d | 63 | 38.1 | 0.047 | -0.053 |
| ew5 | 1m | 45 | 37.8 | -0.056 | -0.156 |
| ew_r2_d1 | 1h | 176 | 50.6 | 0.338 | 0.238 |
| ew_r2_d2 | 1h | 69 | 59.4 | 0.486 | 0.386 |
| ew_r2_v | 1m | 136 | 45.6 | 0.187 | 0.087 |
| ew_r3_d1 | 1d | 34 | 32.4 | 0.156 | 0.056 |
| ew_r3_d2 | 4h | 56 | 42.9 | 0.167 | 0.067 |
| ew_r3_v | 1d | 30 | 36.7 | 0.206 | 0.106 |
| fib | 15m | 642 | 42.4 | 0.093 | -0.007 |
| fvg | 1d | 121 | 41.3 | 0.168 | 0.068 |
| judas | 1m | 758 | 39.6 | 0.015 | -0.085 |
| level | 1m | 1201 | 39.5 | 0.015 | -0.085 |
| liqline | 1d | 155 | 40.0 | 0.206 | 0.106 |
| m2022 | 1d | 81 | 48.1 | 0.374 | 0.274 |
| ma_cross | 1d | 130 | 45.4 | 0.268 | 0.168 |
| macd_div | 1d | 74 | 48.6 | 0.336 | 0.236 |
| msb_ob | 15m | 491 | 42.4 | 0.116 | 0.016 |
| ob | 1m | 306 | 40.2 | 0.078 | -0.022 |
| ohl_break | 1d | 46 | 47.8 | 0.296 | 0.196 |
| ohl_open | 1h | 778 | 41.0 | 0.08 | -0.02 |
| orb | 15m | 169 | 37.9 | -0.007 | -0.107 |
| ote | 15m | 212 | 45.3 | 0.165 | 0.065 |
| pa_engulf | 1h | 91 | 37.4 | -0.014 | -0.114 |
| pa_inside | 1h | 79 | 44.3 | 0.152 | 0.052 |
| pa_pin | 1h | 113 | 43.4 | 0.162 | 0.062 |
| po3 | 15m | 62 | 43.5 | 0.116 | 0.016 |
| rsi_div | 1h | 338 | 37.3 | 0.008 | -0.092 |
| sess_amd | 1h | 230 | 37.8 | -0.028 | -0.128 |
| sma1040 | 1d | 53 | 58.5 | 0.612 | 0.512 |
| smt | 1m | 346 | 42.5 | 0.078 | -0.022 |
| sweep | 1m | 510 | 41.2 | 0.066 | -0.034 |
| tlbreak | 1d | 152 | 38.2 | 0.123 | 0.023 |
| turtle55 | 1d | 88 | 46.6 | 0.272 | 0.172 |
| unicorn | 15m | 81 | 45.7 | 0.208 | 0.108 |
| vwap | 1d | 422 | 36.3 | 0.032 | -0.068 |
| wavec | 4h | 30 | 46.7 | 0.204 | 0.104 |
| wyck | 1h | 40 | 42.5 | 0.09 | -0.01 |
| zombie | 1d | 54 | 44.4 | 0.241 | 0.141 |

## Long vs short

| key | long n | long avg R | short n | short avg R |
|---|---|---|---|---|
| *ALL* | 0 | None | 0 | None |
| abc | 69 | -0.244 | 39 | 0.068 |
| breaker | 200 | -0.049 | 197 | 0.077 |
| breakout | 466 | -0.077 | 627 | 0.067 |
| cisd | 496 | 0.013 | 449 | 0.048 |
| crt | 502 | -0.078 | 436 | -0.067 |
| dbl | 331 | -0.143 | 354 | -0.028 |
| donch | 1121 | -0.072 | 1637 | 0.027 |
| ema_stack | 2229 | -0.122 | 2698 | 0.035 |
| ew3 | 501 | -0.205 | 503 | 0.043 |
| ew5 | 65 | -0.346 | 126 | 0.033 |
| ew_r2_d1 | 216 | -0.036 | 341 | 0.082 |
| ew_r2_d2 | 111 | 0.099 | 183 | 0.157 |
| ew_r2_v | 388 | -0.005 | 551 | 0.053 |
| ew_r3_d1 | 100 | -0.055 | 138 | 0.085 |
| ew_r3_d2 | 45 | 0.158 | 108 | 0.099 |
| ew_r3_v | 151 | -0.072 | 199 | 0.102 |
| fib | 1164 | -0.039 | 1218 | 0.078 |
| fvg | 1627 | -0.054 | 1522 | 0.102 |
| harm_bat | 5 | -0.5 | 0 | None |
| harm_bat_tight | 2 | 0.25 | 0 | None |
| harm_butterfly | 11 | -0.042 | 7 | 0.071 |
| harm_butterfly_tight | 2 | 0.25 | 1 | 1.5 |
| harm_crab | 1 | 1.5 | 0 | None |
| harm_cypher | 7 | -0.191 | 12 | 0.458 |
| harm_cypher_tight | 1 | -1.0 | 6 | 1.5 |
| harm_gartley | 5 | -0.5 | 2 | 0.25 |
| harm_gartley_tight | 1 | -1.0 | 1 | 1.5 |
| harm_vol_bat | 3 | -1.0 | 1 | 1.5 |
| harm_vol_bat_tight | 1 | -1.0 | 0 | None |
| harm_vol_butterfly | 10 | -0.089 | 1 | -1.0 |
| harm_vol_butterfly_tight | 4 | -0.375 | 1 | -1.0 |
| harm_vol_crab | 2 | -1.0 | 0 | None |
| harm_vol_crab_tight | 1 | -1.0 | 0 | None |
| harm_vol_cypher | 11 | -0.545 | 11 | 0.818 |
| harm_vol_cypher_tight | 2 | -1.0 | 4 | 1.5 |
| harm_vol_gartley | 5 | -0.205 | 1 | 1.5 |
| harm_vol_gartley_tight | 1 | -1.0 | 0 | None |
| judas | 860 | -0.087 | 1435 | 0.034 |
| kzs | 23 | -0.483 | 12 | 0.25 |
| level | 3315 | -0.05 | 1677 | 0.082 |
| liqline | 1269 | -0.08 | 1435 | 0.021 |
| m2022 | 323 | -0.089 | 333 | 0.065 |
| ma_cross | 1454 | -0.037 | 1378 | 0.046 |
| macd_div | 772 | -0.005 | 645 | 0.009 |
| msb_ob | 953 | -0.026 | 871 | 0.086 |
| ob | 816 | -0.109 | 851 | 0.096 |
| ohl_break | 349 | -0.013 | 460 | 0.095 |
| ohl_open | 1609 | -0.089 | 1537 | 0.088 |
| orb | 79 | 0.126 | 99 | -0.102 |
| ote | 375 | -0.031 | 424 | 0.13 |
| pa_engulf | 169 | -0.066 | 138 | 0.023 |
| pa_inside | 178 | -0.074 | 185 | 0.185 |
| pa_pin | 165 | -0.073 | 139 | 0.011 |
| pa_star | 23 | -0.297 | 24 | 0.262 |
| po3 | 69 | 0.064 | 69 | 0.047 |
| rect | 11 | 0.364 | 18 | -0.583 |
| rsi_div | 615 | -0.067 | 581 | 0.029 |
| sess_amd | 230 | -0.034 | 235 | -0.043 |
| sma1040 | 24 | 0.782 | 29 | 0.471 |
| smt | 975 | -0.068 | 890 | -0.001 |
| sweep | 2023 | -0.055 | 1608 | 0.059 |
| tlbreak | 1105 | -0.119 | 1110 | 0.031 |
| turtle55 | 44 | 0.162 | 44 | 0.381 |
| unicorn | 206 | -0.088 | 210 | 0.09 |
| vwap | 3431 | -0.114 | 3910 | 0.024 |
| wavec | 77 | -0.27 | 68 | 0.22 |
| wyck | 89 | 0.053 | 82 | 0.144 |
| zombie | 444 | -0.076 | 460 | 0.001 |

## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)

| key | with n | with win % | with avg R | against n | against win % | against avg R |
|---|---|---|---|---|---|---|
| *ALL* | 37784 | 37.1 | -0.021 | 26290 | 37.9 | 0.007 |
| abc | 34 | 29.4 | -0.134 | 74 | 32.4 | -0.13 |
| breaker | 203 | 37.9 | 0.038 | 192 | 35.4 | -0.002 |
| breakout | 773 | 39.3 | 0.011 | 317 | 38.5 | -0.006 |
| cisd | 379 | 36.4 | -0.039 | 563 | 39.8 | 0.077 |
| crt | 362 | 33.4 | -0.114 | 573 | 35.6 | -0.046 |
| dbl | 436 | 35.3 | -0.105 | 248 | 35.9 | -0.042 |
| donch | 2411 | 37.8 | -0.007 | 340 | 36.2 | -0.061 |
| ema_stack | 3959 | 37.1 | -0.019 | 947 | 34.5 | -0.097 |
| ew3 | 606 | 36.3 | -0.054 | 398 | 34.2 | -0.123 |
| ew5 | 147 | 33.3 | -0.083 | 43 | 30.2 | -0.176 |
| ew_r2_d1 | 345 | 36.8 | 0.011 | 212 | 40.1 | 0.077 |
| ew_r2_d2 | 165 | 39.4 | 0.08 | 129 | 45.0 | 0.206 |
| ew_r2_v | 559 | 35.1 | -0.04 | 378 | 42.1 | 0.13 |
| ew_r3_d1 | 200 | 37.0 | 0.025 | 38 | 36.8 | 0.028 |
| ew_r3_d2 | 125 | 36.0 | 0.087 | 28 | 50.0 | 0.25 |
| ew_r3_v | 301 | 38.5 | 0.052 | 49 | 32.7 | -0.127 |
| fib | 1190 | 38.3 | 0.003 | 1181 | 39.3 | 0.039 |
| fvg | 1778 | 38.4 | 0.016 | 1354 | 39.3 | 0.037 |
| harm_bat | 2 | 0.0 | -1.0 | 3 | 33.3 | -0.167 |
| harm_bat_tight | 1 | 0.0 | -1.0 | 1 | 100.0 | 1.5 |
| harm_butterfly | 6 | 66.7 | 0.667 | 12 | 25.0 | -0.33 |
| harm_butterfly_tight | 1 | 100.0 | 1.5 | 2 | 50.0 | 0.25 |
| harm_crab | 0 | None | None | 1 | 100.0 | 1.5 |
| harm_cypher | 9 | 22.2 | -0.371 | 10 | 70.0 | 0.75 |
| harm_cypher_tight | 2 | 50.0 | 0.25 | 5 | 100.0 | 1.5 |
| harm_gartley | 2 | 0.0 | -1.0 | 5 | 40.0 | 0.0 |
| harm_gartley_tight | 1 | 0.0 | -1.0 | 1 | 100.0 | 1.5 |
| harm_vol_bat | 2 | 0.0 | -1.0 | 2 | 50.0 | 0.25 |
| harm_vol_bat_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| harm_vol_butterfly | 2 | 50.0 | 0.25 | 9 | 22.2 | -0.265 |
| harm_vol_butterfly_tight | 1 | 0.0 | -1.0 | 4 | 25.0 | -0.375 |
| harm_vol_crab | 0 | None | None | 2 | 0.0 | -1.0 |
| harm_vol_crab_tight | 0 | None | None | 1 | 0.0 | -1.0 |
| harm_vol_cypher | 8 | 25.0 | -0.375 | 14 | 57.1 | 0.429 |
| harm_vol_cypher_tight | 3 | 33.3 | -0.167 | 3 | 100.0 | 1.5 |
| harm_vol_gartley | 3 | 0.0 | -0.508 | 3 | 66.7 | 0.667 |
| harm_vol_gartley_tight | 1 | 0.0 | -1.0 | 0 | None | None |
| judas | 1476 | 39.2 | 0.008 | 807 | 36.1 | -0.059 |
| kzs | 13 | 30.8 | -0.231 | 22 | 27.3 | -0.232 |
| level | 2397 | 37.4 | -0.025 | 2573 | 38.2 | 0.016 |
| liqline | 1533 | 35.9 | -0.048 | 1166 | 37.6 | 0.002 |
| m2022 | 372 | 38.7 | 0.024 | 282 | 35.8 | -0.06 |
| ma_cross | 1678 | 38.1 | 0.004 | 1143 | 38.0 | 0.005 |
| macd_div | 292 | 37.3 | -0.018 | 1122 | 37.8 | 0.009 |
| msb_ob | 900 | 37.4 | 0.001 | 917 | 39.9 | 0.059 |
| ob | 906 | 37.2 | -0.009 | 753 | 36.9 | 0.002 |
| ohl_break | 489 | 39.9 | 0.019 | 318 | 41.8 | 0.092 |
| ohl_open | 1691 | 37.1 | -0.01 | 1447 | 38.0 | 0.008 |
| orb | 97 | 38.1 | -0.046 | 81 | 38.3 | 0.053 |
| ote | 338 | 35.8 | -0.058 | 459 | 43.1 | 0.136 |
| pa_engulf | 151 | 32.5 | -0.145 | 156 | 41.0 | 0.089 |
| pa_inside | 214 | 41.1 | 0.07 | 149 | 38.3 | 0.041 |
| pa_pin | 124 | 35.5 | -0.031 | 179 | 36.3 | -0.031 |
| pa_star | 23 | 17.4 | -0.444 | 24 | 54.2 | 0.403 |
| po3 | 71 | 47.9 | 0.246 | 66 | 31.8 | -0.133 |
| rect | 17 | 35.3 | -0.118 | 12 | 25.0 | -0.375 |
| rsi_div | 328 | 38.7 | 0.024 | 866 | 35.6 | -0.035 |
| sess_amd | 214 | 37.9 | -0.045 | 251 | 37.1 | -0.033 |
| sma1040 | 19 | 52.6 | 0.389 | 34 | 61.8 | 0.737 |
| smt | 965 | 34.7 | -0.082 | 900 | 38.3 | 0.014 |
| sweep | 1610 | 35.8 | -0.047 | 2013 | 38.6 | 0.032 |
| tlbreak | 1109 | 36.3 | -0.052 | 1104 | 35.9 | -0.034 |
| turtle55 | 67 | 43.3 | 0.194 | 21 | 57.1 | 0.519 |
| unicorn | 203 | 40.9 | 0.075 | 211 | 33.2 | -0.071 |
| vwap | 5852 | 36.2 | -0.041 | 1469 | 36.5 | -0.047 |
| wavec | 46 | 39.1 | 0.168 | 99 | 33.3 | -0.137 |
| wyck | 76 | 34.2 | -0.082 | 95 | 45.3 | 0.239 |
| zombie | 495 | 34.5 | -0.092 | 409 | 38.9 | 0.03 |

## Time of day (UTC session, intraday bars) and weekday - every detector pooled

| when | n | win % | avg R |
|---|---|---|---|
| Fri | 15020 | 35.0 | -0.027 |
| Mon | 7691 | 38.8 | -0.008 |
| Sat | 11480 | 35.4 | -0.048 |
| Sun | 7167 | 37.8 | -0.033 |
| Thu | 7573 | 39.7 | 0.06 |
| Tue | 7532 | 38.5 | -0.013 |
| Wed | 7800 | 39.9 | 0.028 |
| Asia 00-07 | 19188 | 37.2 | -0.025 |
| Late 20-24 | 8412 | 37.6 | -0.01 |
| London 07-12 | 11301 | 39.2 | 0.01 |
| New York 12-20 | 21663 | 36.8 | -0.018 |

## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), volume, volatility regime, session

Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).

| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |
|---|---|---|---|---|---|---|---|---|---|---|
| all signals | 64263 | 37.4 | -0.01 | -0.002 | -1.31 | 27755 | -0.023 | 36508 | -0.001 |  |
| grade A+++ | 490 | 41.0 | 0.082 | 0.094 | -0.17 | 253 | 0.088 | 237 | 0.075 |  |
| grade A+ | 8579 | 36.6 | -0.027 | 0.014 | -2.46 | 4144 | -0.016 | 4435 | -0.037 |  |
| grade A | 21307 | 37.4 | 0.004 | 0.019 | -1.46 | 9809 | -0.031 | 11498 | 0.033 |  |
| grade B | 22095 | 37.4 | -0.014 | -0.021 | +0.69 | 9278 | -0.032 | 12817 | -0.001 |  |
| grade C | 11792 | 37.9 | -0.022 | -0.023 | +0.10 | 4271 | 0.001 | 7521 | -0.035 |  |
| layer htf | 37784 | 37.1 | -0.021 | 0.009 | -3.75 | 16265 | -0.044 | 21519 | -0.004 |  |
| layer loc | 13968 | 38.2 | 0.015 | -0.007 | +1.68 | 5975 | 0.037 | 7993 | -0.002 |  |
| layer vol | 20363 | 38.0 | -0.004 | 0.011 | -1.35 | 8870 | -0.019 | 11493 | 0.008 |  |
| layer reg | 46103 | 36.8 | -0.01 | -0.004 | -0.93 | 20082 | -0.024 | 26021 | 0.0 |  |
| layer time | 36663 | 37.4 | -0.003 | 0.014 | -2.07 | 18312 | -0.024 | 18351 | 0.018 |  |
| no htf | 26479 | 37.8 | 0.005 | -0.018 | +2.48 | 11490 | 0.008 | 14989 | 0.003 |  |
| no loc | 50295 | 37.2 | -0.017 | -0.001 | -2.35 | 21780 | -0.039 | 28515 | -0.001 |  |
| no vol | 43900 | 37.1 | -0.013 | -0.008 | -0.66 | 18885 | -0.024 | 25015 | -0.005 |  |
| no reg | 18160 | 39.0 | -0.01 | 0.001 | -0.97 | 7673 | -0.02 | 10487 | -0.003 |  |
| no time | 27600 | 37.3 | -0.02 | -0.024 | +0.39 | 9443 | -0.02 | 18157 | -0.02 |  |
| no loc / sma1040 | 48 | 60.4 | 0.664 | -0.113 | +3.65 | 15 | 0.833 | 33 | 0.587 |  |
| loc / ew_r3_d2 | 32 | 59.4 | 0.557 | 0.088 | +1.79 | 16 | 0.148 | 16 | 0.966 |  |
| grade B / wyck | 43 | 48.8 | 0.287 | 0.229 | +0.27 | 18 | 0.389 | 25 | 0.214 |  |
| no loc / turtle55 | 88 | 46.6 | 0.272 | 0.31 | -0.25 | 32 | 0.114 | 56 | 0.362 |  |
| no loc / wyck | 72 | 45.8 | 0.239 | 0.123 | +0.62 | 27 | 0.124 | 45 | 0.309 |  |
| grade A+ / ew_r3_v | 44 | 47.7 | 0.231 | 0.105 | +0.51 | 24 | 0.32 | 20 | 0.125 |  |
| grade A / ew_r3_d2 | 71 | 42.3 | 0.231 | 0.037 | +1.12 | 32 | 0.167 | 39 | 0.284 |  |
| grade B / pa_inside | 112 | 47.3 | 0.229 | 0.065 | +1.03 | 40 | 0.188 | 72 | 0.252 |  |
| grade C / ote | 141 | 46.8 | 0.21 | -0.042 | +1.86 | 58 | 0.192 | 83 | 0.222 |  |
| grade A / ew_r3_d1 | 100 | 41.0 | 0.199 | -0.023 | +1.45 | 34 | -0.068 | 66 | 0.337 |  |
| loc / liqline | 346 | 43.6 | 0.158 | 0.036 | +1.48 | 144 | 0.28 | 202 | 0.07 |  |
| grade A / turtle55 | 39 | 43.6 | 0.155 | 0.31 | -0.65 | 14 | 0.127 | 25 | 0.171 |  |
| grade A / ew_r2_d2 | 112 | 41.1 | 0.154 | 0.189 | -0.23 | 45 | 0.238 | 67 | 0.097 |  |
| grade A+ / breakout | 318 | 44.7 | 0.153 | 0.059 | +0.98 | 152 | 0.114 | 166 | 0.189 |  |
| no loc / po3 | 119 | 43.7 | 0.15 | 0.146 | +0.02 | 58 | -0.121 | 61 | 0.407 |  |

## Conflicts (pointing opposite ways on the same bar)

| a | b | together | opposite | % |
|---|---|---|---|---|
| level | vwap | 8226 | 4159 | 50.6 |
| sweep | vwap | 6452 | 3866 | 59.9 |
| ema_stack | sweep | 3328 | 2440 | 73.3 |
| ema_stack | level | 4017 | 2218 | 55.2 |
| fvg | vwap | 4524 | 1808 | 40.0 |
| ohl_open | vwap | 4088 | 1739 | 42.5 |
| macd_div | vwap | 2169 | 1737 | 80.1 |
| fib | vwap | 3048 | 1565 | 51.3 |
| level | sweep | 3676 | 1537 | 41.8 |
| msb_ob | vwap | 2660 | 1522 | 57.2 |
| ob | vwap | 2652 | 1459 | 55.0 |
| rsi_div | vwap | 1830 | 1437 | 78.5 |
| fvg | level | 3220 | 1434 | 44.5 |
| judas | level | 2537 | 1417 | 55.9 |
| smt | vwap | 3026 | 1359 | 44.9 |
| level | ma_cross | 2557 | 1339 | 52.4 |
| ma_cross | sweep | 2049 | 1279 | 62.4 |
| liqline | vwap | 3591 | 1272 | 35.4 |
| ma_cross | vwap | 4201 | 1246 | 29.7 |
| level | ohl_open | 2366 | 1218 | 51.5 |
| tlbreak | vwap | 2610 | 1209 | 46.3 |
| judas | vwap | 3783 | 1078 | 28.5 |
| judas | sweep | 1635 | 1015 | 62.1 |
| fvg | ohl_open | 1211 | 997 | 82.3 |
| liqline | sweep | 1848 | 980 | 53.0 |

## Confluence: more agreeing families = better?

| agreeing families | n | win % | avg R |
|---|---|---|---|
| 1 families | 26 | 42.3 | 0.272 |
| 2 families | 401 | 38.7 | 0.025 |
| 2 families (with opposition) | 1387 | 35.4 | -0.045 |
| 3 families | 1138 | 40.2 | 0.072 |
| 3 families (with opposition) | 4627 | 36.4 | -0.039 |
| 4+ families | 924 | 38.1 | -0.007 |
| 4+ families (with opposition) | 4195 | 35.8 | -0.051 |

## Gann time cycles: another swing pivot within +-2 bars of pivot + 30/45/60/90/120/144/180 bars vs ordinary offsets

| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |
|---|---|---|---|---|---|
| 1m | 82.9 | 28411 | 82.7 | 390888 | +0.8 |
| 1m shapes 120/180/240/360 deg | 79.9 | 11520 | 80.4 | 11695 | -1.3 |
| 15m | 65.0 | 19938 | 65.0 | 276338 | +0.1 |
| 15m shapes 120/180/240/360 deg | 63.0 | 10407 | 63.4 | 10293 | -0.9 |
| 1h | 58.0 | 16155 | 57.9 | 223801 | +0.1 |
| 1h shapes 120/180/240/360 deg | 56.6 | 8825 | 56.9 | 8804 | -0.6 |
| 4h | 56.6 | 12040 | 57.7 | 166361 | -2.5 |
| 4h shapes 120/180/240/360 deg | 56.9 | 6767 | 56.2 | 6780 | +1.1 |
| 1d | 55.5 | 3175 | 56.1 | 42604 | -0.7 |
| 1d shapes 120/180/240/360 deg | 57.5 | 2020 | 57.6 | 2024 | -0.1 |

Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.

## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)

| tf | trades | win % | avg R | random-direction avg R | difference (t) |
|---|---|---|---|---|---|
| 15m | 71 | 26.8 | +0.450 | +0.262 | +0.34 |
| 1d | 55 | 41.8 | +0.031 | +0.333 | -1.13 |
| 1h | 132 | 22.7 | -0.067 | -0.089 | +0.10 |
| 4h | 100 | 33.0 | +0.146 | -0.187 | +1.83 |

Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.

## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)

| window | days | mean daily return % |
|---|---|---|
| 15 days around new moon | 2380 | -0.101 |
| 15 days around full moon | 2328 | 0.035 |

Difference t = -1.68 (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous).

## Exit variants on the SAME entries (RR and break-even stop)

Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.

Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.

| exit | n | win % | avg R | net avg R (after costs) | total R | t |
|---|---|---|---|---|---|---|
| rr1.0 | 64263 | 48.8 | -0.023 | -0.123 | -1477.7 | -5.90 |
| rr1.5 | 64263 | 40.2 | -0.01 | -0.11 | -665.8 | -2.20 |
| rr2.0 | 64263 | 35.0 | 0.001 | -0.099 | 82.5 | +0.24 |
| rr3.0 | 64263 | 29.7 | 0.024 | -0.076 | 1517.7 | +3.67 |
| rr1.5_be | 64263 | 34.4 | -0.005 | -0.105 | -343.1 | -1.22 |
| rr2.0_be | 64263 | 27.5 | 0.01 | -0.09 | 620.8 | +2.00 |
| rr1.5_h16 | 64263 | 41.9 | -0.005 | -0.105 | -330.5 | -1.16 |
| rr2.0_h16 | 64263 | 38.7 | 0.008 | -0.092 | 505.7 | +1.59 |
| pt_1.5_3 | 64263 | 48.7 | 0.031 | -0.069 | 1996.2 | +6.74 |
| pt_1.0_3 | 64263 | 48.8 | 0.018 | -0.082 | 1185.8 | +4.29 |
| pt_1.5_5 | 64263 | 48.7 | 0.049 | -0.051 | 3164.0 | +10.27 |
| trail_only | 64263 | 48.7 | 0.096 | -0.004 | 6185.2 | +17.23 |
