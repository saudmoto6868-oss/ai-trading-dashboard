"""Durable meeting-room journal for the Trade Intelligence Center.

Uses the shared Academy Intelligence database adapter. SQLite is local/dev only;
cross-instance persistence requires DATABASE_URL to point at a persistent PostgreSQL service.
Entries are append-only: corrections are new entries, never silent edits.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from modules.academy_intelligence import db_session, _execute


def initialize_meeting_store() -> None:
    with db_session() as db:
        _execute(db, """CREATE TABLE IF NOT EXISTS intelligence_meeting_entries (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            actor TEXT NOT NULL DEFAULT 'owner',
            entry_type TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'recorded',
            owner TEXT NOT NULL DEFAULT '',
            related_url TEXT NOT NULL DEFAULT '',
            metadata TEXT NOT NULL DEFAULT '{}'
        )""")
        _execute(db, "CREATE INDEX IF NOT EXISTS idx_intel_meeting_created ON intelligence_meeting_entries(created_at)")


def append_entry(*, entry_type: str, title: str, body: str, actor: str = "owner",
                 status: str = "recorded", owner: str = "", related_url: str = "",
                 metadata: dict[str, Any] | None = None) -> str:
    allowed = {"owner_request", "decision", "completed", "next_step", "blocker",
               "recommendation", "meeting_note", "agent_report", "test_result"}
    if entry_type not in allowed:
        raise ValueError("Unsupported meeting entry type")
    if not title.strip() or not body.strip():
        raise ValueError("title and body are required")
    if related_url and not related_url.startswith(("https://", "http://")):
        raise ValueError("related_url must be HTTP(S)")
    initialize_meeting_store()
    entry_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    with db_session() as db:
        _execute(db, """INSERT INTO intelligence_meeting_entries
            (id, created_at, actor, entry_type, title, body, status, owner, related_url, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (entry_id, created_at, actor[:120], entry_type, title[:240], body,
             status[:40], owner[:120], related_url, json.dumps(metadata or {}, ensure_ascii=False)))
    return entry_id


def list_entries(*, limit: int = 100, entry_type: str = "") -> list[dict]:
    initialize_meeting_store()
    sql = "SELECT * FROM intelligence_meeting_entries"
    args: list[Any] = []
    if entry_type:
        sql += " WHERE entry_type = ?"
        args.append(entry_type)
    sql += " ORDER BY created_at DESC LIMIT ?"
    args.append(max(1, min(int(limit), 500)))
    with db_session() as db:
        rows = _execute(db, sql, args).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        try:
            item["metadata"] = json.loads(item.get("metadata") or "{}")
        except (TypeError, ValueError):
            item["metadata"] = {}
        out.append(item)
    return out


def list_task_proposals() -> tuple[list[dict], dict[str, dict]]:
    """Return every task proposal and its latest review, independent of journal pagination.

    The original proposal and each review remain immutable append-only entries.
    """
    initialize_meeting_store()
    with db_session() as db:
        rows = _execute(
            db,
            "SELECT * FROM intelligence_meeting_entries "
            "WHERE entry_type IN (?, ?) ORDER BY created_at DESC",
            ("recommendation", "decision"),
        ).fetchall()
    proposals: list[dict] = []
    reviews: dict[str, dict] = {}
    for row in rows:
        item = dict(row)
        try:
            item["metadata"] = json.loads(item.get("metadata") or "{}")
        except (TypeError, ValueError):
            item["metadata"] = {}
        meta = item["metadata"]
        if meta.get("kind") == "task_proposal":
            proposals.append(item)
        elif meta.get("kind") == "task_proposal_review" and meta.get("proposal_id"):
            # Rows are newest-first, so the first review for an ID is authoritative.
            reviews.setdefault(meta["proposal_id"], item)
    return proposals, reviews


def meeting_summary(limit: int = 200) -> dict:
    rows = list_entries(limit=limit)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["entry_type"]] = counts.get(row["entry_type"], 0) + 1
    return {"entries": len(rows), "by_type": counts, "latest": rows[0] if rows else None}
