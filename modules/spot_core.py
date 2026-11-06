"""Spot desk core (page 11, owner 2026-11-06): pure functions, no network, no Streamlit.

- Metals units: troy ounce <-> gram, gold karats 24 / 21 / 18, silver 999 / 925, platinum / palladium 999 / 950, copper per kg.
- USD -> EGP with the exchange rate AT THE TIME (each ledger row keeps its own rate).
- Ledger (buys / sells / invoices) -> positions by average cost, realized + unrealized P&L in USD and EGP,
  and the EGP P&L split into 'metal move' + 'dollar move' (the two parts add up exactly).
- Buy / sell ladder (staged entries) and price alerts (buy zone / sell zone / stop).
- Excel export / import (openpyxl).
Nothing here places an order."""
from __future__ import annotations

import io
import math
import uuid
from datetime import datetime, timezone

OZ_G = 31.1034768            # grams in one troy ounce
LB_KG = 0.45359237           # kilograms in one pound (COMEX copper is quoted per lb)

# asset -> (price unit of the feed, purities offered {label: fraction})
METALS = {
    "GOLD": ("oz", {"24K": 1.0, "21K": 0.875, "18K": 0.75}),
    "SILVER": ("oz", {"999": 0.999, "925": 0.925}),
    "PLATINUM": ("oz", {"999": 0.999, "950": 0.95}),
    "PALLADIUM": ("oz", {"999": 0.999, "950": 0.95}),
    "COPPER": ("lb", {"pure": 1.0}),
}
METAL_NAMES_AR = {"GOLD": "ذهب", "SILVER": "فضة", "PLATINUM": "بلاتين", "PALLADIUM": "بلاديوم", "COPPER": "نحاس"}
UNITS = ("oz", "g", "kg", "lb", "coin")


def is_metal(asset: str) -> bool:
    return str(asset).upper() in METALS


# ---------------------------------------------------------------- units / prices
def to_oz(qty: float, unit: str) -> float:
    """Quantity in troy ounces (metals) - 'coin' / unknown units are returned unchanged."""
    u = (unit or "").lower()
    if u == "g":
        return qty / OZ_G
    if u == "kg":
        return qty * 1000 / OZ_G
    if u == "lb":
        return qty * LB_KG * 1000 / OZ_G
    return qty


def base_qty(asset: str, qty: float, unit: str, purity: float = 1.0) -> float:
    """Quantity in the feed's own unit of PURE metal (oz for gold/silver/Pt/Pd, lb for copper) or coins for crypto."""
    a = str(asset).upper()
    if a not in METALS:
        return float(qty)
    feed_unit = METALS[a][0]
    pure = float(qty) * float(purity or 1.0)
    if feed_unit == "lb":   # copper: everything -> grams -> pounds
        return to_oz(pure, unit) * OZ_G / (LB_KG * 1000)
    return to_oz(pure, unit)


def per_unit_prices(asset: str, feed_price: float, fx: float | None = None) -> list[dict]:
    """Price table for one metal: per oz / gram / kg for each purity, in USD and (if fx) EGP.
    feed_price = USD per troy oz (copper: USD per lb)."""
    a = str(asset).upper()
    unit, pur = METALS[a]
    rows = []
    for lab, f in pur.items():
        if unit == "lb":
            kg = feed_price / LB_KG * f
            vals = {"lb": feed_price * f, "kg": kg, "g": kg / 1000}
        else:
            vals = {"oz": feed_price * f, "g": feed_price / OZ_G * f, "kg": feed_price / OZ_G * 1000 * f}
        r = {"purity": lab, "fraction": f}
        for k, v in vals.items():
            r[f"usd_{k}"] = v
            if fx:
                r[f"egp_{k}"] = v * fx
        rows.append(r)
    return rows


def local_gap(theory_egp: float, shop_egp: float) -> float | None:
    """% difference of a shop (Egyptian market) price over the computed price; None if missing."""
    if not theory_egp or not shop_egp:
        return None
    return (shop_egp / theory_egp - 1) * 100


