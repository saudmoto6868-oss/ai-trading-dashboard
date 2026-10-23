# AI — Sessions / Liquidity (detailed)

```yaml
id: sessions
name_en: Liquidity Sessions
role_in_system: timing
lab_status: candidate

branches:
  - id: clock
    title: Session clock
    rules_hard:
      - "Single timezone for all rules (recommend America/New_York)"
      - "Asia/London/NY bounds stored as config not magic numbers in detectors"
    rules_soft:
      - "Approx NY: Asia 18:00-00:00, London 03:00-12:00, NY 08:00-17:00; refine per desk"
      - "Kill zones: London open window; NY AM; overlap"
    confirmations: []
    invalidation: []

  - id: asia_range
    title: Asia range
    rules_hard:
      - "Asia high = max high in Asia window; Asia low = min low"
    rules_soft:
      - "Narrow Asia range often precedes larger London move — optional filter"
    confirmations: []
    invalidation: []

  - id: sweep_mechanics
    title: Sweep definition
    rules_hard:
      - "Sweep: price beyond level by at least 1 tick/pip then close back inside within K bars OR same bar wick beyond with close inside"
      - "Choose ONE definition and never mix in same Lab run"
    rules_soft:
      - "Marketing win rates 70-80% unsupported; expect modest PF if any"
    confirmations: ["Displacement after reclaim"]
    invalidation: ["Accepted break: closes beyond level"]

setups:
  - id: session_long_asia_sweep
    direction: long
    name: Sweep Asia low reclaim
    context: "London; optional HTF filter not strongly bearish"
    entry_conditions:
      - "Asia low swept per hard definition"
      - "Close back above Asia low"
    entry_trigger: "Reclaim close or micro BOS up"
    stop_rule: "Below sweep extreme"
    targets: ["Asia high", "PDH", "1.5R"]
    confirmations: ["In London or overlap window"]
    invalidation_price_rule: "Close below sweep low"
    example:
      points: { asia_low: 100, sweep: 99.6, entry: 100.2, stop: 99.5, asia_high: 101.5 }
    detector_hint: "liqline"
    research_option: R4

  - id: session_short_asia_sweep
    direction: short
    name: Sweep Asia high reject
    entry_conditions: ["Asia high swept", "Close back below"]
    entry_trigger: "Reject close"
    stop_rule: "Above sweep high"
    targets: ["Asia low", "PDL"]
    invalidation_price_rule: "Close above sweep high"
    detector_hint: "liqline"

  - id: session_timing_and
    direction: long
    name: Timing AND filter
    context: "Parent setup from levels/trend"
    entry_conditions: ["Now in allowed session list"]
    entry_trigger: "Parent trigger"
    stop_rule: "Parent"
    targets: ["Parent"]
    invalidation_price_rule: "Parent"
    detector_hint: null
    development_notes: ["Decision Chain Timing layer only"]

development_notes:
  - "Never trade session clock alone"
  - "Log session tag on every journal row for later split stats"
```
