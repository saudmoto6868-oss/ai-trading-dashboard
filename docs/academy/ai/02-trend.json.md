# AI — Trend / Turtle / TSMOM

```yaml
id: trend
name_ar: تتبع الاتجاه
name_en: Trend Following
role_in_system: primary
lab_status: primary_candidate

branches:
  - id: donchian_turtle
    title: Donchian / Turtle-style breakout
    rules_hard:
      - "Entry on close beyond N-day high/low (define N: 20 entry / 55 alternate; exit often 10 or 20 opposite)"
      - "Position size from volatility unit N = ATR(20); risk fixed fraction per unit"
    rules_soft:
      - "Pyramid limited units on favorable excursions"
      - "Accept low win rate; edge in fat right tail"
    confirmations:
      - "Daily or higher timeframe"
      - "No conflicting max correlation book limit"
    invalidation:
      - "Exit on opposite Donchian or trailing stop rule"

  - id: ma_trend
    title: Moving average trend
    rules_hard:
      - "Long only when fast MA > slow MA (params fixed before test)"
      - "Short only when fast MA < slow MA"
    rules_soft:
      - "Filter ADX or slope optional"
    confirmations: ["Price above/below both MAs"]
    invalidation: ["MA cross against position"]

  - id: tsmom
    title: Time-series momentum
    rules_hard:
      - "Signal from past return over lookback L; hold next period"
    rules_soft:
      - "Vol-scale position"
    confirmations: []
    invalidation: ["Signal flips"]

setups:
  - id: trend_long_turtle55
    direction: long
    name: Long 55-day breakout
    context: "Daily chart; trend-following book"
    entry_conditions:
      - "Close > highest high of prior 55 days"
    entry_trigger: "Close beyond 55-day high"
    stop_rule: "2 * ATR(20) below entry or below 20-day low per playbook"
    targets:
      - "Trail; no fixed TP required"
      - "Exit on close < 20-day low (classic variant)"
    confirmations:
      - "Optional: not into major HTF resistance without plan"
    invalidation_price_rule: "Exit rule hit"
    example:
      points: { entry_break: 110, atr20: 2.0, stop: 106 }
      narrative: "Illustrative unit sizing with N=2"
    risk_notes: "Whipsaw in ranges; disable or reduce in low ADX regime if policy says so"
    detector_hint: "turtle55"

  - id: trend_short_turtle55
    direction: short
    name: Short 55-day breakdown
    context: "Daily"
    entry_conditions:
      - "Close < lowest low of prior 55 days"
    entry_trigger: "Close beyond 55-day low"
    stop_rule: "2 * ATR(20) above entry or above 20-day high"
    targets: ["Trail / 20-day high exit"]
    confirmations: []
    invalidation_price_rule: "Exit rule hit"
    example:
      narrative: "Mirror long"
    detector_hint: "turtle55"

  - id: trend_long_sma
    direction: long
    name: Long SMA cross / stack
    context: "Daily; e.g. 10/40 style if in project"
    entry_conditions:
      - "Fast SMA > slow SMA"
    entry_trigger: "Cross up or first close while stacked"
    stop_rule: "Opposite cross or ATR stop"
    targets: ["Trail under swing / MA"]
    confirmations: ["Price above both"]
    invalidation_price_rule: "Fast < slow"
    example:
      narrative: "Params locked to Lab definition"
    detector_hint: "sma1040"
```
