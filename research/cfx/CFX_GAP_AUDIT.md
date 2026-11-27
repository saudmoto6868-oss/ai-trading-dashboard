# CFX (Confluence X) — Gap and Consistency Audit

**Date:** Tuesday 10 November 2026, Africa/Cairo (UTC+2)  
**Scope:** Read-and-report only. No Pine/Python edits. No GitLab writes.  
**Owner:** Mohamed (Egyptian Arabic speaker, trader).  
**Name under review:** standalone indicator **CFX** (Confluence X), separate from the TIA tab.

## Method

Compared owner asks (parent conversation t22u–t34u on 10 Nov 2026, plus the hard rules in the earlier TIA spec) against:

| Source | Path | Role |
|---|---|---|
| Parent conversation | relayed t22u–t34u (SearchTranscripts could not open the parent session id) | Requirements |
| Sarhan research/spec | `/workspace/indicator_research/SARHAN_INDICATOR_RESEARCH_AND_SPEC.md` | Hard rules, Sarhan catalog |
| Fib + fused-osc research | `/workspace/indicator_research/FIB_SETUPS_AND_FUSED_OSC.md` | 17 fib setups; MT5 reconstruction; backtest |
| Pine draft | `/workspace/indicator_research/tia_confluence_draft.pine` (963 lines) + `.bak` + `tia_display_edit.diff` | Only Pine file in the project |
| Fused oscillator | `/workspace/indicator_research/fused_osc/fused_oscillator.py` | Research prototype (Python only) |
| CFX renderer | `/workspace/cfx/cfx_lib.py`, `build_cfx_chart.py`, `cfx_chart_meta.json`, `cfx_chart_real.png`, `cfx_settings.png` | Real-data chart + painted settings mockup |
| Jamie audit / desk risk | `/workspace/tia_audit/`, `/workspace/src/desk_risk.py` | `min_rr=2.0`, prior methodology |
| Owner MT5 screenshots | attachments folder | Only **one of four** still on disk (Amirulss). See §Screenshots. |
| Sarhan screenshots | — | **Never received on this box** (stated in the spec; re-checked). |

Every status below was checked in code, not assumed from conversation summaries.

**Status key**

| Status | Meaning |
|---|---|
| Done in Pine | Present and wired in `tia_confluence_draft.pine` |
| Done only in Python render | Computed and/or drawn by `cfx_lib.py` / `build_cfx_chart.py` (or `fused_oscillator.py`); not in Pine |
| Only in mockup/spec | Described in a markdown spec or painted on `cfx_settings.png` / earlier generated mockups; not executed |
| Missing | Not in Pine, not in Python CFX, not a working setting |
| Wrong/inconsistent | Implemented, but conflicts with another layer, with the spec, or with the owner's ask |

---

## 1. Checklist matrix

### 1.1 Product identity and packaging

| # | Requirement | Status | Evidence |
|---|---|---|---|
| P1 | Standalone name of three letters, not the TIA tab — CFX / Confluence X | Wrong/inconsistent | Python renders and `cfx_settings.png` say CFX. The only Pine file is still `indicator("TIA Confluence [DRAFT/UNTESTED]")` and lives at `tia_confluence_draft.pine`. Header comments still say TIA. `fused_oscillator.py` docstring still says “TIA fused scalp oscillator”. |
| P2 | Three presentation options: overlay on the chart / its own tab / a widget | Only in mockup/spec | Conversation and the settings footer claim “standalone CFX, not the TIA tab” and “separate branch / widget option”. There is no dashboard tab, no widget, no GitLab branch. Delivered artifacts are two PNGs plus Python/Pine drafts. |
| P3 | Can consume XPIX (and later other platform) outputs | Done only in Python render | Python copies the XPIX nearer-edge + 70% hysteresis + hide-if-both-edges > 15 ATR + 30-bar extension + `price \| 15M` / `price \| 1H` tags (orange/green). Pine has a parallel XPIX block, with the bugs in C16–C17. No live read of the dashboard XPIX module. |

### 1.2 Sarhan-style chart elements

Sarhan VIP screenshots were **never received**. Catalog is from the owner's verbal description only.

