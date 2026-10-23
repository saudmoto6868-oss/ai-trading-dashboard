"""AI page: chat with Mr X about any symbol (text). Uses the same brain, caps and cache as the Workspace guide (modules/guide_ai.py).
Token budget (owner rule): the model gets a short computed summary of the chart (price, change, EMA trend, RSI, ATR, range) - never raw candles."""
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


def render_ai_page(symbols, L):
    st.subheader(L("Mr X - AI analyst"))
    if not guide_ai.provider():
        st.info(L("Add OPENAI_API_KEY, GEMINI_API_KEY (free), or ANTHROPIC_API_KEY in Streamlit Secrets to talk to Mr X."))
        return
    c1, c2, c3 = st.columns([2, 1, 1])
    sym = c1.selectbox(L("Symbol"), symbols, key="ai_sym")
    tf = c2.selectbox(L("Timeframe"), ["15m", "1h", "4h", "1d"], index=1, key="ai_tf")
    if c3.button(L("New chat"), key="ai_new"):
        st.session_state["ai_hist"], st.session_state["ai_msgs"] = [], []
    hist, msgs = st.session_state.setdefault("ai_hist", []), st.session_state.setdefault("ai_msgs", [])
    for m in msgs:
        with st.chat_message(m["role"], avatar="🧑‍💼" if m["role"] == "assistant" else None):
            st.markdown(m["text"])
    q = st.chat_input(L("Ask Mr X about this chart, a setup, risk..."))
    if not q:
        st.caption(L("Answers are education, not financial advice. Mr X only sees a short summary of the chart (price, trend, RSI, ATR, range)."))
        return
    msgs.append({"role": "user", "text": q})
    with st.chat_message("user"):
        st.markdown(q)
    ctx = {"lang": "ar", "page": "AI analyst", "sym": sym, "tf": tf}
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
