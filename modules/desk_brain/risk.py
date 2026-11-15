"""Risk desk for the three prop-firm accounts in Saud's framework.

Rules (from the framework doc, "Risk Management"):
  • every account is sized and tracked on its own; risk is never pooled
  • 0.5% of equity per trade by default, 1% is the hard ceiling
  • personal daily stop = half of the firm's daily limit (a buffer before the firm's wall)
  • tiers: account 2 (entry) → account 1 (mid) → account 3 (instant, A+++ only)
  • instant account: 20% consistency cap → a daily profit cap

Balances are typed in by you (accounts.json in the data folder). The desk never connects to
a broker or a prop firm.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from .config import CONTRACT, DATA_DIR, UNIVERSE
from .data import sources

ACCOUNTS = DATA_DIR / "accounts.json"
DISCIPLINE = DATA_DIR / "discipline.json"

DEFAULT = {
    "risk_pct": 0.5, "risk_cap_pct": 1.0, "stop_pips": [30, 50],
    "accounts": [
        {"id": "acc2", "name": "Account 2 · Step 1/3", "tier": 1, "type": "challenge",
         "start": 100000, "balance": 98548.36, "day_start": 98548.36, "high_water": 101813,
         "daily_dd_pct": 5, "max_loss_pct": 10, "max_loss_mode": "trailing", "target_pct": 5,
         "consistency_pct": None, "min_days": None, "min_payout": None, "prior_profit": 0},
        {"id": "acc1", "name": "Account 1 · Challenge 1/2", "tier": 2, "type": "challenge",
         "start": 100000, "balance": 101597.67, "day_start": 101597.67, "high_water": 101597.67,
         "daily_dd_pct": 4, "max_loss_pct": 6, "max_loss_mode": "static", "target_pct": 5,
         "consistency_pct": None, "min_days": None, "min_payout": None, "prior_profit": 0},
        {"id": "acc3", "name": "Account 3 · Instant (live)", "tier": 3, "type": "instant",
         "start": 100000, "balance": 100000, "day_start": 100000, "high_water": 100000,
         "daily_dd_pct": 4, "max_loss_pct": 7, "max_loss_mode": "static", "target_pct": None,
         "consistency_pct": 20, "min_days": 6, "min_payout": 1000, "prior_profit": 0},
    ],
}
TIER_RULE = {1: "مستوى الدخول: أي فكرة READY/PENDING بـ 3 نجوم فأكثر",
             2: "المستوى الأوسط: READY بـ 4 نجوم فأكثر واعتراض واحد على الأكثر",
             3: "الحساب الممول: فقط A+++ (READY، 5 نجوم، بلا اعتراضات، بيانات حقيقية)"}


def load() -> dict:
    if not ACCOUNTS.exists():
        ACCOUNTS.write_text(json.dumps(DEFAULT, indent=2, ensure_ascii=False))
    return json.loads(ACCOUNTS.read_text())


def save(cfg: dict) -> None:
    ACCOUNTS.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))


def account_state(a: dict, cfg: dict) -> dict:
    daily_floor = a["day_start"] * (1 - a["daily_dd_pct"] / 100)
    base = a["high_water"] if a["max_loss_mode"] == "trailing" else a["start"]
    max_floor = base * (1 - a["max_loss_pct"] / 100)
    personal_floor = a["day_start"] * (1 - a["daily_dd_pct"] / 200)  # half the firm's daily limit
    floor = max(daily_floor, max_floor, personal_floor)
    room_today = max(0.0, a["balance"] - personal_floor)
    risk = min(a["balance"] * cfg["risk_pct"] / 100, a["balance"] * cfg["risk_cap_pct"] / 100, room_today)
    out = {**a, "daily_floor": round(daily_floor, 2), "max_floor": round(max_floor, 2),
           "personal_floor": round(personal_floor, 2), "room_today": round(room_today, 2),
           "room_to_max": round(a["balance"] - max_floor, 2), "risk_per_trade": round(risk, 2),
           "trades_left_today": int(room_today // risk) if risk else 0,
           "stopped_today": a["balance"] <= personal_floor, "tier_rule": TIER_RULE[a["tier"]]}
    if a.get("target_pct"):
        tgt = a["start"] * (1 + a["target_pct"] / 100)
        out["target"] = round(tgt, 2)
        out["to_target"] = round(tgt - a["balance"], 2)
    if a.get("consistency_pct"):
        c = a["consistency_pct"] / 100
        # today ≤ c·(prior + today)  ⇔  today ≤ c/(1−c)·prior. Before any profit, plan for
        # the minimum payout: no day above c·min_payout.
        cap = max(c / (1 - c) * a.get("prior_profit", 0), c * (a.get("min_payout") or 0))
        out["daily_profit_cap"] = round(cap, 2)
        out["today_pnl"] = round(a["balance"] - a["day_start"], 2)
        out["cap_hit"] = out["today_pnl"] >= cap > 0
    return out


def state() -> dict:
    cfg = load()
    return {"risk_pct": cfg["risk_pct"], "risk_cap_pct": cfg["risk_cap_pct"], "stop_pips": cfg["stop_pips"],
            "accounts": [account_state(a, cfg) for a in sorted(cfg["accounts"], key=lambda x: x["tier"])],
            "discipline": discipline()}


def update_account(acc_id: str, fields: dict) -> dict:
    cfg = load()
    allowed = {"balance", "day_start", "high_water", "prior_profit", "name"}
    for a in cfg["accounts"]:
        if a["id"] == acc_id:
            for k, v in fields.items():
                if k in allowed:
                    a[k] = v if k == "name" else float(v)
            a["high_water"] = max(a["high_water"], a["balance"])
    save(cfg)
    return state()


# ------------------------------------------------------------------ sizing
def _usd_per_unit(symbol: str, price: float) -> float:
    """USD P&L for a 1.0 price move on 1.0 lot."""
    m = UNIVERSE[symbol]
    if m["kind"] != "fx":
        return CONTRACT.get(m["base"], 1)
    units = CONTRACT["fx"]
    q = m["quote"]
    if q == "USD":
        return units
    if m["base"] == "USD":
        return units / price
    # cross: convert quote currency to USD with the live USD pair
    pair = f"{q}USD" if f"{q}USD" in UNIVERSE else f"USD{q}"
    px = float(sources.prices(UNIVERSE[pair]["yf"], "1d")[0]["Close"].iloc[-1])
    return units * px if pair.startswith(q) else units / px


def pip_size(symbol: str) -> float:
    m = UNIVERSE[symbol]
    if m["kind"] == "fx":
        return 0.01 if m["quote"] == "JPY" else 0.0001
    return {"XAU": 0.1, "XAG": 0.01}.get(m["base"], 1.0)


def size(symbol: str, entry: float, stop: float, acc_id: str | None = None) -> dict:
    st = state()
    dist = abs(entry - stop)
    per = _usd_per_unit(symbol, entry)
    pips = dist / pip_size(symbol)
    lo, hi = st["stop_pips"]
    out = {"symbol": symbol, "stop_pips": round(pips, 1),
           "pip_rule": "ok" if lo <= pips <= hi or UNIVERSE[symbol]["kind"] != "fx" else ("tight" if pips < lo else "wide"),
           "accounts": []}
    for a in st["accounts"]:
        if acc_id and a["id"] != acc_id:
            continue
        lots = a["risk_per_trade"] / (dist * per) if dist and per else 0
        out["accounts"].append({"id": a["id"], "name": a["name"], "risk": a["risk_per_trade"],
                                "lots": round(lots, 2), "stopped": a["stopped_today"] or st["discipline"]["locked"]})
    return out


def route(idea: dict, stars: int) -> list[str]:
    """Which accounts may take this idea, by tier."""
    ok = []
    real = not idea.get("demo")
    if idea["status"] in ("READY", "PENDING") and stars >= 3:
        ok.append("acc2")
    if idea["status"] == "READY" and stars >= 4 and len(idea["doubts"]) <= 1:
        ok.append("acc1")
    if idea["status"] == "READY" and stars >= 5 and not idea["doubts"] and real:
        ok.append("acc3")
    return ok


# ------------------------------------------------------------------ discipline lock
def discipline() -> dict:
    d = json.loads(DISCIPLINE.read_text()) if DISCIPLINE.exists() else {}
    today = datetime.now(timezone.utc).date().isoformat()
    locked = d.get("locked_on") == today
    return {"locked": locked, "reason": d.get("reason") if locked else None}


def lock(reason: str) -> dict:
    DISCIPLINE.write_text(json.dumps({"locked_on": datetime.now(timezone.utc).date().isoformat(), "reason": reason[:200]},
                                     ensure_ascii=False))
    return discipline()
