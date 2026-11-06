"""Spot desk page (PAGE 11, next to the Radar; owner 2026-11-06).

Tabs: Crypto (OKX spot list like the watchlist + high-timeframe plan) / Metals (gold, silver, platinum, palladium, copper
in USD and EGP, karats) / Ledger & invoices (buys + sells, PDF upload, print, Excel) / Alerts (buy / sell / stop,
Telegram) / News & sources.
Storage: data/spot/ on the server disk (git-ignored: private). Streamlit Cloud may wipe the disk on a restart, so
the page offers a full backup (ZIP) + restore. Nothing here places an order."""
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

ROOT = Path(__file__).resolve().parent.parent / "data" / "spot"
DB = ROOT / "ledger.json"
FILES = ROOT / "files"
METAL_LIST = list(C.METALS)


def T(en: str, ar: str) -> str:
    try:
        from modules.i18n import lang
        return ar if lang() == "ar" else en
    except Exception:
        return en


# ---------------------------------------------------------------- storage
def _empty() -> dict:
    return {"txs": [], "alerts": [], "sources": [], "settings": {"budget": 1000.0, "fx_manual": None, "tg_auto": False}}


def load() -> dict:
    if "spot_db" not in st.session_state:
        d = _empty()
        try:
            if DB.exists():
                d.update(json.loads(DB.read_text(encoding="utf8")))
        except Exception:
            pass
        st.session_state["spot_db"] = d
    return st.session_state["spot_db"]


def save(d: dict) -> None:
    st.session_state["spot_db"] = d
    try:
        ROOT.mkdir(parents=True, exist_ok=True)
        DB.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf8")
    except Exception as e:
        st.warning(T("Could not write to the server disk", "مقدرتش أحفظ على السيرفر") + f": {type(e).__name__}. " +
                   T("Download a backup.", "نزّل نسخة احتياطية."))


def backup_zip(d: dict) -> bytes:
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("ledger.json", json.dumps(d, ensure_ascii=False, indent=1))
        if FILES.exists():
            for f in FILES.iterdir():
                z.write(f, f"files/{f.name}")
    return bio.getvalue()


