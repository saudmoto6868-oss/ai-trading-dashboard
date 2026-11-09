"""Deterministic tests for TIA Risk Engine v1; run with python -m pytest."""
import math
import pytest

from modules.tia_risk_engine import (
    InstrumentSpec, Position, RiskPolicy, RiskSnapshot, assess_new_trade,
)


@pytest.fixture
def policy():
    return RiskPolicy("owner-approved-placeholder", "v1", 0.5, 2.0, 1.0, 3, 2.0)


@pytest.fixture
def spec():
    return InstrumentSpec("XAUUSD", "metals", "USD", 0.01, 0.01, 1.0,
                          fee_per_unit_round_trip=0.1, funding_reserve_per_unit=0.05)


def test_requires_explicit_policy():
    with pytest.raises(TypeError):
        RiskPolicy()


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_rejects_non_finite_equity(bad):
    with pytest.raises(ValueError):
        RiskSnapshot(bad, 0, 0, 0, ())


def test_open_stop_risk_and_unrealized_loss_reduce_budget(policy, spec):
    p = Position("p1", "XAUUSD", "metals", "long", 10, 2000, 1990, 1995, spec)
    snap = RiskSnapshot(10000, -50, 5, 2, (p,))
    a = assess_new_trade(policy=policy, snapshot=snap, symbol="EURUSD", side="long",
                         entry=1.1, stop=1.09, target=1.12, proposed_risk=20,
                         proposed_asset_class="fx")
    assert a.open_stop_risk == pytest.approx(101.5)
    assert a.unrealized_pnl == pytest.approx(-50)
    assert a.daily_net_pnl == pytest.approx(-107)
    assert a.remaining_daily_loss_budget == pytest.approx(93)


def test_opposite_side_duplicate_symbol_blocked(policy, spec):
    p = Position("p1", "XAUUSD", "metals", "long", 1, 2000, 1990, 2001, spec)
    snap = RiskSnapshot(10000, 0, 0, 0, (p,))
    a = assess_new_trade(policy=policy, snapshot=snap, symbol="xauusd", side="short",
                         entry=2000, stop=2010, target=1980, proposed_risk=20,
                         proposed_asset_class="metals")
    assert not a.allowed
    assert any("hedge is disabled" in x for x in a.reasons)


def test_invalid_stop_geometry_and_nan_risk_rejected(policy):
    snap = RiskSnapshot(10000, 0, 0, 0, ())
    with pytest.raises(ValueError):
        assess_new_trade(policy=policy, snapshot=snap, symbol="X", side="long",
                         entry=100, stop=101, target=103, proposed_risk=10,
                         proposed_asset_class="fx")
    with pytest.raises(ValueError):
        assess_new_trade(policy=policy, snapshot=snap, symbol="X", side="long",
                         entry=100, stop=99, target=103, proposed_risk=math.nan,
                         proposed_asset_class="fx")


def test_open_risk_portfolio_cap_blocks(policy, spec):
    p = Position("p1", "XAUUSD", "metals", "long", 100, 2000, 1990, 2000, spec)
    snap = RiskSnapshot(10000, 0, 0, 0, (p,))
    a = assess_new_trade(policy=policy, snapshot=snap, symbol="EURUSD", side="long",
                         entry=1.1, stop=1.09, target=1.13, proposed_risk=20,
                         proposed_asset_class="fx")
    assert not a.allowed
    assert any("aggregate open stop risk" in x for x in a.reasons)


def test_losing_manual_exit_not_counted_as_stop(policy):
    snap = RiskSnapshot(10000, -25, 0, 0, (), stopped_trades=0)
    a = assess_new_trade(policy=policy, snapshot=snap, symbol="BTC", side="long",
                         entry=100, stop=99, target=103, proposed_risk=25,
                         proposed_asset_class="crypto")
    assert a.allowed
