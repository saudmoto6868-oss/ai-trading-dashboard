"""Radar Agent Control Room.

The agents are transparent, deterministic specialist passes over the Radar scan.
They do not claim to be LLMs or to read a live DOM unless those fields are present.
"""
from __future__ import annotations

import html
from collections import Counter


AGENTS = [
    ("market_scout", "Market Scout", "رادار السوق", "radar", "#36D6CE"),
    ("chart_reader", "Chart Reader", "قارئ الشارت", "chart-no-axes-combined", "#D8B46A"),
    ("flow_analyst", "Flow Analyst", "محلل تدفق الأوامر", "waves", "#36D6CE"),
    ("liquidity_sentinel", "Liquidity Sentinel", "حارس السيولة", "scan-eye", "#B99AF7"),
    ("risk_guardian", "Risk Guardian", "مراجع المخاطر", "shield-check", "#F06464"),
    ("research_tutor", "Research Tutor", "مرشد البحث", "graduation-cap", "#36C98F"),
]


def analyse(data: dict, tf: str = "1h") -> dict:
    """Build an auditable work trace from the current Radar scan result."""
    rows = list((data or {}).items())
    valid = [(s, d) for s, d in rows if isinstance(d, dict)]
    up = [(s, d) for s, d in valid if str(d.get("trend", "")).lower() == "up"]
    down = [(s, d) for s, d in valid if str(d.get("trend", "")).lower() == "down"]
    regimes = Counter(str(d.get("regime")) for _, d in valid if d.get("regime"))
    ranked = sorted(valid, key=lambda x: (len(x[1].get("flags") or []), float(x[1].get("volx") or 0)), reverse=True)
    top = ranked[:5]
    flow_rows = []
    try:
        from modules import flow_log
        flow_rows = flow_log.load()[-200:]
    except Exception:
        flow_rows = []
    flow_by_symbol = {}
    for row in flow_rows:
        if row.get("sym"):
            flow_by_symbol[row["sym"]] = row
    flow_ready = bool(flow_by_symbol) or any(any(k in d for k in ("cvd", "delta", "ofi", "imbalance", "open_interest")) for _, d in valid)
    book_ready = any(any(k in d for k in ("bids", "asks", "order_book", "depth")) for _, d in valid)
    stale = sum(1 for _, d in valid if d.get("ts") is None)
    return {
        "tf": tf, "count": len(valid), "up": len(up), "down": len(down),
        "neutral": max(0, len(valid) - len(up) - len(down)),
        "regimes": regimes, "top": top, "flow_ready": flow_ready, "book_ready": book_ready, "flow_rows": flow_by_symbol,
        "missing_ts": stale,
        "steps": [
            {"agent": "market_scout", "title": "١. مسح السوق والاتجاه", "state": "done" if valid else "blocked",
             "detail": f"تم فحص {len(valid)} رمز على {tf}: {len(up)} صاعد، {len(down)} هابط، {max(0, len(valid)-len(up)-len(down))} محايد."},
            {"agent": "chart_reader", "title": "٢. مراجعة الشارت والإشارات", "state": "done" if valid else "blocked",
             "detail": "تم ترتيب الرموز حسب عدد إشارات الرادار والحجم النسبي. أعلى المرشحين: " + (", ".join(s for s, _ in top[:3]) if top else "لا توجد بيانات كافية") + "."},
            {"agent": "flow_analyst", "title": "٣. فتح فحص تدفق الأوامر", "state": "done" if flow_ready else "limited",
             "detail": (f"تمت قراءة سجل Flow Collector لعدد {len(flow_by_symbol)} رمز. هذه لقطات مسجلة وليست بالضرورة بثاً حياً؛ راجع التوقيت والمصدر قبل استخدامها." if flow_by_symbol else "بيانات Order Flow الحية غير مرفقة بنتيجة Radar الحالية، ولا يوجد سجل Collector محفوظ. لم يتم اختلاق CVD أو Delta؛ يلزم ربط مصدر Workspace/Exchange قبل إصدار تأكيد.")},
            {"agent": "liquidity_sentinel", "title": "٤. فحص دفتر الأوامر والسيولة", "state": "done" if book_ready else "limited",
             "detail": "بيانات دفتر الأوامر موجودة في سياق الفحص." if book_ready else "لا توجد لقطة DOM صالحة في سياق الرادار الحالي. لا يمكن تأكيد جدار سيولة أو امتصاص من الشموع وحدها."},
            {"agent": "risk_guardian", "title": "٥. المراجع المستقل: تأكيد أم انتظار؟", "state": "done" if valid and flow_ready and book_ready else "limited" if valid else "blocked",
             "detail": (f"تمت مراجعة {len(valid)} نتيجة ووجود Flow وDOM. المراجعة لا تعني اعتماد صفقة؛ يلزم فحص شروط الدخول والإبطال والتكلفة." if valid and flow_ready and book_ready else f"قرار المراجع: انتظار / غير مؤكد. نتائج الشارت وحدها لا تكفي؛ Flow={'متاح' if flow_ready else 'غير متاح'}، DOM={'متاح' if book_ready else 'غير متاح'}، و{stale} نتيجة لا تحمل توقيتاً واضحاً.")},
            {"agent": "research_tutor", "title": "٦. ربط النتيجة بالدليل والأكاديمية", "state": "done",
             "detail": "النتائج تُعرض كمرشحات من الرادار؛ لا تُرفع إلى دليل إحصائي قبل مراجعة Lab وشرط العينة والتكاليف."},
        ],
    }