| # | Requirement | Status | Evidence |
|---|---|---|---|
| S1 | Order blocks with volume % labels | Done only in Python render | `detect_order_blocks` + chart labels `OB {vol}K ({pct}%)`. Pine has `showOb` / `obDispAtr` / `obMaxAge` / `mitigation` inputs and **never draws or detects an OB** (`showOb` is unused). Volume % formula does not match the spec (C11). |
| S2 | FVG | Wrong/inconsistent | Python: 3-candle, ≥ 0.3 ATR, fill by close, max age **40** (`FVG_MAX_AGE`). Pine: same 3-candle test, boxes created at birth and **never extended, filled, aged, or deleted** (`fvgMaxAge=30` is unused). Settings mockup prints max age 30. |
| S3 | IFVG | Done only in Python render | `detect_ifvg` exists; none in the latest window (`ifvgs: []`). Not in Pine. |
| S4 | Breaker blocks | Done only in Python render | `detect_breakers` (sweep → MSS → last opposite candle). Latest meta lists 7 bear breakers; chart draws the 2 nearest. Not in Pine. |
| S5 | Weak high / strong low labels | Missing | No detector and no labels in Pine or Python. Spec §6.3 defines them; not ported. |
| S6 | BOS / CHoCH | Done only in Python render (Pine partial) | Pine: stub using last swing + `structDir`, Arabic “تغيّر طابع” for CHoCH, labels never cleaned up. Python: `detect_bos_choch` on confirmed swings, last 7 labeled on the real chart. |
| S7 | EQH / EQL | Done only in Python render (Pine partial) | Pine: last two swings within `eqTolAtr`, shown only if `showLiqLevels` (default **false**) and unswept and near price. Python: `find_eq`; latest window has `eqh/eql: null`. |
| S8 | Liquidity / sweep marks | Done only in Python render (Pine partial) | Python marks swept PDL (4062.5, swept) and would mark EQH/EQL sweeps. Pine PDH/PDL/EQH/EQL lines are behind `showLiqLevels=false`. |
| S9 | Shooter X-Trend VWMA with HA source | Wrong/inconsistent | Pine: VWMA(120) of Heikin Ashi close when `haSource=true` (default). `trendAtrLen` / `trendAtrMult` inputs exist and are **unused** (no ATR band). Python CFX has **no VWMA and no HA filter**. Settings mockup paints “Enable VWMA-HA trend gate ON” and “HA source ON” as if live. Full Shooter settings string was never recovered (Sarhan images missing). |
| S10 | Killzones toolkit | Wrong/inconsistent | Both sides use ICT-style NY windows 20:00–00:00 / 02:00–05:00 / 07:00–10:00 `America/New_York` for the **signal** filter. Session **display** windows differ (C8). Pine killzone bgcolor is on; session shading defaults off. |
| S11 | Breakout Buy/Sell labels | Missing | Not in Pine, not in Python. Mentioned only in the Sarhan spec. |
| S12 | Arabic annotations | Wrong/inconsistent | Pine: optional Arabic for CHoCH and some trade tags (`langAr=true` default). Python chart, side panel, and settings PNG are English only. Settings mockup says “Arabic labels ON (optional)”. No `arabic_reshaper` / bidi on the CFX PNGs. |
| S13 | Historical Color, Tiny Adjusted Points `5 5 0.5 8 0`, 068 Trend `1 10` | Missing | Unresolvable without the Sarhan screenshots. |

### 1.3 Schools and per-school options

Owner asked for every school in its own card, with on/off and its own settings (conversation t22u / settings mockup “22 schools”). Hard list from the parent brief:

| # | School | Status | Evidence |
|---|---|---|---|
| K1 | SMC | Done only in Python render | Structure + OB/FVG/BOS/CHoCH scored. Always `"on": True`. No per-school inputs. Pine has structure/FVG inputs only. |
| K2 | ICT | Done only in Python render | Premium/discount mid, OTE flag, CISD line. Shallow: `ict_bull = in_ote and (bull impulse or discount)` etc. |
| K3 | CRT / CISD | Wrong/inconsistent | Python CISD: latest events, drawn as a **level line** (4085.5 bull, 4118.7 bear in meta). Python CRT: last **closed 1H** range + sweep/reclaim; `crt: null` on the latest chart; **no CRT box is drawn** anywhere in `build_cfx_chart.py`. Pine: HTF (default 4H) CISD/CRT **boxes with start/end labels**, gated by `showHtfZones` default **false**. Settings mockup says “Show HTF CISD/CRT zones ON” and “HTF 4H”. Owner asked for HTF start/end marks. |
| K4 | SMT | Done only in Python render (Pine partial) | Python: gold vs DXY, bull SMT “Gold LL not confirmed by DXY LL”, dashed purple line. Pine: `request.security(TVC:DXY)` with invert, behind `showSmt` default **false**. |
| K5 | Elliott (wave 3 / wave 5 done / correction start) | Missing | School row is hardcoded `"n/a (not computed)", "no objective 5-wave count run"`. No wave engine. Owner’s reasoning mode depends on this. |
| K6 | Gann | Missing | `"n/a (not computed)"`. |
| K7 | Harmonic | Missing | `"n/a (not computed)", "no pattern scan this pass"`. Project has a separate harmonic detector (`TOL=0.06`) that CFX does not call. |
| K8 | Wyckoff | Missing | `"n/a (not computed)"`. |
| K9 | Dow | Done only in Python render | HH/HL vs LH/LL on last two confirmed swings. |
| K10 | Fibonacci | Wrong/inconsistent | See §1.6. Latest impulse retracement only (and currently **−0.20**, i.e. already extended). Not a school with setup options. |
| K11 | Volume Profile | Done only in Python render | OHLCV histogram, 40 bins, 70% VA → POC 4128.6 / VAL 4068.8 / VAH 4142.4 on the latest window. Estimated, not tick footprint. |
| K12 | Market Profile / TPO | Missing | Not in the 21-row school list, not computed, not drawn. Owner asked for VP **and** MP/TPO. |
| K13 | VWAP | Done only in Python render | Session VWAP from typical price × volume. Drawn. School scored vs last price. |
| K14 | Pivots | Done only in Python render | Classic floor pivots from prior day H/L/C. Used only for the school score (`P 4111.6`). **Not drawn** on the chart. |
| K15 | Ichimoku | Done only in Python render | 9/26/52 state (above/below/inside cloud). Latest: below cloud, bear. **Cloud itself is not drawn.** |
| K16 | Moving averages | Done only in Python render | EMA20 / EMA50 for the school score only. Not drawn. Pine VWMA is a different MA and is drawn. |
| K17 | Supply & Demand | Done only in Python render | Aliased to “price inside a valid OB”. Neutral on the latest chart (`4 valid OB`, price not inside them). |
| K18 | Price action / candles | Done only in Python render | Pin, shooting star, engulfing, close color. Latest: “shooting star”. |
| K19 | Chart patterns | Done only in Python render | EQH → double top, EQL → double bottom **only**. No H&S, flags, wedges, etc. |
| K20 | Momentum (RSI/MACD/divergence) | Done only in Python render | RSI(14)+MACD cross for the school row (latest RSI 21, MACD −11.43 → against). Chart dots use a separate RSI/MACD/Vol swing divergence (`divs: []` this window). |
| K21 | Session opens | Done only in Python render | Scored vs New York session open only. |
| K22 | Intermarket / seasonality | Wrong/inconsistent | Intermarket: DXY 1H EMA20/50, inverted vs gold — computed. **Seasonality: missing.** |
| K23 | Each school has its own options card (on/off + parameters) | Only in mockup/spec | `school_status(..., on=True)` always. `cfx_settings.png` paints 21 toggles and “Min schools to confirm 6 of 21”. That minimum is **not coded**. Pine has no per-school groups for the 21 schools. |
| K24 | Count displayed vs owner’s 22 | Wrong/inconsistent | Side panel: “Computed 17/21”. Settings: 21 named schools. Missing MP/TPO and seasonality versus the owner’s list. |

