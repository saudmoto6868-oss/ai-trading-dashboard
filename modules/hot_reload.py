"""Reload an imported module when a redeploy left an OLD copy in memory (owner 2026-10-23: the live Radar crashed with 'class_symbols() got an unexpected keyword
argument wide'). Streamlit keeps imported modules between runs, and a hot redeploy replaces the files but not always the process. Every module whose new functions
main.py relies on is listed here with the names (and one parameter) the current version must have; a copy missing any of them is reloaded before use.
When you add a function or a parameter that main.py calls, add it to NEED / SIGS."""
from __future__ import annotations

import importlib
import importlib.util
import os
import sys

NEED = {   # module -> attributes the current version defines
    "modules.academy": ("deep", "ordered_schools", "learning_path", "refs", "schools", "load", "GRADE", "SCHOOL_ORDER"),
    "modules.academy_art": ("ART", "MIRRORED", "art"),
    "modules.ui_kit": ("css", "kpi", "row", "donut", "gauge", "bars", "panel", "TOKENS"),
    "modules.market_map": ("apply_filters", "board", "breadth", "by_class"),
    "modules.fv_screen": ("metrics", "apply", "test", "similar", "candle_set", "FILTERS"),
    "modules.symbol_icon": ("icon",),
    "modules.asset_classes": ("class_symbols",),
}
SIGS = {   # (module, function) -> a parameter name the current version has
    ("modules.asset_classes", "class_symbols"): "wide",
    ("modules.ui_kit", "css"): "rad",
}


def stale(mod, attrs=(), sig=None) -> bool:
    """True when the module lacks a needed attribute, or the function in sig = (name, parameter) lacks that parameter."""
    if any(not hasattr(mod, a) for a in attrs):
        return True
    if sig:
        fn = getattr(mod, sig[0], None)
        code = getattr(fn, "__code__", None)
        if code is not None and sig[1] not in code.co_varnames[:code.co_argcount]:
            return True
    return False


def refresh(modules=None, need=None, sigs=None) -> list:
    """Reload every stale module; returns the names reloaded. modules / need / sigs can be replaced in tests."""
    modules = sys.modules if modules is None else modules
    need, sigs = NEED if need is None else need, SIGS if sigs is None else sigs
    out = []
    for name, attrs in need.items():
        mod = modules.get(name)
        if mod is None:
            continue
        sg = next(((f, p) for (m, f), p in sigs.items() if m == name and stale(mod, (), (f, p))), None)
        if stale(mod, attrs) or sg:
            try:
                importlib.reload(mod)
                out.append(name)
            except Exception:
                pass
    return out


def compiled_from_older_source(mod) -> bool:
    """True when the .pyc on disk was compiled from a DIFFERENT source time than the file now: the copy in memory (loaded earlier) is older than the file. A module
    that was just imported fresh has a matching .pyc, and a hash-based or missing .pyc is left alone."""
    src = getattr(mod, "__file__", None)
    if not src or not src.endswith(".py"):
        return False
    try:
        cached = importlib.util.cache_from_source(src)
        if not os.path.exists(cached):
            return False
        with open(cached, "rb") as fh:
            head = fh.read(16)
        if len(head) < 12 or int.from_bytes(head[4:8], "little") & 1:     # bit 0 = hash-based pyc
            return False
        return int.from_bytes(head[8:12], "little") != (int(os.path.getmtime(src)) & 0xFFFFFFFF)
    except Exception:
        return False


def refresh_changed(prefix: str = "modules.", modules=None) -> list:
    """Reload every project module whose source file changed since it was loaded (all of modules.*, so no list has to be kept up to date)."""
    modules = sys.modules if modules is None else modules
    out = []
    for name in sorted(n for n in list(modules) if n.startswith(prefix) and n != __name__):
        if compiled_from_older_source(modules[name]):
            try:
                importlib.reload(modules[name])
                out.append(name)
            except Exception:
                pass
    return out
