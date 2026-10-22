"""Technical Office control-room widgets (owner's reference images, 2026-10-22): dark cards with status dots, a gauge, alert
cards, an indicator grid, a system map and a tool grid. Pure HTML builders (no Streamlit import) so they can be tested;
main.py feeds them real numbers only (lab file, work board, workflow files, source checks)."""
from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TONE = {"ok": "#2dd4bf", "warn": "#f0b429", "bad": "#f87171", "info": "#93c5fd", "off": "#6b7480"}
STATUS_TONE = {"done": "ok", "running": "ok", "decided": "ok", "ready": "info", "review": "info", "in progress": "info",
               "open": "off", "waiting": "warn", "parked": "off", "blocked": "bad"}

CSS = """<style>
.xo-row{display:flex;flex-wrap:wrap;gap:12px;margin:4px 0 12px}
.xo-card{background:#1b2027;border:1px solid #2a313a;border-radius:14px;padding:14px 16px;color:#e6e9ee;box-sizing:border-box}
.xo-h{font-size:15px;font-weight:700;margin:0 0 8px;color:#e6e9ee}
.xo-sub{font-size:12px;color:#a3adba}
.xo-chip{display:inline-flex;align-items:center;gap:6px;background:#232a33;border-radius:8px;padding:5px 10px;font-size:12px;color:#e6e9ee;margin:0 6px 6px 0}
.xo-dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none}
.xo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.xo-tile{background:#232a33;border-radius:10px;padding:10px 12px}
.xo-big{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:26px;font-weight:700;line-height:32px}
.xo-alert{background:#232a33;border-radius:10px;padding:10px 12px;margin-bottom:8px}
.xo-badge{border-radius:6px;padding:2px 8px;font-size:11px}
.xo-map{display:flex;flex-direction:column;align-items:center;gap:0}
.xo-maprow{display:flex;flex-wrap:wrap;justify-content:center;gap:12px}
.xo-node{background:#1f262e;border:1px solid #2f3742;border-radius:10px;padding:8px 10px;min-width:150px;display:flex;gap:8px;align-items:center;font-size:13px}
.xo-link{width:2px;height:22px;background:#3d4753;margin:2px 0}
.xo-tool{background:#232a33;border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:4px;min-height:86px}
.xo-table{width:100%;border-collapse:collapse;font-size:13px}.xo-table td,.xo-table th{border-bottom:1px solid #2a313a;padding:6px 8px;text-align:start}
.xo-table th{color:#a3adba;font-weight:600}
</style>"""


def esc(x) -> str:
    return html.escape(str(x))


def dot(tone: str) -> str:
    return f"<span class='xo-dot' style='background:{TONE.get(tone, tone)}'></span>"


def badge(text: str, tone: str) -> str:
    c = TONE.get(tone, tone)
    return f"<span class='xo-badge' style='background:{c}22;color:{c}'>{esc(text)}</span>"


def chips(items) -> str:
    """items: (label, value, tone)."""
    return "<div>" + "".join(f"<span class='xo-chip'>{dot(t)}<span style='color:#a3adba'>{esc(a)}</span> <b>{esc(b)}</b></span>" for a, b, t in items) + "</div>"


def gauge(value: int, total: int, title: str, caption: str, center_label: str) -> str:
    """Half-ring gauge: value of total (e.g. groups that passed the evidence gate)."""
    frac = 0.0 if not total else max(0.0, min(1.0, value / total))
    ang = math.pi * (1 - frac)
    x, y = 120 + 100 * math.cos(ang), 125 - 100 * math.sin(ang)
    col = TONE["ok"] if frac >= .5 else TONE["warn"] if frac > 0 else TONE["bad"]
    arc = f"<path d='M 20 125 A 100 100 0 0 1 {x:.1f} {y:.1f}' fill='none' stroke='{col}' stroke-width='16' stroke-linecap='round'/>" if frac > 0 else \
          f"<circle cx='20' cy='125' r='8' fill='{col}'/>"
    return (f"<div class='xo-card' style='flex:1 1 280px;max-width:420px'><div class='xo-h'>{esc(title)}</div><div class='xo-sub'>{esc(caption)}</div>"
            f"<div style='position:relative;height:150px;display:flex;justify-content:center'><svg role='img' aria-label='{esc(value)} / {esc(total)}' width='240' height='140' viewBox='0 0 240 140'>"
            f"<path d='M 20 125 A 100 100 0 0 1 220 125' fill='none' stroke='#2a313a' stroke-width='16' stroke-linecap='round'/>{arc}</svg>"
            f"<div style='position:absolute;top:62px;text-align:center'><div class='xo-big' style='font-size:38px'>{esc(value)}<span style='font-size:18px;color:#a3adba'> / {esc(total)}</span></div>"
            f"<div class='xo-sub'>{esc(center_label)}</div></div></div></div>")