### 1.4 Reasoning mode

Owner: the indicator should think and explain — wave count, why the reversal, 2–3 meaningful targets (POC/VAL…), how many schools agree, invalidation, weak alternative scenario. Not just toggles.

| # | Requirement | Status | Evidence |
|---|---|---|---|
| R1 | Narrative: where we are (wave 3 / wave 5 done / correction start) | Missing | No Elliott count. |
| R2 | Why this entry / why this reversal, per contributing school | Only in mockup/spec | Side panel “Why” is a short string. Latest: `No active setup — no fused hook, 1H bias flat`. The one historical trade: `Buy — fused hook, div, HTF agree`. No per-school reason list on an open idea. |
| R3 | 2–3 meaningful targets (POC, VAL, opposing liquidity, fib extensions…) | Wrong/inconsistent | Python TPs = nearest **confirmed swing highs/lows** that clear `rr1 >= 1.5`. Latest trade TP1 **4150.7** and TP2 **4156.2** are exactly two bearish OB highs in `cfx_chart_meta.json` (`obs[1].hi`, `obs[0].hi`). Not POC (4128.6), not VAL (4068.8), not PDH (4157.7) as named liquidity. Pine stub TPs are `close ± rr1Min * risk` (synthetic multiple), then last opposite swing. |
| R4 | Schools-agreeing count | Wrong/inconsistent | Panel shows Confirm 5 / Against 9 / Computed 17/21. Scoring reference is **4H EMA bias** (`side_ref = buy if bias4h == BULL`), not “does this school support the candidate trade”. With 4H still BULL and LTF structure bear (`struct_dir = -1`), nine schools go AGAINST automatically. See C6. |
| R5 | Invalidation level / condition | Done only in Python render | Trade field `invalidation` = `Close below {SL}` (or above). Side panel surfaces it. Not a structural invalidation separate from the stop (owner example: “close above 213.400 means wave 5 is still extending”). |
| R6 | Weak alternative scenario | Missing | Not generated. |
| R7 | Display at most two trades; open stays until close; then fade | Done only in Python render (Pine partial) | Python: `shown = vis_tr[-2:]`, `draw_position(..., faded)`. Latest chart: one faded BUY that hit SL (fill 10 Nov 10:15 Cairo at 4127.2, SL 4116.19 at 11:00, rr1 2.13). Pine: `TradeVis` cap of 2 + fade, but only if `showPlanDrawings` (default **false**) and only from a CHoCH stub. Pine draws lines, not TradingView-style position boxes. |

### 1.5 Divergence and fused scalp oscillator

| # | Requirement | Status | Evidence |
|---|---|---|---|
| O1 | Divergence as glowing dots on the candles, tagged with the indicator name (no separate RSI pane) | Done only in Python render | `detect_divergences` + scatter/label for RSI / MACD / Vol. Latest window: `divs: []` so nothing drawn. Not in Pine. |
| O2 | One fused oscillator in the bottom pane; BUY/SELL dots only when accurate | Wrong/inconsistent | Python pane plots `stoch_med` and dots on `sig_buy` / `sig_sell`. Caption on the chart itself: “dots = fused_loose fire **(not RR-gated)**”. Research (`FIB_SETUPS_AND_FUSED_OSC.md`): raw ~44–50% to +1R, filtered ~54%, location-or-div 58.5% on 1m (n=41). Fixed 10/90 consensus produced **zero** signals on GC=F. Owner asked for “buy where there is a buy”; the research already said that is not available from these oscillators alone. Pine has **no oscillator pane**. |
| O3 | Merge Amirulss 4-stoch (1,9,8) (1,6,3) (1,5,7) (1,8,8), levels 90 / 10 | Wrong/inconsistent | Sets match the remaining Amirulss screenshot (`Stoch(1,9,8)…(1,8,8)`, red 90 / blue 10). Engine uses those four %Ks but **adaptive 15th/85th percentiles** (lookback 200), not 90/10, because 90/10 was silent on GC=F. Settings mockup admits “Fixed 10/90 rails off (too silent on GC=F)”. |
| O4 | Merge ScalpKing RSI(1) MACD, sell 82 / buy 18 | Wrong/inconsistent | `rsi1_macd` is computed (`fast/slow/sig = 8/17/5`, levels stored as `SK_SELL, SK_BUY = 82, 18`). **Never read** by `hook_flags` or `build_fused`. The owner’s other three MT5 screenshots are **no longer on disk** (see §Screenshots), so the 8/17/5 reconstruction cannot be re-checked visually this pass. |
| O5 | Merge RSI(1) Stoch with Waiting 90 / sell 83 / sell 75 / S.B 50 / buy 25 / buy 18 / Waiting 7 | Missing | `rsi1_stoch_k/d` is computed (stoch-of-smoothed-RSI, n=8, slowing 5, D 3). Named levels and reversal-zone boxes are not implemented and not used in the signal. |
| O6 | Reversal zone boxes from the MT5 screenshots | Missing | Not drawn. |
| O7 | Do not double-count four correlated period-1 oscillators as four schools | Done only in Python render | Hook is “3 of 4” on the four stochs, then one `Fused hook` flag. RSI(1) MACD / RSI(1) Stoch are unused, so they are not double-counted — they are also not merged. Divergence-as-location (`bull_div` from median stoch) is a separate yes/no from the named RSI/MACD/Vol dots (C13). |

