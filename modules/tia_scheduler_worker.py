"""Supervised TIA schedule dispatcher.

This worker materializes due schedules as durable QUEUED tasks. It does not run agents,
call external tools, send orders, or treat task creation as task completion.
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta, timezone

from modules.tia_agent_store import TIAStore
from modules.tia_session_scheduler import next_occurrence, utc_iso

LOGGER = logging.getLogger(__name__)


def run_once(store: TIAStore | None = None, now: datetime | None = None,
             limit: int = 20, retry_seconds: int = 300) -> dict:
    store = store or TIAStore()
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(timezone.utc)
    now_iso = utc_iso(now)
    claimed = store.claim_due_jobs(now_iso, limit=limit, actor="tia-scheduler-worker")
    result = {"claimed": len(claimed), "enqueued": 0, "failed": 0, "task_ids": []}

    for job in claimed:
        due_at = job["next_run_at"]
        idem = "schedule:{}:{}".format(job["job_id"], due_at)
        try:
            task_id = store.create_task(
                title=job["title"],
                description="Recurring scheduled task. Schedule ID: {}. Due occurrence: {}.".format(job["job_id"], due_at),
                owner_agent_id=job["owner_agent_id"],
                task_type="monitoring",
                due_at=due_at,
                ongoing=True,
                payload={"schedule_id": job["job_id"], "scheduled_for": due_at,
                         "timezone": job["timezone"], "schedule": job["schedule"]},
                idempotency_key=idem,
                actor="tia-scheduler-worker",
            )
            rule = job["schedule"]
            following = next_occurrence(rule, job["timezone"], now)
            store.record_scheduled_run(job["job_id"], utc_iso(following), "enqueued",
                                       actor="tia-scheduler-worker")
            result["enqueued"] += 1
            result["task_ids"].append(task_id)
        except Exception as exc:
            retry_at = utc_iso(now + timedelta(seconds=max(30, min(int(retry_seconds), 3600))))
            try:
                store.record_scheduled_run(job["job_id"], retry_at, "failed",
                                           actor="tia-scheduler-worker")
            except Exception:
                LOGGER.exception("Could not release failed schedule lease: %s", job["job_id"])
            result["failed"] += 1
            LOGGER.exception("Scheduled job dispatch failed: %s", job["job_id"])
    return result


def run_forever(stop_event: threading.Event, poll_seconds: int = 15,
                store: TIAStore | None = None) -> None:
    """Polling loop for an external process supervisor; stop_event enables graceful shutdown."""
    interval = max(2, min(int(poll_seconds), 300))
    repository = store or TIAStore()
    while not stop_event.is_set():
        try:
            run_once(repository)
        except Exception:
            LOGGER.exception("TIA scheduler worker cycle failed")
        stop_event.wait(interval)
