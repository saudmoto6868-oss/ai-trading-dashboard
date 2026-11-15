"""Read-only cross-platform knowledge router for TIA-owned shared research guidance.

Other platform areas may import these public functions without changing their owned files.
The router never fetches market data, creates signals, grades trades, or places orders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "tia_platform_knowledge_registry.json"


def load_registry(path: str | Path = REGISTRY_PATH) -> dict[str, Any]:
    """Load the versioned knowledge registry; return a safe empty registry on failure."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) and isinstance(data.get("routes"), dict) else {"routes": {}, "schools": {}}
    except (OSError, ValueError, TypeError):
        return {"routes": {}, "schools": {}}


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().replace("_", " ").replace("-", " ").split())


def resolve_guidance(
    page: str,
    feature: str | None = None,
    *,
    task: str | None = None,
    available_data: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve the most relevant platform route and return auditable study guidance.

    available_data is capability metadata only, e.g. {"volume_at_price": False,
    "classified_trades": True}; it must not contain secrets or raw market payloads.
    """
    data = registry if isinstance(registry, dict) else load_registry()
    routes = data.get("routes", {})
    page_key, feature_key = _norm(page), _norm(feature)
    route = None
    route_id = None

    # Exact page + feature match first, then page-wide fallback.
    for key, item in routes.items():
        if _norm(item.get("page")) == page_key and feature_key and feature_key in {
            _norm(x) for x in item.get("features", [])
        }:
            route, route_id = item, key
            break
    if route is None:
        for key, item in routes.items():
            if _norm(item.get("page")) == page_key and item.get("default_for_page"):
                route, route_id = item, key
                break
    if route is None:
        return {
            "status": "unmapped", "route_id": None, "page": page, "feature": feature,
            "message": "No registered guidance route. Keep the UI functional and request a registry addition.",
            "schools": [], "thinking_steps": [], "missing_capabilities": [],
            "related_routes": [],
        }

    schools = data.get("schools", {})
    school_cards = []
    missing = []
    caps = available_data or {}
    for school_id in route.get("schools", []):
        school = schools.get(school_id, {})
        required = school.get("requires_capabilities", [])
        absent = [cap for cap in required if caps.get(cap) is not True]
        if absent:
            missing.extend({"school": school_id, "capability": cap} for cap in absent)
        school_cards.append({
            "id": school_id,
            "name": school.get("name", school_id),
            "role": school.get("role", "context"),
            "use_when": school.get("use_when", []),
            "limits": school.get("limits", []),
            "blocked_by": absent,
        })

    return {
        "status": "ready_with_gates" if missing else "guidance_ready",
        "route_id": route_id,
        "page": route.get("page"),
        "feature": feature,
        "task": task,
        "purpose": route.get("purpose", ""),
        "thinking_steps": route.get("thinking_steps", []),
        "schools": school_cards,
        "missing_capabilities": missing,
        "required_outputs": route.get("required_outputs", []),
        "next_actions": route.get("next_actions", []),
        "safety": data.get("global_rules", []),
        "related_routes": route.get("related_routes", []),
        "provenance": "tia_platform_knowledge_registry",
    }


def list_routes(registry: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return a compact, stable route catalogue for a UI or audit page."""
    data = registry if isinstance(registry, dict) else load_registry()
    return [
        {"id": key, "page": value.get("page"), "features": value.get("features", []),
         "purpose": value.get("purpose", "")}
        for key, value in data.get("routes", {}).items()
    ]
