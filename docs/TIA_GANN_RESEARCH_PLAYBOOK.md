# TIA Gann Research Playbook — Version 1

Status: research specification; not a validated trading system.
Scope: standalone Gann study for TIA / XPIX Gann. Keep separate from XPIX SHIX and non-Gann indicators.

## 0. Existing project decisions and defects to preserve

- Do not treat XPIX Gann v16 as current. Earlier project history recorded Gann General Geometry v1.2 as later; the Library also contains v1.3 Repair, v1.4.1 Scale Fix and XPIX Gann Auto MTF v17/v18. Inspect history before changing code.
- Keep Gann standalone: no RSI, ADX, EMA filters, unrelated boxes, Smart Map or SHIX logic.
- Preserve independently toggleable Gann layers.
- Previously accepted defaults: automatic higher-timeframe confirmed pivot anchor; Square of Nine ON; time cycles ON; yellow target / direction arrow ON where applicable; fan, geometric shapes/star and channel OFF by default.
- Anchor label must show the exact price and time used by calculations.
- Drawings must not distort chart price scale or compress candles.
- Signals only at confirmed bar close; no future leakage, repainting or historical backdating.
- Defects to guard against: fallback anchor drifting every bar; time cycles projected from current bar rather than anchor time; fan starting from current close or ATR slope rather than calibrated anchor-based price/time ratio; historical boxes not representing true historical outcomes; unconfirmed MTF data.

## 1. Anchor selection and integrity

### 1.1 Immutable anchor record

Store symbol, venue/feed, chart timeframe, anchor timeframe, pivot side, pivot price, pivot bar time/index, left/right pivot lengths, confirmation bar time/index (when knowable), source mode (manual/chart/HTF), selection policy, tie-break rule, data revision and script version.

Never confuse the pivot's historical location with the later time it became confirmed. A pivot with R right-bars is only knowable after those R bars close. The drawing may be visually anchored back at the pivot, but any signal must not be timestamped before confirmation.

### 1.2 Selection policy

- Preferred automatic mode: latest eligible confirmed pivot on selected HTF, subject to age and minimum swing-size constraints.
- Chart mode: confirmed chart-timeframe pivot.
- Manual mode: user-entered price/time; validate positive price, valid time and symbol/session compatibility.
- Most-recent-pivot tie-break: compare confirmation times, not merely pivot timestamps.
- Never replace a valid anchor with current close, current bar, zero or a moving fallback. If no anchor exists, display NO CONFIRMED ANCHOR and suppress dependent layers.
- Preserve the previous valid anchor until a new eligible pivot is confirmed; log every change.

### 1.3 MTF and Pine safety

TradingView documents that HTF request.security values can change during a realtime HTF bar and repaint after reload. Its documented non-repainting HTF pattern offsets the requested expression by one HTF bar and uses barmerge.lookahead_on; these two parts are interdependent. Do not use lookahead_on on un-offset current HTF values: that can leak future data into historical bars.
- Validate that requested timeframe is actually higher where HTF semantics are expected.
- Verify the pivot itself is confirmed and correctly offset in its requested context. A wrapper does not automatically make a custom tuple of pivots safe.
- Test historical/realtime parity by recording values live, reloading, and comparing when each anchor first appeared.
- Every event stores pivot_time and known_time separately.

## 2. Square of Nine — arithmetic, levels and limitations

### 2.1 Reproducible practitioner formula

A commonly used modern Square-of-Nine price-level reconstruction is:

level = (sqrt(anchor_price) +/- degrees / 180)^2

The angle increment is applied to the square root, then the result is squared. For anchor 100 (sqrt=10):
- 45°: (10 +/- 0.25)^2 = 105.0625 / 95.0625
- 90°: (10 +/- 0.50)^2 = 110.25 / 90.25
- 180°: (10 +/- 1.00)^2 = 121 / 81
- 270°: (10 +/- 1.50)^2 = 132.25 / 72.25
- 360°: (10 +/- 2.00)^2 = 144 / 64

Attribution boundary: this is a widely circulated practitioner reconstruction. Do not claim this exact equation, unit choice or every modern implementation is a verbatim original W.D. Gann formula. Store it as a named, versioned calculation convention.

