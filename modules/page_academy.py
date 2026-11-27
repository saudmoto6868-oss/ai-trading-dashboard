"""Academy page (index 7): Path / Schools / References / Lab tools. Moved from main.py unchanged (maintenance plan M7 / 4.2)."""
import html
import os

import streamlit as st

from modules.i18n import L
from modules.page_kit import kit_css


def _ac_go(lesson_id: str, level: int):
    """Callback: jump to a lesson (sets the level pills and that level's lesson pills before the widgets are drawn)."""
    st.session_state["ac_level"] = level
    st.session_state[f"ac_les_{level}"] = lesson_id


def _academy_lab_tools():
    """Four short lessons on the Lab Summary sections (docs/academy/lab_tools/): what each section shows, from the code; lazy read, a missing file degrades to a message."""
    from modules.lab_shared import t as _t
    lessons = [("10-validation-lab", _t("جدول المعمل الكامل", "Full lab table")), ("11-calibration", _t("المعايرة: داخل/خارج العينة", "Calibration: in / out of sample")),
               ("12-rotation", _t("دوران الفئات", "Class rotation")), ("13-evidence-summary", _t("ملخص الأدلة لكل Setup", "Evidence per setup"))]
    names = dict(lessons)
    pick = st.radio(L("Lesson"), [k for k, _n in lessons], format_func=lambda k: names[k], key="ac_lab_pick", horizontal=True, label_visibility="collapsed")
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "academy", "lab_tools", pick + ".md")
    try:
        st.markdown(open(p, encoding="utf-8").read())
    except OSError:
        st.info(_t("الدرس مش موجود لسه: ", "Lesson not available yet: ") + pick)
    st.caption(_t("الصفحة اللي بتشرحها: Lab Summary.", "The page these lessons explain: Lab Summary."))


