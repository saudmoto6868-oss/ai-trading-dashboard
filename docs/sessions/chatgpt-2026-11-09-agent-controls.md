# TIA session note — 2026-11-09 — Persistent controls integration

## Work completed
- Added SQLite persistence for agent profiles, instruction versions, tasks, append-only task/audit events, memory and session handoffs.
- Wired persistent profile controls into TIA workspace: rename, enable/pause, Do/Don't instructions, task creation, task history and cancellation.
- Stable agent IDs preserve historical ownership after renaming.
- Added raw credential rejection for instruction, task and memory text; secret references only.
- Fixed in-memory SQLite mode to use a shared connection URI for repeatable tests.

## Validation
- GitLab branch pipeline reports failed with zero jobs; no CI test actually ran.
- No local compile, automated test, browser or mobile smoke test has been run.
- Task records persist, but no worker or scheduler executes them. Start/execution UI is intentionally not exposed.

## Next
- Add repository unit tests and run them in a configured CI job.
- Add timezone-aware session calendar and durable scheduler.
- Add worker runtime, typed agent messages and server-side permission broker.
