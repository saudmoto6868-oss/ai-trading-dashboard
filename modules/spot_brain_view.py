"""Spot brain screen - a mosaic of small tiles like the owner's reference picture (2026-11-06): charcoal tiles, amber line
charts, amber rings and a solid amber disc, big numbers, amber bars on the right, a row of small tiles at the bottom.
render(brain, markets) -> HTML (components.html / Telegram image). Pure SVG + CSS."""
from __future__ import annotations

import html as _h
import math
from datetime import datetime, timezone

import numpy as np

A, A2, BG, T, D, L, P, BL, RED = "#ffc21a", "#ffdf73", "#0d0e10", "#eceef1", "#7f8590", "#24262b", "#141518", "#5b8cff", "#e05a5a"
HZ = [("day", "يوم-3"), ("week", "أسبوع-4"), ("month", "شهر-3"), ("year", "6-12 شهر")]
CSS = f"""<style>*{{box-sizing:border-box}}body{{margin:0;background:{BG};color:{T};font-family:Inter,Segoe UI,Tahoma,Arial,sans-serif}}
svg{{direction:ltr}} .m{{display:grid;grid-template-columns:2.15fr 1fr;gap:10px;padding:12px;max-width:1600px;margin:auto}}
.col{{display:grid;gap:10px;align-content:start}} .row{{display:grid;gap:10px}} .t{{background:{P};border:1px solid {L};border-radius:4px;padding:10px;min-width:0;position:relative}}
.h{{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:{D};display:flex;justify-content:space-between;margin-bottom:6px}} .h b{{color:{A}}}
.n{{font-size:28px;font-weight:800;line-height:1.05;unicode-bidi:plaintext}} .s{{font-size:11px;color:{D}}} .a{{color:{A}}} .r{{color:{RED}}}
.disc{{width:118px;height:118px;border-radius:50%;background:{A};color:#111;display:flex;flex-direction:column;align-items:center;justify-content:center;margin:auto;font-weight:800;text-align:center}}
.bar{{background:{A};color:#111;border-radius:3px;padding:9px 10px;font-weight:800;display:flex;justify-content:space-between;margin-top:6px;font-size:13px}}
.bar.o{{background:transparent;color:{A};border:1px solid {A}}} .bar.x{{background:{RED};color:#fff}}
table{{width:100%;border-collapse:collapse;font-size:11px}} td{{padding:4px 3px;border-bottom:1px solid {L}}} .dot{{display:inline-block;width:9px;height:9px;border-radius:50%}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:10px}} .g4{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}} .g6{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}}
.ln{{font-size:12px;line-height:1.65}} @media(max-width:1000px){{.m{{grid-template-columns:1fr}}.g4,.g6{{grid-template-columns:1fr 1fr}}}}</style>"""


def e(s) -> str:
    return _h.escape(str(s))


def f(x):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    ax = abs(x)
    return f"{x:,.0f}" if ax >= 1000 else f"{x:,.2f}" if ax >= 1 else f"{x:.4f}"


def ring(score, size=96, label="", fill=False):
    r = size / 2 - 8
    c = 2 * math.pi * r
    col = A if score > 0 else D if score == 0 else "#a7adb8"
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}"><circle cx="{size / 2}" cy="{size / 2}" r="{r}" fill="none" stroke="{L}" stroke-width="8"/>'
            f'<circle cx="{size / 2}" cy="{size / 2}" r="{r}" fill="none" stroke="{col}" stroke-width="8" stroke-dasharray="{c * min(1, abs(score) / 100):.1f} {c:.1f}" '
            f'transform="rotate(-90 {size / 2} {size / 2})" stroke-linecap="round"/><text x="50%" y="{size / 2 + 4}" text-anchor="middle" fill="{T}" font-size="{size * .22:.0f}" font-weight="800">{score:+d}</text>'
            f'<text x="50%" y="{size / 2 + size * .2:.0f}" text-anchor="middle" fill="{D}" font-size="{size * .11:.0f}">{e(label)}</text></svg>')


