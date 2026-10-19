# schools - gemini

_Model opinion, not evidence. Verify every source._

### 1. School-by-School Review

---

#### 1. Smart Money Concepts (SMC) / ICT
* **Core Rules:** Price is driven by institutional liquidity seeking. The market oscillates between resting liquidity pools (equal highs/lows, swing extremes) and balance areas. Setups require an initial liquidity sweep, market structure shift (MSS/BOS), and an entry on the retest of an imbalance—typically a Fair Value Gap (FVG) or an Order Block (OB)—often during specific session "killzones."
* **Objectively Codeable:** 
  * Fair Value Gaps (3-bar pattern: bar 1 high < bar 3 low for bullish, or bar 1 low > bar 3 high for bearish).
  * Sweeps of prior swing highs/lows based on fixed pivot lookbacks (e.g., fractal $n$-bar pivots).
  * Break of Structure (BOS) defined by a candle close beyond a defined pivot.
* **Subjective / Discretionary:** 
  * Selecting *which* order block or FVG matters when several stack along a price run.
  * Determining whether an impulse constitutes "institutional displacement" or mere volatility noise.
  * Shifting narrative framing post-hoc when multiple liquidity pools exist.
* **Biggest Known Weaknesses:** 
  * Extreme narrative flexibility: almost any past price run contains unmitigated imbalances and swept pivots, enabling severe hindsight bias.
  * Raw components (OB, FVG) test poorly in isolation because they occur frequently in choppy regimes, yielding a high false-positive rate.
* **Published Evidence:** No rigorous peer-reviewed academic literature demonstrates that ICT-specific nomenclature (FVGs, OBs) outperforms standard mean-reversion or order-flow proxies. Independent quantitative audits (e.g., retail practitioner backtests across large-sample FX and futures data) uniformly show raw FVG/OB signals generate negative to flat expectation after transaction friction.

---

#### 2. Classical Price Action
* **Core Rules:** Price movement alone contains all necessary information without lagging indicators. Traders map swing highs and swing lows to define market structure (higher highs/higher lows for uptrends; lower highs/lower lows for downtrends), monitor chart patterns (flags, wedges, double bottoms), and trade trigger candle formations (pin bars, engulfing bars, inside bars) at structural inflection points.
* **Objectively Codeable:** 
  * Swing pivot definitions using strict bar algorithms (e.g., $k$-bars to the left and right).
  * Single/multi-candle formations (pin bar body-to-wick ratios, engulfing candle ranges).
  * Trendline/channel boundaries using linear regression or rolling local extrema.
* **Subjective / Discretionary:** 
  * Filtering out "low-quality" bars versus "clean" bars.
  * Adjusting trendlines dynamically across wick vs. body closes.
  * Resolving conflicting signals across adjacent timeframes.
* **Biggest Known Weaknesses:** 
  * Candle patterns in isolation have virtually zero predictive power without context (location, regime).
  * Susceptible to whipsaws in low-volatility, non-trending regimes.
* **Published Evidence:** *Brock, Lakonishok, and LeBaron (1992, Journal of Finance)* validated support/resistance and moving average breakout rules on the Dow Jones Industrial Average over 90 years, finding statistically significant predictive ability (though reduced after transaction costs). Conversely, studies on individual candlestick patterns—such as *Marshall, Young, and Rose (2006)* on DJIA stocks—found that candlestick patterns do not generate profitable investment returns once trading costs are incorporated.

---

#### 3. Elliott Wave Theory
* **Core Rules:** Financial markets move in repetitive, fractal cycles driven by collective investor psychology. Trending phases develop in 5-wave motive sequences (waves 1-3-5 directional, waves 2-4 corrective), followed by 3-wave counter-trend consolidations (waves A-B-C). Wave counts must adhere to strict cardinal axioms (e.g., Wave 3 is never the shortest; Wave 4 cannot overlap the price territory of Wave 1 in an impulse).
* **Objectively Codeable:** 
  * Structural axioms (identifying whether a potential Wave 3 is shorter than Waves 1 and 5, or checking if Wave 4 enters Wave 1 territory).
  * Automated wave counters using recursive parsing algorithms, zigzag extrema, and strict Fibonacci ratio bounds.