### 1.6 Fibonacci entry setups

Catalog from `FIB_SETUPS_AND_FUSED_OSC.md`. Owner: light lines, not heavy squares mixed into the trade boxes; setups are a **story**, not a touch.

| # | Setup | Status | Evidence |
|---|---|---|---|
| F1 | ICT OTE 62–79% (mark 70.5%) | Done only in Python render | `OTE = (0.62, 0.79)`; location flag `in_ote`. Levels 0.705 and 0.79 drawn dotted on the latest impulse. Pine: none (file header: “This draft had no Fibonacci setups; none were added.”). |
| F2 | Sweep → displacement → OTE (the “story” setup) | Wrong/inconsistent | Settings mockup: “Sweep then impulse then OTE ON”. Code: `at_location = in_ote \| in_pocket \| near_fvg \| after_sweep` (**OR**, not a sequence). A trade can fire on divergence alone with no OTE and no sweep (the 10 Nov 10:15 buy did exactly that). |
| F3 | Golden pocket 0.618–0.65 | Done only in Python render | `GOLDEN_POCKET = (0.618, 0.65)`; both levels drawn. |
| F4 | Classic 38.2 / 50 / 61.8 | Wrong/inconsistent | 0.5 is computed in `latest_impulse` levels and **not drawn**. 0.382 is not computed. 0.618 is drawn as “0.618 GP”. |
| F5 | Deep 0.786 / 0.886 | Missing | Not in the levels dict `(0.0, 0.5, 0.618, 0.65, 0.705, 0.79, 1.0)`. |
| F6 | Parabola Pop (break 0.786 toward 1.0) | Only in mockup/spec | Settings row “Parabola Pop (break 0.786) OFF”. No detector. |
| F7 | Fib + OB / FVG confluence | Missing | No intersection test. Location OR’s `near_fvg` with OTE but does not require overlap. |
| F8 | ICT extensions −0.27 / −0.62 / −1 / −2 (targets) | Missing | Not computed. TPs are swing highs/lows. |
| F9 | Fib time / fan / channel | Missing | — |
| F10 | Fib + CHoCH / BOS | Missing | CHoCH is separate; not combined with a fib zone as an entry rule. |
| F11 | Breaker / Unicorn (breaker + FVG + OTE) | Missing | Breakers are detected; Unicorn (`breaker ∩ FVG`) is not. |
| F12 | Elliott wave 2 / wave 4 fib | Missing | Depends on K5. |
| F13 | Fibonacci Flush (same ratio, multiple TFs) | Missing | — |
| F14 | AB=CD / measured move | Missing | — |
| F15 | Cluster (several impulses at one price) | Missing | — |
| F16 | Fib display: light, not heavy filled squares colliding with trades | Wrong/inconsistent | Lines are thin and dotted (good). They are still drawn across the latest **already-extended** bear impulse (`retracement: -0.204`), so 0.618–0.79 sit at 4113–4124 — straight through the faded trade box (entry 4127.2 / SL 4116.2). Owner asked specifically for this not to happen. |

### 1.7 Order-flow marks

| # | Requirement | Status | Evidence |
|---|---|---|---|
| OF1 | SMT line | Done only in Python render (Pine partial) | See K4. Estimated from two OHLCV series (gold vs DXY), not DOM. |
| OF2 | Absorption | Missing | No detector. Earlier mockups labeled estimated absorption; current real chart does not. |
| OF3 | Exhaustion | Missing | — |
| OF4 | Imbalance (stacked buying/selling) | Missing | The word “imbalance” in `fused_oscillator.py` refers to a 3-candle FVG, not order-flow imbalance. |
| OF5 | Delta divergence | Missing | No tick/delta/footprint feed. `data_reality` would be OHLCV (spec). |
| OF6 | POC / VAH / VAL | Done only in Python render | Estimated by spreading each bar’s volume uniformly across its high–low. Not a real profile. Drawn as thin dash-dot lines. |

### 1.8 Display, sessions, MTF, XPIX, style