# ---------------------------------------------------------------- ledger
def new_tx(**kw) -> dict:
    """One ledger row (buy or sell). Prices are PER UNIT of `unit` in `currency`; `fx` = EGP per 1 USD at that time."""
    tx = {"id": uuid.uuid4().hex[:10], "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "side": "buy", "asset": "GOLD",
          "qty": 0.0, "unit": "oz", "purity": 1.0, "price": 0.0, "currency": "USD", "fx": None, "fees": 0.0,
          "invoice_no": "", "party": "", "channel": "", "notes": "", "files": []}
    tx.update({k: v for k, v in kw.items() if k in tx or k in ("tags",)})
    tx["asset"] = str(tx["asset"]).upper()
    tx["side"] = "sell" if str(tx["side"]).lower().startswith("s") else "buy"
    return tx


def tx_usd(tx: dict) -> tuple[float, float]:
    """(gross USD, fees USD) of one row. EGP rows need their fx; without it -> (nan, nan)."""
    gross = float(tx.get("qty") or 0) * float(tx.get("price") or 0)
    fees = float(tx.get("fees") or 0)
    if str(tx.get("currency", "USD")).upper() == "EGP":
        fx = tx.get("fx")
        if not fx:
            return math.nan, math.nan
        return gross / float(fx), fees / float(fx)
    return gross, fees


def tx_egp(tx: dict) -> tuple[float, float]:
    """(gross EGP, fees EGP) with the row's own rate; nan when a USD row has no rate."""
    gross = float(tx.get("qty") or 0) * float(tx.get("price") or 0)
    fees = float(tx.get("fees") or 0)
    if str(tx.get("currency", "USD")).upper() == "EGP":
        return gross, fees
    fx = tx.get("fx")
    if not fx:
        return math.nan, math.nan
    return gross * float(fx), fees * float(fx)


def positions(txs: list[dict], prices: dict | None = None, fx_now: float | None = None) -> list[dict]:
    """Average-cost positions per asset. prices = {asset: USD per feed unit}. Sells reduce qty at the average cost
    (realized P&L = proceeds - fees - avg cost x qty). EGP P&L uses each row's own rate, split into metal + dollar parts."""
    prices = prices or {}
    book: dict = {}
    for tx in sorted(txs, key=lambda t: (str(t.get("date", "")), str(t.get("id", "")))):
        a = str(tx.get("asset", "")).upper()
        q = base_qty(a, float(tx.get("qty") or 0), tx.get("unit", "oz"), float(tx.get("purity") or 1.0))
        if q <= 0:
            continue
        usd, fee_u = tx_usd(tx)
        egp, fee_e = tx_egp(tx)
        b = book.setdefault(a, {"asset": a, "qty": 0.0, "cost_usd": 0.0, "cost_egp": 0.0, "realized_usd": 0.0, "realized_egp": 0.0,
                                "n_buy": 0, "n_sell": 0, "egp_known": True})
        if math.isnan(egp):
            b["egp_known"] = False
        if tx.get("side") == "sell":
            if b["qty"] <= 0:
                continue
            q = min(q, b["qty"])
            share = q / b["qty"]
            cu, ce = b["cost_usd"] * share, b["cost_egp"] * share
            b["realized_usd"] += (usd - fee_u) - cu
            b["realized_egp"] += (0 if math.isnan(egp) else egp - fee_e) - ce
            b["qty"] -= q
            b["cost_usd"] -= cu
            b["cost_egp"] -= ce
            b["n_sell"] += 1
        else:
            b["qty"] += q
            b["cost_usd"] += usd + fee_u
            b["cost_egp"] += 0 if math.isnan(egp) else egp + fee_e
            b["n_buy"] += 1
    out = []
    for a, b in book.items():
        qty = b["qty"]
        b["avg_usd"] = b["cost_usd"] / qty if qty > 1e-12 else None
        b["avg_egp"] = b["cost_egp"] / qty if qty > 1e-12 else None
        px = prices.get(a)
        if px and qty > 1e-12:
            b["value_usd"] = qty * px
            b["unreal_usd"] = b["value_usd"] - b["cost_usd"]
            b["unreal_pct"] = b["unreal_usd"] / b["cost_usd"] * 100 if b["cost_usd"] else None
            if fx_now and b["egp_known"]:
                b["value_egp"] = b["value_usd"] * fx_now
                b["unreal_egp"] = b["value_egp"] - b["cost_egp"]
                b["metal_part_egp"] = (px - b["avg_usd"]) * qty * fx_now      # price move, valued at today's rate
                b["fx_part_egp"] = b["unreal_egp"] - b["metal_part_egp"]       # the rest = the dollar move since each buy
        out.append(b)
    return sorted(out, key=lambda r: -(r.get("value_usd") or r["cost_usd"]))


