"""Spot trade checklist + risk-based sizing (owner 2026-11-27: finish the plan with sizing, stops, and a checklist).

Pure functions. They read the output of spot_plan.plan() and never place or suggest an order by themselves.
Defaults are RULES OF THUMB chosen for safety, not results of any backtest: label them 'not evidence' in the UI.
  - risk per trade: 1% of equity (the full staged ladder filled, loss at the invalidation level)
  - max position: 25% of equity (so a tight stop cannot create a huge position)
  - reward / risk to the first target: at least 2
  - a stop wider than 20% below the average entry is refused (too wide to size sanely)
"""
from __future__ import annotations

from modules import spot_core as C

RISK_PCT = 0.01
MAX_POS_PCT = 0.25
MIN_RR = 2.0
MAX_STOP_PCT = 0.20
BUY_ACTIONS = ("accumulate", "hold_buy_dips")   # spot_plan.plan() actions that mean 'buy' (take_profit_wait / wait do not)
CHASE_PCT = 0.03          # price more than 3% above the first buy level = wait for the level, do not chase


def size_plan(equity: float, avg_entry: float, invalidation: float, risk_pct: float = RISK_PCT,
              max_pos_pct: float = MAX_POS_PCT) -> dict:
    """Total USD for the whole ladder so that a fill-all loss at the invalidation is at most risk_pct of equity.
    Capped at max_pos_pct of equity. Returns {ok, total_usd, risk_usd, stop_pct, why}."""
    if not equity or equity <= 0 or not avg_entry or not invalidation or invalidation >= avg_entry:
        return {"ok": False, "total_usd": 0.0, "risk_usd": 0.0, "stop_pct": None, "why": "بيانات الحجم ناقصة أو الإلغاء فوق الدخول"}
    stop_pct = (avg_entry - invalidation) / avg_entry
    if stop_pct > MAX_STOP_PCT:
        return {"ok": False, "total_usd": 0.0, "risk_usd": 0.0, "stop_pct": stop_pct, "why": f"الوقف أبعد من {MAX_STOP_PCT:.0%} - الحجم هيطلع صغير جدًا، اختار مكان أقرب أو اتجاهل الصفقة"}
    risk_usd = equity * risk_pct
    total = min(risk_usd / stop_pct, equity * max_pos_pct)
    capped = total < risk_usd / stop_pct
    return {"ok": True, "total_usd": total, "risk_usd": total * stop_pct, "stop_pct": stop_pct,
            "why": "الحد الأقصى للمركز اتطبق" if capped else "الحجم من المخاطرة"}


def checklist(p: dict, equity: float | None = None, budget: float | None = None) -> dict:
    """p = spot_plan.plan() result. Returns {items: [{id, ar, ok: True|False|None, why}], passed, failed, unknown, verdict}.
    ok None = cannot check from the data (shown as unknown, never as a pass)."""
    items = []

    def add(i, ar, ok, why=""):
        items.append({"id": i, "ar": ar, "ok": ok, "why": why})

    rows = p.get("rows") or []
    avail = sum(1 for r in rows if r.get("available"))
    px = p.get("price")
    buys = sorted([float(x) for x in (p.get("buys") or []) if x], reverse=True)
    sells = sorted([float(x) for x in (p.get("sells") or []) if x])
    inv = p.get("invalidation")

    add("data", "سعر حي ومعاه الفريمات الثلاثة (يوم / أسبوع / شهر)", bool(px) and avail == 3,
        f"فريمات متاحة {avail}/3")
    add("levels", "فيه مستويات شراء محددة (سلم)", bool(buys), "" if buys else "مفيش مستوى شراء - متدخلش")
    add("invalidation", "فيه نقطة إلغاء تحت السلم", bool(inv and buys and inv < min(buys)),
        "" if inv else "مفيش إلغاء")
    avg = C.ladder_avg(C.ladder(buys, 1.0)) if buys else None
    add("chase", "السعر مش بعيد فوق أول مستوى شراء (منطاردش)",
        (px <= buys[0] * (1 + CHASE_PCT)) if (px and buys) else None,
        "" if not buys else f"السعر {(px / buys[0] - 1):+.1%} من أول مستوى" if px else "")
    if avg and inv and sells:
        rr = (sells[0] - avg) / (avg - inv) if avg > inv else None
        add("rr", f"العائد للهدف الأول ≥ {MIN_RR:g} ضعف الخطر", (rr is not None and rr >= MIN_RR) if rr is not None else None,
            f"R/R {rr:.2f}" if rr is not None else "")
    else:
        add("rr", f"العائد للهدف الأول ≥ {MIN_RR:g} ضعف الخطر", None, "محتاج سلم + إلغاء + هدف")
    if avg and inv and equity:
        sz = size_plan(equity, avg, inv)
        add("size", f"الخسارة لو اتملا السلم كله ≤ {f"{RISK_PCT:.0%}"} من الرأسمال", sz["ok"] and sz["risk_usd"] <= equity * RISK_PCT + 1e-9,
            sz["why"])
        if budget is not None and sz["ok"]:
            add("budget", "الميزانية اللي في الشاشة ≤ الحجم المسموح", budget <= sz["total_usd"] + 1e-9,
                f"المسموح ${sz['total_usd']:,.0f}")
    else:
        add("size", f"الخسارة لو اتملا السلم كله ≤ {f"{RISK_PCT:.0%}"} من الرأسمال", None, "محتاج رأس المال (equity)")
    add("plan_side", "الخطة بتقول شراء (تجميع أو شراء عند المستويات)",
        (p.get("action") in BUY_ACTIONS) if p.get("action") else None, f"الـ action: {p.get('action')}")
    passed = sum(1 for i in items if i["ok"] is True)
    failed = sum(1 for i in items if i["ok"] is False)
    unknown = sum(1 for i in items if i["ok"] is None)
    verdict = "ممنوع الدخول" if failed else ("ناقص بيانات" if unknown else "كل الشروط متحققة (ده مش ضمان ربح)")
    return {"items": items, "passed": passed, "failed": failed, "unknown": unknown, "verdict": verdict}


def take_profit_plan(total_units: float, sells: list[float]) -> list[dict]:
    """Ladder: sell 1/3 at T1, 1/3 at T2, rest trails under the last higher low (rule of thumb, not backtested)."""
    t = sorted(float(x) for x in sells if x)[:2]
    if not t:
        return []
    shares = [1 / 3, 1 / 3] if len(t) == 2 else [1 / 3]
    out = [{"target": px, "units": total_units * s, "note": "بيع جزء" if i < len(shares) else ""} for i, (px, s) in enumerate(zip(t, shares))]
    rest = total_units - sum(r["units"] for r in out)
    out.append({"target": None, "units": rest, "note": "الباقي بوقف متحرك تحت آخر قاع أعلى"})
    return out
