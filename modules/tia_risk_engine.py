"""TIA Risk Engine v1: deterministic, fail-closed risk calculations.

This module is a calculation/decision contract only. It does not persist state,
connect to brokers, or place orders. Callers must supply a versioned policy and
fresh, source-stamped marks/FX conversions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Literal


Side = Literal["long", "short"]


def _finite(name: str, value: float, *, positive: bool = False, non_negative: bool = False) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if positive and value <= 0:
        raise ValueError(f"{name} must be > 0")
    if non_negative and value < 0:
        raise ValueError(f"{name} must be >= 0")
    return value


@dataclass(frozen=True)
class RiskPolicy:
    policy_id: str
    version: str
    risk_per_trade_pct: float
    daily_loss_limit_pct: float
    max_open_risk_pct: float
    max_stops: int
    min_reward_risk: float = 2.0
    allow_hedged_sides: bool = False

    def __post_init__(self):
        if not self.policy_id.strip() or not self.version.strip():
            raise ValueError("policy_id and version are required")
        for name in ("risk_per_trade_pct", "daily_loss_limit_pct", "max_open_risk_pct", "min_reward_risk"):
            _finite(name, getattr(self, name), positive=True)
        if self.risk_per_trade_pct > self.daily_loss_limit_pct:
            raise ValueError("per-trade risk cannot exceed daily loss limit")
        if self.max_stops < 1:
            raise ValueError("max_stops must be >= 1")


@dataclass(frozen=True)
class InstrumentSpec:
    symbol: str
    asset_class: str
    quote_currency: str
    tick_size: float
    quantity_step: float
    point_value: float
    contract_multiplier: float = 1.0
    fee_per_unit_round_trip: float = 0.0
    funding_reserve_per_unit: float = 0.0
    account_ccy_per_quote_ccy: float = 1.0

    def __post_init__(self):
        if not self.symbol.strip() or not self.asset_class.strip() or not self.quote_currency.strip():
            raise ValueError("instrument identity and currencies are required")
        for name in ("tick_size", "quantity_step", "point_value", "contract_multiplier", "account_ccy_per_quote_ccy"):
            _finite(name, getattr(self, name), positive=True)
        for name in ("fee_per_unit_round_trip", "funding_reserve_per_unit"):
            _finite(name, getattr(self, name), non_negative=True)


@dataclass(frozen=True)
class Position:
    position_id: str
    symbol: str
    asset_class: str
    side: Side
    quantity: float
    entry: float
    stop: float
    mark: float
    spec: InstrumentSpec

    def __post_init__(self):
        if not self.position_id.strip():
            raise ValueError("position_id is required")
        if self.side not in ("long", "short"):
            raise ValueError("side must be long or short")
        _finite("quantity", self.quantity, positive=True)
        _finite("entry", self.entry, positive=True)
        _finite("stop", self.stop, positive=True)
        _finite("mark", self.mark, positive=True)
        if self.symbol.upper() != self.spec.symbol.upper():
            raise ValueError("position symbol does not match instrument spec")
        if self.side == "long" and self.stop >= self.entry:
            raise ValueError("long stop must be below entry")
        if self.side == "short" and self.stop <= self.entry:
            raise ValueError("short stop must be above entry")

    @property
    def stop_risk(self) -> float:
        distance = abs(self.entry - self.stop)
        gross = distance * self.spec.point_value * self.spec.contract_multiplier
        costs = self.spec.fee_per_unit_round_trip + self.spec.funding_reserve_per_unit
        return self.quantity * (gross + costs) * self.spec.account_ccy_per_quote_ccy

    @property
    def unrealized_pnl(self) -> float:
        move = self.mark - self.entry
        if self.side == "short":
            move = -move
        gross = move * self.spec.point_value * self.spec.contract_multiplier * self.quantity
        return gross * self.spec.account_ccy_per_quote_ccy


@dataclass(frozen=True)
class RiskSnapshot:
    start_equity: float
    realized_pnl: float
    fees_paid: float
    funding_paid: float
    positions: tuple[Position, ...]
    stopped_trades: int = 0

    def __post_init__(self):
        _finite("start_equity", self.start_equity, positive=True)
        for name in ("realized_pnl", "fees_paid", "funding_paid"):
            _finite(name, getattr(self, name))
        _finite("fees_paid", self.fees_paid, non_negative=True)
        _finite("funding_paid", self.funding_paid, non_negative=True)
        if self.stopped_trades < 0:
            raise ValueError("stopped_trades must be >= 0")
        ids = [p.position_id for p in self.positions]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate position_id")


@dataclass(frozen=True)
class RiskAssessment:
    allowed: bool
    reasons: tuple[str, ...]
    realized_net_pnl: float
    unrealized_pnl: float
    daily_net_pnl: float
    daily_loss_pct: float
    open_stop_risk: float
    proposed_risk: float
    aggregate_open_risk: float
    remaining_daily_loss_budget: float
    policy_id: str
    policy_version: str


def assess_new_trade(
    *, policy: RiskPolicy, snapshot: RiskSnapshot, symbol: str, side: Side,
    entry: float, stop: float, target: float, proposed_risk: float,
    proposed_asset_class: str,
) -> RiskAssessment:
    """Evaluate a proposed trade against realized + marked-to-market portfolio risk."""
    entry = _finite("entry", entry, positive=True)
    stop = _finite("stop", stop, positive=True)
    target = _finite("target", target, positive=True)
    proposed_risk = _finite("proposed_risk", proposed_risk, positive=True)
    if side not in ("long", "short"):
        raise ValueError("side must be long or short")
    if side == "long" and not stop < entry < target:
        raise ValueError("long trade requires stop < entry < target")
    if side == "short" and not target < entry < stop:
        raise ValueError("short trade requires target < entry < stop")

    positions = snapshot.positions
    unrealized = sum(p.unrealized_pnl for p in positions)
    realized_net = snapshot.realized_pnl - snapshot.fees_paid - snapshot.funding_paid
    daily_net = realized_net + unrealized
    daily_loss = max(0.0, -daily_net) / snapshot.start_equity * 100.0
    open_risk = sum(p.stop_risk for p in positions)
    aggregate = open_risk + proposed_risk
    daily_cap = snapshot.start_equity * policy.daily_loss_limit_pct / 100.0
    remaining = max(0.0, daily_cap + daily_net)
    reasons: list[str] = []

    if snapshot.stopped_trades >= policy.max_stops:
        reasons.append(f"stop count {snapshot.stopped_trades} reached limit {policy.max_stops}")
    if daily_loss >= policy.daily_loss_limit_pct - 1e-9:
        reasons.append("daily net loss limit reached")
    if proposed_risk > snapshot.start_equity * policy.risk_per_trade_pct / 100.0 + 1e-9:
        reasons.append("proposed risk exceeds per-trade policy cap")
    if aggregate > snapshot.start_equity * policy.max_open_risk_pct / 100.0 + 1e-9:
        reasons.append("aggregate open stop risk exceeds portfolio cap")
    if proposed_risk > remaining + 1e-9:
        reasons.append("proposed risk exceeds remaining daily loss budget")

    matching = [p for p in positions if p.symbol.upper() == symbol.upper()]
    if matching and not policy.allow_hedged_sides:
        reasons.append("symbol already has an open position; opposing-side hedge is disabled")
    if matching and any(p.side == side for p in matching):
        reasons.append("duplicate same-side position")

    risk_distance = abs(entry - stop)
    reward_distance = (target - entry) if side == "long" else (entry - target)
    rr = reward_distance / risk_distance
    if rr < policy.min_reward_risk - 1e-9:
        reasons.append(f"reward:risk {rr:.3f} below policy minimum {policy.min_reward_risk:.3f}")

    return RiskAssessment(
        allowed=not reasons, reasons=tuple(reasons), realized_net_pnl=realized_net,
        unrealized_pnl=unrealized, daily_net_pnl=daily_net, daily_loss_pct=daily_loss,
        open_stop_risk=open_risk, proposed_risk=proposed_risk, aggregate_open_risk=aggregate,
        remaining_daily_loss_budget=remaining, policy_id=policy.policy_id,
        policy_version=policy.version,
    )
