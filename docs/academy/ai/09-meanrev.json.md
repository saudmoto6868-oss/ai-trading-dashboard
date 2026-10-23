# AI — Mean Reversion (مفصّل)

```yaml
id: meanrev
name_ar: العودة للمتوسط
name_en: Mean Reversion
role_in_system: separate_system
lab_status: candidate

branches:
  - id: regime_gate
    title: Regime gate
    rules_hard:
      - "Enable only when regime_flag == range (e.g. ADX(14) < threshold T or price inside Donchian width percentile)"
      - "Disable entire MR book when regime_flag == trend"
    rules_soft:
      - "External evidence: MR + Trend portfolio improves MAR when both funded separately"
    confirmations: []
    invalidation: ["Regime flips to trend mid-trade — optional early exit rule"]

  - id: range_geometry
    title: Range geometry
    rules_hard:
      - "Range high/low from last confirmed pivots or rolling W-day max/min with acceptance rule"
    rules_soft: ["Midpoint and VWAP as first targets"]
    confirmations: []
    invalidation: ["Accepted close outside range"]

  - id: oscillators
    title: Oscillators
    rules_hard:
      - "RSI length and thresholds fixed before test (e.g. 2-period or 14-period — pick one family)"
    rules_soft: ["Band touch + oscillator better than oscillator alone"]
    confirmations: []
    invalidation: []

setups:
  - id: meanrev_long_range_low
    direction: long
    name: Range low exhaustion long
    context: "regime_flag range"
    entry_conditions:
      - "regime_flag == range"
      - "Price at range low band"
      - "Oscillator oversold per fixed params"
    entry_trigger: "Close back inside range"
    stop_rule: "Below range low - buffer"
    targets: ["Mid", "VWAP", "Range high partial"]
    confirmations: ["Optional OF absorption"]
    invalidation_price_rule: "Close below range low with follow-through"
    research_option: R3
    detector_hint: null

  - id: meanrev_short_range_high
    direction: short
    name: Range high exhaustion short
    entry_conditions: ["regime range", "At range high", "Overbought"]
    entry_trigger: "Close back inside"
    stop_rule: "Above range high + buffer"
    targets: ["Mid", "Range low"]
    invalidation_price_rule: "Close above range high with follow-through"
    detector_hint: null

  - id: meanrev_long_bb
    direction: long
    name: Bollinger lower band in range
    entry_conditions: ["regime range", "Close below lower BB then close back above"]
    entry_trigger: "Reentry close"
    stop_rule: "Below recent extreme"
    targets: ["Middle band"]
    invalidation_price_rule: "New low after entry"
    detector_hint: null

development_notes:
  - "Never merge MR signals into trend Grade without portfolio layer"
  - "Research R10 after R1 and R3 stable"
  - "Expect higher win rate lower payoff than trend"
```
