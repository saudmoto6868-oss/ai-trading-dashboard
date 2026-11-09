from datetime import datetime, timezone

import pytest

from modules.tia_market_evidence import MarketEvidenceSnapshot
from modules.tia_market_risk_context import (
    MarketRiskThresholds,
    build_market_risk_context,
)


def snap(evidence, freshness="UNVERIFIED_PROVIDER_TIMESTAMP"):
    return MarketEvidenceSnapshot(
        asset="BTC", asset_class="crypto",
        collected_at=datetime(2026, 11, 9, tzinfo=timezone.utc),
        collection_source="modules.spot_flow.fetch", provider_event_time=None,
        freshness=freshness, evidence={"src": "OKX", **evidence},
        health=(), limitations=("market data only",),
    )


def test_consensus_and_crowding_are_context_not_position_sizing():
    context = build_market_risk_context("BTC", "crypto", snapshot=snap({
        "tape": {"ok": True, "buy_share": 0.61},
        "taker": {"ok": True, "slope": 3.0},
        "book": {"ok": True, "imbalance": 0.22, "bid_usd": 1000, "ask_usd": 700},
        "deriv": {"ok": True, "funding": 0.05, "ls_ratio": 2.3, "oi_chg_7d": 12.0},
    }))
    assert context.directional_read == "BUY_PRESSURE_CONSENSUS"
    codes = {flag.code for flag in context.flags}
    assert {"ORDER_BOOK_IMBALANCE", "POSITIVE_FUNDING_CROWDING",
            "LONG_ACCOUNT_CROWDING", "OPEN_INTEREST_CONTEXT",
            "PROVIDER_TIMESTAMP_UNVERIFIED"} <= codes
    assert context.sizing_impact == "NONE_MARKET_CONTEXT_ONLY"
    assert context.execution_risk_status == "REVIEW_REQUIRED"


def test_mixed_flow_is_not_forced_into_buy_or_sell():
    context = build_market_risk_context("BTC", "crypto", snapshot=snap({
        "tape": {"ok": True, "buy_share": 0.62},
        "taker": {"ok": True, "slope": -4.0},
        "book": {"ok": True, "imbalance": 0.01},
    }))
    assert context.directional_read == "MIXED_FLOW"


def test_unavailable_feeds_are_not_zero_values():
    context = build_market_risk_context("BTC", "crypto", snapshot=snap({
        "tape": {"ok": False, "why": "rate limited"},
        "book": {"ok": False, "why": "empty book"},
        "deriv": {"ok": False, "why": "timeout"},
    }))
    assert context.directional_read == "INSUFFICIENT_DIRECTIONAL_EVIDENCE"
    assert set(context.unavailable_components) == {"tape", "taker", "book", "deriv", "premium", "vp"}
    assert "ORDER_FLOW_UNAVAILABLE" in {flag.code for flag in context.flags}
    assert context.sizing_impact == "NONE_MARKET_CONTEXT_ONLY"


def test_thresholds_reject_invalid_values():
    for value in (float("nan"), float("inf"), True, "not-a-number"):
        with pytest.raises(ValueError):
            MarketRiskThresholds(book_imbalance_abs=value)
    with pytest.raises(ValueError):
        MarketRiskThresholds(thin_book_usd=-1)


def test_unverified_freshness_always_creates_caution_flag():
    context = build_market_risk_context("BTC", "crypto", snapshot=snap({
        "tape": {"ok": True, "buy_share": 0.5},
    }))
    assert "PROVIDER_TIMESTAMP_UNVERIFIED" in {flag.code for flag in context.flags}


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf"), True, "broken"])
def test_malformed_directional_metrics_are_ignored_not_defaulted_to_zero(bad):
    context = build_market_risk_context("BTC", "crypto", snapshot=snap({
        "tape": {"ok": True, "buy_share": bad},
        "taker": {"ok": True, "slope": 2.0},
        "book": {"ok": True, "imbalance": bad, "bid_usd": bad, "ask_usd": 10},
        "deriv": {"ok": True, "funding": bad, "ls_ratio": bad, "oi_chg_7d": bad},
    }))
    assert context.directional_read == "BUY_PRESSURE_CONSENSUS"
    assert "INVALID_PROVIDER_METRIC" in {flag.code for flag in context.flags}
    assert "ORDER_BOOK_IMBALANCE" not in {flag.code for flag in context.flags}
    assert context.sizing_impact == "NONE_MARKET_CONTEXT_ONLY"


def test_empty_or_nonfinite_book_depth_does_not_create_false_thin_book_flag():
    context = build_market_risk_context("BTC", "crypto",
        thresholds=MarketRiskThresholds(thin_book_usd=100),
        snapshot=snap({"book": {"ok": True, "imbalance": 0.0,
                                "bid_usd": float("nan"), "ask_usd": 1}}))
    codes = {flag.code for flag in context.flags}
    assert "THIN_DISPLAYED_BOOK" not in codes
    assert "INVALID_PROVIDER_METRIC" in codes
