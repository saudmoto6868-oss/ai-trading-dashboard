"""Shared look for the Radar and Technical Office (owner 2026-10-23, taking IDEAS from his reference images, not a copied theme: KPI cards
with an icon badge and a ring, donuts, half-circle gauges, glowing bars, status legends). Pure HTML / SVG strings so they can be tested without Streamlit.
Colour semantics (kept from the desk conventions): green / red = direction only, amber = warning or stale, accent = the theme colour for flags."""
from __future__ import annotations

import html
import math

TOKENS = {"bg": "#12161b", "panel": "#1a2027", "panel2": "#212832", "line": "#323b47", "text": "#eaecef", "dim": "#8d97a5", "accent": "#f0b90b", "accent2": "#2dd4bf"}   # the site's own dark palette (amber accent), no copied theme
UP, DOWN, WARN = "#0ecb81", "#f6465d", "#f0b90b"
_TONE = {"up": UP, "down": DOWN, "warn": WARN, "": None}


def css(tokens: dict | None = None, rad: int = 14) -> str:
    """Stylesheet for the cards. tokens / rad come from the active dashboard theme (main._kit_theme) so every page follows the Theme menu."""
    t = {**TOKENS, **(tokens or {})}
    return f"""<style>
:root{{--uk-bg:{t['bg']};--uk-panel:{t['panel']};--uk-panel2:{t['panel2']};--uk-line:{t['line']};--uk-text:{t['text']};--uk-dim:{t['dim']};--uk-acc:{t['accent']};--uk-acc2:{t['accent2']}}}
.uk-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:4px 0 8px}}
.uk-card{{position:relative;background:linear-gradient(160deg,var(--uk-panel2),var(--uk-panel));border:1px solid var(--uk-line);border-radius:{rad}px;padding:9px 11px;
 box-shadow:0 4px 14px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.04);color:var(--uk-text);min-height:64px;overflow:hidden}}
.uk-card .uk-lbl{{font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--uk-dim);display:flex;align-items:center;gap:6px}}
.uk-ic{{display:inline-flex;width:20px;height:20px;border-radius:7px;align-items:center;justify-content:center;font-size:12px;background:rgba(255,255,255,.07);border:1px solid var(--uk-line)}}
.uk-card .uk-val{{font:700 22px/1.15 ui-monospace,Menlo,Consolas,monospace;margin-top:3px}}
.uk-card .uk-sub{{font-size:10.5px;color:var(--uk-dim);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.uk-card .uk-ring{{position:absolute;inset-inline-end:8px;bottom:6px;width:40px;height:40px;opacity:.95}}.uk-card.has-ring .uk-sub{{padding-inline-end:46px}}
.uk-card.up{{box-shadow:0 0 0 1px {UP}55,0 0 16px {UP}33}}.uk-card.down{{box-shadow:0 0 0 1px {DOWN}55,0 0 16px {DOWN}33}}.uk-card.warn{{box-shadow:0 0 0 1px {WARN}55,0 0 16px {WARN}2a}}
.uk-panel{{background:linear-gradient(160deg,var(--uk-panel2),var(--uk-panel));border:1px solid var(--uk-line);border-radius:{rad}px;padding:10px 12px;color:var(--uk-text);margin:4px 0 8px}}
.uk-panel h4{{margin:0 0 6px;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--uk-dim);font-weight:600}}
.uk-flex{{display:flex;gap:14px;align-items:center;flex-wrap:wrap}}
.uk-leg{{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:11px;color:var(--uk-dim)}}.uk-leg i{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}}
.uk-chipbar{{display:flex;flex-wrap:wrap;gap:4px}}.uk-chip{{font-size:10.5px;padding:1px 7px;border-radius:999px;border:1px solid var(--uk-line);background:rgba(255,255,255,.04);color:var(--uk-text)}}
.xr-card{{background:linear-gradient(160deg,var(--uk-panel2),var(--uk-panel));border:1px solid var(--uk-line);border-radius:{max(0, rad - 2)}px;padding:6px 7px 4px;margin-bottom:6px}}
.xr-card.conf{{box-shadow:0 0 0 1px {UP}66,0 0 14px {UP}33}}.xr-card.cand{{box-shadow:0 0 0 1px {WARN}55}}
</style>"""


def _c(tone: str, default: str = "var(--uk-text)") -> str:
    return _TONE.get(tone) or default


def ring(pct: float, color: str = "var(--uk-acc)", size: int = 46, w: int = 5) -> str:
    """Donut ring showing pct (0-100) of one value."""
    pct = max(0.0, min(100.0, float(pct)))
    r = (size - w) / 2; c = 2 * math.pi * r; on = c * pct / 100
    return (f"<svg class='uk-ring' viewBox='0 0 {size} {size}' width='{size}' height='{size}'><circle cx='{size/2}' cy='{size/2}' r='{r:.1f}' fill='none' stroke='rgba(255,255,255,.1)' stroke-width='{w}'/>"
            f"<circle cx='{size/2}' cy='{size/2}' r='{r:.1f}' fill='none' stroke='{color}' stroke-width='{w}' stroke-linecap='round' stroke-dasharray='{on:.1f} {c:.1f}' "
            f"transform='rotate(-90 {size/2} {size/2})'/></svg>")


