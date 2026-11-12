"""Spot desk page (PAGE 11, next to the Radar; owner 2026-11-06).

Tabs: Crypto (OKX spot list like the watchlist + high-timeframe plan) / Metals (gold, silver, platinum, palladium, copper
in USD and EGP, karats) / Ledger & invoices (buys + sells, PDF upload, print, Excel) / Alerts (buy / sell / stop,
Telegram) / News & sources.
Storage, Excel & fields: online store (modules/spot_store.py: private GitHub repo when SPOT_GH_* are set, else the local
disk), ZIP backup / restore, Excel export / template / import with saved column matching, the owner's custom fields.
Nothing here places an order."""
from __future__ import annotations

import io
import json
import math
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from modules import spot_core as C

STORE = None   # tests / callers can set a store; otherwise spot_store.get_store() (GitHub when SPOT_GH_* exist, else local disk)
METAL_LIST = list(C.METALS)


def T(en: str, ar: str) -> str:
    try:
        from modules.i18n import lang
        return ar if lang() == "ar" else en
    except Exception:
        return en


# ---------------------------------------------------------------- storage
def _store():
    global STORE
    if STORE is None:
        from modules.spot_store import get_store
        STORE = get_store()
    return STORE


def _empty() -> dict:
    return {"txs": [], "alerts": [], "sources": [], "settings": {"budget": 1000.0, "fx_manual": None, "tg_auto": False, "custom_fields": [],
                                                              "import_forms": {}, "visible_cols": []}}


def load(force: bool = False) -> dict:
    if force or "spot_db" not in st.session_state:
        d = _empty()
        try:
            got = _store().load()
            if got:
                d.update(got)
                d["settings"] = {**_empty()["settings"], **got.get("settings", {})}
        except Exception as e:
            st.error(T("Could not read the ledger", "مقدرتش أقرا السجل") + f": {e}")
        st.session_state["spot_db"] = d
    return st.session_state["spot_db"]


def save(d: dict, msg: str = "") -> bool:
    st.session_state["spot_db"] = d
    try:
        _store().save(d, msg)
        return True
    except Exception as e:
        st.error(T("NOT saved", "ماتحفظش") + f": {e}")
        return False


def backup_zip(d: dict) -> bytes:
    bio = io.BytesIO()
    s = _store()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("ledger.json", json.dumps(d, ensure_ascii=False, indent=1))
        for f in sorted({f for t in d["txs"] for f in t.get("files", [])}):
            b = s.get_file(f)
            if b is not None:
                z.writestr(f"files/{f}", b)
    return bio.getvalue()


def restore_zip(data: bytes) -> dict:
    s = _store()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        d = _empty()
        got = json.loads(z.read("ledger.json").decode("utf8"))
        d.update(got)
        d["settings"] = {**_empty()["settings"], **got.get("settings", {})}
        for n in z.namelist():
            if n.startswith("files/") and not n.endswith("/"):
                s.put_file(Path(n).name, z.read(n))   # no path parts from the archive
    return d


# ---------------------------------------------------------------- shared prices
def _fx(d: dict) -> tuple[float | None, str]:
    from modules import spot_data
    man = d["settings"].get("fx_manual")
    if man:
        return float(man), T("manual rate", "سعر يدوي")
    r = spot_data.usd_egp()
    if r.get("rate"):
        return r["rate"], f"{r['src']} · {r['time']} UTC"
    return None, T("USD/EGP unavailable", "سعر الدولار مش متاح") + f" ({r.get('error', '')})"


def _prices() -> tuple[dict, dict, list]:
    """({asset: USD price}, metals detail, crypto rows)."""
    from modules import spot_data
    px, met, cr = {}, {}, []
    try:
        met = spot_data.metal_prices()
        px.update({a: v["px"] for a, v in met.items()})
    except Exception:
        pass
    try:
        cr = spot_data.crypto_tickers()
        px.update({r["base"]: r["last"] for r in cr})
    except Exception:
        pass
    return px, met, cr


