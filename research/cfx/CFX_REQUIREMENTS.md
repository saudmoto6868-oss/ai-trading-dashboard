# CFX — consolidated user requirements

Collected 10 Nov 2026 (Africa/Cairo) from the running conversation, CFX_FIX_LOG.md, and the owner’s notes as restated across v2–v7. SearchTranscripts on this bot’s store returned no extra session records, so older turns are taken from the written briefs and fix log rather than raw chat playback.

Status is against **the current v7 tree**. GC=F futures (yfinance), not spot XAUUSD. Research only — no edge claimed.

## Standing constraints

1. Work only under `/workspace/cfx`. Local files. **No GitLab push, no merge to `main`.** — **done** (honoured through v7).
2. Standalone 3-letter indicator **CFX**, separate from TIA; new files/versions rather than overwriting TIA. — **done**.
3. Do not rebuild from scratch each pass; copy forward and patch. — **done** (v7 built from v6, which restored v2).
4. Never claim an edge. Backtest n=83, hit 37.35%, +0.238R after $0.30 spread; show numbers at n≥30, claim edge only at n≥100 and t>3 after costs. — **done** (disclaimers on chart, dashboard, log).
5. rr1 minimum **1.5**. — **done** (engine `RR1_MIN`).
6. Gmail read-only; outgoing mail only via DraftExternalMessage when asked. — **done** (not touched here).

## Chart content & style

7. Follow the original reference style (dark TradingView-like, professional). — **done**.
8. Real images on real GC=F 15m (window 6–10 Nov 2026, Africa/Cairo). — **done**.
9. Mockups of the indicator plus an options/settings panel. — **done** (`cfx_settings_v7.png`).
10. Fib drawn **light** (dotted), not heavy boxes. — **done**.
11. Trades as TradingView-style **position boxes**; max **2** shown; an open trade stays until close, then fades. — **done**.
12. Trend line + SMT line. — **done**.
13. HTF CISD / CRT start–end. CISD itself is a **short line on its own candle span** (origin → confirm), tagged `CISD 15m` / `CISD 4H`, including HTF CISD drawn on the LTF. — **done**.
14. MTF alignment (4H / Daily bias in the badge and side panel). — **done**.
15. Sessions as **light boxes** (time × session high/low) with a small label — not full-height bands and not long rays. — **done**.
16. **Fewer session lines**: remove right-edge Asia H / Lon H / NY H / Asia L stubs and session-open lines. — **done** (v7).
17. Liquidity highs/lows (PDH/PDL, EQH/EQL, sweeps). — **partial** (PDH/PDL and EQH/EQL pairs in view + `$` sweep marks; not every historical pool).
18. XPIX-style 15M / 1H levels. — **done**.
19. Clean, readable, not cluttered — but **do not remove elements the user did not ask to remove**. — **partial** (v3–v5 over-deleted; v6 restored v2; v7 only drops the session stubs he asked to drop).
20. Interactive dashboard reacting to trade / school / setup / session, with per-school small distinct markers and trade-story alerts. Clean is an optional toggle, not the default. — **done** (default Detailed since v6/v7).
21. Could later be a tab / indicator / widget. — **partial** (standalone HTML dashboard + static PNG; not a TradingView widget or MT5 `.ex5`).

## SMC / ICT structure (must all be visible, not only CISD)

22. BOS — labeled **short line at the broken swing**. — **done** (v7).
23. CHoCH — same treatment, distinct from BOS. — **done** (v7).
24. CISD — short on its candle span. — **done**.
25. Order blocks, bull and bear, with a label. — **done** (v7 labels `OB bull` / `OB bear`).
26. FVG and IFVG. — **done**.
27. Breakers. — **done**.
28. Mitigation (MIT on mitigated OB/breaker). — **done** (v7).
29. Liquidity sweeps marked with `$`. — **done** (v7: EQH/EQL, CISD sweep, PDL sweep).
30. EQH / EQL. — **done** (engine pair + other near-equal swings in the window).
31. Premium / discount (EQ 50% + zone). — **done**.
32. OTE when present. — **done** (OTE band if `in_ote`; none live in this window — “No active setup”).
33. SMT. — **done**.

