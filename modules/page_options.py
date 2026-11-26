"""Trading > Options & macro page (index 16). Moved from main.py unchanged (maintenance plan M7 / 4.2)."""
import html

import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.page_kit import kit_css


def _office_options():
    """Technical Office > Options desk: the crypto option market from Deribit's free public book (no chart needed). Per-expiry put/call,
    max pain, ATM IV, skew proxy and OI walls, the IV term structure, and plain-Arabic reading lines. Context, not a trade signal."""
    import altair as alt
    import pandas as _pd
    from modules import office_ui as U, options_desk as OD
    st.markdown(U.CSS, unsafe_allow_html=True)
    cur = st.segmented_control(L("Underlying"), ["BTC", "ETH"], default="BTC", key="od_cur", label_visibility="collapsed") or "BTC"

    @st.cache_data(ttl=120, show_spinner=False)
    def _rows(c):
        return OD.fetch(c)
    try:
        rows = _rows(cur)
    except Exception as e:
        st.warning(f"Deribit: {type(e).__name__}: {e}")
        return
    s = OD.summarize(rows)
    ex = s["expiries"]
    try:
        @st.cache_data(ttl=1800, show_spinner=False)
        def _dv(c):
            return OD.dvol(c)
        hist = _dv(cur)
        rk = OD.iv_rank([v for _d, v in hist])
    except Exception:
        hist, rk = [], None
    if not ex:
        st.info(L("No option data."))
        return
    t = s["totals"]
    near = next((e for e in ex if e["days"] >= 1), ex[0])
    st.markdown("<div class='xo-row'>" + U.indicators(f"{cur} · Deribit", [
        (L("Spot (index)"), f"{s['spot']:,.0f}", "", None),
        (L("Open interest"), f"{t['oi']:,.0f} {cur}", "", None),
        (L("Put / call (open interest)"), f"{t['pc_oi']}" if t["pc_oi"] else "-", L("all expiries"), "warn" if t["pc_oi"] and t["pc_oi"] > 1 else None),
        (L("Volume (24 h)"), f"{t['vol']:,.0f} {cur}", "", None),
        (L("Nearest expiry"), str(near["exp"]), f"{near['days']} " + L("days"), None),
        (L("ATM IV, nearest"), f"{near['iv']}%" if near["iv"] else "-", L("annualised"), None),
        (L("IV rank (1 year)"), f"{rk['rank']:.0f}%" if rk else "-", (f"DVOL {rk['now']} · " + L("min") + f" {rk['min']} / " + L("max") + f" {rk['max']} · " + L("percentile") + f" {rk['percentile']:.0f}%") if rk else L("DVOL history not available"), None)]) + "</div>", unsafe_allow_html=True)
    df = _pd.DataFrame([{L("Expiry"): str(e["exp"]), L("Days"): e["days"], L("Open interest"): e["oi"], "P/C OI": e["pc_oi"], "P/C vol": e["pc_vol"],
                         L("Max pain"): e["max_pain"], "ATM IV %": e["iv"], L("Skew ±10% (put IV - call IV)"): e["skew10"],
                         L("Biggest strikes"): " · ".join(f"{int(k)}{c} ({oi:,.0f})" for k, c, oi in e["walls"])} for e in ex])
    a, b = st.columns([1, 1])
    with a:
        st.markdown(f"<div class='xo-h'>{html.escape(L('IV term structure'))}</div>", unsafe_allow_html=True)
        ts = _pd.DataFrame([{"days": e["days"], "iv": e["iv"], "exp": str(e["exp"])} for e in ex if e["iv"]])
        if len(ts):
            st.altair_chart(alt.Chart(ts).mark_line(point=True, color="#2dd4bf").encode(x=alt.X("days:Q", title=L("Days")), y=alt.Y("iv:Q", title="IV %", scale=alt.Scale(zero=False)),
                            tooltip=["exp", "days", "iv"]).properties(height=220), width="stretch")
    with b:
        pick = st.selectbox(L("Expiry"), [str(e["exp"]) for e in ex], index=ex.index(near), key="od_exp")
        d_pick = next(e for e in ex if str(e["exp"]) == pick)
        ks = _pd.DataFrame(OD.strikes(rows, d_pick["exp"], s["spot"]), columns=["strike", "calls", "puts"])
        if len(ks):
            lng = ks.melt("strike", var_name="side", value_name="oi")
            ch = alt.Chart(lng).mark_bar().encode(x=alt.X("strike:Q", title=L("Strike")), y=alt.Y("oi:Q", title=L("Open interest")), color=alt.Color("side:N",
                    scale=alt.Scale(domain=["calls", "puts"], range=["#2dd4bf", "#f87171"]), legend=alt.Legend(orient="top")), tooltip=["strike", "side", "oi"])
            rl = alt.Chart(_pd.DataFrame({"x": [s["spot"]], "t": [L("Spot (index)")]})).mark_rule(color="#f0b429", strokeDash=[6, 4]).encode(x="x:Q")
            mp = alt.Chart(_pd.DataFrame({"x": [d_pick["max_pain"]]})).mark_rule(color="#a78bfa", strokeDash=[2, 3]).encode(x="x:Q")
            st.altair_chart((ch + rl + mp).properties(height=220), width="stretch")
            st.caption(L("Gold line = spot, purple dotted = max pain for this expiry."))
    st.dataframe(df, hide_index=True, width="stretch")
    # plain reading of the nearest expiry: description, never a signal
    lines = []
    _oa = _ui_lang() == "ar"
    _ot = lambda e, a: a if _oa else e   # English / Arabic text of this reading, chosen by the site language
    if near["pc_oi"]:
        lines.append(_ot(f"Put / call ratio by open interest for the nearest expiry ({near['exp']}) = {near['pc_oi']}: ", f"نسبة puts / calls بالـ open interest لأقرب استحقاق ({near['exp']}) = {near['pc_oi']}: ") +
                     (_ot("more puts than calls; often protection and hedge positions, not necessarily a bearish bet.", "puts أكتر من calls؛ غالباً حماية ومراكز هيدج، مش رهان هابط بالضرورة.") if near["pc_oi"] > 1.1 else
                      _ot("more calls than puts; seen with optimism or with covered-call selling, not necessarily a rise.", "calls أكتر من puts؛ بيحصل مع التفاؤل أو مع بيع calls مغطاة، مش بالضرورة صعود.") if near["pc_oi"] < 0.8 else _ot("roughly balanced.", "متوازنة تقريباً.")))
    if near["max_pain"] and s["spot"]:
        dist = (near["max_pain"] / s["spot"] - 1) * 100
        lines.append(_ot(f"Max pain = {near['max_pain']:,.0f} ({dist:+.1f}% from the price). The pull toward it tends to matter only in the last day or two before expiry.",
                         f"الـ max pain = {near['max_pain']:,.0f} ({dist:+.1f}% عن السعر). نظرية الشد ناحيته بتبقى ذات معنى في آخر يوم أو يومين قبل الاستحقاق بس."))
    wk = next((e for e in ex if e["days"] >= 7 and e["skew10"] is not None), None)   # the 1-day wings are illiquid, so skew is read from >= 7 days
    if wk:
        lines.append(_ot(f"Skew for the {wk['exp']} expiry (put IV 10% below minus call IV 10% above) = ", f"السكيو لاستحقاق {wk['exp']} (IV بوت 10% تحت ناقص IV كول 10% فوق) = ") + f"{wk['skew10']:+.1f}: " +
                     (_ot("the market pays more for protection against a fall.", "السوق بيدفع أكتر للحماية من النزول.") if wk["skew10"] > 3 else _ot("the market pays more for upside.", "السوق بيدفع أكتر للصعود.") if wk["skew10"] < -3 else _ot("no clear tilt.", "مفيش ميل واضح.")))
    if rk:
        lines.append(_ot(f"IV rank over one year = {rk['rank']:.0f}% (DVOL {rk['now']} between a low of {rk['min']} and a high of {rk['max']}): ", f"الـ IV rank سنة = {rk['rank']:.0f}% (الـ DVOL {rk['now']} بين أقل {rk['min']} وأعلى {rk['max']}): ") +
                     (_ot("implied volatility is cheap relative to the year; options are not expensive and the market is not pricing stress.", "التقلب الضمني رخيص نسبياً مقارنة بالسنة؛ الأوبشنز غير غالية، والسوق مش مسعّر توتر.") if rk["rank"] < 25 else
                      _ot("implied volatility is expensive relative to the year; the market is pricing stress or an event.", "التقلب الضمني غالي نسبياً؛ السوق مسعّر توتر أو حدث.") if rk["rank"] > 75 else _ot("mid-range for the year.", "وسط السنة.")) + _ot(" (A description, not a signal.)", " (وصف، مش إشارة.)"))
    ivs = [e for e in ex if e["iv"] and e["days"] >= 1]
    if len(ivs) >= 3:
        lines.append(_ot("IV structure: ", "هيكل الـ IV: ") + (_ot("inverted (near expiries cost more than far ones): the market is tense in the short term.", "مقلوب (القريب أغلى من البعيد): السوق متوتر على المدى القصير.") if ivs[0]["iv"] > ivs[-1]["iv"] + 2 else
                                       _ot("normal (far expiries cost more): relative calm.", "طبيعي (البعيد أغلى): هدوء نسبي.") if ivs[-1]["iv"] > ivs[0]["iv"] + 2 else _ot("flat.", "مسطح.")))
    st.markdown(f"<div class='xo-card' dir='{'rtl' if _oa else 'ltr'}' style='line-height:24px'><b>" + _ot("Reading of the nearest expiry (context, not a signal)", "قراءة أقرب استحقاق (سياق مش إشارة)") + "</b><br>" + "<br>".join(html.escape(x) for x in lines) + "</div>", unsafe_allow_html=True)
    # GEX (gamma exposure) from the same book: call wall, put wall, gamma flip (modules/gex.py). Naive dealer sign; context, not a signal.
    def _gex_block(chain, spot, mult, title, days):
        from modules import gex as GX
        _td = _pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
        gx, tb = GX.levels(chain, spot, _td, max_days=days, mult=mult), GX.by_strike(chain, spot, _td, max_days=days, mult=mult)
        if not gx["n_contracts"]:
            st.info(L("No open interest to compute GEX."))
            return
        f = lambda v: f"{v:,.0f}" if v else "-"
        st.markdown("<div class='xo-row'>" + U.indicators(title, [
            (L("Call wall"), f(gx["call_wall"]), L("strike with the most call gamma"), None),
            (L("Put wall"), f(gx["put_wall"]), L("strike with the most put gamma"), None),
            (L("Gamma flip"), f(gx["gamma_flip"]), L("total GEX changes sign near here"), None),
            (L("Net GEX per 1% move"), f"${gx['net_gex'] / 1e6:,.1f}M", L("positive = moves dampened, negative = moves can extend"), "warn" if gx["net_gex"] < 0 else None)]) + "</div>", unsafe_allow_html=True)
        nb = tb[(tb.index >= spot * 0.8) & (tb.index <= spot * 1.2)].reset_index()
        if len(nb):
            nb["side"] = nb["net_gex"].map(lambda v: "+" if v >= 0 else "-")
            bars = alt.Chart(nb).mark_bar().encode(x=alt.X("strike:Q", title=L("Strike")), y=alt.Y("net_gex:Q", title="GEX $ / 1%"),
                                                   color=alt.Color("side:N", scale=alt.Scale(domain=["+", "-"], range=["#e3a857", "#b8574a"]), legend=None), tooltip=["strike", "call_gex", "put_gex", "net_gex"])
            marks = [alt.Chart(_pd.DataFrame({"x": [spot]})).mark_rule(color="#eaecef", strokeDash=[6, 4]).encode(x="x:Q")]
            if gx["gamma_flip"]:
                marks.append(alt.Chart(_pd.DataFrame({"x": [gx["gamma_flip"]]})).mark_rule(color="#a78bfa", strokeDash=[2, 3]).encode(x="x:Q"))
            ch_ = bars
            for m_ in marks:
                ch_ = ch_ + m_
            st.altair_chart(ch_.properties(height=220), width="stretch")
            st.caption(L("Gold = positive GEX, rust = negative; white dashed = spot, purple dotted = gamma flip."))
        st.caption(L("GEX assumes dealers are long the calls and short the puts the public holds; public data cannot confirm who is long or short, and providers disagree. Context, not a trade signal."))
    st.markdown(f"<div class='xo-h'>{html.escape(L('Gamma exposure (GEX)'))}</div>", unsafe_allow_html=True)
    try:
        _gex_block(OD.gex_chain(rows), s["spot"], 1, f"GEX · {cur} · " + L("expiries up to 45 days"), 45)
    except Exception as _e:
        st.warning(f"GEX: {type(_e).__name__}: {_e}")
    with st.expander(L("GEX for a US index / stock (Cboe, 15 min delayed)")):
        _us = (st.text_input(L("Symbol"), value="SPX", key="od_gex_us") or "SPX").strip().upper()
        if st.button(L("Load"), key="od_gex_us_go"):
            try:
                from modules import cboe_options as CB
                _px, _chain = CB.fetch(_us)
                if not _px:
                    st.warning(L("Cboe sent no underlying price."))
                else:
                    _gex_block(_chain, float(_px), 100, f"GEX · {_us} · Cboe · " + L("expiries up to 30 days"), 30)
            except Exception as _e:
                st.warning(f"Cboe: {type(_e).__name__}: {_e}")
    st.caption(L("The open interest and volume do not say if a trade opened or closed a position, or whether it was a hedge or a bet; put/call and walls are context. IV rank uses Deribit's DVOL daily history. Free Deribit data, about 2 minutes old. Educational, not investment advice."))


