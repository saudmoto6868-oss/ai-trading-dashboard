# CFX fix log — 10 November 2026, Africa/Cairo (UTC+2)

Fixes applied on box files under `/workspace/cfx/` only. No GitLab commit, branch, push, or merge.
Originals kept in `/workspace/cfx/backups/`.

**Decisions used:** name CFX; `rr1` minimum 1.5 (gate only); data = yfinance `GC=F` labeled as gold futures; order-flow beyond SMT/VP omitted or labeled estimated; news calendar = manual hook (empty list, no feed).

---

## Deliverable paths

| File | Role |
|---|---|
| `/workspace/cfx/cfx.pine` | Renamed Pine overlay (from `tia_confluence_draft.pine`) |
| `/workspace/cfx/cfx_pipeline.py` | Sequential engine, merged hook, named TPs, news hook, Elliott zigzag (off) |
| `/workspace/cfx/cfx_lib.py` | Detectors + bundle; now calls the pipeline |
| `/workspace/cfx/build_cfx_chart.py` | v2 renderer + honest settings |
| `/workspace/cfx/cfx_chart_real_v2.png` | Real GC=F 15m chart |
| `/workspace/cfx/cfx_settings_v2.png` | Settings listing only wired options |
| `/workspace/cfx/cfx_chart_meta_v2.json` | Numbers behind the chart + backtest |
| `/workspace/cfx/backups/` | Pre-fix copies of lib, renderer, pine, old PNGs |

---

## Backtest (sequential pipeline, GC=F 15m)

- Window: 2026-09-01 00:00 America/New_York → 2026-11-10 08:45 America/New_York (~70 calendar days of cached yfinance 15m).
- Symbol: `GC=F` gold futures, not spot XAUUSD.
- Spread: 0.30 USD, rejected if `cost_R > 0.20`. Same-bar SL+TP counted as SL.
- First-exit R: SL = −1R − cost_R; TP1 / TP2 / TP1-then-SL = +rr1 − cost_R.

| Metric | Value |
|---|---|
| n taken / decided | 83 / 83 |
| n still open | 0 |
| n TP1 or better | 31 (of which TP2 = 26, TP1-then-SL = 5) |
| n SL first | 52 |
| Hit rate (TP1 vs SL) | 37.35% |
| Average R after cost | +0.238R |

n = 83 ≥ 30, so the numbers may be shown. n < 100, and no t-statistic was computed, so **no edge is claimed**. A 37% hit rate at a ≥1.5R first target can print a small positive average R from payoff asymmetry; that is not evidence the oscillator “buys where there is a buy.”

---

## What the v2 chart actually shows

Window: Friday 6 Nov 2026 01:00 → Tuesday 10 Nov 2026 15:45 Africa/Cairo. Last print **4063.9**. 4H bias **BULL**, daily bias **BEAR**, LTF structure **bear** (`struct_dir = -1`).

**No open trade.** Banner: “No active setup — no live fib retracement.” Schools: 0 confirm / 0 against / 17 watch as `no trade` / 4 n/a. This replaces the old “5 confirm / 9 against vs 4H EMA” board.

Two faded historical trades in the window (cap of 2):

1. **BUY** filled 9 Nov 18:45 Cairo at 4120.6 (signal 16:15), SL 4098.4, TP1 ext 1.62 at 4162.79 (1.9R), TP2 ext 2.0 at 4177.5. POI = breaker. Outcome **SL** at 10 Nov 11:00. cost_R = 0.014.
2. **SELL** filled 10 Nov 03:30 Cairo at 4148.53 (signal 03:15), SL 4157.53, TP1 Asia L 4130.8 (1.97R), TP2 ext 1.27 at 4123.94. POI = OTE after sweep 4156.2. Outcome **TP2** at 04:30. cost_R = 0.033.

Other drawn facts (computed, not invented):

- XPIX 15M 4061.1 (orange), 1H 4046.4 (green) — last closed nearer edge.
- 2 unfilled FVGs, 6 visible OBs labeled as share of visible OBs, 8 breakers (nearest drawn).
- HTF 4H CRT box 4135.5–4089.1, no sweep/reclaim yet; 2 HTF CISD start/end boxes.
- LTF CISD levels 4085.5 (bull, age 7) and 4118.7 (bear, age 19).
- PDL 4062.5 swept; PDH 4157.7 unswept.
- VP (OHLCV estimate): POC 4128.6, VAH 4142.4, VAL 4068.8.
- SMT bull: “Gold LL not confirmed by DXY LL.”
- Fib **not drawn**: latest impulse retracement = −0.20 (already extended, not a live pullback).
- Oscillator dots = pipeline fills only (3 buys / 2 sells inside the visible window).
- Sessions shaded on the single NY clock (Asia 19:00–02:00, London 02:00–09:00, NY 08:00–17:00).

---

## Status vs CFX_GAP_AUDIT.md

### 1.1 Product identity

| # | Status | Note |
|---|---|---|
| P1 Standalone CFX name | **fixed** | Pine title is `CFX Confluence X [DRAFT/UNTESTED]`; file is `cfx.pine`. Python already said CFX. |
| P2 Chart / tab / widget shells | **not done** | Overlay + PNG preview only. No dashboard tab or widget. Owner said that can wait. |
| P3 Consume XPIX | **partial** | Same XPIX rules copied (Python + Pine). No live read of the dashboard module. |

### 1.2 Sarhan-style elements

| # | Status | Note |
|---|---|---|
| S1 Order blocks + volume % | **fixed** | Drawn in Python; Pine now draws OBs. Volume % = share of visible OBs (spec), old 20-bar share kept as `bar_pct`. |
| S2 FVG | **fixed** | Python fill_i + age 30. Pine boxes extend, mitigate, and expire at `fvgMaxAge`. |
| S3 IFVG | **partial** | Python detector unchanged. Pine flips a mitigated FVG to purple IFVG when `showIfvg` is on. |
| S4 Breaker blocks | **partial** | Python detector + pipeline POI. Pine converts a mitigated OB to orange after opposite CHoCH. |
| S5 Weak high / strong low | **not done** | Not in this pass. |
| S6 BOS / CHoCH | **partial** | Python full; Pine still stub labels (now cleaned less — still no historical purge of old labels). |
| S7 EQH / EQL | **fixed** (display) | Pine default ON. Python unchanged. |
| S8 Liquidity / sweep marks | **fixed** (display) | Pine `showLiqLevels` default ON. |
| S9 Shooter VWMA-HA | **partial** | Pine filter + ATR band now referenced (`trendAtrLen` / `trendAtrMult`). Not a Python gate. |
| S10 Killzones | **fixed** | Same NY windows on both sides. Display sessions no longer pretend to be Cairo wall-clock. |
| S11 Breakout Buy/Sell labels | **not done** | Sarhan-only; screenshots still missing. |
| S12 Arabic annotations | **partial** | Still Pine-only (`langAr=true`). Python chart stays English. |
| S13 Historical Color / Tiny Points / 068 Trend | **not done** | Unresolvable without Sarhan screenshots. |

