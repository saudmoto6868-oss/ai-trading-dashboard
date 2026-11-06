"""Spot analyzer dashboard (owner 2026-11-06, style from the owner's reference picture: charcoal panels, amber accent,
rings, small KPI cards, big charts side by side). Pure SVG + CSS from Python: no chart library, nothing loaded from the web.

render(bundle) -> one HTML page for st.components.v1.html. bundle comes from load_bundle(symbol) (network) or tests (mocks)."""
from __future__ import annotations

import html as _h
import math

import numpy as np

from modules import spot_ind as I

AMB, AMB2, BEAR, TXT, DIM, BG, PANEL, LINE = "#f7b500", "#ffd34d", "#9aa3b2", "#e9eaec", "#80858f", "#1a1b1e", "#111214", "#26282d"
BLUE = "#5b8cff"
TFS = ("1mo", "1w", "1d", "4h")
TF_NAME = {"1mo": ("Monthly", "شهري"), "1w": ("Weekly", "أسبوعي"), "1d": ("Daily", "يومي"), "4h": ("4 hours", "4 ساعات")}
BARS = {"1mo": 120, "1w": 156, "1d": 180, "4h": 180}
FAM = [("ma", "Moving averages", "المتوسطات"), ("rsi", "RSI / divergence", "RSI والدايفرجنس"), ("macd", "MACD", "MACD"),
       ("smc", "SMC structure", "هيكل SMC"), ("ict", "ICT premium / discount", "ICT بريميوم / ديسكاونت"), ("elliott", "Elliott", "اليوت"),
       ("smt", "SMT", "SMT")]


def _t(ar: bool, en: str, a: str) -> str:
    return a if ar else en


def _f(x, nd=2):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    ax = abs(x)
    if ax >= 1e5:
        return f"{x:,.0f}"
    if ax >= 100:
        return f"{x:,.1f}"
    if ax >= 1:
        return f"{x:,.{nd}f}"
    return f"{x:.5f}"


def esc(s) -> str:
    return _h.escape(str(s))


# ---------------------------------------------------------------- SVG pieces
def ring(score: int, size: int = 92, label: str = "", sub: str = "") -> str:
    """Amber ring gauge: arc = |score| %, colour by side."""
    r = size / 2 - 7
    circ = 2 * math.pi * r
    frac = min(1, abs(score) / 100)
    col = AMB if score > 0 else BEAR if score < 0 else DIM
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}"><circle cx="{size / 2}" cy="{size / 2}" r="{r}" fill="none" stroke="{LINE}" stroke-width="7"/>'
            f'<circle cx="{size / 2}" cy="{size / 2}" r="{r}" fill="none" stroke="{col}" stroke-width="7" stroke-linecap="round" '
            f'stroke-dasharray="{circ * frac:.1f} {circ:.1f}" transform="rotate(-90 {size / 2} {size / 2})"/>'
            f'<text x="50%" y="{size / 2 + 2}" text-anchor="middle" fill="{TXT}" font-size="{size * 0.24:.0f}" font-weight="700">{score:+d}</text>'
            f'<text x="50%" y="{size / 2 + size * 0.2:.0f}" text-anchor="middle" fill="{DIM}" font-size="{size * 0.11:.0f}">{esc(label)}</text></svg>'
            + (f'<div class="rs">{esc(sub)}</div>' if sub else ""))


def spark(vals, w=260, h=70, col=AMB, ref=None) -> str:
    v = np.asarray([x for x in vals if x is not None and math.isfinite(x)], float)
    if len(v) < 2:
        return f'<svg width="{w}" height="{h}"></svg>'
    lo, hi = v.min(), v.max()
    if hi == lo:
        hi = lo + 1
    pts = " ".join(f"{i * (w - 4) / (len(v) - 1) + 2:.1f},{h - 4 - (x - lo) / (hi - lo) * (h - 8):.1f}" for i, x in enumerate(v))
    refl = ""
    if ref is not None and lo <= ref <= hi:
        y = h - 4 - (ref - lo) / (hi - lo) * (h - 8)
        refl = f'<line x1="0" x2="{w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{DIM}" stroke-dasharray="3 3"/>'
    area = f'<polygon points="2,{h - 2} {pts} {w - 2},{h - 2}" fill="{col}" opacity="0.08"/>'
    return f'<svg width="100%" viewBox="0 0 {w} {h}" preserveAspectRatio="none" height="{h}">{refl}{area}<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.6"/></svg>'