def _academy_path():
    """The learning path, laid out for a wide screen (owner 2026-10-23): small chrome, large explanation, three columns on one screen:
    lesson list | animated bullish / bearish diagrams + the idea | steps, setups, mistakes, platform, references, quiz."""
    from modules import academy as AC, academy_art as ART, ui_kit as UK
    e = html.escape
    lp = AC.learning_path()
    ls, lvs = lp["lessons"], lp["levels"]
    if not ls:
        st.info(L("No lessons yet."))
        return
    done = st.session_state.setdefault("ac_done", set())
    by_level = {lv["id"]: [x for x in ls if x["level"] == lv["id"]] for lv in lvs}
    n_done = sum(1 for x in ls if x["id"] in done)
    nxt = next((x for x in ls if x["id"] not in done), ls[0])
    st.markdown("""<style>
.st-key-acpath{--fs:15.5px}
.st-key-acpath [data-testid="stWidgetLabel"] p,.st-key-acpath label p{font-size:12px!important}
.st-key-acpath [data-testid="stRadio"] label p{font-size:13px!important;line-height:1.35}
.st-key-acpath .ac-exp{font-size:var(--fs);line-height:1.9;color:var(--uk-text)}
.st-key-acpath .ac-exp li{margin:0 0 6px}
.st-key-acpath .ac-small{font-size:12px;color:var(--uk-dim);line-height:1.6}
.st-key-acpath .ac-h{font-size:12px;letter-spacing:.06em;color:var(--uk-dim);text-transform:uppercase;margin:10px 0 4px;font-weight:700}
.st-key-acpath svg{width:100%;height:auto}
</style>""", unsafe_allow_html=True)
    lv_ids = [lv["id"] for lv in lvs]
    if "ac_level" not in st.session_state:
        st.session_state["ac_level"] = nxt["level"]
        st.session_state[f"ac_les_{nxt['level']}"] = nxt["id"]
    with st.container(key="acpath"):
        top = st.columns([5, 1.4])
        lv = top[0].pills(L("Level"), lv_ids, key="ac_level", format_func=lambda i: f"{i} · " + next(x["title"].split(":")[0] for x in lvs if x["id"] == i) + f"  ({sum(1 for y in by_level[i] if y['id'] in done)}/{len(by_level[i])})",
                          label_visibility="collapsed") or lv_ids[0]
        top[1].markdown(f"<div class='uk-chipbar' style='justify-content:flex-end'><span class='uk-chip'>✅ {n_done}/{len(ls)}</span><span class='uk-chip'>➡️ {e(nxt['title'][:18])}</span></div>", unsafe_allow_html=True)
        lvl = next(x for x in lvs if x["id"] == lv)
        left, mid, right = st.columns([1.0, 3.4, 2.5], gap="medium")
        names = {x["id"]: ("✅ " if x["id"] in done else "") + x["title"] for x in by_level[lv]}
        with left:
            st.markdown(f"<div class='ac-small'><b>{e(lvl['title'])}</b><br>{e(lvl.get('goal', ''))}</div>", unsafe_allow_html=True)
            cur_id = st.radio(L("Lesson"), list(names), key=f"ac_les_{lv}", format_func=names.get, label_visibility="collapsed")
            c_ = next(x for x in by_level[lv] if x["id"] == cur_id)
            i_cur = ls.index(c_)
            n1, n2 = st.columns(2)
            if i_cur > 0:
                n1.button("→ " + L("Previous"), key="ac_prev", on_click=_ac_go, args=(ls[i_cur - 1]["id"], ls[i_cur - 1]["level"]), width="stretch")
            if i_cur < len(ls) - 1:
                n2.button(L("Next") + " ←", key="ac_next", on_click=_ac_go, args=(ls[i_cur + 1]["id"], ls[i_cur + 1]["level"]), width="stretch")
            if c_["id"] in done:
                st.button("↩ " + L("Mark not done"), key="ac_undo", on_click=lambda: done.discard(c_["id"]), width="stretch")
            else:
                st.button("✅ " + L("Mark done"), key="ac_mark", on_click=lambda: done.add(c_["id"]), width="stretch")
        gc = AC.GRADE[c_["grade"]]
        with mid:
            st.markdown(f"<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap'><span style='font-size:19px;font-weight:800'>{e(c_['title'])}</span>"
                        f"<span class='uk-chip' style='border-color:{gc};color:{gc}'>{e(L('Evidence'))}: {e(c_.get('grade_label', c_['grade']))}</span>"
                        f"<span class='ac-small'>{e(L('Level'))} {c_['level']} · {e(L('Lesson'))} {i_cur + 1}/{len(ls)}</span></div>", unsafe_allow_html=True)
            items = []
            for a in c_["arts"]:
                items += [(a, "bull"), (a, "bear")] if a in ART.MIRRORED else [(a, "bull")]
            for r0 in range(0, len(items), 2):
                row = items[r0:r0 + 2]
                cc = st.columns(2) if len(row) == 2 else st.columns([1, 1])[:1]
                for col, (a, side) in zip(cc, row):
                    tag = ""
                    if a in ART.MIRRORED:
                        tc = UK.UP if side == "bull" else UK.DOWN
                        tag = f"<div class='uk-chipbar' style='margin:0 0 3px'><span class='uk-chip' style='border-color:{tc};color:{tc}'>{e(L('Bullish') if side == 'bull' else L('Bearish'))}</span></div>"
                    col.markdown(tag + ART.art(a, side), unsafe_allow_html=True)
            st.caption(L("The drawings are illustrations built from a few price points, not market data and not a forecast."))
            st.markdown(f"<div class='ac-h'>{e(L('The idea'))}</div><div class='ac-exp'>{e(c_['idea'])}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ac-small' style='margin-top:8px;border-inline-start:3px solid {gc};padding-inline-start:8px'>{e(c_['grade_note'])}</div>", unsafe_allow_html=True)
        with right:
            st.markdown(f"<div class='ac-h'>{e(L('Steps'))}</div><ol class='ac-exp' style='padding-inline-start:20px;margin:0'>" + "".join(f"<li>{e(t)}</li>" for t in c_["steps"]) + "</ol>", unsafe_allow_html=True)
            if c_["bull"] or c_["bear"]:
                st.markdown(f"<div class='uk-panel' style='border-color:{UK.UP};padding:6px 10px'><div class='ac-small' style='color:{UK.UP};font-weight:700'>📈 {e(L('Bullish setup'))}</div><div class='ac-exp' style='font-size:14px;line-height:1.7'>{e(c_['bull'])}</div></div>"
                            f"<div class='uk-panel' style='border-color:{UK.DOWN};padding:6px 10px'><div class='ac-small' style='color:{UK.DOWN};font-weight:700'>📉 {e(L('Bearish setup'))}</div><div class='ac-exp' style='font-size:14px;line-height:1.7'>{e(c_['bear'])}</div></div>", unsafe_allow_html=True)
            if c_["mistakes"]:
                st.markdown(f"<div class='ac-h'>⚠️ {e(L('Common mistakes'))}</div><ul class='ac-small' style='padding-inline-start:18px;margin:0'>" + "".join(f"<li>{e(t)}</li>" for t in c_["mistakes"]) + "</ul>", unsafe_allow_html=True)
            if c_["platform"]:
                st.markdown(f"<div class='ac-h'>{e(L('Where it lives in the platform'))}</div><div class='uk-chipbar'>" + "".join(f"<span class='uk-chip'>🔗 {e(t)}</span>" for t in c_["platform"]) + "</div>", unsafe_allow_html=True)
            with st.expander(L("References")):
                st.markdown(chr(10).join(f"- {t}" for t in c_["refs"]))
                st.caption(L("Book and paper citations, given without links; check the edition. Educational, not investment advice."))
            with st.expander(L("Quick quiz"), expanded=False):
                picks = [st.radio(q["q"], q["opts"], index=None, key=f"acq_{c_['id']}_{k}") for k, q in enumerate(c_["quiz"])]
                if st.button(L("Check answers"), key=f"acc_{c_['id']}"):
                    right_n = 0
                    for q, pk in zip(c_["quiz"], picks):
                        if pk is None:
                            st.info(f"{q['q']} — {L('Not answered')}")
                        elif q["opts"].index(pk) == q["a"]:
                            right_n += 1
                            st.success(f"✓ {q['why']}")
                        else:
                            st.error(f"✗ {L('Correct answer')}: {q['opts'][q['a']]} — {q['why']}")
                    if right_n == len(c_["quiz"]):
                        done.add(c_["id"])
            if c_["school"]:
                st.caption(L("The full school curriculum is in the Schools tab") + f": {c_['school']}")


