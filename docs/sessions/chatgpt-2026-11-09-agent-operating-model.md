# ChatGPT / TIA session note — 2026-11-09 — Agent operating model

## Owner request
Define individual responsibilities and continuous research/development; cover Asia, London, New York; prepare daily/weekly plans and post-holiday opens; show data; monitor an approved order then resume other work; allow editable names and per-agent Do/Don't instructions, memory and secrets; record everything and design for scale.

## Decisions
- Stable machine IDs with user-editable display names.
- Nine roles: intelligence director, market scout, chart reader, flow analyst, liquidity sentinel, auction guide, risk guardian, trade reviewer and research tutor.
- Each role has bounded ownership, required outputs and prohibited actions.
- Use exchange calendars and timezone-aware schedules, not fixed Cairo times.
- Daily, weekly, session handoff and post-holiday playbooks.
- Memory separated into identity, standing instructions, episodic history, research, evaluation and secret references.
- Raw secrets never enter prompts, source, profiles or logs.
- Order monitoring is a separate task and releases agents when terminal.
- Append-only audit, provenance, idempotency, backups and maintenance cadence.
- Paper trading before live; exact order approval and risk checks required.

## Work completed
- Added modules/tia_agent_charter.py (declarative roles, playbooks, guardrails and maintenance).
- Added docs/TIA_AGENT_OPERATING_MODEL.md (architecture and operating specification).
- Only TIA-owned code/docs paths changed in this increment.

## Not implemented or tested
- No database, migrations, scheduler, daily research worker, runtime or inter-agent bus.
- No persistent rename/instruction UI, memory service or secrets broker.
- No live DOM or broker adapter; no paper/live execution.
- No compile/unit tests run; no CI success claimed.

## Next
1. Persistent profiles/instructions/tasks/events/memory/handoffs/approvals schema.
2. Storage repository with append-only events and idempotency.
3. Calendar-aware scheduler and session jobs.
4. Worker runtime and typed agent messages.
5. User UI for names, Do/Don't, pause, memory and approvals.
6. Server-side permission broker, security tests, paper-trading and reconciliation.
