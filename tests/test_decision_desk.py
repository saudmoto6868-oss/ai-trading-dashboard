"""Tests for modules/decision_desk.py — plain Python.
Run: python3 tests/test_decision_desk.py
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = FAIL = 0
def ok(n): global PASS; PASS += 1; print(f"  ✓ {n}")
def fail(n, m): global FAIL; FAIL += 1; print(f"  ✗ {n}: {m}")


def test_stars():
    from modules.decision_desk import _stars
    assert _stars(0) == "☆☆☆☆☆"
    assert _stars(3) == "★★★☆☆"
    assert _stars(5) == "★★★★★"
    assert _stars(9) == "★★★★★"   # clamped
    ok("_stars (4 cases)")


def test_gate():
    from modules.decision_desk import _gate
    # passes
    ok_res = {"direction": "bull", "stars": 3, "against": False}
    p, r = _gate(ok_res, 0.05)
    assert p is True and r == "", f"expected pass, got: p={p} r={r}"
    # blocked: neutral
    p, _ = _gate({"direction": "neutral", "stars": 3, "against": False}, 0.05)
    assert p is False
    # blocked: low stars
    p, _ = _gate({"direction": "bull", "stars": 1, "against": False}, 0.05)
    assert p is False
    # blocked: no evidence
    p, _ = _gate({"direction": "bull", "stars": 3, "against": False}, None)
    assert p is False
    # blocked: against
    p, _ = _gate({"direction": "bull", "stars": 3, "against": True}, 0.05)
    assert p is False
    ok("_gate (5 cases)")


def test_render_no_result():
    fake_st = MagicMock()
    info_calls = []
    fake_st.session_state = {}
    fake_st.info.side_effect = lambda m: info_calls.append(m)
    fake_ui = MagicMock(); fake_ui.strip.return_value = ""
    fake_i18n = MagicMock(); fake_i18n.L.side_effect = lambda a, e="": a
    fake_shared = MagicMock(); fake_shared.fmt_r = lambda v: "—"; fake_shared.no_data_msg = MagicMock()
    with patch.dict("sys.modules", {"streamlit": fake_st, "modules.ui_kit": fake_ui,
                                     "modules.i18n": fake_i18n, "modules.lab_shared": fake_shared}):
        import importlib
        import modules.decision_desk as dd
        importlib.reload(dd)
        dd.render_decision_desk()
        if info_calls:
            ok("render shows info when no last_result")
        else:
            fail("no-result", "st.info not called")


def test_render_with_result():
    res = {
        "symbol": "BTC-USDT", "timeframe": "1h",
        "direction": "bull", "stars": 3, "against": False,
        "signals": [{"key": "rsi_div", "name": "RSI Div", "family": "Momentum",
                     "direction": "bull", "icon": "📈"}],
        "htf": [{"tf": "4h", "available": True, "confirms": [], "trend_aligned": True}],
    }
    fake_st = MagicMock()
    fake_st.session_state = {"last_result": res}
    fake_st.columns.return_value = [MagicMock() for _ in range(4)]
    fake_st.expander.return_value.__enter__ = lambda s: s
    fake_st.expander.return_value.__exit__ = MagicMock(return_value=False)
    fake_ui = MagicMock(); fake_ui.strip.return_value = "<div/>"
    fake_i18n = MagicMock(); fake_i18n.L.side_effect = lambda a, e="": a
    fake_shared = MagicMock(); fake_shared.fmt_r = lambda v: f"{v:+.3f}" if v else "—"
    fake_tiers = MagicMock()
    fake_tiers.evidence.return_value = 0.08
    fake_tiers.off_keys.return_value = frozenset()
    fake_scorer = MagicMock()
    fake_scorer.scenarios.return_value = ["Scenario 1", "Scenario 2"]
    with patch.dict("sys.modules", {
        "streamlit": fake_st, "modules.ui_kit": fake_ui,
        "modules.i18n": fake_i18n, "modules.lab_shared": fake_shared,
        "modules.lab_tiers": fake_tiers, "modules.scorer": fake_scorer,
    }):
        import importlib
        import modules.decision_desk as dd
        importlib.reload(dd)
        try:
            dd.render_decision_desk()
            ok("render_decision_desk() runs with full result (no crash)")
        except Exception as e:
            fail("render_with_result", str(e))


if __name__ == "__main__":
    print("── test_decision_desk ───────────────────────────────────────────")
    test_stars()
    test_gate()
    test_render_no_result()
    test_render_with_result()
    print(f"\n{'OK' if FAIL==0 else 'FAILED'}  {PASS} passed, {FAIL} failed")
    sys.exit(0 if FAIL==0 else 1)
