from types import SimpleNamespace

from modules.tia_unified_market_risk import compose_market_risk_context


def test_composition_keeps_components_separate_and_never_scores_options_direction():
    flow = SimpleNamespace(asset="BTC", asset_class="crypto",
                           directional_read="BUY_PRESSURE_CONSENSUS",
                           execution_risk_status="REVIEW_REQUIRED")
    options = SimpleNamespace(asset="BTC", asset_class="crypto",
                              status="AVAILABLE_WITH_LIMITATIONS",
                              metrics={"put_call_oi_ratio": 1.2, "dvol_latest": 65})
    result = compose_market_risk_context(flow, options)
    assert result.synthesis_status == "REVIEW_REQUIRED"
    assert result.policy_effect == "NONE_CONTEXT_ONLY"
    assert any("not a directional confirmation" in item for item in result.observations)
    assert result.flow_context is flow and result.options_context is options


def test_options_cannot_fill_missing_orderflow_direction():
    flow = SimpleNamespace(asset="ETH", asset_class="crypto",
                           directional_read="INSUFFICIENT_DIRECTIONAL_EVIDENCE",
                           execution_risk_status="UNAVAILABLE")
    options = SimpleNamespace(asset="ETH", asset_class="crypto",
                               status="AVAILABLE_WITH_LIMITATIONS",
                               metrics={"put_call_oi_ratio": 0.8})
    result = compose_market_risk_context(flow, options)
    assert any("cannot fill" in item for item in result.observations)
    assert result.policy_effect == "NONE_CONTEXT_ONLY"


def test_no_options_data_is_not_a_zero_or_neutral_vote():
    flow = SimpleNamespace(asset="XRP", asset_class="crypto",
                           directional_read="MIXED_FLOW",
                           execution_risk_status="CONTEXT_ONLY")
    options = SimpleNamespace(asset="XRP", asset_class="crypto",
                               status="UNSUPPORTED_ASSET", metrics={})
    result = compose_market_risk_context(flow, options)
    assert any("absence is not" in item for item in result.observations)
