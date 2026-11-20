import json

from modules.tia_knowledge_router import load_registry, list_routes, resolve_guidance


def test_registry_has_all_platform_surfaces():
    routes = list_routes()
    pages = {r["page"] for r in routes}
    assert {"Workspace", "Radar", "Spot", "TIA", "Trading Lab", "Learn and AI", "Order Flow Desk"} <= pages
    assert len(routes) >= 14


def test_workspace_footprint_blocks_without_classified_trades():
    result = resolve_guidance("Workspace", "footprint", available_data={"classified_trades": False})
    assert result["status"] == "ready_with_gates"
    assert any(x["capability"] == "classified_trades" for x in result["missing_capabilities"])


def test_radar_auction_blocks_without_volume_at_price():
    result = resolve_guidance("Radar", "Volume Profile", available_data={"volume_at_price": False})
    assert result["status"] == "ready_with_gates"
    assert any(x["capability"] == "volume_at_price" for x in result["missing_capabilities"])


def test_gann_route_contains_anchor_and_calibration_steps():
    result = resolve_guidance("Workspace", "Gann")
    assert result["route_id"] == "workspace_gann"
    assert any("anchor" in step.lower() for step in result["thinking_steps"])
    assert any("calibration" in step.lower() for step in result["thinking_steps"])


def test_unknown_route_fails_closed():
    result = resolve_guidance("Unknown Page", "Unknown Feature")
    assert result["status"] == "unmapped"
    assert result["schools"] == []


def test_missing_registry_is_safe(tmp_path):
    registry = load_registry(tmp_path / "missing.json")
    assert registry == {"routes": {}, "schools": {}}
