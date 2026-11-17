import pytest

from modules.desk_risk import DeskRules
from modules.tia_risk_engine import InstrumentSpec, Position, RiskPolicy, RiskSnapshot
from modules.tia_risk_shadow import compare_legacy_and_tia


def args(**overrides):
    data = dict(
        legacy_rules=DeskRules(daily_max_loss_pct=2.0, max_stops=3, min_rr=2.0),
        legacy_start_equity=10_000, legacy_realized_pnl=0, legacy_stops=0,
        legacy_open_keys=set(), symbol="XAUUSD", side="long",
        entry=2000, stop=1990, target=2020, legacy_caller_risk_amount=20,
        tia_policy=RiskPolicy("test", "v1", 0.25, 2.0, 1.0, 3, 2.0),
        tia_snapshot=RiskSnapshot(10_000, 0, 0, 0, ()),
        proposed_risk=20, proposed_asset_class="metals",
    )
    data.update(overrides)
    return data


def test_matching_simple_case_is_shadow_match():
    result = compare_legacy_and_tia(**args())
    assert result.legacy_allowed and result.tia_allowed
    assert result.decision_match
    assert "PER_TRADE_POLICY_DIFFERS" not in result.differences
    assert result.mode == "SHADOW_ONLY_NO_EXECUTION"


def test_tia_blocks_unrealized_loss_that_legacy_does_not_see():
    spec = InstrumentSpec("BTC", "crypto", "USD", 1, 0.001, 1)
    position = Position("p1", "BTC", "crypto", "long", 10, 100, 90, 70, spec)
    result = compare_legacy_and_tia(**args(
        symbol="ETH",
        tia_policy=RiskPolicy("test", "v1", 0.25, 2.0, 20.0, 3, 2.0),
        tia_snapshot=RiskSnapshot(10_000, 0, 0, 0, (position,)),
    ))
    assert result.legacy_allowed
    assert not result.tia_allowed
    assert "ALLOW_BLOCK_DISAGREEMENT" in result.differences
    assert "TIA_INCLUDES_OPEN_PNL_OR_COSTS_NOT_IN_LEGACY" in result.differences
    assert "daily net loss limit reached" in result.tia_reasons


def test_caller_risk_amount_mismatch_is_reported():
    result = compare_legacy_and_tia(**args(legacy_caller_risk_amount=10, proposed_risk=20))
    assert "CALLER_RISK_AMOUNT_DIFFERS_FROM_TIA_PROPOSED_RISK" in result.differences


def test_invalid_legacy_state_fails_closed():
    with pytest.raises(ValueError):
        compare_legacy_and_tia(**args(legacy_stops=-1))


if __name__ == "__main__":   # CI runs plain `python3 tests/x.py`
    raise SystemExit(pytest.main([__file__, "-q"]))