def line(vals, W=420, H=150, levels=None, dots=True, col=A, area=True):
    v = np.asarray([x for x in vals if x is not None and math.isfinite(x)], float)
    if len(v) < 3:
        return f'<div class="s">مفيش داتا</div>'
    lv = [x for x in (levels or []) if x[0] is not None]
    lo, hi = min(v.min(), *[x[0] for x in lv]) if lv else v.min(), max(v.max(), *[x[0] for x in lv]) if lv else v.max()
    pad = (hi - lo) * .08 or 1
    lo, hi = lo - pad, hi + pad
    X = lambda i: 4 + i * (W - 58) / (len(v) - 1)
    Y = lambda p: 6 + (hi - p) / (hi - lo) * (H - 14)
    s = [f'<line x1="4" x2="{W - 54}" y1="{Y(lo + (hi - lo) * k / 4):.1f}" y2="{Y(lo + (hi - lo) * k / 4):.1f}" stroke="{L}" stroke-width=".6"/>' for k in range(5)]
    for val, lab, c2, dash in lv:
        y = Y(val)
        s.append(f'<line x1="4" x2="{W - 54}" y1="{y:.1f}" y2="{y:.1f}" stroke="{c2}" stroke-width="1" stroke-dasharray="{dash}"/><text x="{W - 52}" y="{y + 3:.1f}" fill="{c2}" font-size="9">{e(lab)}</text>')
    pts = " ".join(f"{X(i):.1f},{Y(p):.1f}" for i, p in enumerate(v))
    if area:
        s.append(f'<polygon points="4,{H - 4} {pts} {X(len(v) - 1):.1f},{H - 4}" fill="{col}" opacity=".07"/>')
    s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.6"/>')
    if dots:
        idx = sorted(set([int(np.argmax(v)), int(np.argmin(v)), len(v) - 1]))
        s += [f'<circle cx="{X(i):.1f}" cy="{Y(v[i]):.1f}" r="3" fill="{col}"/>' for i in idx]
    return f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="none" height="{H}">{"".join(s)}</svg>'