### 1.3 Schools

| # | Status | Note |
|---|---|---|
| K1–K4 SMC / ICT / CRT-CISD / SMT | **partial** | Computed and scored vs the candidate trade (or `no trade`). CRT/CISD now share a 4H start/end box definition. |
| K5 Elliott | **partial** | Simple zigzag 5-wave/ABC labeler exists, **off by default**, marked experimental. Latest window: unlabeled. |
| K6 Gann | **not done** | Honest `n/a (not computed)` / settings “not implemented”. |
| K7 Harmonic | **not done** | Same. |
| K8 Wyckoff | **not done** | Same. |
| K9 Dow | **fixed** (scoring) | Scored vs trade, not 4H EMA. |
| K10 Fibonacci | **partial** | Live-retracement draw; sweep→displacement→OTE as AND for OTE POIs; extra levels + extensions. Not a full 17-setup catalog. |
| K11 Volume Profile | **partial** | Still OHLCV estimate, labeled as such. |
| K12 Market Profile / TPO | **not done** | — |
| K13–K21 VWAP, Pivots, Ichimoku, MAs, S&D, PA, patterns, momentum, session opens | **partial** | Same detectors; scoring fixed. Pivots / Ichimoku cloud / EMAs still not drawn (scored only), same as before. |
| K22 Intermarket / seasonality | **partial** | DXY computed. Seasonality still missing. |
| K23 Per-school option cards + min 6 of 21 | **not done** | Not painted as live toggles; min-6 row removed from settings because it was never coded. |
| K24 School count | **partial** | 21 rows; MP/TPO and seasonality still absent. |

### 1.4 Reasoning mode

| # | Status | Note |
|---|---|---|
| R1 Wave narrative | **partial** | Depends on Elliott zigzag (off). No live count this window. |
| R2 Per-school why | **fixed** | Side panel lists one-liners when a candidate exists; otherwise watch notes + missing steps. |
| R3 Named targets | **fixed** | TPs are EQH/EQL, PDH/PDL, session H/L, then POC/VAL/VAH, then ICT extensions. Shown as e.g. “TP1 Asia L”. |
| R4 Schools-agreeing count | **fixed** | Scored against the candidate trade, or “no trade”. Latest chart: 0 / 0 / 17 watch. |
| R5 Invalidation | **partial** | Structural swing + 0.15 ATR, worded as a close through the SL. Not a separate wave-invalidation level. |
| R6 Weak alternative | **fixed** | Generated per trade and, when flat, from 4H/daily state. |
| R7 At most two trades; fade after close | **fixed** | Unchanged Python cap; Pine defaults now draw plans (CHoCH approximation, structural TPs only). |

### 1.5 Oscillator / divergence

| # | Status | Note |
|---|---|---|
| O1 Divergence dots tagged with name | **fixed** | One function (`detect_divergences`) for dots. Volume rule: lower second volume = non-confirmation on both sides. |
| O2 Fused pane; accurate dots | **fixed** (gating) | Dots fire only on pipeline fills, not raw hooks. Pine still has no oscillator pane. |
| O3 Multi-stoch merge | **fixed** | Still 3-of-4 leaving adaptive zones, now AND-ed into one hook. |
| O4 RSI(1) MACD 82/18 | **fixed** | Now used (in or leaving the 18/82 extreme). |
| O5 RSI(1) Stoch zones | **fixed** | Now used (≤25 buy / ≥75 sell). |
| O6 MT5 reversal-zone boxes | **not done** | Not drawn. |
| O7 Do not quadruple-count period-1 osc | **fixed** | Bundle counts as one momentum confirmation. |

### 1.6 Fibonacci

| # | Status | Note |
|---|---|---|
| F1 ICT OTE 62–79 (70.5) | **fixed** | Live retracement only. |
| F2 Sweep → displacement → OTE as AND | **fixed** | OTE-only POIs require the live impulse (displacement) plus a recent sweep. Location is no longer `OTE OR pocket OR FVG OR sweep`. |
| F3 Golden pocket | **fixed** | Still flagged; drawn when live. |
| F4 Classic 38.2 / 50 / 61.8 | **fixed** | 0.382, 0.5, 0.618 all drawn on a live retracement. |
| F5 Deep 0.786 / 0.886 | **fixed** | Drawn when live. |
| F6 Parabola Pop | **not done** | Not wired; omitted from settings. |
| F7 Fib + OB/FVG confluence | **not done** | Separate POI kinds; no intersection test. |
| F8 ICT extensions −0.27 / −0.62 / −1 | **fixed** | Used as named targets and drawn (light) when they do not cross a position box. −2 not added. |
| F9 Time / fan / channel | **not done** | — |
| F10 Fib + CHoCH/BOS | **partial** | Pipeline requires CHoCH/CISD and a POI (which may be OTE), not a dedicated combo detector. |
| F11 Unicorn | **not done** | — |
| F12 Elliott W2/W4 fib | **not done** | Needs a trusted Elliott engine. |
| F13–F15 Flush / AB=CD / cluster | **not done** | — |
| F16 Light lines, not through trades | **fixed** | No draw unless `0 < retracement < 1`; segments clipped away from position boxes. Current window: not drawn (ret = −0.20). |

Pine still has no Fibonacci (same as the draft header said). Python is the engine.

### 1.7 Order flow

| # | Status | Note |
|---|---|---|
| OF1 SMT | **fixed** (display default) | Pine `showSmt` default ON. Estimated from gold vs DXY OHLCV. |
| OF2–OF5 Absorption / exhaustion / imbalance / delta | **not done** | Omitted (no footprint feed). Not drawn as fake estimates. |
| OF6 POC / VAH / VAL | **partial** | Still an OHLCV estimate, now labeled that way. |

### 1.8 Display / sessions / MTF / XPIX

| # | Status | Note |
|---|---|---|
| D1–D3 Two trades, fade, TV-style boxes | **fixed** | Python unchanged (already). Pine plans default ON with structural TPs (no synthetic rr multiples). |
| D4 Trend line | **fixed** | Pine default ON. |
| D5 SMT line | **fixed** | Pine default ON. |
| D6 HTF CISD/CRT start and end | **fixed** | Shared 4H definition in Python (`detect_htf_zones`) and existing Pine 4H boxes, now default ON. |
| D7 MTF in the signal | **fixed** | Daily **and** 4H against → veto. 4H+1H+current alignment is computed (`htf_bull` / `htf_bear`) and used by Pine’s `useMtfFilter`. |
| D8 Session awareness | **fixed** | One clock: America/New_York display windows 19:00–02:00 / 02:00–09:00 / 08:00–17:00. Killzones stay 20:00–00:00 / 02:00–05:00 / 07:00–10:00. Cairo labels are derived, not a second clock. |
| D9 Relevant H/L | **fixed** | Pine defaults ON. |
| D10 XPIX 15M on a 15m chart | **fixed** | `f_tfAtLeast` (TF ≥) plus `lookahead_off` with `[1]`. |
| D11 Style | **partial** | Clean dark reference style kept. No Sarhan screenshots to match. |

