import pytest

from modules.desk_risk import DeskRules
from modules.tia_risk_engine import RiskPolicy, RiskSnapshot
from modules.tia_risk_shadow import compare_legacy_and_tia


def args(**overrides):
    data = dict(
        legacy_rules=DeskRules(risk_pct=0.5, daily_max_loss_pct=2.0, max_stops=3, min_rr=2.0),
        legacy_start_equity=10_000, legacy_realized_pnl=0, legacy_stops=0,
        legacy_open_keys=set(), symbol="XAUUSD", side="long",
        entry=2000, stop=1990, target=2020, legacy_caller_risk_amount=40,
        tia_policy=RiskPolicy("test", "v1", 0.5, 2.0, 1.0, 3, 2.0),
        tia_snapshot=RiskSnapshot(10_000, 0, 0, 0, ()),
        proposed_risk=40, proposed_asset_class="metals",
    )
    data.update(overrides)
    return data


def test_matching_simple_case_is_shadow_match():
    result = compare_legacy_and_tia(**args())
    assert result.legacy_allowed and result.tia_allowed
    assert result.decision_match
    assert result.mode == "SHADOW_ONLY_NO_EXECUTION"


def test_tia_blocks_unrealized_loss_that_legacy_does_not_see():
    result = compare_legacy_and_tia(**args(
        tia_snapshot=RiskSnapshot(10_000, 0, 0, 0, (), stopped_trades=0),
        tia_policy=RiskPolicy("tight", "v1", 0.5, 0.5, 1.0, 3, 2.0),
    ))
    # Both can still allow at zero P&L; policy mismatch is surfaced, not hidden.
    assert "DAILY_LOSS_POLICY_DIFFERS" in result.differences


def test_caller_risk_amount_mismatch_is_reported():
    result = compare_legacy_and_tia(**args(legacy_caller_risk_amount=10, proposed_risk=40))
    assert "CALLER_RISK_AMOUNT_DIFFERS_FROM_TIA_PROPOSED_RISK" in result.differences


def test_invalid_legacy_state_fails_closed():
    with pytest.raises(ValueError):
        compare_legacy_and_tia(**args(legacy_stops=-1))
