# Trading schools in XPIX: what each one says, where it lives in the code, and what the lab found

Lab numbers: all timeframes, stop 1.5 ATR, target 1.5R, no costs, vs a random direction at the same bars (data/strategy_lab.json, 2026-10-18 run).
Evidence rule: n >= 100, t > 3 vs random, positive in both halves. Only `level` (Levels / breakouts) passes the edge gate; the rest does not.

| school | core claim (short) | detectors in code | lab (n, avg R, random) | role we give it |
|---|---|---|---|---|
| Smart Money / ICT | institutions leave order blocks, fair value gaps and liquidity sweeps; price returns to them | ob, fvg, breaker, unicorn, msb_ob, cisd, m2022 | ob -0.10 (967) · fvg +0.01 (2067) · breaker -0.14 (257) · unicorn -0.13 (341) · msb_ob -0.07 (1346) · cisd 0.00 (710) · m2022 +0.04 (438) | location / trigger; none proven alone |
| Price action | S/R, breakouts, trend structure read from candles | level, breakout, tlbreak, ohl_break, ohl_open | level +0.07/+0.08 (3150+, PASSES) · breakout +0.05 (753) · tlbreak -0.00 (1727) · ohl_break -0.06 (483) · ohl_open 0.00 (2410) | the only school with an edge so far (level) |
| Elliott waves | 5-wave impulse + 3-wave correction, subjective counting | ew3, ew5, abc, wavec | ew3 -0.13 (775) · ew5 +0.03 (106) · abc +0.07 (103) · wavec +0.10 (88) | not proven; counts are subjective, keep as context only |
| Gann | time cycles and price angles | gann_lab (time cycles, zone trades) | cycle hits: no signal in the Gann test; zone trades out-of-sample: see STRATEGY_LAB.md | not proven; keep as a hypothesis |
| Harmonic (XABCD) | Fibonacci ratios complete a PRZ | harmonic.py (in the lab since 2026-10-18, key harmonic) | pending the next lab run | evidence needed before any use |
| Fibonacci | retracement / extension levels | fib, ote | fib -0.00 (1812) · ote +0.01 (645) | location only |
| Trend / moving averages | trend follows; buy above MA | ma_cross, ema_stack, vwap, donch, sma1040, turtle55 | vwap +0.01 (5383) · ema_stack -0.01 (3490) · donch -0.02 (2040) · sma1040 +0.35 (78, n too small) | HTF bias |
| Liquidity | stops above/below swings get swept | sweep, crt, liqline, zombie | sweep -0.02 (2780) · liqline +0.04 (1794) · zombie +0.09 (655) · crt -0.04 (651) | trigger candidates |
| Sessions / time | some hours move more (Judas, Asia range, opening range, power of 3) | judas, kzs, orb, po3, sess_amd | judas +0.03 (1713) · orb -0.18 (98) · sess_amd +0.18 (360) · po3 +0.03 (89) | timing |
| Momentum / divergence | RSI / MACD disagree with price | rsi_div, macd_div | rsi_div +0.05 (824) · macd_div +0.05 (988) | confirmation candidates |
| SMT (intermarket) | correlated assets fail to confirm a new high | smt | not in the lab summary | to test |

## Overlaps (they read the same candles)
- ICT order block, breaker, mitigation and SMC "demand zone" are the same candle-zone idea with different names.
- FVG and "imbalance" are the same gap rule.
- Liquidity sweep, Judas swing and stop hunts are the same event seen from different schools.
- Price action levels and Fibonacci levels both mark horizontal prices: they often coincide, so counting them twice is double counting.
- Elliott and harmonic both use swing pivots and Fibonacci ratios; their pivots are not identical, so results differ.

## Complementary (different questions)
- HTF bias (trend) answers "which side", location (Fib / levels / premium-discount) answers "is the price good", trigger (ICT / liquidity) answers "what fires", timing (sessions) answers "when".

## What to verify (open questions for the external reviews)
- Published tests of ICT / SMC concepts: most public material is discretionary; find any out-of-sample study.
- Harmonic pattern tests: several academic and practitioner tests report weak or no edge after costs; confirm.
- Elliott: subjective counts make a test hard; check whether any study uses fixed rules.
- Gann: the claims are mostly unfalsifiable; treat as hypotheses until a pre-registered test passes.
- Breakout / level trading: find the costs-adjusted results; ours have no costs.

## Our next steps
1. Add harmonic and SMT to the lab (same method) so every school has a number.
2. Test school PAIRS (e.g. level + sessions, sweep + HTF bias), not only single detectors, out-of-sample.
3. Keep one school's rule per trading style (see docs/PLAYBOOKS.md).