def totals(pos: list[dict]) -> dict:
    t = {"cost_usd": 0.0, "value_usd": 0.0, "unreal_usd": 0.0, "realized_usd": 0.0, "cost_egp": 0.0, "value_egp": 0.0, "unreal_egp": 0.0,
         "realized_egp": 0.0}
    for p in pos:
        for k in t:
            v = p.get(k)
            if isinstance(v, (int, float)) and not math.isnan(v):
                t[k] += v
    return t


# ---------------------------------------------------------------- staged entries / exits
def ladder(levels: list[float], budget: float, weights=(0.3, 0.3, 0.4)) -> list[dict]:
    """Split a budget (USD) over buy levels, highest first (first fill = smallest share). -> [{price, usd, qty}]"""
    lv = sorted({round(float(x), 10) for x in levels if x and x > 0}, reverse=True)[:len(weights)]
    if not lv:
        return []
    w = list(weights[:len(lv)])
    s = sum(w)
    return [{"price": p, "usd": budget * wi / s, "qty": budget * wi / s / p} for p, wi in zip(lv, w)]


def ladder_avg(rows: list[dict]) -> float | None:
    q = sum(r["qty"] for r in rows)
    return sum(r["usd"] for r in rows) / q if q else None


# ---------------------------------------------------------------- alerts
def new_alert(asset: str, kind: str, price: float, note: str = "") -> dict:
    """kind: 'buy' (price <= level), 'sell' (price >= level), 'stop' (price <= level)."""
    return {"id": uuid.uuid4().hex[:8], "asset": str(asset).upper(), "kind": kind, "price": float(price), "note": note, "active": True,
            "fired_at": None}


def check_alerts(alerts: list[dict], prices: dict) -> list[dict]:
    """Active alerts whose condition holds now (does not mutate)."""
    hits = []
    for a in alerts:
        px = prices.get(a.get("asset"))
        if not a.get("active") or not px:
            continue
        if (a["kind"] in ("buy", "stop") and px <= a["price"]) or (a["kind"] == "sell" and px >= a["price"]):
            hits.append({**a, "now": px})
    return hits


def alert_text(h: dict, ar: bool = True) -> str:
    if ar:
        what = {"buy": "🟢 وقت شراء", "sell": "🔴 وقت بيع / جني ربح", "stop": "⛔ كسر نقطة الإلغاء"}[h["kind"]]
        return f"{what} — {h['asset']}: السعر {h['now']:,.4g} (المستوى {h['price']:,.4g}) {h.get('note', '')}".strip()
    what = {"buy": "🟢 Buy zone", "sell": "🔴 Sell / take profit", "stop": "⛔ Invalidation broken"}[h["kind"]]
    return f"{what} - {h['asset']}: price {h['now']:,.4g} (level {h['price']:,.4g}) {h.get('note', '')}".strip()


# ---------------------------------------------------------------- Excel
TX_COLS = ["id", "date", "side", "asset", "qty", "unit", "purity", "price", "currency", "fx", "fees", "invoice_no", "party", "channel", "notes"]


