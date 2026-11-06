"""Spot desk <-> Telegram bot (owner 2026-11-06): read the online ledger and answer about any invoice / position / alert.

READ-ONLY for the bot: nothing here writes the ledger or places an order.
Entry point for any bot (scripts/xpix_bot.py or the one being built in another chat):
    from modules import spot_query
    reply, files = spot_query.handle("/inv INV-12")      # files = [(name, bytes)] to send as documents
Commands: /spot (positions + P&L) · /inv <text> (invoices matching a number / shop / date / asset ...) ·
          /find <text> (any field) · /spotalerts · /spotxl (Excel of everything)
Free text: spot_query.llm_context(question) -> a short JSON of the matching rows to give the bot's LLM (not the whole ledger)."""
from __future__ import annotations

import json
import math

from modules import spot_core as C

MAX_ROWS = 8


def load_db(store=None) -> dict:
    from modules.spot_store import get_store
    st = store or get_store()
    d = st.load() or {}
    d.setdefault("txs", [])
    d.setdefault("alerts", [])
    d.setdefault("settings", {})
    return d


def _live():
    """({asset: USD}, fx) or ({}, None) when offline."""
    px, fx = {}, None
    try:
        from modules import spot_data
        px.update({a: v["px"] for a, v in spot_data.metal_prices().items()})
        px.update({r["base"]: r["last"] for r in spot_data.crypto_tickers()[:300]})
        fx = (spot_data.usd_egp() or {}).get("rate")
    except Exception:
        pass
    return px, fx


def search(txs: list[dict], q: str) -> list[dict]:
    """Rows where EVERY word of q appears in some field (standard or custom), newest first."""
    words = [w.lower() for w in str(q).split() if w.strip()]
    out = []
    for t in txs:
        blob = " ".join(str(v) for k, v in t.items() if k not in ("files", "extra")) + " " + " ".join(f"{k} {v}" for k, v in (t.get("extra") or {}).items())
        blob = blob.lower()
        if all(w in blob for w in words):
            out.append(t)
    return sorted(out, key=lambda t: str(t.get("date", "")), reverse=True)


def _n(x, nd=2):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.{nd}f}"


def tx_text(t: dict) -> str:
    u, fu = C.tx_usd(t)
    e, fe = C.tx_egp(t)
    sg = 1 if t.get("side") == "buy" else -1
    side = "شراء" if t.get("side") == "buy" else "بيع"
    name = C.METAL_NAMES_AR.get(t.get("asset"), t.get("asset"))
    lines = [f"🧾 {t.get('invoice_no') or t['id']} · {t.get('date')} · {side} {name}",
             f"الكمية: {t.get('qty')} {t.get('unit')} · نقاوة {t.get('purity')} · سعر الوحدة {_n(float(t.get('price') or 0))} {t.get('currency')}",
             f"الإجمالي: {_n(u + sg * fu if not math.isnan(u) else None)} $ · {_n(e + sg * fe if not math.isnan(e) else None)} ج · سعر الدولار {t.get('fx') or '—'}",
             f"الطرف: {t.get('party') or '—'} · {t.get('channel') or ''} · {t.get('payment_method') or ''} · الحالة: {t.get('status') or ''}"]
    if t.get("notes"):
        lines.append(f"ملاحظات: {t['notes']}")
    if t.get("files"):
        lines.append(f"📎 {len(t['files'])} ملف")
    return "\n".join(lines)


def summary_text(d: dict, px: dict | None = None, fx: float | None = None) -> str:
    if px is None:
        px, fx = _live()
    pos = C.positions(d["txs"], px, fx)
    if not pos:
        return "مفيش مراكز سبوت متسجلة."
    out = ["📊 السبوت" + (f" · الدولار {fx:,.2f} ج" if fx else "")]
    for p in pos:
        if p["qty"] <= 1e-12 and not p["realized_usd"]:
            continue
        unit = "رطل" if p["asset"] == "COPPER" else "أونصة" if C.is_metal(p["asset"]) else ""
        line = f"• {C.METAL_NAMES_AR.get(p['asset'], p['asset'])}: {p['qty']:,.4f} {unit} · متوسط {_n(p['avg_usd'])}$"
        if p.get("unreal_usd") is not None:
            line += f" · مفتوح {_n(p['unreal_usd'])}$ ({_n(p.get('unreal_pct'), 1)}%)"
        if p.get("unreal_egp") is not None:
            line += f" · {_n(p['unreal_egp'], 0)}ج (معدن {_n(p['metal_part_egp'], 0)} / دولار {_n(p['fx_part_egp'], 0)})"
        if p["realized_usd"]:
            line += f" · محقق {_n(p['realized_usd'])}$"
        out.append(line)
    t = C.totals(pos)
    out.append(f"الإجمالي: تكلفة {_n(t['cost_usd'])}$ · قيمة {_n(t['value_usd'])}$ · مفتوح {_n(t['unreal_usd'])}$ · محقق {_n(t['realized_usd'])}$")
    if not px:
        out.append("(الأسعار اللايف مش متاحة دلوقتي: القيم الحالية ناقصة)")
    return "\n".join(out)


