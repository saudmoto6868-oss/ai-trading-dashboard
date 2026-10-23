# Backtest evidence for each school: an internet review (2024-2026)

> An honest summary of what appears in measurable research and publications. It is **not** a Lab result of the 6868 X project.
> Any external number = context; operational reliance only after costs and two halves on your own data.

## An approximate ranking of the strength of the published evidence

| Rank | School | Strength of external evidence | Short notes |
|------|--------|-------------------------------|-------------|
| 1 | Trend / Turtle / TSMOM | **Relatively strong** (academic + futures) | A time-series momentum edge; sensitive to costs on a short timeframe; shorting stocks/NQ is usually weak |
| 2 | Mean reversion (range) | **Medium to strong** in separate systems | A higher win rate; a left tail; it fails in a strong trend |
| 3 | Levels / simple breakout | **Medium** | Depends on the definition and costs; daily is better than 1m |
| 4 | Sessions / liquidity sweep | **Weak to medium** | Sometimes real dynamics; marketing ratios are exaggerated |
| 5 | Mechanical SMC/ICT | **Weak to marginal** | PF roughly 1.2-1.5 after costs in the best mechanical tests; a "complete" bot may lose |
| 6 | Order flow as a gate | **Weak as standalone** | Useful as confirmation at a level; few strong public tests |
| 7 | Elliott / Harmonic / Gann | **Weak as a full count** | Hard to automate; proxies (zigzag+fib) sometimes filter momentum; not proof of the whole theory |

---

## 1) Trend following

**What recurs:**
- TF / TSMOM systems on liquid futures linked to institutional trend indicators; the net Sharpe after costs depends on the lookback span and the memory length.
- Turtle/Donchian: the long side on rising indexes (such as NQ historically) is far better than the short on the same instrument in long-rising contracts.
- The original rules without modification may weaken over 2004-2026; modifications (profit harvesting, unit management) improve in some studies.
- Intraday (5m/15m) it usually dies to costs.

**Published examples (context, not to copy):**
- NQ Donchian 55 long: a high PF in a long sample; the short has a PF << 1 over the same period.
- Baskets of stocks/futures: Turtle modifications raise CAGR and lower DD against the original in some reports.

**For 6868 X:** daily + size from ATR + do not force shorts on assets with a long structural rise.

---

## 2) Mean reversion

**What recurs:**
- A win rate of ~60-70% against ~35-45% for trend.
- Combining **50/50 trend + mean reversion** often improves Sharpe/MAR because they lose at different times: not because each one is "better".
- Without a regime filter (ADX/range) MR gets crushed in thrusts.

**For 6868 X:** a separate system + a range filter; do not merge the Grade with trend.

---

## 3) Levels / Price action

**What recurs:**
- A break + retest or a bounce at a proven level is more mechanizable than a "pretty Pin".
- The sample and quality (how many times the level was respected) matter more than the candle's shape.

**For 6868 X:** consistent with the Lab (levels are relatively your strongest family).

---

## 4) Sessions / Liquidity

**What recurs:**
- A sweep then a reclaim: a small edge is possible after costs (an approximate example PF ~1.3 on large samples): **not** 70-80% as in the marketing.
- The session is a time filter; the strength comes from the level + the response.

---

## 5) SMC / ICT

**What recurs:**
- A mechanical definition of FVG / sweep / OB: usually a **small edge** (PF ~1.2-1.5) on liquid futures after spread: far below the promises.
- A "full ICT" bot without discrimination may end negative over a year.
- Discretionary + the same vocabulary may look better in small samples: a risk of curve-fitting and storytelling.
- Serious testing demands fixed rules + a large n + disabling component by component.

**For 6868 X:** context; not primary by default.

---

## 6) Order flow

**What recurs:**
- Few strong public backtests; most are educational.
- A mechanical frame for absorption (a large delta + a narrow price range at a level) is testable.
- An "order flow" proxy via relative open deviation (QuantifiedStrategies research) is illustrative only.

**For 6868 X:** a gate at a prepared level; the OF journal.

---

## 7) Elliott

**What recurs:**
- The full count is nearly impossible to backtest objectively.
- A proxy: ZigZag + fib + momentum (for example wave 3) may improve filtering of random momentum in narrow samples: **sensitive to the ZigZag threshold**.
- Commercial sources claiming high performance are usually without a full scientific method.

**For 6868 X:** invalidation + context.

---

## 8) Harmonic / Gann

**What recurs:**
- A scarcity of rigorous public tests per pattern with costs.
- Without an epsilon for the ratios and without separating the patterns = easy overfitting.

**For 6868 X:** visual/context; the Lab later for each pattern separately.

---

## Reference sources (for review)

- arXiv/SSRN: *Science and Practice of Trend-Following Systems* (Sepp & Lucic, 2026): TF/TSMOM
- Donchian/Turtle backtests on indexes (for example NQ variants 2010-2026)
- A systematic evaluation of the Turtle (modifications vs the original)
- A trend + mean reversion portfolio (Setup4Alpha / Price Action Lab patterns)
- ICT/SMC mechanical tests (Puravida Edge 2026; Raw Edge warnings)
- Elliott: testing difficulty (QuantifiedStrategies); ZigZag proxies (StratBase)
- Order flow: mechanical absorption frames; reservations on the standalone use

---

## What we do in your Lab (priority)

1. Trend daily (turtle/sma) + costs  
2. Levels + location  
3. Mean reversion as a separate range system  
4. Sweep/session as a filter  
5. OF as a gate on a journal sample  
6. No primary for Elliott/Gann/Harmonic/SMC until proven otherwise
