"""Shared Academy Intelligence data layer.

SQLite is the local-development adapter. Streamlit Cloud's filesystem may be
ephemeral; production persistence must use a shared persistent database before
multi-instance sharing is claimed.
"""
from __future__ import annotations
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from typing import Any

STATUSES = {"inbox", "review", "accepted", "rejected", "archived"}
EVIDENCE_GRADES = {"unreviewed", "source_only", "corroborated", "backtest_candidate", "validated"}
CLAIM_TYPES = {"fact", "interpretation", "hypothesis", "disputed", "empirically_validated"}
_REQUIRED = ("title", "summary", "topic", "claim_type")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def database_path() -> Path:
    return Path(os.getenv("ACADEMY_DB_PATH", "data/academy_hub.sqlite3"))


def connect(path: str | Path | None = None):
    # DATABASE_URL selects shared persistent PostgreSQL. Explicit paths stay SQLite for tests.
    url = os.getenv("DATABASE_URL", "").strip() if path is None else ""
    if url:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc
        return psycopg.connect(url, row_factory=dict_row, connect_timeout=10)
    target = Path(path) if path else database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(target), timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA journal_mode=WAL")
    return db


def _execute(db, sql: str, args=()):
    if isinstance(db, sqlite3.Connection):
        return db.execute(sql, args)
    return db.execute(sql.replace("?", "%s"), args)


@contextmanager
def db_session(path: str | Path | None = None):
    db = connect(path)
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path: str | Path | None = None) -> None:
    statements = [
        """CREATE TABLE IF NOT EXISTS knowledge_records (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL,
            topic TEXT NOT NULL, school TEXT NOT NULL DEFAULT '',
            claim_type TEXT NOT NULL, status TEXT NOT NULL, evidence_grade TEXT NOT NULL,
            asset TEXT NOT NULL DEFAULT '', timeframe TEXT NOT NULL DEFAULT '',
            language TEXT NOT NULL DEFAULT '', source_url TEXT NOT NULL DEFAULT '',
            source_title TEXT NOT NULL DEFAULT '', source_author TEXT NOT NULL DEFAULT '',
            source_published_at TEXT NOT NULL DEFAULT '', captured_at TEXT NOT NULL,
            provenance TEXT NOT NULL DEFAULT '[]', details TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )""",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_topic ON knowledge_records(topic)",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_school ON knowledge_records(school)",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_status ON knowledge_records(status)",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_asset_tf ON knowledge_records(asset, timeframe)",
        """CREATE TABLE IF NOT EXISTS knowledge_review_events (
            id TEXT PRIMARY KEY, record_id TEXT NOT NULL, created_at TEXT NOT NULL,
            actor TEXT NOT NULL, decision TEXT NOT NULL, reason TEXT NOT NULL,
            source_class TEXT NOT NULL,
            FOREIGN KEY(record_id) REFERENCES knowledge_records(id)
        )""",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_review_record ON knowledge_review_events(record_id, created_at)",
    ]
    with db_session(path) as db:
        for statement in statements:
            _execute(db, statement)


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
    source_url = str(out.get("source_url", "") or "").strip()
    if source_url and not source_url.startswith(("https://", "http://")):
        raise ValueError("source_url must be HTTP(S)")
    out["source_url"] = source_url
    return out


def upsert_record(record: dict[str, Any], path: str | Path | None = None) -> str:
    item = validate_record(record)
    now = _now()
    columns = ("id", "title", "summary", "topic", "school", "claim_type", "status",
               "evidence_grade", "asset", "timeframe", "language", "source_url",
               "source_title", "source_author", "source_published_at", "captured_at",
               "provenance", "details")
    values = []
    for key in columns:
        value = item.get(key, "")
        if key in {"provenance", "details"}:
            value = json.dumps(value, ensure_ascii=False, sort_keys=True)
        values.append(value)
    with connect(path) as db:
        _execute(db,
            f"INSERT INTO knowledge_records ({','.join(columns)}, created_at, updated_at) "
            f"VALUES ({','.join('?' for _ in range(len(columns)+2))}) "
            f"ON CONFLICT(id) DO UPDATE SET "
            f"{','.join(f'{key}=excluded.{key}' for key in columns if key != 'id')}, "
            "updated_at=excluded.updated_at",
            values + [now, now],
        )
    return item["id"]


SOURCE_CLASSES = {"primary", "secondary", "marketing", "community", "internal", "unknown"}
REVIEW_DECISIONS = {"accept": "accepted", "reject": "rejected", "return_to_review": "review", "archive": "archived"}