### 1.9 Hard rules

| # | Status | Note |
|---|---|---|
| H1 Daily + 4H veto | **fixed** | `veto_buy = daily_bear & 4h_bear`; `veto_sell = daily_bull & 4h_bull`. |
| H2 POI | **fixed** | Required: unmitigated FVG / OB / breaker / live OTE. |
| H3 Sweep | **fixed** | Required (wick beyond last swing, close back, last 16 bars). |
| H4 LTF CISD or CHoCH (body) | **fixed** | Required before a limit is armed. |
| H5 Limit at FVG/OB | **fixed** | Fill at POI midpoint (CE). Gap-through uses the open. Next-bar market fill removed. |
| H6 SL = swing + 0.15 ATR | **fixed** | Prefers the swept level when it is beyond the last swing. |
| H7 TP at opposing liquidity | **fixed** | Named ladder; `rr1` is a gate, not the target itself. |
| H8 `rr1 >= 1.5` | **fixed** | Owner decision this pass: 1.5. Desk `min_rr = 2.0` was not changed (outside CFX). |
| H9 Risk 0.5% | **not done** | Pine `riskPct` still display-only. No position sizer in Python. |
| H10 Killzone + news blackout | **partial** | Killzone still required. News hook is a configurable timestamp list, 30 min before / 15 after; empty list + `NEWS_FEED = "manual (no calendar feed connected)"`. Does not block when empty. |
| H11 Spread / `cost_R > 0.20` reject | **fixed** | Applied inside `run_pipeline`. |
| H12 No edge claim until n/t bars | **fixed** (reporting) | Backtest note and this log follow the rule. No runtime UI gate. |

### Conflicts C1–C23

| # | Status | Note |
|---|---|---|
| C1 Pine still named TIA | **fixed** | |
| C2 Oscillator only in Python | **partial** | Still true — Pine has no pane. Dots are pipeline-gated in Python. |
| C3 Fib absent from Pine | **partial** | Still absent from Pine (intentionally; engine is Python). |
| C4 Four schools painted ON | **fixed** | Settings mark Gann/Harmonic/Wyckoff “not implemented”; Elliott “OFF • experimental”. |
| C5 Order flow estimated | **partial** | SMT/VP remain estimated and labeled. Fake absorption marks not re-added. |
| C6 School board vs 4H EMA | **fixed** | |
| C7 rr1 1.5 vs desk 2.0 | **fixed** (decision) | CFX uses 1.5 as instructed. Desk file untouched. |
| C8 Session clocks disagree | **fixed** | One NY table shared by Python display and Pine session inputs. |
| C9 Pine display defaults off | **fixed** | Sessions, SMT, trend, HTF zones, liquidity, plans default ON. |
| C10 `showPlanDrawings` off / stub | **partial** | Default ON. TPs are last opposite swing (no synthetic multiple). Not the full Python pipeline. |
| C11 OB volume % formula | **fixed** | Visible-OB share. |
| C12 Plotted trade with no POI | **fixed** | Pipeline cannot fire without POI + sweep + CISD/CHoCH. The old 10 Nov 10:15 hook+div buy is gone. New window trades both have a named POI. |
| C13 Two divergence definitions | **fixed** | Chart dots use `detect_divergences` only. Stoch-median div is no longer a trigger. |
| C14 HA VWMA only in Pine | **partial** | Still Pine-only, but no longer advertised as a live Python gate. |
| C15 Settings PNG over-claim | **fixed** | Regenerated from wired flags only (`cfx_settings_v2.png`). |
| C16 15M XPIX hidden on 15m | **fixed** | |
| C17 Pine XPIX `lookahead_on` | **fixed** | All those calls are `lookahead_off`. |
| C18 FVG leak / unused inputs | **fixed** | FVG boxes expire; `showOb`, `obDispAtr`, `obMaxAge`, `mitigation`, `fvgMaxAge`, `trendAtrLen`, `trendAtrMult` are referenced. |
| C19 Uncompiled Pine risks | **partial** | Still uncompiled (no Pine compiler here). New box arrays add more untested Pine. |
| C20 Unused MT5 siblings | **fixed** | Merged into one hook. |
| C21 GC=F vs XAUUSD | **fixed** (label) | Chart badge and meta say gold futures. |
| C22 Min impulse 1.5 vs 2.5 ATR | **not done** | Left at 1.5 (existing CFX setting). Not silently changed. |
| C23 Old mockup SL-on-wrong-side | **n/a** | v2 chart SLs are on the correct side of each trade. |

---

## What remains (priority leftovers)

1. No dashboard tab or widget shell (P2).
2. Pine plan hook is still a CHoCH approximation, not a full port of the Python pipeline. Pine has no oscillator pane and no fib.
3. Gann, Harmonic, Wyckoff, Market Profile/TPO, seasonality, weak/strong highs and lows, breakout labels, Parabola Pop, Unicorn, fib time/fan/channel/flush/AB=CD/cluster, absorption/exhaustion/imbalance/delta.
4. Elliott zigzag is experimental and off; it did not label this window.
5. News blackout has no calendar feed.
6. Position sizing at 0.5% not implemented.
7. Pine is uncompiled.
8. No live XPIX read from the dashboard repo.
9. Backtest n=83 is below the claim threshold; do not treat +0.238R as an edge.


---

## v3 display cleanup — 10 November 2026, 17:50 Africa/Cairo (UTC+2)

Owner voice (t37u): too many CISD / Asia / high-low lines; draw sessions as boxes; draw CISD on the candle itself (“from here to here”), and keep that compact when dropping to a lower timeframe (a 15m CISD should only span those 15m candles). Then review the rest.

Backups of the pre-v3 tree: `/workspace/cfx/backups/v2_20261110_173724/`. Local files only; no GitLab write.

### Deliverable paths (v3)

| File | Role |
|---|---|
| `/workspace/cfx/cfx_chart_real_v3.png` | GC=F 15m, same window as v2 (Fri 6 Nov 01:00 → Tue 10 Nov 15:45 Africa/Cairo) |
| `/workspace/cfx/cfx_chart_ltf_v3.png` | Real GC=F 5m zoom showing 15m (and 4H) CISD on the candle span |
| `/workspace/cfx/cfx_settings_v3.png` | Settings listing the new display inputs |
| `/workspace/cfx/cfx_chart_meta_v3.json` | Numbers behind the v3 charts |
| `/workspace/cfx/data/gc_5m.csv` | Cached yfinance GC=F 5m (aligned to the 15m last print) |
| `/workspace/cfx/cfx.pine` | Session boxes + CISD short lines + max-count inputs |
| `/workspace/cfx/cfx_lib.py` | `start_i` on CISD, session box helpers, compact `cisd_draw` |
| `/workspace/cfx/cfx_pipeline.py` | Deduped HTF CISD boxes |
| `/workspace/cfx/build_cfx_chart.py` | v3 renderer + 5m LTF view |

