"""
Item 25 — Wire pipeline winners to the scanner (step 3 of PIPELINE.md).

Reads data/strategy_lab.json, finds keys that pass the strict gate
(n>=100, t>3, avgR>0 in both IS and OOS halves), and returns a
STRATEGY_FILTERS-compatible dict so chart_scan.py can offer a
"Pipeline winners" filter group.

Works with or without a real lab run:
- No lab data / no winners  → returns an empty dict (scanner unchanged).
- Winners present           → adds one filter per key + a group filter.

Usage (in chart_scan.py):
    from modules.pipeline_wire import pipeline_filters
    STRATEGY_FILTERS.update(pipeline_filters())
"""

from __future__ import annotations
from modules.pipeline_report import load_rows, gate_passed

# Map lab key -> (signal_key_or_family, kind)
# Extend this table as new keys are added to signals.py / strategy_lab.
_KEY_MAP: dict[str, tuple[str, str]] = {
    # Existing signal keys already in chart_scan STRATEGY_FILTERS
    "level":        ("level",      "key"),
    "ob":           ("ob",         "key"),
    "fvg":          ("fvg",        "key"),
    "sweep":        ("sweep",      "key"),
    "smt":          ("smt",        "key"),
    "kzs":          ("kzs",        "key"),
    "po3":          ("po3",        "key"),
    "donch":        ("donch",      "key"),
    "sma1040":      ("sma1040",    "key"),
    "turtle55":     ("turtle55",   "key"),
    "rsi_div":      ("rsi_div",    "key"),
    "macd_div":     ("macd_div",   "key"),
    "ohl_break":    ("ohl_break",  "key"),
    "ote":          ("ote",        "key"),
    "judas":        ("judas",      "key"),
    "breaker":      ("breaker",    "key"),
    "orb":          ("orb",        "key"),
    "sess_amd":     ("sess_amd",   "key"),
    "m2022":        ("m2022",      "key"),
    "cisd":         ("cisd",       "key"),
    "tlbreak":      ("tlbreak",    "key"),
    "crt":          ("crt",        "key"),
    "harmonic":     ("harm",       "extra"),
    # Elliott / SMT lab keys
    "ew_r3_1.2":    ("Elliott",    "family"),
    "ew_r3_3.0":    ("Elliott",    "family"),
    "ew_r2_1.2":    ("Elliott",    "family"),
    "ew_r2_3.0":    ("Elliott",    "family"),
}


def pipeline_filters(side: str = "all") -> dict:
    """
    Return a STRATEGY_FILTERS-compatible dict for keys that pass the
    strict A+++ gate.  Empty dict if no winners or lab not available.
    """
    rows = load_rows(side=side)
    if not rows:
        return {}

    winners = gate_passed(rows)
    if not winners:
        return {}

    out: dict = {}
    for row in winners:
        key = row.get("key", "")
        if key not in _KEY_MAP:
            continue  # lab key not yet wired to a signal
        signal_key, kind = _KEY_MAP[key]
        avgR = row.get("avgR", 0)
        n    = row.get("n", 0)
        fid  = f"st_pip_{key}"
        label = f"Pipeline ⭐ {key} (+{avgR:.2f}R, n={n})"
        out[fid] = (label, (kind, signal_key))

    if len(out) > 1:
        # Group filter: any pipeline winner
        # We can't do OR in the existing filter engine, so we add a note.
        out["st_pip_any"] = (
            f"Pipeline ⭐ any winner ({len(out)} keys)",
            ("family", "__pipeline__"),   # handled in chart_scan if needed
        )

    return out


def winner_keys(side: str = "all") -> list[str]:
    """Return just the lab keys that pass the gate (for other modules)."""
    rows = load_rows(side=side)
    return [r["key"] for r in gate_passed(rows)]
