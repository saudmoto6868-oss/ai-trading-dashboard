"""Weekly briefing in Egyptian Arabic for Telegram (owner 2026-11-06): 'this week gold is going down, next week it may go
up about X dollars an ounce' - built from the Spot analyzer bundle (spot_dash.load_bundle).

The expected move is STATISTICAL, not a promise: the typical weekly range = ATR 14 of the weekly candles (average true range),
in dollars per ounce for metals and in dollars + % for crypto. The direction comes from the confluence score of the schools
(not backtested -> said in the message). Levels: staged buys / targets / invalidation from spot_plan, the nearest bullish FVG /
order block, the Elliott state, the Gann time window and SMT."""
from __future__ import annotations

import math

UNIT = {"GOLD": "دولار للأونصة", "SILVER": "دولار للأونصة", "PLATINUM": "دولار للأونصة", "PALLADIUM": "دولار للأونصة", "COPPER": "دولار للرطل"}
NAME = {"GOLD": "الدهب", "SILVER": "الفضة", "PLATINUM": "البلاتين", "PALLADIUM": "البلاديوم", "COPPER": "النحاس", "BTC": "البيتكوين", "ETH": "الإيثريوم"}


def _f(x):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    return f"{x:,.0f}" if abs(x) >= 1000 else f"{x:,.2f}" if abs(x) >= 1 else f"{x:.5f}"


def outlook(b: dict) -> dict:
    """Numbers for the message: price, week change, weekly ATR, direction, ranges, levels."""
    w = b["reads"].get("1w") or {}
    px = b.get("price") or (w.get("px") if w.get("ok") else None)
    o = {"asset": b["symbol"], "price": px, "score": b["conf"]["score"], "per_tf": b["conf"]["per_tf"]}
    if w.get("ok"):
        c = w["c"]
        o["week_chg"] = float(c[-1] - c[-2]) if len(c) > 1 else None
        o["week_pct"] = float(c[-1] / c[-2] - 1) * 100 if len(c) > 1 else None
        o["atr_w"] = float(w["atr"]) or None
        o["trend_w"] = w.get("trend")
        o["dr_w"] = w.get("dr")
        bull_fvg = [z for z in w.get("fvg", []) if z["side"] == "bull" and z["hi"] < (px or 0)]
        bull_ob = [z for z in w.get("obs", []) if z["side"] == "bull" and z["hi"] < (px or 0)]
        o["support_zone"] = max(bull_fvg + bull_ob, key=lambda z: z["hi"], default=None)
        o["elliott_w"] = (w.get("elliott") or {}).get("kind")
        g = (w.get("gann") or {}).get("fit") or {}
        o["gann_turn_w"] = g.get("bars_to_turn")
    m = b["reads"].get("1mo") or {}
    o["trend_m"] = m.get("trend") if m.get("ok") else None
    pl = b.get("plan") or {}
    o["buys"], o["sells"], o["inval"] = pl.get("buys", []), pl.get("sells", []), pl.get("invalidation")
    sc = o["score"]
    o["bias"] = "up" if sc >= 20 else "down" if sc <= -20 else "flat"
    a = o.get("atr_w")
    if a and px:
        o["range"] = (px - a, px + a)
        o["up_to"] = min([x for x in o["sells"] if x > px] + [px + a])
        o["down_to"] = max([x for x in o["buys"] if x < px] + [px - a])
    o["smt"] = b.get("smt_text", [])
    return o


def message_ar(o: dict) -> str:
    a = o["asset"]
    nm = NAME.get(a, a)
    unit = UNIT.get(a, "دولار")
    is_metal = a in UNIT
    px = o.get("price")
    lines = [f"📊 {nm} - تقرير الأسبوع", f"السعر دلوقتي: {_f(px)} {unit if is_metal else '$'}"]
    if o.get("week_chg") is not None:
        verb = "نازل" if o["week_chg"] < 0 else "طالع"
        lines.append(f"الأسبوع ده {nm} {verb} {_f(abs(o['week_chg']))} {unit if is_metal else '$'} ({o['week_pct']:+.1f}%).")
    if o.get("atr_w") and px:
        pct = o["atr_w"] / px * 100
        lines.append(f"الحركة المعتادة في الأسبوع (متوسط المدى ATR): حوالي {_f(o['atr_w'])} {unit if is_metal else '$'} = {pct:.1f}%.")
    trend = {"up": "صاعد", "down": "هابط"}
    lines.append(f"الاتجاه: الشهري {trend.get(o.get('trend_m'), 'مش واضح')} · الأسبوعي {trend.get(o.get('trend_w'), 'مش واضح')} · درجة المدارس {o['score']:+d}")
    if o.get("range"):
        lo, hi = o["range"]
        if o["bias"] == "up":
            lines.append(f"الأسبوع الجاي: الميل للطلوع. ممكن يوصل لحد {_f(o['up_to'])} (+{_f(o['up_to'] - px)}). لو رجع، الدعم عند {_f(o['down_to'])}.")
        elif o["bias"] == "down":
            lines.append(f"الأسبوع الجاي: الميل للنزول. ممكن ينزل لحد {_f(o['down_to'])} (-{_f(px - o['down_to'])}). ده مكان شراء سبوت مش بيع. المقاومة عند {_f(o['up_to'])}.")
        else:
            lines.append(f"الأسبوع الجاي: مفيش اتجاه واضح. المدى المتوقع تقريبًا {_f(lo)} - {_f(hi)}.")
    dr = o.get("dr_w")
    if dr:
        lines.append(f"ICT: السعر في {'الديسكاونت (منطقة شراء)' if dr['zone'] == 'discount' else 'البريميوم (منطقة غالية للشراء)'} - {dr['pos'] * 100:.0f}% من الرينج الأسبوعي.")
    z = o.get("support_zone")
    if z:
        lines.append(f"SMC: أقرب منطقة طلب أسبوعية {_f(z['lo'])} - {_f(z['hi'])}.")
    ew = {"impulse_up": "دافعة صاعدة (5 موجات)", "impulse_down": "دافعة هابطة (5 موجات)", "abc": "تصحيح ABC"}.get(o.get("elliott_w"))
    if ew:
        lines.append(f"اليوت (أسبوعي): {ew}.")
    if o.get("gann_turn_w") is not None and o["gann_turn_w"] <= 2:
        lines.append(f"جان: نافذة انعكاس زمنية خلال {o['gann_turn_w']} أسبوع - خلي بالك من تغيير الاتجاه.")
    for s in o.get("smt", [])[:2]:
        lines.append(f"SMT: {s}")
    if o.get("buys"):
        lines.append("خطة الشراء على دفعات: " + " / ".join(_f(x) for x in o["buys"]) + (f" · الإلغاء تحت {_f(o['inval'])} (قفلة أسبوعية)" if o.get("inval") else ""))
    if o.get("sells"):
        lines.append("أهداف جني الربح: " + " / ".join(_f(x) for x in o["sells"]))
    lines.append("⚠️ الأرقام دي مدى إحصائي من حركة الأسابيع اللي فاتت، مش وعد. درجة المدارس لسه ماتعملهاش باك تيست. مفيش أي أمر بيتنفذ.")
    return "\n".join(lines)


def build(asset: str, candles=None) -> tuple[dict, str]:
    """-> (bundle, Arabic message) for one asset (network unless `candles` is injected)."""
    from modules import spot_dash
    b = spot_dash.load_bundle(asset, candles)
    return b, message_ar(outlook(b))
