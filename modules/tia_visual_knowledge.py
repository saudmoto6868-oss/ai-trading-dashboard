"""Structured, guarded knowledge extracted from user-provided trading reference images.

This is an educational catalog. It does not detect patterns, create signals, or
claim that the pictured setups are profitable.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tia_visual_knowledge.json"
REQUIRED_MODULE_FIELDS = ("id", "title", "patterns", "required_context", "caution")


def load_knowledge(path: Path = DATA_PATH) -> dict[str, Any]:
    """Load and validate the catalog; malformed or duplicate modules are skipped."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"schema_version": 1, "status": "unavailable", "modules": [], "guardrails": [], "workflow": []}
    if not isinstance(raw, dict) or not isinstance(raw.get("modules"), list):
        return {"schema_version": 1, "status": "unavailable", "modules": [], "guardrails": [], "workflow": []}
    modules, seen = [], set()
    for item in raw["modules"]:
        if not isinstance(item, dict) or not all(item.get(k) for k in REQUIRED_MODULE_FIELDS):
            continue
        if item["id"] in seen:
            continue
        if not isinstance(item["patterns"], list) or not isinstance(item["required_context"], list):
            continue
        seen.add(item["id"])
        modules.append(item)
    return {
        "schema_version": raw.get("schema_version", 1),
        "status": raw.get("status", "educational_reference_unvalidated"),
        "modules": modules,
        "guardrails": list(raw.get("guardrails", [])),
        "workflow": list(raw.get("workflow", [])),
    }


def module_status(knowledge: dict, module_id: str, capabilities: dict[str, bool] | None = None) -> dict:
    """Report capability readiness without implying that a detector/feed exists."""
    capabilities = capabilities or {}
    item = next((m for m in knowledge.get("modules", []) if m.get("id") == module_id), None)
    if item is None:
        return {"status": "unknown", "available": False, "reason": "Knowledge module not found"}
    if module_id == "volume_profile" and not capabilities.get("volume_at_price", False):
        return {"status": "blocked_missing_data", "available": False,
                "reason": "Requires verified volume-at-price data; OHLCV candles are insufficient"}
    if module_id == "order_flow_footprint" and not capabilities.get("classified_trades", False):
        return {"status": "blocked_missing_data", "available": False,
                "reason": "Requires verified aggressor-side trade prints and coverage metadata"}
    return {"status": "reference_only", "available": False,
            "reason": "Educational reference only; no validated detector or signal is connected"}


def summary(knowledge: dict) -> dict:
    """Compact counts for a future TIA panel."""
    modules = knowledge.get("modules", [])
    return {
        "status": knowledge.get("status", "unavailable"),
        "module_count": len(modules),
        "pattern_count": sum(len(m.get("patterns", [])) for m in modules),
        "guardrail_count": len(knowledge.get("guardrails", [])),
    }
