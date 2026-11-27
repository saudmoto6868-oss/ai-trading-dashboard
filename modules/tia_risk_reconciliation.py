"""Fail-closed reconciliation between TIA's event projection and broker positions.

This module is read-only. It does not connect to a broker or mutate account state.
A caller must map provider payloads into the normalized BrokerPosition contract.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime

from modules.tia_risk_engine import _finite


@dataclass(frozen=True)
class BrokerPosition:
    position_id: str
    symbol: str
    side: str
    quantity: float
    entry: float

    def __post_init__(self):
        if not self.position_id.strip() or not self.symbol.strip():
            raise ValueError("broker position identity is required")
        if self.side not in ("long", "short"):
            raise ValueError("broker side must be long or short")
        _finite("broker quantity", self.quantity, positive=True)
        _finite("broker entry", self.entry, positive=True)


@dataclass(frozen=True)
class BrokerPositionSnapshot:
    account_id: str
    source: str
    observed_at: datetime
    positions: tuple[BrokerPosition, ...]
    complete: bool

    def __post_init__(self):
        if not self.account_id.strip() or not self.source.strip():
            raise ValueError("broker account and source are required")
        if self.observed_at.tzinfo is None:
            raise ValueError("broker snapshot timestamp must be timezone-aware")
        if not isinstance(self.complete, bool):
            raise ValueError("broker snapshot complete must be an explicit boolean")
        if not isinstance(self.positions, tuple) or any(not isinstance(p, BrokerPosition) for p in self.positions):
            raise ValueError("broker positions must be a tuple of validated BrokerPosition objects")
        ids = [p.position_id for p in self.positions]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate broker position_id")


@dataclass(frozen=True)
class ReconciliationResult:
    reconciled: bool
    reasons: tuple[str, ...]
    source: str
    observed_at: datetime
    matched_position_count: int
    ledger_only_ids: tuple[str, ...]
    broker_only_ids: tuple[str, ...]
    mismatched_ids: tuple[str, ...]


def reconcile_positions(*, ledger_state: dict, broker: BrokerPositionSnapshot,
                        now: datetime, max_age_seconds: int = 15,
                        quantity_tolerance: float = 1e-8,
                        entry_tolerance: float = 1e-8) -> ReconciliationResult:
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if isinstance(max_age_seconds, bool) or not isinstance(max_age_seconds, int) or max_age_seconds < 0:
        raise ValueError("max_age_seconds must be a non-negative integer")
    qt = _finite("quantity_tolerance", quantity_tolerance, non_negative=True)
    et = _finite("entry_tolerance", entry_tolerance, non_negative=True)
    age = (now - broker.observed_at).total_seconds()
    reasons = []
    if age < -5:
        reasons.append("broker snapshot timestamp is in the future")
    elif age > max_age_seconds:
        reasons.append("broker position snapshot is stale")
    if not broker.complete:
        reasons.append("broker position snapshot is incomplete")
    if str(ledger_state.get("account_id", "")) != broker.account_id:
        reasons.append("broker and ledger account IDs do not match")

    ledger_positions = ledger_state.get("open_positions")
    if not isinstance(ledger_positions, list):
        raise ValueError("ledger_state.open_positions must be a list")
    ledger_by_id = {}
    for p in ledger_positions:
        pid = str(p.get("position_id", ""))
        if not pid or pid in ledger_by_id:
            raise ValueError("ledger projection contains missing or duplicate position IDs")
        ledger_by_id[pid] = p
    broker_by_id = {p.position_id: p for p in broker.positions}
    ledger_ids, broker_ids = set(ledger_by_id), set(broker_by_id)
    ledger_only = tuple(sorted(ledger_ids - broker_ids))
    broker_only = tuple(sorted(broker_ids - ledger_ids))
    mismatched = []
    for pid in sorted(ledger_ids & broker_ids):
        lp, bp = ledger_by_id[pid], broker_by_id[pid]
        try:
            same = (
                str(lp["symbol"]).upper() == bp.symbol.upper()
                and lp["side"] == bp.side
                and math.isclose(float(lp["quantity"]), bp.quantity, rel_tol=0.0, abs_tol=qt)
                and math.isclose(float(lp["entry"]), bp.entry, rel_tol=0.0, abs_tol=et)
            )
        except (KeyError, TypeError, ValueError):
            same = False
        if not same:
            mismatched.append(pid)
    if ledger_only:
        reasons.append("ledger contains positions absent from broker snapshot")
    if broker_only:
        reasons.append("broker contains positions absent from ledger")
    if mismatched:
        reasons.append("broker and ledger position attributes differ")
    return ReconciliationResult(
        reconciled=not reasons, reasons=tuple(reasons), source=broker.source,
        observed_at=broker.observed_at, matched_position_count=len(ledger_ids & broker_ids) - len(mismatched),
        ledger_only_ids=ledger_only, broker_only_ids=broker_only,
        mismatched_ids=tuple(mismatched),
    )