def _n(x, nd=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if x == 0:
        return "0"
    if abs(x) >= 100000:
        return f"{x:,.0f}"
    return f"{x:,.{nd}f}" if abs(x) >= 1 else f"{x:,.6f}"


# ---------------------------------------------------------------- plan view (shared by crypto + metals)
@st.cache_data(ttl=3600, show_spinner=False)
def _plan_for(hist_sym: str) -> dict:
    from modules import spot_data, spot_plan
    frames, errs = {}, []
    for tf in ("1d", "1w", "1mo"):
        try:
            frames[tf] = spot_data.candles(hist_sym, tf, 300)
        except Exception as e:
            errs.append(f"{tf}: {type(e).__name__}")
    y = spot_data.yearly(frames["1mo"]) if "1mo" in frames else None
    p = spot_plan.plan(frames, y)
    p["errors"] = errs
    p["bars"] = {tf: len(df) for tf, df in frames.items()}
    p["years"] = 0 if y is None else len(y)
    return p


def _plan_card(p: dict, lad: list, k: float, cur: str) -> str:
    """The trade split as one visible card: 3 staged buys (30/30/40), take-profit targets, invalidation (owner 2026-11-06:
    'I do not see the trade split')."""
    A, D, P, L = "#f7b500", "#8d93a0", "#15171a", "#2a2d33"
    def box(title, inner):
        return (f'<div style="flex:1;min-width:230px;background:{P};border:1px solid {L};border-radius:8px;padding:12px">'
                f'<div style="color:{D};font-size:12px;letter-spacing:.06em;margin-bottom:8px">{title}</div>{inner}</div>')
    buys = "".join(f'<div style="display:flex;justify-content:space-between;background:{A};color:#111;border-radius:5px;padding:8px 10px;margin-top:6px;font-weight:700">'
                   f'<span>{T("Buy", "شراء")} {i + 1} · {w}% · {_n(r["usd"] * k)} {cur}</span><span dir="ltr">{_n(r["price"] * k)}</span></div>'
                   for i, (r, w) in enumerate(zip(lad, (30, 30, 40))))
    avg = C.ladder_avg(lad)
    buys += f'<div style="color:{D};font-size:12px;margin-top:6px">{T("Average if all fill", "المتوسط لو الكل اتنفذ")}: <b dir="ltr">{_n(avg * k) if avg else "—"}</b> {cur}</div>'
    tps = "".join(f'<div style="display:flex;justify-content:space-between;border:1px solid {A};color:{A};border-radius:5px;padding:8px 10px;margin-top:6px;font-weight:700">'
                  f'<span>T{i + 1} · <span dir="ltr">{(x / p["price"] - 1) * 100:+.1f}%</span></span><span dir="ltr">{_n(x * k)}</span></div>' for i, x in enumerate(p["sells"]))
    inv = (f'<div style="font-size:26px;font-weight:800;color:#e05a5a" dir="ltr">{_n((p["invalidation"] or 0) * k)}</div>'
           f'<div style="color:{D};font-size:12px">{T("Weekly close below it = plan void, stop adding.", "قفلة أسبوعية تحته = الخطة تتلغي ووقف الشراء.")}</div>')
    return (f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 10px">{box(T("TRADE SPLIT - STAGED BUYS", "تقسيم الصفقة - الشراء على دفعات"), buys or "—")}'
            f'{box(T("TAKE PROFIT", "جني الربح"), tps or "—")}{box(T("INVALIDATION", "الإلغاء"), inv)}</div>')


def _show_plan(asset: str, hist_sym: str, d: dict, live_px: float | None, fx: float | None, egp: bool):
    from modules.spot_plan import ACTION_TXT
    with st.spinner(T("Reading 1D / 1W / 1M with the schools ...", "بقرا اليومي والويكلي والشهري بالمدارس ...")):
        p = _plan_for(hist_sym)
    if not p.get("ok"):
        st.warning(p.get("why", "") + (" · " + ", ".join(p.get("errors", [])) if p.get("errors") else ""))
        return
    k = (fx if egp and fx else 1.0)
    cur = "EGP" if egp and fx else "USD"
    a, b, c3, d4 = st.columns(4)
    a.metric(T("Schools score", "درجة توافق المدارس"), f"{p['score']:+d}", help=T("-100..100, 1M x3 / 1W x2 / 1D x1", "-100 لـ 100، الشهري ×3 والويكلي ×2 واليومي ×1"))
    en, ar = ACTION_TXT[p["action"]]
    b.metric(T("Price (history source)", "السعر (مصدر التاريخ)"), _n(p["price"] * k))
    c3.metric(T("Invalidation (weekly close)", "الإلغاء (قفلة ويكلي)"), _n((p["invalidation"] or 0) * k))
    d4.metric(T("Turn window (Gann time)", "نافذة انعكاس زمنية (جان)"), ", ".join(p["time_turn"]) or "—")
    tone = {"accumulate": st.success, "hold_buy_dips": st.info, "take_profit_wait": st.warning, "wait": st.info}[p["action"]]
    tone(T("Action", "الإجراء") + ": **" + T(en, ar) + "**")
    if live_px and abs(live_px / p["price"] - 1) > 0.02:
        st.caption(T(f"History source closes at {_n(p['price'])}; live price {_n(live_px)} (perp / futures vs spot differ).",
                     f"مصدر التاريخ قافل على {_n(p['price'])} والسعر اللايف {_n(live_px)} (الفيوتشر/البيربتشوال بيختلف شوية عن السبوت)."))
    bc, _ = st.columns([1, 3])
    budget = bc.number_input(T("Budget (USD)", "الميزانية (دولار)"), min_value=0.0, value=float(d["settings"].get("budget", 1000.0)),
                             step=100.0, key=f"sp_bud_{asset}")
    lad = C.ladder(p["buys"], budget)
    st.markdown(_plan_card(p, lad, k, cur), unsafe_allow_html=True)
    st.caption(T("Backtest (Mondays, 22 markets): the score alone did NOT pick better entries - use the levels, not the score, and size small.",
                 "الباك تيست (كل اتنين، 22 سوق): الدرجة لوحدها ماختارتش نقط دخول أحسن - اشتغل بالمستويات مش بالدرجة، وبكمية صغيرة."))
    vt = {1: "🟢", -1: "🔴", 0: "⚪"}
    st.dataframe(pd.DataFrame([{"TF": r["tf"], T("Trend", "الاتجاه"): vt[r.get("v_trend", 0)] if r["available"] else T("no data", "مفيش داتا"),
                                "Elliott": vt.get(r.get("v_elliott", 0)), "SMC / ICT": vt.get(r.get("v_smc_ict", 0)),
                                T("Regime", "حالة السوق"): r.get("regime"), T("Gann cycle (bars)", "دورة جان (شمعات)"): r.get("gann_cycle"),
                                T("Next turn in", "الانعكاس الجاي بعد"): r.get("gann_turn_in"), T("Signals", "الإشارات"): " · ".join(r.get("notes", [])[:3])}
                               for r in p["rows"]]), hide_index=True, width="stretch")
    st.caption(T(f"Bars: {p['bars']} · yearly bars: {p['years']}. Not backtested as a combination - a structured reading, not evidence. Spot = buy only.",
                 f"الشمعات: {p['bars']} · السنوي: {p['years']} شمعة. التركيبة دي لسه ماتعملهاش باك تيست - قراية منظمة مش دليل. السبوت شراء بس."))
    if st.button(T("Add alerts from this plan (buy levels, T1, invalidation)", "اعمل تنبيهات من الخطة (مستويات الشراء، الهدف الأول، الإلغاء)"), key=f"sp_al_{asset}"):
        for i, r in enumerate(lad):
            d["alerts"].append(C.new_alert(asset, "buy", r["price"], f"#{i + 1}"))
        if p["sells"]:
            d["alerts"].append(C.new_alert(asset, "sell", p["sells"][0], "T1"))
        if p["invalidation"]:
            d["alerts"].append(C.new_alert(asset, "stop", p["invalidation"], ""))
        if save(d):
            st.success(T("Alerts added - see the Alerts tab.", "التنبيهات اتضافت - شوف تاب التنبيهات."))
            _notify(d, T(f"{len(lad) + 2} plan alerts armed for {asset}", f"اتسجلت تنبيهات الخطة لـ {asset}: شراء " + " / ".join(_n(r["price"]) for r in lad)
                         + (f" · هدف {_n(p['sells'][0])}" if p["sells"] else "") + (f" · إلغاء {_n(p['invalidation'])}" if p["invalidation"] else "")))


# ---------------------------------------------------------------- tabs
@st.cache_data(ttl=900, show_spinner=False)
def _bundle(asset: str) -> dict:
    from modules import spot_dash
    return spot_dash.load_bundle(asset)


def _tab_analyzer(cr, met):
    """Spot analyzer: pick a symbol -> 1M / 1W / 1D / 4H charts with every school + confluence (modules/spot_dash.py)."""
    a, b = st.columns([3, 1])
    metals = [m for m in METAL_LIST]
    coins = [r["base"] for r in cr[:200]] or ["BTC", "ETH", "SOL"]
    opts = metals + [c for c in coins if c not in metals]
    pick = a.selectbox(T("Symbol", "الرمز"), opts, index=opts.index("BTC") if "BTC" in opts else 0, key="sp_an_sym",
                       format_func=lambda x: T(x.title(), C.METAL_NAMES_AR[x]) if x in C.METAL_NAMES_AR else x)
    if b.button(T("Refresh", "تحديث"), key="sp_an_ref"):
        _bundle.clear()
    with st.spinner(T("Loading 1M / 1W / 1D / 4H and reading every school ...", "بحمّل الشهري والأسبوعي واليومي والـ 4 ساعات وبقرا كل المدارس ...")):
        try:
            bd = _bundle(pick)
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
            return
    if bd.get("errors"):
        st.caption(T("Missing frames: ", "فريمات ناقصة: ") + ", ".join(bd["errors"]))
    if not any(r.get("ok") for r in bd["reads"].values()):
        st.warning(T("No candles for this symbol right now.", "مفيش شموع للرمز ده دلوقتي."))
        return
    from modules import spot_dash
    from modules.i18n import lang
    import streamlit.components.v1 as components
    components.html(spot_dash.render(bd, lang() == "ar"), height=2450, scrolling=True)


def _tab_library():
    """Every setup of every school the spot desk knows + its weekly lab evidence (modules/spot_setups.py)."""
    from modules import spot_setups as SS
    rows = SS.library()
    run = "—"
    try:
        run = json.loads(SS.EVIDENCE.read_text(encoding="utf8")).get("run", "—")
    except Exception:
        pass
    st.caption(T(f"{len(rows)} setups. Weekly lab (Mondays): every setup on 1W and 1D, walk-forward on 18 markets; 'worked' needs n >= 30 and t >= 3. Last run: {run}",
                 f"{len(rows)} سيت أب. المعمل الأسبوعي (كل اتنين): كل سيت أب على الأسبوعي واليومي على 18 سوق من غير ما يشوف المستقبل؛ «اشتغل» محتاج 30 مرة على الأقل و t ≥ 3. آخر تشغيل: {run}"))
    schools = sorted({r["school"] for r in rows})
    pick = st.multiselect(T("Schools", "المدارس"), schools, default=schools, key="sp_lib_sch")
    q = st.text_input(T("Search", "بحث"), key="sp_lib_q").strip().lower()
    show = [r for r in rows if r["school"] in pick and (not q or q in (r["name"] + r["id"] + r.get("why", "")).lower())]
    st.dataframe(pd.DataFrame([{T("School", "المدرسة"): r["school"], T("Setup", "السيت أب"): r["name"], T("Side", "النوع"): r["side"], T("Source", "المصدر"): r["source"],
                                T("Evidence", "النتيجة"): " · ".join(f"{k}: {v}" for k, v in r["evidence"].items()), T("Meaning", "معناه"): r.get("why", "")} for r in show]),
                 hide_index=True, width="stretch", height=520)
    st.caption(T("Adding a setup = one rule in spot_setups.py (CATALOG + spot_only); the next Monday lab measures it automatically. New ideas are reviewed by the school-review job (topic 'spot_setups').",
                 "إضافة سيت أب = قاعدة واحدة في spot_setups.py (CATALOG + spot_only)، ومعمل الاتنين اللي بعده بيقيسه لوحده. الأفكار الجديدة بتتراجع في مهمة مراجعة المدارس (موضوع spot_setups)."))


@st.cache_data(ttl=1800, show_spinner=False)
def _brain(asset: str, cls: str, name: str, holdings_key: str) -> dict:
    import json as _j
    from modules import spot_brain
    return spot_brain.run(asset, cls, name, holdings=_j.loads(holdings_key))


def _tab_brain(d, px, met, cr, fx):
    """Spot brain: one market -> day / week / month / year verdicts, order flow, institutions, holdings guard (mosaic)."""
    from modules.spot_ideas import UNIVERSE
    uni = list(UNIVERSE) + [(r["base"], "crypto", r["base"]) for r in cr[:30] if r["base"] not in {u[0] for u in UNIVERSE}]
    a, b = st.columns([4, 1])
    pick = a.selectbox(T("Market", "السوق"), range(len(uni)), format_func=lambda i: f"{uni[i][2]} · {uni[i][0]}", key="sp_br_pick")
    if b.button(T("Refresh", "تحديث"), key="sp_br_ref"):
        _brain.clear()
    asset, cls, name = uni[pick]
    import json as _j
    pos = [{k: p.get(k) for k in ("asset", "qty", "avg_usd", "unreal_pct")} for p in C.positions(d["txs"], px, fx)]
    with st.spinner(T("Thinking: schools, order flow, institutions, news ...", "بفكر: المدارس والأوردر فلو والمؤسسات والأخبار ...")):
        try:
            br = _brain(asset, cls, name, _j.dumps(pos, default=str))
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
            return
    marks = []
    for u in UNIVERSE:
        if u[0] in met and met[u[0]].get("prev"):
            marks.append({"name": u[2], "price": met[u[0]]["px"], "wk": (met[u[0]]["px"] / met[u[0]]["prev"] - 1) * 100, "score": 0})
        r = next((r for r in cr if r["base"] == u[0]), None)
        if r:
            marks.append({"name": u[2], "price": r["last"], "wk": r["chg24"] or 0, "score": 0})
    for m in marks:
        m["score"] = 20 if m["wk"] > 0.3 else -20 if m["wk"] < -0.3 else 0
    from modules import spot_brain_view
    import streamlit.components.v1 as components
    components.html(spot_brain_view.render(br, marks), height=1400, scrolling=True)
    with st.expander(T("How it decided (thinking log)", "فكّر إزاي (سجل التفكير)")):
        for k, h in br["horizons"].items():
            st.markdown(f"**{h['label']}: {h['verdict_ar']} ({h['score']:+d})** - " + " · ".join(h["reasons"]))
        st.markdown("\n".join(br.get("log", [])))
    st.caption(T("24 h change used for the market list (weekly in the brain). Rules, not backtested per horizon yet.",
                 "قايمة الأسواق بتغير 24 ساعة (العقل نفسه بالأسبوعي). قواعد، لسه من غير باك تيست لكل مدة."))


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _desk(day: str) -> dict:
    from modules import spot_ideas
    return spot_ideas.desk()


def _tab_ideas():
    """Daily ideas desk (modules/spot_ideas.py + spot_board.py), refreshed every 6 h or on Refresh."""
    a, b = st.columns([4, 1])
    a.caption(T("Reads 8 markets on 1M / 1W / 1D / 4H with every school + the news, then builds spot ideas. First load ~30 s, then cached 6 h.",
                "بيقرا 8 أسواق على الشهري والأسبوعي واليومي والـ 4 ساعات بكل المدارس + الأخبار ويطلع أفكار سبوت. أول تحميل حوالي 30 ثانية وبعدها محفوظ 6 ساعات."))
    if b.button(T("Refresh", "تحديث"), key="sp_id_ref"):
        _desk.clear()
    with st.spinner(T("Thinking: reading every market and school ...", "بفكر: بقرا كل سوق وكل مدرسة ...")):
        try:
            r = _desk(date.today().isoformat())
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
            return
    from modules import spot_board
    import streamlit.components.v1 as components
    components.html(spot_board.render(r), height=3700, scrolling=True)
    if st.button(T("Send today's ideas to Telegram", "ابعت أفكار النهارده على تليجرام"), key="sp_id_tg"):
        from modules import spot_ideas, telegram_alerts
        err = telegram_alerts.send(spot_ideas.telegram_text(r))
        (st.error if err else st.success)(f"Telegram: {err}" if err else T("Sent.", "اتبعت."))


def _tab_crypto(d, cr, fx):
    if not cr:
        st.warning(T("OKX spot list unavailable right now.", "قايمة OKX سبوت مش متاحة دلوقتي."))
        return
    a, b, c3 = st.columns([1, 2, 1])
    top = a.selectbox(T("Show", "اعرض"), ["50", "100", "200", T("All", "الكل")], key="sp_top")
    q = b.text_input(T("Search", "بحث"), key="sp_q").strip().upper()
    b2b = c3.toggle(T("EGP (B2B)", "بالجنيه (B2B)"), key="sp_cr_egp", help=T("Crypto is shown in USD; this shows EGP too", "الكريبتو أساسًا بالدولار؛ ده بيضيف الجنيه"))
    rows = [r for r in cr if not q or q in r["base"]]
    if top.isdigit():
        rows = rows[:int(top)]
    pick = st.selectbox(T("Plan for", "خطة لـ"), [r["base"] for r in rows] or ["BTC"], key="sp_cr_pick")
    live = next((r["last"] for r in cr if r["base"] == pick), None)
    _show_plan(pick, f"{pick}-USDT", d, live, fx, b2b)
    with st.expander(T(f"Coin list ({len(rows)})", f"قايمة العملات ({len(rows)})")):
        df = pd.DataFrame([{"#": i + 1, T("Coin", "العملة"): r["base"], "USD": r["last"], "24h %": None if r["chg24"] is None else round(r["chg24"], 2),
                            T("Volume 24h (USD)", "الفوليوم 24 ساعة"): round(r["vol_usd"])} | ({"EGP": round(r["last"] * fx, 4)} if b2b and fx else {})
                           for i, r in enumerate(rows)])
        st.dataframe(df, hide_index=True, width="stretch", height=320)
    with st.expander(T("Scan the list (plan score for each coin)", "مسح القايمة (درجة الخطة لكل عملة)")):
        n = st.slider(T("How many coins (biggest volume first)", "كام عملة (الأكبر فوليوم الأول)"), 5, 60, 20, key="sp_scan_n")
        if st.button(T("Run the scan", "شغّل المسح"), key="sp_scan"):
            out, bar = [], st.progress(0.0)
            for i, r in enumerate(cr[:n]):
                p = _plan_for(r["sym"])
                bar.progress((i + 1) / n)
                if p.get("ok"):
                    out.append({T("Coin", "العملة"): r["base"], T("Score", "الدرجة"): p["score"], T("Action", "الإجراء"): p["action"],
                                T("Buy 1", "شراء 1"): _n(p["buys"][0]) if p["buys"] else "—", "T1": _n(p["sells"][0]) if p["sells"] else "—"})
            st.session_state["sp_scan_out"] = sorted(out, key=lambda x: -x[T("Score", "الدرجة")])
        if st.session_state.get("sp_scan_out"):
            st.dataframe(pd.DataFrame(st.session_state["sp_scan_out"]), hide_index=True, width="stretch")


def _tab_metals(d, met, fx, fx_src, egp):
    st.caption(T("USD/EGP", "سعر الدولار") + f": **{_n(fx, 3) if fx else '—'}** · {fx_src}")
    with st.expander(T("Exchange rate source / manual rate", "مصدر سعر الصرف / سعر يدوي")):
        man = st.number_input(T("Manual USD/EGP (0 = automatic)", "سعر دولار يدوي (0 = تلقائي)"), min_value=0.0, value=float(d["settings"].get("fx_manual") or 0), step=0.05, key="sp_fxman")
        if st.button(T("Save rate", "احفظ السعر"), key="sp_fxsave"):
            d["settings"]["fx_manual"] = man or None
            save(d)
            st.rerun()
    if not met:
        st.warning(T("Metal prices unavailable (Hyperliquid and Yahoo unreachable).", "أسعار المعادن مش متاحة (Hyperliquid وYahoo مش واصلين)."))
        return
    rows = []
    for a in METAL_LIST:
        m = met.get(a)
        if not m:
            continue
        chg = (m["px"] / m["prev"] - 1) * 100 if m.get("prev") else None
        for r in C.per_unit_prices(a, m["px"], fx):
            unit = "lb" if a == "COPPER" else "oz"
            row = {T("Metal", "المعدن"): T(a.title(), C.METAL_NAMES_AR[a]), T("Purity", "العيار"): r["purity"], T("Unit", "الوحدة"): unit,
                   T("USD / unit", "دولار / وحدة"): round(r[f"usd_{unit}"], 2), "USD/g": round(r["usd_g"], 3), "USD/kg": round(r["usd_kg"], 1),
                   "24h %": None if chg is None else round(chg, 2)}
            if fx:
                row |= {T("EGP / unit", "جنيه / وحدة"): round(r[f"egp_{unit}"], 1), "EGP/g": round(r["egp_g"], 2), "EGP/kg": round(r["egp_kg"], 0)}
            rows.append(row)
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption(T("Source per metal", "المصدر لكل معدن") + ": " + " · ".join(f"{a}: {m['src']}" for a, m in met.items()) +
               T(". Computed prices: shop prices in Egypt add workmanship and a local premium.", ". أسعار محسوبة: سعر المحل في مصر بيزود مصنعية وفرق سوق محلي."))
    if fx and met.get("GOLD"):
        g21 = C.per_unit_prices("GOLD", met["GOLD"]["px"], fx)[1]["egp_g"]
        shop = st.number_input(T("Shop price of 21K gold today (EGP / g) - optional", "سعر جرام 21 في المحل النهارده (جنيه) - اختياري"), min_value=0.0, step=5.0, key="sp_shop21")
        gap = C.local_gap(g21, shop)
        if gap is not None:
            st.info(T(f"Computed 21K = {g21:,.2f} EGP/g · shop {shop:,.2f} · gap {gap:+.2f}%", f"21 المحسوب = {g21:,.2f} جنيه/جرام · المحل {shop:,.2f} · الفرق {gap:+.2f}%"))
    st.divider()
    pick = st.selectbox(T("Plan for", "خطة لـ"), [a for a in METAL_LIST if a in met], format_func=lambda a: T(a.title(), C.METAL_NAMES_AR[a]), key="sp_mt_pick")
    from modules import spot_data
    _show_plan(pick, spot_data.METAL_Y[pick], d, met[pick]["px"], fx, egp)


FIELD_META = {k: (en, ar, t, o) for k, en, ar, t, o in C.FIELDS}
PURITY_PICK = {"24K / 999.9": 1.0, "999": 0.999, "21K (875)": 0.875, "18K (750)": 0.75, "925": 0.925, "950": 0.95, "900": 0.9}
MAIN_KEYS = ["side", "asset", "date", "item_type", "qty", "unit", "price", "currency", "fx"]
COST_KEYS = ["workmanship_per_g", "fees", "tax", "other_costs", "gross_weight"]


OPT_AR = {"buy": "شراء", "sell": "بيع", "bar": "سبيكة", "coin": "عملة / جنيه ذهب", "jewelry": "مشغولات", "scrap": "كسر", "crypto": "كريبتو",
          "other": "تاني", "cash": "كاش", "bank": "تحويل بنكي", "instapay": "انستاباي", "card": "كارت", "settled": "متسوّي", "pending": "معلّق",
          "cancelled": "ملغي", "Exchange": "منصة"}


def _lab(k: str) -> str:
    en, ar, _, _ = FIELD_META[k]
    return T(en, ar)


def _widget(k: str, val, key: str, fx=None):
    """One input for a standard field, typed by the schema."""
    en, ar, t, opts = FIELD_META[k]
    lab = T(en, ar)
    if t == "select":
        opts = list(opts)
        return st.selectbox(lab, opts, index=opts.index(val) if val in opts else 0, key=key,
                            format_func=lambda o: T(o, OPT_AR.get(o, o)) if not (k == "unit" and o == "coin") else T("coin", "عملة"))
    if t == "number":
        v = float(val) if isinstance(val, (int, float)) and not (isinstance(val, float) and math.isnan(val)) else (float(fx) if k == "fx" and fx else 0.0)
        return st.number_input(lab, value=v, step=0.01 if k in ("qty", "gross_weight") else 1.0, format="%.6f" if k in ("qty", "gross_weight") else "%.4f", key=key)
    if t == "date":
        try:
            dv = date.fromisoformat(str(val)[:10]) if val else (date.today() if k == "date" else None)
        except ValueError:
            dv = date.today()
        return st.date_input(lab, value=dv, key=key)
    return st.text_input(lab, value=str(val or ""), key=key)


def _custom_widget(c: dict, val, key: str):
    t = c.get("type", "text")
    if t == "number":
        try:
            v = float(val)
        except (TypeError, ValueError):
            v = 0.0
        return st.number_input(c["label"], value=v, key=key)
    if t == "date":
        try:
            return st.date_input(c["label"], value=date.fromisoformat(str(val)[:10]) if val else None, key=key)
        except ValueError:
            return st.date_input(c["label"], value=None, key=key)
    if t == "select":
        opts = [o.strip() for o in str(c.get("options", "")).split(",") if o.strip()] or [""]
        return st.selectbox(c["label"], opts, index=opts.index(val) if val in opts else 0, key=key)
    return st.text_input(c["label"], value=str(val or ""), key=key)


def _record_form(d: dict, fx, tx: dict | None = None):
    """Add (tx None) or edit one record. Every standard field + the owner's custom fields + files."""
    base = tx or C.new_tx(fx=fx)
    pre = f"spe_{tx['id']}_" if tx else "spn_"
    custom = d["settings"].get("custom_fields", [])
    with st.form(pre + "form", clear_on_submit=tx is None):
        vals = {}
        st.markdown("**" + T("Main", "الأساسي") + "**")
        cols = st.columns(3)
        for i, k in enumerate(MAIN_KEYS):
            with cols[i % 3]:
                vals[k] = _widget(k, base.get(k), pre + k, fx)
        c1, c2 = st.columns(2)
        with c1:
            pur_lab = next((l for l, v in PURITY_PICK.items() if abs(v - float(base.get("purity") or 1)) < 1e-9), "24K / 999.9")
            pur = st.selectbox(T("Karat / purity", "العيار / النقاوة"), list(PURITY_PICK), index=list(PURITY_PICK).index(pur_lab), key=pre + "pur")
        with c2:
            vals["invoice_no"] = _widget("invoice_no", base.get("invoice_no"), pre + "invoice_no")
        with st.expander(T("Costs and weights", "التكاليف والأوزان"), expanded=bool(tx)):
            cols = st.columns(3)
            for i, k in enumerate(COST_KEYS):
                with cols[i % 3]:
                    vals[k] = _widget(k, base.get(k), pre + k)
        with st.expander(T("Party, payment, place, references", "الطرف والدفع والمكان والمراجع"), expanded=bool(tx)):
            rest = [k for k in C.FIELD_KEYS if k not in MAIN_KEYS + COST_KEYS + ["purity", "invoice_no"]]
            cols = st.columns(3)
            for i, k in enumerate(rest):
                with cols[i % 3]:
                    vals[k] = _widget(k, base.get(k), pre + k)
        extra = dict(base.get("extra") or {})
        if custom:
            with st.expander(T("My fields", "خاناتي"), expanded=True):
                cols = st.columns(3)
                for i, c in enumerate(custom):
                    with cols[i % 3]:
                        extra[c["key"]] = _custom_widget(c, extra.get(c["key"]), pre + "x_" + c["key"])
        up = st.file_uploader(T("Invoice / receipt files (PDF, image, Excel)", "ملفات الفاتورة / الإيصال (PDF، صورة، Excel)"),
                              type=["pdf", "png", "jpg", "jpeg", "xlsx"], accept_multiple_files=True, key=pre + "up")
        if not st.form_submit_button(T("Save changes", "احفظ التعديل") if tx else T("Save", "سجّل"), type="primary"):
            return
    for k in ("date", "settlement_date"):
        if vals.get(k) is not None and hasattr(vals[k], "isoformat"):
            vals[k] = vals[k].isoformat()
    for k, v in list(extra.items()):
        if hasattr(v, "isoformat"):
            extra[k] = v.isoformat()
    vals["asset"] = str(vals.get("asset") or "").strip().upper()
    if not vals["asset"] or float(vals.get("qty") or 0) <= 0 or float(vals.get("price") or 0) <= 0:
        st.error(T("Asset, quantity and price are required.", "الأصل والكمية والسعر لازم يتكتبوا."))
        return
    vals["purity"] = PURITY_PICK[pur] if C.is_metal(vals["asset"]) else 1.0
    if not C.is_metal(vals["asset"]):
        vals["unit"] = "coin"
    if not vals.get("fx"):
        vals["fx"] = None
    rec = C.new_tx(**vals, extra=extra)
    if tx:
        rec["id"], rec["files"], rec["created"] = tx["id"], list(tx.get("files", [])), tx.get("created")
        rec["edited"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    s = _store()
    for f in up or []:
        rec["files"].append(s.put_file(f"{rec['id']}_{f.name}", f.getvalue()))
    if tx:
        d["txs"] = [rec if t["id"] == tx["id"] else t for t in d["txs"]]
    else:
        d["txs"].append(rec)
    if save(d, f"spot: {'edit' if tx else 'add'} {rec['side']} {rec['asset']} {rec.get('invoice_no') or rec['id']}"):
        st.success(T("Saved.", "اتسجل."))
        from modules.spot_query import tx_text
        _notify(d, ("✏️ " if tx else "") + tx_text(rec))


def _table(d: dict, txs: list[dict]):
    custom = d["settings"].get("custom_fields", [])
    allc = C.columns(custom)
    labels = {k: T(en, ar) for k, en, ar in allc}
    default = ["date", "side", "asset", "item_type", "qty", "unit", "purity", "price", "currency", "fx", "invoice_no", "party", "status"]
    vis = d["settings"].get("visible_cols") or default
    vis = st.multiselect(T("Columns shown (add any field)", "الأعمدة المعروضة (ضيف أي خانة)"), [k for k, _, _ in allc], default=[k for k in vis if k in labels],
                         format_func=lambda k: labels[k], key="sp_vis")
    if vis != d["settings"].get("visible_cols"):
        d["settings"]["visible_cols"] = vis
        st.session_state["spot_db"] = d
    rows = []
    for t in txs:
        r = {labels[k]: v for (k, _, _), v in zip([c for c in allc if c[0] in vis], C.row_values(t, [c for c in allc if c[0] in vis]))}
        u, fu = C.tx_usd(t)
        r[T("Costs", "التكاليف")] = round(C.costs(t), 2)
        r["USD"] = None if math.isnan(u) else round(u + (fu if t["side"] == "buy" else -fu), 2)
        r["📎"] = len(t.get("files", []))
        rows.append(r)
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def _tab_ledger(d, px, fx, egp):
    with st.expander(T("➕ New record (buy / sell)", "➕ تسجيل جديد (شراء / بيع)"), expanded=not d["txs"]):
        _record_form(d, fx)
    txs = d["txs"]
    pos = C.positions(txs, px, fx)
    tot = C.totals(pos)
    k = "egp" if egp and fx else "usd"
    a, b, c3, d4 = st.columns(4)
    a.metric(T("Cost", "التكلفة"), _n(tot[f"cost_{k}"]))
    b.metric(T("Value now", "القيمة دلوقتي"), _n(tot[f"value_{k}"]))
    c3.metric(T("Unrealized P&L", "ربح/خسارة مفتوح"), _n(tot[f"unreal_{k}"]))
    d4.metric(T("Realized P&L", "ربح/خسارة محقق"), _n(tot[f"realized_{k}"]))
    if pos:
        cols = ["asset", "qty", f"avg_{k}", f"cost_{k}", f"value_{k}", f"unreal_{k}", "unreal_pct", f"realized_{k}"] + (["metal_part_egp", "fx_part_egp"] if k == "egp" else [])
        hdr = {"asset": T("Asset", "الأصل"), "qty": T("Qty (pure)", "الكمية (صافي)"), f"avg_{k}": T("Avg cost", "متوسط التكلفة"), f"cost_{k}": T("Cost", "التكلفة"),
               f"value_{k}": T("Value", "القيمة"), f"unreal_{k}": T("Open P&L", "ربح مفتوح"), "unreal_pct": "%", f"realized_{k}": T("Realized", "محقق"),
               "metal_part_egp": T("from metal price", "من سعر المعدن"), "fx_part_egp": T("from the dollar", "من الدولار")}
        st.dataframe(pd.DataFrame([{hdr[c]: (round(p[c], 6 if c == "qty" else 2) if isinstance(p.get(c), float) else p.get(c)) for c in cols} for p in pos]),
                     hide_index=True, width="stretch")
        st.caption(T("qty = pure oz for metals (copper: lb), coins for crypto. Cancelled records are not counted.",
                     "الكمية = أونصة صافية للمعادن (النحاس رطل) وعدد العملات للكريبتو. التسجيلات الملغية مش بتتحسب."))
    if not txs:
        st.info(T("No records yet.", "مفيش تسجيلات لسه."))
        return
    q = st.text_input(T("Search any field (invoice, shop, date, serial ...)", "دوّر في أي خانة (فاتورة، محل، تاريخ، سيريال ...)"), key="sp_q_led")
    from modules.spot_query import search
    shown = search(txs, q) if q.strip() else sorted(txs, key=lambda t: str(t.get("date", "")), reverse=True)
    _table(d, shown)
    if not shown:
        return
    sel = st.selectbox(T("Record", "التسجيل"), [t["id"] for t in shown],
                       format_func=lambda i: next(f"{t['date']} · {t['side']} · {t['asset']} · {t['qty']} {t['unit']} · {t.get('invoice_no') or i}" for t in shown if t["id"] == i), key="sp_sel")
    tx = next(t for t in txs if t["id"] == sel)
    a, b, c3 = st.columns(3)
    html = C.invoice_html(tx)
    a.download_button(T("Invoice (HTML, print / save PDF)", "الفاتورة (HTML للطباعة / PDF)"), html.encode("utf8"), file_name=f"invoice_{tx.get('invoice_no') or tx['id']}.html", mime="text/html")
    if b.button(T("Print preview", "معاينة الطباعة"), key="sp_prev"):
        import streamlit.components.v1 as components
        components.html(html, height=560, scrolling=True)
    if c3.button(T("Delete record", "امسح التسجيل"), key="sp_del"):
        st.session_state["sp_del_ask"] = sel
    if st.session_state.get("sp_del_ask") == sel:
        st.warning(T("Delete this record and its files?", "تمسح التسجيل ده وملفاته؟"))
        y, n_ = st.columns(2)
        if y.button(T("Yes, delete", "أيوه امسح"), key="sp_del_yes"):
            for f in tx.get("files", []):
                try:
                    _store().delete_file(f)
                except Exception:
                    pass
            d["txs"] = [t for t in txs if t["id"] != sel]
            st.session_state.pop("sp_del_ask", None)
            save(d, f"spot: delete {tx.get('invoice_no') or sel}")
            st.rerun()
        if n_.button(T("Cancel", "إلغاء"), key="sp_del_no"):
            st.session_state.pop("sp_del_ask", None)
            st.rerun()
    for f in tx.get("files", []):
        b_ = _store().get_file(f) if st.session_state.get("sp_show_files") == sel else None
        if b_ is not None:
            st.download_button(f"📎 {f.split('_', 1)[-1]}", b_, file_name=f.split("_", 1)[-1], key=f"sp_f_{f}")
    if tx.get("files") and st.session_state.get("sp_show_files") != sel and st.button(T(f"Load {len(tx['files'])} attached file(s)", f"حمّل {len(tx['files'])} ملف مرفق"), key="sp_lf"):
        st.session_state["sp_show_files"] = sel
        st.rerun()
    with st.expander(T("✏️ Edit this record", "✏️ عدّل التسجيل ده")):
        _record_form(d, fx, tx)


def _tab_setup(d, px, fx):
    """Storage status, backups, Excel forms (template / import with column matching), custom fields."""
    s = _store()
    st.markdown("**" + T("Storage", "التخزين") + "**")
    if s.kind == "github":
        st.success(T("Online: ", "أونلاين: ") + s.describe() + T(" - every save is a commit (full history).", " - كل حفظ بيتسجل بتاريخه (history كامل)."))
    else:
        st.warning(T("Local disk only. Add SPOT_GH_TOKEN + SPOT_GH_REPO in Secrets to keep everything online (see docs/SPOT_DESK.md).",
                     "على ديسك السيرفر بس. ضيف SPOT_GH_TOKEN و SPOT_GH_REPO في Secrets عشان كله يتحفظ أونلاين (شوف docs/SPOT_DESK.md)."))
    if st.button(T("Test storage (save + read a test file)", "اختبر التخزين (يحفظ ويقرا ملف تجربة)"), key="sp_stest"):
        from modules.spot_store import self_test
        ok, why = self_test(s)
        (st.success if ok else st.error)((T("Storage works: ", "التخزين شغال: ") if ok else T("Storage FAILED: ", "التخزين فشل: ")) + why)
    if st.button(T("Reload from storage", "حمّل من التخزين تاني"), key="sp_reload"):
        load(force=True)
        st.rerun()
    a, b = st.columns(2)
    a.download_button(T("Full backup now (ZIP: ledger + files)", "نسخة احتياطية دلوقتي (ZIP: السجل + الملفات)"), backup_zip(d) if st.session_state.get("sp_zip_ok") else b"",
                      file_name=f"spot_backup_{date.today()}.zip", mime="application/zip", disabled=not st.session_state.get("sp_zip_ok"), key="sp_zip_dl")
    if not st.session_state.get("sp_zip_ok") and a.button(T("Prepare the ZIP", "جهّز الـ ZIP"), key="sp_zip_prep"):
        st.session_state["sp_zip_ok"] = True
        st.rerun()
    rz = b.file_uploader(T("Restore a backup (replaces the ledger)", "رجّع نسخة احتياطية (هتستبدل السجل)"), type=["zip"], key="sp_rz")
    if rz and b.button(T("Restore", "رجّع"), key="sp_rzb"):
        save(restore_zip(rz.getvalue()), "spot: restore from backup")
        st.rerun()
    st.caption(T("Automatic copy on your Mac every 48 h (old copy deleted after the new one is verified): tools/spot_backup (docs/SPOT_DESK.md).",
                 "نسخة أوتوماتيك على الماك كل 48 ساعة (القديمة بتتمسح بعد ما الجديدة تتأكد): tools/spot_backup (docs/SPOT_DESK.md)."))
    st.divider()
    custom = d["settings"].setdefault("custom_fields", [])
    st.markdown("**" + T("Excel", "Excel") + "**")
    a, b = st.columns(2)
    try:
        a.download_button(T("Export everything (Excel)", "صدّر كل حاجة (Excel)"), C.to_excel(d["txs"], C.positions(d["txs"], px, fx), px, fx, custom),
                          file_name=f"spot_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="sp_xl_all")
    except Exception as e:
        a.caption(f"Excel: {type(e).__name__}")
    b.download_button(T("Blank form / template (Excel)", "فورم فاضية / تمبليت (Excel)"), C.template_xlsx(custom), file_name="spot_template.xlsx",
                      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="sp_xl_tpl")
    xl = st.file_uploader(T("Import any Excel (ours or a shop / exchange sheet)", "استورد أي Excel (بتاعنا أو شيت محل / منصة)"), type=["xlsx"], key="sp_xlin")
    if xl:
        hdr, rows = C.read_sheet(xl.getvalue())
        forms = d["settings"].setdefault("import_forms", {})
        fn = st.selectbox(T("Saved form", "فورم محفوظة"), ["(auto)"] + list(forms), key="sp_form")
        guess = forms.get(fn) or C.guess_mapping(hdr, custom)
        opts = [""] + [k for k, _, _ in C.columns(custom)]
        labels = {k: f"{k} · {T(en, ar)}" for k, en, ar in C.columns(custom)} | {"": T("(skip)", "(تجاهل)")}
        st.caption(T(f"{len(rows)} rows. Match each column of the sheet to a field:", f"{len(rows)} صف. وصّل كل عمود في الشيت بخانة:"))
        mapping = {}
        cols = st.columns(3)
        for i, h in enumerate(hdr):
            with cols[i % 3]:
                g = guess.get(h, "")
                mapping[h] = st.selectbox(str(h), opts, index=opts.index(g) if g in opts else 0, format_func=lambda k: labels.get(k, k), key=f"sp_map_{i}")
        keep = st.checkbox(T("Keep unmatched columns inside the record (nothing lost)", "احتفظ بالأعمدة اللي ماتوصلتش جوه التسجيل (مفيش حاجة تضيع)"), value=True, key="sp_keep")
        new = C.import_rows(rows, mapping, keep)
        st.caption(T(f"{len(new)} rows readable (need asset + quantity).", f"{len(new)} صف ينفع يتقري (لازم أصل + كمية)."))
        a, b = st.columns(2)
        name = a.text_input(T("Save this matching as a form named", "احفظ التوصيلة دي كفورم باسم"), key="sp_formname")
        if a.button(T("Save form", "احفظ الفورم"), key="sp_formsave") and name.strip():
            forms[name.strip()] = mapping
            save(d, f"spot: import form {name.strip()}")
        if b.button(T(f"Import {len(new)} rows", f"استورد {len(new)} صف"), type="primary", key="sp_xladd", disabled=not new):
            have = {t["id"] for t in d["txs"]}
            add = [t for t in new if t["id"] not in have]
            d["txs"] += add
            if save(d, f"spot: import {len(add)} rows from Excel"):
                st.success(f"+{len(add)}")
    st.divider()
    st.markdown("**" + T("My fields (extra columns for every record)", "خاناتي (أعمدة زيادة لكل تسجيل)") + "**")
    with st.form("sp_cf", clear_on_submit=True):
        a, b, c3 = st.columns([2, 1, 2])
        lab = a.text_input(T("Field name", "اسم الخانة"))
        typ = b.selectbox(T("Type", "النوع"), ["text", "number", "date", "select"])
        opt = c3.text_input(T("Choices (for select, comma separated)", "الاختيارات (للقايمة، بينهم فاصلة)"))
        if st.form_submit_button(T("Add field", "ضيف خانة")) and lab.strip():
            key = "".join(ch if ch.isalnum() else "_" for ch in lab.strip().lower())[:40] or f"f{len(custom) + 1}"
            if key in {c["key"] for c in custom} or key in C.FIELD_KEYS:
                key = f"{key}_{len(custom) + 1}"
            custom.append({"key": key, "label": lab.strip(), "type": typ, "options": opt})
            save(d, f"spot: field {lab.strip()}")
    for i, c in enumerate(custom):
        x, y = st.columns([6, 1])
        x.markdown(f"• **{c['label']}** · {c['type']}" + (f" · {c['options']}" if c.get("options") else ""))
        if y.button("✕", key=f"sp_cfdel_{i}"):
            custom.pop(i)
            save(d, "spot: remove field")
            st.rerun()
    st.caption(T("Removing a field hides it; values already saved stay inside the records.", "مسح الخانة بيخفيها بس؛ القيم المتسجلة بتفضل جوه التسجيلات."))


def _notify(d: dict, text: str) -> None:
    """Confirmation on Telegram after a record / alert (owner 2026-11-06: 'I record and nothing is sent'). Shows the reason when it fails."""
    if not d["settings"].get("tg_confirm", True):
        return
    from modules import telegram_alerts
    tok, chat = telegram_alerts.creds()
    if not tok or not chat:
        st.warning(T("Not sent to Telegram: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID are not in this app's Streamlit Secrets.",
                     "ماتبعتش على تليجرام: TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID مش موجودين في Streamlit Secrets بتاعة التطبيق."))
        return
    err = telegram_alerts.send("XPiX Spot · " + text)
    if err:
        st.error(T("Telegram refused: ", "تليجرام رفض: ") + err)
    else:
        st.toast(T("Sent to Telegram", "اتبعت على تليجرام"))


def _tg_box(d: dict) -> None:
    from modules import telegram_alerts
    tok, chat = telegram_alerts.creds()
    with st.container(border=True):
        st.markdown("**" + T("Telegram", "تليجرام") + "**")
        st.write(("✅ " if tok else "❌ ") + "TELEGRAM_BOT_TOKEN · " + ("✅ " if chat else "❌ ") + "TELEGRAM_CHAT_ID " +
                 T("(Streamlit Secrets of this app)", "(في Streamlit Secrets بتاعة التطبيق)"))
        if not (tok and chat):
            st.caption(T("Add both in Streamlit Cloud > Manage app > Settings > Secrets (for the page) AND in GitHub > Settings > Secrets > Actions (for the 30-min alerts, the daily ideas and the backtest).",
                         "ضيفهم في Streamlit Cloud > Manage app > Settings > Secrets (للصفحة) وكمان في GitHub > Settings > Secrets > Actions (للتنبيهات كل 30 دقيقة والأفكار اليومية والباك تيست)."))
        a, b = st.columns(2)
        if a.button(T("Send a test message", "ابعت رسالة تجربة"), key="sp_tgtest"):
            err = telegram_alerts.send("XPiX Spot · " + T("test message - Telegram works", "رسالة تجربة - تليجرام شغال"))
            (st.error if err else st.success)((T("Failed: ", "فشل: ") + err) if err else T("Sent - check Telegram.", "اتبعت - شوف تليجرام."))
        on = b.toggle(T("Confirm every record / alert on Telegram", "ابعت تأكيد على تليجرام مع كل تسجيل / تنبيه"), value=bool(d["settings"].get("tg_confirm", True)), key="sp_tgconf")
        if on != bool(d["settings"].get("tg_confirm", True)):
            d["settings"]["tg_confirm"] = on
            save(d)


def _tab_alerts(d, px):
    _tg_box(d)
    with st.form("sp_alf", clear_on_submit=True):
        a, b, c3, d4 = st.columns(4)
        asset = a.text_input(T("Asset (GOLD, SILVER, BTC ...)", "الأصل (GOLD، SILVER، BTC ...)")).strip().upper()
        kind = b.selectbox(T("Type", "النوع"), ["buy", "sell", "stop"], format_func=lambda k: {"buy": T("Buy zone (price <= level)", "وقت شراء (السعر ≤ المستوى)"),
                           "sell": T("Sell / TP (price >= level)", "وقت بيع (السعر ≥ المستوى)"), "stop": T("Invalidation (price <= level)", "إلغاء (السعر ≤ المستوى)")}[k])
        lvl = c3.number_input(T("Level (USD)", "المستوى (دولار)"), min_value=0.0, step=1.0, format="%.4f")
        note = d4.text_input(T("Note", "ملاحظة"))
        if st.form_submit_button(T("Add alert", "ضيف تنبيه")) and asset and lvl > 0:
            d["alerts"].append(C.new_alert(asset, kind, lvl, note))
            if save(d):
                _notify(d, T(f"alert armed: {asset} {kind} at {lvl:,.4g}", f"تنبيه اتسجل: {asset} {'شراء' if kind == 'buy' else 'بيع' if kind == 'sell' else 'إلغاء'} عند {lvl:,.4g}"))
    hits = C.check_alerts(d["alerts"], px)
    ar = T("en", "ar") == "ar"
    for h in hits:
        st.warning(C.alert_text(h, ar))
    auto = st.toggle(T("Send new hits to Telegram automatically (while this page is open)", "ابعت التنبيهات الجديدة على تليجرام تلقائي (طول ما الصفحة مفتوحة)"),
                     value=bool(d["settings"].get("tg_auto")), key="sp_tgauto")
    if auto != bool(d["settings"].get("tg_auto")):
        d["settings"]["tg_auto"] = auto
        save(d)
    if hits and (auto or st.button(T("Send these to Telegram", "ابعتهم على تليجرام"), key="sp_tgsend")):
        from modules import telegram_alerts
        sent = 0
        for h in hits:
            al = next(x for x in d["alerts"] if x["id"] == h["id"])
            if al.get("fired_at"):
                continue
            err = telegram_alerts.send("XPiX Spot · " + C.alert_text(h, ar))
            if err:
                st.error(f"Telegram: {err}")
                break
            al["fired_at"] = datetime.now(timezone.utc).isoformat(timespec="minutes")
            al["active"] = False   # one message per alert; re-arm it below
            sent += 1
        if sent:
            save(d)
            st.success(T(f"Sent {sent}.", f"اتبعت {sent}."))
    if d["alerts"]:
        st.dataframe(pd.DataFrame([{**a, "now": px.get(a["asset"])} for a in d["alerts"]]), hide_index=True, width="stretch")
        a, b = st.columns(2)
        sel = a.selectbox(T("Alert", "التنبيه"), [x["id"] for x in d["alerts"]], key="sp_alsel",
                          format_func=lambda i: next(f"{x['asset']} {x['kind']} {x['price']:,.4g}" for x in d["alerts"] if x["id"] == i))
        c1, c2 = b.columns(2)
        if c1.button(T("Re-arm", "فعّله تاني"), key="sp_alre"):
            for x in d["alerts"]:
                if x["id"] == sel:
                    x["active"], x["fired_at"] = True, None
            save(d)
            st.rerun()
        if c2.button(T("Delete", "امسح"), key="sp_aldel"):
            d["alerts"] = [x for x in d["alerts"] if x["id"] != sel]
            save(d)
            st.rerun()
    st.caption(T("Checked when the page loads or refreshes. Server-side checks every few minutes (tg_cron) are the next step.",
                 "التنبيهات بتتفحص لما الصفحة تفتح أو تتحدث. الفحص من السيرفر كل كام دقيقة (tg_cron) هو الخطوة الجاية."))


KEYWORDS = ("gold", "silver", "copper", "platinum", "palladium", "bitcoin", "crypto", "ethereum", "fed", "dollar", "inflation", "egypt", "ذهب", "فضة")


def _tab_news(d):
    try:
        from modules import rss_news
        items = rss_news.fetch(40)
    except Exception as e:
        items = []
        st.caption(f"News: {type(e).__name__}")
    rel = [i for i in items if any(k in (str(i.get("title", "")) + " " + str(i.get("summary", ""))).lower() for k in KEYWORDS)]
    for i in (rel or items)[:15]:
        st.markdown(f"- [{i.get('title')}]({i.get('link') or i.get('url', '#')}) · {i.get('source', '')}")
    if not items:
        st.info(T("News feeds unreachable right now.", "مصادر الأخبار مش واصلة دلوقتي."))
    st.divider()
    st.markdown("**" + T("Accounts to follow (Instagram / TikTok / YouTube / X)", "حسابات للمتابعة (انستجرام / تيك توك / يوتيوب / X)") + "**")
    with st.form("sp_srcf", clear_on_submit=True):
        a, b, c3 = st.columns([1, 2, 1])
        plat = a.selectbox(T("Platform", "المنصة"), ["Instagram", "TikTok", "YouTube", "X", "Telegram", "Other"])
        url = b.text_input(T("Profile link or @handle", "لينك الحساب أو @الاسم"))
        every = c3.selectbox(T("Check every", "افحص كل"), ["3 days", "7 days"])
        if st.form_submit_button(T("Add", "ضيف")) and url.strip():
            d["sources"].append({"platform": plat, "url": url.strip(), "every": every, "added": date.today().isoformat()})
            save(d)
    for i, s in enumerate(d["sources"]):
        c1, c2 = st.columns([6, 1])
        link = s["url"] if s["url"].startswith("http") else f"https://www.{s['platform'].lower()}.com/{s['url'].lstrip('@')}"
        c1.markdown(f"{s['platform']} · [{s['url']}]({link}) · {s['every']}")
        if c2.button("✕", key=f"sp_srcdel_{i}"):
            d["sources"].pop(i)
            save(d)
            st.rerun()
    st.caption(T("Reading the posts / videos automatically is NOT built yet: Instagram and TikTok have no free public API and block bots; it needs a "
                 "scraping service key (owner decision) + a weekly job that summarises what each account said and its calls. Until then the list is links only.",
                 "قراية البوستات والفيديوهات أوتوماتيك لسه ماتعملتش: انستجرام وتيك توك مالهمش API مجاني وبيقفلوا على البوتات؛ محتاجة مفتاح خدمة "
                 "سكرابينج (قرارك) + مهمة أسبوعية تلخص كل حساب قال إيه وتوصياته. لحد كده القايمة لينكات بس."))


def render() -> None:
    d = load()
    st.markdown("### " + T("Spot desk - crypto + metals", "السبوت - كريبتو + معادن"))
    fx, fx_src = _fx(d)
    px, met, cr = _prices()
    egp = st.toggle(T("Show metals / ledger in EGP", "اعرض المعادن والسجل بالجنيه"), key="sp_egp", value=True)
    # owner 2026-11-09: these tabs stay as they are - add to them and improve them, never remove or merge them
    tabs = st.tabs([T("Spot brain", "العقل المدبر"), T("Daily ideas", "الأفكار اليومية"), T("Crypto", "كريبتو"), T("Metals", "المعادن"), T("Ledger & invoices", "السجل والفواتير"), T("Alerts", "التنبيهات"),
                    T("News & sources", "الأخبار والمصادر"), T("Storage, Excel & fields", "التخزين والإكسل والخانات"), T("Analyzer (optional)", "المحلل (اختياري)"), T("Setup library", "مكتبة السيت أبات")])
    with tabs[0]:
        _tab_brain(d, px, met, cr, fx)
    with tabs[1]:
        _tab_ideas()
    with tabs[2]:
        _tab_crypto(d, cr, fx)
    with tabs[3]:
        _tab_metals(d, met, fx, fx_src, egp)
    with tabs[4]:
        _tab_ledger(d, px, fx, egp)
    with tabs[5]:
        _tab_alerts(d, px)
    with tabs[6]:
        _tab_news(d)
    with tabs[7]:
        _tab_setup(d, px, fx)
    with tabs[8]:   # owner 2026-11-06: an option on the side, loaded only on request
        if st.session_state.get("sp_an_on") or st.button(T("Open the analyzer (1M / 1W / 1D / 4H + every school)", "افتح المحلل (شهري / أسبوعي / يومي / 4 ساعات + كل المدارس)"), key="sp_an_open"):
            st.session_state["sp_an_on"] = True
            _tab_analyzer(cr, met)
        else:
            st.caption(T("Not loaded until you open it (it downloads 4 timeframes).", "مش بيتحمّل غير لما تفتحه (بيحمّل 4 فريمات)."))
    with tabs[9]:
        _tab_library()
    st.caption(T("Suggestions only - nothing here places an order.", "اقتراحات بس - مفيش هنا أي أمر بيتنفذ."))