def _css():
    return """
<style>
.rac-wrap{background:linear-gradient(135deg,#0b1117,#101a21 58%,#0b1117);border:1px solid #263943;border-radius:14px;padding:12px;margin:8px 0 14px;color:#e7ecef}
.rac-head{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;border-bottom:1px solid #263943;padding-bottom:9px;margin-bottom:10px}
.rac-brand{font-size:13px;font-weight:800;letter-spacing:.12em;color:#d8b46a}
.rac-sub{font-size:10px;color:#91a2ad}
.rac-live{font-size:10px;color:#36d6ce;border:1px solid #235e61;border-radius:20px;padding:4px 8px}
.rac-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:7px}
.rac-agent{background:#121d25;border:1px solid #263943;border-radius:10px;padding:8px;min-width:0;position:relative;overflow:hidden}
.rac-agent.active{border-color:#36d6ce;box-shadow:0 0 0 1px #36d6ce33,0 0 18px #36d6ce16}
.rac-agent .name{font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rac-agent .ar{font-size:10px;color:#93a1aa;margin-top:3px}
.rac-orb{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:1px solid var(--agent);color:var(--agent);margin-bottom:7px;box-shadow:0 0 12px color-mix(in srgb,var(--agent) 18%,transparent)}
.rac-orb:after{content:'';position:absolute;width:28px;height:28px;border:1px solid var(--agent);border-radius:50%;opacity:.35;animation:rac-pulse 2.4s ease-out infinite}
.rac-state{font-size:9px;color:var(--agent);margin-top:6px}
.rac-track{height:3px;background:#263943;border-radius:4px;margin-top:7px;overflow:hidden}
.rac-track i{display:block;height:100%;width:100%;background:var(--agent);transform-origin:left;animation:rac-scan 2.8s ease-in-out infinite}
.rac-step{display:flex;gap:9px;padding:8px 0;border-bottom:1px solid #202e37}
.rac-step:last-child{border-bottom:0}
.rac-num{width:23px;height:23px;flex:0 0 23px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#17242c;color:#d8b46a;font-size:10px;font-weight:800;border:1px solid #3b4a50}
.rac-step-title{font-size:11px;font-weight:700;color:#e7ecef}
.rac-step-detail{font-size:10px;line-height:1.6;color:#9aaab3;margin-top:3px}
.rac-ok{color:#36c98f}.rac-warn{color:#e8a85b}.rac-bad{color:#f06464}
.rac-terminal{background:#080d11;border:1px solid #263943;border-radius:10px;padding:10px;font-family:ui-monospace,monospace}
.rac-log{font-size:10px;line-height:1.8;color:#b8c6ce;border-bottom:1px solid #17242c;padding:3px 0}
.rac-log b{color:#36d6ce}
.rac-mini{background:#101a21;border:1px solid #263943;border-radius:9px;padding:8px}
.rac-mini label{font-size:9px;color:#93a1aa;display:block}
.rac-mini strong{font-size:17px;color:#e7ecef}
.rac-news{background:#171c1b;border-left:3px solid #d8b46a;border-radius:6px;padding:8px;margin:5px 0}
@keyframes rac-pulse{0%{transform:scale(.8);opacity:.55}100%{transform:scale(1.7);opacity:0}}
@keyframes rac-scan{0%,100%{transform:scaleX(.2);opacity:.45}50%{transform:scaleX(1);opacity:1}}
@media(max-width:900px){.rac-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:520px){.rac-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(prefers-reduced-motion:reduce){.rac-orb:after,.rac-track i{animation:none!important}}
</style>
"""


