# TIA Native Knowledge and Meeting Services

## Scope and separation

This increment is implemented inside the TIA repository from `main`. It does not import, modify, merge, or depend on the separate Academy project or its branches, files, database, or UI. The Academy remains independently owned and operated. Future knowledge exchange must use explicitly approved, versioned exports or APIs; no shared writable storage is assumed.

## Components

- `modules/tia_knowledge_store.py`: SQLite-backed TIA knowledge registry and append-only meeting event journal.
- `modules/tia_page.py`: a read-only **Knowledge & Decisions** section in the existing TIA page. No new top-level route is introduced.
- `tests/test_tia_knowledge_store.py`: validation, lifecycle, hash-chain and append-only contract tests.

## Knowledge lifecycle

Knowledge records contain a title, body, category, author, status, optional HTTP(S) source URL, tags, bounded JSON metadata, timestamps, and a SHA-256 content digest.

Allowed transitions:
- draft -> review or archived
- review -> approved, rejected, draft, or archived
- approved -> review or archived
- rejected -> draft or archived
- archived -> terminal

Approval is a workflow state, not proof that the underlying claim is factually correct. Source quality and human review remain necessary.

## Meeting journal

Meeting events are append-only at the SQLite layer using update/delete rejection triggers. Each event includes a unique ID, meeting ID, event type, title, body, actor, related IDs, metadata, timestamp, previous-event hash, and event hash. The verification method checks the event chain and payload integrity.

This is tamper-evident application storage, not a cryptographic signature or a defense against a privileged database administrator who can alter the database and recompute the chain. Backups and external audit anchoring remain future controls.

## Source and failure semantics

The UI exposes store health and query failures as explicit errors. An unavailable store is not rendered as zero knowledge or a healthy empty journal. An empty result is displayed only after a successful query.

## Storage and release limitations

The initial backend is local SQLite, selected for a safe, dependency-free first increment. The default path is `data/tia_institutional.db`, overridable with `TIA_DATABASE_PATH`.

- Local SQLite readiness does not imply shared or multi-instance durability.
- Production shared-database support, authentication/authorization, backup and restore, migration rehearsal, concurrency testing, retention policy, and operational monitoring are not yet implemented or certified.
- The first UI increment is read-only; no write controls or live order execution are added.
- No Academy data is copied or queried.
- No full application, browser, mobile, or deployment test is claimed by this change.

## Next gates

1. Run unit tests and the repository test suite in a supported environment.
2. Validate persistence across process restart and concurrent writers.
3. Add migration and backup/restore tests.
4. Define authenticated roles and approval audit requirements before enabling UI writes.
5. Decide on shared PostgreSQL only after deployment configuration and operational ownership are established.
6. Define a read-only, versioned knowledge exchange contract with the independent Academy only when both workstreams explicitly agree.
