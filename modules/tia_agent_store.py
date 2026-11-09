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

SCHEMA_VERSION = 4
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


def _safe_text(value: str, field: str) -> str:
    text = str(value or "").strip()
    if re.search(r"(?i)(bearer\\s+[A-Za-z0-9._~+/-]{12,}|(?:api[_-]?key|password|secret|access[_-]?token)\\s*[:=]\\s*[^\\s,;]{8,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)", text):
        raise ValueError(f"raw credentials are forbidden in {field}; use a secret reference")
    return text


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
            # Additive migration preserves all existing records.
            db.executescript("""
            CREATE TABLE IF NOT EXISTS scheduled_jobs (
                job_id TEXT PRIMARY KEY, title TEXT NOT NULL, owner_agent_id TEXT NOT NULL,
                schedule_json TEXT NOT NULL, timezone TEXT NOT NULL, next_run_at TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1, lease_until TEXT, last_run_at TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL, idempotency_key TEXT UNIQUE,
                FOREIGN KEY(owner_agent_id) REFERENCES agent_profiles(agent_id)
            );
            CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_due ON scheduled_jobs(enabled,next_run_at,lease_until);
            CREATE TABLE IF NOT EXISTS scheduler_events (
                event_id TEXT PRIMARY KEY, job_id TEXT NOT NULL, event_type TEXT NOT NULL,
                actor TEXT NOT NULL, created_at TEXT NOT NULL, payload_json TEXT NOT NULL,
                FOREIGN KEY(job_id) REFERENCES scheduled_jobs(job_id)
            );
            CREATE TABLE IF NOT EXISTS agent_messages (
                message_id TEXT PRIMARY KEY, sender_agent_id TEXT NOT NULL,
                receiver_agent_id TEXT NOT NULL, message_type TEXT NOT NULL,
                subject TEXT NOT NULL, body TEXT NOT NULL, payload_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'sent', created_at TEXT NOT NULL,
                acknowledged_at TEXT, correlation_id TEXT NOT NULL,
                FOREIGN KEY(sender_agent_id) REFERENCES agent_profiles(agent_id),
                FOREIGN KEY(receiver_agent_id) REFERENCES agent_profiles(agent_id)
            );
            CREATE INDEX IF NOT EXISTS idx_agent_messages_inbox ON agent_messages(receiver_agent_id,status,created_at);
            CREATE INDEX IF NOT EXISTS idx_agent_messages_outbox ON agent_messages(sender_agent_id,created_at);
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
        do = [_safe_text(x, "agent instructions") for x in do]
        dont = [_safe_text(x, "agent instructions") for x in dont]
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
        title = _safe_text(title, "task title")
        description = _safe_text(description, "task description")
        if not title or len(title) > 160:
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
        content = _safe_text(content, "agent memory")
        if not content or len(content) > 12000:
            raise ValueError("memory content must contain 1..12000 characters")
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

    def create_agent_message(self, sender_agent_id, receiver_agent_id, message_type, subject, body, payload=None, correlation_id=None):
        allowed = {"analysis", "alert", "question", "decision", "task_handoff", "status"}
        if message_type not in allowed: raise ValueError("unsupported agent message type")
        subject = _safe_text(subject, "message subject")
        body = _safe_text(body, "message body")
        if not subject or len(subject) > 160 or not body or len(body) > 12000:
            raise ValueError("message subject/body length is invalid")
        safe = _redact(payload or {})
        message_id, now = str(uuid.uuid4()), utc_now()
        correlation = correlation_id or str(uuid.uuid4())
        with self._connect() as db:
            for agent_id in (sender_agent_id, receiver_agent_id):
                if not db.execute("SELECT 1 FROM agent_profiles WHERE agent_id=?", (agent_id,)).fetchone(): raise KeyError(agent_id)
            db.execute("INSERT INTO agent_messages VALUES(?,?,?,?,?,?,?,'sent',?,NULL,?)",
                       (message_id, sender_agent_id, receiver_agent_id, message_type, subject, body, _json(safe), now, correlation))
            self._audit(db, "agent_message", message_id, sender_agent_id, "message.sent",
                        {"receiver_agent_id": receiver_agent_id, "message_type": message_type}, correlation)
        return message_id

    def list_agent_messages(self, agent_id, mailbox="inbox", status=None, limit=100):
        if mailbox not in {"inbox", "outbox", "all"}: raise ValueError("mailbox must be inbox, outbox or all")
        limit = max(1, min(int(limit), 500))
        if mailbox == "inbox": clauses, params = ["receiver_agent_id=?"], [agent_id]
        elif mailbox == "outbox": clauses, params = ["sender_agent_id=?"], [agent_id]
        else: clauses, params = ["(sender_agent_id=? OR receiver_agent_id=?)"], [agent_id, agent_id]
        if status: clauses.append("status=?"); params.append(status)
        params.append(limit)
        with self._connect() as db:
            rows = db.execute("SELECT * FROM agent_messages WHERE " + " AND ".join(clauses) + " ORDER BY created_at DESC LIMIT ?", params).fetchall()
        return [{**dict(row), "payload": json.loads(row["payload_json"])} for row in rows]

    def acknowledge_agent_message(self, message_id, actor_agent_id):
        with self._connect() as db:
            row = db.execute("SELECT receiver_agent_id,status FROM agent_messages WHERE message_id=?", (message_id,)).fetchone()
            if not row: raise KeyError(message_id)
            if row["receiver_agent_id"] != actor_agent_id: raise PermissionError("only the receiving agent may acknowledge")
            if row["status"] == "acknowledged": return
            now = utc_now()
            db.execute("UPDATE agent_messages SET status='acknowledged',acknowledged_at=? WHERE message_id=?", (now, message_id))
            self._audit(db, "agent_message", message_id, actor_agent_id, "message.acknowledged", {})

    def search_memory(self, agent_id, query, memory_type=None, limit=50):
        query = _safe_text(query, "memory search query")
        if not query: raise ValueError("memory search query is required")
        terms = [term for term in re.findall(r"[\\w-]+", query) if len(term) > 1][:8]
        if not terms: return []
        clauses, params = ["agent_id=?"], [agent_id]
        if memory_type: clauses.append("memory_type=?"); params.append(memory_type)
        for term in terms: clauses.append("content LIKE ?"); params.append("%" + term + "%")
        params.append(max(1, min(int(limit), 200)))
        with self._connect() as db:
            rows = db.execute("SELECT * FROM memory_items WHERE " + " AND ".join(clauses) + " ORDER BY created_at DESC LIMIT ?", params).fetchall()
        return [{**dict(row), "provenance": json.loads(row["provenance_json"])} for row in rows]

    def create_scheduled_job(self, title, owner_agent_id, schedule, timezone_name, next_run_at, idempotency_key=None, actor="owner"):
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        from modules.tia_session_scheduler import validate_weekly_rule
        title = _safe_text(title, "scheduled job title")
        if not title or len(title) > 160 or not next_run_at.endswith("Z"):
            raise ValueError("valid title and UTC next_run_at are required")
        try: ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc: raise ValueError("unknown IANA timezone") from exc
        safe = validate_weekly_rule(schedule)
        job_id, now = str(uuid.uuid4()), utc_now()
        with self._connect() as db:
            if not db.execute("SELECT 1 FROM agent_profiles WHERE agent_id=? AND enabled=1", (owner_agent_id,)).fetchone():
                raise ValueError("owner agent is missing or disabled")
            if idempotency_key:
                old = db.execute("SELECT job_id FROM scheduled_jobs WHERE idempotency_key=?", (idempotency_key,)).fetchone()
                if old: return old["job_id"]
            db.execute("INSERT INTO scheduled_jobs VALUES(?,?,?,?,?,?,1,NULL,NULL,?,?,?)",
                       (job_id, title, owner_agent_id, _json(safe), timezone_name, next_run_at, now, now, idempotency_key))
            self._scheduler_event(db, job_id, "schedule.created", actor, {"timezone":timezone_name,"next_run_at":next_run_at})
        return job_id

    def _scheduler_event(self, db, job_id, event_type, actor, payload):
        db.execute("INSERT INTO scheduler_events VALUES(?,?,?,?,?,?)",
                   (str(uuid.uuid4()), job_id, event_type, actor, utc_now(), _json(_redact(payload))))

    def list_scheduled_jobs(self, enabled=None, limit=100):
        limit=max(1,min(int(limit),500))
        with self._connect() as db:
            if enabled is None: rows=db.execute("SELECT * FROM scheduled_jobs ORDER BY next_run_at LIMIT ?",(limit,)).fetchall()
            else: rows=db.execute("SELECT * FROM scheduled_jobs WHERE enabled=? ORDER BY next_run_at LIMIT ?",(int(enabled),limit)).fetchall()
        return [{**dict(x),"schedule":json.loads(x["schedule_json"]),"enabled":bool(x["enabled"])} for x in rows]

    def set_scheduled_job_enabled(self, job_id, enabled, actor="owner"):
        with self._connect() as db:
            cur=db.execute("UPDATE scheduled_jobs SET enabled=?,updated_at=? WHERE job_id=?",(int(bool(enabled)),utc_now(),job_id))
            if not cur.rowcount: raise KeyError(job_id)
            self._scheduler_event(db,job_id,"schedule.enabled_changed",actor,{"enabled":bool(enabled)})

    def claim_due_jobs(self, now_utc, lease_seconds=120, limit=20, actor="scheduler"):
        from datetime import timedelta
        now=datetime.fromisoformat(now_utc.replace("Z","+00:00"))
        if now.tzinfo is None: raise ValueError("now_utc must be timezone-aware")
        now=now.astimezone(timezone.utc)
        now_s=now.isoformat(timespec="seconds").replace("+00:00","Z")
        lease_s=(now+timedelta(seconds=max(10,min(int(lease_seconds),3600)))).isoformat(timespec="seconds").replace("+00:00","Z")
        claimed=[]
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows=db.execute("SELECT * FROM scheduled_jobs WHERE enabled=1 AND next_run_at<=? AND (lease_until IS NULL OR lease_until<=?) ORDER BY next_run_at LIMIT ?",(now_s,now_s,max(1,min(int(limit),100)))).fetchall()
            for row in rows:
                cur=db.execute("UPDATE scheduled_jobs SET lease_until=?,updated_at=? WHERE job_id=? AND (lease_until IS NULL OR lease_until<=?)",(lease_s,now_s,row["job_id"],now_s))
                if cur.rowcount:
                    item=dict(row); item["schedule"]=json.loads(item.pop("schedule_json")); claimed.append(item)
                    self._scheduler_event(db,row["job_id"],"schedule.claimed",actor,{"lease_until":lease_s,"due_at":row["next_run_at"]})
        return claimed

    def record_scheduled_run(self, job_id, next_run_at, outcome, actor="scheduler"):
        if outcome not in {"enqueued","skipped","failed"}: raise ValueError("unsupported scheduler outcome")
        if next_run_at is not None and not next_run_at.endswith("Z"): raise ValueError("next_run_at must be UTC ISO-8601")
        now=utc_now()
        with self._connect() as db:
            if not db.execute("SELECT 1 FROM scheduled_jobs WHERE job_id=?",(job_id,)).fetchone(): raise KeyError(job_id)
            db.execute("UPDATE scheduled_jobs SET last_run_at=?,next_run_at=COALESCE(?,next_run_at),lease_until=NULL,updated_at=? WHERE job_id=?",(now,next_run_at,now,job_id))
            self._scheduler_event(db,job_id,"schedule.run_recorded",actor,{"outcome":outcome,"next_run_at":next_run_at})