| # | Requirement | Status | Evidence |
|---|---|---|---|
| D1 | At most two trades on the chart | Done only in Python render (Pine partial) | See R7. |
| D2 | Open trade stays visible until close, then fades | Done only in Python render (Pine partial) | Python faded the SL trade. Pine fade exists but is off by default. |
| D3 | TradingView-style position boxes (entry / SL / TP zones) | Done only in Python render | `draw_position` uses filled rectangles (SL red, TP green) plus `BUY 2.1R`. Pine uses horizontal lines + a start bar, not boxes. |
| D4 | Trend line | Done only in Python render (Pine partial) | Python: last two swings in structure direction, extended. Pine: same idea, `showTrendLine` default **false**. |
| D5 | SMT line | See K4 / OF1 | — |
| D6 | HTF CISD/CRT zones marked start and end | Wrong/inconsistent | See K3. |
| D7 | Multi-timeframe alignment in the **signal** | Wrong/inconsistent | Settings: “Require MTF alignment (4H+1H+current) ON”. Pine: `useMtfFilter=true`, alignment = HTF VWMA + 1H VWMA + current VWMA-HA. Python `attach_htf`: `htf_bull = htf_1h_bull` — **4H is not a gate**. 4H is used only as the school-board reference. Daily HTF veto from the spec is absent on both sides. |
| D8 | Session awareness on display and in logic | Wrong/inconsistent | Python always shades Asia/London/NY using **Cairo wall-clock** `(2,9), (9,16), (15,24)` and draws session H/L. Pine session shade / H/L / filter default **false**; session strings are in `America/New_York` and do not match the Cairo windows (C8). Killzone filter is separate and is ON in both signal paths. |
| D9 | Relevant highs/lows (liquidity, PDH/PDL, session H/L) | Done only in Python render (Pine partial) | Python draws PDH/PDL (swept PDL 4062.5), session H/L (skips ones that coincide with XPIX/PDL), swing markers. Pine behind defaults-off flags. No weak/strong labels (S5). |
| D10 | XPIX-style 15M / 1H last-**closed** H/L | Wrong/inconsistent | Python matches the documented XPIX rules and is drawn (15M 4061.1 orange, 1H 4046.4 green, both nearer lows). Pine implements the same geometry but (a) uses `lookahead=barmerge.lookahead_on` with `high[1]` (C17), and (b) hides a TF unless `f_tfHigher(tf)` — on a **15m chart the 15M level is hidden** (C16). |
| D11 | Style like the owner’s reference screenshots | Wrong/inconsistent | FVG/OB/BRK/BOS/CHoCH are now on the real chart (owner t33u). Fib is lighter than the earlier mockups but still cuts the trade. No Sarhan screenshots to match against. Earlier AI mockups had errors (SL on the wrong side of a short — called out at the time); the current **real** chart’s SL is on the correct side of the long. |

### 1.9 Hard rules from the TIA / Jamie spec

| # | Requirement | Status | Evidence |
|---|---|---|---|
| H1 | HTF veto (daily **and** 4H against → WAIT) | Missing | Not in Python `build_fused` (1H only). Not in the Pine plan stub (Pine MTF is VWMA of 4H+1H+current, which is an alignment filter, not the daily+4H veto). Gold 10 Nov is the exact case the spec cited: 4H still BULL while LTF sold off. |
| H2 | Then POI (unmitigated OB / FVG / OTE in discount/premium) | Missing | Python can fire on `at_location **OR** div`. The 10 Nov 10:15 buy had no OTE, no FVG, no sweep in `schools` — only hook + div + HTF. |
| H3 | Then sweep | Missing | `after_sweep` is optional inside the OR. |
| H4 | Then LTF CISD or CHoCH (body) | Missing | Python trigger is the fused hook + confirming candle, not CISD/CHoCH. Pine stub uses CHoCH only, and only if `showPlanDrawings`. |
| H5 | Then limit entry at FVG/OB (mid or edge) | Missing | Python fill = **next bar open** (`entry = o[j]`). Pine stub = **current close**. Neither places a limit on a POI. |
| H6 | SL = structural swing + 0.15 ATR | Done only in Python render (Pine partial) | Both use `SL_BUF_ATR = 0.15` / `slBufAtr`. Python: last confirmed swing high/low ± buffer. Pine stub: `lastSl - slBufAtr * atr`. |
| H7 | TP at opposing liquidity | Wrong/inconsistent | See R3. Python uses qualifying swing H/L (which, on 10 Nov, were bearish OB highs). Pine uses RR multiples. |
| H8 | `rr1 >= 1.5` hard gate (do not pass via rr2) | Wrong/inconsistent | Both CFX layers use 1.5 (`RR1_MIN`, `rr1Min`). `/workspace/src/desk_risk.py` `DeskRules.min_rr = 2.0` (meeting 8 Nov 2026). Documented as an open owner question in the spec §8.2. The one plotted trade had rr1 = 2.13, so it would pass either number; the conflict is still unresolved. |
| H9 | Risk 0.5% | Only in mockup/spec | Pine input `riskPct=0.5` is display-only and unused. Python does not size a position. `desk_risk.risk_pct = 0.5` exists outside CFX. |
| H10 | Killzone + news blackout (30 min before / 15 after high-impact) | Wrong/inconsistent | Killzone: yes, on the signal. News blackout: **missing** in Pine and Python (spec lists it as a TODO in the Pine comments). |
| H11 | Spread / cost model; reject if `cost_R > 0.20` | Wrong/inconsistent | `SPREAD_USD = 0.30` is applied only inside `fused_oscillator.evaluate_signals` (research backtest). `build_trades` (what the CFX chart uses) has **no spread, no cost_R**. |
| H12 | No edge claim until `n>=30` to show / `n>=100` and `t>3` to claim | Only in mockup/spec | Research report followed this in prose. No runtime gate. Chart footer: “Research only, no edge claimed.” |

---

## 2. Conflicts (verified)

### C1 — The project is still named TIA in the only Pine file
`tia_confluence_draft.pine` title, tables, and comments say “TIA Confluence”. CFX exists as a Python renderer and two PNGs. There is no `cfx_*.pine`.

### C2 — Fused oscillator exists only in Python
`fused_oscillator.py` (research) + `cfx_lib.build_fused`. Pine `overlay=true` has no pane and no stoch/RSI(1) logic.

### C3 — Fibonacci setups are absent from Pine
Stated in the Pine header itself. Python has OTE + golden-pocket **flags** and four light level lines. The other 13 cataloged setups are not in either codebase.

### C4 — Elliott / Gann / Harmonic / Wyckoff are not computed
Honestly labeled `n/a (not computed)` on the school board. Settings still show them as “ON”.

### C5 — Order flow is estimated from OHLCV
SMT = gold vs DXY swing comparison. VP = uniform volume across each bar’s range. No absorption, exhaustion, imbalance, delta, or footprint. Earlier mockups that labeled “Order flow = estimated” were more honest than the current silent real chart.