### Display changes

1. **Sessions are boxes, not rays.** Each Asia / London / NY run is a low-opacity rectangle spanning session time × session high/low, with a tiny name label. Full-height `axvspan` bands and the right-edge “Asia H / Lon H / NY H” lines are gone. Asia high/low live on the box edges. A short stub is drawn only if that edge is finished and still unswept and near price (and not already an XPIX print). The 15m pane keeps the latest two boxes of each session so older days do not quilt the chart.
2. **CISD is drawn on the candles.** A short capped line runs from the origin candle of the delivery run to the confirming candle, labeled `CISD 15m` or `CISD 4H`. It does not extend to the right of the confirm bar. HTF CISD is no longer a tall start/end zone box. Events whose origin→confirm span exceeds 32 15m bars are dropped (a `detect_cisd_all` walk-back had been painting a day-long bear line at 4081.5).
3. **Other levels are short stubs.** EQ 50%, VP POC/VAH/VAL, unswept PDH/PDL and EQH/EQL use an 8-bar stub and a 5.3pt label. Nearby names within 0.3 ATR are merged. A stub that sits on an XPIX print is folded into the XPIX tag (PDL 4062.5 swept merged into `4061.1 | 15M` on this window). Cap of 6 stubs besides XPIX and the trade box. XPIX still extends 30 bars right. The trend line only projects 6 bars past the last swing. VWAP stays a path, not a ray.
4. **FVG / OB / breaker** stay visible but calmer: nearest 2 FVG, 3 OB, 2 breakers, labels written inside the zone instead of on the right edge.
5. **5m LTF view** (`cfx_chart_ltf_v3.png`) uses real GC=F 5m clipped to the same last 15m print (10 Nov 15:45 Africa/Cairo). A 15m CISD covers only the 15m origin candle through the end of the confirming 15m candle (three 5m bars each, plus any bars between). The compact bull CISD 15m at 4085.5 (bars 4512→4517) is the clearest example. The 4H CISD at 4110.7 spans only those 4H candles.

### Review findings fixed in this pass

- Chart-wide CISD dashed levels and the duplicate HTF CISD zone boxes (same start/end/level drawn twice).
- Session high/low rays stacked on the right (Asia H 4156.7 next to Lon H 4156.2).
- EQ 50% dotted line drawn across the whole pane.
- PDL and XPIX 15M printing as two near-identical right-edge labels.
- OB volume tags crowding the right margin.
- Trend line shooting across empty space to the pad.
- Session display using full-height vertical shading that fought the candles.

### What the v3 15m chart shows (unchanged engine)

Same sequential trades as v2: faded BUY 4120.6 → SL, faded SELL 4148.53 → TP2. No open setup, no live fib. Last print **4063.9**. 4H bias BULL, daily BEAR. Visible CISD: bull 15m 4085.5 (5 bars), bear 15m 4118.7 (21 bars), bear 4H 4110.7. Backtest unchanged: n = 83, TP1-or-better 37.35%, average +0.238R after spread, no edge claimed, gold futures not spot.

### Pine

- Session boxes keep history (cap `maxSessBoxes`, default 9) with tiny name labels. `showSessHL` now means “unswept short stub only” and defaults **false**.
- Chart-TF CISD: `line.new` from origin bar index to confirm bar index, tiny `CISD {tf}` label. HTF CISD: same idea with `xloc.bar_time` at the CISD level, label `CISD 4H` (or whatever `htfTf` is). CRT stays a compact range box.
- New inputs: `showChartCisd`, `maxCisdLines` (4), `cisdShowAge` (24), `maxSessBoxes` (9), `levelStubBars` (8), `dedupeAtr` (0.30), `maxLevelStubs` (6). Stub length is applied to session and PDH/PDL/EQH lines. Full nearby-level merge lives in the Python renderer (Pine still filters by near + unswept).
- Still uncompiled here (no Pine compiler on the box).

### Still imperfect / leftover

- Today’s London session range is 4135–4046, so that box is tall even at 5.5% fill — that is the session high/low, not an extra ray.
- A 4H CISD is longer than a 15m CISD (it spans those 4H candles, ~11 hours on this window). It is not extended past the confirm candle.
- Unfilled FVG/OB still extend to the last bar (standard mitigation drawing), limited by count.
- `dedupeAtr` / `maxLevelStubs` are exposed in Pine but the merge/cap is fully enforced only in Python.
- No dashboard tab/widget, no full Pine port of the pipeline/oscillator/fib, no Gann/Harmonic/Wyckoff, no footprint, no news calendar feed, nothing pushed to GitLab.

## v4 — 10 Nov 2026 (~18:10 Africa/Cairo)

User feedback on v3 (paraphrased): CISD treated as missing; bottom MT5 pane changed and BUY/SELL dots wrong; show every school/indicator as a distinct marker plus a trade story; interactive dashboard that changes with trade / school / setup / session; real screenshots.

Backup before this pass: `/workspace/cfx/backups/v3_20261110_174940/`.

Nothing pushed to GitLab. `main` untouched.

### What was wrong with CISD

v3 hid almost every CISD. The renderer kept only `age > 24` (last ~6 hours) and a latest-per-side pair, then drew them as thin faint lines, so the 15m chart looked empty of CISD (“معاملني أكنه مفيش CISD”).

`detect_cisd_all` also invents day-long walk-backs that are not compact delivery-runs. Raw unique events in/near the window included bogus spans such as bull 4152.6 (246 bars), bear 4081.5 (136), bear 4105.4 (87), bear 4111.8 (52). Those were dropped by curation (`span ≤ 32` 15m bars, start ≥ sweep−16, confirm−sweep ≤ 40, window overlap, dedupe same side within 0.3 ATR overlapping spans — keep the shorter). HTF: keep max display age 24 4H bars; drop multi-day walk-backs (`i1−i0 > 16*6`) and events that end before `vis_start`. Dropped HTF bull 4001.70 (30 Oct–3 Nov) and HTF bear 4073.10 (4–5 Nov, ends before the visible window).

### CISD now drawn (window 06 Nov 01:00 → 10 Nov 15:45 Africa/Cairo)

Each event is a short capped line from the origin candle to the confirm candle only, color `#00e676` / `#ff5252`, line width ~2.2, label `CISD {tf} {level}`. No right-edge ray.