def review_record(record_id: str, decision: str, reason: str, *,
                  source_class: str = "unknown", actor: str = "owner",
                  path: str | Path | None = None) -> str:
    """Append an immutable curation decision; never upgrades empirical evidence."""
    record_id, reason, actor = str(record_id).strip(), str(reason).strip(), str(actor).strip()
    if decision not in REVIEW_DECISIONS:
        raise ValueError("Invalid review decision")
    if source_class not in SOURCE_CLASSES:
        raise ValueError("Invalid source classification")
    if not record_id or not reason or not actor:
        raise ValueError("record_id, actor and review reason are required")
    if len(reason) > 2000 or len(actor) > 120:
        raise ValueError("Review reason or actor exceeds the allowed length")
    event_id, now = str(uuid.uuid4()), _now()
    with db_session(path) as db:
        row = _execute(db, "SELECT details FROM knowledge_records WHERE id = ?", (record_id,)).fetchone()
        if not row:
            raise ValueError("Knowledge record not found")
        details = json.loads(row["details"] if isinstance(row, dict) else row[0])
        details["source_class"] = source_class
        _execute(db, "UPDATE knowledge_records SET status = ?, details = ?, updated_at = ? WHERE id = ?",
                 (REVIEW_DECISIONS[decision], json.dumps(details, ensure_ascii=False, sort_keys=True), now, record_id))
        _execute(db, "INSERT INTO knowledge_review_events (id, record_id, created_at, actor, decision, reason, source_class) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (event_id, record_id, now, actor, decision, reason, source_class))
    return event_id


def list_review_events(record_id: str, *, path: str | Path | None = None) -> list[dict[str, Any]]:
    with connect(path) as db:
        rows = _execute(db, "SELECT id, record_id, created_at, actor, decision, reason, source_class FROM knowledge_review_events WHERE record_id = ? ORDER BY created_at ASC, id ASC",
                        (str(record_id),)).fetchall()
    return [dict(row) for row in rows]


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
        rows = _execute(db, f"SELECT * FROM knowledge_records{where} ORDER BY updated_at DESC LIMIT ?",
                        args + [max(1, min(int(limit), 200))]).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["provenance"] = json.loads(item["provenance"])
        item["details"] = json.loads(item["details"])
        result.append(item)
    return result


def import_legacy_lessons(path: str | Path | None = None,
                          source_file: str | Path = "data/academy.json") -> int:
    """Idempotently index legacy lessons without upgrading their review/evidence state.

    Legacy status and verdict vocabularies are deliberately mapped conservatively.
    The source JSON is never modified.
    """
    source = Path(source_file)
    if not source.exists():
        return 0
    payload = json.loads(source.read_text(encoding="utf-8"))
    imported = 0
    status_map = {"draft": "inbox", "reviewed": "review", "approved": "accepted"}
    claim_map = {
        "consistent": "interpretation",
        "hypothesis": "hypothesis",
        "unverified": "interpretation",
        "contradicted": "disputed",
    }
    for lesson in payload.get("lessons", []):
        if not isinstance(lesson, dict) or not lesson.get("id"):
            continue
        refs = [str(url).strip() for url in lesson.get("sources", [])
                if isinstance(url, str) and url.strip().startswith(("https://", "http://"))]
        record = {
            "id": "legacy-" + str(lesson["id"]),
            "title": lesson.get("title") or "Untitled legacy lesson",
            "summary": lesson.get("summary") or "Legacy lesson imported for review.",
            "topic": lesson.get("topic") or "General",
            "school": lesson.get("school", ""),
            "claim_type": claim_map.get(lesson.get("verdict"), "interpretation"),
            "status": status_map.get(lesson.get("status"), "inbox"),
            "evidence_grade": "source_only" if refs else "unreviewed",
            "source_url": refs[0] if refs else "",
            "source_title": lesson.get("source", ""),
            "language": "ar",
            "provenance": [{"kind": "legacy_academy_json", "source": str(source),
                            "references": refs, "source_label": lesson.get("source", "")}],
            "details": {"legacy_status": lesson.get("status", ""),
                        "legacy_verdict": lesson.get("verdict", ""),
                        "verdict_note": lesson.get("verdict_note", ""),
                        "points": lesson.get("points", []), "caveats": lesson.get("caveats", []),
                        "uses": lesson.get("uses", [])},
        }
        # Imported rows are insert-once: a later owner review must not be
        # overwritten by re-reading the legacy JSON on every workspace render.
        with connect(path) as db:
            exists = _execute(db, "SELECT id FROM knowledge_records WHERE id = ?", (record["id"],)).fetchone()
        if not exists:
            upsert_record(record, path)
        imported += 1
    return imported


def import_legacy_references(path: str | Path | None = None,
                             source_file: str | Path = "data/academy_refs.json") -> int:
    """Index legacy reference catalog sources and claims as unreviewed research inputs.

    Vendor/source reputation and a legacy 'confirmed' verdict are not Lab validation.
    Existing records are never overwritten by a later import.
    """
    source = Path(source_file)
    if not source.exists():
        return 0
    payload = json.loads(source.read_text(encoding="utf-8"))
    items = []
    for item in payload.get("sources", []):
        if not isinstance(item, dict) or not item.get("id") or not item.get("title"):
            continue
        items.append({
            "id": "legacy-ref-source-" + str(item["id"]),
            "title": item["title"],
            "summary": " | ".join(str(x) for x in item.get("takeaways", [])[:5]) or
                       "Legacy reference catalog entry; review the original material before use.",
            "topic": "Reference library",
            "claim_type": "interpretation",
            "status": "inbox",
            "evidence_grade": "source_only" if item.get("path") else "unreviewed",
            "source_title": item.get("origin", ""),
            "language": "ar",
            "provenance": [{"kind": "legacy_reference_catalog", "source": str(source),
                            "path": item.get("path", ""), "origin": item.get("origin", ""),
                            "kind_label": item.get("kind", ""), "open_questions": item.get("open", [])}],
            "details": {"record_type": "reference_source", "takeaways": item.get("takeaways", []),
                        "open_questions": item.get("open", [])},
        })
    for item in payload.get("claims", []):
        if not isinstance(item, dict) or not item.get("id") or not item.get("claim"):
            continue
        urls = [str(url).strip() for url in item.get("urls", [])
                if isinstance(url, str) and url.strip().startswith(("https://", "http://"))]
        verdict = item.get("verdict", "unverified")
        items.append({
            "id": "legacy-ref-claim-" + str(item["id"]),
            "title": str(item["claim"])[:240],
            "summary": item.get("evidence") or item.get("note") or "Legacy claim pending source review.",
            "topic": "Research claims",
            "claim_type": "disputed" if verdict == "contradicted" else "hypothesis",
            "status": "inbox",
            "evidence_grade": "source_only" if urls else "unreviewed",
            "source_url": urls[0] if urls else "",
            "source_title": item.get("origin", ""),
            "language": "ar",
            "provenance": [{"kind": "legacy_reference_claim", "source": str(source),
                            "urls": urls, "legacy_verdict": verdict, "where": item.get("where", "")}],
            "details": {"record_type": "reference_claim", "legacy_verdict": verdict,
                        "note": item.get("note", ""), "where": item.get("where", "")},
        })
    for record in items:
        with connect(path) as db:
            exists = _execute(db, "SELECT id FROM knowledge_records WHERE id = ?", (record["id"],)).fetchone()
        if not exists:
            upsert_record(record, path)
    return len(items)


def promotion_gate(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Minimum metadata guard; not a profitability guarantee."""
    reasons = []
    if record.get("claim_type") != "empirically_validated":
        reasons.append("claim_type is not empirically_validated")
    if record.get("evidence_grade") != "validated":
        reasons.append("evidence_grade is not validated")
    details = record.get("details") or {}
    for key in ("sample_size", "out_of_sample", "costs_included", "lookahead_checked"):
        if not details.get(key):
            reasons.append(f"missing validation evidence: {key}")
    if details.get("sample_size", 0) < 100:
        reasons.append("sample_size is below 100")
    return not reasons, reasons


def workspace_snapshot(limit: int = 80) -> list[dict]:
    """Safe read-only payload for the Workspace widget; gracefully degrades."""
    try:
        initialize()
        # Re-run the deterministic ID-based import so lessons added to the legacy
        # source later are indexed too; upsert keeps the import idempotent.
        import_legacy_lessons()
        import_legacy_references()
        rows = search_records(limit=limit)
        out = []
        for row in rows:
            details, provenance = row.get("details") or {}, row.get("provenance") or []
            refs = []
            for item in provenance:
                if isinstance(item, dict):
                    refs.extend(item.get("references", []))
                    if item.get("url"):
                        refs.append(item["url"])
            out.append({
                "id": row["id"], "title": row["title"], "summary": row["summary"],
                "topic": row["topic"], "school": row["school"], "claim_type": row["claim_type"],
                "status": row["status"], "evidence_grade": row["evidence_grade"],
                "asset": row["asset"], "timeframe": row["timeframe"],
                "source_url": row["source_url"], "source_title": row["source_title"],
                "references": list(dict.fromkeys(str(u) for u in refs
                    if isinstance(u, str) and u.startswith(("https://", "http://"))))[:8],
                "points": details.get("points", [])[:8], "caveats": details.get("caveats", [])[:5],
            })
        return out
    except Exception:
        return []