* **Subjective / Discretionary:** 
  * Degree assignment (determining the active timeframe degree: Minor vs. Intermediate vs. Primary).
  * Wave re-labeling: when a count fails, practitioners routinely invoke complex corrections (e.g., double/triple threes, running flats) to preserve the overall hypothesis.
* **Biggest Known Weaknesses:** 
  * Low falsifiability in real time: multiple mutually exclusive counts are almost always concurrently valid.
  * Incomputable combinatorial explosion of potential counts when applied without rigid, artificial constraints.
* **Published Evidence:** *Cowles (1934)* and later empirical evaluations of market letters (such as *Cowles, 1944*) found that forecasters relying on subjective pattern recognition—including early precursors to wave theory—failed to systematically beat the market. Quantitative algorithmic implementations of Elliott Wave (e.g., software like ELWAVE evaluated in academic surveys) show erratic, regime-dependent performance that degrades once execution costs are applied.

---

#### 4. Gann Analysis
* **Core Rules:** Markets operate on universal geometric and mathematical proportions where price and time are interchangeable ("squaring price and time"). Price movement follows specific angular vectors (e.g., $1 \times 1$ representing one unit of price per one unit of time, $2 \times 1$, $1 \times 2$) anchored to key historical extremes. Future pivot dates are projected using fixed calendar cycles and geometric planetary/astronomical intervals.
* **Objectively Codeable:** 
  * Static geometric angle rays ($P = P_0 \pm m \cdot t$) anchored to defined extrema, provided the price-per-bar scale factor is fixed.
  * Fixed calendar time cycle intervals (e.g., projecting turning points at $n$ bars or calendar days).
* **Subjective / Discretionary:** 
  * Chart scaling: Gann angles change slope if the chart’s vertical aspect ratio is adjusted; setting an objective price-to-time scaling constant ($1 \times 1 = X$ dollars/points per bar) is discretionary.
  * Astrological and esoteric cycle selection.
* **Biggest Known Weaknesses:** 
  * Lack of standard scale invariance: modern electronic markets trade at dynamic volatilities, rendering fixed price-to-time increments arbitrary unless continuously calibrated via ATR.
  * High risk of curve-fitting across numerous cycle intervals.
* **Published Evidence:** There are no peer-reviewed studies in finance demonstrating that Gann angles or astrological time cycles produce an edge. Academic literature treats Gann’s esoteric claims as unfalsifiable or pseudoscientific. Empirical backtests of fixed geometric angles typically show returns indistinguishable from random paths.

---

#### 5. Harmonic Patterns (XABCD)
* **Core Rules:** Price reversals occur at structural turning points governed by specific, tight Fibonacci ratio alignments across a 5-point swing sequence ($X, A, B, C, D$). Specific configurations (Gartley, Bat, Butterfly, Crab, Shark) require exact retracement and extension thresholds (e.g., a Bat requires a $0.382$ to $0.500$ retracement at $B$ and a $0.886$ retracement at $D$). Point $D$ defines the Potential Reversal Zone (PRZ).
* **Objectively Codeable:** 
  * Algorithmic detection of swing pivots using defined zigzag thresholds.
  * Mathematical evaluation of consecutive segment ratios against standardized tolerance bands (e.g., ratio target $\pm 5\%$).
* **Subjective / Discretionary:** 
  * The selection of ratio tolerances (e.g., allowing a $\pm 3\%$ versus $\pm 10\%$ leeway fundamentally changes pattern frequency).
  * Handling overlapping patterns pointing in opposite directions across different pivot depths.