def _office_regime():
    """Technical Office > Macro regime: risk-on / neutral / risk-off from five FRED series (modules/fred_regime.py), walk-forward with
    publication delays (no look-ahead). A description of financial conditions, not a trade signal."""
    import altair as alt
    import pandas as _pd
    from modules import office_ui as U, fred_regime as FR
    st.markdown(U.CSS, unsafe_allow_html=True)

    @st.cache_data(ttl=6 * 3600, show_spinner=False)
    def _load():
        return FR.load_all()
    frames, errs = _load()
    if errs:
        st.caption(L("Not loaded: ") + ", ".join(errs))
    if not frames:
        st.warning(L("FRED did not answer; try again later."))
        return
    now = _pd.Timestamp.now(tz="UTC").tz_localize(None)
    r = FR.regime_at(frames, now)
    if r["score"] is None:
        st.info(L("Not enough FRED history yet."))
        return
    names = {"risk-on": L("Risk on"), "neutral": L("Neutral"), "risk-off": L("Risk off")}
    items = [(L("Regime now"), names[r["regime"]], L("score") + f" {r['score']:+.2f} · {r['n']}/5 " + L("series"), "warn" if r["regime"] == "risk-off" else None)]
    items += [(L(p["label"]), f"{p['value']:.2f}", f"z {p['z']:+.2f} · " + L("known since") + f" {p['known_since'].date()}", "warn" if p["contrib"] > 1 else None) for p in r["parts"]]
    st.markdown("<div class='xo-row'>" + U.indicators(L("Macro regime (FRED)"), items) + "</div>", unsafe_allow_html=True)
    h = FR.history(frames, start=now - _pd.DateOffset(years=3), end=now)
    if len(h):
        line = alt.Chart(h).mark_line(color="#e3a857").encode(x=alt.X("date:T", title=None), y=alt.Y("score:Q", title=L("Stress score")), tooltip=["date:T", "score:Q", "regime:N"])
        rules = alt.Chart(_pd.DataFrame({"y": [FR.TH, -FR.TH]})).mark_rule(color="#8f877a", strokeDash=[4, 4]).encode(y="y:Q")
        st.altair_chart((line + rules).properties(height=240), width="stretch")
        cnt = h["regime"].value_counts()
        st.caption(L("Last 3 years, weekly: ") + " · ".join(f"{names.get(k, k)} {int(v)}" for k, v in cnt.items()))
    st.caption(L("Each point uses only data that was public on that day (publication delay 1 day for the daily series, 5-7 days for the weekly ones); every series is compared with its own previous 252 values. Above +0.5 = risk off, below -0.5 = risk on. A description of financial conditions, not a trade signal: it has not been backtested as a timing rule. Free FRED data, no key."))


def render_page():   # Trading > Options & macro (2026-11-09, moved out of the Technical Office): macro regime first (short), then the options desk + GEX
    st.markdown(kit_css(), unsafe_allow_html=True)
    for _nm, _fn in (("Macro regime", _office_regime), ("Options desk", _office_options)):
        try:
            _fn()
        except Exception as _om_exc:
            st.error(f"{_nm}: {type(_om_exc).__name__}: {_om_exc}")
        if _nm == "Macro regime":
            st.divider()
    st.stop()