def restore_zip(data: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        d = _empty()
        d.update(json.loads(z.read("ledger.json").decode("utf8")))
        FILES.mkdir(parents=True, exist_ok=True)
        for n in z.namelist():
            if n.startswith("files/") and not n.endswith("/"):
                name = Path(n).name   # no path parts from the archive
                (FILES / name).write_bytes(z.read(n))
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
    budget = st.number_input(T("Budget for this asset (USD)", "الميزانية للأصل ده (دولار)"), min_value=0.0, value=float(d["settings"].get("budget", 1000.0)),
                             step=100.0, key=f"sp_bud_{asset}")
    lad = C.ladder(p["buys"], budget)
    l1, l2 = st.columns(2)
    with l1:
        st.markdown("**" + T("Staged buys (30 / 30 / 40 %)", "الشراء على دفعات (30 / 30 / 40 %)") + "**")
        st.dataframe(pd.DataFrame([{T("Level", "المستوى"): _n(r["price"] * k), cur: _n(r["usd"] * k), T("Qty", "الكمية"): _n(r["qty"], 6)} for r in lad]),
                     hide_index=True, width="stretch")
        avg = C.ladder_avg(lad)
        if avg:
            st.caption(T("Average if all fill", "المتوسط لو كله اتنفذ") + f": {_n(avg * k)} {cur}")
    with l2:
        st.markdown("**" + T("Sell / take-profit levels", "مستويات البيع / جني الربح") + "**")
        st.dataframe(pd.DataFrame([{T("Target", "الهدف"): f"T{i + 1}", cur: _n(x * k), "%": f"{(x / p['price'] - 1) * 100:+.1f}%"} for i, x in enumerate(p["sells"])]),
                     hide_index=True, width="stretch")
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
        save(d)
        st.success(T("Alerts added - see the Alerts tab.", "التنبيهات اتضافت - شوف تاب التنبيهات."))


# ---------------------------------------------------------------- tabs
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
    df = pd.DataFrame([{"#": i + 1, T("Coin", "العملة"): r["base"], "USD": r["last"], "24h %": None if r["chg24"] is None else round(r["chg24"], 2),
                        T("Volume 24h (USD)", "الفوليوم 24 ساعة"): round(r["vol_usd"])} | ({"EGP": round(r["last"] * fx, 4)} if b2b and fx else {})
                       for i, r in enumerate(rows)])
    st.dataframe(df, hide_index=True, width="stretch", height=320)
    pick = st.selectbox(T("Plan for", "خطة لـ"), [r["base"] for r in rows] or ["BTC"], key="sp_cr_pick")
    live = next((r["last"] for r in cr if r["base"] == pick), None)
    _show_plan(pick, f"{pick}-USDT", d, live, fx, b2b)
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


def _tx_form(d, fx):
    with st.form("sp_txf", clear_on_submit=True):
        a, b, c3, d4 = st.columns(4)
        side = a.radio(T("Side", "النوع"), ["buy", "sell"], format_func=lambda s: T(s.title(), "شراء" if s == "buy" else "بيع"), horizontal=True)
        asset = b.selectbox(T("Asset", "الأصل"), METAL_LIST + [T("Crypto (type below)", "كريبتو (اكتبها تحت)")])
        coin = c3.text_input(T("Coin (if crypto)", "العملة (لو كريبتو)"), placeholder="BTC")
        dt = d4.date_input(T("Date", "التاريخ"), value=date.today())
        a, b, c3, d4 = st.columns(4)
        qty = a.number_input(T("Quantity", "الكمية"), min_value=0.0, step=0.01, format="%.6f")
        unit = b.selectbox(T("Unit", "الوحدة"), ["oz", "g", "kg", "lb", "coin"])
        purity = c3.selectbox(T("Karat / purity", "العيار / النقاوة"), ["24K / 999", "21K", "18K", "925", "950", "pure"])
        price = d4.number_input(T("Price per unit", "سعر الوحدة"), min_value=0.0, step=1.0, format="%.4f")
        a, b, c3, d4 = st.columns(4)
        cur = a.radio(T("Currency", "العملة"), ["USD", "EGP"], horizontal=True)
        rate = b.number_input(T("USD/EGP at that time", "سعر الدولار وقتها"), min_value=0.0, value=float(fx or 0), step=0.05)
        fees = c3.number_input(T("Fees / workmanship (same currency)", "مصاريف / مصنعية (بنفس العملة)"), min_value=0.0, step=1.0)
        inv = d4.text_input(T("Invoice no.", "رقم الفاتورة"))
        a, b, c3 = st.columns([2, 1, 3])
        party = a.text_input(T("Shop / client / exchange", "المحل / العميل / المنصة"))
        ch = b.selectbox(T("Channel", "القناة"), ["B2C", "B2B", "Exchange"])
        notes = c3.text_input(T("Notes", "ملاحظات"))
        up = st.file_uploader(T("Invoice / receipt (PDF or image)", "الفاتورة / الإيصال (PDF أو صورة)"), type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
        if st.form_submit_button(T("Save", "سجّل"), type="primary"):
            ast = (coin.strip().upper() or "BTC") if asset not in METAL_LIST else asset
            pmap = {"24K / 999": 1.0, "21K": 0.875, "18K": 0.75, "925": 0.925, "950": 0.95, "pure": 1.0}
            p = pmap[purity] if ast in METAL_LIST else 1.0
            if ast in ("SILVER", "PLATINUM", "PALLADIUM") and purity == "24K / 999":
                p = 0.999
            if qty <= 0 or price <= 0:
                st.error(T("Quantity and price must be > 0.", "الكمية والسعر لازم يبقوا أكبر من صفر."))
                return
            tx = C.new_tx(side=side, asset=ast, qty=qty, unit=unit if ast in METAL_LIST else "coin", purity=p, price=price, currency=cur,
                          fx=rate or None, fees=fees, invoice_no=inv, party=party, channel=ch, notes=notes, date=dt.isoformat())
            if up:
                FILES.mkdir(parents=True, exist_ok=True)
                for f in up:
                    safe = "".join(ch_ for ch_ in Path(f.name).name if ch_.isalnum() or ch_ in "._-")[-80:] or "file"
                    name = f"{tx['id']}_{safe}"
                    (FILES / name).write_bytes(f.getvalue())
                    tx["files"].append(name)
            d["txs"].append(tx)
            save(d)
            st.success(T("Saved.", "اتسجل."))


def _tab_ledger(d, px, fx, egp):
    _tx_form(d, fx)
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
        st.caption(T("qty = pure oz for metals (copper: lb), coins for crypto. metal_part = price move, fx_part = dollar move since each buy.",
                     "الكمية = أونصة صافية للمعادن (النحاس رطل) وعدد العملات للكريبتو. metal_part = حركة السعر، fx_part = حركة الدولار من وقت كل شراء."))
    if not txs:
        st.info(T("No records yet.", "مفيش تسجيلات لسه."))
    else:
        st.dataframe(pd.DataFrame([{c: t.get(c) for c in C.TX_COLS} | {"files": len(t.get("files", []))} for t in txs]), hide_index=True, width="stretch")
        sel = st.selectbox(T("Record", "التسجيل"), [t["id"] for t in txs][::-1],
                           format_func=lambda i: next(f"{t['date']} · {t['side']} · {t['asset']} · {t['qty']} {t['unit']} · {t.get('invoice_no') or i}" for t in txs if t["id"] == i), key="sp_sel")
        tx = next(t for t in txs if t["id"] == sel)
        a, b, c3 = st.columns(3)
        html = C.invoice_html(tx)
        a.download_button(T("Invoice (HTML, print / save PDF)", "الفاتورة (HTML للطباعة / PDF)"), html.encode("utf8"), file_name=f"invoice_{tx.get('invoice_no') or tx['id']}.html", mime="text/html")
        if b.button(T("Print preview", "معاينة الطباعة"), key="sp_prev"):
            import streamlit.components.v1 as components
            components.html(html, height=520, scrolling=True)
        if c3.button(T("Delete record", "امسح التسجيل"), key="sp_del"):
            for f in tx.get("files", []):
                try:
                    (FILES / f).unlink()
                except Exception:
                    pass
            d["txs"] = [t for t in txs if t["id"] != sel]
            save(d)
            st.rerun()
        for f in tx.get("files", []):
            p = FILES / f
            if p.exists():
                st.download_button(f"📎 {f.split('_', 1)[-1]}", p.read_bytes(), file_name=f.split("_", 1)[-1], key=f"sp_f_{f}")
            else:
                st.caption(f"📎 {f}: " + T("file missing on this server (restore a backup)", "الملف مش موجود على السيرفر (رجّع نسخة احتياطية)"))
    st.divider()
    a, b, c3, d4 = st.columns(4)
    try:
        a.download_button(T("Excel export", "تصدير Excel"), C.to_excel(txs, pos, px, fx), file_name=f"spot_{date.today()}.xlsx",
                          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        a.caption(f"Excel: {type(e).__name__}")
    xl = b.file_uploader(T("Excel import", "استيراد Excel"), type=["xlsx"], key="sp_xlin")
    if xl and b.button(T("Add rows", "ضيف الصفوف"), key="sp_xladd"):
        new = C.from_excel(xl.getvalue())
        have = {t["id"] for t in d["txs"]}
        d["txs"] += [t for t in new if t["id"] not in have]
        save(d)
        st.success(f"+{len([t for t in new if t['id'] not in have])}")
    c3.download_button(T("Full backup (ZIP)", "نسخة احتياطية كاملة (ZIP)"), backup_zip(d), file_name=f"spot_backup_{date.today()}.zip", mime="application/zip")
    rz = d4.file_uploader(T("Restore backup", "رجّع نسخة احتياطية"), type=["zip"], key="sp_rz")
    if rz and d4.button(T("Restore (replaces)", "رجّع (هيستبدل)"), key="sp_rzb"):
        save(restore_zip(rz.getvalue()))
        st.rerun()
    st.caption(T("Records live on the server disk (data/spot, not in git). Streamlit Cloud can wipe it on a restart: download a backup after you add invoices.",
                 "التسجيلات محفوظة على السيرفر (data/spot ومش في git). Streamlit Cloud ممكن يمسحها لو اتعمل restart: نزّل نسخة احتياطية بعد ما تسجل فواتير."))


def _tab_alerts(d, px):
    with st.form("sp_alf", clear_on_submit=True):
        a, b, c3, d4 = st.columns(4)
        asset = a.text_input(T("Asset (GOLD, SILVER, BTC ...)", "الأصل (GOLD، SILVER، BTC ...)")).strip().upper()
        kind = b.selectbox(T("Type", "النوع"), ["buy", "sell", "stop"], format_func=lambda k: {"buy": T("Buy zone (price <= level)", "وقت شراء (السعر ≤ المستوى)"),
                           "sell": T("Sell / TP (price >= level)", "وقت بيع (السعر ≥ المستوى)"), "stop": T("Invalidation (price <= level)", "إلغاء (السعر ≤ المستوى)")}[k])
        lvl = c3.number_input(T("Level (USD)", "المستوى (دولار)"), min_value=0.0, step=1.0, format="%.4f")
        note = d4.text_input(T("Note", "ملاحظة"))
        if st.form_submit_button(T("Add alert", "ضيف تنبيه")) and asset and lvl > 0:
            d["alerts"].append(C.new_alert(asset, kind, lvl, note))
            save(d)
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
    tabs = st.tabs([T("Crypto", "كريبتو"), T("Metals", "المعادن"), T("Ledger & invoices", "السجل والفواتير"), T("Alerts", "التنبيهات"), T("News & sources", "الأخبار والمصادر")])
    with tabs[0]:
        _tab_crypto(d, cr, fx)
    with tabs[1]:
        _tab_metals(d, met, fx, fx_src, egp)
    with tabs[2]:
        _tab_ledger(d, px, fx, egp)
    with tabs[3]:
        _tab_alerts(d, px)
    with tabs[4]:
        _tab_news(d)
    st.caption(T("Suggestions only - nothing here places an order.", "اقتراحات بس - مفيش هنا أي أمر بيتنفذ."))
