"""Portfolio-level prop firm simulator with daily loss limits, max DD, and overlapping trades."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence
import math


@dataclass
class PropRules:
    initial_equity: float = 100_000.0
    risk_per_trade_pct: float = 0.01
    daily_loss_limit_pct: float = 0.02
    max_dd_pct: float = 0.10
    allow_overlapping: bool = True


def _to_date_key(ts: Any, fallback_idx: int) -> str:
    if ts is None:
        return f"day_{fallback_idx // 10}"
    if isinstance(ts, datetime):
        return ts.astimezone(timezone.utc).strftime("%Y-%m-%d")
    if isinstance(ts, (int, float)):
        sec = ts / 1000.0 if ts > 1e12 else float(ts)
        return datetime.fromtimestamp(sec, tz=timezone.utc).strftime("%Y-%m-%d")
    return str(ts)[:10]


def _resolve_pnl_r(trade: Dict[str, Any]) -> float:
    if "pnl_r" in trade and trade["pnl_r"] is not None:
        return float(trade["pnl_r"])
    if "r" in trade and trade["r"] is not None:
        return float(trade["r"])
    entry = float(trade["entry"])
    stop = float(trade["stop"])
    tp = float(trade["take_profit"])
    side = str(trade.get("side", "long")).lower()
    risk_dist = abs(entry - stop)
    if risk_dist <= 0:
        return 0.0
    exit_price = float(trade.get("exit_price", tp if trade.get("win", True) else stop))
    raw_move = (exit_price - entry) if side in ("long", "buy") else (entry - exit_price)
    return raw_move / risk_dist


def lab_to_portfolio_trades(lab_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert strategy_lab rows into standardized portfolio trade dicts."""
    trades: List[Dict[str, Any]] = []
    for idx, row in enumerate(lab_rows):
        entry = float(row.get("entry", 100.0))
        stop = float(row.get("stop", 99.0))
        tp = float(row.get("take_profit", row.get("tp", 102.0)))
        trades.append(
            {
                "trade_id": row.get("trade_id", idx + 1),
                "symbol": row.get("symbol", "UNKNOWN"),
                "side": row.get("side", "long"),
                "entry": entry,
                "stop": stop,
                "take_profit": tp,
                "size_r": float(row.get("size_r", 1.0)),
                "pnl_r": row.get("pnl_r", row.get("r")),
                "open_time": row.get("open_time", row.get("timestamp")),
                "close_time": row.get("close_time", row.get("timestamp")),
            }
        )
    return trades


def simulate_portfolio(
    trades: Sequence[Dict[str, Any]],
    prop_rules: Optional[PropRules] = None,
) -> Dict[str, Any]:
    """Simulate portfolio through trades with prop firm rules (daily loss limit, max DD)."""
    rules = prop_rules or PropRules()
    equity = rules.initial_equity
    peak_equity = equity
    max_dd_pct = 0.0

    daily_pnl: Dict[str, float] = {}
    daily_start_equity: Dict[str, float] = {}
    halted_days: set[str] = set()

    equity_curve: List[float] = [equity]
    trade_records: List[Dict[str, Any]] = []
    accepted_returns: List[float] = []
    win_rs: List[float] = []
    loss_rs: List[float] = []
    skipped_daily_limit = 0
    prop_breached = False

    for idx, tr in enumerate(trades):
        day_key = _to_date_key(tr.get("close_time") or tr.get("open_time"), idx)
        if day_key not in daily_start_equity:
            daily_start_equity[day_key] = equity
            daily_pnl[day_key] = 0.0

        if day_key in halted_days or prop_breached:
            skipped_daily_limit += 1
            trade_records.append(
                {
                    **tr,
                    "executed": False,
                    "equity_at_close": round(equity, 2),
                    "dd_at_close": round(max_dd_pct, 6),
                    "daily_loss": round(min(0.0, daily_pnl[day_key]), 2),
                    "prop_pass": not prop_breached,
                }
            )
            continue

        size_r = float(tr.get("size_r", 1.0))
        pnl_r = _resolve_pnl_r(tr) * size_r
        dollar_risk = equity * rules.risk_per_trade_pct
        pnl_dollar = pnl_r * dollar_risk

        equity += pnl_dollar
        daily_pnl[day_key] += pnl_dollar
        peak_equity = max(peak_equity, equity)
        current_dd = (peak_equity - equity) / peak_equity if peak_equity > 0 else 0.0
        max_dd_pct = max(max_dd_pct, current_dd)

        day_loss_pct = -daily_pnl[day_key] / daily_start_equity[day_key] if daily_start_equity[day_key] > 0 else 0.0
        if day_loss_pct >= rules.daily_loss_limit_pct:
            halted_days.add(day_key)
        if current_dd >= rules.max_dd_pct:
            prop_breached = True

        equity_curve.append(round(equity, 2))
        accepted_returns.append(pnl_r)
        if pnl_r > 0:
            win_rs.append(pnl_r)
        elif pnl_r < 0:
            loss_rs.append(pnl_r)

        trade_records.append(
            {
                **tr,
                "executed": True,
                "pnl_r": round(pnl_r, 4),
                "equity_at_close": round(equity, 2),
                "dd_at_close": round(current_dd, 6),
                "daily_loss": round(min(0.0, daily_pnl[day_key]), 2),
                "prop_pass": not prop_breached,
            }
        )

    n_exec = len(accepted_returns)
    win_pct = (len(win_rs) / n_exec * 100.0) if n_exec else 0.0
    avg_win_r = (sum(win_rs) / len(win_rs)) if win_rs else 0.0
    avg_loss_r = (sum(loss_rs) / len(loss_rs)) if loss_rs else 0.0
    gross_win = sum(win_rs)
    gross_loss = abs(sum(loss_rs))
    profit_factor = (gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)

    if n_exec > 1:
        mean_r = sum(accepted_returns) / n_exec
        var_r = sum((x - mean_r) ** 2 for x in accepted_returns) / (n_exec - 1)
        std_r = math.sqrt(var_r)
        sharpe = (mean_r / std_r) * math.sqrt(n_exec) if std_r > 0 else 0.0
    else:
        sharpe = 0.0

    return {
        "equity_curve": equity_curve,
        "final_equity": round(equity, 2),
        "total_trades": len(trades),
        "executed_trades": n_exec,
        "skipped_daily_limit": skipped_daily_limit,
        "win_pct": round(win_pct, 2),
        "win_r": round(avg_win_r, 4),
        "loss_r": round(avg_loss_r, 4),
        "profit_factor": round(profit_factor, 4) if math.isfinite(profit_factor) else None,
        "sharpe": round(sharpe, 4),
        "max_dd_pct": round(max_dd_pct * 100.0, 2),
        "prop_pass": not prop_breached,
        "trades": trade_records,
    }
