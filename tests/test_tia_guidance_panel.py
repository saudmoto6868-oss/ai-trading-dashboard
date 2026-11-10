from modules.tia_guidance_panel import build_guidance_view


def test_workspace_gann_view_exposes_reasoning_and_provenance():
    view = build_guidance_view("Workspace", "Gann", task="review anchor")
    assert view["status"] == "guidance_ready"
    assert view["route_id"] == "workspace_gann"
    assert any("anchor" in step.lower() for step in view["reasoning"])
    assert view["provenance"] == "tia_platform_knowledge_registry"


def test_footprint_view_explains_missing_classified_trades():
    view = build_guidance_view(
        "Workspace", "footprint", available_data={"classified_trades": False}
    )
    assert view["status"] == "ready_with_gates"
    assert any(
        item["capability"] == "classified_trades"
        for item in view["missing_capabilities"]
    )
    assert "limited" in view["notice"].lower()


def test_unknown_feature_returns_safe_unmapped_view():
    view = build_guidance_view("Workspace", "feature-that-does-not-exist")
    assert view["status"] == "unmapped"
    assert view["route_id"] is None
    assert view["schools"] == []
    assert view["next_actions"] == ["request registry route"]