### C6 — School scores are measured against 4H bias, producing “5 confirm / 9 against”
`build_bundle` sets `side_ref` from `bias4h` (latest: BULL) then marks every school confirm/against relative to that side. LTF structure is bear (`struct_dir = -1`). Result: SMC, Dow, VWAP, Pivots, Ichimoku, MAs, PA, Momentum, Session Opens = against; ICT (discount), CRT/CISD (bull CISD), SMT, VP, Intermarket = confirm. This is not “how many schools support this trade”. It is “how many schools currently agree with a still-bullish 4H EMA while price is dumping”. That is why the board looks like a pile of AGAINST during the exact move the owner is looking at.

### C7 — `rr1` 1.5 vs desk `min_rr` 2.0
CFX/Pine/spec proposal: 1.5. `desk_risk.py` line 20: 2.0, citing the 8 Nov 2026 meeting. Still an open owner decision.

### C8 — Session clocks: Cairo display vs New York Pine vs killzones
| Layer | Asia | London | New York |
|---|---|---|---|
| Python display (`session_flags`, Cairo hours) | 02:00–09:00 Cairo (= 19:00–02:00 NY in November) | 09:00–16:00 Cairo (= 02:00–09:00 NY) | 15:00–00:00 Cairo (= 08:00–17:00 NY) |
| Pine session inputs (tz = `America/New_York`) | 19:00–04:00 | 03:00–12:00 | 08:00–17:00 |
| Killzone (both, `America/New_York`) | 20:00–00:00 | 02:00–05:00 | 07:00–10:00 |

Asia and London **display** windows do not match between Python and Pine. Killzones match each other and the spec, and they are the windows that actually gate signals. Settings mockup prints both sets without saying they disagree.

### C9 — Sessions / SMT / trend / HTF zones / liquidity default OFF in Pine, ON in the Python render
Pine: `showTrendLine`, `showSmt`, `showHtfZones`, `showSessShade`, `showSessHL`, `showLiqLevels` all default false. Owner asked to **see** them. The Python PNG always draws them. Anyone pasting the Pine file into TradingView will not see what the PNG shows.

### C10 — `showPlanDrawings` defaults false, so Pine shows no trades
The 2-trade / fade engine never runs unless that box is checked. Even then, plans are a CHoCH stub, not the fused model.

### C11 — Order-block volume % does not mean what the spec says
Spec §6.3 (LuxAlgo-style): `vol_ob / sum(vol of displayed OBs) * 100`.  
Code (`detect_order_blocks`): `100 * volume[ob_bar] / sum(volume[ob_bar-19 : ob_bar])`.  
That is “this candle’s share of its own 20-bar window”, so the on-chart 3%, 3%, 8%, 5% cannot be compared with each other the way a “share of visible OBs” label implies. Futures volume on `GC=F` is real contract volume, not FX tick volume — the label does not say which.

### C12 — The plotted trade targeted bearish order-block highs, not named liquidity
Trade (Cairo times): signal 10:00, fill 10:15 at **4127.2**, SL **4116.19** (last swing − 0.15 ATR), TP1 **4150.7**, TP2 **4156.2**, rr1 **2.13**, outcome **SL** at 11:00.  
`obs` in the same meta file: one bear OB high = 4150.700, another = 4156.200. Those TPs are swing highs that also *are* those OBs (supply), not POC/VAL/PDH. The buy also had no OTE, no FVG, and no sweep — it was hook + stoch-median divergence + 1H/4H still bullish. This is the “gives a buy where there is no buy” failure mode the owner flagged, showing up on the real chart.

### C13 — Two different “divergence” definitions
1. Signal path (`build_location_and_div`): regular div of **median period-1 stoch** vs price swings. This is what tagged the 10:15 trade as “div”.  
2. Chart dots (`detect_divergences`): regular div of RSI(14), MACD line, and volume. Volume **bull** uses an inverted rule (`o2 < o1`, “smaller second volume”) vs oscillators (`o2 > o1`); volume **bear** uses `o2 < o1` (same comparison as oscillators, which happens to be correct for “lower volume on a higher high”). Latest window drew **no** dots (`divs: []`) while the trade still claimed osc divergence from definition (1).

### C14 — HA source for VWMA
Present in Pine (filter only; decision OHLC stay real). Absent in Python CFX. Settings mockup shows it ON for CFX.

### C15 — Settings PNG over-claims
`cfx_settings.png` is painted by `render_settings()` from a hardcoded `SETTINGS_GROUPS` list. Footer: “Inputs match the edited Pine draft plus the fused oscillator, Fibonacci setups, and school toggles.” That is false: many rows are not Pine inputs, not Python kwargs, and not wired (VWMA-HA, Parabola Pop, Arabic, min 6 of 21 schools, HTF CISD/CRT zones ON, MTF 4H+1H+current, FVG max age 30 vs code 40, CISD max age 6 vs Python draw/score cutoffs 20/12).

### C16 — Pine hides the 15M XPIX level on a 15-minute chart
`f_xpixDraw(..., f_tfHigher("15"), ...)`. `f_tfHigher` is true only when the chart TF is **below** 15m. The CFX working chart is 15m, so a user who copies the Pine file will not see the orange 15M line that the PNG shows.

### C17 — Pine XPIX uses `lookahead_on`
```
request.security(..., [high[1], low[1]], lookahead=barmerge.lookahead_on)
```
The `[1]` offset is meant to be the last closed HTF bar. Combining it with `lookahead_on` is an unnecessary lookahead footgun and disagrees with the MTF alignment calls, which correctly use `lookahead_off`. Python’s `last_closed_bar` is the safer equivalent.