### 2.2 Inputs and normalization

- Anchor price must be positive.
- Explicit price multiplier/unit modifier must be fixed per instrument configuration and recorded. If price is multiplied by M before the formula, divide resulting levels by M afterwards. Changing M changes the ladder; it is not cosmetic.
- Record tick size, decimal precision, contract type and quote currency.
- Round only at the final display/tick boundary; retain unrounded values internally.
- Calculate upper and lower levels independently; reject non-positive results.
- Store source anchor, modifier, degrees and formula variant with every level.
- Do not let automatic modifier selection silently change a historical ladder. If auto mode is supported, freeze the selected modifier for the anchor epoch and log it.

### 2.3 Required tests

- Anchor 100 reproduces all values above.
- 360° upward from 100 equals 144; downward equals 64 under this formula.
- Test multiplier behavior and document that changing M changes results.
- Tick rounding must not feed back into later calculations.
- Test very small prices, high prices, fractional ticks, FX-style quotes and futures.

### 2.4 Interpretation

Square-of-Nine levels are candidate reference levels, not guaranteed support/resistance and not entry signals. A touch, crossing or confluence does not establish a trade. Require independent market-structure confirmation and test whether the level adds predictive value beyond ordinary swing levels.

## 3. Gann fan and angle calibration

### 3.1 Price/time ratio, not screen geometry

A 1x1 is one configured price unit per one configured time unit. Its apparent 45° screen angle changes when chart scaling changes. Therefore:
- Define time unit explicitly: chart bars, trading sessions, calendar days or elapsed seconds.
- Define price unit explicitly: points, ticks, currency units or a fixed instrument-specific increment.
- Calibrate price/time scale from a documented reference swing or explicit user-set scale.
- Store calibration with anchor/instrument; do not recalculate on zoom, scroll or every bar.

TradingView's Fan documentation describes 1x1 as one price unit per time unit and emphasizes proper scale ratio. It describes a practical calibration using comparable top-to-top or bottom-to-bottom price and time differences.

### 3.2 Slope convention

Let base = abs(price_2 - price_1) / abs(time_units_2 - time_units_1) from the selected calibration swing. For a ray ratio a:b, absolute price slope = base * a / b price units per time unit.

projected_price = anchor_price + direction * elapsed_time_units * base * a / b

Direction is +1 for an upward ray and -1 for a downward ray.

Declared implementation convention:
- 1x1 = base
- 2x1 = 2 * base
- 1x2 = 0.5 * base
- 4x1 = 4 * base
- 1x4 = 0.25 * base

Keep numerator/denominator naming consistent across modules.

### 3.3 Calibration variants to compare separately

A. Reference-swing calibration: top-to-top or bottom-to-bottom as described in TradingView help.
B. Fixed user calibration: explicit price units per time unit; stable/reproducible but instrument-specific.
C. Volatility-normalized research variant: freeze an ATR-derived price unit at anchor confirmation. This is a separate experimental fan, not the canonical fan.

Do not mix variants in one backtest.

### 3.4 Events to measure

Approach/touch of ray; close-confirmed break; retest and hold/fail; movement from one ray to next; time spent above/below ray; outcomes by regime/session. Distinguish intrabar touch from bar-close confirmation and include realistic costs.

## 4. Gann squares, boxes, circles and radial geometry

### 4.1 Square / box

A Gann square/box uses a defined price range and time range from a major pivot and partitions both axes into levels. Record anchor coordinate, opposite corner, price range, time range, price-per-bar ratio, division count/spacing, direction/reverse orientation and whether angles/arcs/levels are enabled.

Do not draw a square in pixel space and call it a price-time square. Construct in normalized data coordinates. Chart scaling changes must not change underlying levels or anchor.

### 4.2 Circle / arcs

A circle on a price-time chart requires a common normalized coordinate system. A visually round screen circle is not necessarily a circle in price/time units. Store center, radius in normalized price/time units, scale ratio, anchor and division scheme. Keep arcs display-only until a specific rule and measurable event are defined.

### 4.3 Radial divisions