| tf | side | level | origin (Cairo) | confirm (Cairo) | span (15m bars) |
|---|---|---|---|---|---|
| 15m | bull | 4098.5 | 06 Nov 01:00 | 06 Nov 02:00 | 4 |
| 15m | bull | 4053.6 | 06 Nov 07:15 | 06 Nov 08:15 | 4 |
| 15m | bull | 4080.7 | 06 Nov 04:30 | 06 Nov 10:30 | 24 |
| 15m | bear | 4054.2 | 06 Nov 09:30 | 06 Nov 15:45 | 25 |
| 15m | bull | 4069.5 | 06 Nov 15:30 | 06 Nov 18:00 | 10 |
| 15m | bear | 4064.1 | 06 Nov 19:45 | 09 Nov 01:45 | 20 (weekend gap; 20 bars) |
| 15m | bull | 4076.0 | 09 Nov 01:30 | 09 Nov 02:00 | 2 |
| 15m | bear | 4115.3 | 09 Nov 03:30 | 09 Nov 09:00 | 22 |
| 15m | bull | 4131.7 | 09 Nov 08:00 | 09 Nov 15:15 | 29 |
| 15m | bull | 4134.1 | 09 Nov 16:00 | 09 Nov 18:00 | 8 |
| 15m | bear | 4125.9 | 09 Nov 17:15 | 09 Nov 18:15 | 4 |
| 15m | bear | 4117.2 | 09 Nov 14:00 | 09 Nov 19:00 | 20 |
| 15m | bull | 4147.9 | 10 Nov 02:00 | 10 Nov 03:15 | 5 |
| 15m | bull | 4126.1 | 10 Nov 05:30 | 10 Nov 07:15 | 7 |
| 15m | bear | 4118.7 | 10 Nov 05:45 | 10 Nov 11:00 | 21 |
| 15m | bull | 4085.5 | 10 Nov 12:45 | 10 Nov 14:00 | 5 |
| 4H  | bear | 4110.7 | 09 Nov 20:00 | 10 Nov 08:00 | 4H candles (09 Nov 13:00–10 Nov 01:00 ET) |

16 curated 15m events + 1 HTF bear. Matplotlib companion: `cfx_chart_real_v4.png` (age>24 hide removed). Dashboard overlay draws the same set.

### What was wrong with the oscillator dots

v2/v3 set `sig_buy` / `sig_sell` at the **pipeline fill bar**. Those five window fills were mid-range, so the bottom pane showed BUY/SELL in the middle of the oscillator — not an MT5 hook, and not aligned with the signal bar. That is why the pane “changed” and the dots looked wrong.

The pane itself is the merged MT5 stack: Amirulss 4-stoch `(1,9,8),(1,6,3),(1,5,7),(1,8,8)` 90/10 (median); ScalpKing RSI(1)×MACD 82/18; RSI(1) Stoch rails 90/83/75/50/25/18/7. A BUY dot is only an oversold-turn-up hook (`hook` AND rsi1-macd leaving ≤18 AND rsi1-stoch ≤25, osc<50 and rising). A SELL dot is the symmetric overbought-turn-down. Dots sit on the hook bar, not the later fill. After-the-fact MFE/MAE is logged and is **not** used as a filter (no lookahead). Dots that collide with an HTF veto or an opposite pipeline trade in signal–fill ±2 are dropped.

### Oscillator verification (same window)

Removed (pipeline fill bars, not hooks):

| time (Cairo) | side | osc | zone | price | note |
|---|---|---|---|---|---|
| 06 Nov 14:00 | BUY | 38.76 | MID | 4073.3 | fill, not MT5 hook |
| 06 Nov 18:00 | SELL | 68.57 | MID | 4072.4 | fill, not MT5 hook |
| 09 Nov 16:15 | BUY | 57.00 | MID | 4136.3 | fill, not MT5 hook |
| 09 Nov 18:45 | BUY | 43.87 | MID | 4119.2 | fill, not MT5 hook |
| 10 Nov 03:30 | SELL | 50.13 | MID | 4142.2 | fill, not MT5 hook |

Kept (merged mom_hook at the hook bar):

| time (Cairo) | side | osc | RSI(1) | stoch K | price | next 8 bars |
|---|---|---|---|---|---|---|
| 10 Nov 10:00 | BUY | 34.28 | 33.53 | 10.40 | 4127.0 | high +3.2 / low −38.8 |
| 10 Nov 11:45 | BUY | 38.29 | 28.00 | 17.07 | 4096.3 | high +0.4 / low −20.1 |

No merged SELL hook fired in this window (honest AND of the three oscillators). Neither kept BUY coincided with a pipeline fill (`pipeline_agree=False`); the pipeline entries in this window were the mid-range fills above. After both hooks, price printed a lower low — recorded only, not used to delete the dot.

### Schools + trade story

When a school/indicator points at a bar, the dashboard (and v4 matplotlib chart) places a small arrow + tiny tag (`SMC`, `ICT OTE`, `Sweep`, `FVG`, `BRK`, `SMT`, `NY`, …). Styles differ by school color. CISD confirm arrows are omitted on the dashboard because the labeled CISD span already marks that event. Opening a trade (click the chart near a fill, or an alert row, or `?trade=N`) fills a RTL story card: schools that agreed, setup/POI, session, reason, invalidation, entry / SL / TP1.

### Interactive dashboard

Standalone HTML: `/workspace/cfx/dashboard/index.html`
Embedded data: `/workspace/cfx/dashboard/data.js` (`window.CFX_DATA`, real GC=F plus pipeline output)
Vendor: `/workspace/cfx/dashboard/vendor/lightweight-charts.standalone.production.js` (4.2.1)

Features: click a trade → gold highlight + story card; school checkboxes (markers and CISD lines update); setup filter (OTE / FVG / OB / Breaker); session filter (Asia / London / NY boxes); TF switch 5m / 15m / 1H (730 / 245 / 62 candles in-window); alerts feed; state panel (last, ATR, 4H/D bias, session, XPIX 15M 4061.1, XPIX 1H 4046.4, PDH/PDL); trades as position boxes (SL red / TP green); CISD short lines; session boxes; FVG/OB/breakers; merged oscillator pane with rails 7/10/18/25/50/75/82/83/90 and the two verified BUY dots. Arabic labels + RTL story. Dark theme. Time axis is Africa/Cairo (UTC+2) via `timeScale.tickMarkFormatter` (lightweight-charts reads that option from `timeScale`, not `localization`). URL params: `tf`, `trade`, `schools`, `session`, `setups`.

### Screenshots (Playwright + system Chrome, 1920×1080)

Chrome `--screenshot` hangs on this page because lightweight-charts keeps scheduling frames; headless `--screenshot` waits for idle forever. Screenshots were taken with Playwright driving installed Chrome after an explicit ready wait (not against the box desktop).

- `/workspace/cfx/dashboard/shot_default.png` — 15m, all schools, CISD lines + session boxes + osc BUY dots
- `/workspace/cfx/dashboard/shot_trade_selected.png` — `?trade=4` SELL 10 Nov 03:30 (Cairo) OTE/Asia, gold line on the fill, story card
- `/workspace/cfx/dashboard/shot_schools_filtered.png` — `?schools=SMC,ICT` (CRT/CISD/SMT/Fib/Mom/Session unchecked; CISD lines hidden)
- `/workspace/cfx/dashboard/shot_5m.png` — `?tf=5m`, denser candles, 5m oscillator

