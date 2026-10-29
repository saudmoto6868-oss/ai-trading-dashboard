"""HUB PRESENTATION: one look for every Research Hub tab, built on the app's own card kit (modules/ui_kit.py) so the tabs follow
the Theme menu like Radar and Technical Office do. Pure HTML / SVG strings (testable without Streamlit).

Each tab keeps its own identity (accent colour + glyph, kept in TABS below and checked against the tab's SPEC by a test); the shared
parts are the header, KPI cards, a t-statistic ruler, the consensus graph and the Command Center overview + data-flow diagram.
The overview reads the tabs' PUBLISHED snapshots only (hub_core.read), never their code: the hub rule stays intact."""
from __future__ import annotations

import html
import math

from modules import hub_core, ui_kit

THEME = {"tokens": {}, "rad": 14}

# id, title, glyph, accent, consumes. Must match each tab's SPEC (tests/test_hub_ui.py).
TABS = (
    ("overview", "Command Center", "◈", "#B8BCC6", ()),
    ("truth", "Truth Court", "§", "#E0A526", ()),
    ("plateau", "Plateau Lab", "▦", "#4C8DFF", ("truth", "regime")),
    ("regime", "Regime Radar", "◉", "#2FBF71", ()),
    ("trail", "Decision Trail", "⟡", "#9B6BFF", ("truth",)),
    ("decay", "Decay Watch", "↘", "#E5484D", ("trail", "truth")),
    ("consensus", "Consensus Map", "✦", "#18B6C9", ("truth",)),
    ("funnel", "Kill Funnel", "▼", "#F76808", ("truth",)),
)
BY_ID = {t[0]: t for t in TABS}
UP, DOWN, WARN = ui_kit.UP, ui_kit.DOWN, ui_kit.WARN


def set_theme(tokens: dict | None, rad: int | None = 14) -> None:
    """Called by main.py with the active dashboard theme so hub tabs follow the Theme menu."""
    THEME["tokens"], THEME["rad"] = dict(tokens or {}), int(rad if rad is not None else 14)


def css() -> str:
    return ui_kit.css(THEME["tokens"], THEME["rad"])


def show(st, body: str) -> None:
    st.markdown(css() + body, unsafe_allow_html=True)


def header(spec, purpose: str, title: str | None = None) -> str:
    """Identity strip: accent bar, glyph, title, what it does, and which tabs it reads."""
    acc = html.escape(spec.accent)
    reads = "".join(f"<span class='uk-chip'>{html.escape(BY_ID[c][2])} {html.escape(BY_ID[c][1])}</span>" for c in spec.consumes if c in BY_ID)
    reads = f"<div class='uk-chipbar' style='margin-top:6px'><span class='uk-chip' style='border-style:dashed'>reads</span>{reads}</div>" if reads else ""
    return (f"<div class='uk-panel' style='border-inline-start:4px solid {acc};box-shadow:0 0 18px {acc}22'>"
            f"<div style='display:flex;align-items:center;gap:10px'><span class='uk-ic' style='width:30px;height:30px;font-size:18px;color:{acc};border-color:{acc}66'>{html.escape(spec.glyph)}</span>"
            f"<div><div style='font-weight:700;font-size:16px'>{html.escape(title or spec.title)}</div>"
            f"<div style='font-size:12px;color:var(--uk-dim)'>{html.escape(purpose)}</div></div></div>{reads}</div>")


def cards(items: list) -> str:
    """items = (icon, label, value, sub, tone, pct) -> a row of KPI cards."""
    out = []
    for it in items:
        icon, label, value, sub, tone, pct = (list(it) + ["", "", "", "", "", None])[:6] if len(it) < 6 else it
        out.append(ui_kit.kpi(icon, label, value, sub, tone, pct))
    return ui_kit.row(out)


def tone_for(ok: bool | None) -> str:
    return "" if ok is None else "up" if ok else "warn"