def _academy_refs():
    """Research intake: every source the team gathered is a preliminary reference (not rejected, not approved); names map to ours; claims keep their verdict and sources."""
    from modules import academy as AC, ui_kit as UK
    import pandas as _pd
    e = html.escape
    R = AC.refs()
    st.info(L("Every source below is a preliminary reference: kept open, neither rejected nor approved. Where names differ we keep ours and carry the concept into our schools and lessons."))
    gen = [l_ for l_ in AC.load() if l_["id"] not in AC.REVIEW_OF]
    if gen:
        st.markdown(f"**{L('Our review')}** · {L('general findings')}")
        for l_ in gen:
            vl, vc = AC.verdict_label(l_["verdict"])
            with st.expander(f"[{vl}] {l_['title']}"):
                st.markdown(l_["summary"])
                st.markdown(f"<div class='uk-panel' style='border-color:{vc}'><h4>{e(L('Our review'))}</h4>{e(l_['verdict_note'])}</div>", unsafe_allow_html=True)
                if l_["points"]:
                    st.markdown(chr(10).join(f"- {p_}" for p_ in l_["points"]))
                if l_["caveats"]:
                    st.warning(chr(10).join(f"- {p_}" for p_ in l_["caveats"]))
    st.markdown(f"**{L('Sources gathered')}**")
    for x in R["sources"]:
        with st.expander(f"{x['title']}  ·  {x['origin']}"):
            st.caption(f"{x.get('kind', '')} · {x.get('path', '')}")
            if x.get("takeaways"):
                st.markdown(chr(10).join(f"- {t}" for t in x["takeaways"]))
            if x.get("open"):
                st.warning(f"**{L('Still open')}**" + chr(10) + chr(10).join(f"- {t}" for t in x["open"]))
    st.markdown(f"**{L('Naming map: their term, our term')}**")
    st.dataframe(_pd.DataFrame([{L("Their term"): g["their"], L("Our term"): g["ours"], L("Where"): g.get("where", ""), L("Note"): g.get("note", "")} for g in R["glossary"]]), hide_index=True, width="stretch")
    st.markdown(f"**{L('Claims checked against sources')}**")
    if not R["claims"]:
        st.caption(L("No claims checked yet."))
        return
    cnt = {}
    for c in R["claims"]:
        cnt[c["verdict"]] = cnt.get(c["verdict"], 0) + 1
    st.markdown(UK.panel(L("Claim verdicts"), UK.donut([(AC.claim_verdict_label(k)[0], v, AC.CLAIM_VERDICT[k][1]) for k, v in cnt.items()], center=str(len(R["claims"])))), unsafe_allow_html=True)
    for c in R["claims"]:
        vl, vc = AC.claim_verdict_label(c["verdict"])
        with st.expander(f"[{vl}] {c['claim'][:110]}"):
            st.markdown(f"<div class='uk-chipbar'><span class='uk-chip' style='border-color:{vc};color:{vc}'>{e(vl)}</span><span class='uk-chip'>{e(AC.origin_label(c.get('origin', '')))}</span><span class='uk-chip'>{e(str(c.get('where', '')))}</span></div>", unsafe_allow_html=True)
            st.markdown(c.get("evidence", ""))
            if c.get("note"):
                st.markdown(f"**{L('What to do')}:** {c['note']}")
            if c["urls"]:
                st.markdown(" · ".join(f"[{i + 1}]({u})" for i, u in enumerate(c["urls"])))