def chart(r: dict, tf: str, ar: bool, W: int = 640, H: int = 330) -> str:
    """Candles + EMA 20 / 50 / 200 + SMC / ICT boxes + structure breaks + Elliott labels + Gann levels + RSI and MACD strips."""
    n = r["n"]
    k = min(n, BARS.get(tf, 150))
    i0 = n - k
    o, h, l_, c = r["o"][i0:], r["h"][i0:], r["l"][i0:], r["c"][i0:]
    logy = tf in ("1mo", "1w") and l_.min() > 0 and h.max() / max(l_.min(), 1e-12) > 3
    tr = (lambda v: math.log(v)) if logy else (lambda v: v)
    lo, hi = tr(float(l_.min())), tr(float(h.max()))
    pad = (hi - lo) * 0.06 or 1
    lo, hi = lo - pad, hi + pad
    PH, RH, MH, G = H, 70, 54, 6            # price / rsi / macd heights
    L, R = 6, 62                             # right axis width
    cw = (W - L - R) / k
    X = lambda i: L + (i - i0 + 0.5) * cw
    Y = lambda v: 8 + (hi - tr(max(v, 1e-12) if logy else v)) / (hi - lo) * (PH - 16)
    s = []
    for q in range(5):                        # grid + price axis
        v = lo + (hi - lo) * q / 4
        pv = math.exp(v) if logy else v
        y = Y(pv)
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{LINE}" stroke-width="0.6"/><text x="{W - R + 4}" y="{y + 3:.1f}" fill="{DIM}" font-size="9">{_f(pv)}</text>')
    dr = r.get("dr")
    if dr:                                    # ICT: premium / discount / equilibrium + OTE
        ya, yb, ye = Y(dr["hi"]), Y(dr["lo"]), Y(dr["eq"])
        s.append(f'<rect x="{L}" y="{ya:.1f}" width="{W - L - R}" height="{max(0, ye - ya):.1f}" fill="{BEAR}" opacity="0.05"/>')
        s.append(f'<rect x="{L}" y="{ye:.1f}" width="{W - L - R}" height="{max(0, yb - ye):.1f}" fill="{AMB}" opacity="0.05"/>')
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{ye:.1f}" y2="{ye:.1f}" stroke="{AMB}" stroke-dasharray="2 4" opacity="0.7"/><text x="{L + 3}" y="{ye - 3:.1f}" fill="{AMB}" font-size="9">EQ 50%</text>')
        o1, o2 = sorted(dr["ote"])
        s.append(f'<rect x="{X(max(i0, min(dr["i_hi"], dr["i_lo"]))):.1f}" y="{Y(o2):.1f}" width="{W - R - X(max(i0, min(dr["i_hi"], dr["i_lo"]))):.1f}" height="{max(1, Y(o1) - Y(o2)):.1f}" fill="none" stroke="{AMB2}" stroke-dasharray="4 3" opacity="0.6"/>'
                 f'<text x="{W - R - 30}" y="{Y(o2) - 2:.1f}" fill="{AMB2}" font-size="8">OTE</text>')
    for z in r.get("fvg", []):               # fair value gaps
        if z["i"] < i0:
            continue
        col = AMB if z["side"] == "bull" else BEAR
        s.append(f'<rect x="{X(z["i"]):.1f}" y="{Y(z["hi"]):.1f}" width="{W - R - X(z["i"]):.1f}" height="{max(1, Y(z["lo"]) - Y(z["hi"])):.1f}" fill="{col}" opacity="0.13"/>'
                 f'<text x="{X(z["i"]) + 2:.1f}" y="{Y(z["hi"]) + 9:.1f}" fill="{col}" font-size="8">FVG</text>')
    for b in r.get("obs", []):               # order blocks
        if b["i"] < i0:
            continue
        col = AMB if b["side"] == "bull" else BEAR
        s.append(f'<rect x="{X(b["i"]) - cw / 2:.1f}" y="{Y(b["hi"]):.1f}" width="{W - R - X(b["i"]) + cw / 2:.1f}" height="{max(1, Y(b["lo"]) - Y(b["hi"])):.1f}" fill="none" stroke="{col}" stroke-width="1"/>'
                 f'<text x="{X(b["i"]) + 2:.1f}" y="{Y(b["lo"]) - 2:.1f}" fill="{col}" font-size="8">OB</text>')
    for q in r.get("liq", []):               # equal highs / lows
        if q["i2"] < i0:
            continue
        y = Y(q["level"])
        s.append(f'<line x1="{X(max(i0, q["i1"])):.1f}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{BLUE}" stroke-dasharray="1 3"/><text x="{W - R - 22}" y="{y - 2:.1f}" fill="{BLUE}" font-size="8">{"EQH" if q["side"] == "buy-side" else "EQL"}</text>')
    gn = r.get("gann") or {}
    if tf in ("1mo", "1w"):
        for v in sorted(gn.get("sq9", []), key=lambda v: abs(v - c[-1]))[:4]:   # Gann square of 9: the 4 nearest levels
            if l_.min() * 0.9 <= v <= h.max() * 1.1:
                y = Y(v)
                if 8 <= y <= PH - 8:
                    s.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="#b06cff" stroke-width="0.6" stroke-dasharray="6 4" opacity="0.6"/>')
    for i in range(k):                        # candles
        bull = c[i] >= o[i]
        x = L + (i + 0.5) * cw
        col = AMB if bull else BEAR
        y1, y2 = Y(max(o[i], c[i])), Y(min(o[i], c[i]))
        s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{Y(h[i]):.1f}" y2="{Y(l_[i]):.1f}" stroke="{col}" stroke-width="0.8"/>'
                 f'<rect x="{x - cw * 0.35:.1f}" y="{y1:.1f}" width="{max(0.8, cw * 0.7):.1f}" height="{max(0.8, y2 - y1):.1f}" fill="{col if bull else BG}" stroke="{col}" stroke-width="0.7"/>')
    for key, col, wd in (("e20", TXT, 0.8), ("e50", AMB, 1.3), ("e200", BLUE, 1.3)):   # EMAs
        v = r.get(key)
        if v is None:
            continue
        pts = " ".join(f"{L + (i + 0.5) * cw:.1f},{Y(v[i0 + i]):.1f}" for i in range(k) if np.isfinite(v[i0 + i]))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{wd}" opacity="0.9"/>')
    for e in r.get("events", [])[-4:]:       # BOS / CHoCH (last 4, to stay readable)
        if e["from"] < i0:
            continue
        y = Y(e["level"])
        col = AMB if e["dir"] == "up" else BEAR
        s.append(f'<line x1="{X(e["from"]):.1f}" x2="{X(e["i"]):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="0.9"/>'
                 f'<text x="{(X(e["from"]) + X(e["i"])) / 2:.1f}" y="{y + (-3 if e["dir"] == "up" else 10):.1f}" text-anchor="middle" fill="{col}" font-size="8.5" font-weight="700">{e["kind"]}</text>')
    ew = r.get("elliott") or {}
    labs = [x for x in ew.get("labels", []) if x[0] >= i0]
    if labs:                                  # Elliott count
        pts = " ".join(f"{X(i):.1f},{Y(p):.1f}" for i, p, _ in labs)
        s.append(f'<polyline points="{pts}" fill="none" stroke="{TXT}" stroke-width="0.9" stroke-dasharray="3 2" opacity="0.7"/>')
        for i, p, t in labs:
            above = p >= np.median([q for _, q, _ in labs])
            s.append(f'<circle cx="{X(i):.1f}" cy="{Y(p) + (-11 if above else 11):.1f}" r="7" fill="{PANEL}" stroke="{AMB}" stroke-width="0.8"/>'
                     f'<text x="{X(i):.1f}" y="{Y(p) + (-8 if above else 14):.1f}" text-anchor="middle" fill="{AMB}" font-size="8.5" font-weight="700">{t}</text>')
    px = float(c[-1])
    s.append(f'<rect x="{W - R}" y="{Y(px) - 7:.1f}" width="{R - 2}" height="14" rx="3" fill="{AMB}"/><text x="{W - R + 4}" y="{Y(px) + 3.5:.1f}" fill="#111" font-size="9" font-weight="700">{_f(px)}</text>')
    # RSI strip with divergences
    y0 = PH + G
    rs = r["rsi"][i0:]
    RY = lambda v: y0 + (100 - v) / 100 * RH
    s.append(f'<rect x="{L}" y="{y0}" width="{W - L - R}" height="{RH}" fill="{PANEL}"/>')
    for lv in (70, 50, 30):
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{RY(lv):.1f}" y2="{RY(lv):.1f}" stroke="{LINE}" stroke-dasharray="{"" if lv == 50 else "2 3"}"/><text x="{W - R + 4}" y="{RY(lv) + 3:.1f}" fill="{DIM}" font-size="8">{lv}</text>')
    pts = " ".join(f"{L + (i + 0.5) * cw:.1f},{RY(v):.1f}" for i, v in enumerate(rs) if np.isfinite(v))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{AMB}" stroke-width="1.1"/><text x="{L + 3}" y="{y0 + 10}" fill="{DIM}" font-size="8.5">RSI 14 · {_f(float(rs[-1]), 1)}</text>')
    for dv in r.get("div", []):
        if dv["i1"] < i0:
            continue
        col = AMB if dv["side"] == "bull" else BEAR
        dash = "" if dv["kind"] == "regular" else ' stroke-dasharray="4 3"'
        s.append(f'<line x1="{X(dv["i1"]):.1f}" x2="{X(dv["i2"]):.1f}" y1="{Y(dv["p1"]):.1f}" y2="{Y(dv["p2"]):.1f}" stroke="{col}" stroke-width="1.6"{dash}/>'
                 f'<line x1="{X(dv["i1"]):.1f}" x2="{X(dv["i2"]):.1f}" y1="{RY(dv["o1"]):.1f}" y2="{RY(dv["o2"]):.1f}" stroke="{col}" stroke-width="1.6"{dash}/>'
                 f'<text x="{X(dv["i2"]) + 3:.1f}" y="{RY(dv["o2"]) + 3:.1f}" fill="{col}" font-size="8">{_t(ar, "div", "دايفرجنس")} {"" if dv["kind"] == "regular" else _t(ar, "hidden", "مخفي")}</text>')
    # MACD histogram
    y1 = y0 + RH + G
    hs = r["hist"][i0:]
    mx = np.nanmax(np.abs(hs)) or 1
    mid = y1 + MH / 2
    s.append(f'<rect x="{L}" y="{y1}" width="{W - L - R}" height="{MH}" fill="{PANEL}"/><line x1="{L}" x2="{W - R}" y1="{mid}" y2="{mid}" stroke="{LINE}"/>')
    for i, v in enumerate(hs):
        if not np.isfinite(v):
            continue
        hh = v / mx * (MH / 2 - 3)
        s.append(f'<rect x="{L + i * cw + cw * 0.15:.1f}" y="{min(mid, mid - hh):.1f}" width="{max(0.6, cw * 0.7):.1f}" height="{abs(hh):.1f}" fill="{AMB if v >= 0 else BEAR}" opacity="0.85"/>')
    s.append(f'<text x="{L + 3}" y="{y1 + 10}" fill="{DIM}" font-size="8.5">MACD 12/26/9</text>')
    tot = y1 + MH + 2
    return f'<svg viewBox="0 0 {W} {tot}" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block">{"".join(s)}</svg>'


