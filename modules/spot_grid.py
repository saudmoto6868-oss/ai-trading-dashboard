"""Spot > Crypto: a grid of OUR Workspace chart widgets (owner 2026-11-21: "the spot charts still have no tools, the filters are weak").

One thin filter line (search, sort, 24h move, how many charts, columns, height, timeframe), then one chart per coin. Under every chart:
numbered points - 1 = the coin's spot plan (buy 1 / buy 2 / targets / invalidation drawn as lines), then Elliott, harmonic, structure,
support / resistance (the chart's own indicators). ▾ opens the plan as text under the chart. Same radar mode of the chart app as the
Radar page (modules/ws/24f_radar.js). Suggestions only - nothing here places an order."""
from __future__ import annotations

import html
import json
import time
from concurrent.futures import ThreadPoolExecutor

import streamlit as st

SORTS = ["volume", "up", "down", "score"]


def _levels(p: dict) -> list[dict]:
    out = [{"p": x, "label": f"Buy {i + 1}", "color": "#f7b500"} for i, x in enumerate(p.get("buys") or [])]
    out += [{"p": x, "label": f"T{i + 1}", "color": "#0ecb81"} for i, x in enumerate(p.get("sells") or [])]
    if p.get("invalidation"):
        out.append({"p": p["invalidation"], "label": "Invalidation", "color": "#f6465d"})
    return out


def _info(base: str, p: dict, n, T) -> str:
    if not p.get("ok"):
        return html.escape(T("No spot plan for this coin (not enough candles).", "مفيش خطة سبوت للعملة دي (الشموع مش كفاية)."))
    row = lambda k, v: f"<div><span style='color:#8d93a0'>{html.escape(k)}:</span> <b dir='ltr'>{html.escape(str(v))}</b></div>"   # noqa: E731
    return ("<b>" + html.escape(base) + " · " + html.escape(T("spot plan", "خطة السبوت")) + "</b><hr>"
            + row(T("Score", "الدرجة"), p.get("score")) + row(T("Action", "الإجراء"), p.get("action", "—"))
            + "".join(row(f"{T('Buy', 'شراء')} {i + 1}", n(x)) for i, x in enumerate(p.get("buys") or []))
            + "".join(row(f"T{i + 1}", n(x)) for i, x in enumerate(p.get("sells") or []))
            + row(T("Invalidation (weekly close below)", "الإلغاء (قفلة أسبوعية تحت)"), n(p.get("invalidation")))
            + "<hr><span style='color:#8d93a0'>" + html.escape(T("A plan from the daily / weekly / monthly candles, not advice. Buy 1/2 = staged buys (30/30/40).",
                                                                 "خطة من شموع اليوم / الأسبوع / الشهر، مش توصية. شراء 1/2 = شراء على دفعات (30/30/40).")) + "</span>")


def points(p: dict) -> list[dict]:
    """Points under a coin's chart: the plan first (opens by itself), then the chart's main tools."""
    pts = [{"label": "Plan", "tip": "Buy / targets / invalidation", "dir": "long", "kind": "levels", "levels": _levels(p)}] if p.get("ok") and _levels(p) else []
    pts += [{"label": "Elliott", "kind": "ind", "ind": "ew"}, {"label": "Harmonic", "kind": "ind", "ind": "harm"},
            {"label": "Structure (MSB / OB)", "kind": "ind", "ind": "msb"}, {"label": "S/R", "kind": "sr"}, {"label": "VWAP", "kind": "ind", "ind": "vwap"}]
    return pts


