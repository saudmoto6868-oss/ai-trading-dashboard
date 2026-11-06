"""What the institutions do (owner 2026-11-06: 'see what the institutions do and do like them').

CFTC Commitments of Traders, legacy futures-only report (public Socrata API, free, weekly, positions as of Tuesday, out
Friday): commercials (producers / banks hedging - the 'smart money' of the COT method) vs non-commercials (large
speculators / funds). COT index = where today's net position sits in its own last 3-year range (0..100):
  commercials index >= 80 = they are unusually long -> historically bullish; <= 20 -> bearish;
  speculators index >= 90 = crowded long -> risk of a flush.
Market codes cross-checked with the Equibles connector on 2026-11-06. Crypto has no COT here (CME bitcoin is a tiny part of
the market): the flow module's open interest / funding / Coinbase premium stand in for it."""
from __future__ import annotations

import requests

URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
CODES = {"GOLD": "088691", "SILVER": "084691", "COPPER": "085692", "PLATINUM": "076651", "PALLADIUM": "075651", "OIL": "067651", "EURUSD": "099741"}


def parse(rows: list[dict]) -> dict:
    """Socrata rows (any order) -> net positions, 3-year COT indexes, 4-week change."""
    rr = sorted(rows, key=lambda r: r.get("report_date_as_yyyy_mm_dd", ""))
    if len(rr) < 20:
        return {"ok": False, "why": f"only {len(rr)} weekly reports"}
    f = lambda r, k: float(r.get(k) or 0)
    comm = [f(r, "comm_positions_long_all") - f(r, "comm_positions_short_all") for r in rr]
    spec = [f(r, "noncomm_positions_long_all") - f(r, "noncomm_positions_short_all") for r in rr]
    oi = [f(r, "open_interest_all") for r in rr]

    def idx(x):
        w = x[-156:]
        lo, hi = min(w), max(w)
        return (x[-1] - lo) / (hi - lo) * 100 if hi > lo else 50.0
    return {"ok": True, "date": rr[-1].get("report_date_as_yyyy_mm_dd", "")[:10], "comm_net": comm[-1], "spec_net": spec[-1], "oi": oi[-1],
            "comm_idx": idx(comm), "spec_idx": idx(spec), "spec_chg_4w": spec[-1] - spec[-5] if len(spec) > 4 else None,
            "comm_series": comm[-104:], "spec_series": spec[-104:]}


def fetch(asset: str) -> dict:
    code = CODES.get(asset)
    if not code:
        return {"ok": False, "why": "no COT for this market"}
    try:
        r = requests.get(URL, params={"cftc_contract_market_code": code, "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 160}, timeout=15)
        r.raise_for_status()
        return parse(r.json())
    except Exception as e:
        return {"ok": False, "why": type(e).__name__}


def reading(c: dict) -> dict:
    if not c.get("ok"):
        return {"vote": 0, "lines": [f"المؤسسات (COT): {c.get('why', 'مش متاح')}"]}
    v = 0
    ci, si = c["comm_idx"], c["spec_idx"]
    lines = [f"المؤسسات (COT {c['date']}): التجار/البنوك عند {ci:.0f}% من رينج 3 سنين · المضاربين الكبار {si:.0f}%"]
    if ci >= 80:
        v += 1
        lines.append("  التجار (الفلوس الذكية) شاريين بشكل غير عادي → تاريخيًا إيجابي")
    elif ci <= 20:
        v -= 1
        lines.append("  التجار بايعين/متحوطين بشكل غير عادي → تاريخيًا سلبي")
    if si >= 90:
        v -= 1
        lines.append("  المضاربين لونج زحمة → خطر نزول تصفية")
    elif si <= 10:
        v += 1
        lines.append("  المضاربين خرجوا تقريبًا → مساحة للطلوع")
    if c.get("spec_chg_4w"):
        lines.append(f"  تغير صافي المضاربين 4 أسابيع: {c['spec_chg_4w']:+,.0f} عقد")
    return {"vote": max(-1, min(1, v)), "lines": lines}
