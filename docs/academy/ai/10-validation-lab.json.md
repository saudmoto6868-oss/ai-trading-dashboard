# AI — Validation Lab (مختبر التحقق)

```yaml
id: validation_lab
name_ar: مختبر التحقق من الكاشفات
name_en: Validation Lab — Signal Evidence
role_in_system: analytics
lab_status: meta_tool

branches:
  - id: evidence_tiers
    title: Evidence tiers — how signals are graded
    rules_hard:
      - "n < 30 trades = not evidence; label shown dimmed, no tier assigned"
      - "n >= 300 AND avgR <= -0.06 = OFF; signal excluded from scoring"
      - "avgR > 0.0 AND n >= 30 = positive or edge (see edge rule)"
      - "edge requires avgR >= 0.10 AND n >= 100 (configurable)"
    rules_soft:
      - "A positive signal in one TF is not positive in all TFs"
      - "Lab is historical; forward performance may differ"
    confirmations: ["n >= 30 on the exact TF or the mapped TF"]
    invalidation: ["n < 30 — insufficient sample"]

  - id: off_signals
    title: OFF signals — excluded from scoring
    rules_hard:
      - "OFF = n >= 300 AND avgR <= -0.06 across all timeframes (side==all)"
      - "OFF signals still appear on charts as information"
      - "OFF signals are NOT subtracted from score; they are simply excluded"
    rules_soft:
      - "OFF status is recomputed every time lab file is updated; nothing is hardcoded"
    confirmations: []
    invalidation: ["Lab file update may change OFF set"]

  - id: tf_mapping
    title: Timeframe mapping for lab lookup
    rules_hard:
      - "Each chart TF maps to a lab TF: 13m→15m, 2h→1h, 3h→4h, 12h→1d etc."
      - "If no row for mapped TF, fallback to 'all' TF row"
      - "If fallback row also n<30, result is None (no evidence)"
    rules_soft:
      - "Use the mapped TF; do not mix TF rows in one evidence value"
    confirmations: []
    invalidation: []

setups:
  - id: validate_before_trade
    direction: any
    name: Check lab evidence before entry
    context: "Signal fired on any instrument"
    entry_conditions:
      - "Open Validation Lab tab on Stats page"
      - "Filter by your signal's school and TF"
    entry_trigger: "Signal tier = edge ⭐ or positive ✅"
    stop_rule: "Do not proceed if tier = off 🚫 or n < 30 (dimmed)"
    targets: ["Use avgR as expected value input for position sizing"]
    confirmations: ["HTF same tier or neutral"]
    invalidation: ["Signal tier negative ⚠️ — treat as headwind"]

notes:
  honest_disclaimer: >
    Lab results are in-sample (IS) unless OOS fields are present.
    IS avgR overstates expected forward performance.
    n < 30 is not evidence — shown for transparency only.
  not_investment_advice: true
```