def hbars(profile, mids, poc, px, W=260, H=150):
    if not profile:
        return '<div class="s">مفيش بروفايل</div>'
    p = np.asarray(profile, float)
    n = len(p)
    bh = H / n
    mx = p.max() or 1
    s = []
    for i, (v, m) in enumerate(zip(p[::-1], list(mids)[::-1])):
        w = v / mx * (W - 60)
        col = A if abs(m - poc) / max(poc, 1e-9) < 0.004 else "#3a3d44"
        s.append(f'<rect x="0" y="{i * bh:.1f}" width="{w:.1f}" height="{max(1, bh - 1):.1f}" fill="{col}"/>')
    lo, hi = min(mids), max(mids)
    if lo < px < hi:
        y = (hi - px) / (hi - lo) * H
        s.append(f'<line x1="0" x2="{W - 60}" y1="{y:.1f}" y2="{y:.1f}" stroke="{T}" stroke-dasharray="3 2"/><text x="{W - 56}" y="{y + 3:.1f}" fill="{T}" font-size="9">{f(px)}</text>')
    s.append(f'<text x="{W - 56}" y="12" fill="{A}" font-size="9">POC {f(poc)}</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" height="{H}">{"".join(s)}</svg>'


def _tile(head, body, right=""):
    return f'<div class="t"><div class="h"><span>{e(head)}</span><b>{e(right)}</b></div>{body}</div>'


def render(br: dict, markets: list | None = None) -> str:
    b = br["bundle"]
    R = b["reads"]
    px = br["price"]
    hz = br["horizons"]
    fl = br.get("raw_flow") or {}
    ct = br.get("raw_cot") or {}
    st = br.get("stats") or {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    best = max(hz.values(), key=lambda h: h["score"])
    out = [f'<html dir="rtl"><head><meta charset="utf-8">{CSS}</head><body>']
    out.append(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px 0;max-width:1600px;margin:auto">'
               f'<div><span style="font-size:13px;letter-spacing:.2em;color:{D}">SPOT BRAIN</span> <span class="a" style="font-weight:800">· العقل المدبر للسبوت</span></div>'
               f'<div class="s">{e(br["name"])} · {e(b.get("source", ""))} · {now}</div></div>')
    out.append('<div class="m"><div class="col">')
    # row 1: market list | numbers + disc | weekly line chart
    mk = "".join(f'<tr><td>{e(m["name"])}</td><td dir="ltr">{f(m["price"])}</td><td dir="ltr" class="{"a" if m["wk"] >= 0 else "r"}">{m["wk"]:+.1f}%</td>'
                 f'<td><span class="dot" style="background:{A if m["score"] > 10 else RED if m["score"] < -10 else D}"></span></td></tr>' for m in (markets or [])[:9])
    w1 = R.get("1w") or {}
    plan = b.get("plan") or {}
    wl = [(plan.get("invalidation"), "إلغاء", RED, "4 3")] + [(x, f"شراء{i + 1}", A, "2 3") for i, x in enumerate(plan.get("buys", [])[:3])] + \
         [(x, f"T{i + 1}", A2, "6 3") for i, x in enumerate(plan.get("sells", [])[:2])]
    wkchg = (float(w1["c"][-1] / w1["c"][-2] - 1) * 100) if w1.get("ok") else None
    out.append('<div class="row" style="grid-template-columns:1fr .9fr 1.6fr">'
               + _tile("الأسواق", f"<table>{mk}</table>" if mk else '<div class="s">—</div>', f"{len(markets or [])}")
               + f'<div class="col">{_tile("السعر", f"<div class=n dir=ltr>{f(px)}</div><div class=s dir=ltr>{(wkchg or 0):+.2f}% أسبوع</div>")}'
               f'<div class="t"><div class="disc"><div style="font-size:11px">القرار</div><div style="font-size:19px">{e(best["verdict_ar"])}</div>'
               f'<div style="font-size:11px">{e(best["label"])}</div></div></div></div>'
               + _tile("الأسبوعي - مستويات الخطة", line(list(w1.get("c", []))[-104:], 520, 205, wl), e(br["head"])[:48]) + "</div>")
    # row 2: four horizon rings with verdict + levels
    cells = []
    for k, lab in HZ:
        h = hz[k]
        ent = h.get("entry")
        lv = (f'<div class="s" dir="ltr">دخول {f(ent[0])}-{f(ent[1])} · وقف {f(h.get("stop"))} · هدف {f(h.get("target"))}' + (f' · {h["rr"]:.1f}R' if h.get("rr") else "") + "</div>") if ent else ""
        rs = "".join(f'<div class="ln">• {e(x)}</div>' for x in h["reasons"][:3])
        cells.append(f'<div class="t"><div class="h"><span>{e(lab)}</span><b>{e(h["verdict_ar"])}</b></div><div style="display:flex;gap:8px;align-items:center">'
                     f'{ring(h["score"], 84, h["tf"])}<div style="min-width:0">{lv}{rs}</div></div></div>')
    out.append('<div class="row" style="grid-template-columns:1fr 1fr">' + "".join(cells) + "</div>")
    # row 3: daily + 4H line charts | CVD | volume profile
    d1, h4 = R.get("1d") or {}, R.get("4h") or {}
    tk, tp, vp = fl.get("taker") or {}, fl.get("tape") or {}, fl.get("vp") or {}
    cvd = tk.get("cvd") if tk.get("ok") else tp.get("cvd") if tp.get("ok") else []
    out.append('<div class="row" style="grid-template-columns:1.25fr 1.25fr 1fr 1fr">'
               + _tile("اليومي", line(list(d1.get("c", []))[-120:], 360, 150, [((d1.get("dr") or {}).get("eq"), "EQ", A2, "2 4")]), f'{(hz["week"]["score"]):+d}')
               + _tile("4 ساعات", line(list(h4.get("c", []))[-120:], 360, 150, [(hz["day"].get("stop"), "وقف", RED, "4 3")]), f'{(hz["day"]["score"]):+d}')
               + _tile("CVD دلتا تراكمي", line(cvd[-300:], 260, 150, [(0.0, "0", D, "2 3")], dots=False, col=A2 if (cvd and cvd[-1] >= 0) else "#a7adb8"),
                       "24س" if tk.get("ok") else "آخر صفقات")
               + _tile("الفوت برينت - بروفايل 7 أيام", hbars(vp.get("profile"), vp.get("mids", []), vp.get("poc", 0), px or 0) if vp.get("ok") else f'<div class="s">{e(vp.get("why", "—"))}</div>', "POC")
               + "</div>")
    # row 4: schools strip
    votes = []
    for tf, nm in (("1mo", "شهري"), ("1w", "أسبوعي"), ("1d", "يومي"), ("4h", "4س")):
        r = R.get(tf) or {}
        if not r.get("ok"):
            continue
        dots = "".join(f'<span title="{k}" class="dot" style="background:{A if v > 0 else "#a7adb8" if v < 0 else L};margin:0 2px"></span>' for k, v in r["votes"].items())
        votes.append(f"<tr><td>{nm}</td><td>{dots}</td></tr>")
    ew = (w1.get("elliott") or {}).get("kind")
    gn = ((w1.get("gann") or {}).get("fit") or {})
    pats = ", ".join(sorted({i["title"] for i in br.get("ideas", [])})) or "—"
    out.append('<div class="row" style="grid-template-columns:1fr 1fr 1fr">'
               + _tile("المدارس · MA RSI MACD SMC ICT اليوت", f"<table>{''.join(votes)}</table>")
               + _tile("اليوت · جان", f'<div class="ln">اليوت أسبوعي: <b class="a">{e({"impulse_up": "دافعة صاعدة", "impulse_down": "دافعة هابطة", "abc": "تصحيح ABC"}.get(ew, "—"))}</b></div>'
                       f'<div class="ln">جان: دورة {gn.get("tsp", "—")} أسبوع · الانعكاس بعد {gn.get("bars_to_turn", "—")}</div>'
                       f'<div class="ln">مربع التسعة الأقرب: {" / ".join(f(v) for v in sorted((w1.get("gann") or {}).get("sq9", []), key=lambda v: abs(v - (px or 0)))[:2])}</div>')
               + _tile("السيت أبات الشغالة دلوقتي", "".join(
                   f'<div class="ln">{"🟢" if x["side"] == "buy" else "🔴"} <b>{e(x["tf"])}</b> {e(x["name"][:58])}<div class="s">{e(x["ev_label"])}</div></div>'
                   for x in (br.get("setups") or [])[:7]) or f'<div class="ln">{e(pats)}</div>', f'{len(br.get("setups") or [])}') + "</div>")
    out.append('</div><div class="col">')
    # right column: KPI tiles 2 cols + rings + amber bars
    dv = fl.get("deriv") or {}
    bk = fl.get("book") or {}
    pr = fl.get("premium") or {}
    k = [("التمويل", f'{dv["funding"]:+.4f}%' if dv.get("funding") is not None else "—", "لونج زحمة لو عالي"),
         ("OI أسبوع", f'{dv["oi_chg_7d"]:+.1f}%' if dv.get("oi_chg_7d") is not None else "—", "فلوس داخلة / خارجة"),
         ("لونج/شورت", f'{dv["ls_ratio"]:.2f}' if dv.get("ls_ratio") else "—", "عدد الحسابات"),
         ("بريميوم كوين بيس", f'{pr["premium_pct"]:+.3f}%' if pr.get("ok") else "—", "طلب أمريكي"),
         ("الدفتر ±1%", f'{bk["imbalance"] * 100:+.0f}%' if bk.get("ok") else "—", "شراء − بيع"),
         ("مشتري بالسوق", f'{tp["buy_share"] * 100:.0f}%' if tp.get("ok") else "—", f'{tp.get("n", 0)} صفقة'),
         ("مضاعف ماير", f(st.get("mayer")), "<1 رخيص · >2.4 سخن"), ("عن 200 أسبوع", f'{st["dist_200w"]:+.0f}%' if "dist_200w" in st else "—", "القيمة"),
         ("من القمة", f'{st["dd_ath"]:+.0f}%' if "dd_ath" in st else "—", "أعلى سعر تاريخي"), ("ADX يومي", f(d1.get("adx")), "قوة الترند")]
    out.append('<div class="g2">' + "".join(_tile(a, f'<div class="n" style="font-size:22px" dir="ltr">{e(v)}</div><div class="s">{e(c)}</div>') for a, v, c in k) + "</div>")
    if ct.get("ok"):
        out.append('<div class="g2">' + _tile("COT التجار", ring(round(ct["comm_idx"] * 2 - 100), 92, "فلوس ذكية"), f'{ct["comm_idx"]:.0f}%')
                   + _tile("COT المضاربين", ring(round(ct["spec_idx"] * 2 - 100), 92, "صناديق"), f'{ct["spec_idx"]:.0f}%') + "</div>")
        out.append(_tile("صافي المضاربين (سنتين)", line(ct.get("spec_series", []), 380, 90, dots=False), ct.get("date", "")))
    else:
        out.append(_tile("المؤسسات COT", f'<div class="s">{e(ct.get("why", "مش متاح للسوق ده"))}</div>'))
    g = br.get("guard") or []
    bars = "".join(f'<div class="bar{" x" if x["action"] in ("exit", "reduce") else " o" if x["action"] == "protect" else ""}"><span>{e(x["action_ar"])} · {e(x["why"])[:40]}</span>'
                   f'<span dir="ltr">{(x.get("pnl_pct") or 0):+.1f}%</span></div>' for x in g)
    out.append(_tile("اللي معانا - الحماية", bars or '<div class="s">مفيش مركز متسجل للسوق ده في السجل</div>'))
    buys = "".join(f'<div class="bar"><span>{e(h["label"])} · {e(h["verdict_ar"])}</span><span dir="ltr">{f((h["entry"][0] + h["entry"][1]) / 2) if h.get("entry") else "—"}</span></div>'
                   for h in sorted(hz.values(), key=lambda h: -h["score"]) if h["score"] >= 15)
    out.append(_tile("أفضل دخول", buys or '<div class="bar o"><span>مفيش مدة فيها ميزة</span><span>استنى</span></div>'))
    out.append("</div></div>")
    # bottom row: news + flow lines
    nws = (br.get("news") or {}).get("items", [])[:4]
    tiles = [_tile("خبر", f'<div class="ln">{e(x["title"][:95])}</div><div class="s">{e(" · ".join(x["why"][:1]) or "ذكر السوق")}</div>',
                   "▲" if x["push"].get(br["asset"], 0) > 0 else "▼" if x["push"].get(br["asset"], 0) < 0 else "•") for x in nws]
    tiles += [_tile("الأوردر فلو", "".join(f'<div class="ln">• {e(x)}</div>' for x in br["flow"]["lines"][:3]))]
    tiles += [_tile("المؤسسات", "".join(f'<div class="ln">{e(x)}</div>' for x in br["inst"]["lines"][:3]))]
    out.append('<div style="max-width:1600px;margin:auto;padding:0 12px 12px"><div class="g6">' + "".join(tiles[:6]) + "</div>"
               '<div class="s" style="margin-top:8px">قواعد من المدارس والأوردر فلو وتقارير COT، لسه من غير باك تيست لكل مدة. السبوت شراء بس - «بيع» هنا يعني تخرج من اللي معاك. مفيش أي أمر بيتنفذ.</div></div>')
    out.append("</body></html>")
    return "".join(out)
