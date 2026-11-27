# Spot trade plan: the complete rules (2026-11-27)

Status: rules + code for sizing and the checklist are in place (`modules/spot_checklist.py`, mock/synthetic tested only).
Nothing here is a promise of return. Every strategy below is labelled. "Not evidence" means: not backtested to the
owner's luck guard (n ≥ 30 outcomes and |t| ≥ 3 after costs), so it is a rule of discipline, not a proven edge.

## 1. What already existed (kept)
- Levels from the schools on 1D / 1W / 1M (`modules/spot_plan.py`): staged buy levels, take-profit targets, invalidation.
- Staged buys 30 / 30 / 40 over the three highest levels (`spot_core.ladder`).
- Invalidation = a **weekly close** below it voids the plan (page card + alerts).
- Spot only: no shorts. "take profit / wait" is an action, not a sell-short.

## 2. What was missing and is now defined

### 2a. Multi-timeframe entry (top-down)
1. **Monthly (bias):** only plan buys when the monthly read is not against the trade (the page's `action`).
2. **Weekly (zone):** the buy levels come from the weekly structure; invalidation = weekly close below the zone.
3. **Daily (trigger):** the actual buy happens at a level, on a daily close holding above it, not on a wick alone.
4. Price more than **3%** above the first buy level = wait for the level, do not chase (`CHASE_PCT`).

### 2b. Position sizing (fixed fractional risk)
- Risk per trade: **1% of equity** if the whole ladder fills and price closes at the invalidation (`RISK_PCT`).
- Max position: **25% of equity** (`MAX_POS_PCT`), so a very tight stop cannot make a giant position.
- Stop wider than **20%** below the average entry = refused (`MAX_STOP_PCT`): the size would be too small to matter, pick a closer invalidation or skip.
- Source: `spot_checklist.size_plan()`. Rule of thumb, **not evidence**.

### 2c. Stops and invalidation
- Hard invalidation: **weekly close** below the zone. Stop adding; do not average down past it.
- Alerts exist for buy levels, T1, and invalidation (`spot_core` alerts).
- Never move the invalidation lower after a fill. Only raise a trailing stop, and only under a higher low.

### 2d. Staged buys (30 / 30 / 40)
- Levels from highest to lowest. The **40%** goes to the lowest (deepest) level: most room if the thesis is right, and the most price to give back if it is wrong.
- Average entry = total USD / total units, shown on the card. Reward/risk is measured from this average, not the first fill.

### 2e. Take-profit ladder
- T1: sell **1/3**. T2: sell **1/3**. The rest trails under the last higher low (`take_profit_plan`).
- Rule of thumb, **not evidence**. Locking part of the position early is for discipline; it may cut the best trades.

### 2f. Trade checklist (run before any buy)
The checklist (`spot_checklist.checklist`) returns pass / fail / unknown for each item. **Unknown is never a pass.**
1. Data: live price and all three timeframes available.
2. Levels: at least one buy level.
3. Invalidation exists and is below the lowest buy.
4. No chase: price within 3% of the first buy level.
5. Reward/risk to T1 ≥ 2 (from the average entry).
6. Size: a fill-all loss at the invalidation ≤ 1% of equity.
7. Budget on screen ≤ the allowed size.
8. The plan says buy (`accumulate` or `hold_buy_dips`), not `wait` or `take_profit_wait`.
Verdict: any fail = **no entry**. All pass = the checklist allows the trade; it is still not a promise.

## 3. Recommended tools and strategies (labelled)
| Item | Label | Why / how |
|---|---|---|
| Limit orders at the buy levels (not market orders) | Discipline, not backtested | Fills at the planned price; no chasing |
| Staged buys 30/30/40 | Not evidence | Spreads the entry; cost is possibly missing the first move |
| Fixed-fraction risk (1%) | Rule of thumb | Limits damage from a losing streak |
| Weekly invalidation | Not evidence | Simple, rule-based exit; can cause whipsaws |
| Score alone for entries | **Already rejected** | Backtest 2026-11-06: score ≥ 35 was not better than chance. Use levels, not the score |
| Learning loop (`spot-learn.yml`) | Measurement only | Labels groups only at n ≥ 30 and t ≥ 3. Weights never change automatically |
| Trade journal in the Spot ledger | Measurement | Every fill and close logged, so real results can be checked |
| Alerts at levels | Tool, not a strategy | Lets you act at the level without watching the chart |

Not recommended: martingale / averaging down below the invalidation; using leverage on spot; sizing by feeling.

## 4. Open items (owner decides)
- The 1% / 25% / 20% / 3% numbers are safe defaults. Change them only with a reason, and they are not evidence either way.
- No strategy is validated on live data yet. Learn from the daily report for at least 30 outcomes per group before any claim.

## 5. Where the code is
- `modules/spot_checklist.py` (sizing, checklist, take-profit split) + `tests/test_spot_checklist.py` (11 groups, synthetic).
- `modules/spot_plan.py` (levels, actions), `modules/spot_core.py` (ladder, alerts), `modules/spot_page.py` (cards).
- Checklist and sizing are **not yet on the page**; wiring them in is the next step, after the layout work (section 6 of `docs/SPOT_LAYOUT.md`).
