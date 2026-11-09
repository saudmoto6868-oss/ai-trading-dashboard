from datetime import datetime, timezone

from modules.tia_integrations import cmc_evidence, fred_evidence


def test_fred_adapter_preserves_observation_date_and_skips_missing():
    rows = [
        {"label": "US 10Y yield %", "value": 4.25, "date": "2026-11-06"},
        {"label": "Fed funds %", "value": None, "date": "2026-11-06", "note": "no data"},
        {"label": "unknown", "value": 1, "date": "2026-11-06"},
    ]
    evidence = fred_evidence(rows)
    assert len(evidence) == 1
    assert evidence[0].metric_id == "macro.us_10y_yield"
    assert evidence[0].observed_at == "2026-11-06T00:00:00+00:00"
    assert "observation date" in evidence[0].notes


def test_cmc_adapter_uses_explicit_fetch_time_and_units():
    fetched = datetime(2026, 11, 9, 1, 0, tzinfo=timezone.utc)
    evidence = cmc_evidence(
        {"ok": True, "global": {"mcap": 1_000_000, "btc_dom": 58.2}},
        fetched_at=fetched,
    )
    by_id = {item.metric_id: item for item in evidence}
    assert by_id["crypto.global_market_cap_usd"].unit == "USD"
    assert by_id["crypto.global_market_cap_usd"].observed_at == fetched.isoformat()
    assert by_id["crypto.btc_dominance"].unit == "%"
    assert "crypto.global_volume_24h_usd" not in by_id


def test_cmc_adapter_rejects_failed_provider_payload_and_naive_clock():
    assert cmc_evidence({"ok": False, "err": "nokey"}) == []
    try:
        cmc_evidence({"ok": True, "global": {"mcap": 1}}, fetched_at=datetime(2026, 11, 9))
    except ValueError as exc:
        assert "timezone" in str(exc)
    else:
        raise AssertionError("naive fetch time must be rejected")
