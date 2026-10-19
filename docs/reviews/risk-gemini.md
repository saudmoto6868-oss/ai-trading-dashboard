# risk - gemini

_Model opinion, not evidence. Verify every source._

This summary synthesizes the mathematical principles, practitioner frameworks, and peer-reviewed literature on risk management and retail trader survival, with a focus on futures and short-horizon trading.

---

### 1. Break-Even Win Rate vs. Reward-to-Risk (R:R)

#### The Mathematical Baseline
The break-even win rate ($W_{\text{be}}$) for a strategy with a fixed stop-loss ($S$) and take-profit ($T$)—where reward-to-risk ratio $R = T / S$—is defined as:

$$W_{\text{be}} = \frac{1}{1 + R}$$

* *Examples:* 
  * $0.5\text{R}$ ($R = 0.5$): Requires $66.7\%$ win rate to break even.
  * $1.0\text{R}$ ($R = 1.0$): Requires $50.0\%$ win rate to break even.
  * $1.5\text{R}$ ($R = 1.5$): Requires $40.0\%$ win rate to break even.
  * $2.0\text{R}$ ($R = 2.0$): Requires $33.3\%$ win rate to break even.
  * $3.0\text{R}$ ($R = 3.0$): Requires $25.0\%$ win rate to break even.

#### First-Passage Realities & Friction
Under a pure geometric random walk (martingale) without drift or friction, the probability of hitting a target before a stop is exactly $1 / (1 + R)$. Real-world performance deviates significantly due to:

1. **Transaction Cost Asymmetry:** When commissions, exchange fees, bid-ask spread, and slippage are factored in, real risk increases to $S + C$ and real reward shrinks to $T - C$. 
   $$W_{\text{be, net}} = \frac{S + C}{(S + C) + (T - C)} = \frac{S + C}{S + T}$$
   As $S$ tightens (e.g., sub-ATR intraday scalping), $C$ becomes a massive percentage of the trade, steepening the required win rate exponentially.
2. **Path Dependency / Inverse Relationship:** Empirical market studies show that realized win rates decay sharply as $R$ increases. High-R targets require price to travel through wider noise bands, drastically increasing the probability of boundary-crossing at the stop-loss first (*Feller, 1968, "An Introduction to Probability Theory and Its Applications"*).

---

### 2. Sizing Frameworks: Fixed Fraction & The Kelly Criterion

#### Fixed-Fractional Sizing
* **Definition:** Risking a fixed percentage $f$ of total portfolio equity on each trade ($Position\ Size = \frac{\text{Equity} \times f}{\text{Distance to Stop}}$).
* **Mechanics:** 
  * Scales position sizes dynamically down during drawdowns (delaying or mathematically preventing absolute ruin) and up during equity peaks.
  * Introduces an **asymmetric recovery burden**: a $50\%$ drawdown requires a $100\%$ gain to recover.

#### Kelly Criterion & "Optimal $f$"
* **Kelly Formula:** $f^* = \frac{p(b+1) - 1}{b} = p - \frac{q}{b}$  
  *(where $p$ = win rate, $q = 1-p$, $b$ = ratio of average win to average loss).*
* **Optimal $f$ (Ralph Vince, 1990):** In *Portfolio Management Formulas*, Vince expanded Kelly to empirical non-normal trade distributions.
* **The Reality of Full Kelly:** While mathematically maximizing asymptotic geometric growth ($G$), "Full Kelly" sizing is notoriously dangerous in practice:
  * Has a $1/3$ probability of halving account equity before doubling it.
  * Generates extreme drawdowns (frequently exceeding $70\%-80\%$).
* **Practitioner Consensus (Fractional Kelly):**
  * Systematic and quantitative desks generally cap risk at **Half-Kelly** ($0.5 f^*$) or **Quarter-Kelly** ($0.25 f^*$). Fractional Kelly captures $75\%$ to $90\%$ of optimal growth while slashing drawdown depth and variance substantially (*MacLean, Ziemba, & Thorp, 2011, "The Kelly Capital Growth Investment Criterion"*).
  * In discretionary and institutional intraday trading, fixed fraction risk per trade is commonly kept between **$0.25\%$ and $1.0\%$** of NAV.

---

### 3. Daily Loss Limits & Circuit Breakers

#### Mathematical & Empirical Rationale
* **Volatility and Return Clustering:** Returns in financial assets are not identically and independently distributed (i.i.d.). Volatility clusters over time (Mandelbrot, 1963; Engle, 1982 ARCH model). Days with abnormal losses often correlate with abnormal market regimes (liquidity vacuums, macroeconomic shocks) where normal model edges break down.
* **Non-Stationary Regimes:** A systematic strategy's edge is conditional on market state. Repeated intra-day losses flag a high probability that the current intraday environment is out-of-distribution for the strategy.

#### Behavioral Rationale
* **Loss Aversion and Prospect Theory:** Kahneman & Tversky (1979) proved that individuals are risk-averse in the domain of gains, but **risk-seeking in the domain of losses**. 
* **The "Tilt" Effect:** After breaching a threshold loss, discretionary traders systematically widen stops, increase leverage, and enter low-conviction setups to get back to flat (the break-even effect).
* **Practitioner Standard:** Hard daily circuit breakers (e.g., stopping all trading for the day at $-2\text{R}$ or $-3\text{R}$, or $1.5\%-2.0\%$ of equity) act as an external governor preventing account ruin.

---

### 4. Overtrading & Transaction Drag

#### Turnover vs. Net Performance
Overtrading damages performance through two mechanisms:

1. **The Cost Hurdle:** 
   * In futures contracts (e.g., E-mini S&P 500, micro contracts), round-turn exchange fees, broker commissions, and half-spread costs compound with every trade.
   * If a strategy has an edge of $0.05\text{R}$ per trade gross, and average transaction drag is $0.07\text{R}$, the strategy flips from positive to deeply negative expectation exclusively due to trade volume.
2. **Signal Degradation
