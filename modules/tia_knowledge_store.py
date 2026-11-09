"""Native TIA knowledge registry and append-only meeting journal.

This service is intentionally independent of the Academy project. It provides
bounded, validated local persistence; production shared-database deployment
must be configured and verified separately before this store is treated as
institution-wide durable storage.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
MAX_TITLE = 240
MAX_BODY = 40_000
MAX_TAGS = 32
MAX_TAG = 64
MAX_SOURCE_URL = 2_048
MAX_METADATA_BYTES = 16_384

KNOWLEDGE_STATUSES = {"draft", "review", "approved", "rejected", "archived"}
MEETING_KINDS = {"decision", "observation", "question", "handoff", "review", "action"}
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


class TIAStoreError(Exception):
    """Base exception for explicit TIA store failures."""


class ValidationError(TIAStoreError, ValueError):
    """Raised when caller-supplied data violates the store contract."""


@dataclass(frozen=True)
class StoreHealth:
    status: str
    backend: str
    path: str
    schema_version: int | None
    detail: str


def _text(value: Any, field: str, limit: int, *, required: bool = True) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be text")
    value = value.strip()
    if required and not value:
        raise ValidationError(f"{field} is required")
    if len(value) > limit:
        raise ValidationError(f"{field} exceeds {limit} characters")
    return value


def _tags(values: Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, (str, bytes)):
        raise ValidationError("tags must be a list of strings")
    result: list[str] = []
    for item in values:
        tag = _text(item, "tag", MAX_TAG).lower()
        if tag not in result:
            result.append(tag)
        if len(result) > MAX_TAGS:
            raise ValidationError(f"at most {MAX_TAGS} tags are allowed")
    return result


def _metadata(value: dict[str, Any] | None) -> str:
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise ValidationError("metadata must be an object")
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise ValidationError("metadata must contain JSON-safe values") from exc
    if len(encoded.encode("utf-8")) > MAX_METADATA_BYTES:
        raise ValidationError("metadata is too large")
    return encoded


def _source_url(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    url = _text(value, "source_url", MAX_SOURCE_URL)
    if not URL_RE.match(url):
        raise ValidationError("source_url must use http or https")
    return url


class TIAKnowledgeStore:
    """SQLite-backed knowledge registry and immutable meeting event log."""

    def __init__(self, db_path: str | os.PathLike[str] | None = None):
        configured = db_path or os.getenv("TIA_DATABASE_PATH", "data/tia_institutional.db")
        self.db_path = str(configured)
        if self.db_path != ":memory:":
            Path(self.db_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=10000")
        if self.db_path != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tia_schema_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tia_knowledge (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN
                        ('draft','review','approved','rejected','archived')),
                    source_url TEXT,
                    tags_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    created_by TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tia_knowledge_status
                    ON tia_knowledge(status, updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_tia_knowledge_category
                    ON tia_knowledge(category, updated_at DESC);
                CREATE TABLE IF NOT EXISTS tia_meeting_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    meeting_id TEXT NOT NULL,
                    kind TEXT NOT NULL CHECK(kind IN
                        ('decision','observation','question','handoff','review','action')),
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    related_ids_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    previous_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE
                );
                CREATE INDEX IF NOT EXISTS idx_tia_meeting_events_meeting
                    ON tia_meeting_events(meeting_id, sequence);
                CREATE TRIGGER IF NOT EXISTS tia_meeting_events_no_update
                    BEFORE UPDATE ON tia_meeting_events
                    BEGIN SELECT RAISE(ABORT, 'meeting events are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS tia_meeting_events_no_delete
                    BEFORE DELETE ON tia_meeting_events
                    BEGIN SELECT RAISE(ABORT, 'meeting events are append-only'); END;
            """)
            conn.execute(
                "INSERT OR IGNORE INTO tia_schema_meta(key,value) VALUES('schema_version',?)",
                (str(SCHEMA_VERSION),),
            )

    def health(self) -> StoreHealth:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT value FROM tia_schema_meta WHERE key='schema_version'"
                ).fetchone()
                if row is None:
                    return StoreHealth("degraded", "sqlite", self.db_path, None,
                                       "schema version metadata is missing")
                version = int(row["value"])
                if version != SCHEMA_VERSION:
                    return StoreHealth("degraded", "sqlite", self.db_path, version,
                                       "schema version requires migration")
                conn.execute("SELECT 1 FROM tia_knowledge LIMIT 1").fetchone()
                conn.execute("SELECT 1 FROM tia_meeting_events LIMIT 1").fetchone()
                return StoreHealth("ready", "sqlite", self.db_path, version,
                                   "local store is readable; shared durability is not implied")
        except (sqlite3.Error, OSError, ValueError) as exc:
            return StoreHealth("unavailable", "sqlite", self.db_path, None, str(exc))

    def add_knowledge(
        self, *, title: str, body: str, category: str, created_by: str,
        status: str = "draft", source_url: str | None = None,
        tags: Iterable[str] | None = None, metadata: dict[str, Any] | None = None,
        item_id: str | None = None,
    ) -> str:
        title = _text(title, "title", MAX_TITLE)
        body = _text(body, "body", MAX_BODY)
        category = _text(category, "category", 80).lower()
        created_by = _text(created_by, "created_by", 120)
        if status not in KNOWLEDGE_STATUSES:
            raise ValidationError("invalid knowledge status")
        source_url = _source_url(source_url)
        tags_json = json.dumps(_tags(tags), ensure_ascii=False)
        metadata_json = _metadata(metadata)
        item_id = _text(item_id or str(uuid.uuid4()), "item_id", 80)
        now = time.time()
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO tia_knowledge
                (id,title,body,category,status,source_url,tags_json,metadata_json,
                 content_sha256,created_at,updated_at,created_by)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """, (item_id,title,body,category,status,source_url,tags_json,
                  metadata_json,digest,now,now,created_by))
        return item_id

    def transition_knowledge(self, item_id: str, status: str) -> None:
        item_id = _text(item_id, "item_id", 80)
        if status not in KNOWLEDGE_STATUSES:
            raise ValidationError("invalid knowledge status")
        allowed = {
            "draft": {"review", "archived"},
            "review": {"approved", "rejected", "draft", "archived"},
            "approved": {"review", "archived"},
            "rejected": {"draft", "archived"},
            "archived": set(),
        }
        with self._connect() as conn:
            row = conn.execute("SELECT status FROM tia_knowledge WHERE id=?", (item_id,)).fetchone()
            if row is None:
                raise TIAStoreError("knowledge item not found")
            if status not in allowed[row["status"]]:
                raise ValidationError(f"transition {row['status']} -> {status} is not allowed")
            conn.execute(
                "UPDATE tia_knowledge SET status=?, updated_at=? WHERE id=?",
                (status, time.time(), item_id),
            )

    def list_knowledge(self, *, status: str | None = None,
                       category: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
            raise ValidationError("limit must be an integer from 1 to 200")
        clauses, params = [], []
        if status is not None:
            if status not in KNOWLEDGE_STATUSES:
                raise ValidationError("invalid knowledge status")
            clauses.append("status=?"); params.append(status)
        if category is not None:
            clauses.append("category=?"); params.append(_text(category, "category", 80).lower())
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tia_knowledge" + where + " ORDER BY updated_at DESC LIMIT ?",
                (*params, limit),
            ).fetchall()
        return [{
            **dict(row),
            "tags": json.loads(row["tags_json"]),
            "metadata": json.loads(row["metadata_json"]),
        } for row in rows]

    def append_meeting_event(
        self, *, meeting_id: str, kind: str, title: str, body: str,
        actor: str, related_ids: Iterable[str] | None = None,
        metadata: dict[str, Any] | None = None, event_id: str | None = None,
    ) -> str:
        meeting_id = _text(meeting_id, "meeting_id", 120)
        if kind not in MEETING_KINDS:
            raise ValidationError("invalid meeting event kind")
        title = _text(title, "title", MAX_TITLE)
        body = _text(body, "body", MAX_BODY)
        actor = _text(actor, "actor", 120)
        ids = []
        for value in related_ids or []:
            ids.append(_text(value, "related_id", 120))
            if len(ids) > 64:
                raise ValidationError("at most 64 related IDs are allowed")
        related_json = json.dumps(ids, ensure_ascii=False)
        metadata_json = _metadata(metadata)
        event_id = _text(event_id or str(uuid.uuid4()), "event_id", 80)
        now = time.time()
        with self._connect() as conn:
            previous = conn.execute(
                "SELECT event_hash FROM tia_meeting_events ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            previous_hash = previous["event_hash"] if previous else None
            payload = json.dumps({
                "event_id":event_id,"meeting_id":meeting_id,"kind":kind,
                "title":title,"body":body,"actor":actor,"related_ids":ids,
                "metadata":json.loads(metadata_json),"created_at":now,
                "previous_hash":previous_hash,
            }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            event_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            conn.execute("""
                INSERT INTO tia_meeting_events
                (event_id,meeting_id,kind,title,body,actor,related_ids_json,
                 metadata_json,created_at,previous_hash,event_hash)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """, (event_id,meeting_id,kind,title,body,actor,related_json,
                  metadata_json,now,previous_hash,event_hash))
        return event_id

    def list_meeting_events(self, *, meeting_id: str | None = None,
                            limit: int = 100) -> list[dict[str, Any]]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValidationError("limit must be an integer from 1 to 500")
        with self._connect() as conn:
            if meeting_id is None:
                rows = conn.execute(
                    "SELECT * FROM tia_meeting_events ORDER BY sequence DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            else:
                meeting_id = _text(meeting_id, "meeting_id", 120)
                rows = conn.execute(
                    "SELECT * FROM tia_meeting_events WHERE meeting_id=? ORDER BY sequence DESC LIMIT ?",
                    (meeting_id,limit),
                ).fetchall()
        return [{
            **dict(row),
            "related_ids": json.loads(row["related_ids_json"]),
            "metadata": json.loads(row["metadata_json"]),
        } for row in rows]

    def verify_meeting_chain(self) -> bool:
        """Verify event hash links and payload integrity without modifying records."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tia_meeting_events ORDER BY sequence ASC"
            ).fetchall()
        previous_hash = None
        for row in rows:
            if row["previous_hash"] != previous_hash:
                return False
            payload = json.dumps({
                "event_id":row["event_id"],"meeting_id":row["meeting_id"],
                "kind":row["kind"],"title":row["title"],"body":row["body"],
                "actor":row["actor"],"related_ids":json.loads(row["related_ids_json"]),
                "metadata":json.loads(row["metadata_json"]),
                "created_at":row["created_at"],"previous_hash":row["previous_hash"],
            }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            calculated = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            if calculated != row["event_hash"]:
                return False
            previous_hash = calculated
        return True
