from modules.tia_visual_knowledge import load_knowledge, module_status, summary


def test_catalog_loads_four_reference_modules():
    data = load_knowledge()
    assert len(data["modules"]) == 4
    assert {m["id"] for m in data["modules"]} == {
        "price_action_structure", "candlestick_patterns", "volume_profile", "order_flow_footprint"
    }
    assert summary(data)["pattern_count"] > 20


def test_volume_profile_requires_true_volume_at_price():
    data = load_knowledge()
    status = module_status(data, "volume_profile")
    assert status["status"] == "blocked_missing_data"
    assert status["available"] is False


def test_footprint_requires_classified_trade_prints():
    data = load_knowledge()
    status = module_status(data, "order_flow_footprint")
    assert status["status"] == "blocked_missing_data"
    assert status["available"] is False


def test_candles_are_reference_only_without_detector():
    data = load_knowledge()
    status = module_status(data, "candlestick_patterns")
    assert status["status"] == "reference_only"
    assert status["available"] is False


def test_missing_file_returns_safe_empty_catalog(tmp_path):
    data = load_knowledge(tmp_path / "missing.json")
    assert data["modules"] == []
    assert data["status"] == "unavailable"
