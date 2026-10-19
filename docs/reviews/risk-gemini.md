# risk - gemini

_Model opinion, not evidence. Verify every source._

### 1. Break-Even Win Rate vs. Reward:Risk (R:R)

The break-even win rate is the percentage of winning trades required to yield an expected value ($E[R]$) of zero, holding transaction costs constant.

#### Pure Mathematical Formulation
Let:
*   $R = \frac{\text{Average Gain}}{\text{Average Loss}}$ (Reward:Risk ratio)
*   $W = \text{Probability of a winning trade (Win Rate)}$
*   $L = 1 - W = \text{Probability of a losing trade}$

$$\mathbb{E}[R] = (W \cdot R) - (1 - W) \cdot 1 = 0 \implies W_{\text{BE}} = \frac{1}{1 + R}$$

| Planned R:R | Theoretical Break-Even Win Rate | Break-Even with 0.1R Friction (Slippage + Commission)* |
| :--- | :--- | :--- |
| **0.5 : 1** | 66.67% | 71.43% |
| **1.0 : 1** | 50.00% | 52.38% |
| **1.5 : 1** | 40.00% | 42.11% |
| **2.0 : 1** | 33.33% | 35.48% |
| **3.0 : 1** | 25.00% | 26.83% |
| **5.0 : 1** | 16.67% | 18.03% |

*\*Calculated with friction $c = 0.1R$ added to loss and subtracted from gain: $W_{\text{BE}} = \frac{1 + c}{(1 + R)}$.*

#### Empirical & Market Microstructure Reality
*   **Non-linear execution drag:** High theoretical R:R targets (e.g., 3:1 or 5:1) assume execution at the nominal stop and target prices. In empirical microstructure studies (e.g., *Harris, 2003*), limit orders at distant targets suffer from adverse selection (unfilled when the market runs past, filled when momentum exhausts), while market/stop orders incur structural adverse slippage.
*   **The path-dependency paradox:** Price paths exhibit negative autocorrelation on short time horizons (bid-ask bounce and mean reversion). Placing a tighter stop relative to a wider target disproportionately triggers the stop purely through diffusion/noise before the drift reaches the target (*Feller, 1968, "Gambler's Ruin" framework*).

---

### 2. Fixed-Fraction and Volatility-Adjusted Sizing

Position sizing determines geometric capital growth and the asymptotic probability of ruin.

#### The Kelly Criterion
Introduced by J.L. Kelly Jr. (*1956*) and applied to financial markets by Edward Thorp (*1969, 2006*), the Kelly fraction $f^*$ maximizes the expected logarithmic growth rate of capital:

$$f^* = \frac{p \cdot b - q}{b} = \frac{p(b + 1) - 1}{b}$$

Where $p$ = win rate, $q = 1 - p$, and $b$ = net odds received (Reward:Risk ratio $R$).

*   **Practitioner Risk (Over-betting):** Full Kelly assumes known, stationary probability distributions and continuous rebalancing. In reality, trade outcomes exhibit fat tails (kurtosis) and parameter uncertainty. An overestimation of $p$ or $b$ of just 10–20% under Full Kelly leads to negative geometric growth and catastrophic drawdowns (*MacLean, Thorp, & Ziemba, 2011*).
*   **Fractional Kelly:** Systematic hedge funds and quantitative practitioners virtually never trade Full Kelly. Standard institutional practice uses **"Half-Kelly" ($0.5 f^*$)** or **"Quarter-Kelly" ($0.25 f^*$)**, which captures ~75–88% of the maximum growth rate while reducing portfolio variance and maximum drawdown risk by ~50% or more.

#### Fixed-Percentage Risk & Volatility Parity
*   **Fixed Fractional (Ralph Vince, 1990):** Risking a static fraction (e.g., 0.5% to 2.0%) of total account equity per trade.
*   **Volatility-Adjusted Sizing (Robert Carver, *Systematic Trading*, 2015):** Rather than sizing to account equity alone, position size is normalized by the current market volatility:
    $$\text{Position Size} = \frac{\text{Account Capital} \times \text{Risk Target}}{\text{Instrument Volatility (ATR or } \sigma) \times \text{Point Value}}$$
    *Evidence:* Equalizing the dollar volatility per trade across all instruments prevents high-beta assets from dominating portfolio variance and standardizes drawdown distributions across regimes.

---

### 3. Daily Loss Limits, Circuit Breakers, and Drawdowns

#### Quantitative & Statistical Findings
*   **Volatility-clustering & Drawdown Correlation:** Mandelbrot (*1963*) and Engle (*1982*, ARCH models) demonstrated that volatility clusters. A strategy experiencing an intraday breach of a loss limit is often operating in an altered volatility/regime state where model assumptions fail.
*   **Trend-following drawdown controls:** Harvey, Liew, et al. (*2019*, "Strategic Risk Management: Designing Portfolios and Managing Risk") showed that dynamic volatility targeting and systematic drawdown circuit breakers reduce tail risk (kurtosis) and improve the Sharpe ratio by clipping negative skewness.

#### Behavioral & Discretionary Drivers
*   **Loss-Chasing via Cumulative Prospect Theory:** Kahneman & Tversky (*1979, 1992*) proved that human utility functions are concave for gains but **convex for losses**. When in a losing position (e.g., down 2–3 daily risk units), human decision-makers switch from risk-averse to **risk-seeking**, taking sub-optimal, high-leverage gambles to recover to break-even ("get-evenitis").
*   **Intraday Circuit Breakers:** Systematic daily loss limits act as an external mechanical constraint that halts execution before the convex region of Prospect Theory takes over.

---

### 4. Overtrading, Churn, and Transaction Costs

Overtrading affects discretionary traders via emotional impatience and systematic traders via underestimating execution friction.

*   **The Cost Drag:** Barber and Odean (*2000*, "Trading Is Hazardous to Your Wealth", *Journal of Finance*) analyzed 66,465 households and proved that **the most active traders earned the lowest net returns**. The quintile that turned over its portfolio most rapidly trailed the market by 6.5% annually, entirely due to transaction costs.
*   **The Bid-Ask Friction Trap:**
    $$\text{Net Edge per Trade} = \mathbb{E}[\text{Gross Return}] - 2 \cdot (\text{Half-Spread}) - \text{Commissions} - \text{Slippage}$$
    In short-duration setups (intraday futures), the bid-ask spread and latency slippage represent a high percentage of the target move. If your expected gross advantage on a 1.5 ATR trade is $+0.05R$, a $0.06R$ round-trip
