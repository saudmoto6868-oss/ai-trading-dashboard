"""Open setups on the Radar (owner 2026-11-16): one list of harmonic patterns and OTE zones found by the scanner,
with the direction each one points to, and how many of them the Radar filters also pick.
Read only: nothing here places an order. Targets come from the scanner data; where it has none the row says so."""
from __future__ import annotations

from modules.chart_scan import flag_side


def _kind(flag: str) -> str | None:
    if flag.startswith("harm_") and not flag.startswith("harm_vol_"):
        return "Harmonic"
    if flag.startswith("ote"):
        return "OTE"
    return None


def _direction(flag: str, d: dict) -> str:
    """long / short from the scanner's own side tags first, then the flag name, else 'unclear' (never guessed)."""
    for s_ in (d.get("sides") or {}).get(flag, []) or []:
        if s_ in ("buy", "long", "bull"):
            return "long"
        if s_ in ("sell", "short", "bear"):
            return "short"
    side = flag_side(flag)
    if side == "buy":
        return "long"
    if side == "sell":
        return "short"
    low = flag.lower()
    if low.endswith(("_long", "_bull", "_buy")):
        return "long"
    if low.endswith(("_short", "_bear", "_sell")):
        return "short"
    return "unclear"


def open_setups(data: dict, shown: set | None = None) -> list[dict]:
    """data = {symbol: scanner result with 'flags' and 'price'}; shown = symbols that pass the Radar filters."""
    rows = []
    for sym, d in (data or {}).items():
        for flag in d.get("flags") or []:
            kind = _kind(flag)
            if not kind:
                continue
            rows.append({"symbol": sym, "setup": kind, "flag": flag,
                         "direction": _direction(flag, d),
                         "price": d.get("price"), "in_filter": bool(shown and sym in shown)})
    return rows


def summary(rows: list[dict]) -> dict:
    out = {"total": len(rows), "long": 0, "short": 0, "unclear": 0, "in_filter": 0}
    for r in rows:
        out[r["direction"]] = out.get(r["direction"], 0) + 1
        out["in_filter"] += 1 if r["in_filter"] else 0
    return out
