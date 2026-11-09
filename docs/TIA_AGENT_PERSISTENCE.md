# TIA Agent Persistence Layer — Phase B
Date: 2026-11-09
Status: SQLite repository and basic Streamlit profile/task controls integrated; worker runtime not connected.

## Added
`modules/tia_agent_store.py` provides:
- SQLite schema/version table for profiles, instruction versions, tasks, task events, memory, session handoffs and append-only audit events.
- Safe initial roster seeding from `tia_agent_charter.py`.
- Rename and enable/pause operations while preserving stable agent IDs.
- Versioned Do/Don't instruction records.
- Persistent task creation with idempotency key, explicit state transitions and immutable task history.
- Memory records with provenance and supersedes links; no destructive edit API.
- Session handoff creation and receiver-only acknowledgement.
- Filtered audit history and payload secret-field rejection.

## State machine in this phase
draft -> queued -> running -> needs_approval -> approved -> executing -> completed
Failure, cancellation and blocked paths are represented. This repository only records state; it does not run tasks or authorize external actions.

## Storage configuration
Default local path: `data/tia_agents.sqlite3`.
Override with environment variable `TIA_AGENT_DB`. Keep the database outside version control and configure encrypted backups/retention in deployment. SQLite WAL is enabled for local use; move to PostgreSQL before multi-instance concurrent workers.

## Security limits
This is a persistence layer, not a permission broker. It does not retrieve secrets, validate user identity, execute tools, call brokers, or submit orders. Raw secret-like fields are rejected from structured payloads. UI authentication and server-side authorization remain mandatory.

## Not yet complete
- TIA workspace now exposes persistent rename, enable/pause, versioned Do/Don't instructions, task creation, task history and cancellation controls. Radar's original session-state task desk remains a separate prototype.
- No worker, scheduler, message bus, secret manager, approval token service or broker adapter.
- No migration runner beyond schema version 1; future schema changes require numbered migrations.
- GitLab pipeline for the current branch reports failed with zero jobs; no test job ran. No local compile/unit/UI test is claimed. Do not treat persistence as production-ready.
