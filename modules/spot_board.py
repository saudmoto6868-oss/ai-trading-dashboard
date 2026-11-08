"""Spot ideas board (owner 2026-11-06): the ideas desk drawn in the style of the owner's reference picture - charcoal panels,
amber accent, rings, KPI tiles, one card per market, one card per idea with its own chart, the thinking log and the news.
Pure SVG / CSS (no chart library). render(desk_result) -> HTML for st.components.v1.html (and the Telegram image)."""
from __future__ import annotations

import html as _h
import math
from datetime import datetime, timezone

import numpy as np

from modules.spot_dash import AMB, AMB2, BEAR, BG, CSS, DIM, LINE, PANEL, TXT, ring, spark

RED = "#e05a5a"


def esc(s) -> str:
    return _h.escape(str(s))


def _f(x):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    ax = abs(x)
    return f"{x:,.0f}" if ax >= 1000 else f"{x:,.2f}" if ax >= 1 else f"{x:.4f}"


def idea_chart(closes, idea, W=520, H=170) -> str:
    """Weekly closes (last 52) + entry band, stop, targets."""
    v = np.asarray([x for x in closes if x is not None and math.isfinite(x)], float)
    if len(v) < 5:
        return ""
    levels = [x for x in ([idea.get("stop")] + list(idea.get("targets") or []) + list(idea.get("entry") or [])) if x]
    lo, hi = min(v.min(), *levels) if levels else v.min(), max(v.max(), *levels) if levels else v.max()
    pad = (hi - lo) * 0.08 or 1
    lo, hi = lo - pad, hi + pad
    X = lambda i: 4 + i * (W - 70) / (len(v) - 1)
    Y = lambda p: 6 + (hi - p) / (hi - lo) * (H - 12)
    s = []
    if idea.get("entry"):
        a, b = idea["entry"]
        s.append(f'<rect x="4" y="{Y(b):.1f}" width="{W - 70}" height="{max(2, Y(a) - Y(b)):.1f}" fill="{AMB}" opacity="0.18"/>'
                 f'<text x="{W - 62}" y="{(Y(a) + Y(b)) / 2 + 3:.1f}" fill="{AMB}" font-size="10" font-weight="700">{"دخول"} {_f((a + b) / 2)}</text>')
    if idea.get("stop"):
        y = Y(idea["stop"])
        s.append(f'<line x1="4" x2="{W - 70}" y1="{y:.1f}" y2="{y:.1f}" stroke="{RED}" stroke-width="1.4"/><text x="{W - 62}" y="{y + 3:.1f}" fill="{RED}" font-size="10">{"وقف"} {_f(idea["stop"])}</text>')
    for k, t in enumerate(idea.get("targets") or []):
        y = Y(t)
        s.append(f'<line x1="4" x2="{W - 70}" y1="{y:.1f}" y2="{y:.1f}" stroke="{AMB2}" stroke-dasharray="5 4"/><text x="{W - 62}" y="{y + 3:.1f}" fill="{AMB2}" font-size="10">T{k + 1} {_f(t)}</text>')
    pts = " ".join(f"{X(i):.1f},{Y(p):.1f}" for i, p in enumerate(v))
    s.append(f'<polygon points="4,{H - 4} {pts} {X(len(v) - 1):.1f},{H - 4}" fill="{AMB}" opacity="0.06"/><polyline points="{pts}" fill="none" stroke="{TXT}" stroke-width="1.5"/>')
    s.append(f'<circle cx="{X(len(v) - 1):.1f}" cy="{Y(v[-1]):.1f}" r="3.5" fill="{AMB}"/>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" style="display:block;direction:ltr">{"".join(s)}</svg>'


def _ladder(idea):
    a, b = idea["entry"]
    lv = [b, (a + b) / 2, a]
    return "".join(f'<div class="btn"><span>{"شراء"} {i + 1} · {w}%</span><span dir="ltr">{_f(p)}</span></div>' for i, (p, w) in enumerate(zip(lv, (30, 30, 40))))


def render(r: dict) -> str:
    ideas, markets = r["ideas"], r["markets"]
    buy = [i for i in ideas if i["kind"] != "avoid"]
    avoid = [i for i in ideas if i["kind"] == "avoid"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [f'<html dir="rtl"><head><meta charset="utf-8">{CSS}<style>.chips span{{display:inline-block;border:1px solid {AMB};color:{AMB};border-radius:12px;padding:2px 8px;margin:2px;font-size:11px}}'
           f'.chips span.x{{border-color:{RED};color:{RED}}} .log{{font-family:Consolas,monospace;font-size:12px;line-height:1.7;color:{TXT};white-space:pre-wrap}}'
           f'details summary{{cursor:pointer;color:{AMB};font-weight:700;margin:6px 0}} .nw{{font-size:12px;padding:4px 0;border-bottom:1px solid {LINE}}}</style></head><body><div class="wrap grid">']
    best = max((i["rr"] or 0 for i in buy), default=0)
    disc = sum(1 for m in markets if m["zone"] == "discount")
    risk = r.get("risk_off", 0)
    out.append(f'<div class="p" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">'
               f'<div><div class="dim">{now} · {len(markets)} سوق · {len(r.get("news", []))} خبر مؤثر</div><div class="big">مكتب أفكار السبوت <span class="am">اليومي</span></div>'
               f'<div class="dim">فريمات كبيرة · SMC · ICT · اليوت · جان · كلاسيك · نماذج · اختراق · أخبار</div></div>'
               f'{ring(min(100, 20 * len(buy)), 100, "أفكار")}</div>')
    kp = [("أفكار شراء النهارده", str(len(buy)), "كل واحدة شروطها اتحققت"), ("أحسن عائد/مخاطرة", f"{best:.1f}R" if best else "—", "الهدف الأول ÷ الوقف"),
          ("أسواق في الديسكاونت", f"{disc} / {len(markets)}", "تحت 50% من رينجها الأسبوعي"),
          ("مزاج الأخبار", "خوف (ملاذ آمن)" if risk > 0 else "شهية مخاطرة" if risk < 0 else "محايد", "من عناوين الأخبار بالكلمات"),
          ("تجنّب / جني ربح", str(len(avoid)), "أسواق غالية دلوقتي")]
    out.append('<div class="k">' + "".join(f'<div class="p kc"><div class="h">{esc(a)}</div><div class="v">{esc(v)}</div><div class="dim">{esc(c)}</div></div>' for a, v, c in kp) + "</div>")
    # market map
    cards = []
    for m in markets:
        col = AMB if m["wk"] >= 0 else BEAR
        arrow = "▲" if m["news"] > 0 else "▼" if m["news"] < 0 else "•"
        cards.append(f'<div class="p"><div class="h"><b>{esc(m["name"])}</b><span>{esc(m["asset"])}</span></div>'
                     f'<div style="display:flex;justify-content:space-between;align-items:center"><div><div class="mid" dir="ltr">{_f(m["price"])}</div>'
                     f'<div style="color:{col};font-size:12px" dir="ltr">{m["wk"]:+.2f}% أسبوع</div>'
                     f'<div class="dim">{"ديسكاونت" if m["zone"] == "discount" else "بريميوم" if m["zone"] == "premium" else "—"} · أخبار {arrow} · {m["n_ideas"]} فكرة</div></div>'
                     f'{ring(m["score"], 70, "درجة")}</div>{spark(m["spark"], h=46)}</div>')
    out.append('<div class="grid c4">' + "".join(cards) + "</div>")
    # idea cards
    ic = []
    for i in buy[:8]:
        chips = "".join(f"<span>{esc(s)}</span>" for s in i["schools"]) + "".join(f'<span class="x">{esc(s)}</span>' for s in i.get("against", []))
        kp = "".join(f"<tr><td>{esc(k)}</td><td dir='ltr'>{esc(v)}</td></tr>" for k, v in i["kpis"].items())
        nws = "".join(f'<div class="nw">{"🟢" if x["push"].get(i["asset"], 0) > 0 else "🔴" if x["push"].get(i["asset"], 0) < 0 else "⚪"} {esc(x["title"][:110])}'
                      f'<div class="dim">{esc(" · ".join(x["why"][:1]))}</div></div>' for x in i["news"]["items"][:2])
        tgs = "".join(f'<div class="btn o"><span>T{k + 1} · <span dir="ltr">{(t / i["price"] - 1) * 100:+.1f}%</span></span><span dir="ltr">{_f(t)}</span></div>' for k, t in enumerate(i["targets"]))
        ic.append(f'<div class="p"><div class="h"><span><b>{esc(i["name"])}</b> · {esc(i["title"])}</span><span class="am">{i["rr"]:.1f}R</span></div>'
                  f'<div style="display:flex;gap:10px;align-items:flex-start"><div style="flex:1;min-width:0">{idea_chart(next((m["spark"] for m in markets if m["asset"] == i["asset"]), []), i)}</div>'
                  f'<div>{ring(min(100, i["conf"] * 15), 78, "توافق")}</div></div>'
                  f'<div class="chips" style="margin:6px 0">{chips}</div>'
                  f'<div style="font-size:13px;line-height:1.7"><b class="am">ليه:</b> {esc(i["why"])}.<br><b class="am">السيناريو الأساسي:</b> شراء على 3 دفعات في المنطقة، '
                  f'الوقف تحت {_f(i["stop"])} (قفلة أسبوعية)، الأهداف بالترتيب. المدة: {esc(i["horizon"])}.<br><b class="be">البديل:</b> {esc(i["alt"])}</div>'
                  f'<div class="grid c3" style="margin-top:8px"><div>{_ladder(i)}</div><div>{tgs}</div>'
                  f'<div><table>{kp}</table></div></div>{nws}</div>')
    if ic:
        out.append(f'<div class="h" style="margin-top:6px"><b>أفكار الشراء</b><span>مترتبة بالتوافق ثم العائد/المخاطرة</span></div><div class="grid c2">' + "".join(ic) + "</div>")
    else:
        out.append('<div class="p"><div class="mid">مفيش فكرة شراء النهارده</div><div class="dim">ولا وصفة شروطها اتحققت بعائد 1.5R على الأقل - الاستنى قرار.</div></div>')
    if avoid:
        out.append('<div class="grid c4">' + "".join(f'<div class="p"><div class="h"><b>{esc(i["name"])}</b><span class="be">تجنّب</span></div><div style="font-size:13px">{esc(i["why"])}</div>'
                                                      f'<div class="dim" style="margin-top:6px">{esc(i["alt"])}</div></div>' for i in avoid) + "</div>")
    # thinking + news
    log_html, cur = [], None
    for line in r["log"]:
        if not line.startswith("  "):
            if cur is not None:
                log_html.append("</div></details>")
            log_html.append(f'<details{" open" if not cur else ""}><summary>{esc(line[:60])}</summary><div class="log">{esc(line)}\n')
            cur = line
        else:
            log_html.append(esc(line) + "\n")
    if cur is not None:
        log_html.append("</div></details>")
    news = "".join(f'<div class="nw">{esc(x["title"][:120])}<div class="dim">{esc(" · ".join(x["why"][:2]) or "ذكر السوق")} → '
                   + " ".join(f'{a} {"▲" if v > 0 else "▼"}' for a, v in x["push"].items()) + "</div></div>" for x in r.get("news", [])[:10])
    out.append(f'<div class="grid c2"><div class="p"><div class="h"><b>طريقة التفكير</b><span>بص على إيه ورفض إيه ولية</span></div>{"".join(log_html)}</div>'
               f'<div class="p"><div class="h"><b>الأخبار اللي ممكن تحرك السوق</b><span>قواعد كلمات مش تحليل</span></div>{news or "<div class=dim>مفيش أخبار متاحة دلوقتي</div>"}</div></div>')
    out.append('<div class="dim">الوصفات دي قواعد من المدارس ولسه ماتعملهاش باك تيست (اختبار الدرجة المجمعة 2026-11-06 ماطلعش ميزة). كمية صغيرة، والوقف قفلة أسبوعية. '
               'السبوت شراء بس، ومفيش أي أمر بيتنفذ.</div></div></body></html>')
    return "".join(out)
