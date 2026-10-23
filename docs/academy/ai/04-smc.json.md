# AI — SMC / ICT (مفصّل)

```yaml
id: smc
name_ar: SMC ICT
name_en: Smart Money Concepts
role_in_system: context
lab_status: unproven

branches:
  - id: structure_bos_choch
    title: BOS CHoCH
    rules_hard:
      - "Swing pivot length fixed"
      - "BOS: close beyond last swing high in uptrend sequence (define close vs wick)"
      - "CHoCH: first opposite break of structure after prior trend"
    rules_soft: ["CHoCH is warning not auto entry"]
    confirmations: []
    invalidation: ["Structure labels rebuild after break"]

  - id: liquidity
    title: Buy side sell side liquidity
    rules_hard:
      - "Equal highs/lows or session highs marked as liquidity pools by algorithm"
    rules_soft: ["Sweep then reverse is a hypothesis to test not a law"]
    confirmations: []
    invalidation: []

  - id: fvg
    title: Fair value gap
    rules_hard:
      - "Bullish FVG: low[0] > high[2] on 3-candle gap definition (index convention fixed)"
      - "Mitigation rule fixed: touch vs 50% vs full fill"
    rules_soft: ["IFVG optional separate detector"]
    confirmations: ["In discount for longs"]
    invalidation: ["Full fill against thesis if rule says so"]

  - id: order_block
    title: Order block
    rules_hard:
      - "OB = last opposing candle before displacement of size D; zone open-low or full body per code"
      - "Unmitigated flag until price trades through"
    rules_soft: ["Most subjective part — keep geometry dumb and strict"]
    confirmations: ["After sweep optional"]
    invalidation: ["Close through OB"]

  - id: premium_discount
    title: Dealing range
    rules_hard:
      - "Range from swing low to swing high; midpoint = EQ"
    rules_soft:
      - "Longs preferred below EQ; shorts above"
      - "OTE band ~61.8–79% retracement of range optional"
    confirmations: []
    invalidation: []

setups:
  - id: smc_long_sweep_fvg
    direction: long
    name: Sweep sell-side into FVG
    context: "Discount; bullish bias or CHoCH up"
    entry_conditions:
      - "Sell-side pool swept"
      - "Bullish displacement or BOS"
      - "Price revisits bullish FVG"
    entry_trigger: "Rejection in FVG or limit at 50% gap"
    stop_rule: "Below sweep low"
    targets: ["Buy-side pool", "1.5R"]
    confirmations: ["Discount"]
    invalidation_price_rule: "Close below FVG low / sweep"
    research_option: R5
    detector_hint: null

  - id: smc_short_sweep_ob
    direction: short
    name: Sweep buy-side into supply OB
    context: "Premium"
    entry_conditions: ["Buy-side swept", "Bearish BOS", "Rally into supply OB"]
    entry_trigger: "Rejection in OB"
    stop_rule: "Above sweep high"
    targets: ["Sell-side pool"]
    invalidation_price_rule: "Close above OB"
    detector_hint: null

  - id: smc_long_ote
    direction: long
    name: OTE in discount after BOS
    entry_conditions: ["Bullish BOS", "Retrace into 62-79% of impulse"]
    entry_trigger: "Reversal candle in band"
    stop_rule: "Below impulse start"
    targets: ["Prior high"]
    invalidation_price_rule: "Close below impulse start"
    detector_hint: null

development_notes:
  - "External tests: mechanical ICT often PF 1.2-1.5 not miracle"
  - "Ablate: sweep only vs FVG only vs combined"
  - "Do not promote to primary without R5 pass"
```