def alerts(title: str, items) -> str:
    """items: (headline, badge text, tone, note)."""
    body = "".join(f"<div class='xo-alert'><div style='font-size:14px;font-weight:600'>{esc(h)}</div><div style='display:flex;gap:8px;align-items:center;margin-top:4px'>"
                   f"{badge(b, t)}<span class='xo-sub'>{esc(n)}</span></div></div>" for h, b, t, n in items)
    return f"<div class='xo-card' style='flex:1 1 280px'><div class='xo-h'>{esc(title)}</div>{body or ''}</div>"


def indicators(title: str, items) -> str:
    """items: (label, value, sub, tone or None)."""
    tiles = "".join(f"<div class='xo-tile'><div class='xo-sub'>{esc(a)}</div><div class='xo-big' style='color:{TONE.get(t, '#e6e9ee') if t else '#e6e9ee'}'>{esc(v)}</div>"
                    f"<div class='xo-sub' style='font-size:11px'>{esc(s)}</div></div>" for a, v, s, t in items)
    return f"<div class='xo-card' style='flex:2 1 420px'><div class='xo-h'>{esc(title)}</div><div class='xo-grid'>{tiles}</div></div>"


def system_map(title: str, caption: str, rows) -> str:
    """rows: list of rows, each a list of (name, detail, tone); rows are joined top to bottom by a line."""
    parts = []
    for i, row in enumerate(rows):
        if i:
            parts.append("<div class='xo-link'></div>")
        parts.append("<div class='xo-maprow'>" + "".join(
            f"<div class='xo-node' style='border-color:{TONE.get(t, '#2f3742')}66'>{dot(t)}<span><b>{esc(n)}</b><br><span class='xo-sub'>{esc(d)}</span></span></div>"
            for n, d, t in row) + "</div>")
    return f"<div class='xo-card' style='flex:1 1 100%'><div class='xo-h'>{esc(title)}</div><div class='xo-sub' style='margin-bottom:10px'>{esc(caption)}</div><div class='xo-map'>{''.join(parts)}</div></div>"


def tools(title: str, items) -> str:
    """items: (name, what, status text, tone)."""
    cells = "".join(f"<div class='xo-tool'><b style='font-size:14px'>{esc(n)}</b><span class='xo-sub'>{esc(w)}</span><span style='font-size:11px;color:{TONE.get(t, '#a3adba')}'>{esc(s)}</span></div>"
                    for n, w, s, t in items)
    return f"<div class='xo-card' style='flex:1 1 100%'><div class='xo-h'>{esc(title)}</div><div class='xo-grid' style='grid-template-columns:repeat(auto-fill,minmax(200px,1fr))'>{cells}</div></div>"


def table(headers, rows) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<div class='xo-card' style='overflow-x:auto'><table class='xo-table'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


# ---- data helpers -------------------------------------------------------------------------------------------------

def load_tasks(path=ROOT / "data" / "office_tasks.json") -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {"tasks": []}


def task_counts(tasks) -> dict:
    out = {}
    for t in tasks:
        out[t.get("status", "open")] = out.get(t.get("status", "open"), 0) + 1
    return out


def workflows(folder=ROOT / ".github" / "workflows") -> list:
    """[{file, name, schedule, manual, writes}] read from the workflow files (no YAML library needed)."""
    out = []
    for p in sorted(Path(folder).glob("*.yml")):
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        m = re.search(r"^name:\s*(.+)$", txt, re.M)
        crons = re.findall(r"cron:\s*[\"']([^\"']+)[\"']", txt)
        out.append({"file": p.name, "name": (m.group(1).strip().strip("\"'") if m else p.stem), "schedule": ", ".join(crons),
                    "manual": "workflow_dispatch" in txt, "writes": bool(re.search(r"contents:\s*write", txt)) or "git push" in txt})
    return out
