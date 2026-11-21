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


# ---------------------------------------------------------------- options added 2026-11-16 (owner: best spot options)
# Evidence used to choose them: platform setup lab (data/spot_setup_evidence.json) + two 3-year backtests of the
# 200-day rule (BTC +16% vs hold +81%, ETH +3% vs hold -6%, 14 and 10 trades: not evidence). So the 200-day line is
# shown as a MODE reading only, never as a buy / sell system.
BUY_STEPS = [(-10.0, 30.0), (-20.0, 30.0), (-30.0, 40.0)]      # (% below price, % of the reserve)
SELL_STEPS = [(25.0, 25.0), (50.0, 25.0), (100.0, 25.0)]       # (% above average cost, % of the position); 25% is kept


def market_mode(fear_greed, price=None, sma200=None) -> dict:
    """Mode from the fear & greed index and BTC vs its 200-day average. dca_mult scales the weekly DCA; swing_ok gates swings."""
    fg = None if fear_greed in (None, "") else max(0.0, min(100.0, float(fear_greed)))
    above = None if not (_pos(price) and _pos(sma200)) else price > sma200
    mult = 1.0 if fg is None else 1.5 if fg < 25 else 0.5 if fg > 75 else 1.0
    if fg is not None and fg > 75:
        mode = "defend"        # greed: buy less, check the sell ladder
    elif above is False or (fg is not None and fg < 25):
        mode = "accumulate"    # fear or below the 200-day line: DCA only, no swing trades
    else:
        mode = "normal"
    return {"mode": mode, "dca_mult": mult, "swing_ok": bool(above) and mode == "normal", "above_200d": above, "fear_greed": fg}


def buy_ladder(price: float, reserve: float, steps=None) -> list[dict]:
    """Limit buys below the market, funded by the reserve."""
    if not (_pos(price) and _pos(reserve)):
        return []
    out = []
    for drop, share in (steps or BUY_STEPS):
        p = price * (1 + drop / 100.0)
        usd = reserve * share / 100.0
        out.append({"drop_pct": drop, "price": round(p, 8), "usd": round(usd, 2), "qty": round(usd / p, 8)})
    return out


def sell_ladder(avg_cost: float, qty: float, steps=None) -> list[dict]:
    """Limit sells above the average cost. What is left after the last step stays as the long-term part."""
    if not (_pos(avg_cost) and _pos(qty)):
        return []
    out = []
    for gain, share in (steps or SELL_STEPS):
        p = avg_cost * (1 + gain / 100.0)
        q = qty * share / 100.0
        out.append({"gain_pct": gain, "price": round(p, 8), "qty": round(q, 8), "usd": round(p * q, 2)})
    return out


def rebalance(values: dict[str, float], targets: dict[str, float], band_pct: float = 5.0) -> list[dict]:
    """Per asset: current share, target share, and the USD to buy (+) or sell (-) when it is outside the band."""
    total = sum(_pos(v) for v in values.values())
    tsum = sum(_pos(v) for v in targets.values())
    if not total or not tsum:
        return []
    out = []
    for k in targets:
        cur = _pos(values.get(k, 0)) / total * 100.0
        tgt = _pos(targets[k]) / tsum * 100.0
        diff = tgt - cur
        out.append({"asset": k, "current_pct": round(cur, 1), "target_pct": round(tgt, 1),
                    "action_usd": round(diff / 100.0 * total, 2) if abs(diff) > band_pct else 0.0})
    return out


def breakeven_gain_pct(loss_pct: float) -> float | None:
    """Gain needed to get back to cost after a loss of loss_pct (positive number, e.g. 70 for -70%)."""
    l_ = _pos(loss_pct)
    if not l_ or l_ >= 100:
        return None
    return round(l_ / (100 - l_) * 100, 1)


def strategy_table(evidence: dict, min_n: int = 30) -> list[dict]:
    """The platform's own setup lab, ranked. Verdict rule of the lab: n >= 30 and t >= 3 = worked; t <= -3 = worse than normal."""
    rows = []
    for key, v in (evidence or {}).items():
        n, t = v.get("n") or 0, v.get("t")
        if n < min_n or t is None:
            continue
        verdict = "worked in the past" if t >= 3 else "promising, not enough" if t >= 2 else "worse than normal" if t <= -3 else "avoid (negative)" if t <= -2 else "no clear edge"
        sid, _, tf = key.partition("|")
        rows.append({"setup": sid, "tf": tf, "school": v.get("school"), "use as": v.get("side"), "n": n,
                     "avg %": round(v.get("mean_pct") or 0, 1), "normal %": round(v.get("base_pct") or 0, 1), "t": round(t, 1), "verdict": verdict})
    return sorted(rows, key=lambda r: -r["t"])


