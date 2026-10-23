# AI — Elliott Wave

```yaml
id: elliott
name_ar: إليوت
name_en: Elliott Wave
role_in_system: context
lab_status: unproven

branches:
  - id: hard_rules
    title: Three cardinal rules
    rules_hard:
      - "Wave 2 never retraces beyond the origin of wave 1"
      - "Wave 3 is never the shortest among waves 1, 3, and 5"
      - "Wave 4 does not overlap wave 1 price territory in a standard impulse (diagonals excepted)"
    rules_soft: []
    confirmations: []
    invalidation:
      - "Any hard rule break voids the count"

  - id: impulse
    title: Motive 1-2-3-4-5
    rules_hard:
      - "Five-wave structure in trend direction"
      - "Wave 2 is never a triangle"
    rules_soft:
      - "Wave 3 often extends; often strongest volume"
      - "Wave 4 often 23.6–38.2% of wave 3"
      - "After wave 5 expect A-B-C"
    confirmations:
      - "Higher timeframe alignment"
      - "Wave 3 range/volume > wave 1"
      - "Optional RSI divergence into wave 5"
    invalidation:
      - "See hard_rules"

  - id: corrections
    title: Corrective patterns
    rules_hard: []
    rules_soft:
      - "Zigzag 5-3-5; Flat 3-3-5; Triangle 3-3-3-3-3"
      - "Complex W-X-Y possible"
    confirmations: []
    invalidation: []

setups:
  - id: elliott_long_wave3
    direction: long
    name: Long wave 3 after wave 2
    context: "HTF bullish; completed wave 1 up and wave 2 pullback on trading TF"
    entry_conditions:
      - "Valid 1-2 count; wave 2 has not broken wave 1 origin"
      - "Wave 2 preferably 50–61.8% retracement of wave 1"
    entry_trigger: "Break of minor corrective high inside wave 2 OR limit near 50% of wave 1"
    stop_rule: "Below wave 1 origin"
    targets:
      - "1.0 to 1.618 extension of wave 1 projected from end of wave 2"
    confirmations:
      - "Momentum candle or micro BOS"
      - "Optional positive order-flow at end of wave 2"
    invalidation_price_rule: "Close below wave 1 origin"
    example:
      symbol_notes: "Illustrative numbers only"
      points: { w1_start: 100, w1_end: 110, w2_end: 104, invalidation: 100 }
      narrative: "Buy continuation after wave 2 holds above 100; stop under 100"
    risk_notes: "Count error risk high; size from stop distance"
    detector_hint: null

  - id: elliott_short_wave3
    direction: short
    name: Short wave 3 after wave 2
    context: "HTF bearish; wave 1 down, wave 2 rally"
    entry_conditions:
      - "Wave 2 has not broken wave 1 origin (high)"
    entry_trigger: "Break of minor corrective low OR limit near 50% retrace of wave 1"
    stop_rule: "Above wave 1 origin"
    targets:
      - "1.0 to 1.618 extension of wave 1 down from end of wave 2"
    confirmations:
      - "Bearish momentum"
      - "Optional negative delta"
    invalidation_price_rule: "Close above wave 1 origin"
    example:
      points: { w1_start: 110, w1_end: 100, w2_end: 106, invalidation: 110 }
      narrative: "Short after failed wave 2 under 110"
    risk_notes: "Same as long mirror"
    detector_hint: null

  - id: elliott_fade_wave5_long
    direction: long
    name: Counter-trend long at end of bearish wave 5 (advanced)
    context: "Completed 5 down; seeking A-B-C up — higher risk"
    entry_conditions:
      - "Five down labeled without hard-rule break"
      - "Optional RSI bullish divergence into wave 5 low"
    entry_trigger: "Break above end of wave 4"
    stop_rule: "Below wave 5 low"
    targets: ["Wave A zone", "prior wave 4"]
    confirmations: ["Divergence", "reclaim of micro structure"]
    invalidation_price_rule: "Close below wave 5 low"
    example:
      points: { w5_low: 90, w4_high: 96 }
      narrative: "Only with HTF support; not default primary"
    risk_notes: "Counter-trend; reduce size"
    detector_hint: null
```