For 360° geometry, define exact angular set and rotation origin. Common divisions such as 45°, 90°, 120°, 135°, 180°, 225°, 240°, 270°, 315° and 360° appear in secondary summaries of Gann-style methods; they are candidate study divisions, not universal laws. Compare equal angular divisions with the 24-part wheel and Square-of-Nine conventions; do not assume they are the same construction.

### 4.4 Construction validation

Reproduce one diagram manually from its source before coding. Unit-test center, radius, angle, quadrant and endpoint. Chart zoom/scale must not alter underlying price/time coordinates. Ensure drawings do not push chart autoscale. If geometry is decorative and has no decision rule, keep it display-only and disabled by default.

## 5. Time cycles and price-time squaring

### 5.1 Separate cycle families

Keep distinct: elapsed calendar time (seconds/days/weeks/months); trading time (sessions/trading days); bar counts (bars on named timeframe); annual/seasonal calendar dates; price-derived cycles. Never silently substitute one for another. Holidays, weekends, DST, missing bars and exchange sessions make them differ.

### 5.2 Candidate cycle set

Secondary summaries list calendar-day candidates such as 30, 45, 60, 90, 135, 150, 180, 210, 225, 315, 330 and 360; trading-day counts are listed separately (e.g. 11, 22, 33, 45, 56, 67, 78, 90 and others). These are research candidates only, not universal turning points. Existing project defaults of 30/45/90 bars are project conventions, not established laws.

### 5.3 Correct projection

For bar-count cycles: target_bar_index = anchor_bar_index + k * cycle_bars.
For elapsed-time cycles: target_timestamp = anchor_timestamp + k * cycle_duration.

Never project from current bar_index. Preserve anchor time. For HTF anchors projected on LTF charts, convert via timestamps/timeframe duration carefully; bar indices do not necessarily align across timeframes.

### 5.4 Squaring time and price

Define price distance and elapsed time independently, normalize by chosen price/time unit, then measure whether a predeclared equality or ratio is reached. Do not label an arbitrary price move after N bars as a square post hoc. Pre-register ratios and tolerances before testing.

## 6. Historical examples and evidence discipline

### 6.1 What is documented

W.D. Gann and John L. Gann's 1941 book How to Make Profits Trading in Commodities is catalogued as a 391-page work with chapters on formations, trading rules, swings, time periods and commodity histories. The 1942 edition is catalogued at 412 pages with historical commodity examples. This establishes a source corpus to study; it does not prove the efficacy of every modern Square-of-Nine or fan formula.

A secondary summary of Gann-style techniques describes multiple forms of confluence (angles, horizontal prior highs/lows, time cycles, volume and squaring time/price) and says square-of-number levels should not be traded by themselves. Treat this as secondary interpretation, not primary Gann text.

### 6.2 Historical case-study ledger

For every claimed example capture source/book/page/chart number and edition; instrument/contract/venue/date range; original data provenance and adjustments; anchor and whether knowable at the time; calculation variant, units, scale and parameters; forecast timestamp/level/tolerance; outcome definition (touch, rejection, close break, reversal or target); failed examples and competing levels; and whether the example was selected after the outcome was known.

No cherry-picked chart is evidence. Build successful and failed cases from a predefined sampling rule.

## 7. Validation protocol — no strategy validated yet

### 7.1 Baselines

Test each component independently: confirmed swing highs/lows; Square-of-Nine only; calibrated fan only; time cycles only; geometry intersections only; predeclared confluence combinations. Compare against simple baselines such as prior swing levels, equal-distance levels, random timestamps and no-signal benchmark.

### 7.2 Data and event timing

Use point-in-time data; document venue, symbol, contract roll, timezone, session, gaps and adjustments. Store signal known_time, never pivot time alone. Use closed bars for confirmed signals. Define intrabar touch separately from close-confirmed break. Include spread, commission, slippage, funding/borrow and realistic fills. Avoid optimistic same-bar stop/target ordering; use lower-timeframe data or conservative worst-case ordering when both are touched.

### 7.3 Statistics and overfit controls

