"""Shared Academy Intelligence data layer.

This module is deliberately storage-adapter based: the default SQLite database is
suitable for local development and tests. Streamlit Cloud's filesystem may be
ephemeral; production persistence must be configured through ACADEMY_DB_PATH on
a persistent volume or replaced by a shared database adapter before multi-instance
deployment. No model opinion is treated as backtest evidence.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

STATUSES = {"inbox", "review", "accepted", "rejected", "archived"}
EVIDENCE_GRADES = {"unreviewed", "source_only", "corroborated", "backtest_candidate", "validated"}
CLAIM_TYPES = {"fact", "interpretation", "hypothesis", "disputed", "empirically_validated"}
_REQUIRED = ("title", "summary", "topic", "claim_type")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def database_path() -> Path:
    return Path(os.getenv("ACADEMY_DB_PATH", "data/academy_hub.sqlite3"))


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    target = Path(path) if path else database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(target), timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA journal_mode=WAL")
    return db


def initialize(path: str | Path | None = None) -> None:
    with connect(path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS knowledge_records (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            topic TEXT NOT NULL,
            school TEXT NOT NULL DEFAULT '',
            claim_type TEXT NOT NULL,
            status TEXT NOT NULL,
            evidence_grade TEXT NOT NULL,
            asset TEXT NOT NULL DEFAULT '',
            timeframe TEXT NOT NULL DEFAULT '',
            language TEXT NOT NULL DEFAULT '',
            source_url TEXT NOT NULL DEFAULT '',
            source_title TEXT NOT NULL DEFAULT '',
            source_author TEXT NOT NULL DEFAULT '',
            source_published_at TEXT NOT NULL DEFAULT '',
            captured_at TEXT NOT NULL,
            provenance TEXT NOT NULL DEFAULT '[]',
            details TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_knowledge_topic ON knowledge_records(topic);
        CREATE INDEX IF NOT EXISTS idx_knowledge_school ON knowledge_records(school);
        CREATE INDEX IF NOT EXISTS idx_knowledge_status ON knowledge_records(status);
        CREATE INDEX IF NOT EXISTS idx_knowledge_asset_tf ON knowledge_records(asset, timeframe);
        """)


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in _REQUIRED if not str(record.get(key, "")).strip()]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))
    out = dict(record)
    out.setdefault("id", str(uuid.uuid4()))
    out.setdefault("status", "inbox")
    out.setdefault("evidence_grade", "unreviewed")
    out.setdefault("captured_at", _now())
    out.setdefault("provenance", [])
    out.setdefault("details", {})
    if out["status"] not in STATUSES:
        raise ValueError("Invalid status")
    if out["evidence_grade"] not in EVIDENCE_GRADES:
        raise ValueError("Invalid evidence_grade")
    if out["claim_type"] not in CLAIM_TYPES:
        raise ValueError("Invalid claim_type")
    if not isinstance(out["provenance"], list) or not isinstance(out["details"], dict):
        raise ValueError("provenance must be a list and details must be an object")
    return out


def upsert_record(record: dict[str, Any], path: str | Path | None = None) -> str:
    item = validate_record(record)
    now = _now()
    columns = (
        "id", "title", "summary", "topic", "school", "claim_type", "status",
        "evidence_grade", "asset", "timeframe", "language", "source_url",
        "source_title", "source_author", "source_published_at", "captured_at",
        "provenance", "details"
    )
    values = []
    for key in columns:
        value = item.get(key, "")
        if key in {"provenance", "details"}:
            value = json.dumps(value, ensure_ascii=False, sort_keys=True)
        values.append(value)
    with connect(path) as db:
        db.execute(
            f"""INSERT INTO knowledge_records ({','.join(columns)}, created_at, updated_at)
            VALUES ({','.join('?' for _ in range(len(columns) + 2))})
            ON CONFLICT(id) DO UPDATE SET
            {','.join(f'{key}=excluded.{key}' for key in columns if key != 'id')},
            updated_at=excluded.updated_at""",
            values + [now, now],
        )
    return item["id"]


def search_records(query: str = "", *, topic: str = "", school: str = "",
                   status: str = "", asset: str = "", timeframe: str = "",
                   limit: int = 50, path: str | Path | None = None) -> list[dict[str, Any]]:
    clauses, args = [], []
    for field, value in (("topic", topic), ("school", school), ("status", status),
                         ("asset", asset), ("timeframe", timeframe)):
        if value:
            clauses.append(f"{field} = ?")
            args.append(value)
    if query.strip():
        clauses.append("(title LIKE ? OR summary LIKE ? OR details LIKE ?)")
        needle = f"%{query.strip()}%"
        args.extend([needle, needle, needle])
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    with connect(path) as db:
        rows = db.execute(
            f"SELECT * FROM knowledge_records{where} ORDER BY updated_at DESC LIMIT ?",
            args + [max(1, min(int(limit), 200))],
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["provenance"] = json.loads(item["provenance"])
        item["details"] = json.loads(item["details"])
        result.append(item)
    return result


def import_legacy_lessons(path: str | Path | None = None,
                          source_file: str | Path = "data/academy.json") -> int:
    """Idempotently index existing lesson cards; original JSON remains untouched."""
    source = Path(source_file)
    if not source.exists():
        return 0
    payload = json.loads(source.read_text(encoding="utf-8"))
    imported = 0
    for lesson in payload.get("lessons", []):
        verdict = lesson.get("verdict", "hypothesis")
        claim = verdict if verdict in CLAIM_TYPES else "interpretation"
        refs = lesson.get("sources", [])
        record = {
            "id": "legacy-" + str(lesson.get("id", uuid.uuid4())),
            "title": lesson.get("title", "Untitled legacy lesson"),
            "summary": lesson.get("summary", ""),
            "topic": lesson.get("topic", "General"),
            "school": lesson.get("school", ""),
            "claim_type": claim,
            "status": "review" if lesson.get("status") == "draft" else "accepted",
            "evidence_grade": "source_only" if refs else "unreviewed",
            "language": "ar",
            "provenance": [{"kind": "legacy_academy_json", "source": str(source),
                            "references": refs, "source_label": lesson.get("source", "")}],
            "details": {"points": lesson.get("points", []),
                        "caveats": lesson.get("caveats", []),
                        "verdict_note": lesson.get("verdict_note", ""),
                        "uses": lesson.get("uses", [])},
        }
        upsert_record(record, path)
        imported += 1
    return imported


def promotion_gate(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Only empirically validated, sufficiently documented records may be promoted."""
    reasons = []
    if record.get("claim_type") != "empirically_validated":
        reasons.append("claim_type is not empirically_validated")
    if record.get("evidence_grade") != "validated":
        reasons.append("evidence_grade is not validated")
    details = record.get("details") or {}
    required = ("sample_size", "out_of_sample", "costs_included", "lookahead_checked")
    for key in required:
        if not details.get(key):
            reasons.append(f"missing validation evidence: {key}")
    if details.get("sample_size", 0) < 100:
        reasons.append("sample_size is below 100")
    return not reasons, reasons
