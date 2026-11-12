"""Read-only aggregation for the Academy Intelligence / Trade Intelligence Center.

This module deliberately consumes existing published data and does not modify
Technical Office, Radar, Spot, Lab, Playbook or Research Hub engines.
"""
from __future__ import annotations

from datetime import datetime, timezone


def _safe(call, default):
    try:
        return call()
    except Exception:
        return default


def build_command_snapshot() -> dict:
    """Build a bounded snapshot from existing project sources; each source remains authoritative."""
    from modules import hub_core

    hub_ids = ("truth", "plateau", "regime", "trail", "decay", "consensus", "funnel")
    hub = {}
    for key in hub_ids:
        snap = _safe(lambda k=key: hub_core.read(k), None)
        if snap:
            hub[key] = {
                "asof": snap.get("asof"),
                "n_trials": snap.get("n_trials", 0),
                "findings": (snap.get("findings") or [])[:5],
            }

    tasks_data = _safe(lambda: __import__("modules.office_ui", fromlist=["load_tasks"]).load_tasks(), {"tasks": []})
    tasks = tasks_data.get("tasks", []) if isinstance(tasks_data, dict) else []
    task_counts: dict[str, int] = {}
    for task in tasks:
        state = str(task.get("status", "open"))
        task_counts[state] = task_counts.get(state, 0) + 1


    def _academy_count() -> int:
        # Rendering the dashboard must be read-only: legacy imports are explicit
        # migration actions, not side effects of a Streamlit rerun.
        ai = __import__("modules.academy_intelligence", fromlist=["initialize", "search_records"])
        ai.initialize()
        return len(ai.search_records(limit=200))

    academy_count = _safe(_academy_count, 0)
    legacy_count = _safe(lambda: len(__import__("modules.academy", fromlist=["load"]).load()), 0)
    lab_summary = _safe(lambda: __import__("modules.office_kpi", fromlist=["load", "summary"]).summary(
        __import__("modules.office_kpi", fromlist=["load"]).load()) or {}, {})

    meeting = _safe(lambda: __import__("modules.intelligence_meeting", fromlist=["meeting_summary"]).meeting_summary(), {})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tasks": {"total": len(tasks), "by_status": task_counts, "open": [
            {k: t.get(k) for k in ("wbs", "title", "title_ar", "owner", "owner_ar", "status", "next", "next_ar")}
            for t in tasks if t.get("status") not in ("done", "closed")
        ][:20]},
        "academy": {"indexed_records": academy_count, "legacy_lessons": legacy_count},
        "lab": {k: lab_summary.get(k) for k in ("built", "passed", "candidates", "detectors", "symbols")} if lab_summary else {},
        "research_hub": hub,
        "meeting_room": meeting,
        "source_ownership": {
            "technical_office": "read_only",
            "radar": "read_only",
            "spot": "read_only",
            "lab": "authoritative_validation",
            "research_hub": "published_snapshots_only",
        },
    }
