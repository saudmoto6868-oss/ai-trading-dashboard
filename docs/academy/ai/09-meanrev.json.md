# AI — Mean Reversion

```yaml
id: meanrev
name_ar: العودة للمتوسط
name_en: Mean Reversion
role_in_system: separate_system
lab_status: candidate

branches:
  - id: range_regime
    title: Range regime filter
    rules_hard:
      - "Mean-reversion book disabled when trend regime flag on (e.g. ADX high / Donchian expansion)"
    rules_soft:
      - "Works best inside defined range highs/lows"
    confirmations: []
    invalidation: ["Regime flip to trend"]

  - id: oscillators
    title: Oscillator extremes
    rules_hard:
      - "Fixed thresholds (e.g. RSI period and levels) before Lab"
    rules_soft:
      - "Combine with band touch not RSI alone"
    confirmations: ["Price at range boundary"]
    invalidation: ["Close outside range with momentum"]

setups:
  - id: meanrev_long_range_low
    direction: long
    name: Buy range low exhaustion
    context: "ADX low / ranging; clear range low"
    entry_conditions:
      - "Regime = range"
      - "Price at or slightly beyond range low"
      - "RSI (or chosen oscillator) oversold per fixed param"
    entry_trigger: "Reversal candle back inside range"
    stop_rule: "Below range low by buffer or ATR fraction"
    targets:
      - "Range midpoint or VWAP"
      - "Range high partial"
    confirmations: ["Optional OF absorption"]
    invalidation_price_rule: "Close below range low with follow-through"
    example:
      points: { range_low: 100, range_high: 110, mid: 105, entry: 100.5 }
      narrative: "Separate system from trend book"
    risk_notes: "Do not run full size trend + meanrev same symbol without hedge policy"
    detector_hint: null

  - id: meanrev_short_range_high
    direction: short
    name: Sell range high exhaustion
    context: "Range regime"
    entry_conditions:
      - "At range high + oscillator overbought"
    entry_trigger: "Rejection back inside"
    stop_rule: "Above range high"
    targets: ["Mid", "range low"]
    confirmations: []
    invalidation_price_rule: "Close above range high with follow-through"
    example:
      narrative: "Mirror"
    detector_hint: null
```
