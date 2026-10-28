# AI — Calibration Lab (معايرة الانحلال)

```yaml
id: calibration
name_ar: معايرة الانحلال — IS vs OOS
name_en: Calibration Lab — In-Sample vs Out-of-Sample
role_in_system: analytics
lab_status: meta_tool

branches:
  - id: is_oos_concept
    title: IS vs OOS — what overfit looks like
    rules_hard:
      - "IS (in-sample) = data used to discover/tune the signal"
      - "OOS (out-of-sample) = data the signal never saw during tuning"
      - "If IS avgR >> OOS avgR (gap > 0.05R), flag as potential overfit"
      - "Gap <= 0.05R = calibrated (✅ consistent)"
      - "Gap > 0.05R = overfit warning (⚠️ degrades)"
    rules_soft:
      - "A signal with no OOS rows cannot be assessed for overfit — show honestly"
      - "Some decay is expected; extreme gap (> 0.20R) is a red flag"
    confirmations: ["Consistent IS≈OOS across multiple TFs strengthens the case"]
    invalidation: ["Fewer than 30 OOS trades makes OOS estimate unreliable"]

  - id: per_tf_breakdown
    title: Performance breakdown by timeframe
    rules_hard:
      - "Each row in strategy_lab.json is one (key, tf, side) combination"
      - "Sorting by avgR across TFs shows where the signal works best"
      - "TF with n < 30 shown but marked as insufficient"
    rules_soft:
      - "A signal strong in 1h may be weak in 15m — use the relevant TF"
    confirmations: []
    invalidation: []

  - id: no_date_fields
    title: Limitation — no time-series decay possible
    rules_hard:
      - "strategy_lab.json has no date column — true time decay cannot be computed"
      - "IS vs OOS gap is a proxy, not a true decay curve"
    rules_soft:
      - "Adding trade timestamps in a future lab version would enable real decay analysis"
    confirmations: []
    invalidation: []

setups:
  - id: check_before_sizing
    direction: any
    name: Check calibration before increasing position size
    context: "You want to upsize on a signal with good IS performance"
    entry_conditions:
      - "Open Calibration tab on Stats page"
      - "Check IS vs OOS gap for your signal"
    entry_trigger: "Gap <= 0.05R — signal appears calibrated"
    stop_rule: "Gap > 0.05R — treat OOS avgR as your expectation, not IS"
    targets: ["Size to OOS avgR expectation, not IS"]
    confirmations: ["Consistent per-TF table with no outlier TF"]
    invalidation: ["No OOS data — cannot assess calibration"]

notes:
  honest_disclaimer: >
    IS vs OOS gap is a necessary but not sufficient test for overfit.
    A consistent gap across all TFs is more informative than a single TF gap.
    Without timestamps, true time-based decay analysis is not available.
  not_investment_advice: true
```
