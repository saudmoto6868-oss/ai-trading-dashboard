# TIA Agent Operating Model
Date: 2026-11-09
Status: durable design baseline and declarative role charter; runtime not connected.
Branch: feat/radar-market-intelligence-foundation

## Goal
Build a durable digital trading team. Every agent has a stable identity, editable display name, bounded mandate, user instructions, scoped tools, durable memory and an auditable history. The team prepares and monitors Asia, London and New York, plans daily/weekly work, reviews post-holiday openings and improves continuously.

## Roles and ownership
The declarative source is modules/tia_agent_charter.py. Stable IDs never change when the user renames an agent.
- intelligence_director — routes tasks, composes the session brief, resolves handoffs and exposes disagreements.
- market_scout — breadth, sectors, relative strength, regime, correlations, macro calendar and news context.
- chart_reader — structure, trends, levels, patterns and multi-timeframe bull/bear scenarios with trigger/invalidation.
- flow_analyst — executed trades, Delta, CVD, OFI, OI/funding only where sourced; labels source, sample and coverage.
- liquidity_sentinel — DOM validity, venue-specific depth, spread, sweeps and absorption candidates.
- auction_guide — VWAP, Volume Profile, POC/VAH/VAL and acceptance/rejection using valid volume.
- risk_guardian — independent risk, event, data-quality and order-ticket review; can reject with reasons.
- trade_reviewer — counter-thesis, bias detection and post-trade review.
- research_tutor — daily research, backtest proposals, maintenance, incident analysis and Academy feedback.

Each agent must return: request, inputs, source/time/freshness, findings, evidence, limitations, unresolved items and next action. No specialist is allowed to silently promote its opinion to a confirmed setup.

## Sessions and handoffs
Use exchange calendars and a configurable timezone. Do not hard-code Cairo clock times: London/New York daylight-saving transitions and instrument trading hours change.
- Asia: review prior close, Asian open, previous day/week levels, liquidity, range formation and macro context. Handoff range, highs/lows, abnormal liquidity and unresolved scenarios to London.
- London: verify Asia handoff timestamps, review liquidity around Asia range, European events and level reactions. Handoff sweeps/acceptance/rejection, new levels, open hypotheses and US event risk to New York.
- New York: review US macro events and instrument-specific liquidity, opening volatility, spread and flow. Handoff daily summary, unresolved levels and next Asia preparation.
Every handoff records sender, receiver, session, timestamp, evidence references, unresolved questions and acknowledgement. Missing handoffs are visible.

## Daily and weekly operating cycle
Daily: data-health check and market map; independent specialist passes; skeptic and risk review; publish bull/bear scenarios with trigger/invalidation/targets; event-driven monitoring; post-session expected-vs-actual and error review.
Weekly: start-week calendar and levels; midweek regime/correlation review; end-week performance by strategy/asset/session net of costs; prioritize reproducible research.
After holidays: check exchange calendars, accumulated news, gaps, spread and thin liquidity; resync feeds and book sequence; recalculate levels from valid data; block stale/partial data; publish alternatives and wait for confirmation. No automatic entry just because a market reopens.

## Order and return-to-work flow
An order is a separate task linked to setup and approval. Lifecycle: draft -> review -> needs_approval -> approved -> submitting -> acknowledged -> working/part_filled -> filled/cancelled/rejected/expired. A monitor follows order and position state until terminal status or explicit stop. On terminal status it records a final review, closes monitoring and releases agents to their regular queues. Partial fills, disconnects, stale quotes and broker mismatches are explicit exceptions.
Live submission requires explicit user approval of exact account, instrument, side, quantity, order type, price constraints, stop and targets; server-side risk checks, fresh data, duplicate prevention, reconciliation and kill switch. Paper trading comes first. No withdrawals or transfers.

## Names, instructions, memory and secrets
User can rename, enable/pause and version each agent's instructions without changing its stable ID or rewriting history. Each profile supports custom Do/Don't instructions and scoped tool grants.
Memory layers: identity/role version; standing instructions; episodic tasks and session history; research sources and experiments; evaluation/error history; opaque secret references.
Instruction precedence: platform safety/system controls > user global policy > agent-specific policy > task instruction > agent inference. Task prompts cannot override standing prohibitions.
Secrets are never stored in source, prompts, memory, profile or event logs. Store only opaque references; a server-side secrets broker supplies short-lived scoped credentials and masks them in UI.

## Audit and storage
Use append-only events, not chat transcript as system of record. Entities: agent_profiles and role_versions; instruction_versions; memory_items with provenance/retention; tasks/dependencies; task_events; typed agent_messages; session_briefs/handoffs; market_observations; order_tickets/approvals/broker_events; research_runs/test_results/incidents/maintenance_runs.
Every event includes unique ID, entity, actor, event type, UTC timestamp, correlation ID, schema version, redacted payload and evidence references. Corrections append a superseding event; retries use idempotency keys. Define retention, export, backup and restore policies.
SQLite is suitable for a local prototype; PostgreSQL for concurrent/production use. Migrations and backups are required from the beginning.

## Continuous maintenance
Every run: source health, staleness, tool failures, audit completeness.
Daily: failed tasks, false alerts, research queue and verified backup.
Weekly: regression tests, agent quality, strategy evidence and permission audit.
Monthly: data architecture/retention, restore drill, cost/performance and credential review.
Measure coverage, source accuracy, invalid conclusions, missed/false alerts, latency, task completion, reviewer overturn rate and policy violations. Do not reward activity volume or simple agreement. n < 30 remains NOT EVIDENCE.

## Extensible architecture and delivery
1. User controls and UI: names, instructions, pause, memory inspection, task inbox, approvals.
2. Agent registry: stable IDs, role versions, capability manifests and provider/model selection.
3. Orchestrator: decomposition, routing, dependencies, deadlines, retries and handoffs.
4. Isolated runtime workers: checkpoints, cancellation and typed tool calls.
5. Permission broker: server-side allowlists, short-lived grants, approval tokens and kill switch.
6. Data plane: normalized observations with venue, timestamp and provenance.
7. Append-only event/audit plane with replay and export.
8. Storage and migrations; backup/restore.
9. Evaluation, regression, incident and maintenance automation.

Delivery order: declarative charter; persistent schema and migrations; session scheduler; worker runtime and message bus; durable memory; permission broker; live data/session dashboards; paper-trading and reconciliation; evaluation/maintenance. Live execution comes last.

## Implementation truth
modules/tia_agent_charter.py is declarative configuration only. It does not start workers, persist user changes, schedule daily research, store memory, manage secrets, connect live DOM, or execute orders. The existing Radar task desk remains session-state intake only. Do not call the team autonomous until persistence, worker execution and audit have passed end-to-end verification.
