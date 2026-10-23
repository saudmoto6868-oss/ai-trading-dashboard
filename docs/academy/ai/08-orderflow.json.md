# AI — Order Flow

```yaml
id: orderflow
name_ar: تدفق الأوامر
name_en: Order Flow
role_in_system: execution_gate
lab_status: candidate

branches:
  - id: tape
    title: Time and Sales
    rules_hard:
      - "Prefer actual prints over resting DOM size"
    rules_soft:
      - "Speed and size clusters matter near pre-defined level"
    confirmations: ["Aggressive buys into support hold"]
    invalidation: ["Aggressive sells breaking level"]

  - id: delta_footprint
    title: Delta and footprint
    rules_hard:
      - "Delta sign convention fixed in code"
    rules_soft:
      - "Absorption: large opposing volume, little price progress"
    confirmations: ["Delta divergence vs price at level"]
    invalidation: ["Delta and price both break level"]

  - id: dom_limit_track
    title: DOM and limit track
    rules_hard:
      - "Pulled liquidity is not filled liquidity"
    rules_soft:
      - "Snapshots lag; do not treat single wall as truth"
    confirmations: ["Refresh after pull still holds"]
    invalidation: ["Wall pulled and price through"]

setups:
  - id: of_long_absorption_at_level
    direction: long
    name: Absorption at preset demand
    context: "Level from Levels/Sessions already valid; OF is gate"
    entry_conditions:
      - "Price at demand level"
      - "Selling absorbed (tape/delta) without new low close"
    entry_trigger: "Delta flips up or gauge positive + price holds"
    stop_rule: "Below level"
    targets: ["From parent setup"]
    confirmations:
      - "Limit track: bids refill not only pull"
    invalidation_price_rule: "Close below level"
    example:
      narrative: "No standalone OF scalp without level in this academy policy"
    risk_notes: "Crypto/FX feed quality varies"
    detector_hint: "absorption"

  - id: of_short_absorption_at_level
    direction: short
    name: Absorption at preset supply
    context: "Preset resistance"
    entry_conditions:
      - "Buying absorbed at level"
    entry_trigger: "Delta flips down; hold below level"
    stop_rule: "Above level"
    targets: ["From parent setup"]
    confirmations: []
    invalidation_price_rule: "Close above level"
    example:
      narrative: "Mirror"
    detector_hint: "absorption"
```
