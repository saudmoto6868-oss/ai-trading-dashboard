"""Presentation-neutral adapter for shared platform knowledge guidance.

This TIA-owned module shapes router results for page consumers. It deliberately
contains no Streamlit rendering, market-data fetching, signal generation or
execution. Page owners can render the returned model in their own UI.
"""
from __future__ import annotations

from typing import Any

from modules.tia_knowledge_router import resolve_guidance


def build_guidance_view(
    page: str,
    feature: str | None = None,
    *,
    task: str | None = None,
    available_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable, UI-neutral guidance panel model for a page/feature."""
    result = resolve_guidance(
        page,
        feature,
        task=task,
        available_data=available_data,
    )
    status = result.get("status", "unmapped")
    if status == "unmapped":
        return {
            "status": "unmapped",
            "title": "Guidance not mapped",
            "summary": result.get(
                "message",
                "No registered guidance route. Keep the feature functional and request a registry addition.",
            ),
            "route_id": None,
            "schools": [],
            "reasoning": [],
            "missing_capabilities": [],
            "required_outputs": [],
            "next_actions": ["request registry route"],
            "safety": result.get("safety", []),
            "provenance": result.get("provenance", "tia_platform_knowledge_registry"),
        }

    missing = result.get("missing_capabilities", [])
    return {
        "status": status,
        "title": "Guidance and evidence gates",
        "summary": result.get("purpose", ""),
        "route_id": result.get("route_id"),
        "page": result.get("page", page),
        "feature": result.get("feature", feature),
        "task": result.get("task", task),
        "schools": result.get("schools", []),
        "reasoning": result.get("thinking_steps", []),
        "missing_capabilities": missing,
        "required_outputs": result.get("required_outputs", []),
        "next_actions": result.get("next_actions", []),
        "related_routes": result.get("related_routes", []),
        "safety": result.get("safety", []),
        "provenance": result.get("provenance", "tia_platform_knowledge_registry"),
        "notice": (
            "Some specialist checks are limited because required data capabilities are missing."
            if missing else "Guidance is available; validate the evidence and risk before acting."
        ),
    }