def _academy_schools():
    """Grok's nine schools in teaching order, wide layout: ordered list | diagrams + the lesson | tabs for examples, evidence, our review, curriculum, machine spec."""
    from modules import academy as AC, academy_art as ART, ui_kit as UK
    e = html.escape
    sc = AC.ordered_schools()
    if not sc:
        st.info(L("No lessons yet."))
        return
    by = {x["id"]: x for x in sc}
    DEEP = AC.deep()
    st.markdown("""<style>
.st-key-acschools .ac-exp{font-size:15px;line-height:1.85}.st-key-acschools .ac-small{font-size:12px;color:var(--uk-dim);line-height:1.6}
.st-key-acschools [data-testid="stRadio"] label p{font-size:13px!important}.st-key-acschools svg{width:100%;height:auto}
.st-key-acschools [data-testid="stMarkdownContainer"] table{font-size:12.5px}
.st-key-acschools [data-testid="stMarkdownContainer"] p,.st-key-acschools [data-testid="stMarkdownContainer"] li{font-size:14.5px;line-height:1.8}
</style>""", unsafe_allow_html=True)
    with st.container(key="acschools"):
        left, mid, right = st.columns([0.95, 3.0, 2.7], gap="medium")
        with left:
            st.markdown(f"<div class='ac-small'><b>{e(L('Teaching order'))}</b><br>{e(L('Each school builds on the one before it.'))}</div>", unsafe_allow_html=True)
            pick = st.radio(L("School"), [x["id"] for x in sc], key="ac_school_r", label_visibility="collapsed",
                            format_func=lambda k: f"{by[k]['pos']}. {by[k]['icon']} {by[k]['title'].split('—')[0].strip()}")
            nav = st.columns(2)
            i0 = [x["id"] for x in sc].index(pick)
            if i0 > 0:
                nav[0].button("→", key="ac_sprev", on_click=lambda: st.session_state.update(ac_school_r=sc[i0 - 1]["id"]), width="stretch")
            if i0 < len(sc) - 1:
                nav[1].button("←", key="ac_snext", on_click=lambda: st.session_state.update(ac_school_r=sc[i0 + 1]["id"]), width="stretch")
        x = by[pick]
        body, chips = AC.badges(x["visual"])
        body, flows = AC.chains(body)
        with mid:
            st.markdown(f"<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap'><span style='font-size:19px;font-weight:800'>{x['pos']}. {e(x['icon'])} {e(x['title'])}</span>"
                        + "".join(f"<span class='uk-chip' style='border-color:{c};color:{c}'>{e(t)}</span>" for t, c in chips) + "</div>"
                        f"<div class='ac-small' style='margin:4px 0 8px'>{e(L('Why here'))}: {e(x['why'])}</div>", unsafe_allow_html=True)
            items = []
            for a in x["arts"]:
                items += [(a, "bull"), (a, "bear")] if a in ART.MIRRORED else [(a, "bull")]
            for r0 in range(0, len(items), 2):
                row = items[r0:r0 + 2]
                cc = st.columns(2) if len(row) == 2 else st.columns([1, 1])[:1]
                for col, (a, side) in zip(cc, row):
                    tag = ""
                    if a in ART.MIRRORED:
                        tc = UK.UP if side == "bull" else UK.DOWN
                        tag = f"<div class='uk-chipbar' style='margin:0 0 3px'><span class='uk-chip' style='border-color:{tc};color:{tc}'>{e(L('Bullish') if side == 'bull' else L('Bearish'))}</span></div>"
                    col.markdown(tag + ART.art(a, side), unsafe_allow_html=True)
            st.caption(L("The drawings are illustrations built from a few price points, not market data and not a forecast."))
            st.warning(AC.lab_note())
            md = lambda t: t.replace(chr(10), "  " + chr(10))
            dp = DEEP.get(pick)
            if dp:
                st.markdown(f"<div class='ac-h'>{e(L('What it is'))}</div><div class='ac-exp'>{e(dp['what'])}</div>", unsafe_allow_html=True)
                for p_ in dp["parts"]:
                    st.markdown(f"<div class='ac-h'>{e(p_['t'])}</div>", unsafe_allow_html=True)
                    st.markdown(md(p_["b"]))
                c1, c2 = st.columns(2)
                c1.markdown(f"<div class='uk-panel' style='border-color:{UK.UP};padding:6px 10px'><div class='ac-small' style='color:{UK.UP};font-weight:700'>📈 {e(L('Bullish setup'))}</div><div class='ac-exp' style='font-size:14px;line-height:1.75'>{e(dp['bull_story'])}</div></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='uk-panel' style='border-color:{UK.DOWN};padding:6px 10px'><div class='ac-small' style='color:{UK.DOWN};font-weight:700'>📉 {e(L('Bearish setup'))}</div><div class='ac-exp' style='font-size:14px;line-height:1.75'>{e(dp['bear_story'])}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='ac-h'>{e(L('Where it lives in the platform'))}</div>", unsafe_allow_html=True)
                st.markdown(chr(10).join(f"{k + 1}. {t}" for k, t in enumerate(dp["platform"])))
                st.markdown(f"<div class='ac-h'>⚠️ {e(L('Common mistakes'))}</div>", unsafe_allow_html=True)
                st.markdown(chr(10).join(f"- {t}" for t in dp["mistakes"]))
                st.markdown(f"<div class='ac-h'>🧪 {e(L('Exercises'))}</div>", unsafe_allow_html=True)
                st.markdown(chr(10).join(f"{k + 1}. {t}" for k, t in enumerate(dp["exercises"])))
                st.markdown(f"<div class='ac-h'>❓ {e(L('Questions'))}</div>", unsafe_allow_html=True)
                for fq in dp["faq"]:
                    with st.expander(fq["q"]):
                        st.markdown(fq["a"])
                st.markdown(f"<div class='ac-h'>{e(L('Glossary'))}</div><div class='uk-chipbar'>" + "".join(f"<span class='uk-chip' title='{e(g['def'])}'>{e(g['term'])}: {e(g['def'])}</span>" for g in dp["glossary"]) + "</div>", unsafe_allow_html=True)
            with st.expander(L("Grok's short visual notes (source)")):
                for fl in flows:
                    st.markdown("<div class='uk-flex' style='gap:6px'>" + "<span style='color:var(--uk-dim)'>→</span>".join(f"<span class='uk-chip' style='font-size:12px;padding:3px 10px'>{e(t)}</span>" for t in fl) + "</div>", unsafe_allow_html=True)
                st.markdown(body)
        with right:
            # one tab runs per rerun (st.tabs ran all four); same content, same order
            _ac_names = [L("Examples"), L("Evidence"), L("Our review"), L("Machine spec (AI track)")]
            _ac_pick = st.segmented_control(" ", list(range(4)), default=0, format_func=lambda i: _ac_names[i], key=f"ac_ref_tab_{x['id']}", label_visibility="collapsed") or 0
            if _ac_pick == 0:
                st.markdown(x["examples"] or L("No lessons yet."))
            elif _ac_pick == 1:
                st.info(L("External evidence from published sources. It is context, not the project's lab result."))
                st.markdown(x["evidence"] or L("No lessons yet."))
            elif _ac_pick == 2:
                if not x["review"]:
                    st.caption(L("No school-specific review yet; the general findings are in the References tab."))
                for l_ in x["review"]:
                    stl, stc = AC.status_label(l_["status"]); vl, vc = AC.verdict_label(l_["verdict"])
                    st.markdown(f"<div class='uk-chipbar'><span class='uk-chip' style='border-color:{stc};color:{stc}'>{e(stl)}</span><span class='uk-chip' style='border-color:{vc};color:{vc}'>{e(vl)}</span></div>"
                                f"<div style='font-weight:700;margin:6px 0'>{e(l_['title'])}</div>", unsafe_allow_html=True)
                    st.markdown(l_["summary"])
                    st.markdown(f"<div class='uk-panel' style='border-color:{vc}'><h4>{e(L('Our review'))}</h4>{e(l_['verdict_note'])}</div>", unsafe_allow_html=True)
                    if l_["points"]:
                        st.markdown(chr(10).join(f"- {p_}" for p_ in l_["points"]))
                    if l_["caveats"]:
                        st.warning(chr(10).join(f"- {p_}" for p_ in l_["caveats"]))
            else:
                st.markdown(x["ai"] or L("No lessons yet."))


def render_academy_page():
    """Academy (owner 2026-10-23): three tabs only. Path = our ordered course; Schools = Grok's nine schools in teaching order, each with its diagrams, examples, evidence
    and our review; References = every source as a preliminary reference, the naming map, claims checked against sources, and the general review findings."""
    from modules import academy as AC, ui_kit as UK  # noqa: F401
    st.markdown(kit_css(), unsafe_allow_html=True)
    view = st.segmented_control(L("Academy"), ["Path", "Schools", "References", "Lab tools"], default="Path", key="ac_view", format_func=lambda v: L(v), label_visibility="collapsed") or "Path"
    if view == "Path":
        _academy_path()
    elif view == "Schools":
        _academy_schools()
    elif view == "Lab tools":
        _academy_lab_tools()
    else:
        _academy_refs()
