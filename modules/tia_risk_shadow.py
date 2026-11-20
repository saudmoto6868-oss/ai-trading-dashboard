"""Shadow-only comparison between legacy Desk risk and the TIA contract.

This adapter does not replace the Desk, persist state, or authorize orders.
Callers must supply both policy objects and an already-built TIA snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.desk_risk import DeskDay, DeskRules
from modules.risk_policy import risk_pct_for_setup
from modules.tia_risk_engine import RiskPolicy, RiskSnapshot, assess_new_trade


@dataclass(frozen=True)
class RiskShadowComparison:
    legacy_allowed: bool
    tia_allowed: bool
    decision_match: bool
    legacy_reasons: tuple[str, ...]
    tia_reasons: tuple[str, ...]
    legacy_risk_pct: float
    tia_policy_id: str
    tia_policy_version: str
    differences: tuple[str, ...]
    mode: str = "SHADOW_ONLY_NO_EXECUTION"


def compare_legacy_and_tia(
    *,
    legacy_rules: DeskRules,
    legacy_start_equity: float,
    legacy_realized_pnl: float,
    legacy_stops: int,
    legacy_open_keys: set[tuple[str, str]],
    symbol: str,
    side: str,
    entry: float,
    stop: float,
    target: float,
    legacy_caller_risk_amount: float,
    tia_policy: RiskPolicy,
    tia_snapshot: RiskSnapshot,
    proposed_risk: float,
    proposed_asset_class: str,
) -> RiskShadowComparison:
    """Evaluate the same proposed trade under both explicitly supplied models.

    Legacy model sees realized P&L and legacy risk amount. TIA sees its complete
    supplied snapshot and separately calculated proposed risk. This is a
    diagnostic comparison, not an apples-to-apples guarantee.
    """
    if legacy_start_equity <= 0:
        raise ValueError("legacy_start_equity must be positive")
    if legacy_stops < 0:
        raise ValueError("legacy_stops must be non-negative")
    if legacy_caller_risk_amount < 0:
        raise ValueError("legacy_caller_risk_amount must be non-negative")

    legacy = DeskDay(
        start_equity=legacy_start_equity,
        rules=legacy_rules,
        realized=legacy_realized_pnl,
        stops=legacy_stops,
        open_keys={(str(sym).upper(), str(pos_side).lower()) for sym, pos_side in legacy_open_keys},
    )
    old_allowed, old_reasons = legacy.check(
        symbol=symbol, side=side, entry=entry, stop=stop, target=target,
        risk_amount=legacy_caller_risk_amount,
    )
    new = assess_new_trade(
        policy=tia_policy, snapshot=tia_snapshot, symbol=symbol, side=side,
        entry=entry, stop=stop, target=target, proposed_risk=proposed_risk,
        proposed_asset_class=proposed_asset_class,
    )
    # legacy has no fixed risk_pct since the automatic policy; check() without a grade uses the base tier
    legacy_risk_pct = risk_pct_for_setup()
    differences = []
    if old_allowed != new.allowed:
        differences.append("ALLOW_BLOCK_DISAGREEMENT")
    if abs(legacy_risk_pct - tia_policy.risk_per_trade_pct) > 1e-12:
        differences.append("PER_TRADE_POLICY_DIFFERS")
    if abs(legacy_rules.daily_max_loss_pct - tia_policy.daily_loss_limit_pct) > 1e-12:
        differences.append("DAILY_LOSS_POLICY_DIFFERS")
    if legacy_rules.max_stops != tia_policy.max_stops:
        differences.append("STOP_COUNT_POLICY_DIFFERS")
    if abs(legacy_rules.min_rr - tia_policy.min_reward_risk) > 1e-12:
        differences.append("MIN_REWARD_RISK_POLICY_DIFFERS")
    if tia_snapshot.realized_pnl != legacy_realized_pnl:
        differences.append("REALIZED_PNL_INPUT_DIFFERS")
    tia_unrealized = sum(position.unrealized_pnl for position in tia_snapshot.positions)
    if tia_unrealized != 0 or tia_snapshot.fees_paid != 0 or tia_snapshot.funding_paid != 0:
        differences.append("TIA_INCLUDES_OPEN_PNL_OR_COSTS_NOT_IN_LEGACY")
    if tia_snapshot.positions:
        differences.append("TIA_INCLUDES_OPEN_POSITION_STOP_RISK_AND_SYMBOL_GUARDS")
    if abs(legacy_caller_risk_amount - proposed_risk) > 1e-9:
        differences.append("CALLER_RISK_AMOUNT_DIFFERS_FROM_TIA_PROPOSED_RISK")

    return RiskShadowComparison(
        legacy_allowed=old_allowed, tia_allowed=new.allowed,
        decision_match=old_allowed == new.allowed,
        legacy_reasons=tuple(old_reasons), tia_reasons=new.reasons,
        legacy_risk_pct=legacy_risk_pct,
        tia_policy_id=tia_policy.policy_id, tia_policy_version=tia_policy.version,
        differences=tuple(differences),
    )
