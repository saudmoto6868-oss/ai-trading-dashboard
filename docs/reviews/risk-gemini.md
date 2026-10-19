# risk - gemini

_Model opinion, not evidence. Verify every source._

Below is a synthesis of the theoretical and empirical literature on risk management, position sizing, and trader survival, spanning quantitative finance, behavioral economics, and peer-reviewed studies of retail futures markets.

---

### 1. Break-Even Win Rate vs. Reward:Risk (R:R)

#### The Mathematics of Expectancy
Expectancy per trade ($E$) measured in units of risk ($R$, where $1R = \text{capital risked at stop}$) is defined as:
$$E = (P \times W) - ((1 - P) \times L) - C$$
Where:
*   $P$ = Win probability (win rate)
*   $W$ = Reward-to-Risk ratio ($\frac{\text{Take Profit distance}}{\text{Stop Loss distance}}$)
*   $L$ = Loss unit (typically $1.0R$ without slippage)
*   $C$ = Total round-turn transaction cost (commissions, exchange fees, bid-ask spread, and execution slippage) normalized to $R$.

Solving for the zero-friction break-even win rate ($P_{\text{be}}$):
$$P_{\text{be}} = \frac{1}{1 + W}$$

| Reward-to-Risk ($W$) | Zero-Cost Break-Even ($P_{\text{be}}$) | Practical Break-Even with Costs ($C = 0.10R$) | Practical Break-Even with Costs ($C = 0.20R$) |
| :--- | :--- | :--- | :--- |
| **0.5 : 1** | 66.7% | 68.7% | 70.7% |
| **1.0 : 1** | 50.0% | 52.5% | 55.0% |
| **1.5 : 1** *(Lab setup)* | **40.0%** | **42.4%** | **44.8%** |
| **2.0 : 1** | 33.3% | 35.6% | 37.8% |
| **3.0 : 1** | 25.0% | 26.9% | 28.8% |

#### The Random Walk / First-Passage Problem
Under a standard geometric Brownian motion without drift (pure random walk), the probability of hitting a target before a stop is strictly an inverse function of distance:
$$P(\text{Hit Target}) = \frac{D_{\text{stop}}}{D_{\text{stop}} + D_{\text{target}}} = \frac{1}{1 + W}$$
*   **The Fallacy:** Traders often assume they can independently pick a $2:1$ or $3:1$ target while maintaining a $50\%$ win rate. 
*   **The Reality:** In an efficient market, increasing the target distance mechanically reduces the first-passage hitting probability proportionally. A positive edge ($E > 0$) requires the underlying price distribution conditional on the entry signal to have localized positive drift or structural skewness that exceeds the cost hurdle $C$.

---

### 2. Fixed-Fraction Sizing and Risk of Ruin

#### The Kelly Criterion
Introduced by J.L. Kelly Jr. (1956) and extended to investing by Edward O. Thorp (1969, 2006):
$$f^* = \frac{b \cdot p - q}{b}$$
Where $p$ = win rate, $q = 1 - p$, and $b$ = payoff ratio ($W$).

*   **Property:** Full Kelly sizing ($f^*$) maximizes the asymptotic long-run geometric growth rate of capital:
    $$g(f) = E[\ln(1 + f \cdot X)]$$
*   **Drawdown Profile:** Full Kelly is notoriously volatile. Under continuous assumptions, there is a **$33.3\%$ probability of suffering a $50\%$ drawdown** before doubling capital (MacLean, Thorp, & Ziemba, 2011). It also heavily assumes parameter certainty (exact knowledge of $p$ and $b$).
*   **Parameter Estimation Risk:** If true edge is overestimated by as little as $25\%$, Full Kelly shifts into the negative geometric growth zone (the "death zone"), causing guaranteed long-run ruin.

#### Fractional Kelly & Fixed-Fraction Rules
*   **Fractional Kelly ($0.25f^*$ to $0.50f^*$):** Academic consensus among quantitative fund managers and mathematicians (e.g., MacLean et al., 2010; Vince, 1990) recommends "Half-Kelly" ($0.5f^*$) or "Quarter-Kelly" ($0.25f^*$). Half-Kelly achieves **$75\%$ of the maximum theoretical growth rate** while reducing the variance of
