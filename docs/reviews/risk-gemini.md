# risk - gemini

_Model opinion, not evidence. Verify every source._

### 1. Break-Even Win Rate vs. Reward:Risk (R:R)

#### The Formulation
In a binary outcome model (fixed target and fixed stop), the mathematical break-even win rate ($W_{\text{be}}$) ignoring frictional costs is:

$$W_{\text{be}} = \frac{1}{1 + R}$$

where $R = \frac{\text{Target}}{\text{Stop}}$ (the realized reward-to-risk ratio).

When transaction costs $c$ (commissions, exchange fees, bid-ask spread, and slippage) are incorporated as a fraction of the risk unit $1R$:

$$\mathbb{E}[R] = W(R - c) - (1 - W)(1 + c) = 0 \implies W_{\text{be}} = \frac{1 + c}{1 + R}$$

| Nominal R:R ($R$) | Zero-Cost $W_{\text{be}}$ | With Friction ($c = 0.05R$) | With Friction ($c = 0.10R$) |
| :--- | :--- | :--- | :--- |
| **0.5 : 1** (Scalp / Mean Reversion) | 66.7% | 70.0% | 73.3% |
| **1.0 : 1** (Symmetric) | 50.0% | 52.5% | 55.0% |
| **1.5 : 1** (Your Lab Baseline) | 40.0% | 42.0% | 44.0% |
| **2.0 : 1** (Trend / Breakout) | 33.3% | 35.0% | 36.7% |
| **3.0 : 1** (Asymmetric Trend) | 25.0% | 26.25% | 27.5% |

#### The "High R:R Fallacy"
* **Theoretical Grounding:** Vince (*Portfolio Management Formulas*, 1990); Tharp (*Trade Your Way to Financial Freedom*, 1998).
* **The Principle:** A common retail belief is that maintaining a high R:R (e.g., 3:1) compensates for lack of edge. However, assuming an efficient or near-efficient market (martingale baseline), the win rate naturally decays inversely to the distance to the profit target:
  
  $$P(\text{Hit Target before Stop}) \approx \frac{\text{Distance to Stop}}{\text{Distance to Stop} + \text{Distance to Target}} = \frac{1}{1 + R}$$

  Without an underlying structural or microstructural edge, **changing R:R simply shifts your location along an identical zero/negative-sum trade-off curve.** High R:R trades increase variance, lengthen drawdown durations, and increase exposure to regime shifts.

---

### 2. Fixed-Fraction Sizing and the Kelly Criterion

#### Kelly Criterion vs. Fixed Fraction
* **Kelly Criterion (Kelly, 1956):** Calculates the optimal fraction of capital ($f^*$) to maximize the asymptotic growth rate of log-wealth:
  
  $$f^* = \frac{p \cdot b - q}{b} = p - \frac{1 - p}{b}$$
  
  where $p = \text{win rate}$, $q = 1 - p$, and $b = \text{reward-to-risk ratio}$.

* **The Problem with Full Kelly:**
  * **Parameter Uncertainty:** Kelly assumes $p$ and $b$ are stationary and known with certainty. In finance, they are noisy sample estimates. If you overestimate $p$ by even 2–3%, Full Kelly moves into the **negative expected growth zone** (over-betting leads to ruin).
  * **Tail Drawdowns:** Full Kelly portfolios have a 33% probability of experiencing a 50% drawdown before doubling capital (MacLean, Thorp, & Ziemba, *The Kelly Capital Growth Investment Criterion*, 2011).

#### Practical Standards: Fractional Kelly & Fixed Fraction
1. **Fractional Kelly ($\frac{1}{4}$ to $\frac{1}{2}$ Kelly):** 
   Practitioners (e.g., Ed Thorp) scale Kelly by $0.25\times$ to $0.50
