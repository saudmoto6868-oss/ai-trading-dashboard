"""X77 page (Streamlit, Lab hub page 21): the X77 library (text / link / image / video / doc), chart analysis on our own
XPiX chart with detections labelled by school, and an Arabic guide. Labels only: nothing here trades or proves an edge."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from modules import x77_store as store

KIND_CHOICES = ["text", "link", "image", "video", "doc", "setup", "pattern", "trade", "lesson"]
KIND_AR = {"all": "الكل", "text": "نص", "link": "لينك", "image": "صورة", "video": "فيديو", "doc": "ملف", "setup": "سيتاب",
           "pattern": "نموذج", "trade": "صفقة", "lesson": "درس"}
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")

GUIDE_AR = """
**X77 = مخ بيجمع ويصنف، مش إشارة شراء أو بيع.** موجود في 3 أماكن:

1. **التاب ده (المعمل > X77):** المكتبة (احفظ صورة، لينك، فيديو، ملف، أو ملاحظة) + **حلل تشارت** على تشارت XPiX بتاعنا:
   كل كاشف في المشروع بيطلع نتيجته متصنفة بالمدرسة (SMC/ICT، إليوت، فيبو، دايفرجنس، شموع، وايكوف...).
2. **ويدجت في الورك سبيس (+ Widget > القرار > X77 المدارس):** جنب التشارتس. بيقرا سيتابات السكانر الحية للرمز المربوط
   ويكتب مدرسة كل كاشف بالعربي. دوس على سيتاب يفتحه في التشارتس المربوطة.
3. **زرار "Send to X77" في الرادار:** يحفظ الرمز والفريم وسبب الاختيار في المكتبة.

**اللي اتختبر لحد دلوقتي (بقواعد ثابتة قبل ما نشوف النتيجة):**
- عدد المدارس المتفقة (3 أو أكتر): **اتلغى** على التاريخ، حوالي -0.095R للصفقة بعد التكلفة، و4 مدارس أو أكتر أسوأ.
- 4 أزواج مدارس (سويب+OTE، سويب+دايفرجنس، شمعة عند مستوى، ترند+فيبو): **الأربعة اتلغوا** على التاريخ (صافي R تحت الصفر).

