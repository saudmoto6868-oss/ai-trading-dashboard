# AI — Gann (Jan)

```yaml
id: gann
name_ar: جان
name_en: Gann
role_in_system: context
lab_status: unproven

branches:
  - id: fan_angles
    title: Gann Fan angles
    rules_hard:
      - "Anchor exactly on swing high or low; do not move anchor after draw"
      - "1x1 is the reference balance rate of price per time for the chosen scale"
    rules_soft:
      - "Price often migrates angle-to-angle (e.g. 1x1 break toward 1x2)"
      - "Above rising 1x1 = relative strength; below = relative weakness"
    confirmations:
      - "Rejection candle at angle"
      - "Confluence with horizontal level or Sq9 level"
    invalidation:
      - "Sustained close beyond angle against the trade thesis"

  - id: square_of_nine
    title: Square of Nine levels
    rules_hard: []
    rules_soft:
      - "Levels from sqrt rotations of a pivot price are candidate S/R only"
      - "Require price reaction confirmation"
    confirmations: ["Touch + rejection", "overlap with classic level"]
    invalidation: ["Close through level against thesis with follow-through"]

setups:
  - id: gann_long_1x1_bounce
    direction: long
    name: Bounce from rising 1x1
    context: "Major swing low anchor; rising fan; HTF not strongly opposed"
    entry_conditions:
      - "Price pulls to rising 1x1 from above"
      - "Anchor fixed at swing low"
    entry_trigger: "Bullish rejection at 1x1 (close back above) or buy stop above rejection high"
    stop_rule: "Below swing low anchor OR below 1x1 by small ATR buffer"
    targets: ["Next steeper angle 2x1", "prior swing high", "Sq9 level"]
    confirmations: ["Rejection candle", "optional volume/OF"]
    invalidation_price_rule: "Sustained close below 1x1 and failure to reclaim"
    example:
      points: { anchor_low: 100 }
      narrative: "Illustrative: hold 1x1 uptrend line from 100"
    risk_notes: "Scale/timeframe sensitive; wrong scale breaks tool"
    detector_hint: null

  - id: gann_short_1x1_bounce
    direction: short
    name: Rejection from falling 1x1
    context: "Major swing high anchor; falling fan"
    entry_conditions:
      - "Price rallies into falling 1x1 from below"
    entry_trigger: "Bearish rejection at 1x1"
    stop_rule: "Above swing high OR above 1x1"
    targets: ["1x2", "prior swing low"]
    confirmations: ["Rejection candle"]
    invalidation_price_rule: "Sustained close above 1x1"
    example:
      points: { anchor_high: 120 }
      narrative: "Short rejection at descending 1x1 from 120"
    risk_notes: "Mirror of long"
    detector_hint: null

  - id: gann_short_1x1_break
    direction: short
    name: Break down through rising 1x1
    context: "Was supported by 1x1; loses it"
    entry_conditions:
      - "Close below rising 1x1 after prior respect"
    entry_trigger: "Close below 1x1 or retest failed"
    stop_rule: "Above recent swing high or back above 1x1"
    targets: ["1x2 angle", "horizontal support"]
    confirmations: ["Follow-through bar"]
    invalidation_price_rule: "Close back above 1x1"
    example:
      narrative: "Angle-to-angle migration down"
    risk_notes: "False breaks common; wait close"
    detector_hint: null
```
