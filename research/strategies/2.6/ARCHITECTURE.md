# 2.6 Strategy Intelligence — Repository Architecture

Proposed isolated layout under `research/strategies/2.6/`:

```text
research/strategies/2.6/
  README.md
  IMPLEMENTATION_PLAN.md
  ARCHITECTURE.md
  CLAUDE_TASKS.md
  CLAUDE_HANDOFF.md
  CONVERSATION_LOG.md
  pyproject.toml
  configs/
    research.yaml
    instruments.yaml
    costs.yaml
  docs/
    RULEBOOK.md
    DATA_CONTRACT.md
    EVENT_DEFINITIONS.md
    EVALUATION_PROTOCOL.md
    DECISION_LOG.md
  data/
    README.md
    manifests/
    samples/                 # tiny synthetic fixtures only; never commit broker history
  src/two_six/
    __init__.py
    domain/
      ratios.py
      swings.py
      retracement.py         # H1 only
      liquidity.py
      projection.py          # H2 only
      structure.py           # optional BOS/CHoCH context
      events.py
    data/
      schema.py
      ingest.py
      validate.py
      manifests.py
      adapters/
        csv_ohlcv.py
        broker_xauusd.py
        fx_ohlcv.py
    evaluation/
      event_study.py
      controls.py
      costs.py
      splits.py
      metrics.py
      robustness.py
      reports.py
    simulation/
      paper_broker.py
      fills.py
      portfolio.py
    application/
      services.py
      schemas.py
  app/
    pages/
      01_overview.py
      02_evidence_library.py
      03_setup_explorer.py
      04_chart_replay.py
      05_backtest_lab.py
      06_robustness.py
      07_trade_journal.py
      08_data_settings.py
    components/
    assets/
  tests/
    unit/
    integration/
    fixtures/
  reports/
    README.md
  scripts/
    validate_dataset.py
    run_event_study.py
    build_report.py
```

## Dependency direction

`UI -> application -> domain/evaluation/simulation -> data contracts`.
Domain modules must not import UI, broker execution, CFX, or XPIX. Data adapters only produce canonical validated datasets. Reports must be reproducible from a saved config + dataset manifest + code revision.

## Core data objects

- `InstrumentSpec`: symbol, asset class, quote/base currency, tick size, point value, contract size, timezone, trading sessions.
- `DatasetManifest`: provider, instrument, timeframe, date range, source timezone, UTC normalization, checksum, quality report, costs.
- `RuleVersion`: hypothesis ID, ratio, anchor, direction, timeframe, causal confirmation rules, invalidation.
- `ResearchEvent`: stable event ID, hypothesis ID, observable timestamp, anchor references, measured leg, candidate level, outcome window.
- `ExperimentRun`: code revision, config, dataset manifest IDs, split boundaries, cost model, seed, metrics, artifact paths.
- `PaperTrade`: simulated-only state machine, fill assumptions, audit trail.

## Hard boundaries

- No code imports from `research/cfx/`, XPIX modules, or live execution packages.
- Do not write to CFX/XPIX configs, databases, dashboards, or strategy registries.
- Do not commit real broker history, secrets, API keys, or account identifiers.
- Keep GC=F futures labelled as a proxy; do not relabel as spot XAUUSD.
- No live trading switches, credentials, order APIs, or deployment jobs in this workstream.
