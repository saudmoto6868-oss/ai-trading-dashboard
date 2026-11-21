import pytest
from datetime import datetime, timezone, timedelta

from modules.tia_risk_reconciliation import (
    BrokerPosition, BrokerPositionSnapshot, reconcile_positions,
)


@pytest.fixture
def now():
    return datetime(2026, 11, 9, 12, tzinfo=timezone.utc)


@pytest.fixture
def ledger():
    return {"account_id": "acct-1", "open_positions": [
        {"position_id": "p1", "symbol": "XAUUSD", "side": "long",
         "quantity": 0.5, "entry": 2000.0}
    ]}


def snapshot(now, positions=None, complete=True):
    return BrokerPositionSnapshot("acct-1", "broker-adapter-test", now,
                                  tuple([BrokerPosition("p1", "xauusd", "long", .5, 2000)] if positions is None else positions),
                                  complete)


def test_exact_snapshot_reconciles(now, ledger):
    result = reconcile_positions(ledger_state=ledger, broker=snapshot(now), now=now)
    assert result.reconciled
    assert result.matched_position_count == 1


def test_stale_or_incomplete_snapshot_fails_closed(now, ledger):
    stale = snapshot(now - timedelta(seconds=30))
    result = reconcile_positions(ledger_state=ledger, broker=stale, now=now, max_age_seconds=15)
    assert not result.reconciled
    assert any("stale" in reason for reason in result.reasons)
    incomplete = reconcile_positions(ledger_state=ledger, broker=snapshot(now, complete=False), now=now)
    assert not incomplete.reconciled


def test_broker_only_and_ledger_only_positions_are_reported(now, ledger):
    broker = snapshot(now, [BrokerPosition("p2", "BTCUSDT", "short", 1, 60000)])
    result = reconcile_positions(ledger_state=ledger, broker=broker, now=now)
    assert result.ledger_only_ids == ("p1",)
    assert result.broker_only_ids == ("p2",)
    assert not result.reconciled


def test_mismatched_quantity_and_account_fail_closed(now, ledger):
    broker = BrokerPositionSnapshot("other-account", "broker", now,
        (BrokerPosition("p1", "XAUUSD", "long", .6, 2000),), True)
    result = reconcile_positions(ledger_state=ledger, broker=broker, now=now)
    assert not result.reconciled
    assert result.mismatched_ids == ("p1",)
    assert any("account IDs" in reason for reason in result.reasons)


def test_reject_duplicate_broker_ids(now):
    with pytest.raises(ValueError, match="duplicate"):
        snapshot(now, [BrokerPosition("p1", "XAUUSD", "long", 1, 2000),
                      BrokerPosition("p1", "XAUUSD", "long", 1, 2000)])


def test_explicit_empty_broker_snapshot_is_not_replaced_by_fixture_position(now, ledger):
    result = reconcile_positions(ledger_state=ledger, broker=snapshot(now, []), now=now)
    assert result.broker_only_ids == ()
    assert result.ledger_only_ids == ("p1",)
    assert not result.reconciled


def test_snapshot_complete_must_be_boolean(now):
    with pytest.raises(ValueError, match="explicit boolean"):
        BrokerPositionSnapshot("acct", "broker", now, (), 1)


if __name__ == "__main__":   # CI runs plain `python3 tests/x.py`
    raise SystemExit(pytest.main([__file__, "-q"]))