def ruler(points: list, lo: float = 0.0, hi: float | None = None, w: int = 620, title: str = "") -> str:
    """Horizontal number line with labelled markers: points = [(label, value, colour)]. Used for t-levels: luck, hurdle, Bonferroni, best rule."""
    pts = [(l, float(v), c) for l, v, c in points if v is not None]
    if not pts:
        return ""
    hi = hi if hi is not None else max(v for _l, v, _c in pts) * 1.15 or 1.0
    pad, y = 24, 58
    x = lambda v: pad + (w - 2 * pad) * (min(max(v, lo), hi) - lo) / (hi - lo or 1.0)
    out = [f"<line x1='{pad}' y1='{y}' x2='{w - pad}' y2='{y}' stroke='var(--uk-line)' stroke-width='4' stroke-linecap='round'/>"]
    for t in range(int(math.ceil(lo)), int(hi) + 1):
        out.append(f"<line x1='{x(t):.1f}' y1='{y - 5}' x2='{x(t):.1f}' y2='{y + 5}' stroke='var(--uk-dim)'/><text x='{x(t):.1f}' y='{y + 20}' text-anchor='middle' font-size='9' fill='var(--uk-dim)'>{t}</text>")
    for i, (l, v, c) in enumerate(sorted(pts, key=lambda p: p[1])):
        ty = (y - 14, y - 30, y + 36)[i % 3]   # three label lanes so close values (3.00 / 3.13 / 3.24) do not overprint
        out.append(f"<circle cx='{x(v):.1f}' cy='{y}' r='6' fill='{html.escape(c)}'/><text x='{x(v):.1f}' y='{ty}' text-anchor='middle' font-size='10' fill='{html.escape(c)}'>"
                   f"{html.escape(l)} {v:.2f}</text>")
    return ui_kit.panel(title, f"<svg viewBox='0 0 {w} 100' width='100%' style='max-width:{w}px'>{''.join(out)}</svg>") if title else f"<svg viewBox='0 0 {w} 100' width='100%'>{''.join(out)}</svg>"


def graph(edges: list, size: int = 420, title: str = "") -> str:
    """Circle graph of detectors. edges = [(a, b, rho, cls)]; amber = REDUNDANT, red = OPPOSED, grey = INDEPENDENT. Width follows |rho|."""
    names = sorted({n for a, b, _r, _c in edges for n in (a, b)})
    if not names:
        return ""
    cx = cy = size / 2
    R = size / 2 - 52
    pos = {n: (cx + R * math.cos(2 * math.pi * i / len(names) - math.pi / 2), cy + R * math.sin(2 * math.pi * i / len(names) - math.pi / 2)) for i, n in enumerate(names)}
    col = {"REDUNDANT": WARN, "OPPOSED": DOWN, "INDEPENDENT": "var(--uk-line)"}
    out = []
    for a, b, rho, cls in sorted(edges, key=lambda e: abs(e[2])):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        op = ".18" if cls == "INDEPENDENT" else ".85"
        out.append(f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{col.get(cls, 'var(--uk-line)')}' stroke-width='{0.6 + 3.4 * abs(rho):.2f}' opacity='{op}'>"
                   f"<title>{html.escape(a)} / {html.escape(b)}: rho {rho:+.2f} {html.escape(cls)}</title></line>")
    for n, (x, y) in pos.items():
        anchor = "start" if x > cx + 4 else "end" if x < cx - 4 else "middle"
        dx = 9 if anchor == "start" else -9 if anchor == "end" else 0
        dy = -9 if y < cy - 4 and anchor == "middle" else 4
        out.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6' fill='{BY_ID['consensus'][3]}'/><text x='{x + dx:.1f}' y='{y + dy:.1f}' text-anchor='{anchor}' font-size='11' fill='var(--uk-text)'>{html.escape(n)}</text>")
    leg = ui_kit.legend([("redundant (same idea twice)", WARN), ("opposed", DOWN), ("independent", "var(--uk-dim)")])
    svg = f"<svg viewBox='0 0 {size} {size}' width='100%' style='max-width:{size}px'>{''.join(out)}</svg>"
    return ui_kit.panel(title, svg + leg) if title else svg + leg


