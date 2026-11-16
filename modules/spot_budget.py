"""Budget plan math for the Spot desk (owner 2026-11-16): a fixed budget on OKX spot, split into DCA / swing / reserve,
a per-trade loss cap, a monthly loss cap and a weekly review. Pure functions: no network, no orders, no Streamlit."""
from __future__ import annotations

from datetime import date

DEFAULT_SPLIT = {"dca": 60.0, "swing": 25.0, "reserve": 15.0}
DEFAULT_DCA_WEIGHTS = {"BTC": 60.0, "ETH": 40.0}
DEFAULT_PLAN = {"budget": 1000.0, "split": dict(DEFAULT_SPLIT), "dca_weeks": 12, "dca_weights": dict(DEFAULT_DCA_WEIGHTS),
                "risk_pct": 1.0, "monthly_cap_pct": 5.0, "max_open": 2, "min_rr": 2.0}
WEEKLY_CHECKLIST = [
    "DCA executed this week (amount and price written in the journal)",
    "Every open swing trade has a stop placed on the exchange",
    "Month-to-date loss is below the monthly cap",
    "Every closed trade: reason and result match the plan",
    "No rule broken this week (if yes: write it down, do not repeat it)",
    "Market check done (fear & greed, BTC dominance) for context only, not as an entry signal",
]


def _pos(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return v if v > 0 else 0.0


def split_budget(total: float, split: dict[str, float]) -> dict[str, float]:
    """Split a budget by percentages. The percentages are normalised, so they do not have to add up to 100."""
    weights = {k: _pos(v) for k, v in split.items()}
    s = sum(weights.values())
    if _pos(total) == 0 or s == 0:
        return {k: 0.0 for k in split}
    return {k: round(_pos(total) * w / s, 2) for k, w in weights.items()}


def dca_schedule(total: float, weeks: int, weights: dict[str, float]) -> list[dict]:
    """Equal weekly amount over `weeks`, divided between coins by `weights`."""
    weeks = int(weeks) if str(weeks).lstrip("-").isdigit() else 0
    if weeks <= 0 or _pos(total) == 0:
        return []
    per_week = _pos(total) / weeks
    s = sum(_pos(v) for v in weights.values()) or 1.0
    rows = []
    for w in range(1, weeks + 1):
        row = {"week": w}
        for coin, v in weights.items():
            row[coin] = round(per_week * _pos(v) / s, 2)
        row["total"] = round(per_week, 2)
        rows.append(row)
    return rows


def position_size(budget: float, risk_pct: float, stop_pct: float) -> float:
    """Largest position whose loss at the stop is `risk_pct` of the budget. stop_pct = distance from entry to stop, in %."""
    if _pos(budget) == 0 or _pos(risk_pct) == 0 or _pos(stop_pct) == 0:
        return 0.0
    return round(_pos(budget) * (_pos(risk_pct) / 100.0) / (_pos(stop_pct) / 100.0), 2)


def loss_at_stop(size: float, stop_pct: float) -> float:
    return round(_pos(size) * _pos(stop_pct) / 100.0, 2)


def stop_pct_from_prices(entry: float, stop: float) -> float | None:
    """Stop distance below a long entry, in %. None when the numbers do not make a long setup."""
    if _pos(entry) == 0 or _pos(stop) == 0 or stop >= entry:
        return None
    return round((entry - stop) / entry * 100.0, 4)


def reward_risk(entry: float, stop: float, target: float) -> float | None:
    """Reward to risk for a long. None when the levels are not in the right order."""
    if _pos(entry) == 0 or _pos(stop) == 0 or stop >= entry or target <= entry:
        return None
    return round((target - entry) / (entry - stop), 2)


def monthly_cap(budget: float, pct: float) -> float:
    return round(_pos(budget) * _pos(pct) / 100.0, 2)


def month_loss(journal: list[dict], ym: str) -> float:
    """Sum of closed losses whose date starts with `ym` (YYYY-MM). Journal result is a signed USD number."""
    total = 0.0
    for r in journal:
        res = r.get("result")
        if res in (None, "") or not str(r.get("date", "")).startswith(ym):
            continue
        try:
            v = float(res)
        except (TypeError, ValueError):
            continue
        if v < 0:
            total += -v
    return round(total, 2)


def open_count(journal: list[dict]) -> int:
    return sum(1 for r in journal if r.get("result") in (None, "") and str(r.get("asset", "")).strip())


def today_ym() -> str:
    return date.today().strftime("%Y-%m")