def handle(text: str, store=None) -> tuple[str, list]:
    """-> (reply text, [(file name, bytes)]). Unknown commands -> ('', [])."""
    a = str(text).strip().split(maxsplit=1)
    if not a:
        return "", []
    c, arg = a[0].lower().split("@")[0], (a[1] if len(a) > 1 else "")
    if c not in ("/spot", "/inv", "/find", "/spotalerts", "/spotxl"):
        return "", []
    from modules.spot_store import get_store
    st = store or get_store()
    d = load_db(st)
    if c == "/spot":
        return summary_text(d), []
    if c in ("/inv", "/find"):
        if not arg:
            return "اكتب رقم الفاتورة أو اسم المحل أو التاريخ: /inv INV-12", []
        rows = [t for t in search(d["txs"], arg) if c == "/find" or t.get("invoice_no") or t.get("files")] or search(d["txs"], arg)
        if not rows:
            return f"مفيش تسجيل فيه «{arg}».", []
        txt = "\n\n".join(tx_text(t) for t in rows[:MAX_ROWS]) + (f"\n\n(+{len(rows) - MAX_ROWS} كمان)" if len(rows) > MAX_ROWS else "")
        files = []
        if len(rows) == 1:
            for f in rows[0].get("files", [])[:5]:
                b = st.get_file(f)
                if b:
                    files.append((f.split("_", 1)[-1], b))
            files.append((f"invoice_{rows[0].get('invoice_no') or rows[0]['id']}.html", C.invoice_html(rows[0]).encode("utf8")))
        return txt, files
    if c == "/spotalerts":
        px, _ = _live()
        act = [x for x in d["alerts"] if x.get("active")]
        hits = C.check_alerts(act, px)
        lines = [C.alert_text(h) for h in hits] + [f"• {x['asset']} {x['kind']} {x['price']:,.4g} {x.get('note', '')}" for x in act if x["id"] not in {h['id'] for h in hits}]
        return ("🔔 تنبيهات السبوت\n" + "\n".join(lines)) if lines else "مفيش تنبيهات سبوت مفعّلة.", []
    px, fx = _live()
    xl = C.to_excel(d["txs"], C.positions(d["txs"], px, fx), px, fx, d["settings"].get("custom_fields"))
    return f"📗 Excel: {len(d['txs'])} تسجيل", [("spot_ledger.xlsx", xl)]


def llm_context(question: str, store=None, k: int = 20) -> str:
    """Compact JSON for the bot's LLM: totals + up to k rows matching words of the question (or the latest k)."""
    d = load_db(store)
    words = [w for w in str(question).split() if len(w) > 2]
    rows = []
    for w in words:
        rows += [t for t in search(d["txs"], w) if t not in rows]
    rows = (rows or sorted(d["txs"], key=lambda t: str(t.get("date", "")), reverse=True))[:k]
    keep = ("id", "date", "side", "asset", "qty", "unit", "purity", "price", "currency", "fx", "invoice_no", "party", "channel", "status", "notes")
    pos = C.positions(d["txs"])
    return json.dumps({"rows": [{x: t.get(x) for x in keep} | ({"extra": t["extra"]} if t.get("extra") else {}) for t in rows],
                       "positions": [{x: p.get(x) for x in ("asset", "qty", "avg_usd", "cost_usd", "realized_usd")} for p in pos],
                       "n_rows_total": len(d["txs"])}, ensure_ascii=False, default=str)
