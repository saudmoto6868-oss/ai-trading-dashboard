"""Radar / Chart Scanner filter presets (owner 2026-10-24, item B): a dropdown by STRATEGY NAME that sets all the filter dropdowns at once, plus the
user's own saved presets. Pure Python (no Streamlit import): main.py passes st.session_state in, so it can be unit-tested.

Widget keys it writes (all of them exist in main.py `_radar_filters`): cs_rsi, cs_mom_a (moves), cs_mom_v (volume), cs_pat, cs_strat, cs_stack,
cs_side, cs_mode. Anything a preset does not name is reset to "no filter", so choosing a preset never leaves old choices behind."""
import json
import os
import re

PRESET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "radar_presets.json")   # user presets; on Streamlit Cloud the disk is reset on restart
NONE = "— none —"

# name -> {key: value}; lists = multiselect keys, strings = selectbox values
BUILTIN = {
    "Oversold bounce":    {"cs_rsi": ["rsi_lt30"], "cs_mom_v": ["vol_2x"], "cs_side": "Buy only"},
    "Overbought fade":    {"cs_rsi": ["rsi_gt70"], "cs_side": "Sell only"},
    "Bull trend stack":   {"cs_stack": "Bullish (px>9>20>50)", "cs_side": "Buy only"},
    "Bear trend stack":   {"cs_stack": "Bearish (px<9<20<50)", "cs_side": "Sell only"},
    "Volume breakout":    {"cs_mom_a": ["chg_up2"], "cs_mom_v": ["vol_3x"], "cs_side": "Buy only"},
    "Volume breakdown":   {"cs_mom_a": ["chg_dn2"], "cs_mom_v": ["vol_3x"], "cs_side": "Sell only"},
    "Reversal patterns":  {"cs_pat": ["dbl_bottom", "dbl_top"], "cs_mode": "Any selected"},
    "Channels & trendlines": {"cs_pat": ["chan_up", "chan_dn", "tl_up", "tl_dn"], "cs_mode": "Any selected"},
    "SMC / ICT setups":   {"cs_strat": ["st_msb", "st_ob", "st_unicorn"], "cs_mode": "Any selected"},
    "Elliott waves":      {"cs_strat": ["st_elliott"]},
}
LIST_KEYS = ("cs_rsi", "cs_mom_a", "cs_mom_v", "cs_pat", "cs_strat")
SEL_DEFAULTS = {"cs_stack": "—", "cs_side": "Both", "cs_mode": "All selected"}
ALL_KEYS = LIST_KEYS + tuple(SEL_DEFAULTS)


def split_moves(move_filters):
    """MOVE_FILTERS (chg_* and vol_*) -> (momentum keys, volume keys)."""
    return [k for k in move_filters if k.startswith("chg_")], [k for k in move_filters if k.startswith("vol_")]


def user_presets(path=None):
    try:
        with open(path or PRESET_PATH, encoding="utf-8") as f:
            d = json.load(f)
        return {str(k): v for k, v in d.items() if isinstance(v, dict)}
    except Exception:
        return {}


def all_presets(path=None):
    out = dict(BUILTIN)
    for k, v in user_presets(path).items():
        out["★ " + k] = v   # a star marks the user's own
    return out


def apply(ss, name, presets=None):
    """Set the filter widget keys in `ss` (a dict-like, st.session_state) from preset `name`; returns True if applied. Call it from an on_change callback."""
    P = presets if presets is not None else all_presets()
    if name not in P:
        return False
    for k in LIST_KEYS:
        ss[k] = []
    for k, v in SEL_DEFAULTS.items():
        ss[k] = v
    for k, v in P[name].items():
        if k in ALL_KEYS:
            ss[k] = list(v) if k in LIST_KEYS else v
    return True


def snapshot(ss):
    """Current filter choices -> a preset dict (only non-default values)."""
    out = {}
    for k in LIST_KEYS:
        if ss.get(k):
            out[k] = list(ss[k])
    for k, d in SEL_DEFAULTS.items():
        if ss.get(k, d) != d:
            out[k] = ss[k]
    return out


def save_user(name, snap, path=None):
    """Save the user's own preset (name cleaned, max 40 chars). Returns (ok, message)."""
    name = re.sub(r"\s+", " ", str(name or "")).strip()[:40]
    if not name or name.startswith("★"):
        return False, "Give the preset a name"
    if not snap:
        return False, "Nothing selected to save"
    p = path or PRESET_PATH
    cur = user_presets(p)
    cur[name] = snap
    try:
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=1)
    except Exception as e:
        return False, f"Could not save ({type(e).__name__})"
    return True, "Saved"


def delete_user(name, path=None):
    p = path or PRESET_PATH
    cur = user_presets(p)
    if cur.pop(str(name).lstrip("★ ").strip(), None) is None:
        return False
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False
