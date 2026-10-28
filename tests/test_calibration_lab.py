"""Tests for modules/calibration_lab.py — plain Python.
Run: python3 tests/test_calibration_lab.py
"""
import sys, json, os, tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = FAIL = 0
def ok(n): global PASS; PASS += 1; print(f"  ✓ {n}")
def fail(n, m): global FAIL; FAIL += 1; print(f"  ✗ {n}: {m}")

def _fake_st():
    st = MagicMock()
    st.columns.return_value = [MagicMock() for _ in range(6)]
    st.selectbox.side_effect = lambda label, opts, **kw: opts[0] if opts else ""
    return st

ROWS = [
    {"key":"rsi_div","school":"Mom","tf":"all","side":"all","n":141,"win":42.6,"avgR":0.05,"sumR":7.0,"base_win":36.9,"base_avgR":0.008,"edge":False,"is_avgR":0.08,"oos_avgR":0.02},
    {"key":"vwap",   "school":"Lvl","tf":"all","side":"all","n":1301,"win":34.0,"avgR":-0.074,"sumR":-96.3,"base_win":38.5,"base_avgR":0.012,"edge":False},
    {"key":"rsi_div","school":"Mom","tf":"1h", "side":"all","n":60, "win":45.0,"avgR":0.09,"sumR":5.4,"base_win":38.0,"base_avgR":0.01,"edge":False},
    {"key":"rsi_div","school":"Mom","tf":"4h", "side":"all","n":35, "win":40.0,"avgR":0.03,"sumR":1.0,"base_win":38.0,"base_avgR":0.01,"edge":False},
]

def _with_tmp(rows):
    f = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
    json.dump({"rows": rows}, f); f.close()
    return f.name


def test_overfit_flag():
    from modules.calibration_lab import _overfit_flag
    assert _overfit_flag({"is_avgR": 0.10, "oos_avgR": 0.02}) == "⚠️"
    assert _overfit_flag({"is_avgR": 0.10, "oos_avgR": 0.08}) == "✅"
    assert _overfit_flag({"avgR": 0.05}) == ""
    ok("_overfit_flag (3 cases)")

def test_tf_table():
    from modules.calibration_lab import _tf_table
    res = _tf_table("rsi_div", ROWS)
    assert len(res) == 2
    assert res[0]["tf"] == "1h"   # higher avgR first
    ok("_tf_table returns per-tf rows sorted by avgR")

def test_render_no_crash():
    path = _with_tmp(ROWS)
    fake_st = _fake_st()
    fake_ui = MagicMock(); fake_ui.strip.return_value = "<div/>"
    fake_i18n = MagicMock(); fake_i18n.L.side_effect = lambda a, e="": a
    fake_shared = MagicMock()
    fake_shared.load_rows.return_value = ROWS
    fake_shared.tier.side_effect = lambda r: "positive"
    fake_shared.fmt_r.side_effect = lambda v: f"{v:+.3f}" if v else "—"
    fake_shared.TIER_ICON = {"positive": "✅"}
    fake_shared.MIN_N = 30
    fake_shared.no_data_msg = lambda *a: None
    with patch.dict("sys.modules", {"streamlit": fake_st, "modules.ui_kit": fake_ui,
                                     "modules.i18n": fake_i18n, "modules.lab_shared": fake_shared}):
        import importlib
        import modules.calibration_lab as cl
        importlib.reload(cl)
        try:
            cl.render_calibration_lab()
            ok("render_calibration_lab() runs without exception")
        except Exception as e:
            fail("render", str(e))
    os.unlink(path)

def test_render_no_data():
    fake_st = _fake_st()
    fake_ui = MagicMock(); fake_ui.strip.return_value = ""
    fake_i18n = MagicMock(); fake_i18n.L.side_effect = lambda a, e="": a
    fake_shared = MagicMock()
    fake_shared.load_rows.return_value = []
    fake_shared.no_data_msg = MagicMock()
    fake_shared.TIER_ICON = {}; fake_shared.MIN_N = 30
    with patch.dict("sys.modules", {"streamlit": fake_st, "modules.ui_kit": fake_ui,
                                     "modules.i18n": fake_i18n, "modules.lab_shared": fake_shared}):
        import importlib
        import modules.calibration_lab as cl
        importlib.reload(cl)
        cl.render_calibration_lab()
        if fake_shared.no_data_msg.called:
            ok("render shows no-data message when rows empty")
        else:
            fail("no-data", "no_data_msg not called")

if __name__ == "__main__":
    print("── test_calibration_lab ─────────────────────────────────────────")
    test_overfit_flag()
    test_tf_table()
    test_render_no_crash()
    test_render_no_data()
    print(f"\n{'OK' if FAIL==0 else 'FAILED'}  {PASS} passed, {FAIL} failed")
    sys.exit(0 if FAIL==0 else 1)
