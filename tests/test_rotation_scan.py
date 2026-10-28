"""Tests for modules/rotation_scan.py — plain Python.
Run: python3 tests/test_rotation_scan.py
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = FAIL = 0
def ok(n): global PASS; PASS += 1; print(f"  ✓ {n}")
def fail(n, m): global FAIL; FAIL += 1; print(f"  ✗ {n}: {m}")

RESULTS = [
    {"symbol": "BTC-USDT", "signals": [{"key": "rsi_div"}, {"key": "fvg"}]},
    {"symbol": "ETH-USDT", "signals": [{"key": "sweep"}]},
    {"symbol": "HL:xau:XAUUSD", "signals": [{"key": "ob"}]},
    {"symbol": "HL:spx:SPX500", "signals": [{"key": "rsi_div"}]},
    {"symbol": "HL:eurusd:EURUSD", "signals": []},  # no signals
]


def test_class_of():
    from modules.rotation_scan import _class_of
    assert _class_of("BTC-USDT") == "Crypto"
    assert _class_of("HL:xau:XAUUSD") == "Metals"
    assert _class_of("HL:spx:SPX500") == "Indices"
    assert _class_of("HL:eurusd:EURUSD") == "Forex"
    assert _class_of("Y:AAPL") == "Stocks"
    assert _class_of("FH:EURUSD") == "Forex"
    ok("_class_of (6 cases)")


def test_summarise():
    from modules.rotation_scan import _summarise
    fake_shared = MagicMock()
    fake_shared.load_rows.return_value = [
        {"key": "rsi_div", "tf": "all", "side": "all", "n": 141, "avgR": 0.05, "edge": False},
    ]
    fake_shared.MIN_N = 30
    fake_shared.fmt_r = lambda v: f"{v:+.3f}" if v else "—"
    with patch.dict("sys.modules", {"modules.lab_shared": fake_shared}):
        import importlib
        import modules.rotation_scan as rs
        rs._EV_CACHE = {}  # reset cache
        importlib.reload(rs)
        b = rs._summarise(RESULTS)
        assert b["Crypto"]["count"] == 3      # BTC(2) + ETH(1)
        assert b["Metals"]["count"] == 1
        assert b["Indices"]["count"] == 1
        assert "Forex" not in b or b.get("Forex", {}).get("count", 0) == 0
        ok("_summarise counts signals per class")


def test_render_no_results():
    fake_st = MagicMock()
    info_calls = []
    fake_st.session_state = {}
    fake_st.info.side_effect = lambda m: info_calls.append(m)
    fake_ui = MagicMock(); fake_ui.strip.return_value = ""
    fake_i18n = MagicMock(); fake_i18n.L.side_effect = lambda a, e="": a
    fake_shared = MagicMock(); fake_shared.load_rows.return_value = []; fake_shared.MIN_N = 30
    fake_shared.fmt_r = lambda v: "—"
    with patch.dict("sys.modules", {"streamlit": fake_st, "modules.ui_kit": fake_ui,
                                     "modules.i18n": fake_i18n, "modules.lab_shared": fake_shared}):
        import importlib
        import modules.rotation_scan as rs
        importlib.reload(rs)
        rs.render_rotation_scan()
        if info_calls:
            ok("render shows info when no scan results")
        else:
            fail("no-results", "st.info not called")


def test_render_with_results():
    fake_st = MagicMock()
    fake_st.session_state = {"scan_results": RESULTS}
    fake_st.columns.return_value = [MagicMock() for _ in range(4)]
    fake_ui = MagicMock(); fake_ui.strip.return_value = "<div/>"
    fake_i18n = MagicMock(); fake_i18n.L.side_effect = lambda a, e="": a
    fake_shared = MagicMock()
    fake_shared.load_rows.return_value = []
    fake_shared.MIN_N = 30
    fake_shared.fmt_r = lambda v: "—"
    with patch.dict("sys.modules", {"streamlit": fake_st, "modules.ui_kit": fake_ui,
                                     "modules.i18n": fake_i18n, "modules.lab_shared": fake_shared,
                                     "pandas": __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()}):
        import importlib
        import modules.rotation_scan as rs
        rs._EV_CACHE = {}
        importlib.reload(rs)
        try:
            rs.render_rotation_scan()
            ok("render_rotation_scan() runs with results (no crash)")
        except Exception as e:
            fail("render_with_results", str(e))


if __name__ == "__main__":
    print("── test_rotation_scan ───────────────────────────────────────────")
    test_class_of()
    test_summarise()
    test_render_no_results()
    test_render_with_results()
    print(f"\n{'OK' if FAIL==0 else 'FAILED'}  {PASS} passed, {FAIL} failed")
    sys.exit(0 if FAIL==0 else 1)
