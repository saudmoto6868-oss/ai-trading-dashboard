# TIA visual brief (owner references, 2026-11-10)

Owner sent 7 reference images. They are INSPIRATION for layout, indicators and how trades are shown. Numbers inside them are fake; TIA must never copy a number, only a form.

## Rule of the project
Every tile shows real data with a freshness label (source + age in seconds). No data => the tile says UNAVAILABLE, never a placeholder price. Perpetual/delayed/mock sources are labeled. Under n=30 evidence is marked "not evidence".

## What each reference gives us
| Ref | Idea | TIA widget (data source) |
|---|---|---|
| 1 Polymarket bot HUD | dense panel grid, top status bar (UTC, live badge), execution tape, resolution funnel, feed latency panel, 3D shell of inputs->output | **Status bar**, **Signal tape**, **Evidence funnel**, **Source health** |
| 2 monitor with map + gauges | map + gauge rings + orange/green bars | **Session/Region map** (later), gauge rings |
| 3 Grafana home dash | stat tiles, uptime strips, big sparkline, coloured threshold tiles | **Stat tiles row**, **Source uptime strip** |
| 4 black + yellow glass | one accent colour, ring gauge, chips | **Confidence ring**, accent tokens |
| 5 gauges + orange/teal bars | gauge cluster, bar histograms | **Timeframe confluence gauges**, volume/OI bars |
| 6 glass UI kit | explicit states: default/hover/focus/disabled/loading/error/selected/destructive, blur/opacity/elevation tiers | **Design tokens** for every TIA widget |
| 7 green/gold HUD | radial burst, network graph, surface chart, sliders, ring timers | **Correlation network**, **Radial** (exists), **confluence sliders**, **session ring** (exists) |

## New widgets, in build order (P1 first)
P1 (real data already in main):
1. **Trade Plan card**: entry / stop / target / R:R, size by `modules/risk_policy.py` (0.25% base). Shown only when signals + risk rules agree; else "NO PLAN" with the blocking reason. Source: `modules/signals.py`, `scorer.py`, `mtf.py`.
2. **Confidence ring + timeframe sliders**: agreement across 15m/1h/4h/1d from `tia_intelligence.analyze_symbol` (trend, RSI, 20-bar return). Ring = share of agreeing frames; conflicts shown, not hidden.
3. **Evidence funnel**: sources asked -> returned -> agree -> conflict -> stance (from `director_report` `sources`, `warnings`).
4. **Source health strip**: per source status + fetch ms + age. Measured, not assumed.
5. **Top status bar**: UTC clock, market/session, data freshness, run state of the Director.
P2:
6. **Signal tape**: last signals/closed plans from `.signal_log.jsonl` / brain log (real log only; empty = empty).
7. **Correlation network** (owner decision pending on Network/Polygonal): nodes = symbols, edges = rolling correlation.
8. **Stat tiles row** with threshold colours (thresholds written on the tile).
P3 (only if it encodes real inputs):
9. **Evidence shell** (reference 1 torus): inputs -> stance. Decorative-only versions are rejected; it must be driven by the actual agent inputs or it is not built.

## Interaction (the "visual interactivity" ask)
- Click a tile => sets the chart symbol/timeframe (bridge exists: URL params `tia_sym`).
- Hover => provenance tooltip (source, time, n).
- Click an agent/evidence chip => highlights the matching tiles.
- Every state of every control uses the glass-kit states from ref 6.

## Not tested yet / honest limits
- Nothing here is built or browser-tested. Owner's real-browser check is the acceptance test.
- Sandbox cannot reach price sites: new widgets are mock-tested only until the owner confirms them live.
- Real-time here means: OKX/Hyperliquid websockets and REST polling as already wired; Yahoo-based symbols are delayed and must say so.