# spot strategies the owner can pick (2026-11-17): each one is a budget split + what it does. Evidence notes are in PROJECT_STATUS.
STRATEGIES = {
    "Core + swing (default)": {"split": {"dca": 60.0, "swing": 25.0, "reserve": 15.0},
                               "en": "Weekly DCA on BTC / ETH, a small swing part, a reserve for dips.",
                               "ar": "DCA أسبوعي على BTC و ETH، جزء صغير للسوينج، واحتياطي للنزول."},
    "DCA only": {"split": {"dca": 85.0, "swing": 0.0, "reserve": 15.0},
                 "en": "No trading: weekly buys with the fear tilt, reserve for the dip ladder. The simplest plan.",
                 "ar": "من غير تداول: شراء أسبوعي مع ميل الخوف، واحتياطي لسلم النزول. أبسط خطة."},
    "Dip accumulation": {"split": {"dca": 45.0, "swing": 0.0, "reserve": 55.0},
                         "en": "Smaller weekly buys, most of the money waits in limit orders 10 / 20 / 30% below the price.",
                         "ar": "شراء أسبوعي أصغر، ومعظم الفلوس مستنية في أوامر Limit تحت السعر بـ 10 / 20 / 30%."},
    "Value (200-week zone)": {"split": {"dca": 50.0, "swing": 0.0, "reserve": 50.0},
                              "en": "DCA plus extra buys only when price is near the 200-week average (the lab's best buy setup, t 1.7: promising, not proven).",
                              "ar": "DCA + شراء زيادة بس لما السعر يقرب من متوسط 200 أسبوع (أحسن إشارة شراء في المعمل، t 1.7: مشجعة مش مثبتة)."},
    "Swing focus": {"split": {"dca": 30.0, "swing": 55.0, "reserve": 15.0},
                    "en": "More money for swing trades. Highest risk here: no buy setup passed the lab, and swings are off in fear / below the 200-day line.",
                    "ar": "فلوس أكتر للسوينج. أعلى مخاطرة هنا: مفيش إشارة شراء عدّت المعمل، والسوينج مقفول في الخوف / تحت خط 200 يوم."},
    "Capital defence": {"split": {"dca": 25.0, "swing": 0.0, "reserve": 75.0},
                        "en": "Mostly cash. Small weekly buys, sell ladder active. For a falling market or after a loss streak.",
                        "ar": "معظمها كاش. شراء أسبوعي صغير، وسلم البيع شغال. لسوق نازل أو بعد سلسلة خساير."},
}


# ladder plan -> alerts (owner 2026-11-21): one buy now + limit buys lower, each coin split in equal parts
PLAN_2026_11_21 = {"date": "2026-11-21", "steps": [0.0, -10.0, -20.0], "reserve_usd": 350.0,
                   "coins": {"BTC": (56074.0, 1400.0), "ETH": (1552.0, 875.0), "SOL": (65.57, 350.0), "XRP": (0.873, 350.0), "ZEC": (696.6, 175.0)}}


def plan_ladder(coins: dict, steps=None) -> list[dict]:
    """coins: {asset: (start price, USD)} -> rows (asset, step %, price, usd, qty). USD is split equally over the steps;
    rounding goes to the last step so each coin adds up exactly."""
    steps = list(steps if steps is not None else PLAN_2026_11_21["steps"])
    out = []
    for asset, (p0, usd) in (coins or {}).items():
        if not (_pos(p0) and _pos(usd) and steps):
            continue
        part = round(_pos(usd) / len(steps))
        for i, s in enumerate(steps):
            u = part if i < len(steps) - 1 else round(_pos(usd) - part * (len(steps) - 1), 2)
            p = _pos(p0) * (1 + s / 100.0)
            nd = 2 if p >= 100 else 4 if p >= 1 else 6
            out.append({"asset": str(asset).upper(), "step_pct": s, "price": round(p, nd), "usd": u, "qty": round(u / p, 8)})
    return out
