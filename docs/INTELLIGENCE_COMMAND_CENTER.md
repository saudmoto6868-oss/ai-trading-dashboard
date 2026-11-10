# Trade Intelligence Center — architecture contract (summary)

The full original (88 lines, by the ChatGPT session) lives on branch `integration/tia-knowledge-center-2026-11-09` (MR !27, superseded by !49). This is a short, accurate summary for main; nothing was deleted.

- The Center is a front door and project memory, not a replacement for any specialist engine. It is PAGE 17 under the Learn & AI hub (renumbered from 13 on 2026-11-10).
- Four sections: Command Center, Knowledge, Research (published Research Hub snapshots, read-only, mock-only modules labelled), Meeting Room (append-only journal + task proposals, never writes `data/office_tasks.json`).
- Lab stays the only empirical validation authority. Accepting a knowledge record is editorial curation; it never raises `evidence_grade`.
- Technical Office, Radar and Spot are read-only sources for the Center; their behaviour and options are not changed.
- No page is removed until its content is reachable elsewhere and tested.
- Known limits: SQLite is local/dev only (Streamlit Cloud may wipe it); PostgreSQL via `DATABASE_URL` is untested; the Streamlit page has not been browser-tested.
