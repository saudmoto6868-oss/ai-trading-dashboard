# scalp4h - gemini

_Model opinion, not evidence. Verify every source._

Here is the 7-step checklist tailored for 15-minute scalps with a 4-hour max horizon (16 bars), structured strictly in execution order with measurable rules and evidence distinctions.

---

### 1. Regime (Volatility & Trendability Filter)
* **Measurable Rule:** 15-minute ATR(14) must be greater than its 50-period simple moving average ($\text{ATR}_{14} > \text{SMA}_{50}(\text{ATR}_{14})$).
* **Evidence vs. Convention:**
  * *Evidence:* Supported. Volatility clustering and regime shifts have strong empirical validation in financial econometrics (Engle, 1982 ARCH models). Trading directional scalps during volatility compression systematically yields lower win rates and whipsaws.
  * *Convention:* The specific lookbacks (14-period ATR, 50-period SMA) are practitioner conventions.

---

### 2. Higher-Timeframe (HTF) Bias
* **Measurable Rule:** On the 1-hour timeframe, the most recent closed candle must be on the trade’s side of the 50-period Exponential Moving Average ($\text{Close}_{1h} > \text{EMA}_{50}$ for long, $\text{Close}_{1h} < \text{EMA}_{50}$ for short).
* **Evidence vs. Convention:**
  * *Evidence:* Supported. Time-series momentum and moving-average trend-filtering are backed by extensive academic literature across asset classes (e.g., Brock, Lakonishok, & LeBaron, 1992; Moskowitz, Ooi, & Pedersen, 2012).
  * *Convention:* Choosing the 1-hour timeframe (4x multiplier from 15m) and the 50-period EMA over other trend measures (e.g., 200 EMA, 20-bar Donchian) is practitioner convention.

---

### 3. Location (Value / Structural Zone)
* **Measurable Rule:** The 15-minute candle entry must test within 0.5 ATR(14) of a rolling 40-bar pivot high/low that has logged at least two prior unbreached touches.
* **Evidence vs. Convention:**
  * *Evidence:* Supported. Support/resistance zones and horizontal breakout levels exhibit clear clustering of limit/stop orders (Osler, 2000, 2003 on order clusters at structural points). This aligns with your lab run: `level` was the **only** detector to clear the edge gate ($+0.07 / +0.08$ avg $R$).
  * *Convention:* The 0.5 ATR distance tolerance and requiring exactly two touches are operational conventions.

---

### 4. Trigger (Execution Event)
* **Measurable Rule:** A 15-minute candle must probe beyond the extreme of the prior 2 bars and close back across the opening price of the current bar in the direction of the HTF bias (a reversal rejection candle).
* **Evidence vs. Convention:**
  * *Evidence:* **Convention only /
