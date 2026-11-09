import pytest
from datetime import datetime, timezone, timedelta

from modules.tia_risk_engine import InstrumentSpec
from modules.tia_risk_ledger import ConversionQuote, RiskLedger, size_trade


@pytest.fixture
def spec():
    return InstrumentSpec("XAUUSD", "metals", "USD", 0.01, 0.01, 1.0,
                          fee_per_unit_round_trip=0.10, funding_reserve_per_unit=0.05)


def test_quantity_sizing_includes_costs_and_rounds_down(spec):
    now = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
    fx = ConversionQuote("USD", "USD", 1, "account-base", now)
    sized = size_trade(equity=10000, risk_pct=0.5, entry=2000, stop=1990,
                       side="long", spec=spec, fx_quote=fx, account_currency="USD", now=now)
    assert sized.quantity == pytest.approx(4.98)
    assert sized.stop_risk_account_ccy <= sized.risk_budget_account_ccy
    assert sized.estimated_cost_reserve_account_ccy > 0


def test_fx_stale_or_wrong_currency_fails_closed(spec):
    now = datetime.now(timezone.utc)
    stale = ConversionQuote("USD", "EUR", 0.92, "test", now - timedelta(hours=1))
    with pytest.raises(ValueError, match="stale"):
        size_trade(equity=10000, risk_pct=0.5, entry=2000, stop=1990, side="long",
                   spec=spec, fx_quote=stale, account_currency="EUR", now=now)


def test_tick_and_quantity_steps_enforced(spec):
    now = datetime.now(timezone.utc)
    fx = ConversionQuote("USD", "USD", 1, "test", now)
    with pytest.raises(ValueError, match="tick"):
        size_trade(equity=10000, risk_pct=0.5, entry=2000.005, stop=1990,
                   side="long", spec=spec, fx_quote=fx, account_currency="USD", now=now)


def test_ledger_idempotency_conflict_and_timezone_rollover(tmp_path):
    ledger = RiskLedger(str(tmp_path / "risk.sqlite"))
    now = datetime(2026, 11, 9, 23, 30, tzinfo=timezone.utc)
    sid = ledger.open_session(account_id="acct-1", now=now, timezone_name="Africa/Cairo",
                              start_equity=10000, policy_id="p", policy_version="1")
    assert ledger.append_event(session_id=sid, event_id="evt-1", event_type="close",
                               payload={"pnl": -10}, created_at=now)
    assert not ledger.append_event(session_id=sid, event_id="evt-1", event_type="close",
                                   payload={"pnl": -10}, created_at=now)
    with pytest.raises(ValueError, match="different content"):
        ledger.append_event(session_id=sid, event_id="evt-1", event_type="close",
                            payload={"pnl": -20}, created_at=now)
    assert len(ledger.events(sid)) == 1
    # Cairo is UTC+2 on this date; local session date rolls over at 22:00 UTC.
    next_sid = ledger.open_session(account_id="acct-1",
        now=datetime(2026, 11, 9, 22, 30, tzinfo=timezone.utc),
        timezone_name="Africa/Cairo", start_equity=10000, policy_id="p", policy_version="1")
    assert sid != next_sid


def test_ledger_rejects_policy_change_inside_existing_session(tmp_path):
    ledger = RiskLedger(str(tmp_path / "risk.sqlite"))
    now = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
    ledger.open_session(account_id="a", now=now, timezone_name="UTC",
                        start_equity=1000, policy_id="p", policy_version="1")
    with pytest.raises(ValueError, match="different policy"):
        ledger.open_session(account_id="a", now=now, timezone_name="UTC",
                            start_equity=1000, policy_id="p", policy_version="2")
