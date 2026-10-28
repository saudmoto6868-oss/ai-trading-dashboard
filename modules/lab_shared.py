"""Shared helpers for all Lab tabs (validation_lab, calibration_lab, …).

Single source of truth for:
  - loading strategy_lab.json rows with side filter
  - classifier constants (mirrors lab_tiers, no duplication)
  - ui_kit.strip() wrapper with standard tone mapping
  - R-value formatter
"""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any

LAB_PATH = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
MIN_N = 30
OFF_MIN_N = 300
OFF_MAX_R = -0.06

TIER_ICON = {"edge": "⭐", "positive": "✅", "neutral": "➖",
             "negative": "⚠️", "off": "🚫", "weak": "🔘"}
TIER_TONE = {"edge": "up", "positive": "up", "neutral": "",
             "negative": "down", "off": "down", "weak": ""}


def load_rows(side: str = "all") -> list[dict[str, Any]]:
    """Return rows matching *side* from strategy_lab.json; [] on any error."""
    try:
        data = json.loads(LAB_PATH.read_text())
        return [r for r in data.get("rows", []) if r.get("side") == side]
    except Exception:
        return []


def tier(row: dict) -> str:
    n, avg = row.get("n", 0), row.get("avgR", 0.0)
    if n < MIN_N:              return "weak"
    if n >= OFF_MIN_N and avg <= OFF_MAX_R: return "off"
    if row.get("edge"):        return "edge"
    if avg > 0:                return "positive"
    if avg < 0:                return "negative"
    return "neutral"


def fmt_r(v) -> str:
    """Format an R value; return '—' for None."""
    return f"{v:+.3f}" if v is not None else "—"


def no_data_msg(st_mod, ar: str, en: str) -> None:
    """Show st.info in both languages when lab data is absent."""
    try:
        from modules.i18n import L
        st_mod.info(L(ar, en))
    except Exception:
        st_mod.info(ar)
