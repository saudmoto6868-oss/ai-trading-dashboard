"""Spot desk snapshot for the Workspace (owner 2026-11-15: bring Spot into the Workspace).

The Workspace is a browser page and cannot read data/ on the server, so the Spot desk's
daily run writes ONE read-only JSON file: docs/spot/snapshot.json. The Workspace embeds it at
build time (workspace.build_workspace_html -> cfg["spot"]) and the "Spot desk" widget reads it.

Each school keeps its own method. The snapshot carries the ideas, the 4-horizon brain per
market, the live setups with their evidence (t / n), and the news tilt, unchanged.
No orders, no prices written by hand: every number comes from the Spot modules."""
from __future__ import annotations

import datetime as _dt
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "docs", "spot", "snapshot.json")
SETUP_KEYS = ("id", "school_ar", "name", "side", "tf", "entry", "stop", "targets", "ev_label", "evidence")
HZ_KEYS = ("label", "tf", "score", "verdict", "verdict_ar", "reasons", "entry", "stop", "target")


def _num(x):
    try:
        f = float(x)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def _jsonable(o):
    """numpy / pandas scalars -> python; tuples -> lists; anything else -> str."""
    if hasattr(o, "item"):
        try:
            return o.item()
        except Exception:
            pass
    if isinstance(o, (list, tuple)):
        return [_jsonable(x) for x in o]
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if o is None or isinstance(o, (str, bool, int)):
        return o
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    return str(o)


def _brain(br: dict) -> dict:
    hz = {}
    for k, v in (br.get("horizons") or {}).items():
        if isinstance(v, dict):
            hz[k] = {f: _jsonable(v.get(f)) for f in HZ_KEYS if f in v}
    setups = []
    for s in br.get("setups") or []:
        setups.append({f: _jsonable(s.get(f)) for f in SETUP_KEYS if f in s})
    return {"asset": br.get("asset"), "price": _num(br.get("price")), "head": br.get("head"), "horizons": hz,
            "flow": _jsonable(br.get("flow")), "inst": _jsonable(br.get("inst")), "news": _jsonable(br.get("news")),
            "guard": _jsonable(br.get("guard")), "ideas": _jsonable(br.get("ideas") or []), "setups": setups[:40]}


def build(desk: dict, brains: list | None = None, now: _dt.datetime | None = None) -> dict:
    """desk = spot_ideas.desk() result; brains = list of spot_brain.run() results (one per market)."""
    now = now or _dt.datetime.now(_dt.timezone.utc)
    markets = []
    for m in desk.get("markets") or []:
        m = dict(m)
        m["spark"] = [_num(x) for x in (m.get("spark") or [])][-52:]
        markets.append(_jsonable(m))
    return {"generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "ideas": _jsonable(desk.get("ideas") or []),
            "markets": markets, "log": [str(x) for x in (desk.get("log") or [])][:80],
            "news": _jsonable(desk.get("news") or [])[:12], "risk_off": _num(desk.get("risk_off")) or 0,
            "brains": [_brain(b) for b in (brains or []) if isinstance(b, dict) and b.get("asset")]}


def write(snap: dict, path: str = PATH) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)
    return path


def load(path: str = PATH) -> dict:
    """Embedded into the Workspace at build time. Missing or broken file -> {} (the widget says so)."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}
