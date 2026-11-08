"""Shared helpers for the lab tabs on the Stats page (Validation Lab, Calibration, Class rotation, Evidence summary).

One place for: the bilingual text helper (modules.i18n.L takes ONE argument, so it cannot take Arabic + English), the lab file loader
(cached by file mtime), the evidence thresholds (imported from lab_tiers, never copied), the tier classifier and the symbol -> asset-class map.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from modules import lab_tiers as _LT

LAB_PATH = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
MIN_N = _LT.MIN_N
OFF_MIN_N = _LT.OFF_MIN_N
OFF_MAX_R = _LT.OFF_R

# "+" means avgR above 0 in the sample, NOT proven; only the lab's own edge flag gets the star
TIER_ICON = {"edge": "⭐", "positive": "➕", "neutral": "➖", "negative": "⚠️", "off": "🚫", "weak": "🔘"}

_cache: dict = {"mtime": None, "path": None, "rows": []}


def t(ar: str, en: str) -> str:
    """Arabic or English text by the app language."""
    try:
        from modules.i18n import lang
        return ar if lang() == "ar" else en
    except Exception:
        return en


def _all_rows() -> list[dict[str, Any]]:
    try:
        m = os.path.getmtime(LAB_PATH)
        if _cache["mtime"] == m and _cache["path"] == str(LAB_PATH):
            return _cache["rows"]
        rows = json.loads(LAB_PATH.read_text()).get("rows", [])
        _cache.update(mtime=m, path=str(LAB_PATH), rows=rows)
        return rows
    except Exception:
        return []


def load_rows(side: str = "all") -> list[dict[str, Any]]:
    """Rows of strategy_lab.json with this `side` ([] when the file is missing or unreadable)."""
    return [r for r in _all_rows() if r.get("side") == side]


def tier(row: dict) -> str:
    n, avg = row.get("n", 0), row.get("avgR", 0.0)
    if n < MIN_N:
        return "weak"
    if n >= OFF_MIN_N and avg <= OFF_MAX_R:
        return "off"
    if row.get("edge"):
        return "edge"
    if avg > 0:
        return "positive"
    if avg < 0:
        return "negative"
    return "neutral"


def fmt_r(v) -> str:
    return f"{v:+.3f}" if v is not None else "—"


def no_data_msg(st_mod, ar: str, en: str) -> None:
    st_mod.info(t(ar, en))


def class_of(sym: str) -> str:
    """Asset class of a scanner symbol, from the same tables the app uses (not a guess from the name)."""
    s = str(sym or "")
    try:
        if s.startswith("HL:"):
            from modules import hl_feed
            return hl_feed.category(s)
        if s.startswith("FH:"):
            return "Forex"
        if s.startswith("Y:"):
            from modules import yahoo_feed
            for cls, lst in yahoo_feed.BY_CLASS.items():
                if s[2:] in lst:
                    return cls
            return "Stocks"
    except Exception:
        pass
    return "Crypto"
