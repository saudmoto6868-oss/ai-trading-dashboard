# TIA review checklist — 2026-11-10 (Claude)

Purpose: one place to check TIA against `docs/TIA_FOUNDATION.md`, so ChatGPT, Antigravity and Claude work from the same list. "Built" means code is on main; **nothing below is browser-verified except where it says so** (the owner's screenshots confirmed: TIA layout loads, heatmap / pulse / chart / Order Flow Desk render, page 17 opens).

## 1. Page and toolbar
| Item | State |
|---|---|
| TIA is its own top-level page (index 12), Workspace unchanged | built, seen working |
| Own start layout (not a Workspace copy), storage key `tia_ws_v2` | built, seen working |
| Market / symbol / Run TIA Director inside the workspace toolbar (`#bar`), URL params `tia_mkt` / `tia_sym` / `tia_run` | built **2026-11-10, NOT yet seen**. Earlier Streamlit-widget versions never shrank, hence the rewrite |
| Director report listed below the workspace | built, not re-checked after the rewrite |
| Order-flow map uses its own price scale by default | built, **unconfirmed** that the saved state does not override it |

## 2. Widgets vs TIA_FOUNDATION
| Foundation item | Widget | State |
|---|---|---|
| Heatmaps: 24h change | `tiaheat` | built, seen |
| Live ticker snapshot | `tiapulse` | built, seen |
| Options (Deribit public) | `tiaoptions` | built, seen (IV rank shows a dash: DVOL history not returned) |
| Feed health | `tiasources` | built, seen |
| Correlation heatmap | `tiacorr` | built, mock-tested only |
| Radial geometry (centre asset, correlation + lead-lag, sample, window) | `tiaradial` | built, mock-tested only |
| Circular data system (sessions) | `tiaring` | built, mock-tested only; session hours are approximations, labelled |
| Portfolio analytics (journal R-multiples) | `tiaport` | built, maths checked on 3 mock trades |
| Funded-account limits | `tiafunded` | built, rules only (no live balance) |
| Seven specialist functions | `tiaagents` | built **2026-11-10**: descriptive cards, honest that they are responsibilities, not separate AI instances |
| Volume & Order Flow (Footprint, DOM, tape) | chart + Order Flow Desk (+ DOM / Tape from + Widget) | existing engine, reused |
| Network connections | — | **not built**: needs a defined, traceable relationship per edge (owner decision) |
| Polygonal confluence | — | **not built**: needs an agreed list of factors (owner decision) |
| Dynamic grids for liquidity / volatility / strategy performance | partly (heat, corr, ring) | liquidity and strategy-performance grids not built |

## 3. Data-integrity rules (from the foundation)
- Every metric must show source, timestamp, unit, coverage, quality: done for corr / radial / ring / options / portfolio footers; **not yet** for heat / pulse tiles.
- No mock shown as live: Pulse / heat tiles show `STALE` / `NO FEED` states.
- Hourly-candle widgets use OKX public candles, crypto USDT pairs only; non-crypto tabs show a message, not a fake chart.

## 4. Open decisions (owner)
1. Network + Polygonal: which relationships / factors.
2. Reference images: the owner says TIA does not yet look like them; Claude does not have those images in this session. Please send one or two.
3. Risk tiers (!47): needs the cap fix + parity test from its author.
4. GitLab identity verification so CI can run the tests.

## 5. Who can take what (proposal, owner decides)
- **Antigravity** (its own message is not on GitLab main; Claude could not read it): a browser-capable agent is best used for the **visual verification pass** — open TIA on 1H / 1D / 1W, confirm the toolbar controls, Agents card, every widget, page 17 — and report with screenshots. Anything else it proposes should be written to its own branch and recorded here.
- **ChatGPT**: Network / Polygonal specs once the owner decides; the (!47) risk-cap fix; the Heat / Pulse source-timestamp footers; tests for `tia_page` URL-param handling.
- **Claude**: review of every MR, widget fixes after the visual pass, hand-ports onto main.

One writer per record kind (see `docs/OVERLAP_ANALYSIS_2026-11-09.md`); each contributor logs their session in `docs/sessions/`.
