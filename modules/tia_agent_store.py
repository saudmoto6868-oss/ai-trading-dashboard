"""Persistent TIA agent registry, task store and append-only audit log.

SQLite-backed foundation. No network calls, LLM execution, broker access or secret
retrieval. Permission checks for external actions must be implemented server-side
before any worker is allowed to invoke tools.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.tia_agent_charter import default_roster, validate_profile

SCHEMA_VERSION = 1
TASK_STATES = {
    "draft": {"queued", "cancelled"},
    "queued": {"running", "cancelled", "blocked"},
    "running": {"needs_approval", "completed", "failed", "cancelled", "blocked"},
    "needs_approval": {"approved", "cancelled", "blocked"},
    "approved": {"executing", "cancelled", "blocked"},
    "executing": {"completed", "failed", "cancelled", "blocked"},
    "blocked": {"queued", "cancelled"},
    "completed": set(), "failed": {"queued"}, "cancelled": set(),
}
SECRET_KEY_RE = re.compile(r"(secret|password|passwd|api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|private[_-]?key)", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _redact(value: Any, key: str = "") -> Any:
    """Reject raw secret-like fields; redact likely credential strings in payloads."""
    if SECRET_KEY_RE.search(key):
        raise ValueError(f"raw secret field is forbidden: {key}")
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(v, key) for v in value]
    if isinstance(value, str):
        if value.lower().startswith(("bearer ", "token=", "api_key=", "password=")):
            return "[REDACTED]"
        return value
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


class TIAStore:
    """Small transactional repository. Use one instance per process/request."""

    def __init__(self, db_path: str | os.PathLike | None = None):
        default = os.environ.get("TIA_AGENT_DB", "data/tia_agents.sqlite3")
        self.db_path = str(db_path or default)
        self._memory_uri = None
        self._memory_keeper = None
        if self.db_path == ":memory:":
            self._memory_uri = "file:tia_agents_" + uuid.uuid4().hex + "?mode=memory&cache=shared"
            self._memory_keeper = sqlite3.connect(self._memory_uri, uri=True, timeout=15)
        else:
            Path(self.db_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def _connect(self):
        conn = (sqlite3.connect(self._memory_uri, uri=True, timeout=15)
                if self._memory_uri else sqlite3.connect(self.db_path, timeout=15))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=15000")
        if not self._memory_uri:
            conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS agent_profiles (
                agent_id TEXT PRIMARY KEY, display_name TEXT NOT NULL,
                mission TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1,
                role_version INTEGER NOT NULL DEFAULT 1,
                profile_json TEXT NOT NULL, created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS instruction_versions (
                instruction_id TEXT PRIMARY KEY, agent_id TEXT NOT NULL,
                version INTEGER NOT NULL, do_json TEXT NOT NULL,
                dont_json TEXT NOT NULL, created_at TEXT NOT NULL,
                created_by TEXT NOT NULL, UNIQUE(agent_id, version),
                FOREIGN KEY(agent_id) REFERENCES agent_profiles(agent_id)
            );
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY, title TEXT NOT NULL,
                description TEXT NOT NULL, owner_agent_id TEXT NOT NULL,
                status TEXT NOT NULL, task_type TEXT NOT NULL,
                session_key TEXT, due_at TEXT, expires_at TEXT,
                ongoing INTEGER NOT NULL DEFAULT 0,
                idempotency_key TEXT UNIQUE, created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL, payload_json TEXT NOT NULL,
                FOREIGN KEY(owner_agent_id) REFERENCES agent_profiles(agent_id)
            );
            CREATE TABLE IF NOT EXISTS task_events (
                event_id TEXT PRIMARY KEY, task_id TEXT NOT NULL,
                actor TEXT NOT NULL, event_type TEXT NOT NULL,
                from_state TEXT, to_state TEXT, created_at TEXT NOT NULL,
                correlation_id TEXT NOT NULL, payload_json TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(task_id)
            );
            CREATE TABLE IF NOT EXISTS memory_items (
                memory_id TEXT PRIMARY KEY, agent_id TEXT NOT NULL,
                memory_type TEXT NOT NULL, content TEXT NOT NULL,
                provenance_json TEXT NOT NULL, created_at TEXT NOT NULL,
                created_by TEXT NOT NULL, supersedes_id TEXT,
                FOREIGN KEY(agent_id) REFERENCES agent_profiles(agent_id),
                FOREIGN KEY(supersedes_id) REFERENCES memory_items(memory_id)
            );
            CREATE TABLE IF NOT EXISTS session_handoffs (
                handoff_id TEXT PRIMARY KEY, session_key TEXT NOT NULL,
                sender_agent_id TEXT NOT NULL, receiver_agent_id TEXT NOT NULL,
                created_at TEXT NOT NULL, acknowledged_at TEXT,
                report_json TEXT NOT NULL,
                FOREIGN KEY(sender_agent_id) REFERENCES agent_profiles(agent_id),
                FOREIGN KEY(receiver_agent_id) REFERENCES agent_profiles(agent_id)
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY, entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL, actor TEXT NOT NULL,
                event_type TEXT NOT NULL, created_at TEXT NOT NULL,
                correlation_id TEXT NOT NULL, payload_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_tasks_status_updated ON tasks(status, updated_at);
            CREATE INDEX IF NOT EXISTS idx_task_events_task_time ON task_events(task_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_memory_agent_type_time ON memory_items(agent_id, memory_type, created_at);
            CREATE INDEX IF NOT EXISTS idx_audit_entity_time ON audit_events(entity_type, entity_id, created_at);
            """)
            db.execute("INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES(?,?)", (SCHEMA_VERSION, utc_now()))
        self.seed_roster()

    def _audit(self, db, entity_type: str, entity_id: str, actor: str,
               event_type: str, payload: dict | None = None,
               correlation_id: str | None = None) -> str:
        event_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO audit_events VALUES(?,?,?,?,?,?,?,?)",
            (event_id, entity_type, entity_id, actor, event_type, utc_now(),
             correlation_id or str(uuid.uuid4()), _json(_redact(payload or {}))),
        )
        return event_id

    def seed_roster(self) -> int:
        inserted = 0
        with self._connect() as db:
            for p in default_roster():
                exists = db.execute("SELECT 1 FROM agent_profiles WHERE agent_id=?", (p["id"],)).fetchone()
                if exists:
                    continue
                errors = validate_profile({**p, "id": p["id"], "display_name": p["display_name"]})
                if errors:
                    raise ValueError("; ".join(errors))
                now = utc_now()
                db.execute(
                    "INSERT INTO agent_profiles VALUES(?,?,?,?,?,?,?,?)",
                    (p["id"], p["display_name"], p["mission"], 1, 1, _json(p), now, now),
                )
                db.execute(
                    "INSERT INTO instruction_versions VALUES(?,?,?,?,?,?,?)",
                    (str(uuid.uuid4()), p["id"], 1, "[]", "[]", now, "system:seed"),
                )
                self._audit(db, "agent", p["id"], "system:seed", "agent.created",
                            {"display_name": p["display_name"], "role_version": 1})
                inserted += 1
        return inserted

    def list_agents(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM agent_profiles ORDER BY agent_id").fetchall()
        return [self._profile_row(r) for r in rows]

    @staticmethod
    def _profile_row(row) -> dict:
        item = dict(row)
        item["enabled"] = bool(item["enabled"])
        item["profile"] = json.loads(item.pop("profile_json"))
        return item

    def rename_agent(self, agent_id: str, display_name: str, actor: str = "owner") -> dict:
        name = str(display_name).strip()
        if not name or len(name) > 80:
            raise ValueError("display name must contain 1..80 characters")
        with self._connect() as db:
            row = db.execute("SELECT display_name FROM agent_profiles WHERE agent_id=?", (agent_id,)).fetchone()
            if not row:
                raise KeyError(agent_id)
            old = row["display_name"]
            db.execute("UPDATE agent_profiles SET display_name=?, updated_at=? WHERE agent_id=?",
                       (name, utc_now(), agent_id))
            self._audit(db, "agent", agent_id, actor, "agent.renamed", {"old": old, "new": name})
        return next(a for a in self.list_agents() if a["agent_id"] == agent_id)

    def set_agent_enabled(self, agent_id: str, enabled: bool, actor: str = "owner") -> None:
        with self._connect() as db:
            cur = db.execute("UPDATE agent_profiles SET enabled=?, updated_at=? WHERE agent_id=?",
                             (int(bool(enabled)), utc_now(), agent_id))
            if not cur.rowcount:
                raise KeyError(agent_id)
            self._audit(db, "agent", agent_id, actor, "agent.enabled_changed", {"enabled": bool(enabled)})

    def set_instructions(self, agent_id: str, do: list[str] | None = None,
                         dont: list[str] | None = None, actor: str = "owner") -> int:
        do, dont = list(do or []), list(dont or [])
        if any(not isinstance(x, str) or not x.strip() or len(x) > 1000 for x in do + dont):
            raise ValueError("instructions must be non-empty strings up to 1000 characters")
        if len(do) > 50 or len(dont) > 50:
            raise ValueError("maximum 50 Do and 50 Don't instructions")
        with self._connect() as db:
            if not db.execute("SELECT 1 FROM agent_profiles WHERE agent_id=?", (agent_id,)).fetchone():
                raise KeyError(agent_id)
            version = db.execute("SELECT COALESCE(MAX(version),0)+1 FROM instruction_versions WHERE agent_id=?",
                                 (agent_id,)).fetchone()[0]
            now = utc_now()
            db.execute("INSERT INTO instruction_versions VALUES(?,?,?,?,?,?,?)",
                       (str(uuid.uuid4()), agent_id, version, _json(do), _json(dont), now, actor))
            self._audit(db, "agent", agent_id, actor, "agent.instructions_versioned",
                        {"version": version, "do_count": len(do), "dont_count": len(dont)})
        return version

    def get_instructions(self, agent_id: str) -> dict:
        with self._connect() as db:
            row = db.execute("SELECT * FROM instruction_versions WHERE agent_id=? ORDER BY version DESC LIMIT 1",
                             (agent_id,)).fetchone()
        if not row:
            raise KeyError(agent_id)
        return {"version": row["version"], "do": json.loads(row["do_json"]),
                "dont": json.loads(row["dont_json"]), "created_at": row["created_at"]}

    def create_task(self, title: str, description: str, owner_agent_id: str,
                    task_type: str = "analysis", session_key: str | None = None,
                    due_at: str | None = None, expires_at: str | None = None,
                    ongoing: bool = False, payload: dict | None = None,
                    idempotency_key: str | None = None, actor: str = "owner") -> str:
        if not title.strip() or len(title) > 160:
            raise ValueError("task title must contain 1..160 characters")
        safe_payload = _redact(payload or {})
        task_id = str(uuid.uuid4())
        now = utc_now()
        with self._connect() as db:
            if not db.execute("SELECT 1 FROM agent_profiles WHERE agent_id=? AND enabled=1",
                              (owner_agent_id,)).fetchone():
                raise ValueError("owner agent is missing or disabled")
            if idempotency_key:
                old = db.execute("SELECT task_id FROM tasks WHERE idempotency_key=?", (idempotency_key,)).fetchone()
                if old:
                    return old["task_id"]
            db.execute(
                "INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (task_id, title.strip(), description.strip(), owner_agent_id, "queued",
                 task_type, session_key, due_at, expires_at, int(ongoing),
                 idempotency_key, now, now, _json(safe_payload)),
            )
            self._task_event(db, task_id, actor, "task.created", None, "queued",
                             {"title": title, "owner": owner_agent_id})
        return task_id

    def _task_event(self, db, task_id, actor, event_type, old_state, new_state, payload, correlation_id=None):
        event_id = str(uuid.uuid4())
        corr = correlation_id or str(uuid.uuid4())
        safe = _json(_redact(payload or {}))
        db.execute("INSERT INTO task_events VALUES(?,?,?,?,?,?,?,?,?)",
                   (event_id, task_id, actor, event_type, old_state, new_state, utc_now(), corr, safe))
        db.execute("INSERT INTO audit_events VALUES(?,?,?,?,?,?,?,?)",
                   (str(uuid.uuid4()), "task", task_id, actor, event_type, utc_now(), corr, safe))

    def transition_task(self, task_id: str, new_state: str, actor: str,
                        payload: dict | None = None, correlation_id: str | None = None) -> None:
        if new_state not in TASK_STATES:
            raise ValueError("unknown task state")
        with self._connect() as db:
            row = db.execute("SELECT status FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not row:
                raise KeyError(task_id)
            old = row["status"]
            if new_state not in TASK_STATES[old]:
                raise ValueError(f"invalid task transition: {old} -> {new_state}")
            db.execute("UPDATE tasks SET status=?, updated_at=? WHERE task_id=?",
                       (new_state, utc_now(), task_id))
            self._task_event(db, task_id, actor, "task.state_changed", old, new_state,
                             payload or {}, correlation_id)

    def list_tasks(self, status: str | None = None, limit: int = 100) -> list[dict]:
        limit = max(1, min(int(limit), 500))
        with self._connect() as db:
            if status:
                rows = db.execute("SELECT * FROM tasks WHERE status=? ORDER BY created_at DESC LIMIT ?",
                                  (status, limit)).fetchall()
            else:
                rows = db.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for row in rows:
            item = dict(row)
            item["ongoing"] = bool(item["ongoing"])
            item["payload"] = json.loads(item.pop("payload_json"))
            out.append(item)
        return out

    def task_history(self, task_id: str) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM task_events WHERE task_id=? ORDER BY created_at,event_id",
                              (task_id,)).fetchall()
        return [{**dict(r), "payload": json.loads(r["payload_json"])} for r in rows]

    def add_memory(self, agent_id: str, memory_type: str, content: str,
                   provenance: dict | None = None, actor: str = "system",
                   supersedes_id: str | None = None) -> str:
        allowed = {"episodic", "research", "evaluation", "standing_instruction"}
        if memory_type not in allowed:
            raise ValueError("unsupported memory type")
        if not content.strip() or len(content) > 12000:
            raise ValueError("memory content must contain 1..12000 characters")
        if re.search(r"(?i)(bearer\\s+[A-Za-z0-9._~+/-]{12,}|(?:api[_-]?key|password|secret|access[_-]?token)\\s*[:=]\\s*[^\\s,;]{8,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)", content):
            raise ValueError("raw credentials are forbidden in agent memory; store a secret reference instead")
        memory_id = str(uuid.uuid4())
        with self._connect() as db:
            if not db.execute("SELECT 1 FROM agent_profiles WHERE agent_id=?", (agent_id,)).fetchone():
                raise KeyError(agent_id)
            db.execute("INSERT INTO memory_items VALUES(?,?,?,?,?,?,?,?)",
                       (memory_id, agent_id, memory_type, content,
                        _json(_redact(provenance or {})), utc_now(), actor, supersedes_id))
            self._audit(db, "memory", memory_id, actor, "memory.created",
                        {"agent_id": agent_id, "memory_type": memory_type, "supersedes_id": supersedes_id})
        return memory_id

    def list_memory(self, agent_id: str, memory_type: str | None = None, limit: int = 100) -> list[dict]:
        limit = max(1, min(int(limit), 500))
        with self._connect() as db:
            if memory_type:
                rows = db.execute("SELECT * FROM memory_items WHERE agent_id=? AND memory_type=? ORDER BY created_at DESC LIMIT ?",
                                  (agent_id, memory_type, limit)).fetchall()
            else:
                rows = db.execute("SELECT * FROM memory_items WHERE agent_id=? ORDER BY created_at DESC LIMIT ?",
                                  (agent_id, limit)).fetchall()
        return [{**dict(r), "provenance": json.loads(r["provenance_json"])} for r in rows]

    def create_handoff(self, session_key: str, sender_agent_id: str,
                       receiver_agent_id: str, report: dict, actor: str | None = None) -> str:
        handoff_id = str(uuid.uuid4())
        safe = _redact(report)
        with self._connect() as db:
            for agent_id in (sender_agent_id, receiver_agent_id):
                if not db.execute("SELECT 1 FROM agent_profiles WHERE agent_id=?", (agent_id,)).fetchone():
                    raise KeyError(agent_id)
            db.execute("INSERT INTO session_handoffs VALUES(?,?,?,?,?,?,?)",
                       (handoff_id, session_key, sender_agent_id, receiver_agent_id,
                        utc_now(), None, _json(safe)))
            self._audit(db, "handoff", handoff_id, actor or sender_agent_id,
                        "handoff.created", {"session_key": session_key, "report": safe})
        return handoff_id

    def acknowledge_handoff(self, handoff_id: str, actor: str) -> None:
        with self._connect() as db:
            row = db.execute("SELECT receiver_agent_id,acknowledged_at FROM session_handoffs WHERE handoff_id=?",
                             (handoff_id,)).fetchone()
            if not row:
                raise KeyError(handoff_id)
            if row["receiver_agent_id"] != actor:
                raise PermissionError("only the designated receiving agent may acknowledge")
            if row["acknowledged_at"]:
                return
            now = utc_now()
            db.execute("UPDATE session_handoffs SET acknowledged_at=? WHERE handoff_id=?", (now, handoff_id))
            self._audit(db, "handoff", handoff_id, actor, "handoff.acknowledged", {})

    def audit_history(self, entity_type: str | None = None, entity_id: str | None = None,
                      limit: int = 200) -> list[dict]:
        limit = max(1, min(int(limit), 1000))
        clauses, params = [], []
        if entity_type:
            clauses.append("entity_type=?"); params.append(entity_type)
        if entity_id:
            clauses.append("entity_id=?"); params.append(entity_id)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._connect() as db:
            rows = db.execute("SELECT * FROM audit_events" + where +
                              " ORDER BY created_at DESC LIMIT ?", (*params, limit)).fetchall()
        return [{**dict(r), "payload": json.loads(r["payload_json"])} for r in rows]