# ---------------------------------------------------------------- page
CSS = f"""<style>
*{{box-sizing:border-box}} svg{{direction:ltr}} .v,.big,.mid,td,.btn span,.h span,.h b{{unicode-bidi:plaintext}} body{{margin:0;background:{BG};color:{TXT};font-family:Inter,Segoe UI,Tahoma,Arial,sans-serif}}
.wrap{{padding:14px;max-width:1500px;margin:auto}} .grid{{display:grid;gap:12px}}
.p{{background:{PANEL};border:1px solid {LINE};border-radius:6px;padding:12px;min-width:0}}
.h{{display:flex;justify-content:space-between;align-items:center;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:{DIM};margin-bottom:8px}}
.h b{{color:{AMB};font-weight:700}} .big{{font-size:26px;font-weight:700}} .mid{{font-size:18px;font-weight:700}} .dim{{color:{DIM};font-size:11px}}
.k{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}} .kc .v{{font-size:22px;font-weight:700;margin-top:4px}}
.c2{{grid-template-columns:repeat(2,minmax(0,1fr))}} .c3{{grid-template-columns:repeat(3,minmax(0,1fr))}} .c4{{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media(max-width:900px){{.c2,.c3,.c4{{grid-template-columns:1fr}}}}
.am{{color:{AMB}}} .be{{color:{BEAR}}} .bar{{height:6px;background:{LINE};border-radius:3px;position:relative;margin-top:6px}}
.bar i{{position:absolute;top:-3px;width:3px;height:12px;background:{AMB};border-radius:2px}}
table{{width:100%;border-collapse:collapse;font-size:12px}} td,th{{padding:6px 6px;border-bottom:1px solid {LINE};text-align:center}} th{{color:{DIM};font-weight:600}}
td:first-child,th:first-child{{text-align:start}} .dot{{display:inline-block;width:11px;height:11px;border-radius:50%}}
.chip{{display:inline-block;padding:3px 8px;border-radius:4px;border:1px solid {LINE};font-size:11px;margin:2px}}
.btn{{display:flex;justify-content:space-between;background:{AMB};color:#111;border-radius:4px;padding:8px 10px;font-weight:700;margin-top:6px;font-size:13px}}
.btn.o{{background:transparent;color:{AMB};border:1px solid {AMB}}} .rings{{display:flex;justify-content:space-around;flex-wrap:wrap;gap:6px}}
.rings>div{{text-align:center}} .rs{{font-size:10px;color:{DIM}}} .lg{{display:flex;gap:10px;flex-wrap:wrap;font-size:10px;color:{DIM};margin-top:4px}}
.lg span:before{{content:"";display:inline-block;width:10px;height:3px;margin-inline-end:4px;vertical-align:middle;background:var(--c)}}
</style>"""


