"""Radar > Day plan: HTML for the cards and the session timeline (pure, no network)."""
from __future__ import annotations

import html

from modules.day_plan import CHAIN, KILL_ZONES, SESSIONS, session_label


def _hm(m):
    m %= 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def timeline_html(clock, ar=False) -> str:
    sess = " · ".join(f"<b>{n}</b> {_hm(a)}-{_hm(b)}" for n, (a, b) in SESSIONS.items())
    kz = " · ".join(f"{n} {_hm(a)}-{_hm(b)}" for n, (a, b) in KILL_ZONES.items())
    now = f"<b style='color:#f0b90b'>{html.escape(session_label(clock, ar))}</b> · NY {clock['ny_time']}"
    return (f"<div style='font-size:12px;background:#161a1e;border:1px solid #2b3139;border-radius:6px;padding:6px 10px;margin:0 0 8px;color:#a3adba'>"
            f"{now}<br><span style='font-size:11px'>{'جلسات' if ar else 'Sessions'} (NY): {sess}<br>Kill zones: {kz}</span></div>")


def card_html(p, ar=False) -> str:
    up = p["direction"] == "bullish"
    col = "#0ecb81" if up else "#f6465d"
    cf = p["confluence"]
    chips = "".join(
        f"<span style='display:inline-block;margin:0 4px 2px 0;padding:0 6px;border-radius:10px;border:1px solid "
        f"{'#0ecb81' if cf['views'].get(t) == 'bullish' else '#f6465d' if cf['views'].get(t) == 'bearish' else '#2b3139'};font-size:11px;color:"
        f"{'#0ecb81' if cf['views'].get(t) == 'bullish' else '#f6465d' if cf['views'].get(t) == 'bearish' else '#6b7684'}'>{t.upper()} "
        f"{'▲' if cf['views'].get(t) == 'bullish' else '▼' if cf['views'].get(t) == 'bearish' else '·'}</span>" for t in CHAIN)
    tps = " / ".join(str(x) for x in p["tps"])
    pt = "نقطة" if ar else "pts"
    why = "".join(f"<li>{html.escape(str(r))}</li>" for r in p["reasons"][:4])
    sch = " · ".join(html.escape(x) for x in p["schools"][:5])
    ex = html.escape(p["exit"]["text_ar" if ar else "text_en"])
    mode = "Confluence" if p["mode"] == "conf" else "Scalp"
    return (f"<div style='border:1px solid {col};border-radius:8px;padding:8px 10px;margin:0 0 10px;background:#161a1e'>"
            f"<div style='font-weight:700;color:{col}'>{'▲ BUY' if up else '▼ SELL'} {html.escape(p['symbol'])} · {p['tf'].upper()} · {mode} · "
            f"{cf['n']}/{cf['of']} {'فريمات' if ar else 'timeframes'} · {'★' * int(p['stars'])}</div>"
            f"<div style='margin:4px 0'>{chips}</div>"
            f"<div style='font-size:13px'>{'دخول' if ar else 'Entry'} <b>{p['entry']}</b> · {'وقف' if ar else 'Stop'} <b style='color:#f6465d'>{p['stop']}</b> ({p['risk_points']} {pt}) · "
            f"{'أهداف' if ar else 'Targets'} <b style='color:#0ecb81'>{tps}</b></div>"
            f"<div style='font-size:12px;color:#a3adba'>{'حركة محتملة' if ar else 'Possible move'} <b>{p['move_points']}</b> {pt} · R:R 1:{p['rr1']} · {sch}</div>"
            f"<ul style='margin:4px 0 4px 18px;padding:0;font-size:12px;color:#c3c9d1'>{why}</ul>"
            f"<div style='font-size:12px;color:#848e9c'>{'الخروج' if ar else 'Exit'}: {ex}</div></div>")