## Schools, reasoning, options

34. Options / status for schools: SMC, ICT, Elliott, Gann, Wyckoff, Dow, Fibonacci, Volume Profile, VWAP, Pivots, Ichimoku, MAs, SGD, Price Action/Candles, Chart Patterns, Momentum, Session Opens, Harmonic. — **partial** (side panel lists them; Gann / Harmonic / Wyckoff have no detectors — marked n/a, not invented).
35. Reasoning mode: why the trade, 2–3 real targets (including POC/VAL when used), schools agreeing, invalidation, weak alternative. — **partial** (why / targets / invalidation / weak alt on the side panel and trade stories; wave-count reasoning is experimental zigzag only and off).
36. Elliott wave counts. — **partial** (experimental zigzag, off by default).
37. Divergence as glowing named dots — not a separate RSI pane for divergence. — **done** (renderer present; 0 events in this window).

## Oscillator / bottom pane

38. Bottom pane from the user’s own MT5 scalp settings, with BUY/SELL dots only on real signals, both sides, on the exact bar. — **done** in v7 as **one** pane (he asked to pick one that works, not plot every indicator separately).
39. Settings taken from the five MT5 dialogs (10 Nov 2026): SMA 144 close red dashed; SMA 77 close orange dashed; MACD(12,26, SMA 1) close, main grey dash-dot, signal yellow; RSI(14) close, levels 10/90/50; Stochastic %K 5, %D 3, slowing 3, Low/High, Simple, levels 15/85/50. — **done** (JPEGs were not on disk at the named hashes; values follow the extracted dialogs in the brief).
40. SMA 144 and SMA 77 on the **price** chart. — **done** (v7).
41. One working rule using Stoch as the main line, confirmed by RSI(14) and MACD(12,26,1); variants tested; documented honestly. — **done** (variant **B** chosen; see CFX_FIX_LOG.md v7). Dots are not painted on pipeline fill bars.
42. Earlier Amirulss 4-stoch / ScalpKing RSI(1) / RSI(1)-Stoch triple pane. — **superseded** by (38)–(41) at the user’s request (“I don’t want them all, I want one that works”).

## Fibonacci & entries

43. All Fibonacci entry setups the engine knows (OTE, sweep, POP/golden pocket, extensions as targets). — **partial** (OTE/GP/extensions in the live-fib path and as trade targets; no separate “POP” marker beyond GP 0.618–0.65).
44. Show FVG / OB / breakers as indications / POIs. — **done**.

## Order flow / extra studies

45. SMT, absorption, exhaustion, imbalance, VP-POC. — **partial** (SMT + VP POC/VAH/VAL + VWAP are drawn; absorption / exhaustion / imbalance are **not** implemented — no tape/footprint feed).

## Process notes the user repeated

46. “Lighten sessions, don’t delete them.” — **done** (boxes stay, stubs removed in v7).
47. “CISD on its own candles, keep it visible.” — **done**.
48. “Don’t keep wiping things I never asked to remove.” — **done** for v7 relative to v2+v6, with only the session-stub removal and the single-pane osc swap.
49. “Collect all my notes so I don’t have to remind you.” — **done** (this file).
50. Pine `cfx.pine` compiled in TradingView / published. — **missing** (Pine exists as a draft; not compiled here).
51. Native MT5 / TradingView widget distribution. — **missing**.
52. News calendar, footprint, DOM. — **missing**.

## Still missing (short list)

- Gann, Harmonic, and Wyckoff detectors (honestly n/a).
- Absorption / exhaustion / imbalance / footprint.
- A live Elliott count (only an experimental zigzag).
- Compiled/published Pine and an MT5/TV widget.
- News calendar.
- Full historical liquidity-pool map beyond PDH/PDL, visible EQH/EQL, CISD/breaker sweeps, and XPIX.
