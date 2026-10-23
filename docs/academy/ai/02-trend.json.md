# AI — Trend / Turtle / TSMOM (مفصّل)

```yaml
id: trend
name_ar: تتبع الاتجاه
name_en: Trend Following
role_in_system: primary
lab_status: primary_candidate

branches:
  - id: donchian_turtle
    title: Donchian Turtle
    rules_hard:
      - "Entry: close beyond prior N-day high/low (N in {20,55} locked per test)"
      - "Unit size from N_atr = ATR(20); stop distance often 2*N_atr"
      - "No discretionary skip of valid breakout unless coded filter"
    rules_soft:
      - "System 1 (20) more trades; System 2 (55) cleaner trends"
      - "Pyramid +0.5N up to max units if playbook allows"
      - "Original rules may underperform unmodified 2004–2026; test variants"
    confirmations: ["Daily+ timeframe"]
    invalidation: ["Exit on opposite channel or trailing rule"]

  - id: ma_stack
    title: Moving average trend
    rules_hard:
      - "Long when fast MA > slow MA; short when fast < slow; periods fixed"
    rules_soft: ["Price filter above both MAs"]
    confirmations: ["Slope optional"]
    invalidation: ["Cross against"]

  - id: tsmom
    title: Time series momentum
    rules_hard:
      - "Signal = sign of past return over lookback L; hold horizon H"
      - "Vol-scale positions"
    rules_soft: ["Cross-asset diversification is the real edge"]
    confirmations: []
    invalidation: ["Sign flip"]

  - id: costs_and_regime
    title: Costs regime
    rules_hard:
      - "Backtest must include spread/slippage model"
    rules_soft:
      - "Intraday TF often negative net of costs"
      - "Long-only on structurally rising assets may beat dual side"
    confirmations: []
    invalidation: []

setups:
  - id: trend_long_turtle55
    direction: long
    name: Long 55-day breakout
    context: "Daily"
    entry_conditions: ["Close > max high of prior 55 days"]
    entry_trigger: "Breakout close"
    stop_rule: "Entry - 2*ATR(20) or below 20-day low per variant"
    targets: ["Trail until exit rule"]
    confirmations: []
    invalidation_price_rule: "Exit rule"
    example:
      points: { break: 110, atr: 2.0, stop: 106 }
    detector_hint: "turtle55"
    research_option: R1

  - id: trend_short_turtle55
    direction: short
    name: Short 55-day breakdown
    entry_conditions: ["Close < min low of prior 55 days"]
    entry_trigger: "Breakdown close"
    stop_rule: "Entry + 2*ATR(20)"
    targets: ["Trail"]
    invalidation_price_rule: "Exit rule"
    detector_hint: "turtle55"
    development_notes: ["Compare long-only vs long-short on each symbol class"]

  - id: trend_long_turtle20
    direction: long
    name: Long 20-day breakout
    entry_conditions: ["Close > max high prior 20 days"]
    entry_trigger: "Close"
    stop_rule: "2*ATR or 10-day low variant"
    targets: ["Trail"]
    detector_hint: "turtle20"

  - id: trend_long_sma1040
    direction: long
    name: SMA stack long
    entry_conditions: ["SMA10 > SMA40"]
    entry_trigger: "Cross or first bar stacked"
    stop_rule: "Cross down or ATR"
    targets: ["Trail under swing"]
    detector_hint: "sma1040"

development_notes:
  - "Run R1 with project cost model before raising size"
  - "Portfolio of uncorrelated markets > single chart perfection"
  - "Accept 30-45% win rate as normal"
```
