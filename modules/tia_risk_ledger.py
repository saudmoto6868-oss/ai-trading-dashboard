"""TIA risk sizing and durable daily ledger.

SQLite ledger is a local single-database coordination primitive, not a distributed
multi-process guarantee across hosts or network filesystems. Production deployment
must place it on a supported transactional database and define account/session keys.
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from modules.tia_risk_engine import InstrumentSpec, Position, _finite


@dataclass(frozen=True)
class ConversionQuote:
    source_currency: str
    account_currency: str
    rate: float
    source: str
    observed_at: datetime

    def validate(self, *, now: datetime, max_age_seconds: int) -> float:
        if not self.source.strip():
            raise ValueError("FX conversion source is required")
        if self.observed_at.tzinfo is None or now.tzinfo is None:
            raise ValueError("FX quote and now must be timezone-aware")
        if isinstance(max_age_seconds, bool) or not isinstance(max_age_seconds, int) or max_age_seconds < 0:
            raise ValueError("max_fx_age_seconds must be a non-negative integer")
        rate = _finite("FX rate", self.rate, positive=True)
        age = (now - self.observed_at).total_seconds()
        if age < -5:
            raise ValueError("FX quote timestamp is in the future")
        if age > max_age_seconds:
            raise ValueError("FX conversion quote is stale")
        return rate


@dataclass(frozen=True)
class SizedTrade:
    quantity: float
    stop_risk_account_ccy: float
    gross_stop_risk_account_ccy: float
    estimated_cost_reserve_account_ccy: float
    risk_budget_account_ccy: float
    risk_per_unit_account_ccy: float
    actual_risk_pct: float


def _on_increment(value: float, increment: float, name: str) -> None:
    units = value / increment
    if abs(units - round(units)) > 1e-7:
        raise ValueError(f"{name} must align to instrument increment {increment}")


def size_trade(*, equity: float, risk_pct: float, entry: float, stop: float,
               side: Literal["long", "short"], spec: InstrumentSpec,
               fx_quote: ConversionQuote, account_currency: str,
               now: datetime, max_fx_age_seconds: int = 300) -> SizedTrade:
    """Size down to quantity step; costs and FX conversion are included in risk."""
    equity = _finite("equity", equity, positive=True)
    risk_pct = _finite("risk_pct", risk_pct, positive=True)
    entry = _finite("entry", entry, positive=True)
    stop = _finite("stop", stop, positive=True)
    if side not in ("long", "short"):
        raise ValueError("side must be long or short")
    if side == "long" and stop >= entry:
        raise ValueError("long stop must be below entry")
    if side == "short" and stop <= entry:
        raise ValueError("short stop must be above entry")
    if account_currency.upper() != fx_quote.account_currency.upper():
        raise ValueError("FX quote account currency mismatch")
    if spec.quote_currency.upper() != fx_quote.source_currency.upper():
        raise ValueError("FX quote source currency mismatch")
    fx = fx_quote.validate(now=now, max_age_seconds=max_fx_age_seconds)
    _on_increment(entry, spec.tick_size, "entry")
    _on_increment(stop, spec.tick_size, "stop")

    price_risk_quote = abs(entry - stop) * spec.point_value * spec.contract_multiplier
    cost_quote = spec.fee_per_unit_round_trip + spec.funding_reserve_per_unit
    per_unit_account = (price_risk_quote + cost_quote) * fx
    budget = equity * risk_pct / 100.0
    raw_qty = budget / per_unit_account
    qty = math.floor(raw_qty / spec.quantity_step + 1e-10) * spec.quantity_step
    if qty <= 0:
        raise ValueError("risk budget is too small for the minimum quantity step")
    gross = qty * price_risk_quote * fx
    costs = qty * cost_quote * fx
    risk = gross + costs
    return SizedTrade(qty, risk, gross, costs, budget, per_unit_account,
                      risk / equity * 100.0)


class RiskLedger:
    """Append-only event ledger with idempotency and atomic session updates."""

    def __init__(self, db_path: str, *, busy_timeout_ms: int = 5000):
        if not str(db_path).strip() or db_path == ":memory:":
            raise ValueError("a persistent file-backed db_path is required; :memory: is not supported")
        self.db_path = db_path
        self.busy_timeout_ms = int(busy_timeout_ms)
        if self.busy_timeout_ms < 1:
            raise ValueError("busy_timeout_ms must be positive")
        if db_path != ":memory:":
            Path(db_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        con = sqlite3.connect(self.db_path, timeout=self.busy_timeout_ms / 1000,
                              isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute(f"PRAGMA busy_timeout={self.busy_timeout_ms}")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _initialize(self):
        with closing(self._connect()) as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS risk_sessions (
                session_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                session_date TEXT NOT NULL,
                timezone TEXT NOT NULL,
                start_equity REAL NOT NULL CHECK(start_equity > 0),
                policy_id TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS risk_events (
                event_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES risk_sessions(session_id),
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_risk_events_session
                ON risk_events(session_id, created_at);
            CREATE TRIGGER IF NOT EXISTS risk_events_no_update
            BEFORE UPDATE ON risk_events BEGIN
                SELECT RAISE(ABORT, 'risk events are append-only');
            END;
            CREATE TRIGGER IF NOT EXISTS risk_events_no_delete
            BEFORE DELETE ON risk_events BEGIN
                SELECT RAISE(ABORT, 'risk events are append-only');
            END;
            """)

    @staticmethod
    def session_date(now: datetime, timezone_name: str) -> str:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        try:
            zone = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("unknown IANA session timezone") from exc
        return now.astimezone(zone).date().isoformat()

    def open_session(self, *, account_id: str, now: datetime, timezone_name: str,
                     start_equity: float, policy_id: str, policy_version: str) -> str:
        if not account_id.strip() or not policy_id.strip() or not policy_version.strip():
            raise ValueError("account and policy identity are required")
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        equity = _finite("start_equity", start_equity, positive=True)
        day = self.session_date(now, timezone_name)
        sid = hashlib.sha256(f"{account_id}|{timezone_name}|{day}".encode()).hexdigest()
        stamp = now.astimezone(timezone.utc).isoformat()
        with closing(self._connect()) as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM risk_sessions WHERE session_id=?", (sid,)).fetchone()
            if row:
                if (row["policy_id"], row["policy_version"]) != (policy_id, policy_version):
                    con.rollback()
                    raise ValueError("session already exists under a different policy version")
                if not math.isclose(row["start_equity"], equity, rel_tol=1e-9, abs_tol=1e-8):
                    con.rollback()
                    raise ValueError("session already exists with different start equity")
            else:
                con.execute("""INSERT INTO risk_sessions
                    (session_id,account_id,session_date,timezone,start_equity,policy_id,policy_version,created_at)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (sid, account_id, day, timezone_name, equity, policy_id, policy_version, stamp))
            con.commit()
        return sid

    def append_event(self, *, session_id: str, event_id: str, event_type: str,
                     payload: dict, created_at: datetime) -> bool:
        if not session_id.strip() or not event_id.strip() or not event_type.strip():
            raise ValueError("session_id, event_id and event_type are required")
        if created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        stamp = created_at.astimezone(timezone.utc).isoformat()
        with closing(self._connect()) as con:
            con.execute("BEGIN IMMEDIATE")
            if not con.execute("SELECT 1 FROM risk_sessions WHERE session_id=?", (session_id,)).fetchone():
                con.rollback()
                raise ValueError("unknown risk session")
            prior = con.execute("SELECT payload_sha256, event_type, session_id FROM risk_events WHERE event_id=?",
                                (event_id,)).fetchone()
            if prior:
                con.rollback()
                if prior["payload_sha256"] != digest or prior["event_type"] != event_type or prior["session_id"] != session_id:
                    raise ValueError("event_id replayed with different content")
                return False
            con.execute("""INSERT INTO risk_events
                (event_id,session_id,event_type,payload_json,payload_sha256,created_at)
                VALUES(?,?,?,?,?,?)""", (event_id, session_id, event_type, canonical, digest, stamp))
            con.commit()
        return True

    def events(self, session_id: str) -> list[dict]:
        with closing(self._connect()) as con:
            rows = con.execute("""SELECT event_id,event_type,payload_json,payload_sha256,created_at
                                  FROM risk_events WHERE session_id=? ORDER BY rowid""",
                               (session_id,)).fetchall()
        return [{**dict(row), "payload": json.loads(row["payload_json"])} for row in rows]


    def project_session(self, session_id: str) -> dict:
        """Rebuild deterministic daily risk state from the append-only event journal.

        Event contract:
        - position_open: {position_id, symbol, asset_class, side, quantity, entry, stop, mark, spec:{...}}
        - position_mark: {position_id, mark}
        - position_close: {position_id, realized_pnl, fees_paid, funding_paid, stopped}
        Stop classification is explicit; a losing manual close is not automatically a stop.
        """
        session = self.session(session_id)
        if session is None:
            raise ValueError("unknown risk session")
        positions: dict[str, dict] = {}
        realized = fees = funding = 0.0
        deposits = withdrawals = 0.0
        cashflow_count = 0
        stopped_trades = 0
        for event in self.events(session_id):
            payload = event["payload"]
            kind = event["event_type"]
            if kind == "position_open":
                required = ("position_id", "symbol", "asset_class", "side", "quantity", "entry", "stop", "mark", "spec")
                if any(k not in payload for k in required):
                    raise ValueError("position_open event is missing required fields")
                pid = str(payload["position_id"])
                if not pid or pid in positions:
                    raise ValueError("position_open duplicates an active position_id")
                spec = InstrumentSpec(**dict(payload["spec"]))
                Position(position_id=pid, symbol=str(payload["symbol"]),
                         asset_class=str(payload["asset_class"]), side=payload["side"],
                         quantity=payload["quantity"], entry=payload["entry"],
                         stop=payload["stop"], mark=payload["mark"], spec=spec)
                positions[pid] = {k: payload[k] for k in required if k != "spec"}
                positions[pid]["spec"] = dict(payload["spec"])
            elif kind == "position_mark":
                pid = str(payload.get("position_id", ""))
                if pid not in positions:
                    raise ValueError("position_mark references an unknown open position")
                mark = _finite("mark", payload.get("mark"), positive=True)
                positions[pid]["mark"] = mark
            elif kind == "account_cashflow":
                flow_type = payload.get("flow_type")
                if flow_type not in ("deposit", "withdrawal"):
                    raise ValueError("account_cashflow requires flow_type deposit or withdrawal")
                amount = _finite("cashflow amount", payload.get("amount"), positive=True)
                currency = payload.get("account_currency")
                source = payload.get("source")
                reference = payload.get("external_reference")
                if not isinstance(currency, str) or not currency.strip():
                    raise ValueError("account_cashflow requires account_currency")
                if not isinstance(source, str) or not source.strip():
                    raise ValueError("account_cashflow requires source provenance")
                if not isinstance(reference, str) or not reference.strip():
                    raise ValueError("account_cashflow requires external_reference")
                if flow_type == "deposit":
                    deposits += amount
                else:
                    withdrawals += amount
                cashflow_count += 1
            elif kind == "position_close":
                pid = str(payload.get("position_id", ""))
                if pid not in positions:
                    raise ValueError("position_close references an unknown open position")
                realized += _finite("realized_pnl", payload.get("realized_pnl", 0.0))
                fees += _finite("fees_paid", payload.get("fees_paid", 0.0), non_negative=True)
                funding += _finite("funding_paid", payload.get("funding_paid", 0.0), non_negative=True)
                stopped = payload.get("stopped")
                if not isinstance(stopped, bool):
                    raise ValueError("position_close requires explicit boolean stopped classification")
                if stopped:
                    stopped_trades += 1
                del positions[pid]
            else:
                raise ValueError(f"unsupported risk event type: {kind}")
        return {
            "session_id": session_id,
            "account_id": session["account_id"],
            "session_date": session["session_date"],
            "timezone": session["timezone"],
            "start_equity": session["start_equity"],
            "policy_id": session["policy_id"],
            "policy_version": session["policy_version"],
            "realized_pnl": realized,
            "fees_paid": fees,
            "funding_paid": funding,
            "deposits_account_ccy": deposits,
            "withdrawals_account_ccy": withdrawals,
            "net_cashflow_account_ccy": deposits - withdrawals,
            "cashflow_count": cashflow_count,
            "stopped_trades": stopped_trades,
            "open_positions": list(positions.values()),
            "open_position_count": len(positions),
        }

    def session(self, session_id: str) -> dict | None:
        with closing(self._connect()) as con:
            row = con.execute("SELECT * FROM risk_sessions WHERE session_id=?", (session_id,)).fetchone()
        return dict(row) if row else None
