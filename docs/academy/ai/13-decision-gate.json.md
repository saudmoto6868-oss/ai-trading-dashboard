# AI — Decision Gate (بوابة القرار)

```yaml
id: decision_gate
name_ar: بوابة القرار — مكتب القرار
name_en: Decision Gate — Decision Desk
role_in_system: decision
lab_status: meta_tool

branches:
  - id: gate_conditions
    title: Gate conditions — all four must pass
    rules_hard:
      - "1. Direction set: direction != neutral (bull or bear)"
      - "2. Stars >= 2 (out of 5 max)"
      - "3. Lab evidence not None (at least one signal with n >= 30)"
      - "4. No opposing signal (against == False)"
      - "ALL four must pass — one failure blocks the gate"
    rules_soft:
      - "Gate passing does not mean the trade will win — it means it meets minimum criteria"
      - "A tight stop and proper R:R are still required regardless of gate status"
    confirmations: ["HTF alignment adds conviction but is not in the gate itself"]
    invalidation: ["Any one condition failing blocks the entire gate"]

  - id: stars_meaning
    title: Stars — what they represent
    rules_hard:
      - "Stars come from scorer.aggregate (signal count + quality blend)"
      - "Max stars = 5; clamped at 5 even if more signals fire"
      - "Stars < 2 = too few / too weak signals for a gate pass"
    rules_soft:
      - "Stars >= 4 = strong conviction, but still requires direction + evidence"
    confirmations: []
    invalidation: []

  - id: opposing_signal
    title: Opposing signals — against flag
    rules_hard:
      - "against = True when a signal fires in the opposite direction to the setup"
      - "against blocks the gate AND applies a 0.10R penalty to lab evidence"
      - "The penalty is: evidence = mean_ev - 0.10R"
    rules_soft:
      - "Even one strong opposing signal should be taken seriously"
    confirmations: []
    invalidation: []

  - id: off_in_gate
    title: OFF signals in gate context
    rules_hard:
      - "OFF signals are excluded from stars and direction computation"
      - "OFF signals shown as warning but do not block the gate by themselves"
      - "If all signals are OFF, evidence = None → gate blocked by condition 3"
    rules_soft:
      - "OFF signals are informational — trader decides how to weigh them"
    confirmations: []
    invalidation: []

  - id: htf_confirmation
    title: HTF confirmation — extra conviction layer
    rules_hard:
      - "HTF data shown separately after gate result"
      - "HTF not in gate conditions — it is bonus confirmation only"
      - "HTF unavailable is shown as 'no data', not as a block"
    rules_soft:
      - "Trade in direction of HTF trend when possible"
    confirmations: []
    invalidation: []

setups:
  - id: use_decision_desk
    direction: any
    name: Use Decision Desk before every entry
    context: "You have a Workspace scan result and are considering an entry"
    entry_conditions:
      - "Run scan on Workspace (or Scanner page)"
      - "Open Stats → Decision Desk tab"
      - "Check gate status: ✅ Passes gate"
    entry_trigger: "Gate passes AND HTF aligned (optional but preferred)"
    stop_rule: "Gate blocked → do not enter; understand which condition failed"
    targets: ["Use scenarios from Decision Desk as pre-planned trade management"]
    confirmations: ["Stars >= 3", "Positive lab evidence", "HTF trend agrees"]
    invalidation: [
      "direction = neutral",
      "stars < 2",
      "evidence = None",
      "against = True"
    ]

notes:
  honest_disclaimer: >
    Gate passing means minimum criteria met — it is not a guarantee of profit.
    Stars and lab evidence are derived from historical IS data.
    Final trade decision, sizing, and risk management belong to the trader.
  not_investment_advice: true
```
