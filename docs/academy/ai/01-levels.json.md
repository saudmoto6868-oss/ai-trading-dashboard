# AI — Levels / Price Action (مفصّل)

```yaml
id: levels
name_ar: مستويات وحركة سعرية
name_en: Levels Price Action
role_in_system: primary
lab_status: primary_candidate

branches:
  - id: market_structure
    title: Market structure HH HL LL LH
    rules_hard:
      - "Swing definition fixed in code (e.g. fractal length or pivot strength)"
      - "Uptrend requires higher highs and higher lows by that definition"
    rules_soft:
      - "Break of structure against trend warns; wait for new structure before flipping bias"
    confirmations: ["HTF alignment"]
    invalidation: ["Opposite structure sequence completes"]

  - id: horizontal_zones
    title: Support resistance zones
    rules_hard:
      - "Zone from at least N touches or break-and-retest event (N fixed)"
      - "Zone has high and low bound not single tick line only"
    rules_soft:
      - "Fresh zones after break often cleaner than 10-year lines"
    confirmations: ["Prior reaction", "round numbers optional"]
    invalidation: ["Full close through zone with follow-through"]

  - id: candlestick_at_level
    title: Candle signals only at level
    rules_hard:
      - "Pin/engulfing/inside ignored if not intersecting active zone"
    rules_soft:
      - "Rejection wick >= body multiple optional filter"
    confirmations: ["Close back inside zone for pins"]
    invalidation: ["Close beyond zone"]

  - id: failed_breakout
    title: Failed breakout fakey
    rules_hard:
      - "Break beyond level then close back inside within K bars"
    rules_soft:
      - "Often aligns with liquidity grab narrative"
    confirmations: ["Volume spike on false break optional"]
    invalidation: ["Second close outside level"]

setups:
  - id: levels_long_pullback
    direction: long
    name: Trend pullback to support
    context: "HH/HL; demand zone active"
    entry_conditions:
      - "Uptrend structure intact"
      - "Price inside demand zone"
    entry_trigger: "Bullish pin or engulfing; enter above signal bar high"
    stop_rule: "Below zone low and signal bar low"
    targets: ["Prior HH", "1.5R", "2R"]
    confirmations: ["Lighter pullback volume optional", "HTF bullish"]
    invalidation_price_rule: "Close below zone"
    example:
      points: { zone_low: 100, zone_high: 101, entry: 100.8, stop: 99.6, t1: 103 }
    detector_hint: "level"
    research_option: R2

  - id: levels_short_pullback
    direction: short
    name: Trend pullback to resistance
    context: "LL/LH"
    entry_conditions: ["Downtrend intact", "Price in supply zone"]
    entry_trigger: "Bearish pin/engulfing; enter below signal bar"
    stop_rule: "Above zone high"
    targets: ["Prior LL", "1.5R"]
    invalidation_price_rule: "Close above zone"
    detector_hint: "level"

  - id: levels_long_break_retest
    direction: long
    name: Breakout retest long
    context: "Close above resistance; wait retest"
    entry_conditions:
      - "Breakout close beyond resistance"
      - "Retest holds as support"
    entry_trigger: "Rejection at retest or close resume up"
    stop_rule: "Below retest low"
    targets: ["Measured move", "next level"]
    invalidation_price_rule: "Close back below broken level"
    example:
      points: { level: 100, break: 101, retest: 100.2, stop: 99.5 }
    detector_hint: "ohl_break"

  - id: levels_short_failed_break
    direction: short
    name: Failed breakout short
    context: "Attempted break above resistance fails"
    entry_conditions:
      - "Trade above level then close back below within K bars"
    entry_trigger: "Close back inside"
    stop_rule: "Above failed break high"
    targets: ["Opposite side of range"]
    invalidation_price_rule: "Close above failed high"
    detector_hint: null

development_notes:
  - "Fix pivot length before any Lab run"
  - "Prefer zones over exact prices for FX/gold noise"
  - "Compare break-retest vs pin-only in FILTER_COMPARE style tests"
```