def render(data: dict, tf: str = "1h", news_items: list | None = None):
    """Render the optional agent room and transparent terminal inside existing Radar."""
    import streamlit as st
    import pandas as pd

    result = analyse(data, tf)
    news_items = news_items if news_items is not None else st.session_state.get("rac_news_cache")
    st.markdown(_css(), unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([2.0, 1, 1, 1, 1.1])
    with c1:
        st.markdown("**◉ RADAR AGENT CONTROL ROOM**  <span style='color:#93a1aa;font-size:10px'>فريق التحليل والمراجعة</span>", unsafe_allow_html=True)
    with c2:
        terminal = st.toggle("إظهار التيرمينال", value=True, key="rac_terminal")
    with c3:
        show_news = st.toggle("الأخبار", value=True, key="rac_news")
    with c4:
        show_agents = st.toggle("فريق الوكلاء", value=True, key="rac_agents")
    with c5:
        rerun_round = st.button("إعادة الجولة", key="rac_run_round", use_container_width=True)
    if rerun_round:
        st.session_state["rac_round_id"] = int(st.session_state.get("rac_round_id", 0)) + 1
        st.rerun()
    if not show_agents:
        st.caption("تم إخفاء غرفة الوكلاء. فعّل الخيار لإظهار فريق التحليل وسجل خطواته.")
        if show_news:
            _render_news(st, news_items)
        return

    st.caption(f"جولة التحليل رقم {int(st.session_state.get('rac_round_id', 1))} · نتائج مبنية على بيانات Radar الحالية، وليست أوامر تداول.")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("الرموز المفحوصة", result["count"])
    k2.metric("صاعد", result["up"])
    k3.metric("هابط", result["down"])
    k4.metric("سجل Flow", len(result["flow_rows"]))

    selected = st.session_state.get("rac_agent_selected", "market_scout")
    cards = []
    for key, en, ar, icon, color in AGENTS:
        active = key == selected
        cards.append(
            f"<div class='rac-agent {'active' if active else ''}' style='--agent:{color}'>"
            f"<div class='rac-orb'>✦</div><div class='name'>{html.escape(en)}</div>"
            f"<div class='ar'>{html.escape(ar)}</div><div class='rac-state'>{'● نشط في العرض' if active else '○ جاهز للمراجعة'}</div>"
            f"<div class='rac-track'><i></i></div></div>"
        )
    st.markdown("<div class='rac-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)
    labels = {a[0]: a[2] for a in AGENTS}
    choices = [a[0] for a in AGENTS]
    selected = st.selectbox("اختر الوكيل لعرض مهمته", choices, format_func=lambda k: labels[k], key="rac_agent_selected")
    step_cols = st.columns([1.25, 1])
    with step_cols[0]:
        st.markdown("**مسار العمل · خطوة بخطوة**")
        for i, step in enumerate(result["steps"], 1):
            state_cls = "rac-ok" if step["state"] == "done" else "rac-warn" if step["state"] == "limited" else "rac-bad"
            st.markdown(
                f"<div class='rac-step'><div class='rac-num'>{i}</div><div><div class='rac-step-title'>{html.escape(step['title'])} "
                f"<span class='{state_cls}'>· {'تم' if step['state']=='done' else 'محدود' if step['state']=='limited' else 'متوقف'}</span></div>"
                f"<div class='rac-step-detail'>{html.escape(step['detail'])}</div></div></div>",
                unsafe_allow_html=True,
            )
    with step_cols[1]:
        st.markdown("**مكتب الوكيل المختار**")
        selected_step = next((x for x in result["steps"] if x["agent"] == selected), None)
        agent = next(x for x in AGENTS if x[0] == selected)
        st.markdown(
            f"<div class='rac-mini'><div style='font-size:10px;color:{agent[4]}'>{html.escape(agent[1])}</div>"
            f"<div style='font-size:15px;font-weight:800;margin:6px 0'>{html.escape(agent[2])}</div>"
            f"<div style='font-size:11px;line-height:1.7;color:#a8b7bf'>{html.escape(selected_step['detail'] if selected_step else '')}</div></div>",
            unsafe_allow_html=True,
        )
        if result["top"]:
            st.markdown("**الشارتات تحت المراجعة**")
            for sym, d in result["top"][:3]:
                st.caption(f"{sym} · {d.get('trend','—')} · RSI {d.get('rsi','—')} · Vol ×{d.get('volx','—')}")
                svg = d.get("svg")
                if svg and isinstance(svg, str) and svg.startswith("data:image/svg+xml"):
                    st.markdown(f"<img src='{svg}' style='width:100%;border-radius:5px;border:1px solid #263943'/>", unsafe_allow_html=True)
        if result["flow_rows"]:
            flow_view = []
            for sym, row in list(result["flow_rows"].items())[:8]:
                flow_view.append({"الرمز": sym, "Mid": row.get("mid"), "CVD": row.get("cvd"), "OFI": row.get("ofi"), "Imbalance": row.get("imb"), "Spread bps": row.get("spread_bps"), "سرعة الصفقات": row.get("speed"), "وقت السجل": row.get("t")})
            st.markdown("**قراءة Flow Collector المحفوظة**")
            st.dataframe(pd.DataFrame(flow_view), hide_index=True, use_container_width=True)
            st.caption("السجل قد يكون تاريخياً أو متأخراً؛ لا يُعرض على أنه بث مباشر.")
        elif not result["flow_ready"]:
            st.warning("الوكيل طلب Order Flow، لكن بيانات DOM / Tape / CVD غير موجودة في سياق Radar الحالي. لن يعرض قراءة وهمية.")
        if not result["book_ready"]:
            st.info("دفتر الأوامر غير متصل بهذه الجولة. راجع Order Flow Desk في Workspace حتى يتم ربط المصدر.")

    if terminal:
        with st.expander("فتح التيرمينال · سجل التنفيذ بالعربي", expanded=True):
            st.markdown("<div class='rac-terminal'>", unsafe_allow_html=True)
            for i, step in enumerate(result["steps"], 1):
                badge = "DONE" if step["state"] == "done" else "WAIT"
                st.markdown(
                    f"<div class='rac-log'><b>[{i:02d}] {badge}</b> · {html.escape(step['title'])}<br/>&nbsp;&nbsp;↳ {html.escape(step['detail'])}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("<div class='rac-log'><b>[END]</b> انتهت الجولة · لم يتم إرسال أوامر تداول.</div></div>", unsafe_allow_html=True)

    if show_news:
        _render_news(st, news_items)


def _render_news(st, news_items):
    with st.expander("رادار الأخبار والتأثير المحتمل على الأسواق", expanded=False):
        if news_items is None:
            st.caption("اضغط تحديث الأخبار لجلب العناوين من المصادر العامة.")
            if st.button("تحديث الأخبار الآن", key="rac_fetch_news"):
                try:
                    from modules import news_watch
                    with st.spinner("جاري قراءة المصادر وتصنيف العناوين..."):
                        items, dead = news_watch.fetch_all(news_watch.default_fetch_text)
                        news_items = news_watch.alerts(items)
                        st.session_state["rac_news_cache"] = news_items
                        st.session_state["rac_news_dead"] = dead
                    st.rerun()
                except Exception as e:
                    st.warning(f"تعذر تحديث الأخبار: {type(e).__name__}")
        else:
            if st.button("إعادة تحديث الأخبار", key="rac_refresh_news"):
                st.session_state.pop("rac_news_cache", None)
                st.rerun()
            if not news_items:
                st.info("لا توجد عناوين عالية التأثير حديثة وفق قواعد التصنيف الحالية.")
            for item in news_items[:6]:
                lean = item.get("lean")
                lean_ar = "ميل لغوي متشدد" if lean == "hawkish" else "ميل لغوي متساهل" if lean == "dovish" else "لا يوجد ميل لغوي واضح"
                st.markdown(
                    f"<div class='rac-news'><b>{html.escape(item.get('title',''))}</b><br/>"
                    f"<span style='font-size:10px;color:#93a1aa'>{html.escape(item.get('source',''))} · تأثير محتمل: {item.get('impact','—')}/3 · {lean_ar}</span><br/>"
                    f"<span style='font-size:10px;color:#d8b46a'>قد يؤثر على: {html.escape(item.get('assets_ar',''))} — في الاتجاهين، وليس توقعاً لاتجاه السعر.</span>"
                    + (f"<br/><a href='{html.escape(item.get('url',''), quote=True)}' target='_blank'>المصدر</a>" if str(item.get("url","")).startswith(("http://","https://")) else "")
                    + "</div>", unsafe_allow_html=True,
                )
            dead = st.session_state.get("rac_news_dead", [])
            if dead:
                st.caption("مصادر لم تستجب في آخر تحديث: " + "، ".join(dead[:8]))
