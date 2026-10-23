# AI — SMC / ICT

```yaml
id: smc
name_ar: مفاهيم المال الذكي
name_en: SMC ICT
role_in_system: context
lab_status: unproven

branches:
  - id: structure
    title: BOS / CHoCH
    rules_hard:
      - "BOS and CHoCH definitions must be code-fixed (swing length, close vs wick)"
    rules_soft:
      - "CHoCH warns regime shift; BOS continues"
    confirmations: []
    invalidation: ["Opposite structure break"]

  - id: order_block_fvg
    title: Order block and FVG
    rules_hard:
      - "OB/FVG geometry defined in code; zone must be unmitigated per rule"
    rules_soft:
      - "Prefer confluence with HTF discount/premium"
    confirmations:
      - "Reaction at zone"
      - "Prior sweep optional"
    invalidation:
      - "Full close through zone against thesis"

  - id: premium_discount
    title: Premium discount OTE
    rules_hard: []
    rules_soft:
      - "Longs preferred in discount; shorts in premium of dealing range"
      - "OTE ~0.62–0.79 retracement band optional"
    confirmations: []
    invalidation: []

setups:
  - id: smc_long_sweep_ob
    direction: long
    name: Sweep sell-side then demand OB/FVG
    context: "Bullish HTF or CHoCH up; price in discount"
    entry_conditions:
      - "Sell-side liquidity swept"
      - "Bullish BOS or displacement"
      - "Retrace into bullish OB or FVG"
    entry_trigger: "Rejection in zone or limit at zone midpoint"
    stop_rule: "Below zone and below sweep low"
    targets:
      - "Buy-side liquidity / prior high"
      - "1.5R minimum plan"
    confirmations:
      - "Discount location"
      - "Optional OF"
    invalidation_price_rule: "Close below OB/FVG zone"
    example:
      points: { sweep: 99.5, ob_low: 100, ob_high: 100.8, entry: 100.4 }
      narrative: "Illustrative only"
    risk_notes: "Subjective OB selection kills Lab; fix rules"
    detector_hint: null

  - id: smc_short_sweep_ob
    direction: short
    name: Sweep buy-side then supply OB/FVG
    context: "Bearish HTF; premium"
    entry_conditions:
      - "Buy-side swept"
      - "Bearish BOS"
      - "Rally into supply OB/FVG"
    entry_trigger: "Rejection in zone"
    stop_rule: "Above zone and sweep high"
    targets: ["Sell-side liquidity"]
    confirmations: ["Premium"]
    invalidation_price_rule: "Close above zone"
    example:
      narrative: "Mirror"
    detector_hint: null
```