def _dot(v):
    col = AMB if v > 0 else BEAR if v < 0 else LINE
    return f'<span class="dot" style="background:{col}"></span>'


def render(b: dict, ar: bool = True) -> str:
    reads, conf, stats = b["reads"], b["conf"], b.get("stats", {})
    dirn = 'dir="rtl"' if ar else ""
    T = lambda en, a: _t(ar, en, a)
    px = b.get("price")
    sc = conf["score"]
    verdict = (T("Accumulate on the discount levels", "تجميع على مستويات الديسكاونت") if sc >= 35 else
               T("Hold / buy dips only", "احتفظ / اشتري على النزول بس") if sc >= 10 else
               T("Take profit / wait (spot never shorts)", "جني ربح / استنى (مفيش بيع على المكشوف)") if sc <= -35 else T("Wait - frames disagree", "استنى - الفريمات مش متفقة"))
    out = [f'<html {dirn}><head><meta charset="utf-8">{CSS}</head><body><div class="wrap grid">']
    # header + KPI cards
    out.append(f'<div class="p" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">'
               f'<div><div class="dim">{esc(b.get("source", ""))}</div><div class="big">{esc(b["symbol"])} <span class="am">{_f(px)}</span></div>'
               f'<div class="dim">{T("Spot analyzer", "محلل السبوت")} · {esc(b.get("asof", ""))}</div></div>'
               f'<div style="display:flex;align-items:center;gap:14px">{ring(sc, 104, T("score", "الدرجة"))}<div class="mid">{esc(verdict)}</div></div></div>')
    kp = [(T("Mayer multiple", "مضاعف ماير"), _f(stats.get("mayer")), T("close / 200-day avg · <0.8 cheap · >2.4 hot", "السعر / متوسط 200 يوم · أقل من 0.8 رخيص · فوق 2.4 سخن")),
          (T("vs 200-week avg", "عن متوسط 200 أسبوع"), (f'{stats["dist_200w"]:+.1f}%' if "dist_200w" in stats else "—"), T(f"{stats.get('sma200w_n', 0)} weeks of data", f"{stats.get('sma200w_n', 0)} أسبوع داتا")),
          (T("From all-time high", "من أعلى سعر تاريخي"), (f'{stats["dd_ath"]:+.1f}%' if "dd_ath" in stats else "—"), _f(stats.get("ath"))),
          (T("1-year return", "عائد سنة"), (f'{stats["ret1y"]:+.1f}%' if "ret1y" in stats else "—"), T("weekly closes", "قفلات أسبوعية")),
          (T("Volatility 30d", "التذبذب 30 يوم"), (f'{stats["vol30"]:.0f}%' if "vol30" in stats else "—"), T("annualised", "سنوي")),
          (T("Daily ADX", "ADX اليومي"), _f((reads.get("1d") or {}).get("adx"), 1), T(">25 trend · <20 range", "فوق 25 ترند · تحت 20 عرضي"))]
    out.append('<div class="k">' + "".join(f'<div class="p kc"><div class="h">{esc(a)}</div><div class="v">{v}</div><div class="dim">{esc(c)}</div></div>' for a, v, c in kp) + "</div>")
    if "hi52" in stats and px:
        pos = (px - stats["lo52"]) / max(1e-12, stats["hi52"] - stats["lo52"])
        out.append(f'<div class="p"><div class="h">{T("52-week range", "مدى 52 أسبوع")}<span>{_f(stats["lo52"])} — {_f(stats["hi52"])}</span></div><div class="bar"><i style="inset-inline-start:{min(100, max(0, pos * 100)):.0f}%"></i></div></div>')
    # charts 2 x 2
    cells = []
    for tf in TFS:
        r = reads.get(tf) or {}
        en, a = TF_NAME[tf]
        if not r.get("ok"):
            cells.append(f'<div class="p"><div class="h">{T(en, a)}</div><div class="dim">{T("no data", "مفيش داتا")}</div></div>')
            continue
        dr = r.get("dr") or {}
        tag = f'{T("trend", "الاتجاه")} {T(r["trend"] or "—", {"up": "صاعد", "down": "هابط"}.get(r["trend"], "—"))} · {T(dr.get("zone", "—"), {"premium": "بريميوم", "discount": "ديسكاونت"}.get(dr.get("zone"), "—"))}'
        cells.append(f'<div class="p"><div class="h"><span><b>{T(en, a)}</b> · {esc(tag)}</span><span class="{"am" if conf["per_tf"].get(tf, 0) >= 0 else "be"}">{conf["per_tf"].get(tf, 0):+d}</span></div>'
                     f'{chart(r, tf, ar)}</div>')
    out.append('<div class="grid c2">' + "".join(cells) + "</div>")
    out.append(f'<div class="lg"><span style="--c:{TXT}">EMA 20</span><span style="--c:{AMB}">EMA 50</span><span style="--c:{BLUE}">EMA 200</span>'
               f'<span style="--c:{AMB}">FVG / OB {T("bull", "صاعد")}</span><span style="--c:{BEAR}">FVG / OB {T("bear", "هابط")}</span><span style="--c:{BLUE}">EQH / EQL</span>'
               f'<span style="--c:#b06cff">Gann Sq9</span><span style="--c:{AMB2}">OTE 62-79%</span></div>')
    # confluence matrix + rings
    smt = b.get("smt", {})
    rows = []
    for key, en, a in FAM:
        tds = []
        for tf in TFS:
            r = reads.get(tf) or {}
            v = smt.get(tf, 0) if key == "smt" else (r.get("votes") or {}).get(key, 0)
            tds.append(f"<td>{_dot(v) if r.get('ok') else '—'}</td>")
        rows.append(f"<tr><td>{T(en, a)}</td>{''.join(tds)}</tr>")
    head = "".join(f"<th>{T(*TF_NAME[tf])}</th>" for tf in TFS)
    rings = "".join(f'<div>{ring(conf["per_tf"].get(tf, 0), 84, T(*TF_NAME[tf]))}</div>' for tf in TFS if tf in conf["per_tf"])
    out.append(f'<div class="grid c2"><div class="p"><div class="h">{T("Confluence matrix", "مصفوفة التوافق")}<b>{T("amber = bull · grey = bear", "أصفر = صاعد · رمادي = هابط")}</b></div>'
               f'<table><tr><th></th>{head}</tr>{"".join(rows)}</table><div class="dim" style="margin-top:6px">'
               f'{T("Weights 1M x3 · 1W x2.5 · 1D x1.5 · 4H x1 (timing). ADX < 20 halves the trend votes.", "الأوزان: شهري ×3 · أسبوعي ×2.5 · يومي ×1.5 · 4 ساعات ×1 (توقيت). ADX تحت 20 بيقسم أصوات الترند على 2.")}</div></div>'
               f'<div class="p"><div class="h">{T("Score by timeframe", "الدرجة لكل فريم")}</div><div class="rings">{rings}</div></div></div>')
    # SMC / ICT, Elliott, Gann cards
    smc_rows = []
    for tf in TFS:
        r = reads.get(tf) or {}
        if not r.get("ok"):
            continue
        ev = r["events"][-1] if r["events"] else None
        dr = r.get("dr")
        fv = [z for z in r["fvg"] if z["side"] == "bull"]
        ob = [z for z in r["obs"] if z["side"] == "bull"]
        smc_rows.append(f"<tr><td>{T(*TF_NAME[tf])}</td><td>{(ev['kind'] + ' ' + ('↑' if ev['dir'] == 'up' else '↓')) if ev else '—'}</td>"
                        f"<td>{_f(ob[-1]['lo']) + '–' + _f(ob[-1]['hi']) if ob else '—'}</td><td>{_f(fv[-1]['lo']) + '–' + _f(fv[-1]['hi']) if fv else '—'}</td>"
                        f"<td>{(f'{dr['pos'] * 100:.0f}%') if dr else '—'}</td></tr>")
    ew_rows, gn_rows = [], []
    for tf in ("1mo", "1w", "1d"):
        r = reads.get(tf) or {}
        if not r.get("ok"):
            continue
        ew = r["elliott"]
        kind = {"impulse_up": T("5-wave impulse up", "دافعة 5 موجات صاعدة"), "impulse_down": T("5-wave impulse down", "دافعة 5 موجات هابطة"),
                "abc": T("ABC correction", "تصحيح ABC")}.get(ew.get("kind"), "—")
        last = ew["labels"][-1][2] if ew.get("labels") else "—"
        tg = ew.get("targets") or {}
        ew_rows.append(f"<tr><td>{T(*TF_NAME[tf])}</td><td>{kind}</td><td>{esc(last)}</td><td>{_f(tg.get('0.618'))}</td><td>{_f(tg.get('1.618'))}</td></tr>")
        g = r["gann"]
        p = g.get("pivot")
        near = sorted(g.get("sq9", []), key=lambda v: abs(v - r["px"]))[:2]
        fit = g.get("fit") or {}
        gn_rows.append(f"<tr><td>{T(*TF_NAME[tf])}</td><td>{_f(p[1]) if p else '—'}</td><td>{' / '.join(_f(v) for v in sorted(near))}</td>"
                       f"<td>{fit.get('tsp', '—')}</td><td>{fit.get('bars_to_turn', '—')}</td></tr>")
    out.append(f'<div class="grid c3">'
               f'<div class="p"><div class="h">SMC / ICT<b>{T("buy-side view", "من ناحية الشراء")}</b></div><table><tr><th></th><th>{T("last break", "آخر كسر")}</th><th>OB</th><th>FVG</th><th>{T("range pos.", "مكان في الرينج")}</th></tr>{"".join(smc_rows)}</table>'
               f'<div class="dim" style="margin-top:6px">{T("Below 50% = discount (where spot buys); above = premium.", "تحت 50% = ديسكاونت (مكان شراء السبوت)؛ فوق = بريميوم.")}</div></div>'
               f'<div class="p"><div class="h">{T("Elliott", "اليوت")}<b>Fibonacci</b></div><table><tr><th></th><th>{T("count", "العد")}</th><th>{T("now", "دلوقتي")}</th><th>0.618</th><th>1.618</th></tr>{"".join(ew_rows)}</table></div>'
               f'<div class="p"><div class="h">{T("Gann", "جان")}<b>Sq9 · {T("time", "زمن")}</b></div><table><tr><th></th><th>{T("pivot", "المحور")}</th><th>{T("nearest levels", "أقرب مستويات")}</th><th>{T("cycle", "الدورة")}</th><th>{T("turn in", "الانعكاس بعد")}</th></tr>{"".join(gn_rows)}</table></div></div>')
    # ratios + SMT
    rat = b.get("ratios", {})
    rc = []
    for name, (vals, note) in rat.items():
        last = vals[-1] if vals else None
        rc.append(f'<div class="p"><div class="h">{esc(name)}<b>{_f(last)}</b></div>{spark(vals[-156:], ref=float(np.median(vals[-156:])) if vals else None)}<div class="dim">{esc(note)}</div></div>')
    smt_txt = b.get("smt_text") or []
    rc.append(f'<div class="p"><div class="h">SMT<b>{esc(b.get("peer", ""))}</b></div>' + ("".join(f'<div class="chip">{esc(x)}</div>' for x in smt_txt) or f'<div class="dim">{T("no divergence now", "مفيش دايفرجنس دلوقتي")}</div>')
              + f'<div class="dim" style="margin-top:6px">{T("Correlated market refuses to confirm the new low / high.", "السوق المرتبط رافض يأكد القاع / القمة الجديدة.")}</div></div>')
    out.append('<div class="grid c4">' + "".join(rc) + "</div>")
    # plan
    pl = b.get("plan") or {}
    if pl.get("ok"):
        buys = "".join(f'<div class="btn"><span>{T("Buy", "شراء")} {i + 1} · {w}%</span><span>{_f(v)}</span></div>' for i, (v, w) in enumerate(zip(pl["buys"], (30, 30, 40))))
        sells = "".join(f'<div class="btn o"><span>T{i + 1}</span><span>{_f(v)}</span></div>' for i, v in enumerate(pl["sells"]))
        out.append(f'<div class="grid c3"><div class="p"><div class="h">{T("Staged buys", "الشراء على دفعات")}</div>{buys}</div>'
                   f'<div class="p"><div class="h">{T("Take profit", "جني الربح")}</div>{sells}</div>'
                   f'<div class="p"><div class="h">{T("Invalidation", "الإلغاء")}</div><div class="big be">{_f(pl.get("invalidation"))}</div>'
                   f'<div class="dim">{T("weekly close below = plan void", "قفلة أسبوعية تحته = الخطة تتلغي")}</div></div></div>')
    out.append(f'<div class="dim">{T("A structured reading of the chart, not a forecast. The combined score is NOT backtested yet (not evidence). Spot = buy only; nothing here places an order.", "قراية منظمة للشارت مش توقع. الدرجة المجمعة لسه ماتعملهاش باك تيست (مش دليل). السبوت شراء بس؛ مفيش أي أمر بيتنفذ.")}</div>')
    out.append("</div></body></html>")
    return "".join(out)


