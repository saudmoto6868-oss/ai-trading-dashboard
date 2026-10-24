# AI — Harmonic

```yaml
id: harmonic
name_ar: توافقي
name_en: Harmonic
role_in_system: context
lab_status: unproven

branches:
  - id: xabcd
    title: XABCD and PRZ
    rules_hard:
      - "Pattern is five points X-A-B-C-D"
      - "Trade reaction at D/PRZ requires price confirmation; ratios alone are not an entry"
    rules_soft:
      - "C typically 0.382–0.886 of AB"
    confirmations:
      - "Rejection at PRZ"
      - "Confluence with level/liquidity"
    invalidation:
      - "Break of X for internal patterns (Gartley/Bat) or PRZ invalidation rule for extended patterns"

patterns:
  gartley:
    ab_xa: 0.618
    d_xa: 0.786
    d_vs_x: inside
  bat:
    ab_xa: [0.382, 0.50]
    d_xa: 0.886
    d_vs_x: inside
  butterfly:
    ab_xa: 0.786
    d_xa: 1.272   # some allow to 1.618
    d_vs_x: beyond
  crab:
    ab_xa: [0.382, 0.618]
    d_xa: 1.618
    d_vs_x: beyond

setups:
  - id: harmonic_gartley_long
    direction: long
    name: Bullish Gartley at D
    context: "Completed bullish Gartley ratios into PRZ"
    entry_conditions:
      - "B ~0.618 XA; D ~0.786 XA; D does not break X"
      - "Price in PRZ at D"
    entry_trigger: "Bullish rejection candle or micro structure shift at D"
    stop_rule: "Below X (or below D swing low if tighter policy)"
    targets:
      - "0.382 retracement of AD"
      - "0.618 retracement of AD"
      - "Optional C / A"
    confirmations: ["Rejection", "optional divergence"]
    invalidation_price_rule: "Close below X"
    example:
      points: { X: 100, A: 80, B: 92.4, D: 84.3 }
      narrative: "Long PRZ near 84.3; stop under 100"
    risk_notes: "Ratio tolerance needed in code; define epsilon"
    detector_hint: "harmonic_gartley"

  - id: harmonic_gartley_short
    direction: short
    name: Bearish Gartley at D
    context: "Mirror of bullish Gartley"
    entry_conditions:
      - "Same ratios inverted"
    entry_trigger: "Bearish rejection at D"
    stop_rule: "Above X"
    targets: ["0.382 AD", "0.618 AD"]
    confirmations: ["Rejection"]
    invalidation_price_rule: "Close above X"
    example:
      narrative: "Short at bearish D PRZ"
    risk_notes: "Mirror"
    detector_hint: "harmonic_gartley"

  - id: harmonic_bat_long
    direction: long
    name: Bullish Bat at D
    entry_conditions:
      - "B in 0.382–0.50 XA; D ~0.886 XA; D inside X"
    entry_trigger: "Rejection at D"
    stop_rule: "Below X"
    targets: ["0.382 AD", "0.618 AD"]
    confirmations: ["Rejection"]
    invalidation_price_rule: "Close below X"
    example:
      narrative: "Deeper D than Gartley"
    detector_hint: "harmonic_bat"

  - id: harmonic_butterfly_long
    direction: long
    name: Bullish Butterfly at D beyond X
    entry_conditions:
      - "B ~0.786 XA; D ~1.272 XA extension beyond X"
    entry_trigger: "Rejection at PRZ"
    stop_rule: "Beyond D/PRZ by rule or ATR buffer (not merely X)"
    targets: ["0.382 AD", "0.618 AD"]
    confirmations: ["Strong rejection"]
    invalidation_price_rule: "Close beyond stop side of PRZ"
    example:
      narrative: "Extended pattern; wider stop"
    detector_hint: "harmonic_butterfly"

  - id: harmonic_crab_long
    direction: long
    name: Bullish Crab at 1.618 XA
    entry_conditions:
      - "D at 1.618 XA"
    entry_trigger: "Rejection at PRZ"
    stop_rule: "Beyond D with buffer"
    targets: ["0.382 AD", "0.618 AD"]
    confirmations: ["Rejection"]
    invalidation_price_rule: "Close beyond stop"
    example:
      narrative: "Rarest; largest extension"
    detector_hint: "harmonic_crab"
```

**Code note:** Evaluate each pattern id separately in Lab; never pool all harmonics into one statistic.