def render(cr: list, plan_for, n, T, lang: str = "en") -> None:
    """cr = spot_data.crypto_tickers() rows; plan_for = spot_page._plan_for (cached); n = number format; T = (en, ar) text."""
    ss = st.session_state
    for k, v in (("spg_sort", "volume"), ("spg_n", 12), ("spg_cols", 4), ("spg_h", 360), ("spg_tf", "1d"), ("spg_min", 0)):
        ss.setdefault(k, v)
    c = st.columns([1.4, 1.1, 0.9, 0.7, 0.8, 0.7, 0.7], vertical_alignment="center")
    q = c[0].text_input(T("Search", "بحث"), key="spg_q", placeholder=T("Search coin", "ابحث عن عملة"), label_visibility="collapsed").strip().upper()
    c[1].selectbox(T("Sort", "ترتيب"), SORTS, key="spg_sort", label_visibility="collapsed",
                   format_func=lambda s: {"volume": T("Biggest volume", "الأكبر فوليوم"), "up": T("Top gainers 24h", "الأكثر صعود 24س"),
                                          "down": T("Top losers 24h", "الأكثر هبوط 24س"), "score": T("Best plan score", "أعلى درجة خطة")}[s])
    c[2].selectbox(T("24h move", "حركة 24س"), [0, 2, 5, 10], key="spg_min", label_visibility="collapsed", format_func=lambda m: T("Any move", "أي حركة") if not m else f"|24h| ≥ {m}%")
    c[3].number_input(T("Charts", "الشارتات"), 1, 40, key="spg_n", label_visibility="collapsed", help=T("How many charts", "عدد الشارتات"))
    c[4].selectbox(T("Columns", "الأعمدة"), [1, 2, 3, 4, 5, 6, 8], key="spg_cols", label_visibility="collapsed", format_func=lambda x: f"{x} " + T("per row", "في الصف"))
    c[5].selectbox(T("Height", "الارتفاع"), [260, 300, 360, 420, 500, 600], key="spg_h", label_visibility="collapsed", format_func=lambda x: f"{x}px")
    c[6].selectbox("TF", ["15m", "1h", "4h", "1d", "1w"], key="spg_tf", label_visibility="collapsed")
    rows = [r for r in cr if (not q or q in r["base"]) and (not ss["spg_min"] or (r.get("chg24") is not None and abs(r["chg24"]) >= ss["spg_min"]))]
    srt = ss["spg_sort"]
    if srt in ("up", "down"):
        rows.sort(key=lambda r: -(r.get("chg24") or 0) if srt == "up" else (r.get("chg24") or 0))
    want = int(ss["spg_n"])
    pool = rows[:max(want, 40)] if srt == "score" else rows[:want]   # score: rank the 40 biggest that pass the filters
    with st.spinner(T("Building the spot plans...", "بنجهز خطط السبوت...")):
        with ThreadPoolExecutor(6) as ex:
            plans = dict(zip([r["base"] for r in pool], ex.map(lambda r: _safe(plan_for, r["sym"]), pool)))
    if srt == "score":
        pool.sort(key=lambda r: -(plans[r["base"]].get("score") or -1))
    pool = pool[:want]
    if not pool:
        st.info(T("No coin matches these filters.", "مفيش عملة على الفلاتر دي."))
        return
    items = [{"sym": r["sym"], "tf": ss["spg_tf"], "tag": (f"{plans[r['base']].get('score')} · {plans[r['base']].get('action', '')}" if plans[r["base"]].get("ok") else ""),
              "info": _info(r["base"], plans[r["base"]], n, T), "pts": points(plans[r["base"]])} for r in pool]
    cols, h = int(ss["spg_cols"]), int(ss["spg_h"])
    st.caption(f"{len(pool)} / {len(rows)} " + T("coins · tag = plan score · action. Point 1 draws the plan on the chart; ▾ = the plan as text. Suggestions only.",
                                                   "عملة · العلامة = درجة الخطة · الإجراء. النقطة 1 بترسم الخطة على الشارت؛ ▾ = الخطة مكتوبة. اقتراحات بس."))
    from modules.workspace import build_workspace_html
    key = json.dumps([items, cols, h, lang], sort_keys=True, default=str)
    last = ss.get("spg_doc")
    if last and last[0] == key and time.time() - last[2] < 600:
        doc = last[1]
    else:
        doc = build_workspace_html([it["sym"] for it in items], None, lang, asset_cls="Crypto", solo="radar", radar={"cols": cols, "h": h, "items": items})
        ss["spg_doc"] = (key, doc, time.time())
    st.iframe(doc, height=-(-len(items) // cols) * h + 40, alt="Spot charts")   # + the all-charts bar


def _safe(fn, sym):
    try:
        return fn(sym) or {}
    except Exception:   # one coin's data problem must not break the grid
        return {}
