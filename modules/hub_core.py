"""RESEARCH HUB CORE: the small contract every Hub tab follows, so each tab stays separate but can help the others.

Rules (docs/RESEARCH_HUB.md):
  * A tab OWNS one snapshot file data/hub/<tab_id>.json. Only that tab writes it (publish()).
  * Other tabs only READ it (read()). No tab imports another tab's code, so a broken tab cannot break the rest.
  * Every tab publishes {"asof", "tab", "n_trials", "findings": [...]} so the Truth Court can count all trials honestly.
  * Self-improvement is gated: promote() is the ONE rule for "a change may go live" (same bar as docs/PRIORITIES.md:
    n >= 100, t > 3, both halves positive, costs included). decay_cusum() says when a live rule should be shrunk or retired.
Pure Python, stdlib only (no streamlit import here), so it is testable without the app."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

HUB_DIR = Path(__file__).resolve().parent.parent / "data" / "hub"

MIN_N = 100          # trades before a number counts as evidence
MIN_T = 3.0          # Harvey-Liu-Zhu style hurdle
DECAY_K = 0.5        # CUSUM slack, in sigmas
DECAY_H = 4.0        # CUSUM alarm level, in sigmas


@dataclass(frozen=True)
class TabSpec:
    """Identity of one Hub tab: its own name, glyph and accent colour, what it publishes and which tabs it reads."""
    id: str
    title: str
    glyph: str
    accent: str
    purpose: str
    consumes: tuple = field(default_factory=tuple)


def _path(tab_id: str, root: Path | None = None) -> Path:
    safe = "".join(c for c in tab_id if c.isalnum() or c in "_-")
    return (root or HUB_DIR) / f"{safe}.json"


def publish(tab_id: str, findings: list, n_trials: int, extra: dict | None = None, root: Path | None = None) -> dict:
    """Write this tab's snapshot (owner only). n_trials = how many hypotheses/configs this tab looked at."""
    doc = {"asof": int(time.time()), "tab": tab_id, "n_trials": int(n_trials), "findings": findings}
    if extra:
        doc.update(extra)
    p = _path(tab_id, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    tmp.replace(p)
    return doc


def read(tab_id: str, root: Path | None = None) -> dict | None:
    """Read another tab's snapshot (read-only). None if it was never published or is unreadable."""
    try:
        return json.loads(_path(tab_id, root).read_text())
    except (FileNotFoundError, ValueError, OSError):
        return None


def total_trials(tab_ids: list, root: Path | None = None) -> int:
    """Sum of n_trials over the given tabs: the honest N for multiple-testing corrections."""
    return sum(int((read(t, root) or {}).get("n_trials", 0)) for t in tab_ids)


def promote(cand: dict, champion: dict | None = None, min_n: int = MIN_N, min_t: float = MIN_T) -> tuple[bool, list]:
    """The single gate for 'may go live'. cand needs: n, t, is_avgR, oos_avgR, net_avgR (after costs).
    Returns (ok, reasons_it_failed). A challenger must also beat the champion's OOS net R."""
    why = []
    n = cand.get("n") or 0
    t = cand.get("t")
    if n < min_n:
        why.append(f"n={n} < {min_n}")
    if t is None:
        why.append("no t-stat")
    elif abs(t) < min_t:
        why.append(f"|t|={abs(t):.2f} < {min_t}")
    for k, label in (("is_avgR", "in-sample"), ("oos_avgR", "out-of-sample")):
        v = cand.get(k)
        if v is None:
            why.append(f"{label} half missing")
        elif v <= 0:
            why.append(f"{label} half not positive ({v:+.3f}R)")
    net = cand.get("net_avgR")
    if net is None:
        why.append("costs not included")
    elif net <= 0:
        why.append(f"net of costs {net:+.3f}R")
    if champion is not None and not why:
        if (cand.get("oos_avgR") or 0) <= (champion.get("oos_avgR") or 0):
            why.append("does not beat the champion out-of-sample")
    return (not why, why)


def decay_cusum(xs: list, mu0: float, sigma: float, k: float = DECAY_K, h: float = DECAY_H) -> dict:
    """One-sided CUSUM for a live edge fading below its backtest mean mu0. xs = per-trade R in time order.
    alarm=True once the downward cumulative sum passes h sigmas: shrink size or retire by a rule fixed in advance."""
    if sigma <= 0:
        return {"alarm": False, "s": 0.0, "at": None, "n": len(xs)}
    s, at = 0.0, None
    for i, x in enumerate(xs):
        s = max(0.0, s + (mu0 - x) / sigma - k)
        if at is None and s > h:
            at = i
    return {"alarm": at is not None, "s": round(s, 3), "at": at, "n": len(xs)}