### C18 — Pine FVG / label leak and unused inputs
Every qualifying FVG spawns a `box.new` that is never deleted or mitigated. BOS/CHoCH spawn `label.new` forever. On a long history this will hit `max_boxes_count=200` / `max_labels_count=200`. Unused inputs (so the settings lie): `showOb`, `obDispAtr`, `obMaxAge`, `mitigation`, `fvgMaxAge`, `trendAtrLen`, `trendAtrMult`. `riskPct` is unused by design (commented display-only).

### C19 — Other Pine syntax / runtime risks (uncompiled)
The file states it is untested and there is no Pine compiler here. Additional risks from reading the source: UDT (`TradeVis`) values taken from an array and mutated (`t.isOpen := false`) — Pine array-of-UDT reference semantics are easy to get wrong; HTF CISD/CRT reconstruction walks arrays of `request.security` values only when `ta.change(htfT) != 0`; CRT right-edge uses `int(math.max(t1, time))` mixed with `xloc.bar_time`. None of this has been compiled.

### C20 — Double-counting / unused MT5 siblings
The four period-1 stochs are fused (good). The two other MT5 indicators the owner sent are reconstructed and then ignored, so the “one fused oscillator” does not actually merge all three screenshots. Adaptive zones also mean a BUY dot on GC=F 15m is not the same event as a 90/10 cross on the owner’s XAUUSD M1 broker feed (the Amirulss screenshot shows the four lines pinned at 0 and 100 on M1; the research noted that mismatch).

### C21 — Data: GC=F futures, not XAUUSD spot
Chart subtitle and meta are explicit (`yfinance GC=F`, last 4063.9 at 10 Nov 2026 15:45 Cairo). Owner screenshots are XAUUSD. Levels will not match a spot gold TradingView chart.

### C22 — Min impulse length 1.5 ATR vs project `ote_bull` 2.5 ATR
`MIN_LEG_ATR = 1.5` in the fused/CFX code. The project detector documented in the spec uses 2.5 ATR. Settings mockup prints 1.5.

### C23 — Earlier AI mockups vs the real chart
A previous generated mockup had a short with the stop on the wrong side of entry (called out when it was sent). The current `cfx_chart_real.png` long has a correct SL below entry. Do not treat older mockups as ground truth.

---

## 3. Screenshots

- **Sarhan signals VIP (~20 TradingView captures):** never landed on this box. Spec §7 verification list is still open (full Shooter settings after `6...`, which Killzones Toolkit, Historical Color, Tiny Adjusted Points, 068 Trend, breakout-label source, GBPJPY 212.900 geometry, etc.).
- **Owner MT5 captures (conversation t25ua0, four files):** only  
  `/home/box/agent-data/agents/e54dad2b-9120-452e-a196-e100da1af35d/attachments/6e6bea018df0d6602843e73167cbda92f2000b5e852c2b5f8cfafb64e1e58e90.png`  
  is still present. It confirms Amirulss “FINAL STOCHASTIC OSCILLATOR” on XAUUSD M1 with `Stoch(1,9,8) (1,6,3) (1,5,7) (1,8,8)` and rails at 90 / 10. The other three hashes from that turn (`d03ad69a…`, `301b56cf…`, `38d89185…` — ScalpKing RSI(1) MACD and RSI(1) Stoch, plus the fourth frame) return file-not-found now. Reconstruction of 82/18 and Waiting/sell/S.B/buy levels therefore rests on the earlier conversation notes, not on a re-view.

- **Current CFX artifacts:** `cfx_chart_real.png` (GC=F 15m, Fri 6 Nov 01:00 → Tue 10 Nov 15:45 Cairo, last 4063.9) and `cfx_settings.png` (painted, not a live UI).

---

## 4. What actually works today (so the gaps are in context)

Python render, on real GC=F data, does compute and draw: candles; session shading; unfilled FVGs; nearest OBs with a volume label; nearest breakers; BOS/CHoCH tags; premium/discount 50% line; VP POC/VAH/VAL; session VWAP; light fib of the latest impulse; trend line; SMT vs DXY; PDH/PDL + sweep mark; session H/L; CISD level line; XPIX 15M/1H; at most two TV-style position boxes with fade; a fused-osc pane with ungated BUY/SELL dots; a 21-row school board that honestly marks four schools n/a.

Pine draft does: VWMA-HA filter (partial), killzone windows, Arabic CHoCH tags, stub BOS/CHoCH/FVG, optional (default off) sessions / SMT / trend / HTF CISD-CRT boxes / EQH-EQL / PDH-PDL, XPIX geometry, and a default-off 2-trade fade engine.

Neither layer implements the sequential entry engine the spec and the owner described.

---

## 5. Top missing items

1. Sequential entry engine: HTF veto → POI → sweep → LTF CISD/CHoCH → FVG/OB **limit** (H1–H5). Current Python trigger is fused-hook + (location OR divergence) + 1H bias.
2. Reasoning mode: Elliott wave state, per-school “why”, named targets (POC/VAL/opposing liquidity/extensions), invalidation that is not just the stop, weak alternative (R1–R3, R6).
3. Elliott, Gann, Harmonic, Wyckoff engines (K5–K8) — required for the wave narrative and for several fib setups (F12).
4. Most Fibonacci setups (F5–F15): 0.786/0.886, Parabola Pop, extensions, time/fan/channel, fib+OB/FVG, fib+CHoCH, Unicorn, Flush, AB=CD, cluster, W2/W4.
5. Fused oscillator in Pine, and a real merge of all three MT5 indicators (O2, O4, O5, O6). RSI(1) MACD and RSI(1) Stoch are computed then ignored.
6. Order-flow marks the owner asked to see: absorption, exhaustion, stacked imbalance, delta divergence (OF2–OF5). True footprint data is not in the feed; anything drawn from OHLCV must stay labeled estimated.
7. Market Profile / TPO and seasonality (K12, K22).
8. Weak high / strong low, breakout labels, news blackout, live spread/`cost_R` gate, position sizing at 0.5% (S5, S11, H9–H11).
9. A CFX-named Pine file, plus the tab/widget shells (P1, P2).
10. Sarhan-only items that cannot be finished until those screenshots arrive: Shooter full settings, Historical Color, Tiny Adjusted Points, 068 Trend, breakout-label source (S9, S13).
11. Per-school option cards and the “min 6 of 21 must confirm” rule (K23) — painted only.

