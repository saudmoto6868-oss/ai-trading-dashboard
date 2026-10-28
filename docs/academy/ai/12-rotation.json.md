# AI — Rotation Scan (الماسح والتدوير)

```yaml
id: rotation
name_ar: الماسح والتدوير بين فئات الأصول
name_en: Rotation Scan — Asset Class Signals
role_in_system: scanner
lab_status: scan_aggregator

branches:
  - id: asset_class_concept
    title: Asset class rotation — what it means
    rules_hard:
      - "Each scanned symbol belongs to one asset class (Crypto, Indices, Metals, Oil & Gas, Forex, Stocks, Bonds, Options, Meme coins)"
      - "Classification is prefix-based: HL:xau→Metals, HL:spx→Indices, Y:→Stocks, FH:→Forex, else Crypto"
      - "Rotation tab groups signals by asset class, not by symbol"
    rules_soft:
      - "A class with many signals is not necessarily stronger — check lab EV per class"
      - "Use rotation view to find which class has the most lab-supported signals"
    confirmations: ["Lab EV > 0 across multiple signals in the same class"]
    invalidation: ["All signals in a class are OFF or negative — avoid that class"]

  - id: scan_dependency
    title: Rotation uses session scan results only
    rules_hard:
      - "Rotation tab reads session_state['scan_results'] — it does NOT run a new scan"
      - "If no scan results in session, tab shows info message to run Radar first"
      - "This avoids double CPU on Stats page"
    rules_soft:
      - "Run the Radar scan on the Workspace page first, then come to Rotation"
    confirmations: []
    invalidation: []

  - id: ev_per_class
    title: Expected value aggregated per asset class
    rules_hard:
      - "EV per class = mean of lab avgR of non-OFF signals in that class"
      - "If no EV available for any signal in a class, class EV shown as None"
      - "Class bar chart shows signal count; table shows EV and signal keys"
    rules_soft:
      - "Prefer classes with both high count AND positive EV"
    confirmations: []
    invalidation: []

setups:
  - id: find_best_class
    direction: any
    name: Find the strongest asset class to focus on
    context: "You ran a broad Radar scan across multiple instruments"
    entry_conditions:
      - "Run Radar scan on Workspace (or Scanner page)"
      - "Open Stats → Rotation tab"
    entry_trigger: "Class with highest count AND positive EV highlighted"
    stop_rule: "Avoid classes with negative or None EV regardless of count"
    targets: ["Focus next trades on highest-EV class"]
    confirmations: ["Multiple signals in same class, not just one"]
    invalidation: ["Scan results are stale — re-run Radar"]

notes:
  honest_disclaimer: >
    Signal count per class does not equal strength.
    EV is based on lab (IS) data.
    A class with 1 high-EV signal may be better than 5 neutral signals.
  not_investment_advice: true
```