def flow(snaps: dict | None = None) -> str:
    """Data-flow diagram: who reads whose published snapshot. A tab nobody reads yet is drawn dashed (an honest gap, not hidden)."""
    boxes = {"truth": (110, 40), "plateau": (310, 40), "trail": (110, 130), "decay": (310, 130), "consensus": (510, 40), "regime": (510, 130), "funnel": (110, 222)}
    bw, bh = 150, 44
    readers = {c for t in TABS for c in t[4]}
    out = ["<defs><marker id='ar' viewBox='0 0 8 8' refX='7' refY='4' markerWidth='7' markerHeight='7' orient='auto'><path d='M0 0 L8 4 L0 8 z' fill='var(--uk-dim)'/></marker></defs>"]
    for t in TABS:
        for src in t[4]:
            if t[0] in boxes and src in boxes:
                (sx, sy), (dx, dy) = boxes[src], boxes[t[0]]
                x1, y1 = sx + (bw / 2 if dx > sx else -bw / 2 if dx < sx else 0), sy + (bh / 2 if dy > sy else -bh / 2 if dy < sy else 0)
                x2, y2 = dx - (bw / 2 if dx > sx else -bw / 2 if dx < sx else 0), dy - (bh / 2 if dy > sy else -bh / 2 if dy < sy else 0)
                if dx == sx:
                    x1 = x2 = dx
                if dy == sy:
                    y1 = y2 = dy
                if src == "truth" and t[0] == "funnel":
                    out.append(f"<path d='M{sx - bw / 2} {sy} C{sx - 105} {sy + 40} {sx - 105} {dy - 30} {dx - bw / 2} {dy}' fill='none' stroke='var(--uk-line)' stroke-width='1.2' marker-end='url(#ar)'/>")
                elif src == "truth" and t[0] in ("decay",):   # long diagonal: keep it light so the picture stays readable
                    out.append(f"<line x1='{sx + 40}' y1='{sy + bh / 2}' x2='{dx - 40}' y2='{dy - bh / 2}' stroke='var(--uk-line)' stroke-width='1.2' marker-end='url(#ar)'/>")
                elif src == "truth" and t[0] == "consensus":
                    out.append(f"<path d='M{sx} {sy - bh / 2} Q{(sx + dx) / 2} {sy - 50} {dx} {dy - bh / 2}' fill='none' stroke='var(--uk-line)' stroke-width='1.2' marker-end='url(#ar)'/>")
                else:
                    out.append(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='var(--uk-dim)' stroke-width='1.4' marker-end='url(#ar)'/>")
    for tid, (x, y) in boxes.items():
        _i, title, glyph, acc, _c = BY_ID[tid]
        dash = " stroke-dasharray='4 3'" if tid == "regime" and tid not in readers else ""   # the one tab that was meant to feed others and does not yet
        out.append(f"<rect x='{x - bw / 2}' y='{y - bh / 2}' width='{bw}' height='{bh}' rx='10' fill='var(--uk-panel2)' stroke='{acc}' stroke-width='1.6'{dash}/>"
                   f"<text x='{x - bw / 2 + 12}' y='{y + 5}' font-size='15' fill='{acc}'>{html.escape(glyph)}</text>"
                   f"<text x='{x - bw / 2 + 32}' y='{y + 4}' font-size='11' fill='var(--uk-text)'>{html.escape(title)}</text>")
    if "regime" not in readers:
        out.append("<text x='510' y='172' text-anchor='middle' font-size='9' fill='var(--uk-dim)'>nobody reads the regime yet</text>")
    return ui_kit.panel("How the tabs help each other (arrows = reads the published snapshot)", f"<svg viewBox='0 0 620 254' width='100%'>{''.join(out)}</svg>")


def funnel(stages: list, accent: str = "#F76808", title: str = "") -> str:
    """Horizontal funnel: stages = [{name, n, killed}]. Bar width follows the count; the cut from the stage above is written beside it."""
    if not stages:
        return ""
    top = max(s["n"] for s in stages) or 1
    lw, bw, rh = 130, 330, 28
    out = []
    for i, s in enumerate(stages):
        y = 8 + i * rh
        w = max(2.0, bw * s["n"] / top)
        cut = f"  -{s['killed']}" if s.get("killed") else ""
        out.append(f"<text x='{lw - 8}' y='{y + 15}' text-anchor='end' font-size='11' fill='var(--uk-dim)'>{html.escape(str(s['name']))}</text>"
                   f"<rect x='{lw}' y='{y}' width='{w:.1f}' height='20' rx='5' fill='{html.escape(accent)}' opacity='{0.95 - 0.07 * i:.2f}'><title>{html.escape(str(s['name']))}: {s['n']}</title></rect>"
                   f"<text x='{lw + w + 8:.1f}' y='{y + 15}' font-size='11' fill='var(--uk-text)'>{s['n']}<tspan fill='{DOWN}'>{html.escape(cut)}</tspan></text>")
    h = 16 + len(stages) * rh
    svg = f"<svg viewBox='0 0 {lw + bw + 90} {h}' width='100%' style='max-width:{lw + bw + 90}px'>{''.join(out)}</svg>"
    return ui_kit.panel(title, svg) if title else svg


def overview_cards(root=None) -> list:
    """One card per tab from its PUBLISHED snapshot: (icon, label, value, sub, tone, pct). Missing snapshot = 'not run yet'."""
    r = lambda t: hub_core.read(t, root)
    cards = []
    s = r("truth")
    if s:
        cards.append((BY_ID["truth"][2], "Truth Court", f"N={s.get('n_trials', 0)}", f"need t>={s.get('bonferroni_t')} · luck ~{s.get('expected_max_null_t')} · pass {s.get('n_promotable', 0)}",
                      "up" if s.get("n_promotable") else "warn", None))
    else:
        cards.append((BY_ID["truth"][2], "Truth Court", "—", "not run yet", "", None))
    s = r("plateau")
    if s and s.get("findings"):
        f = s["findings"]
        ok = sum(1 for x in f if x.get("promote"))
        cards.append((BY_ID["plateau"][2], "Plateau Lab", f"{ok}/{len(f)}", f"series passing walk-forward · {s.get('n_trials', 0)} cells counted", "up" if ok else "warn", None))
    else:
        cards.append((BY_ID["plateau"][2], "Plateau Lab", "—", "not run yet", "", None))
    s = r("regime")
    if s and s.get("findings"):
        f = s["findings"]
        hot = [c for c, v in (s.get("funding") or {}).items() if v.get("stretched")]
        cards.append((BY_ID["regime"][2], "Regime Radar", f"{len(f)} series", ", ".join(f"{x['key'].split()[0].split(':')[-1]} {x['regime']}" for x in f[:3]) + (f" · funding stretched: {','.join(hot)}" if hot else ""), "", None))
    else:
        cards.append((BY_ID["regime"][2], "Regime Radar", "—", "not run yet", "", None))
    s = r("trail")
    sm = (s or {}).get("summary")
    if sm:
        lr = sm.get("live_net_avg_r")
        cards.append((BY_ID["trail"][2], "Decision Trail", f"{sm['signals']} signals", f"unproven {sm['unproven']} · closed {sm['closed_trusted']} · live net R {'n/a' if lr is None else lr}", "warn" if sm["unproven"] else "", None))
    else:
        cards.append((BY_ID["trail"][2], "Decision Trail", "—", "no signal log yet", "", None))
    s = r("decay")
    f = (s or {}).get("findings") or []
    if f:
        st_ = f[0]["state"]
        cards.append((BY_ID["decay"][2], "Decay Watch", st_, f"size x{f[0]['size']}" if f[0].get("size") is not None else f[0].get("why", ""),
                      "down" if st_ in ("RETIRE",) else "warn" if st_ in ("SHRINK", "WATCH") else "up" if st_ == "OK" else "", None))
    else:
        cards.append((BY_ID["decay"][2], "Decay Watch", "—", "not run yet", "", None))
    s = r("consensus")
    c = (s or {}).get("counts")
    if c:
        cards.append((BY_ID["consensus"][2], "Consensus Map", f"{c['REDUNDANT']} / {c['OPPOSED']} / {c['INDEPENDENT']}", "redundant / opposed / independent pairs", "warn" if c["REDUNDANT"] else "", None))
    else:
        cards.append((BY_ID["consensus"][2], "Consensus Map", "—", "not run yet", "", None))
    s = r("funnel")
    if s and s.get("tested"):
        cards.append((BY_ID["funnel"][2], "Kill Funnel", f"{s['kill_rate']}% killed", f"{s['survived']} of {s['tested']} survive · biggest cut: {s.get('biggest_kill')}", "warn" if not s["survived"] else "up", None))
    else:
        cards.append((BY_ID["funnel"][2], "Kill Funnel", "—", "not run yet", "", None))
    return cards


def render_overview(st, L=lambda x: x, root=None) -> None:
    """Command Center: one card per tab (from published snapshots only) and the data-flow diagram."""
    spec = type("S", (), {"title": "Command Center", "glyph": "◈", "accent": BY_ID["overview"][3], "consumes": ()})
    show(st, header(spec, L("Headline of every tab and how they feed each other. Run a tab to fill its card.")) + cards(overview_cards(root)) + flow())
    st.caption(L("Cards come from each tab's published snapshot; a tab that has not run shows 'not run yet'. Nothing here is estimated."))
