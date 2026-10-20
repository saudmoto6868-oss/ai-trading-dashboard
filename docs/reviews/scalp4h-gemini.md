# scalp4h - gemini

_Model opinion, not evidence. Verify every source._

Here is the 7-step checklist for 15-minute scalps with a mandatory 4-hour (16-bar) time horizon, structured in sequence.

---

### 1. Regime (Volatility Filter)
* **Measurable Rule:** 15-minute 14-period ATR must be greater than its 50-period simple moving average ($\text{ATR}_{14} > \text{SMA}_{50}(\text{ATR}_{14})$).
* **Published Evidence:** **Supported.** Volatility clustering (Mandelbrot, 1963; Engle’s ARCH, 1982) demonstrates that large price movements follow large price movements. Volatility expansion filters consistently improve trend/breakout payoff distributions over fixed-time horizons.
* **Convention:** The choice of a 14-period ATR and 50-period SMA threshold is an operational convention rather than a mathematical law.

---

### 2. Higher-Timeframe Bias (Directional Filter)
* **Measurable Rule:** The most recent completed 1-hour bar must close above its 50-period Exponential Moving Average ($\text{Close}_{1\text{H}} > \text{EMA}_{50, 1\text{H}}$) for longs, or below for shorts.
* **Published Evidence:** **Supported.** Multi-frequency time-series momentum (Asness, Moskowitz, Pedersen, 2013) demonstrates that conditioning short-horizon trades on intermediate-term trend direction significantly reduces left-tail drawdowns and whipsaws.
* **Convention:** The 50 EMA on the 1-hour timeframe (and the choice of 1H relative to 15m) is discretionary charting convention.

---

### 3. Location (Structural Reference Point)
* **Measurable Rule:** The low of the setup must be within $0.5 \times \text{ATR}_{14}$ of an established horizontal structural pivot (defined as the high or low of a rolling 20-period 1-hour Donchian boundary).
* **Published Evidence:** **Supported.** Empirical microstructure research (Osler, 2000, 2003; Brock, Lakonishok, LeBaron, 1992) shows measurable clustering of stop and limit orders around prominent multi-hour highs/lows. This directly aligns with the XPIX lab result, where horizontal `level` was the only detector passing the statistical edge gate ($t > 3$, out-of-sample positive).
* **Convention:** Rebranding horizontal boundaries as institutional "order blocks," "fair value gaps," or "points of interest" is marketing convention; the lab found single ICT zone detectors failed or broke even.

---

### 4. Trigger (Execution Catalyst)
* **Measurable Rule:** On the 15-minute chart, price pierces the structural pivot and closes back on the active side of the level, with the closing price falling within the top 25% of that bar's total range (a rejection/absorption bar).
* **Published Evidence:** **Mixed / Limited.** Price rejection patterns and liquidity sweeps (false breakout failure) are documented in market-making literature as temporary liquidity imbalances. However, isolated candle shapes have weak standalone statistical significance in academic tests without strict context.
* **Convention:** Naming this a "liquidity grab," "Judas swing," or "turtle soup" is narrative convention. The measurable event is simply a failed breakout with a high close-to-range ratio.

---

### 5. Confirmation (Flow / Momentum Co-sign)
* **Measurable Rule:** The trigger bar's volume must exceed $1.5 \times$ the 20-period volume moving average, AND the 14-period 15-minute RSI must print between 50 and 65 for longs (above equilibrium, but below overbought).
* **Published Evidence:** **Supported.** The "High-Volume Return Premium" (Gervais, Kaniel, Mingelgrin, 2001; Blume, Easley, O'Hara, 1994) confirms that breakout moves accompanied by above-average volume have higher continuation rates over subsequent short horizons.
* **Convention:** Specific indicator bounds (