* **Biggest Known Weaknesses:** 
  * Extremely strict criteria make genuine patterns rare; relaxing criteria leads to high false-positive rates.
  * Stop placement is often ambiguous when the PRZ spans a wide price range.
* **Published Evidence:** Few formal peer-reviewed academic papers validate harmonic patterns. Independent quantitative assessments (e.g., backtests conducted by systematic trading platforms such as QuantConnect community studies) show that while certain patterns (e.g., the Bat) display moderate directional hit rates, the edge degrades once realistic bid-ask spreads and slippage are factored into PRZ execution.

---

#### 6. Fibonacci Retracement & Extension
* **Core Rules:** Price movements retrace predictable mathematical fractions of a prior directional impulse before continuing in the prevailing direction. The primary retracement levels are $38.2\%$, $50.0\%$ (not a Fib ratio, but standard Dow theory), and $61.8\%$ (the Golden Ratio), supplemented by deep retracements ($78.6\%$, $88.6\%$) and expansion/extension levels ($127.2\%$, $161.8\%$, $261.8\%$).
* **Objectively Codeable:** 
  * Exact horizontal price coordinates calculated directly as $P = P_{\text{low}} + R \cdot (P_{\text{high}} - P_{\text{low}})$, anchored to automated pivot points.
* **Subjective / Discretionary:** 
  * Selecting the reference swing high and low (which impulse leg is the "active" leg).
  * Deciding whether wicks or closing prices define the extreme points.
* **Biggest Known Weaknesses:** 
  * Density of levels: plotting retracements ($23.6, 38.2, 50, 61.8, 78.6$) alongside extensions creates so many horizontal lines that price will naturally encounter one purely by chance.
  * Provides location only; it offers no internal timing mechanism or confirmation of structural respect.
* **Published Evidence:** *Batchelor and Ramyar (2006)* tested whether Fibonacci ratios appear in Dow Jones Industrial Average price swings and found no evidence that reversals cluster around Fibonacci levels more frequently than around random fractions. Empirical consensus indicates that standalone Fibonacci levels lack statistical significance beyond what self-fulfilling retail order clustering generates in specific liquid instruments.

---

#### 7. Sessions and Time-of-Day (Killzones / AMD)
* **Core Rules:** Intraday volatility and volume follow distinct institutional schedules governed by exchange openings, settlement periods, and algorithmic liquidity shifts. Daily range development often exhibits an "Accumulation, Manipulation, Distribution" (AMD) profile: an Asian session consolidation, a London session liquidity run (e.g., the "Judas swing" fakeout), and a New York session expansion/trend phase.
* **Objectively Codeable:** 
  * Hardcoded UTC/exchange-local time filters (e.g., London Open 07:00–10:00 UTC, NY Open 12:00–15:00 UTC).
  * Breakouts or reversals relative to the Asian Session Range (High/Low).
  * Opening Range Breakout (ORB) definitions (e.g., initial 15-minute or 30-minute bar boundaries).
* **Subjective / Discretionary:** 
  * Assigning session intent (deciding whether a breakout during London is the "manipulation" run or the start of genuine trend distribution).
  * Adjusting for Daylight Saving Time variations across non-synchronized jurisdictions.
* **Biggest Known Weaknesses:** 
  * Regimes switch frequently based on macroeconomic calendars; on days with major data releases (e.g., US CPI, FOMC), typical session mechanics collapse into news-driven momentum.
* **Published Evidence:** Time-of-day volatility clustering is heavily validated in academic market microstructure literature. *Toby Crabel (1990)* documented the viability of the Opening Range Breakout. Furthermore, extensive financial econometric studies confirm that intraday volatility follows a well-documented U-shaped or W-shaped curve around market opens, economic releases, and closes (*Andersen & Bollerslev, 1997*).

---

#### 8. Trend Following / Moving Averages
* **Core Rules:** Asset prices exhibit serial autocorrelation over medium-to-long horizons. Traders align directional exposure with the broader trend by maintaining long positions when price is above a moving average (or when a