# ---------------------------------------------------------------- data
PEER = {"OIL": ("Y:BZ=F", False), "EURUSD": ("Y:DX-Y.NYB", True), "GBPUSD": ("Y:EURUSD=X", False), "BTC": ("ETH-USDT", False), "GOLD": ("Y:SI=F", False), "SILVER": ("Y:GC=F", False), "PLATINUM": ("Y:GC=F", False),
        "PALLADIUM": ("Y:PL=F", False), "COPPER": ("Y:GC=F", False)}


EXTRA_Y = {"OIL": "Y:CL=F", "BRENT": "Y:BZ=F", "EURUSD": "Y:EURUSD=X", "GBPUSD": "Y:GBPUSD=X", "USDJPY": "Y:JPY=X", "DXY": "Y:DX-Y.NYB",
           "SP500": "Y:^GSPC", "NASDAQ": "Y:^NDX"}   # non-crypto, non-metal markets for the ideas board (Yahoo, delayed)


def load_bundle(asset: str, candles=None) -> dict:
    """Fetch 1M / 1W / 1D / 4H (+ peer for SMT, + ratio series) and analyse. `candles(sym, tf, limit)` injectable for tests."""
    from modules import spot_data, spot_plan
    from modules.smt import smt_signals
    get = candles or spot_data.candles
    a = asset.upper()
    is_metal = a in spot_data.METAL_Y
    extra = EXTRA_Y.get(a)
    sym = spot_data.METAL_Y[a] if is_metal else extra if extra else (a if "-" in a else f"{a}-USDT")
    frames, errs = {}, []
    for tf in TFS:
        try:
            frames[tf] = get(sym, tf, 300)
        except Exception as e:
            errs.append(f"{tf}: {type(e).__name__}")
    reads = {tf: I.analyse(df) for tf, df in frames.items()}
    peer_sym, inv = PEER.get(a, ("BTC-USDT", False))
    smt, smt_text = {}, []
    if peer_sym != sym:
        for tf in ("1w", "1d", "4h"):
            try:
                pdf = get(peer_sym, tf, 300)
                sg = smt_signals(frames[tf], pdf, peer_sym.replace("Y:", "").replace("-USDT", ""), inv)
                if sg:
                    v = 1 if sg[-1]["direction"] == "bullish" else -1
                    smt[tf] = v
                    smt_text.append(f"{TF_NAME[tf][1]}: {sg[-1]['name']}")
            except Exception:
                pass
    conf = I.confluence(reads, smt)
    ratios = {}

    def ratio(n1, n2, label, note, tf="1w"):
        try:
            x, y = get(n1, tf, 300), get(n2, tf, 300)
            m = x[["time", "close"]].merge(y[["time", "close"]], on="time", suffixes=("_a", "_b"))
            if len(m) > 10:
                ratios[label] = ((m["close_a"] / m["close_b"]).tolist(), note)
        except Exception:
            pass
    if extra:
        pass
    elif is_metal:
        ratio("Y:GC=F", "Y:SI=F", "Gold / Silver", "high = silver cheap vs gold")
        ratio("Y:HG=F", "Y:GC=F", "Copper / Gold", "rising = growth / risk-on")
    else:
        ratio("ETH-USDT", "BTC-USDT", "ETH / BTC", "rising = alt season pressure")
        if sym not in ("BTC-USDT", "ETH-USDT"):
            ratio(sym, "BTC-USDT", f"{a} / BTC", "rising = coin beats bitcoin")
    try:
        y = spot_data.yearly(frames["1mo"]) if "1mo" in frames else None
        plan = spot_plan.plan({k: frames.get(k) for k in ("1d", "1w", "1mo")}, y)
    except Exception:
        plan = {}
    d1 = frames.get("1d")
    return {"symbol": a, "sym": sym, "price": float(d1["close"].iloc[-1]) if d1 is not None and len(d1) else None,
            "asof": str(d1["time"].iloc[-1])[:16] if d1 is not None and len(d1) else "", "source": "Yahoo (delayed)" if (is_metal or extra) else "OKX spot",
            "reads": reads, "conf": conf, "stats": I.spot_stats(frames.get("1d"), frames.get("1w"), frames.get("1mo")),
            "smt": smt, "smt_text": smt_text, "peer": peer_sym.replace("Y:", ""), "ratios": ratios, "plan": plan, "errors": errs}


def to_png(html: str, path: str, ctx=None, width: int = 1440) -> str:
    """Screenshot of the dashboard HTML (Telegram photo). ctx = an open Playwright browser context (the bot's), else a
    throw-away headless Chromium is started. The page has no outside requests (pure SVG / CSS)."""
    def _shot(page):
        page.set_viewport_size({"width": width, "height": 1000})
        page.set_content(html, wait_until="load")
        page.wait_for_timeout(300)
        page.screenshot(path=path, full_page=True)
        page.close()
    if ctx is not None:
        _shot(ctx.new_page())
        return path
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        _shot(b.new_page())
        b.close()
    return path
