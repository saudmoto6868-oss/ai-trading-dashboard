# scalp4h - gemini

_Model opinion, not evidence. Verify every source._

Here is a quantitative, 7-step checklist tailored for 15-minute execution with a 4-hour (16-bar) hard time stop.

---

### Scalp Execution Checklist (Max 7 Conditions)

| # | Condition | Measurable Rule | Status: Evidence vs. Convention |
|---|---|---|---|
| **1** | **Regime** *(Volatility)* | $15\text{m ATR}(14) > 50\text{-bar Simple Moving Average of ATR}(14)$. | **Published Evidence**: Supported by volatility clustering literature (Engle, 1982; Mandelbrot). Low-volatility regimes fail to generate the dispersion needed to hit $1.5\text{R}$ within 16 bars. |
| **2** | **HTF Bias** *(Trend direction)* | $1\text{H Close} > 1\text{H EMA}(50)$ and $1\text{H EMA}(50)$ slope is positive over the last 3 bars (reversed for shorts). | **Published Evidence**: Supported by time-series momentum anomalies (Moskowitz, Ooi, Pedersen, 2012; Brock, Lakonishok, LeBaron, 1992). Moving average slope reliably filters directional drift. |
| **3** | **Location** *(Value boundary)* | Price tests a validated horizontal level (a rolling $1\text{H}$ swing high/low tested $\ge 2$ times over the last 5 trading days) within $\pm 0.25 \times 15\text{m ATR}(14)$. | **Published Evidence**: Partially supported. Academic microstructure confirms limit/stop order clustering at prior structural pivots (Osler, 2003, 2005). Supported internally by the XPIX lab (`level` edge passed). |
| **4** | **Trigger** *(Execution event)* | The $15\text{m}$ candle breaks the prior bar’s extreme in the bias direction, with bar range $> 1.0 \times 15\text{m ATR}(14)$. | **Mixed**: Intraday range expansion and directional micro-breakouts have empirical support (Crabel, 1990). However, specific candlestick shapes (engulfing, pinbars) are **trader convention**. |
| **5** | **Confirmation** *(Volume validation)* | Trigger bar volume $> 1.5 \times 20\text{-bar SMA of volume}$. | **Published Evidence**: Supported by volume-price literature (Blume, Easley, O’Hara, 1994; Karpoff, 1987). Breakouts lacking anomalous volume have a significantly higher false-breakout rate. |
| **6** | **Timing** *(Liquidity window)* | Entry timestamp falls strictly within high-liquidity session opens: 07:00–10:00 UTC (London) or 12:30–15:30 UTC (New York). | **Published Evidence**: Highly supported by empirical market microstructure (Admati & Pfleiderer, 1988). Intraday spreads, volatility, and order flow follow a strict U-shaped curve; off-session scalps are net-negative after spread drag. |
| **7** | **Risk** *(Sizing & Exits)* | Initial Stop Loss = $1.5 \times 15\text{m ATR}(14)$; Take Profit = $1.5 \times \text{Risk}$ ($1:1.5\text{R}$); Hard Time Exit = close trade at market on the close of the 16th bar ($4\text{ hours}$) if neither SL nor TP is triggered. | **Convention & Methodological**: Volatility-based sizing (ATR stops) and time exits are standard quantitative risk controls to combat the disposition effect (Shefrin & Statman, 1985). The exact $1.5\text{R}$ target and 16-bar limit are **operational conventions**. |

---

### Implementation Discipline

1. **Failure Rule**: If any single condition (1 through 6) fails, the signal is discarded—no discretionary overrides.
2. **Time-Stop Enforcement**: The 16-bar (4-hour) exit prevents capital tie-up in dead chop. If a scalp has not reached the $1.5\text{R}$ threshold within 16 bars, the thesis has expired, and holding longer degrades the volatility edge.
