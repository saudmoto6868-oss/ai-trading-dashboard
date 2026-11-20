"""Portfolio / drawdown simulator for the weekly lab's detectors (Research Hub > Plateau & regime): "if I trade these together, how deep
does the account fall, and how often does it break?" Opportunity 3 in docs/decisions/2026-11-20-opportunities.md.

Two data modes, always named on screen:
  * real    data/lab_trades.json (written by strategy_lab.py since 2026-11-20): every lab trade with its signal time, replayed in time
            order, so losses that cluster on the same days stay together. Drawdown range = block bootstrap (blocks of BLOCK trades keep
            the clustering).
  * approx  only the averages in data/strategy_lab.json exist: each detector's trades are rebuilt as wins at +RR (lab win %) and losses
            at the value that reproduces the lab avg R, then shuffled. Assumes detectors are INDEPENDENT, so it understates drawdowns.
Every trade risks `risk` of the current equity and pays COST_R (0.10 R, the lab's planning cost). Overlapping positions are not capped
(each trade is sized on the equity before it). Past candle-based lab trades: a description, not a forecast or advice.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from modules.lab_shared import MIN_N, t
from modules.mc_journal import mc_summary

TRADES_PATH = Path(__file__).resolve().parent.parent / "data" / "lab_trades.json"
COST_R = 0.10   # same planning cost as the lab (strategy_lab.COST_R)
RR = 1.5        # lab default target (strategy_lab.RR); real mode reads it from the file
BLOCK = 10


def load_trades(path: Path = TRADES_PATH) -> dict | None:
    try:
        d = json.loads(Path(path).read_text())
        return d if d.get("trades") else None
    except Exception:
        return None


def approx_series(row: dict, rr: float = RR, seed: int = 0) -> list[float]:
    """R of each trade rebuilt from one aggregate lab row: round(n * win%) wins at +rr, the rest at the loss value that keeps avgR."""
    n, w, avg = int(row.get("n") or 0), (row.get("win") or 0) / 100.0, row.get("avgR")
    if n < 1 or avg is None:
        return []
    k = int(round(n * w))
    loss = (avg * n - k * rr) / (n - k) if n > k else 0.0
    rs = np.array([rr] * k + [max(-1.0, min(rr, loss))] * (n - k), float)
    np.random.default_rng(seed).shuffle(rs)
    return rs.tolist()


def portfolio_r(keys: list[str], trades: dict | None, rows: list[dict], oos_only: bool = False, seed: int = 0) -> dict:
    """-> {'mode': 'real'|'approx', 'r': [R per trade in replay order], 'per_key': {key: n}, 'missing': [keys with no data]}."""
    if trades:
        seq, per, miss = [], {}, []
        for k in keys:
            tr = [x for x in trades["trades"].get(k, []) if not oos_only or x[3]]
            if not tr:
                miss.append(k)
            per[k] = len(tr)
            seq += [(x[0], x[2]) for x in tr]
        seq.sort(key=lambda x: x[0])
        return {"mode": "real", "r": [r for _, r in seq], "per_key": per, "missing": miss}
    by = {r["key"]: r for r in rows if r.get("tf") == "all" and r.get("side") == "all"}
    parts, per, miss = [], {}, []
    for i, k in enumerate(keys):
        s = approx_series(by.get(k, {}), RR, seed + i)
        if not s:
            miss.append(k)
        per[k] = len(s)
        parts += s
    rng = np.random.default_rng(seed)
    parts = np.asarray(parts, float)
    rng.shuffle(parts)
    return {"mode": "approx", "r": parts.tolist(), "per_key": per, "missing": miss}


def equity_stats(r_list, risk: float, cost_r: float = COST_R) -> dict:
    """Compound the R series at `risk` of equity per trade (net of cost_r). -> equity curve + max drawdown, worst losing streak, final."""
    r = np.asarray(r_list, float)
    if r.size == 0:
        return {"n": 0}
    ret = risk * (r - cost_r)
    eq = np.cumprod(1.0 + ret)
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
    dd = 1.0 - eq / peak
    streak = best = 0
    for x in r - cost_r:
        streak = streak + 1 if x < 0 else 0
        best = max(best, streak)
    return {"n": int(r.size), "returns": ret, "equity": eq, "final": float(eq[-1]), "max_dd": float(dd.max()),
            "loss_streak": int(best), "net_r_per_trade": float((r - cost_r).mean())}


def block_dd(returns, n_paths: int = 2000, block: int = BLOCK, seed: int = 0) -> dict:
    """Max-drawdown range of the same trades redrawn in blocks of `block` (keeps clusters of losses). -> p50 / p95 max drawdown."""
    x = np.asarray(returns, float)
    n = x.size
    if n < 2 * block:
        return {}
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, size=(n_paths, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n_paths, -1)[:, :n]
    eq = np.cumprod(1.0 + x[idx], axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((n_paths, 1)), eq], axis=1), axis=1)[:, 1:]
    mdd = (1.0 - eq / peak).max(axis=1)
    return {"dd_p50": float(np.percentile(mdd, 50)), "dd_p95": float(np.percentile(mdd, 95))}


def simulate(keys, trades, rows, risk: float = 0.01, oos_only: bool = False, ruin_dd: float = 0.20, seed: int = 7) -> dict:
    p = portfolio_r(list(keys), trades, rows, oos_only=oos_only, seed=seed)
    st_ = equity_stats(p["r"], risk)
    out = {**p, **{k: v for k, v in st_.items() if k not in ("returns",)}}
    if st_.get("n", 0) >= 2:
        mc = mc_summary(st_["returns"], ruin_dd=ruin_dd, seed=seed)
        out.update({"ruin": mc.get("ruin"), "p_value": mc.get("p_value"), "final_p5": mc.get("final_p5"), "final_p95": mc.get("final_p95"),
                    "verdict": mc.get("verdict")}, **block_dd(st_["returns"], seed=seed))
    return out


def render(st=None, L=None) -> None:
    """Research Hub part: pick detectors, risk per trade, see the account path and how deep it can fall."""
    import pandas as pd
    if st is None:
        import streamlit as st
    from modules.lab_shared import _all_rows
    from modules.quant_robustness import build_matrix

    st.subheader(t("محاكي المحفظة والـ drawdown — صفقات المختبر", "Portfolio & drawdown simulator - lab trades"))
    rows = _all_rows()
    mx = build_matrix(rows)
    if not mx:
        st.info(t("مفيش بيانات مختبر (data/strategy_lab.json).", "No lab data (data/strategy_lab.json)."))
        return
    trades = load_trades()
    if trades:
        st.caption(t("بيانات حقيقية: كل صفقة من المختبر بوقتها (data/lab_trades.json)، بنفس الترتيب اللي حصلت بيه.",
                     "Real data: every lab trade with its time (data/lab_trades.json), replayed in the order it happened."))
    else:
        st.warning(t("تقدير: ملف الصفقات (data/lab_trades.json) لسه مااتعملش، هيتعمل في تشغيل المختبر الأسبوعي الجاي. "
                     "الصفقات هنا متعادة البناء من نسبة النجاح ومتوسط R، والاستراتيجيات معتبرة مستقلة عن بعض، فالـ drawdown الحقيقي غالبًا أكبر.",
                     "Approximation: the trades file (data/lab_trades.json) does not exist yet; the next weekly lab run writes it. "
                     "Trades here are rebuilt from win % and avg R, and detectors are treated as independent, so the real drawdown is likely deeper."))
    default = [e["key"] for e in mx if e["survives_trend"]][:5] or [mx[0]["key"]]
    c1, c2, c3 = st.columns([3, 1, 1])
    keys = c1.multiselect(t("الاستراتيجيات", "Detectors"), [e["key"] for e in mx], default=default, key="pf_keys")
    risk = c2.number_input(t("مخاطرة الصفقة %", "Risk per trade %"), 0.1, 5.0, 1.0, 0.1, key="pf_risk") / 100
    ruin = c3.number_input(t("حد الانهيار % من القمة", "Ruin = drop from peak %"), 5, 60, 20, 5, key="pf_ruin") / 100
    oos = st.checkbox(t("خارج العينة بس (النص التاني من البيانات)", "Out-of-sample only (second half of the data)"), key="pf_oos", disabled=not trades)
    if not keys:
        st.info(t("اختار استراتيجية واحدة على الأقل.", "Pick at least one detector."))
        return
    res = simulate(keys, trades, rows, risk=risk, oos_only=oos and bool(trades), ruin_dd=ruin)
    if res.get("n", 0) < 2:
        st.info(t("مفيش صفقات كفاية للاستراتيجيات دي.", "Not enough trades for these detectors."))
        return
    m = st.columns(4)
    m[0].metric(t("صفقات", "Trades"), res["n"])
    m[1].metric(t("أقصى نزول (الترتيب ده)", "Max drawdown (this order)"), f"{res['max_dd'] * 100:.1f}%")
    m[2].metric(t("أقصى نزول 50% / 95%", "Max drawdown 50% / 95%"),
                f"{res['dd_p50'] * 100:.1f}% / {res['dd_p95'] * 100:.1f}%" if "dd_p50" in res else "—")
    m[3].metric(t("احتمال الانهيار", "Ruin probability"), f"{res['ruin'] * 100:.1f}%" if res.get("ruin") is not None else "—")
    m = st.columns(4)
    m[0].metric(t("صافي R للصفقة", "Net R per trade"), f"{res['net_r_per_trade']:+.3f}")
    m[1].metric(t("رصيد النهاية (x)", "Final equity (x)"), f"{res['final']:.2f}")
    m[2].metric(t("أطول سلسلة خسارة", "Longest losing streak"), res["loss_streak"])
    m[3].metric("P-value", f"{res['p_value']:.3f}" if res.get("p_value") is not None else "—")
    st.line_chart(pd.Series(res["equity"], name=t("الرصيد", "equity")))
    if res["n"] < MIN_N:
        st.warning(t(f"أقل من {MIN_N} صفقة = مش دليل.", f"Under {MIN_N} trades = not evidence."))
    if res["missing"]:
        st.caption(t("من غير صفقات: ", "No trades for: ") + ", ".join(res["missing"]))
    st.caption(t(f"كل صفقة بتخاطر بـ {risk * 100:.1f}% من الرصيد وقتها، بعد خصم {COST_R}R تكلفة. الصفقات المتداخلة مش متحدودة. "
                 f"مدى الـ drawdown من إعادة سحب الصفقات في بلوكات من {BLOCK} صفقات (بيحافظ على تجمع الخساير). وصف لصفقات ماضية على شموع، مش توقع ولا نصيحة.",
                 f"Each trade risks {risk * 100:.1f}% of the equity at the time, after a {COST_R}R cost. Overlapping positions are not capped. "
                 f"The drawdown range redraws the trades in blocks of {BLOCK} (keeps clusters of losses). Past candle-based lab trades, not a forecast or advice."))
