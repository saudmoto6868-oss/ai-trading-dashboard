# Schools coverage audit (2026-11-06, owner: "review the schools we forgot")

Read from the code, not from memory. "Scored" = counts as a star in `scorer.py`; "Context" = shown as a tag / flag, never a star and never a trade by itself; "Lab" = measured by the weekly
strategy lab (`strategy_lab.py`, keys in `SCHOOL`); "Chart" = drawn in the Workspace; "Radar" = a filter in the Chart Scanner.

| School | Scanner | Lab | Chart | Radar filter | Gap |
|---|---|---|---|---|---|
| Trend (MA cross, EMA stack, VWAP, Donchian, Turtle 55, SMA 10/40) | Scored (MA / VWAP are confirm-only) | yes | yes | yes | - |
| SMC / ICT (OB, FVG, breaker, Unicorn, MSB-OB, CISD, Model 2022, IFVG, MSS, premium / discount, Silver Bullet, mitigation) | Scored (Unicorn, MSB-OB) / flags | most | yes | yes | IFVG / MSS / PD / Silver / mitigation are Radar flags only (no lab key) |
| Liquidity (sweep, liquidity line, zombie, CRT) | Scored | yes | partly | yes | - |
| Time / sessions (Judas, session AMD, ORB, Kill Zone Sniper, Power of 3) | Scored | yes | yes | yes | - |
| Fibonacci (retracement, OTE) | Scored | yes | yes | yes | - |
| Elliott (3, 5, A-B-C, C) | Context | yes, per degree | auto count + forming | yes | lab: ew3 -0.13R (n = 775), so it stays context |
| Harmonic (Gartley, Bat, Butterfly, Crab, Cypher) | Radar flag only | yes | yes | yes | not a scanner detector: no tag on the live setup / strip |
| Momentum / divergence (RSI, MACD) | Confirm-only (family MA) | yes | lines | yes | volume divergence missing |
| Levels / breakouts (support, N-bar breakout, OHL, trendline break) | Confirm / flags | yes | yes | yes | - |
| Intermarket SMT | board (PR #235) + tag | yes (walk with peers) | yes | yes | no Telegram alert yet |
| Order flow | Workspace only | forward test | yes | - | by design (execution gate, not a scanner family) |
| **Price action** (engulfing, pin bar, inside bar, morning star AT a level) | **NEW: Context** | **NEW** | - | **NEW** | before: only context-free candle filters in the Radar |
| **Chart patterns as setups** (rectangle breakout + retest, double bottom / top neckline break) | **NEW: Context** | **NEW** | - | **NEW** | before: shapes only (`patterns.py`), no breakout / retest rule |
| **Wyckoff** (spring / upthrust) | **NEW: Context** | **NEW** | - | **NEW** | phases (accumulation / distribution, SOS / LPS) not built |
| **Gann** | - | yes (`gann_lab`) | yes (grid, angles, time, star) | **no** | **missing in the scanner**: needs a decision on WHICH grid (it is a per-chart setting); not built here |

## Found while auditing
- The Radar **"School ·" filters never fired**: they matched `signal["school"]`, a field no signal carries. Fixed in `chart_scan.strategy_flags` (key -> school through `strategy_lab.SCHOOL`, Elliott by family, Harmonic from `find_harmonics`). Test: `tests/test_school_filters_fire.py`.
- `CONTEXT_FAMILIES` now also holds `PA`, so the new detectors can show up as tags but cannot add a star or start a trade. They are in `signals.DETECTORS`, so the next weekly lab run measures every new key; nothing is promoted without n >= 30 and real costs (`docs/academy/DEVELOPMENT_NOTES.md`).

## Still not built (ideas ranked by usefulness, owner decides)
1. **Day plan**: per symbol, top-down (1D / 4H bias, 1H / 15m / 5m setups), grouped by session / kill zone, with the schools that agree. The pieces exist (HTF alignment in `scorer`, sessions in `intermarket.session_of`); the board does not.
2. Gann bounce in the scanner (needs the grid decision above).
3. ~~Telegram alert for the new context setups~~ done 2026-11-06 as "Watch" alerts (agree with the 1D + 4H bias); SMT Telegram alert still missing.
4. Exits: partial + trailing now exist in the Day plan and are measured by the lab (`pt_*` rows). Still missing: time stop, "exit if the school's invalidation level breaks".
5. Volume-profile setups (POC / VAH / VAL reaction) as a scanner key; anchored VWAP; pivot points. Ichimoku / Supertrend only if the lab shows they add something over Donchian.
