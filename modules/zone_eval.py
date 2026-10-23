"""Judge of the confluence-zone forward test (owner 2026-10-23). The Workspace logs every zone (2+ independent sources at one price) and follows
the price path (JS: ZoneLog in modules/workspace_app.html); 'Export zone test log' downloads the records, this module judges them.

Per zone: outcome 'hold' (after touching the level price moved >= rbp bp back to the side it came from), 'break' (>= rbp bp through) or None
(not touched / unresolved). Every zone has a CONTROL level (mirror price across the mid at creation) tracked the same way. The question is only
whether zones hold more often than arbitrary levels at the same distance (direction-neutral). Gate = the lab's: >= 100 paired zones, paired
t > 3, mean difference > 0, and > 0 in both time halves. Anything below that is 'not evidence'."""
from __future__ import annotations

import json
import math

GATE_N, GATE_T = 100, 3.0


def load(files) -> list:
    """Records from one or several exported JSON files (paths, file-like objects or already-parsed dicts)."""
    recs = []
    for f in files:
        d = f if isinstance(f, dict) else json.load(f) if hasattr(f, "read") else json.load(open(f, encoding="utf-8"))
        for r in d.get("recs", []):
            r = dict(r); r["sym"] = d.get("sym", r.get("sym", "?")); recs.append(r)
    return sorted(recs, key=lambda r: r.get("t", 0))


def _out(r, k):
    return (r.get(k) or {}).get("out")


def _t(x):
    n = len(x)
    if n < 2:
        return 0.0
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1))
    return m / (sd / math.sqrt(n)) if sd > 0 else 0.0


def diffs(recs) -> list:
    """Paired outcome differences (1 = zone held and control did not, -1 = the reverse, 0 = same) for zones where both resolved."""
    return [(1 if _out(r, "z") == "hold" else 0) - (1 if _out(r, "c") == "hold" else 0) for r in recs if _out(r, "z") and _out(r, "c")]


def judge(recs) -> dict:
    d = diffs(recs); n = len(d)
    paired = [r for r in recs if _out(r, "z") and _out(r, "c")]
    half = n // 2
    h1, h2 = d[:half], d[half:]
    mean = lambda x: round(sum(x) / len(x), 3) if x else None
    cnt = lambda k, v: sum(1 for r in recs if _out(r, k) == v)
    by = {}
    for r in paired:
        b = by.setdefault(r.get("strength", 0), []); b.append((1 if _out(r, "z") == "hold" else 0) - (1 if _out(r, "c") == "hold" else 0))
    out = {"zones": len(recs), "zone_touched": sum(1 for r in recs if (r.get("z") or {}).get("touchT")), "zone_hold": cnt("z", "hold"), "zone_break": cnt("z", "break"),
           "ctrl_hold": cnt("c", "hold"), "ctrl_break": cnt("c", "break"), "paired": n, "diff": mean(d), "t": round(_t(d), 2),
           "half1": mean(h1), "half2": mean(h2), "by_strength": {k: {"n": len(v), "diff": mean(v)} for k, v in sorted(by.items())}}
    out["pass"] = bool(n >= GATE_N and out["t"] > GATE_T and (out["diff"] or 0) > 0 and (out["half1"] or 0) > 0 and (out["half2"] or 0) > 0)
    return out