### How to open

```
# local file
xdg-open /workspace/cfx/dashboard/index.html
# or browse file:///workspace/cfx/dashboard/index.html

# or a static server
cd /workspace/cfx/dashboard && python3 -m http.server 8765 --bind 127.0.0.1
# then http://127.0.0.1:8765/index.html
# examples: ?trade=4   ?schools=SMC,ICT   ?tf=5m   ?session=london   ?setups=OTE
```

### Companion static charts

`/workspace/cfx/cfx_chart_real_v4.png`, `cfx_chart_ltf_v4.png`, `cfx_settings_v4.png`, `cfx_chart_meta_v4.json`. Helpers: `cfx_display.py`, `export_cfx_dashboard.py`.

### Backtest (unchanged, no edge claimed)

n=83, TP1-or-better 37.35%, average +0.238R after $0.30 spread. yfinance GC=F gold futures, not spot XAUUSD. n≥30 so the numbers may be shown; n<100 and this is not an edge.

### Remaining gaps

- Pine still uncompiled here; session-box / CISD-line inputs from v3 stand, but `dedupeAtr` / `maxLevelStubs` are fully enforced only in Python.
- No GitLab push, `main` not merged.
- No Gann / Harmonic / Wyckoff markers invented (no detectors).
- Zero merged SELL hooks in this window.
- Session London box is tall (4135–4046) because that is the session high/low, not an extra ray.
- 4H CISD is longer than a 15m CISD by construction (it spans those 4H candles only).
- Dashboard is a standalone HTML file, not a product tab/widget.
- No footprint, no news calendar.

## v5 — 10 Nov 2026 (~18:20 Africa/Cairo)

User feedback on the v4 dashboard: the chart went back to the old cluttered look; he cannot see the candles. Sessions must be much lighter. Make candles the dominant element. Clean / Detailed switch, Clean default.

Backup before this pass: `/workspace/cfx/backups/v4_20261110_181200/`. Nothing pushed to GitLab.

### Display rules (Clean = default)

- **Candles** are the dominant layer (dark grid `#141414`, no stacked right-edge text).
- **Sessions**: fill ~3.5% opacity (`rgba(...,0.035)`), dotted 1px border at ~25% opacity, 9px muted label drawn inside the top-left of the box (not floating above the candles). Same treatment on the matplotlib companion chart (`alpha=0.035` fill + `:` edge `alpha=0.25`).
- **CISD**: thin (1.4px) capped lines, short `CISD {level}` labels with vertical collision skip. Clean shows only the most recent ~4 (15m + HTF ranked by confirm). The rest are available via **كل CISD** or Detailed mode. When a trade is selected, any CISD that overlaps that trade’s window is also drawn (so the setup’s own CISD is not hidden).
- **School markers**: Clean shows only markers that sit on a trade’s signal/fill bar (±20 minutes). Small arrows, **no long text**. Full tag appears on crosshair hover (tooltip) or when that trade is selected. **كل العلامات / all marks** is a separate toggle, off by default.
- **FVG / OB / breaker**: Clean draws the nearest 1 of each, ~4.5% fill, faint dotted edge, no on-chart label (name on hover). Detailed draws the nearest 2 with a tiny 9px label.
- **Trades**: Clean draws only an open position box, or the box of a selected trade (gold outline). Detailed draws every filtered trade. No faded pile of historical boxes on the default view.
- **XPIX 15M / 1H**: short stubs that stop before the price scale, small `15M 4061.1` / `1H 4046.4` labels — no stacked level column on the right.
- **Clean / Detailed** toolbar switch. URL: `?mode=detailed`, `?allMarks=1`, `?allCisd=1`, `?trade=N`, `?tf=5m`.

### Companion static chart

`/workspace/cfx/cfx_chart_real_v5.png` uses the same Clean rules: last 4 CISD, faint sessions, nearest-1 FVG/OB/breaker without interior labels, no BOS/CHoCH/VWAP/CRT/divergence text on the pane, school icons only at trade bars, no on-candle story card (it was covering price), no closed position boxes (no trade is open). XPIX stays as short right extensions.

### Screenshots

- `/workspace/cfx/dashboard/shot_v5_default.png` — Clean 15m, candles readable, 4 CISD, faint sessions
- `/workspace/cfx/dashboard/shot_v5_trade_selected.png` — `?trade=4` SELL 10 Nov 03:30 Cairo, gold line + position box + story + ICT OTE tag + CISD 4147.9
- `/workspace/cfx/dashboard/shot_v5_detailed.png` — `?mode=detailed`, all CISD, historical trade boxes, extra zones
- `/workspace/cfx/dashboard/shot_v5_5m.png` — `?tf=5m` in Clean

### Package

`/workspace/cfx/cfx_dashboard.zip` rebuilt with `shutil.make_archive` from the dashboard folder, screenshots (`shot_*.png`) excluded.

### Unchanged

Backtest n=83 / 37.35% / +0.238R after $0.30 spread. GC=F futures, not spot. No edge claimed. No GitLab push.


## v6 — 10 Nov 2026 (~18:30 Africa/Cairo)

User feedback on v3–v5: things he never asked to remove disappeared (فaded trade boxes, FVG/OB/breakers, XPIX, CRT, VP, SMT, schools panel, fib/levels/labels, trend line). He asked only to *lighten* sessions (keep them) and to draw CISD as a short span on its own candles. Bottom-pane MT5 dots were still wrong.

Backup before this pass: `/workspace/cfx/backups/v5_20261110_181930/`. v2 source kept at `/workspace/cfx/backups/v2_20261110_173724/`. v3–v5 PNG/JSON artifacts were not overwritten. Nothing pushed to GitLab.

### Restore rule

`build_cfx_chart.py` was copied back from the v2 backup, then only two drawing changes were applied on top:

1. **Sessions** — full-height `axvspan` bands replaced by light boxes from `B["sess_boxes"]` (session time × that session’s high/low), fill alpha 0.045, dotted edge alpha 0.30, small `Asia` / `London` / `NY` label. Right-edge session H/L stubs (`Asia H`, `Lon H`, `NY H`, `Asia L`, …) stay, same as v2.
2. **CISD** — long dashed rays, `CISD start`/`CISD end` HTF zone boxes, and right-edge `CISD {price}` stubs replaced by short origin→confirm lines (`draw_cisd_span`) tagged `CISD 15m` / `CISD 4H`, using the curated v4 list (`cisd_draw`, 16 events) plus the 1 HTF bear at 4110.7. CRT start/end box kept.

Everything else (faded position boxes, FVG/IFVG/OB/BRK, XPIX, VP POC/VAH/VAL, SMT, schools/reasoning panel, fib when live, EQ 50%, VWAP, PDH/PDL, EQH/EQL when present, BOS/CHoCH, divergence dots, legend, footer) is the v2 renderer again.

