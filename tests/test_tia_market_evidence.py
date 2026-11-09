from datetime import datetime, timezone

import pytest

from modules import tia_market_evidence as bridge


def test_catalog_distinguishes_public_market_from_account_data():
    ids = {item.source_id for item in bridge.SOURCE_CATALOG}
    assert {"okx_public_market", "hyperliquid_xyz", "deribit_options",
            "cboe_delayed_options", "finnhub_news", "dashboard_workspace"} <= ids
    caps = bridge.account_data_capabilities()
    assert caps["balance"].startswith("UNAVAILABLE")
    assert caps["broker_fills"].startswith("UNAVAILABLE")
    assert caps["market_prices_and_orderflow"].startswith("AVAILABLE")


def test_collect_existing_orderflow_preserves_feed_health(monkeypatch):
    monkeypatch.setattr(
        "modules.spot_flow.fetch",
        lambda asset, cls: {
            "src": "OKX",
            "tape": {"ok": True, "n": 20},
            "book": {"ok": False, "why": "rate limited"},
            "funding": {"ok": True, "value": 0.01},
        },
    )
    snap = bridge.collect_existing_orderflow("btc", "crypto")
    assert snap.asset == "BTC"
    assert snap.collection_source == "modules.spot_flow.fetch"
    assert snap.provider_event_time is None
    assert snap.freshness == "UNVERIFIED_PROVIDER_TIMESTAMP"
    health = {item.key: item for item in snap.health}
    assert health["tape"].available is True
    assert health["book"].available is False
    assert health["book"].reason == "rate limited"
    assert any("not broker account state" in item for item in snap.limitations)


def test_metals_snapshot_discloses_perpetual_market_limitation(monkeypatch):
    monkeypatch.setattr("modules.spot_flow.fetch", lambda asset, cls: {
        "src": "Hyperliquid (perp)", "tape": {"ok": False, "why": "no prints"}
    })
    snap = bridge.collect_existing_orderflow("GOLD", "metals")
    assert any("perpetual contracts" in item for item in snap.limitations)


@pytest.mark.parametrize("asset,cls", [("", "crypto"), ("BTC", "forex"), ("XAUUSD", "stocks")])
def test_invalid_market_request_rejected(asset, cls):
    with pytest.raises(ValueError):
        bridge.collect_existing_orderflow(asset, cls)
