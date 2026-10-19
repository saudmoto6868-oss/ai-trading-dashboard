# scalp4h - gemini

_Model opinion, not evidence. Verify every source._

### 1. Regime
* **Measurable Rule:** Current 15-minute $\text{ATR}(14)$ must be greater than the 50-period simple moving average of $\text{ATR}(14)$ ($\text{ATR}_{14} > \text{SMA}_{50}(\text{ATR}_{14})$).
* **Published / Lab Evidence:** Strong empirical backing. Intraday volatility exhibits autoregressive clustering (Engle, 1982). A trade capped by a strict 4-hour time stop requires active expansion; running mean-reversion or directional trades in compressed/contracting volatility yields elevated theta/time-decay risk and target-underfill.
* **Convention:** The choice of a 14-period ATR and a 50-period baseline SMA is an arbitrary charting standard; other volatility estimators (e.g., Garman-Klass or Parkinson ranges) measure the same property.

---

### 2. Higher-Timeframe (HTF) Bias
* **Measurable Rule:** On the 1-hour chart, the 20-period EMA must be strictly above the 50-period EMA ($\text{EMA}_{20} > \text{EMA}_{50}$) for longs (or below for shorts).
* **Published / Lab Evidence:** Supported by time-series momentum and trend-following literature (Moskowitz, Ooi, Pedersen, 2012), showing directional persistence across intermediate horizons. In the lab, baseline trend filters eliminate adverse runs even if simple MA crosses generate negative standalone alpha.
* **Convention:** Using the 1-hour timeframe (4x the execution frame) and specific EMA parameters (20/50) is standard retail/institutional heuristic, not a derived mathematical optimum.

---

### 3. Location
* **Measurable Rule:** The 15-minute candle low touches or penetrates a rolling 48-period (12-hour) swing high/low that has had at least two prior unbreached touches.
* **Published / Lab Evidence:** Supported by the XPIX lab (`level` passed the edge gate: $+0.07 / +0.08\,\text{avg R}$, $n > 3150$, $t > 3$) and academic work on order clustering at discrete, visible horizontal reference points (Brock, Lakonishok, LeBaron, 1992; Osler, 2000).
* **Convention:** The 48-bar lookback window and the definition of a "touch zone" (within a fraction of ATR) are discretionary design parameters.

---

### 4. Trigger
* **Measurable Rule:** The 15-minute entry candle penetrates the location level by at least $0.1 \times \text{ATR}(14)$ and closes back on the HTF-bias side of the level (rejection/sweep close).
* **Published / Lab Evidence:** Supported by order-flow microstructure studies on liquidity sweeps and liquidity-replenishment dynamics around institutional stops (Harris, 2003). (Note: The lab showed standalone `sweep` is net-flat to negative at $-0.02\,\text{R}$, meaning the edge relies on pairing it directly with a verified HTF/location filter).
* **Convention:** Requiring the condition to settle strictly at the *close* of the 15-minute bar rather than using a tick-level or sub-minute limit order is an operational convention to avoid intra-bar whipsaws.

---

### 5. Confirmation
* **Measurable Rule:** 14-period RSI on the 15-minute chart must show a regular momentum divergence across the two most recent swing extremes within the last 16 bars.
* **Published / Lab Evidence:** Moderate lab backing (`rsi_div` produced $+0.05\,\text{avg R}$, $n = 824$). Academic literature on technical oscillators indicates mild mean-reversion qualities at intraday turning points, though edge deteriorates rapidly after spreads.
* **Convention:** The standard 14-bar RSI window and the strict definition of what constitutes a "pivot" for the divergence calculation are inherited charting conventions.

---

### 6. Timing
* **Measurable Rule:** The bar timestamp must open within high-volume session windows: 07:00–10:30 UTC (London morning) or 12:30–16:00 UTC (New York morning).
* **Published / Lab Evidence:** Robust academic support. Intraday volume, spread, and directional velocity follow a well-documented U-shaped curve (Jain & Joh, 1988; Biais, Hillion, Spatt, 1995). The lab confirms timing detectors hold positive expectation (`sess_amd` $+0.18\,\text{R}$, `judas` $+0.03\,\text{R}$), ensuring the position moves before the 4-hour window expires.
* **Convention:** Hard calendar cutoffs (e.g., cutting off at 10:30 vs. 11:00 UTC) are practical approximations of continuous liquidity ebbs.

---
