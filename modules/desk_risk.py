"""Order Flow Desk - agent 5 (risk manager): position size + daily guard.

Rules: 0.25 % base; 0.50 % only for explicitly validated A+ setups with n >= 30. Max daily loss 2 %,
stop trading after 3 stops in a day, reward:risk at least 1:2 (docs/MEETING_ROOM.md, 2026-11-08).
Nothing here places orders - it only says "allowed / blocked, and why".

Pure functions, no Streamlit, no network -> unit-tested in tests/test_desk_risk.py.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from modules.risk_policy import risk_pct_for_setup


@dataclass(frozen=True)
class DeskRules:
    daily_max_loss_pct: float = 2.0  # % of start-of-day equity; reaching it locks the day
    max_stops: int = 3               # stops (losing trades) per day before the day locks
    min_rr: float = 2.0              # first target must be >= min_rr x risk


RULES = DeskRules()


def position_size(equity: float, entry: float, stop: float,
                  point_value: float = 1.0, qty_step: float = 0.0, *, grade=None,
                  validation_n=0, validation_passed=False) -> dict:
    """Size under the shared automatic risk policy; callers cannot choose a percentage.

    point_value = money per 1.0 price move per unit (1 for spot crypto / CFD units, 50 for ES, 20 for NQ ...).
    qty_step > 0 rounds the quantity DOWN to that step (never up: rounding up would break the risk cap).
    -> includes qty, risk_amount, risk_per_unit, policy risk_pct and actual_risk_pct. qty 0 means the stop is too wide for the step.
    """
    rp = risk_pct_for_setup(grade, validation_n, validation_passed)
    if equity <= 0 or rp <= 0:
        raise ValueError("equity and risk_pct must be > 0")
    per_unit = abs(float(entry) - float(stop)) * float(point_value)
    if per_unit <= 0:
        raise ValueError("stop must differ from entry")
    budget = equity * rp / 100.0
    qty = budget / per_unit
    if qty_step and qty_step > 0:
        qty = math.floor(qty / qty_step + 1e-9) * qty_step
    risk = qty * per_unit
    return {"qty": qty, "risk_amount": risk, "risk_per_unit": per_unit,
            "risk_pct": rp, "actual_risk_pct": risk / equity * 100.0}


def reward_risk(entry: float, stop: float, target: float) -> float:
    """Reward:risk of one target. Negative if the target is on the stop's side."""
    risk = abs(entry - stop)
    if risk <= 0:
        raise ValueError("stop must differ from entry")
    long = stop < entry
    reward = (target - entry) if long else (entry - target)
    return reward / risk


@dataclass
class DeskDay:
    """One trading day. Feed it closed trades with record(); ask check() before every new trade."""
    start_equity: float
    rules: DeskRules = RULES
    realized: float = 0.0
    stops: int = 0
    open_keys: set = field(default_factory=set)
    log: list = field(default_factory=list)

    # ---- state -------------------------------------------------------------------------------
    @property
    def loss_pct(self) -> float:
        """Today's net realized loss as % of start equity (0 when the day is green)."""
        return max(0.0, -self.realized) / self.start_equity * 100.0

    def lock_reason(self) -> str | None:
        if self.stops >= self.rules.max_stops:
            return f"{self.stops} stops today (limit {self.rules.max_stops}) - day locked"
        if self.loss_pct >= self.rules.daily_max_loss_pct - 1e-9:
            return f"daily loss {self.loss_pct:.2f}% >= {self.rules.daily_max_loss_pct}% - day locked"
        return None

    def remaining_budget(self) -> float:
        """Money that can still be lost today before the daily cap."""
        cap = self.start_equity * self.rules.daily_max_loss_pct / 100.0
        return max(0.0, cap - max(0.0, -self.realized))

    # ---- actions -----------------------------------------------------------------------------
    def open(self, symbol: str, side: str) -> None:
        self.open_keys.add((symbol.upper(), side.lower()))

    def record(self, pnl: float, symbol: str = "", side: str = "", stopped: bool | None = None) -> None:
        """A trade closed. stopped defaults to pnl < 0 (a loss counts as a stop)."""
        self.realized += float(pnl)
        if stopped if stopped is not None else pnl < 0:
            self.stops += 1
        if symbol:
            self.open_keys.discard((symbol.upper(), side.lower()))
        self.log.append({"pnl": float(pnl), "symbol": symbol, "side": side})

    def check(self, symbol: str, side: str, entry: float, stop: float, target: float,
              risk_amount: float, *, grade=None, validation_n=0, validation_passed=False) -> tuple[bool, list[str]]:
        """-> (allowed, reasons). Every failed rule is listed, not only the first."""
        why = []
        lock = self.lock_reason()
        if lock:
            why.append(lock)
        key = (symbol.upper(), side.lower())
        if key in self.open_keys:
            why.append(f"already open: {symbol} {side} (no duplicates)")
        try:
            rr = reward_risk(entry, stop, target)
            if rr < self.rules.min_rr - 1e-9:
                why.append(f"reward:risk {rr:.2f} < {self.rules.min_rr}")
        except ValueError as e:
            why.append(str(e))
        effective_risk_pct = risk_pct_for_setup(grade, validation_n, validation_passed)
        per_trade_cap = self.start_equity * effective_risk_pct / 100.0
        if risk_amount > per_trade_cap * 1.0001:
            why.append(f"risk {risk_amount:.2f} > per-trade cap {per_trade_cap:.2f} ({effective_risk_pct}%)")
        if risk_amount > self.remaining_budget() * 1.0001:
            why.append(f"risk {risk_amount:.2f} > what is left of today's cap {self.remaining_budget():.2f}")
        return (not why), why