يعني التصنيف بيساعدك **تفهم** التشارت، لكنه لوحده مش ميزة. أي فكرة جديدة لازم تتسجل الأول وبعدين تتختبر.
"""


def _ar() -> bool:
    try:
        from modules.i18n import lang
        return lang() == "ar"
    except Exception:
        return False


def _tags(raw: str) -> tuple[str, ...]:
    return tuple(t for t in raw.split(",") if t.strip())


def _analyze(ar: bool, T) -> None:
    a, b, c = st.columns([2, 1, 1])
    sym = a.text_input(T("Symbol", "الرمز"), "BTC-USDT", key="x77_an_sym")
    tf = b.selectbox(T("Timeframe", "الفريم"), ["15m", "1h", "4h", "1d"], index=1, key="x77_an_tf")
    if c.button(T("Analyze", "حلل"), key="x77_an_go"):
        from modules import market_cache, x77_detect
        try:
            st.session_state["x77_an_res"] = (sym, tf, x77_detect.events(market_cache.get_klines(sym, tf, 300)))
        except Exception as exc:
            st.session_state.pop("x77_an_res", None)
            st.error(T("No candles: ", "مفيش شموع: ") + f"{type(exc).__name__}: {exc}")
    got = st.session_state.get("x77_an_res")
    if not got:
        return
    sym, tf, res = got
    from modules.x77_detect import SCHOOLS, summary
    st.caption(T(f"{sym} {tf} · regime: {res['regime'] or '-'} · labels only, not evidence",
                 f"{sym} {tf} · حالة السوق: {res['regime'] or '-'} · تصنيف بس، مش دليل"))
    cnt = summary(res)
    st.markdown(" · ".join(f"**{SCHOOLS.get(s, (s, s, ''))[0 if ar else 1]}** {n}" for s, n in cnt.items()) or T("No detections.", "مفيش أي كاشف طلع."))
    rows = [{T("School", "المدرسة"): SCHOOLS.get(e["school"], (e["school"], e["school"], ""))[0 if ar else 1],
             T("Side", "الاتجاه"): ({"bullish": "شراء", "bearish": "بيع", "buy": "شراء", "sell": "بيع"}.get(e.get("side"), e.get("side") or "-") if ar else e.get("side") or "-"),
             T("Detector", "الكاشف"): e.get("name", e["key"]), T("Detail", "التفاصيل"): e.get("detail", ""),
             T("What the school says", "المدرسة بتقول إيه"): SCHOOLS.get(e["school"], ("", "", ""))[2]}
            for e in res["events"] + res["patterns"]]
    if rows:
        st.dataframe(rows, hide_index=True)
    for e in res["errors"]:
        st.caption(e)
    try:   # our own XPiX chart (the Workspace chart widget, chart-only mode), same as the RSI Heatmap page uses
        from modules.workspace import render_workspace
        render_workspace([sym], lang="ar" if ar else "en", height=560, solo="chart")
    except Exception as exc:
        st.caption(T("Chart not available: ", "التشارت مش متاح: ") + f"{type(exc).__name__}")


def render() -> None:
    ar = _ar()
    T = (lambda en, a: a) if ar else (lambda en, a: en)
    st.subheader("X77")
    st.caption(T("Library + chart labels by school. Labels are not evidence; nothing here trades.",
                  "مكتبة + تصنيف التشارت بالمدرسة. التصنيف مش دليل، ومفيش أي تداول هنا."))
    with st.expander(T("How X77 works (Arabic guide)", "X77 بيشتغل إزاي؟"), expanded=False):
        st.markdown(GUIDE_AR)

    with st.form("x77_add", clear_on_submit=True):
        kind = st.selectbox(T("Kind", "النوع"), KIND_CHOICES, index=0, format_func=(lambda k: KIND_AR.get(k, k)) if ar else str)
        text = st.text_area(T("Text", "النص"), height=80)
        url = st.text_input(T("Link (https://...)", "لينك (https://...)"))
        tags = st.text_input(T("Tags (comma separated)", "تاجات (افصل بفاصلة)"))
        up = st.file_uploader(T("File", "ملف"), type=["png", "jpg", "jpeg", "webp", "gif", "mp4", "mov", "pdf", "txt", "md"])
        ok = st.form_submit_button(T("Save to X77", "احفظ في X77"))
    if ok:
        try:
            if up is not None:
                tmp = store.base_dir() / "_upload" / up.name
                tmp.parent.mkdir(parents=True, exist_ok=True)
                tmp.write_bytes(up.getvalue())
                try:
                    saved = store.add_item(kind, text=text, url=url, file=str(tmp), tags=_tags(tags))
                finally:
                    tmp.unlink(missing_ok=True)
            else:
                saved = store.add_item(kind, text=text, url=url, tags=_tags(tags))
            st.success(T("Saved ", "اتحفظ ") + saved["id"])
        except ValueError as exc:
            st.error(str(exc))

    with st.expander(T("Analyze a chart (our XPiX chart, every detector labelled by school)",
                       "حلل تشارت (تشارت XPiX بتاعنا، كل كاشف متصنف بالمدرسة)")):
        _analyze(ar, T)

    filt = st.segmented_control(T("Show", "اعرض"), ["all"] + KIND_CHOICES, default="all", key="x77_filter",
                                format_func=(lambda k: KIND_AR.get(k, k)) if ar else str)
    items = store.list_items(None if filt in (None, "all") else filt)
    st.caption(T(f"{len(items)} item(s)", f"{len(items)} عنصر"))
    for it in reversed(items[-200:]):
        with st.container(border=True):
            st.markdown(f"**{it['id']}** · `{KIND_AR.get(it['kind'], it['kind']) if ar else it['kind']}` · "
                        + T("tags: ", "تاجات: ") + (", ".join(it["tags"]) or "-"))
            if it.get("text"):
                st.write(it["text"])
            if it.get("url"):
                st.write(it["url"])
            if it.get("media"):
                p = Path(it["media"])
                if p.suffix.lower() in IMG_EXT and p.is_file():
                    st.image(str(p), width=360)
                else:
                    st.caption(p.name)


def send_box(symbols, key: str = "x77_send") -> None:
    """Radar button (owner 2026-11-20): save one symbol + timeframe + note as an X77 'setup'. No analysis, no order."""
    ar = _ar()
    T = (lambda en, a: a) if ar else (lambda en, a: en)
    with st.popover(T("Send to X77", "ابعت لـ X77")):
        sym = st.selectbox(T("Symbol", "الرمز"), list(symbols) or ["BTC-USDT"], key=f"{key}_sym")
        tf = st.selectbox(T("Timeframe", "الفريم"), ["5m", "15m", "1h", "4h", "1d"], index=2, key=f"{key}_tf")
        note = st.text_input(T("Why (pattern / school)", "ليه (النموذج / المدرسة)"), key=f"{key}_note")
        if st.button(T("Save", "احفظ"), key=f"{key}_go"):
            try:
                saved = store.add_item("setup", text=f"{sym} {tf} {note}".strip(), tags=("radar", sym, tf))
                st.success(T("Saved ", "اتحفظ ") + saved["id"])
            except ValueError as exc:
                st.error(str(exc))
