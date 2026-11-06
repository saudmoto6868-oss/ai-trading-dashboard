# Spot analyzer - what each panel computes (Spot page > Analyzer)

Pick a symbol (crypto from OKX spot, metals from Yahoo futures) -> 4 charts side by side (Monthly, Weekly, Daily, 4 hours)
+ cards. Style follows the owner's reference picture (charcoal panels, amber accent, rings). Code: `modules/spot_ind.py`
(math), `modules/spot_dash.py` (drawing + data), tests `tests/test_spot_analyzer.py`.
**Mock-tested only. The combined score is not backtested: it is a structured reading of the chart, not evidence.**

## Timeframe roles (spot = buy and hold, no shorts)
| TF | Role | Weight in the score |
|---|---|---|
| 1M | primary trend, cycle position | 3 |
| 1W | trend + where to accumulate | 2.5 |
| 1D | setup | 1.5 |
| 4H | timing / confirmation of the entry | 1 |
Yearly is context only (too few bars). Monthly / weekly charts use a log price scale when the range is > 3x.

## Indicators and formulas
| Panel | Formula | Vote (+1 bull / -1 bear / 0) |
|---|---|---|
| EMA 20 / 50 / 200 | EMA_t = a x close_t + (1 - a) x EMA_t-1, a = 2/(n+1) | +1 close > EMA50 > EMA200, -1 reverse (with < 200 bars: close vs EMA50) |
| RSI 14 (Wilder) | RS = smoothed gain / smoothed loss (1/14), RSI = 100 - 100/(1+RS) | > 55 +1, < 45 -1; a divergence in the last 15 bars overrides |
| Divergence | last two confirmed swing lows: price lower low + RSI higher low = regular bull; price higher low + RSI lower low = hidden bull (mirror for highs) | drawn on price and RSI (solid regular, dashed hidden) |
| MACD | EMA12 - EMA26, signal EMA9, histogram = MACD - signal | +1 histogram > 0 and rising, -1 < 0 and falling |
| ADX 14 | Wilder +DI / -DI, DX = 100 x abs(+DI - -DI)/(+DI + -DI), ADX = Wilder mean of DX | ADX < 20 (range) halves the MA / MACD / structure votes |
| Bollinger | SMA20 +- 2 sd, %B, width | info |

RSI, ADX and MACD equal pandas-ta-classic to 1e-9 (test).

## SMC / ICT
- **Swings:** fractal, 2 bars each side (known 2 bars later, no look-ahead in the structure walk).
- **BOS / CHoCH:** a close above the last swing high = break up, below the last swing low = break down. First break against the
  current trend = CHoCH (change of character), breaks with it = BOS (break of structure). Vote = current structure trend.
- **Order block:** the last opposite-colour candle before the move that broke structure; kept while price has not closed through it.
- **Fair value gap:** 3 candles, low[i] > high[i-2] (bull) or high[i] < low[i-2] (bear), at least 0.25 ATR; removed once filled.
- **Liquidity:** equal highs / lows (two swings within 0.1 ATR) = resting stops (EQH buy-side, EQL sell-side).
- **Premium / discount (ICT):** dealing range = last swing high + low; above 50 % = premium, below = discount; OTE = 62-79 %
  retracement of the last leg. Vote: discount with structure not down = +1 (where spot buys), premium with structure not up = -1.

## Elliott + Fibonacci
Volatility-scaled zig-zag -> the most recent 6 pivots that form a 5-wave impulse with all 3 rules (wave 2 not beyond the start
of wave 1, wave 4 not into wave 1, wave 3 not the shortest) are labelled 0-5, then A B C after it; otherwise the last ABC.
Targets: 0.382 / 0.5 / 0.618 retracements and 1.272 / 1.618 extensions. Vote: impulse up +1 (down -1); once the ABC after an
impulse has started the vote flips (correction running).

## Gann
- **Square of 9:** from the last major pivot P: levels (sqrt(P) +- 0.25 k)^2, each 0.25 step in the root = 45 degrees.
  The 4 nearest are drawn on 1M / 1W.
- **Fitted grid + time cycle:** `gann_lab.fit` (grid that the past swings respected better than shifted grids) and the bar
  cycle with the most pivots; "turn in" = bars to the next cycle date. No vote (levels and timing only).

## SMT
Correlated pair on the same timeframe (BTC <-> ETH, coin <-> BTC, gold <-> silver, copper / platinum <-> gold): one makes a new
low / high, the other refuses (`modules/smt.py`, |correlation| >= 0.5 or nothing). Vote on 1W / 1D / 4H.

## Spot-only cards
Mayer multiple = close / SMA 200-day (crypto rule of thumb: < 0.8 historically cheap, > 2.4 overheated - not evidence here),
distance to the 200-week SMA, drawdown from the all-time high, 52-week range, 1-year return, 30-day realised volatility (annualised).
Ratios: gold / silver, copper / gold, ETH / BTC, coin / BTC (weekly closes, dashed line = 3-year median).

## Score
Per TF: mean of the votes x 100 (-100..100). Overall: weighted by the TF weights above. >= 35 accumulate, >= 10 hold / buy
dips, <= -35 take profit / wait, else wait. The staged buys / targets / invalidation come from `spot_plan.py`.

## Backtest result 1 (2026-11-06, run 42166341725, 18 coins + gold / silver / copper / platinum, 1W + 1M score)
Non-overlapping samples, spot long, no costs:
| Group | Horizon | score >= 35 | score <= -35 | all weeks | top vs rest |
|---|---|---|---|---|---|
| Crypto | 4 weeks (n 1038) | +0.45 % (n 187) | +0.79 % (n 221) | +1.43 % | t -0.64, no difference |
| Crypto | 12 weeks (n 334) | -3.13 % (n 62) | +10.09 % (n 64) | +4.79 % | t -1.63, no difference (leans the wrong way) |
| Metals | 4 weeks (n 236) | +1.90 % (n 71) | +1.49 % (n 8) | +1.22 % | t +0.59, no difference |
| Metals | 12 weeks (n 76) | +4.76 % (n 25) | +4.70 % (n 2) | +4.44 % | not evidence (n < 30) |
**Verdict: the combined score does NOT pick better spot entries.** On crypto a LOW score (after a fall) was followed by
higher 12-week returns than a high score (buying weakness beat buying strength), but not significantly. The Analyzer stays an
optional chart-reading tool; the score is not used as a buy signal. The test reruns every Monday.

## Next
- Backtest the score on 1W / 1M across many coins + gold before trusting it (lab).
- Telegram: send this screen as an image on request (`/spotchart BTC`), after the owner's bot setup.
