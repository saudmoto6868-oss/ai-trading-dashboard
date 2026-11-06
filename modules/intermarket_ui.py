"""Radar views for the intermarket board: a banner (always on top of the Radar) and the SMT pairs board (two mini charts per event). Pure HTML / SVG, no network."""
from __future__ import annotations

import html


def _norm(vals, w, h, pad=4):
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    n = len(vals)
    return [(pad + (w - 2 * pad) * i / max(1, n - 1), pad + (h - 2 * pad) * (1 - (v - lo) / span)) for i, v in enumerate(vals)]


def leg_svg(vals, color, mark_idx, name, w=250, h=96):
    """One market's last candles as a line in its own colour, a dashed line at the swing the divergence is about, and the name."""
    if not vals or len(vals) < 5:
        return ""
    pts = _norm(vals, w, h)
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    mi = min(max(0, mark_idx), len(pts) - 1)
    mx, my = pts[mi]
    return (f"<svg width='{w}' height='{h}' viewBox='0 0 {w} {h}' style='background:#0f1317;border:1px solid #2b3139;border-radius:6px'>"
            f"<polyline fill='none' stroke='{html.escape(color)}' stroke-width='1.6' points='{poly}'/>"
            f"<line x1='{mx:.1f}' y1='0' x2='{mx:.1f}' y2='{h}' stroke='#8a94a3' stroke-dasharray='3,3' stroke-width='1'/>"
            f"<circle cx='{mx:.1f}' cy='{my:.1f}' r='3.5' fill='{html.escape(color)}'/>"
            f"<text x='6' y='13' fill='{html.escape(color)}' font-size='11' font-family='sans-serif' font-weight='700'>{html.escape(name)}</text></svg>")


def event_card(e, ar=False):
    up = e["direction"] == "bullish"
    col = "#0ecb81" if up else "#f6465d"
    mark = len(e["series_a"]) - 1 - int(e["bars_ago"])
    title = f"SMT {'▲' if up else '▼'}  {e['a_name']} / {e['b_name']}  ·  {e['tf'].upper()}  ·  {e['session']}  ·  {e['bars_ago']} {'شمعة' if ar else 'bars ago'}"
    b_name = e["b_name"] + (" (inverse)" if e.get("inverse") else "")
    return (f"<div style='border:1px solid {col};border-radius:8px;padding:8px 10px;margin:0 0 10px;background:#161a1e'>"
            f"<div style='font-weight:700;color:{col};margin-bottom:6px'>{html.escape(title)}</div>"
            f"<div style='display:flex;gap:8px;flex-wrap:wrap'>{leg_svg(e['series_a'], e['a_color'], mark, e['a_name'])}{leg_svg(e['series_b'], e['b_color'], mark, b_name)}</div>"
            f"<div style='color:#a3adba;font-size:12px;margin-top:6px'>{html.escape(e['text_ar' if ar else 'text_en'])}</div></div>")


def banner_html(events, ar=False, limit=8):
    """One line for the top of the Radar: what is diverging right now (or that nothing is)."""
    if not events:
        msg = "مفيش SMT واضح دلوقتي بين الأزواج المرتبطة" if ar else "No clear SMT between the correlated pairs right now"
        return f"<div style='font-size:12px;color:#848e9c;background:#161a1e;border:1px solid #2b3139;border-radius:6px;padding:4px 10px;margin:0 0 6px'>SMT: {msg}</div>"
    chips = []
    for e in events[:limit]:
        up = e["direction"] == "bullish"
        col = "#0ecb81" if up else "#f6465d"
        chips.append(f"<span title='{html.escape(e['text_ar' if ar else 'text_en'], quote=True)}' style='border:1px solid {col};border-radius:12px;padding:1px 8px;margin-inline-end:6px;white-space:nowrap'>"
                     f"<b style='color:{col}'>{'▲' if up else '▼'}</b> <b style='color:{html.escape(e['a_color'])}'>{html.escape(e['a_name'])}</b>/<b style='color:{html.escape(e['b_color'])}'>{html.escape(e['b_name'])}</b> "
                     f"<span style='color:#a3adba'>{html.escape(e['tf'].upper())} · {html.escape(e['session'])} · {e['bars_ago']}</span></span>")
    head = f"SMT ({len(events)})" if not ar else f"SMT ({len(events)})"
    return (f"<div style='font-size:12px;background:#161a1e;border:1px solid #2b3139;border-radius:6px;padding:4px 10px;margin:0 0 6px;overflow-x:auto;white-space:nowrap'>"
            f"<b style='color:#ffd54f;margin-inline-end:8px'>{head}</b>{''.join(chips)}</div>")
