"""Tests for modules/validation_lab.py — plain Python, no pytest needed.
Run: python3 tests/test_validation_lab.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

# ── make sure repo root is on sys.path ────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── minimal fake Streamlit so we can import without a running server ──────────
def _make_fake_st():
    st = MagicMock()
    st.columns.return_value = [MagicMock() for _ in range(7)]
    st.selectbox.side_effect = lambda label, opts, **kw: opts[0]
    return st

# ── helpers ───────────────────────────────────────────────────────────────────
def _make_lab_json(rows: list) -> str:
    return json.dumps({"rows": rows})


SAMPLE_ROWS = [
    # edge-confirmed
    {"key": "fib_ret", "school": "Fibonacci", "tf": "all", "side": "all",
     "n": 80, "win": 55.0, "avgR": 0.12, "sumR": 9.6, "base_win": 40.0,
     "base_avgR": 0.01, "edge": True},
    # positive ev
    {"key": "rsi_div", "school": "Momentum / divergence", "tf": "all", "side": "all",
     "n": 141, "win": 42.6, "avgR": 0.05, "sumR": 7.0, "base_win": 36.9,
     "base_avgR": 0.008, "edge": False},
    # OFF candidate
    {"key": "vwap", "school": "Levels / breakouts", "tf": "all", "side": "all",
     "n": 1301, "win": 34.0, "avgR": -0.074, "sumR": -96.3, "base_win": 38.5,
     "base_avgR": 0.012, "edge": False},
    # weak (n < 30)
    {"key": "new_det", "school": "SMC / ICT", "tf": "all", "side": "all",
     "n": 10, "win": 60.0, "avgR": 0.2, "sumR": 2.0, "base_win": 38.0,
     "base_avgR": 0.01, "edge": False},
    # non-all side — should be filtered out
    {"key": "fib_ret", "school": "Fibonacci", "tf": "all", "side": "long",
     "n": 50, "win": 50.0, "avgR": 0.08, "sumR": 4.0, "base_win": 38.0,
     "base_avgR": 0.01, "edge": False},
]

PASS = 0
FAIL = 0


def ok(name):
    global PASS
    PASS += 1
    print(f"  ✓ {name}")


def fail(name, msg):
    global FAIL
    FAIL += 1
    print(f"  ✗ {name}: {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: _load_rows returns only side=="all" rows
# ─────────────────────────────────────────────────────────────────────────────
def test_load_rows_filters_side():
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
        f.write(_make_lab_json(SAMPLE_ROWS))
        path = f.name
    try:
        import modules.validation_lab as vl
        orig = vl._LAB_PATH
        vl._LAB_PATH = Path(path)
        rows = vl._load_rows()
        vl._LAB_PATH = orig
        all_side = [r for r in rows if r.get("side") == "all"]
        if len(rows) == len(all_side) == 4:
            ok("_load_rows filters to side==all only")
        else:
            fail("_load_rows", f"expected 4, got {len(rows)}")
    finally:
        os.unlink(path)


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: _load_rows returns [] on missing file
# ─────────────────────────────────────────────────────────────────────────────
def test_load_rows_missing_file():
    import modules.validation_lab as vl
    orig = vl._LAB_PATH
    vl._LAB_PATH = Path("/nonexistent/path/x.json")
    rows = vl._load_rows()
    vl._LAB_PATH = orig
    if rows == []:
        ok("_load_rows returns [] on missing file")
    else:
        fail("_load_rows missing", f"expected [], got {rows}")


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: _tier classification
# ─────────────────────────────────────────────────────────────────────────────
def test_tier_classification():
    import modules.validation_lab as vl
    cases = [
        ({"n": 10, "avgR": 0.5, "edge": False}, "weak"),
        ({"n": 80, "avgR": 0.12, "edge": True}, "edge"),
        ({"n": 1301, "avgR": -0.074, "edge": False}, "off"),
        ({"n": 141, "avgR": 0.05, "edge": False}, "positive"),
        ({"n": 50, "avgR": -0.03, "edge": False}, "negative"),
        ({"n": 50, "avgR": 0.0, "edge": False}, "neutral"),
    ]
    all_ok = True
    for row, expected in cases:
        got = vl._tier(row)
        if got != expected:
            fail(f"_tier {row}", f"expected {expected}, got {got}")
            all_ok = False
    if all_ok:
        ok("_tier classification (6 cases)")


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: render_validation_lab doesn't crash with real lab file
# ─────────────────────────────────────────────────────────────────────────────
def test_render_no_crash():
    fake_st = _make_fake_st()
    fake_ui = MagicMock()
    fake_ui.strip.return_value = "<div>strip</div>"

    with patch.dict("sys.modules", {
        "streamlit": fake_st,
        "modules.ui_kit": fake_ui,
    }):
        import importlib
        import modules.validation_lab as vl
        importlib.reload(vl)
        try:
            vl.render_validation_lab()
            ok("render_validation_lab() runs without exception (real lab file)")
        except Exception as exc:
            fail("render_validation_lab", str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: render shows info message when lab file missing
# ─────────────────────────────────────────────────────────────────────────────
def test_render_no_data_shows_info():
    fake_st = _make_fake_st()
    info_calls = []
    fake_st.info.side_effect = lambda msg: info_calls.append(msg)
    fake_ui = MagicMock()
    fake_ui.strip.return_value = ""

    with patch.dict("sys.modules", {
        "streamlit": fake_st,
        "modules.ui_kit": fake_ui,
    }):
        import importlib
        import modules.validation_lab as vl
        importlib.reload(vl)
        orig = vl._LAB_PATH
        vl._LAB_PATH = Path("/no/such/file.json")
        vl.render_validation_lab()
        vl._LAB_PATH = orig
        if info_calls:
            ok("render shows info message when lab file missing")
        else:
            fail("render no-data", "expected st.info() call, got none")


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: summary counts are correct
# ─────────────────────────────────────────────────────────────────────────────
def test_summary_counts():
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
        f.write(_make_lab_json(SAMPLE_ROWS))
        path = f.name
    try:
        import modules.validation_lab as vl
        orig = vl._LAB_PATH
        vl._LAB_PATH = Path(path)
        rows = vl._load_rows()  # 4 all-side rows
        total = len(rows)
        ev_pos = sum(1 for r in rows if r.get("n", 0) >= vl._MIN_N and r.get("avgR", 0) > vl._POS_MIN_R)
        off_count = sum(1 for r in rows if r.get("n", 0) >= vl._OFF_MIN_N and r.get("avgR", 0) <= vl._OFF_MAX_R)
        edge_count = sum(1 for r in rows if r.get("edge"))
        vl._LAB_PATH = orig

        if total == 4 and ev_pos == 2 and off_count == 1 and edge_count == 1:
            ok("summary counts: total=4, ev_pos=2, off=1, edge=1")
        else:
            fail("summary counts", f"total={total} ev_pos={ev_pos} off={off_count} edge={edge_count}")
    finally:
        os.unlink(path)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("── test_validation_lab ──────────────────────────────────────────")
    test_load_rows_filters_side()
    test_load_rows_missing_file()
    test_tier_classification()
    test_render_no_crash()
    test_render_no_data_shows_info()
    test_summary_counts()
    print(f"\n{'OK' if FAIL == 0 else 'FAILED'}  {PASS} passed, {FAIL} failed")
    sys.exit(0 if FAIL == 0 else 1)