New module: `/workspace/cfx/cfx_osc_mt5.py`. Current `cfx_lib.py` / `cfx_pipeline.py` / `cfx_display.py` were kept (they already carry `sess_boxes`, `cisd_draw`, `detect_cisd_all`).

### v2 elements checklist (static chart v6 vs v2)

| Element | v6 |
|---|---|
| Title `CFX • GC=F gold futures 15m • 4H BULL D BEAR` | present |
| `No active setup` (no live fib) | present |
| Faded BUY position box + SL/TP/IN/R tags | present |
| Faded SELL position box + SL/TP/IN/R tags | present |
| Unfilled FVG boxes + `FVG` labels | present |
| IFVG drawing path | present (none in this window) |
| OB boxes + volume labels (`OB 1.3K (15% vis)` …) | present |
| Breakers (`BRK` / `BOS BRK`) | present |
| XPIX `4061.1 \| 15M` and `4046.4 \| 1H` | present |
| CISD short span lines tagged `CISD 15m` (16) and `CISD 4H` (1) | present (intended change b; replaced long rays / CISD start-end boxes / right-edge CISD price stubs) |
| CRT start / CRT end box | present |
| VP POC 4120.6 / VAH 4142.4 / VAL 4068.8 | present |
| SMT purple dashed line + `SMT` | present |
| Reasoning & Schools side panel | present |
| Live fib retracement | absent in both (no live impulse; same “No active setup”) |
| EQ 50% 4106.3 (discount) | present |
| VWAP 4103.3 | present |
| PDH | absent in both (not near / not swept this window) |
| PDL 4062.5 swept | present |
| EQH / EQL | absent in both (`eqh`/`eql` empty this window) |
| Session H/L stubs (Asia H 4150.7, Lon H 4135.1, NY H 4090.5, Asia L 4117.2) | present |
| Session full-height vertical bands | replaced by light session boxes (intended change a) |
| BOS / CHoCH labels | present |
| Divergence glowing dots | present in code; 0 events this window (same as v2 data) |
| Last price 4063.9 + footer disclaimer | present |
| Schools legend / footer “no edge claimed” | present |
| Bottom pane | changed: three original MT5 panes instead of one gold pipeline line (required to show the owner’s indicators and correct dots) |

### Oscillator rules (faithful MT5, no extra filters)

Screenshot used: Amirulss “FINAL STOCHASTIC OSCILLATOR” at `/home/box/agent-data/agents/e54dad2b-9120-452e-a196-e100da1af35d/attachments/6e6bea018df0d6602843e73167cbda92f2000b5e852c2b5f8cfafb64e1e58e90.png` (title `Stoch(1,9,8)(1,6,3)(1,5,7)(1,8,8)`, red 90 / blue 10). ScalpKing / RSI(1)-Stoch MT5 shots were not on disk (see `CFX_GAP_AUDIT`); parameters follow the owner’s earlier notes.

MT5 `iStochastic(Kperiod, Dperiod, slowing)`: `%K` = SMA(slowing) of raw `(close−LL)/(HH−LL)*100` over Kperiod; `%D` = SMA(Dperiod) of `%K`. RSI period 1 on close = 100 up / 0 down / 50 flat.

1. **Amirulss (4 stochastics)** — sets `(K, D, slowing) = (1,9,8), (1,6,3), (1,5,7), (1,8,8)`. Levels 90 / 10. Reversal boxes while all 4 sit in 0–10 or 90–100. **BUY** = all 4 `%K` were ≤10 last bar AND all 4 are now >10 AND median rising. **SELL** = all 4 were ≥90, now all <90, median falling. On this GC=F 15m window (245 bars) no set of 4 was ever in the zone together (`amir_n_os_max = 1`, `amir_n_ob_max = 1`; only `(1,6,3)` reached 8.0 / 94.6). **0 Amirulss dots** — the lines are drawn; we did not invent a 3-of-4 or adaptive 15/85 substitute.
2. **ScalpKing RSI(1) MACD** — 0–100 line = `EMA8(RSI(1))`, hollow signal = `EMA5` of that line, histogram = line − signal, levels 82 / 18. **BUY** = prev ≤ 18 and now > 18. **SELL** = prev ≥ 82 and now < 82. (A `50 + (EMA8−EMA17)/2` remap only spanned ~41–59 here and would have hidden every 18/82 cross.) Sanity: line 7.4–91.2; 6 BUY + 4 SELL.
3. **RSI(1) Stochastic** — range-stoch of `EMA8(RSI(1))` with `(K, D, slowing) = (8, 3, 5)`, blue `%K` / red `%D`. Levels Waiting 90 / sell 83 / sell 75 / S.B 50 / buy 25 / buy 18 / Waiting 7. **BUY** = `%K` crossed back up through waiting 7. **SELL** = crossed back down through waiting 90. Sanity: 0–100; 5 BUY + 10 SELL.

Dots fire if **any** of the three indicators signals that side (OR, not an AND-merge). Dots sit on the exact bar, never on a pipeline `fill_i`. Next-8 excursion is logged after the fact and is **not** a filter. Research only — no edge claimed.

### Verification table (Africa/Cairo UTC+2)

| Time (Cairo) | Side | Indicators that fired | Price | Next 8 bars |
|---|---|---|---|---|
| 06 Nov 11:15 | SELL | ScalpKing down through 82; RSI(1) Stoch down from 90 | 4087.00 | high +0.9 / low −14.7 |
| 06 Nov 12:45 | BUY | RSI(1) Stoch up from 7 | 4073.50 | high +9.2 / low −4.8 |
| 06 Nov 16:30 | BUY | ScalpKing up through 18 | 4045.40 | high +30.7 / low −0.3 |
| 06 Nov 18:15 | SELL | RSI(1) Stoch down from 90 | 4071.40 | high +6.2 / low −8.8 |
| 06 Nov 21:15 | SELL | RSI(1) Stoch down from 90 | 4074.20 | high +4.1 / low −4.7 |
| 09 Nov 10:00 | BUY | ScalpKing up through 18; RSI(1) Stoch up from 7 | 4099.90 | high +9.7 / low −1.9 |
| 09 Nov 11:15 | SELL | RSI(1) Stoch down from 90 | 4102.90 | high +14.8 / low −0.8 |
| 09 Nov 12:15 | SELL | RSI(1) Stoch down from 90 | 4105.40 | high +18.5 / low −1.5 |
| 09 Nov 13:45 | SELL | ScalpKing down through 82; RSI(1) Stoch down from 90 | 4117.70 | high +21.1 / low −2.4 |
| 09 Nov 20:00 | BUY | ScalpKing up through 18; RSI(1) Stoch up from 7 | 4112.80 | high +39.4 / low −3.6 |
| 09 Nov 22:30 | SELL | ScalpKing down through 82 | 4146.90 | high +9.3 / low −3.5 |
| 09 Nov 22:45 | SELL | RSI(1) Stoch down from 90 | 4150.70 | high +5.5 / low −7.3 |
| 10 Nov 07:00 | SELL | ScalpKing down through 82 | 4124.30 | high +12.1 / low +0.2 |
| 10 Nov 07:15 | SELL | RSI(1) Stoch down from 90 | 4132.10 | high +4.3 / low −7.5 |
| 10 Nov 10:00 | BUY | ScalpKing up through 18; RSI(1) Stoch up from 7 | 4127.00 | high +3.2 / low −38.8 |
| 10 Nov 11:45 | BUY | ScalpKing up through 18; RSI(1) Stoch up from 7 | 4096.30 | high +0.4 / low −20.1 |
| 10 Nov 12:30 | BUY | ScalpKing up through 18 | 4085.40 | high +1.7 / low −9.2 |
| 10 Nov 14:15 | SELL | RSI(1) Stoch down from 90 | 4083.50 | high +7.0 / low −37.1 |
| 10 Nov 15:00 | SELL | RSI(1) Stoch down from 90 | 4084.60 | high +5.9 / low −38.2 |

