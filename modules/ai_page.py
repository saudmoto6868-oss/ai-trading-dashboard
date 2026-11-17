"""AI page: Mr X teaches from the existing Academy and explains the selected chart.
The model receives bounded lesson metadata plus a compact chart summary, never raw candles."""
import time

import streamlit as st

from modules import guide_ai


def chart_summary(df) -> dict:
    """Short facts from a candle DataFrame (open/high/low/close/volume). Empty dict if there is not enough data."""
    if df is None or len(df) < 30:
        return {}
    c = df["close"].astype(float)
    h, l = df["high"].astype(float), df["low"].astype(float)
    ema20, ema50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    d = c.diff()
    up, dn = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(), (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + up.iloc[-1] / dn.iloc[-1]) if dn.iloc[-1] > 0 else 100.0
    tr = (h - l).combine((h - c.shift()).abs(), max).combine((l - c.shift()).abs(), max)
    last = float(c.iloc[-1])
    n = min(len(c) - 1, 24)
    return {"price": round(last, 6), "change_pct_last_%d_bars" % n: round(100 * (last / float(c.iloc[-1 - n]) - 1), 2),
            "ema20": round(float(ema20.iloc[-1]), 6), "ema50": round(float(ema50.iloc[-1]), 6),
            "trend": "up" if ema20.iloc[-1] > ema50.iloc[-1] and last > ema20.iloc[-1] else "down" if ema20.iloc[-1] < ema50.iloc[-1] and last < ema20.iloc[-1] else "mixed",
            "rsi14": round(float(rsi), 1), "atr14_pct": round(100 * float(tr.tail(14).mean()) / last, 2),
            "range_high_50": round(float(h.tail(50).max()), 6), "range_low_50": round(float(l.tail(50).min()), 6)}


def _academy_lessons():
    """Return the existing learning-path lessons; do not create a parallel AI curriculum."""
    try:
        from modules import academy as AC
        return AC.learning_path().get("lessons", [])
    except Exception:
        return []


def _lesson_context(lesson):
    """Bounded, provenance-aware lesson context for Mr X (never a full course dump)."""
    if not isinstance(lesson, dict):
        return {}
    return {
        "id": str(lesson.get("id", ""))[:80],
        "title": str(lesson.get("title", ""))[:160],
        "school": str(lesson.get("school", ""))[:80],
        "evidence_grade": str(lesson.get("grade", ""))[:40],
        "concept": str(lesson.get("idea", ""))[:420],
        "key_steps": [str(x)[:120] for x in (lesson.get("steps") or [])[:3]],
        "caveat": "Educational context only; a lesson or hypothesis is not empirical validation.",
    }


def render_ai_page(symbols, L):
    st.subheader(L("Mr X - AI analyst"))
    if not guide_ai.provider():
        st.info(L("Add GEMINI_API_KEY (free) or ANTHROPIC_API_KEY in Streamlit Secrets to talk to Mr X."))
        return
    c1, c2, c3 = st.columns([2, 1, 1])
    sym = c1.selectbox(L("Symbol"), symbols, key="ai_sym")
    tf = c2.selectbox(L("Timeframe"), ["15m", "1h", "4h", "1d"], index=1, key="ai_tf")
    if c3.button(L("New chat"), key="ai_new"):
        st.session_state["ai_hist"], st.session_state["ai_msgs"] = [], []
    lessons = _academy_lessons()
    lesson_by_id = {x.get("id"): x for x in lessons if x.get("id")}
    lesson_ids = [""] + list(lesson_by_id)
    lesson_id = st.selectbox(
        L("Learn with an Academy lesson"),
        lesson_ids,
        key="ai_lesson_context",
        format_func=lambda k: L("No lesson selected") if not k else lesson_by_id[k].get("title", k),
        help=L("Mr X will use this existing Academy lesson as bounded context. No new course is created."),
    )
    hist, msgs = st.session_state.setdefault("ai_hist", []), st.session_state.setdefault("ai_msgs", [])
    for m in msgs:
        with st.chat_message(m["role"], avatar="🧑‍💼" if m["role"] == "assistant" else None):
            st.markdown(m["text"])
    q = st.chat_input(L("Ask Mr X about this chart, a setup, risk..."))
    if not q:
        st.caption(L("Answers are education, not financial advice. Mr X only sees a short chart summary and, optionally, one existing Academy lesson."))
        return
    msgs.append({"role": "user", "text": q})
    with st.chat_message("user"):
        st.markdown(q)
    ctx = {"lang": "ar", "page": "AI analyst", "sym": sym, "tf": tf}
    if lesson_id:
        ctx["academy_lesson"] = _lesson_context(lesson_by_id[lesson_id])
    try:
        from modules.market_cache import get_klines
        ctx.update(chart_summary(get_klines(sym, tf, 200)))
    except Exception as e:   # no data: Mr X says so instead of guessing prices
        ctx["data"] = "unavailable (" + type(e).__name__ + ")"
    with st.chat_message("assistant", avatar="🧑‍💼"), st.spinner(L("Mr X is thinking...")):
        out = guide_ai.answer({"id": "ai%d" % time.time_ns(), "q": q, "ctx": ctx}, hist)
        say = out.get("say") or {"cap": L("Today's question limit is reached."), "nokey": L("No AI key in Secrets.")}.get(out.get("err"), L("Mr X could not answer") + " (" + str(out.get("err")) + ")")
        st.markdown(say)
    msgs.append({"role": "assistant", "text": say})
