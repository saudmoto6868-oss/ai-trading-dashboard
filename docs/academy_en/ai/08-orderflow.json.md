# AI — Order Flow (detailed)

```yaml
id: orderflow
name_en: Order Flow
role_in_system: execution_gate
lab_status: candidate

branches:
  - id: hierarchy
    title: Reliability hierarchy
    rules_hard:
      - "Prefer Time&Sales / aggressor prints over resting DOM size"
      - "Pulled liquidity != support"
    rules_soft:
      - "Rank: Tape > Delta/Footprint > Gauge > LimitTrack > DOM walls"
    confirmations: []
    invalidation: []

  - id: absorption
    title: Absorption
    rules_hard:
      - "Absorption candidate: high opposing volume at level with limited price progress over W window"
      - "Must co-locate with preset chart level from parent school"
    rules_soft:
      - "Then require delta flip or hold for entry"
    confirmations: ["Level from levels/sessions"]
    invalidation: ["Price closes through level with rising aggressor pressure"]

  - id: delta
    title: Delta conventions
    rules_hard:
      - "delta = aggressive buy volume - aggressive sell volume; sign convention documented"
    rules_soft:
      - "CVD divergence at level is confirmation not standalone signal"
    confirmations: []
    invalidation: []

  - id: limit_track_dom
    title: Limit track DOM
    rules_hard:
      - "Track PLACED/PULLED/FILLED separately"
      - "Snapshot interval known (e.g. ~20s) — do not overfit micro changes"
    rules_soft: ["Refresh after pull more meaningful than single wall"]
    confirmations: []
    invalidation: []

setups:
  - id: of_long_absorption_at_level
    direction: long
    name: Absorption at demand
    context: "Parent long level active"
    entry_conditions:
      - "At demand level"
      - "Absorption criteria true"
      - "Delta non-negative or flipping up"
    entry_trigger: "Hold above level + gauge optional green"
    stop_rule: "Below level"
    targets: ["Parent targets"]
    confirmations: ["Tape speed slows on sells"]
    invalidation_price_rule: "Close below level"
    research_option: R6
    detector_hint: "absorption"

  - id: of_short_absorption_at_level
    direction: short
    name: Absorption at supply
    entry_conditions: ["At supply", "Buy absorption", "Delta flipping down"]
    entry_trigger: "Hold below level"
    stop_rule: "Above level"
    targets: ["Parent"]
    invalidation_price_rule: "Close above level"
    detector_hint: "absorption"

  - id: of_long_delta_thrust
    direction: long
    name: Delta thrust continuation
    context: "Trend day parent long; pullback to VWAP/level"
    entry_conditions:
      - "Pullback with weak counter delta"
      - "Thrust delta resumes with price"
    entry_trigger: "Resume bar"
    stop_rule: "Below pullback low"
    targets: ["Session extreme"]
    invalidation_price_rule: "Close below pullback low"
    detector_hint: null

development_notes:
  - "No OF-only Grade path in academy policy"
  - "Crypto/FX synthetic delta quality differs from futures footprint"
  - "Journal every OF-tagged trade for R6"
```
