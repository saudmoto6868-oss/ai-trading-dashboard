# AI — Liquidity / Sessions

```yaml
id: sessions
name_ar: السيولة والجلسات
name_en: Liquidity and Sessions
role_in_system: timing
lab_status: candidate

branches:
  - id: asia_range
    title: Asia range build
    rules_hard:
      - "Asia high/low defined by session clock (project timezone fixed)"
    rules_soft:
      - "Range often liquidity pool for London"
    confirmations: []
    invalidation: []

  - id: sweep
    title: Liquidity sweep
    rules_hard:
      - "Sweep = trade beyond prior high/low then close back inside (define wick/close rule in code)"
    rules_soft:
      - "Best when aligns with HTF bias"
    confirmations:
      - "Displacement after sweep"
      - "Optional OF absorption"
    invalidation:
      - "Continued close beyond swept level against planned reversal"

  - id: kill_zones
    title: Session kill zones
    rules_hard:
      - "Timestamps in one timezone (e.g. America/New_York)"
    rules_soft:
      - "London open and London-NY overlap = higher activity windows"
    confirmations: []
    invalidation: []

setups:
  - id: session_long_asia_sweep
    direction: long
    name: Sweep Asia low then reclaim
    context: "London session; HTF not strongly bearish"
    entry_conditions:
      - "Asia low taken out by wick or brief trade"
      - "Close back above Asia low"
    entry_trigger: "Close reclaim OR micro BOS up after sweep"
    stop_rule: "Below sweep extreme"
    targets:
      - "Asia high"
      - "Prior day high / measured range"
    confirmations:
      - "In London or London-NY window preferred"
      - "Optional positive delta after sweep"
    invalidation_price_rule: "Close back below sweep low"
    example:
      points: { asia_low: 100, sweep: 99.6, entry: 100.2, stop: 99.5 }
      narrative: "Classic Judas/sweep narrative simplified"
    risk_notes: "Session filter is timing not edge alone"
    detector_hint: "liqline"

  - id: session_short_asia_sweep
    direction: short
    name: Sweep Asia high then reject
    context: "London; HTF not strongly bullish"
    entry_conditions:
      - "Asia high swept then close back below"
    entry_trigger: "Close below Asia high after sweep"
    stop_rule: "Above sweep extreme"
    targets: ["Asia low", "prior day low"]
    confirmations: ["London window"]
    invalidation_price_rule: "Close above sweep high"
    example:
      narrative: "Mirror long"
    detector_hint: "liqline"

  - id: session_timing_filter_only
    direction: long
    name: Timing filter (not standalone trade)
    context: "Any setup from other schools"
    entry_conditions:
      - "Current time inside allowed kill zone list"
    entry_trigger: "N/A — AND with other setup"
    stop_rule: "From parent setup"
    targets: ["From parent setup"]
    confirmations: []
    invalidation_price_rule: "N/A"
    example:
      narrative: "Use as conjunction filter in Decision Chain Timing layer"
    detector_hint: null
```
