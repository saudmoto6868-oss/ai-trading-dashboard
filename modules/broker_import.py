"""MAE/MFE computation and broker trade import (MT5 CSV)."""
from __future__ import annotations

import csv
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


def _parse_dt(val: Any) -> datetime:
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    if isinstance(val, (int, float)):
        sec = val / 1000.0 if val > 1e12 else float(val)
        return datetime.fromtimestamp(sec, tz=timezone.utc)
    s = str(val).strip().replace(".", "-", 2).replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def compute_mae_mfe(
    trade: Dict[str, Any],
    candles: Sequence[Dict[str, Any]],
) -> Dict[str, float]:
    """Calculate MAE/MFE in price points and % of stop/target."""
    entry = float(trade["entry"])
    stop = float(trade["stop"])
    tp = float(trade.get("tp", trade.get("take_profit", entry)))
    side = str(trade.get("type", trade.get("side", "buy"))).lower()

    if not candles:
        return {
            "mae_points": 0.0,
            "mfe_points": 0.0,
            "mae_percent_of_stop": 0.0,
            "mfe_percent_of_target": 0.0,
        }

    highs = [float(c["high"]) for c in candles if "high" in c]
    lows = [float(c["low"]) for c in candles if "low" in c]
    if not highs or not lows:
        return {
            "mae_points": 0.0,
            "mfe_points": 0.0,
            "mae_percent_of_stop": 0.0,
            "mfe_percent_of_target": 0.0,
        }

    if side in ("buy", "long"):
        mae_pts = max(0.0, entry - min(lows))
        mfe_pts = max(0.0, max(highs) - entry)
    else:
        mae_pts = max(0.0, max(highs) - entry)
        mfe_pts = max(0.0, entry - min(lows))

    stop_dist = abs(entry - stop)
    tp_dist = abs(tp - entry)
    return {
        "mae_points": round(mae_pts, 4),
        "mfe_points": round(mfe_pts, 4),
        "mae_percent_of_stop": round((mae_pts / stop_dist) * 100.0, 2) if stop_dist > 0 else 0.0,
        "mfe_percent_of_target": round((mfe_pts / tp_dist) * 100.0, 2) if tp_dist > 0 else 0.0,
    }


def parse_mt5_csv(csv_path: Path | str) -> List[Dict[str, Any]]:
    """Parse MetaTrader 5 CSV export."""
    path = Path(csv_path)
    trades: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader or []):
            if not row:
                continue
            trades.append(
                {
                    "broker_id": row.get("broker_id") or f"MT5_{idx + 1}",
                    "timestamp": _parse_dt(row["timestamp"]),
                    "symbol": str(row["symbol"]).strip().upper(),
                    "type": str(row.get("type", "buy")).strip().lower(),
                    "entry": float(row["entry"]),
                    "stop": float(row["stop"]),
                    "tp": float(row["tp"]),
                    "profit": float(row.get("profit", 0.0)),
                }
            )
    return trades


def match_trades_with_signals(
    broker_trades: Sequence[Dict[str, Any]],
    signal_log: Sequence[Dict[str, Any]],
    tolerance_minutes: int = 5,
    candles_by_symbol: Optional[Dict[str, Sequence[Dict[str, Any]]]] = None,
) -> List[Dict[str, Any]]:
    """Match broker trades against signal_log and compute MAE/MFE."""
    tol = timedelta(minutes=tolerance_minutes)
    used_signals: set[Any] = set()
    merged: List[Dict[str, Any]] = []

    for bt in broker_trades:
        bt_ts = _parse_dt(bt["timestamp"])
        bt_sym = str(bt["symbol"]).strip().upper()
        matched_sig: Optional[Dict[str, Any]] = None
        best_delta: Optional[timedelta] = None

        for sig in signal_log:
            sid = sig.get("signal_id")
            if sid in used_signals:
                continue
            if str(sig.get("symbol", "")).strip().upper() != bt_sym:
                continue
            delta = abs(_parse_dt(sig["timestamp"]) - bt_ts)
            if delta <= tol and (best_delta is None or delta < best_delta):
                best_delta = delta
                matched_sig = sig

        if matched_sig is not None:
            used_signals.add(matched_sig.get("signal_id"))

        candles = (candles_by_symbol or {}).get(bt_sym, [])
        excursion = compute_mae_mfe(bt, candles) if candles else {"mae_points": 0.0, "mfe_points": 0.0}
        merged.append(
            {
                "broker_id": bt.get("broker_id"),
                "signal_id": matched_sig.get("signal_id") if matched_sig else None,
                "symbol": bt_sym,
                "matched": matched_sig is not None,
                "mae": excursion["mae_points"],
                "mfe": excursion["mfe_points"],
                "profit": bt.get("profit", 0.0),
            }
        )
    return merged


def filter_imported_trades(
    rows: Sequence[Dict[str, Any]],
    status: str = "all",
) -> List[Dict[str, Any]]:
    """Filter Imported Trades by 'all', 'matched', or 'unmatched'."""
    st = status.lower()
    if st == "matched":
        return [r for r in rows if r.get("matched")]
    if st == "unmatched":
        return [r for r in rows if not r.get("matched")]
    return list(rows)