## 6. Top wrong / conflicting items

1. School board scored against 4H EMA bias → 9 AGAINST while LTF is bear (C6).
2. 10 Nov 10:15 buy fired without POI/sweep/CISD, TPs landed on bearish OB highs, then hit SL (C12). Oscillator dots are explicitly not RR-gated (O2).
3. Settings PNG and school toggles over-claim what the code does (C15, C4).
4. Pine still titled TIA; defaults hide sessions/SMT/trend/HTF zones/liquidity/trades; 15M XPIX hidden on a 15m chart; unused OB/fib/HA-band inputs (C1, C9, C10, C16, C18).
5. Fib drawn on an already-extended impulse (retracement −0.20) cutting through the trade box (F16); “sweep then OTE” is an OR, not a story (F2).
6. Two divergence definitions; volume-bull rule inverted vs RSI/MACD (C13).
7. OB volume % formula ≠ spec (C11).
8. `rr1` 1.5 vs `desk_risk.min_rr` 2.0 still unresolved (C7).
9. Session display clocks disagree (Cairo Python vs NY Pine) (C8).
10. HA VWMA exists only in Pine; Python MTF gate is 1H-only, not 4H+1H+current as advertised (C14, D7).
11. CRT: Pine = 4H boxes off-by-default; Python = 1H sweep/reclaim, currently null, never drawn (K3).
12. GC=F vs XAUUSD; adaptive 15/85 zones vs the owner’s 90/10 M1 screenshot (C20, C21).

---

## 7. Recommended fix order

Each item is one line: what to change, not a redesign.

1. **Decide the open product questions first:** name the Pine file CFX; pick `rr1` 1.5 or 2.0; state that order-flow beyond SMT/VP is estimated unless a footprint feed is connected; confirm GC=F vs XAUUSD as the development symbol.
2. **Stop the settings PNG from lying:** generate it from real flags, drop rows that are not wired, and mark Elliott/Gann/Harmonic/Wyckoff as n/a until engines exist.
3. **Rescore schools against the candidate trade (or “no trade”), not against raw 4H EMA bias** — this single change fixes the 5-vs-9 board the owner is looking at.
4. **Make the entry pipeline sequential** in `build_fused` / `build_trades`: HTF daily+4H veto, then POI in premium/discount, then sweep, then LTF CISD/CHoCH (body), then limit at FVG/OB; remove `location OR div` as a sufficient trigger.
5. **Point TPs at named opposing liquidity** (unswept EQH/EQL, PDH/PDL, session H/L, then POC/VAL/VAH or ICT extensions), and keep `rr1` as a gate, not as the target itself.
6. **Gate oscillator dots with the same pipeline + RR** (or stop labeling ungated hook-fires as BUY/SELL). Use 90/10 as an optional rail; keep adaptive zones as a research fallback, clearly labeled.
7. **Actually merge the three MT5 oscillators into one hook** (4-stoch consensus AND RSI(1) MACD extreme AND RSI(1) Stoch zone), and count the bundle as one momentum confirmation.
8. **Fib: draw only when price is inside a live retracement of a valid impulse; implement the story setup (sweep → displacement → OTE) as AND; add 0.382 / 0.786 / 0.886 and ICT extensions; leave Pop/time/fan/channel/Unicorn behind explicit off defaults.** Keep lines light and clipped so they do not cross an active position box.
9. **Align clocks and defaults:** one session table (display vs killzone vs Cairo labels); turn Pine display flags on to match the PNG (sessions, SMT, trend, HTF zones, liquidity); set `showPlanDrawings` semantics to the real engine, not the CHoCH stub.
10. **Fix Pine packaging and XPIX:** rename to CFX; draw OB/IFVG/Breaker or remove those inputs; delete unused inputs or wire them (`fvgMaxAge`, mitigation, HA ATR band); expire FVG boxes; use `lookahead_off` and show 15M levels on a 15m chart (`tf >=` not `tf >`).
11. **HTF CISD/CRT:** one definition (owner asked for higher-TF start/end boxes). Port the Pine 4H zone drawing into Python (or the other way around) and stop advertising 4H while computing 1H.
12. **Honest OB volume %:** either `vol_ob / sum(displayed OBs)` as specified, or label the 20-bar share as “bar vol % of 20”.
13. **One divergence function** for both dots and signals, with the volume rule documented (lower second volume = non-confirmation on both sides).
14. **Add news blackout + `cost_R` to `build_trades`** (spread model already sketched in `evaluate_signals`).
15. **Then** the larger engines: Elliott count (unlocks reasoning + W2/W4), Harmonic, simple Wyckoff phases, Gann as context-only, Market Profile/TPO, seasonality, weak/strong highs and lows, breakout labels — each behind its own off-by-default switch.
16. **Do not claim accuracy or edge** until the sequential engine has `n>=30` visible trades and `n>=100` with `t>3` after costs. The fused oscillator research already failed that bar.

No files other than this audit were modified. No GitLab write was made.