def to_excel(txs: list[dict], pos: list[dict], prices: dict, fx_now: float | None) -> bytes:
    """Workbook with Transactions / Positions / Prices sheets."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"
    ws.append(TX_COLS + ["usd_total", "egp_total"])
    for t in txs:
        u, fu = tx_usd(t)
        e, fe = tx_egp(t)
        ws.append([t.get(c) for c in TX_COLS] + [None if math.isnan(u) else round(u + (fu if t["side"] == "buy" else -fu), 2),
                                                 None if math.isnan(e) else round(e + (fe if t["side"] == "buy" else -fe), 2)])
    ws2 = wb.create_sheet("Positions")
    pc = ["asset", "qty", "avg_usd", "cost_usd", "value_usd", "unreal_usd", "unreal_pct", "realized_usd", "avg_egp", "cost_egp", "value_egp",
          "unreal_egp", "metal_part_egp", "fx_part_egp", "realized_egp"]
    ws2.append(pc)
    for p in pos:
        ws2.append([p.get(c) for c in pc])
    ws3 = wb.create_sheet("Prices")
    ws3.append(["asset", "usd_per_feed_unit", "usd_egp_rate", "time_utc"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    for a, px in prices.items():
        ws3.append([a, px, fx_now, now])
    hdr = PatternFill("solid", fgColor="F0B90B")
    for sh in (ws, ws2, ws3):
        for c in sh[1]:
            c.font = Font(bold=True)
            c.fill = hdr
        for col in sh.columns:
            sh.column_dimensions[col[0].column_letter].width = max(10, min(28, max(len(str(c.value or "")) for c in col) + 2))
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


def from_excel(data: bytes) -> list[dict]:
    """Transactions sheet (or the first sheet) -> ledger rows; unknown columns ignored, missing ones defaulted."""
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    ws = wb["Transactions"] if "Transactions" in wb.sheetnames else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    hdr = [str(h or "").strip().lower() for h in rows[0]]
    out = []
    for r in rows[1:]:
        d = {h: v for h, v in zip(hdr, r) if h in TX_COLS and v is not None}
        if not d.get("asset") or not d.get("qty"):
            continue
        for k in ("qty", "price", "fees", "purity"):
            if k in d:
                d[k] = float(d[k])
        if d.get("fx") not in (None, ""):
            d["fx"] = float(d["fx"])
        if "date" in d and hasattr(d["date"], "strftime"):
            d["date"] = d["date"].strftime("%Y-%m-%d")
        tid = d.pop("id", None)
        tx = new_tx(**d)
        if tid:
            tx["id"] = str(tid)
        out.append(tx)
    return out


# ---------------------------------------------------------------- invoice (print / save as PDF from the browser)
def invoice_html(tx: dict, shop: str = "6868 X") -> str:
    """Printable Arabic invoice for one row (the browser's Print -> Save as PDF makes the PDF)."""
    u, fu = tx_usd(tx)
    e, fe = tx_egp(tx)
    side = "شراء" if tx.get("side") == "buy" else "بيع"
    name = METAL_NAMES_AR.get(tx.get("asset"), tx.get("asset"))
    pur = tx.get("purity") or 1
    pur_txt = next((k for k, v in METALS.get(tx.get("asset"), ("", {}))[1].items() if abs(v - float(pur)) < 1e-6), f"{float(pur):.3f}")

    def f(x):
        return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.2f}"
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>فاتورة {tx.get('invoice_no') or tx['id']}</title>
<style>body{{font-family:Tahoma,Arial,sans-serif;margin:32px;color:#111}}h1{{margin:0 0 4px;font-size:22px}}.m{{color:#555;font-size:13px}}
table{{width:100%;border-collapse:collapse;margin-top:18px}}td,th{{border:1px solid #bbb;padding:8px;text-align:right;font-size:14px}}th{{background:#f6e7b0}}
.t{{font-weight:700;font-size:16px}}@media print{{button{{display:none}}}}</style></head><body>
<h1>فاتورة {side} — {name}</h1><div class="m">{shop} · رقم: {tx.get('invoice_no') or tx['id']} · التاريخ: {tx.get('date')} · الطرف: {tx.get('party') or '—'} · القناة: {tx.get('channel') or '—'}</div>
<table><tr><th>الصنف</th><th>العيار / النقاوة</th><th>الكمية</th><th>الوحدة</th><th>سعر الوحدة</th><th>العملة</th></tr>
<tr><td>{name}</td><td>{pur_txt}</td><td>{tx.get('qty')}</td><td>{tx.get('unit')}</td><td>{f(float(tx.get('price') or 0))}</td><td>{tx.get('currency')}</td></tr></table>
<table><tr><th>البند</th><th>دولار</th><th>جنيه</th></tr>
<tr><td>القيمة</td><td>{f(u)}</td><td>{f(e)}</td></tr><tr><td>مصاريف / مصنعية</td><td>{f(fu)}</td><td>{f(fe)}</td></tr>
<tr class="t"><td>الإجمالي</td><td>{f(u + fu if tx.get('side') == 'buy' else u - fu)}</td><td>{f(e + fe if tx.get('side') == 'buy' else e - fe)}</td></tr>
<tr><td>سعر الصرف المستخدم</td><td colspan="2">{tx.get('fx') or '—'} جنيه / دولار</td></tr></table>
<p class="m">{tx.get('notes') or ''}</p><button onclick="window.print()">طباعة / حفظ PDF</button></body></html>"""
