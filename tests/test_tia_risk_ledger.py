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
    assert sized.quantity == pytest.approx(4.92)
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
    now = datetime(2026, 11, 9, 21, 30, tzinfo=timezone.utc)
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



def test_projection_replays_open_mark_close_and_explicit_stop_classification(tmp_path):
    ledger = RiskLedger(str(tmp_path / "projection.sqlite"))
    now = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
    sid = ledger.open_session(account_id="acct", now=now, timezone_name="UTC",
                              start_equity=5000, policy_id="p", policy_version="1")
    spec_payload = {
        "symbol": "XAUUSD", "asset_class": "metals", "quote_currency": "USD",
        "tick_size": 0.01, "quantity_step": 0.01, "point_value": 1.0,
        "contract_multiplier": 1.0, "fee_per_unit_round_trip": 0.1,
        "funding_reserve_per_unit": 0.05, "account_ccy_per_quote_ccy": 1.0
    }
    opened = {"position_id": "pos-1", "symbol": "XAUUSD", "asset_class": "metals",
              "side": "long", "quantity": 1.0, "entry": 2000.0, "stop": 1990.0,
              "mark": 2000.0, "spec": spec_payload}
    ledger.append_event(session_id=sid, event_id="open-1", event_type="position_open",
                        payload=opened, created_at=now)
    ledger.append_event(session_id=sid, event_id="mark-1", event_type="position_mark",
                        payload={"position_id": "pos-1", "mark": 1998.0}, created_at=now + timedelta(seconds=1))
    ledger.append_event(session_id=sid, event_id="close-1", event_type="position_close",
                        payload={"position_id": "pos-1", "realized_pnl": -2.0,
                                 "fees_paid": 0.1, "funding_paid": 0.0, "stopped": False},
                        created_at=now + timedelta(seconds=2))
    state = ledger.project_session(sid)
    assert state["open_position_count"] == 0
    assert state["realized_pnl"] == -2.0
    assert state["fees_paid"] == 0.1
    assert state["stopped_trades"] == 0


def test_projection_requires_explicit_stop_classification(tmp_path):
    ledger = RiskLedger(str(tmp_path / "projection-stop.sqlite"))
    now = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
    sid = ledger.open_session(account_id="acct", now=now, timezone_name="UTC",
                              start_equity=5000, policy_id="p", policy_version="1")
    spec_payload = {"symbol": "XAUUSD", "asset_class": "metals", "quote_currency": "USD",
                    "tick_size": 0.01, "quantity_step": 0.01, "point_value": 1.0}
    ledger.append_event(session_id=sid, event_id="o", event_type="position_open",
        payload={"position_id":"p1","symbol":"XAUUSD","asset_class":"metals","side":"long",
                 "quantity":1,"entry":2000,"stop":1990,"mark":2000,"spec":spec_payload},
        created_at=now)
    ledger.append_event(session_id=sid, event_id="c", event_type="position_close",
        payload={"position_id":"p1","realized_pnl":-10}, created_at=now + timedelta(seconds=1))
    with pytest.raises(ValueError, match="explicit boolean stopped"):
        ledger.project_session(sid)


def test_projection_preserves_append_order_when_event_timestamps_tie(tmp_path):
    ledger = RiskLedger(str(tmp_path / "same-time.sqlite"))
    now = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
    sid = ledger.open_session(account_id="acct", now=now, timezone_name="UTC",
                              start_equity=5000, policy_id="p", policy_version="1")
    spec_payload = {"symbol":"XAUUSD","asset_class":"metals","quote_currency":"USD",
                    "tick_size":0.01,"quantity_step":0.01,"point_value":1.0}
    ledger.append_event(session_id=sid,event_id="z-open",event_type="position_open",
        payload={"position_id":"p1","symbol":"XAUUSD","asset_class":"metals","side":"long",
                 "quantity":1,"entry":2000,"stop":1990,"mark":2000,"spec":spec_payload},created_at=now)
    ledger.append_event(session_id=sid,event_id="a-mark",event_type="position_mark",
        payload={"position_id":"p1","mark":2001},created_at=now)
    ledger.append_event(session_id=sid,event_id="m-close",event_type="position_close",
        payload={"position_id":"p1","realized_pnl":1,"fees_paid":0,"funding_paid":0,"stopped":False},created_at=now)
    assert [e["event_id"] for e in ledger.events(sid)] == ["z-open","a-mark","m-close"]
    assert ledger.project_session(sid)["open_position_count"] == 0


def test_cashflows_are_audited_but_excluded_from_trading_pnl(tmp_path):
    ledger = RiskLedger(str(tmp_path / "cashflows.sqlite"))
    now = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
    sid = ledger.open_session(account_id="acct", now=now, timezone_name="UTC",
                              start_equity=5000, policy_id="p", policy_version="1")
    ledger.append_event(session_id=sid, event_id="deposit-1", event_type="account_cashflow",
        payload={"flow_type":"deposit","amount":1000,"account_currency":"USD",
                 "source":"broker-statement","external_reference":"dep-001"}, created_at=now)
    ledger.append_event(session_id=sid, event_id="withdrawal-1", event_type="account_cashflow",
        payload={"flow_type":"withdrawal","amount":250,"account_currency":"USD",
                 "source":"broker-statement","external_reference":"wd-001"}, created_at=now)
    state = ledger.project_session(sid)
    assert state["start_equity"] == 5000
    assert state["realized_pnl"] == 0
    assert state["deposits_account_ccy"] == 1000
    assert state["withdrawals_account_ccy"] == 250
    assert state["net_cashflow_account_ccy"] == 750
    assert state["cashflow_count"] == 2


@pytest.mark.parametrize("payload", [
    {"flow_type":"deposit","amount":0,"account_currency":"USD","source":"broker","external_reference":"x"},
    {"flow_type":"transfer","amount":10,"account_currency":"USD","source":"broker","external_reference":"x"},
    {"flow_type":"deposit","amount":10,"account_currency":"USD","source":"","external_reference":"x"},
    {"flow_type":"withdrawal","amount":10,"account_currency":"USD","source":"broker","external_reference":""},
])
def test_cashflow_requires_valid_auditable_fields(tmp_path, payload):
    ledger = RiskLedger(str(tmp_path / "bad-cashflow.sqlite"))
    now = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
    sid = ledger.open_session(account_id="acct", now=now, timezone_name="UTC",
                              start_equity=5000, policy_id="p", policy_version="1")
    ledger.append_event(session_id=sid, event_id="cashflow", event_type="account_cashflow",
                        payload=payload, created_at=now)
    with pytest.raises(ValueError):
        ledger.project_session(sid)
