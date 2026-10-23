# AI — Levels / Price Action

```yaml
id: levels
name_ar: مستويات وحركة سعرية
name_en: Levels Price Action
role_in_system: primary
lab_status: primary_candidate
setups:
  - id: levels_long_pullback
    direction: long
    name: Trend pullback to broken level
    context: "HH/HL structure; level broken and retested"
    entry_conditions:
      - "Uptrend structure intact"
      - "Price in demand zone at prior resistance-turned-support"
    entry_trigger: "Bullish pin or engulfing at zone; enter above signal bar"
    stop_rule: "Below signal bar and zone"
    targets: ["Prior swing high", "1.5R–2R"]
    confirmations: ["Level previously respected", "lighter volume on pullback"]
    invalidation_price_rule: "Close below zone"
    example:
      points: { level: 100, break_high: 103, entry_zone: 100.5, stop: 99.8 }
    detector_hint: "level"
  - id: levels_short_pullback
    direction: short
    name: Trend pullback to resistance
    context: "LL/LH; retest of broken support as resistance"
    entry_trigger: "Bearish pin/engulfing at zone"
    stop_rule: "Above zone"
    targets: ["Prior swing low", "1.5R–2R"]
    invalidation_price_rule: "Close above zone"
    detector_hint: "level"
```
