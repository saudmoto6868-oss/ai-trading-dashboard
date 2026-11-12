# CFX v7 — Confluence X (research snapshot)

Standalone research overlay for **GC=F gold futures** (yfinance), not spot XAUUSD.
This folder is a snapshot of the v7 work. It does **not** change the live TIA trading engine.
Research only — **no edge claimed**.

## Single sub-chart oscillator

Primary line: **Stochastic(5, 3, 3)** with MT5 semantics `%K` period 5, `%D` period 3, slowing 3, price field **Low/High**, method **Simple (SMA)**, levels **15 / 85 / 50**.

Confirmation (not plotted as extra panes):

- **RSI(14)** on close, levels 10 / 90 / 50
- **MACD(12, 26, 1)** on close. Signal period 1 means SMA(1) of the MACD line equals the line itself, so the histogram is ~0. Confirmation uses the **MACD main slope**.

On the **price** pane:

- **SMA 144** — red dashed
- **SMA 77** — orange dashed

### BUY / SELL rule (variant B)

Chosen after comparing three variants on GC=F 15m (visible window 6–10 Nov 2026, and the longer Sep–Nov sample).

- **BUY**: Stochastic `%K` crosses above `%D` after `%K` has touched **≤ 15** within the last 3 bars, **and** RSI(14) is turning up, **and** the MACD main line is rising.
- **SELL**: `%K` crosses below `%D` after touching **≥ 85** within the last 3 bars, **and** RSI(14) is turning down, **and** the MACD main line is falling.

Dots sit on the exact signal bar, both sides. They are **not** painted on sequential-pipeline fill bars.

Honest check (next 8 bars, MFE vs MAE, Sep–Nov, n=62): **59.7% against-move**. That is documented, not filtered, and is **not** an edge.

The CFX sequential trade engine backtest on the same futures series (separate from this oscillator) is n=83, 37.35% TP1-or-better, +0.238R after a $0.30 spread. Numbers may be shown at n≥30; an edge would require n≥100 and t>3 after costs. Neither threshold is met.

## SMC / ICT structure

The main chart draws:

- **BOS** and **CHoCH** as short labeled lines at the broken swing
- **CISD** as a short origin→confirm line on its own candles (`CISD 15m` / `CISD 4H`). In the 6–10 Nov window: 16 curated 15m events and 1 HTF 4H event
- **Order blocks** (bull / bear) with a label, plus **MIT** when mitigated
- **FVG** and **IFVG**
- **Breakers**
- Liquidity **sweeps** marked with `$`
- **EQH / EQL**
- Premium / discount (EQ 50%)
- **SMT**
- **CRT** start / end when present
- **OTE** band when a live impulse is in the OTE zone
- XPIX 15M / 1H levels, VP POC/VAH/VAL, VWAP
- At most two TradingView-style position boxes (open stays until close, then fades)

## Sessions

Sessions are **faint boxes** only (session time × that session’s high/low) with a small Asia / London / NY label. Right-edge session high/low stubs and session-open rays are not drawn.

## Requirements sheet

`CFX_REQUIREMENTS.md` lists **52** gathered user requirements, each marked done / partial / missing against this v7 snapshot.

## How to view

Open `dashboard/index.html` (needs `dashboard/data.js` and `dashboard/vendor/lightweight-charts.standalone.production.js` next to it). Static images: `cfx_chart_real_v7.png`, `cfx_osc_v7.png`, `cfx_settings_v7.png`, `dashboard/shot_v7_default.png`.

Python entry points (`build_cfx_chart.py`, `cfx_lib.py`, `cfx_pipeline.py`, …) reconstruct the snapshot from cached GC=F CSVs; those CSVs are **not** committed here.