19 dots (7 BUY / 12 SELL). 0 Amirulss. Several next-8 moves go the other way — logged only, not used to hide a signal.

### Dashboard

Default view is **Detailed** (v2-like): last-2 faded trade boxes, all curated CISD short lines, FVG/OB/BRK, SMT, CRT start/end, VP/VWAP/EQ 50%/PDL/session H-L stubs, light session boxes, BOS/CHoCH tags, original MT5 oscillator lines (4 Amirulss + ScalpKing + RSI1 K/D) and the same 19 dots. **Clean remains an optional toggle**, not the default. `?mode=clean` still works.

### Paths

- `/workspace/cfx/cfx_chart_real_v6.png`
- `/workspace/cfx/cfx_osc_v6.png`
- `/workspace/cfx/cfx_chart_meta_v6.json`
- `/workspace/cfx/cfx_settings_v6.png`
- `/workspace/cfx/dashboard/shot_v6_default.png`
- `/workspace/cfx/cfx_dashboard.zip` (shutil, `shot_*.png` excluded)
- module: `/workspace/cfx/cfx_osc_mt5.py`

### Unchanged

Backtest n=83 / 37.35% / +0.238R after $0.30 spread. yfinance GC=F gold futures, not spot XAUUSD. n≥30 so the numbers may be shown; n<100 and this is not an edge. No GitLab push.


## v7 — 10 Nov 2026 (~18:55 Africa/Cairo)

User (Egyptian Arabic): he does not want every oscillator plotted separately — he wants **one that works**; the chart still looks “all CISD” and is missing labeled BOS/CHoCH/OB/FVG/etc.; session high/open lines should be fewer, sessions as boxes; collect every note so he does not have to keep reminding us.

Five MT5 settings dialogs were named (`e48a4bb9…jpg` SMA 144; `c980e0fa…jpg` SMA 77; `55b0e1b7…jpg` MACD 12/26/1; `9d668f90…jpg` RSI 14; `df7c3de6…jpg` Stoch 5,3,3 Low/High SMA). Those exact hashes were not on disk when read; values below follow the extracted dialogs in the brief.

Backup before this pass: `/workspace/cfx/backups/v6_20261110_184857/`. v3–v6 artifacts kept. No GitLab push.

### Oscillator — one pane, variant B

Settings implemented: Stochastic `%K=5, %D=3, slowing=3`, price field Low/High, method Simple, levels 15/85/50 (main line); RSI(14) on close, levels 10/90/50 (confirmation + faint overlay); MACD fast 12, slow 26, signal SMA 1, close (confirmation). SMA 144 red dashed and SMA 77 orange dashed on **price**.

MACD signal period 1 ⇒ SMA(1) of the MACD line equals the line, histogram ≈ 0. Confirmation uses the **MACD main slope**.

Three rules tested on GC=F 15m:

| Variant | Rule | Vis 6–10 Nov (245 bars) | Sep–Nov (4525 bars) | Against-move rate (next 8, MFE vs MAE) |
|---|---|---|---|---|
| A | K/D cross from ≤15/≥85 on this or prior bar + RSI turning + MACD slope | 0 | 3 (2 buy / 1 sell), 3 against | 100% (n=3) |
| **B (chosen)** | Same, but the zone may have been touched in the last 3 bars | 2 buy / 0 sell, both against | 62 (39 buy / 23 sell), 25 with / 37 against | **59.7%** |
| C | A + close on the SMA144 side of the signal | 0 | 0 | n/a (silent) |

Chosen: **B** — the only rule that actually fires and the lowest against-rate among variants that produce signals. It is also the natural reading of “cross **from** oversold”: %K has often already left 15 by the time it crosses %D. Research only; 59.7% against-move on the next 8 bars is **not** an edge.

Vis-window verification (Africa/Cairo):

| Time | Side | Rule | Price | Next 8 |
|---|---|---|---|---|
| 06 Nov 13:15 | BUY | Stoch K↑D after ≤15 (3-bar), RSI up, MACD main rising | 4080.10 | high +2.6 / low −15.8 |
| 10 Nov 10:00 | BUY | same | 4127.00 | high +3.2 / low −38.8 |

No SELL fired in this 6–10 Nov window under the chosen rule (23 SELLs exist on the Sep–Nov sample). Dots sit on the exact bar. Both sides are implemented.

### SMC / ICT on the main chart

BOS and CHoCH as short labeled lines at the broken swing (not text-only); CISD short spans `CISD 15m`/`CISD 4H`; OB bull/bear labels + MIT when mitigated; FVG/IFVG; breakers + MIT; `$` sweep marks (EQH/EQL, CISD sweep, PDL); EQH/EQL (engine pair plus other 0.10 ATR equal swings in view); EQ 50% premium/discount; OTE band when `in_ote` (none live this window); SMT; faded position boxes; XPIX; VP POC/VAH/VAL; VWAP.

### Sessions

Right-edge Asia H / Lon H / NY H / Asia L stubs and session-open rays **removed**. Sessions remain light time×H/L boxes with a small label.

### Notes file

`/workspace/cfx/CFX_REQUIREMENTS.md` — numbered checklist of every gathered requirement with done / partial / missing.

### Paths

- `/workspace/cfx/cfx_chart_real_v7.png`
- `/workspace/cfx/cfx_osc_v7.png`
- `/workspace/cfx/cfx_chart_meta_v7.json`
- `/workspace/cfx/cfx_settings_v7.png`
- `/workspace/cfx/dashboard/shot_v7_default.png`
- `/workspace/cfx/cfx_dashboard.zip` (screenshots excluded)
- `/workspace/cfx/cfx_osc_combo.py`
- `/workspace/cfx/CFX_REQUIREMENTS.md`

### Unchanged

Backtest n=83 / 37.35% / +0.238R after $0.30 spread. GC=F futures, not spot. No edge claimed. No GitLab push.