def kpi(icon: str, label: str, value, sub: str = "", tone: str = "", pct: float | None = None, title: str = "") -> str:
    """One KPI card: icon badge, label, big value, small line, optional ring (pct) and a glow when tone is up / down / warn."""
    rg = ring(pct, _c(tone, "var(--uk-acc)")) if pct is not None else ""
    return (f"<div class='uk-card {tone}{' has-ring' if pct is not None else ''}' title='{html.escape(title, quote=True)}'><div class='uk-lbl'><span class='uk-ic'>{icon}</span>{html.escape(str(label))}</div>"
            f"<div class='uk-val' style='color:{_c(tone)}'>{html.escape(str(value))}</div><div class='uk-sub'>{html.escape(str(sub))}</div>{rg}</div>")


def row(cards: list) -> str:
    return "<div class='uk-row'>" + "".join(cards) + "</div>"


def donut(parts: list, center: str = "", size: int = 92) -> str:
    """parts = [(label, value, colour)] -> donut with the centre text and a legend."""
    tot = sum(max(0.0, v) for _l, v, _c2 in parts) or 1.0
    r, w = size / 2 - 8, 11; circ = 2 * math.pi * r; off = 0.0; segs = []
    for _l, v, col in parts:
        ln = circ * max(0.0, v) / tot
        segs.append(f"<circle cx='{size/2}' cy='{size/2}' r='{r:.1f}' fill='none' stroke='{col}' stroke-width='{w}' stroke-dasharray='{ln:.1f} {circ:.1f}' stroke-dashoffset='{-off:.1f}' transform='rotate(-90 {size/2} {size/2})'/>")
        off += ln
    leg = "".join(f"<span><i style='background:{col}'></i>{html.escape(str(l))} {int(v)}</span>" for l, v, col in parts)
    return (f"<div class='uk-flex'><svg viewBox='0 0 {size} {size}' width='{size}' height='{size}'><circle cx='{size/2}' cy='{size/2}' r='{r:.1f}' fill='none' stroke='rgba(255,255,255,.07)' stroke-width='{w}'/>"
            f"{''.join(segs)}<text x='50%' y='54%' text-anchor='middle' fill='var(--uk-text)' font-size='15' font-weight='700' font-family='ui-monospace,monospace'>{html.escape(center)}</text></svg>"
            f"<div class='uk-leg' style='flex-direction:column'>{leg}</div></div>")


def gauge(pct: float, label: str = "", lo: str = "0", hi: str = "100", color: str = "var(--uk-acc)", w: int = 150) -> str:
    """Half-circle gauge for a value 0-100 (e.g. share of symbols in an up-trend)."""
    pct = max(0.0, min(100.0, float(pct))); r = 56; cx, cy = 70, 66; L = math.pi * r
    return (f"<svg viewBox='0 0 140 84' width='{w}'><path d='M{cx-r} {cy} A{r} {r} 0 0 1 {cx+r} {cy}' fill='none' stroke='rgba(255,255,255,.1)' stroke-width='10' stroke-linecap='round'/>"
            f"<path d='M{cx-r} {cy} A{r} {r} 0 0 1 {cx+r} {cy}' fill='none' stroke='{color}' stroke-width='10' stroke-linecap='round' stroke-dasharray='{L*pct/100:.1f} {L:.1f}'/>"
            f"<text x='{cx}' y='{cy-10}' text-anchor='middle' fill='var(--uk-text)' font-size='20' font-weight='700' font-family='ui-monospace,monospace'>{pct:.0f}%</text>"
            f"<text x='{cx}' y='{cy+8}' text-anchor='middle' fill='var(--uk-dim)' font-size='9'>{html.escape(label)}</text>"
            f"<text x='{cx-r}' y='{cy+16}' text-anchor='middle' fill='var(--uk-dim)' font-size='8'>{html.escape(lo)}</text><text x='{cx+r}' y='{cy+16}' text-anchor='middle' fill='var(--uk-dim)' font-size='8'>{html.escape(hi)}</text></svg>")


def bars(items: list, color: str = "var(--uk-acc)", h: int = 74, bw: int = 24) -> str:
    """Glowing vertical bars: items = [(label, value)]."""
    if not items:
        return ""
    mx = max(v for _l, v in items) or 1; gap = 6; wd = len(items) * (bw + gap)
    out = []
    for i, (l, v) in enumerate(items):
        bh = max(2.0, (h - 14) * v / mx); x = i * (bw + gap)
        out.append(f"<rect x='{x}' y='{h-14-bh:.1f}' width='{bw}' height='{bh:.1f}' rx='4' fill='{color}' opacity='.85' style='filter:drop-shadow(0 0 4px {color})'><title>{html.escape(str(l))}: {v}</title></rect>"
                   f"<text x='{x+bw/2}' y='{h-2}' text-anchor='middle' font-size='11'>{html.escape(str(l))}</text>"
                   f"<text x='{x+bw/2}' y='{h-17-bh:.1f}' text-anchor='middle' fill='var(--uk-text)' font-size='8'>{v}</text>")
    return f"<svg viewBox='0 0 {wd} {h}' width='{min(wd, 760)}' height='{h}'>{''.join(out)}</svg>"


def panel(title: str, body: str) -> str:
    return f"<div class='uk-panel'><h4>{html.escape(title)}</h4>{body}</div>"


def legend(items: list) -> str:
    """items = [(label, colour)]."""
    return "<div class='uk-leg'>" + "".join(f"<span><i style='background:{c}'></i>{html.escape(l)}</span>" for l, c in items) + "</div>"