Pre-register a small number of hypotheses/parameters. Keep chronological train, validation and untouched test segments. Use walk-forward tests and regime-separated reporting. Report trade count, expectancy, median R, profit factor, max drawdown, tail loss, time in market, turnover, costs and confidence intervals. Test parameter stability; do not select a winner from hundreds of configurations without correction. Consider Probability of Backtest Overfitting / CSCV when many configurations are tried. Report negative and neutral results as first-class outcomes.

The project's previously documented promotion gate (n >= 100, t > 3, net after costs positive, both halves positive) may be retained as an initial gate, but it is not a universal guarantee. Require untouched out-of-sample and forward/paper review before promotion.

## 8. TIA module requirements

Keep Gann independent from SHIX and core risk logic. Proposed TIA-only modules:
- anchor_engine: confirmed anchor selection and immutable anchor records
- square_of_nine: formula variants, modifiers and level generation
- fan_engine: scale calibration and ratio projections
- geometry_engine: square/box/circle/radial coordinates
- time_cycle_engine: bar/calendar/session cycles
- gann_event_evaluator: candidate touches/breaks/retests and outcome labels
- gann_research_ledger: source citations, test cases, versioned hypotheses and results

UI must show layer status, formula/scale/anchor metadata and research reference/unvalidated labels. Visual confluence is not a signal unless a separately specified and validated setup says so. No live orders.

## 9. Minimum tests before promotion

- Anchor remains fixed until a later pivot is confirmed.
- Pivot known_time is later than pivot_time by configured right-bars confirmation.
- No fallback to current close/current bar.
- HTF historical and realtime outputs match after reload.
- No un-offset HTF lookahead.
- Square-of-Nine vectors above.
- Modifier and tick-rounding tests.
- Fan 1x1 / 2x1 / 1x2 slope ratio tests.
- Fan remains anchored under chart zoom/scale changes.
- Time cycles project from anchor time/index, not current bar.
- Calendar/trading/bar-count cycles tested across weekends, holidays and DST.
- Geometry coordinates stable under visual scale changes.
- Drawings do not distort autoscale.
- Event timestamps never precede known_time.
- Backtest prevents future leakage and optimistic same-bar fills.
- Historical examples include failed cases.

## 10. Source register

Primary/platform documentation:
- TradingView, Gann Fan: https://www.tradingview.com/support/solutions/43000518151-gann-fan-drawing-tool/
- TradingView, Gann Box: https://www.tradingview.com/support/solutions/43000518152-gann-box-drawing-tool/
- TradingView, Gann Square: https://www.tradingview.com/support/solutions/43000518149-gann-square-drawing-tool/
- TradingView Pine Script, Repainting: https://www.tradingview.com/pine-script-docs/concepts/repainting/
- TradingView Pine Script, Other timeframes and data: https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
- Google Books catalogue, W.D. Gann and John L. Gann, How to Make Profits Trading in Commodities (1941): https://books.google.com/books?id=JYm-QQAACAAJ
- FAO AGRIS bibliographic record: https://agris.fao.org/search/en/providers/122535/records/65ddec5263b8185d9ca59e6a

Secondary references (not original Gann text):
- Summary of W.D. Gann techniques: https://cyclesresearchinstitute.org/pdf/cycles-economy/Summary-of-W-D-Gann-Techniques-of-Analysis.pdf
- Square-of-Nine formula guide; notes formula is a later practitioner reconstruction: https://www.quantum-algo.com/ar/blog/guides/gann-square-of-9/
- Bailey et al., The Probability of Backtest Overfitting: https://papers.ssrn.com/sol3/Papers.cfm?abstract_id=2326253

## 11. Open research questions

- Which exact Square-of-Nine wheel/numbering convention appears in each archived Gann image (refs 20–30)?
- Which diagrams are original source material and which are modern reinterpretations?
- Is the 24-part wheel equivalent to the spiral formula in a given source? Verify, do not assume.
- What exact price unit and scale did the historical chart use?
- Can fan/square/cycle components add predictive value after costs over simple swing/time baselines?
- Which historical examples survive point-in-time reconstruction and include failures?
- Which instrument-specific calibration remains stable across regimes without overfitting?

Conclusion: research foundation is explicit. Gann levels, fans, geometry and cycles remain unvalidated research tools until source reconstruction, no-lookahead implementation and independent out-of-sample testing are complete.
