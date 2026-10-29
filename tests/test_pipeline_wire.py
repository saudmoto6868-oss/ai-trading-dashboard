"""
Tests for modules/pipeline_wire.py  (Item 25 step 3)
mock-tested only — no real lab data, no network.
"""
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── helpers ────────────────────────────────────────────────────────────────
def _make_lab(rows, tmp_dir):
    """Write a fake strategy_lab.json and monkey-patch LAB_PATH as Path."""
    from pathlib import Path
    import modules.pipeline_report as pr
    path = Path(tmp_dir) / "strategy_lab.json"
    data = {"meta": {}, "rows": rows, "conflicts": {}, "confluence": {}, "gann": {}}
    path.write_text(json.dumps(data))
    pr.LAB_PATH = path                       # redirect at module level (must be Path)
    return path


def _gate_row(key, avgR=0.10, n=200, t=4.0, is_avgR=0.09, oos_avgR=0.08):
    """A row that passes the strict gate."""
    return {"key": key, "tf": "1h", "side": "all", "school": "ICT",
            "n": n, "avgR": avgR, "t": t,
            "is_n": n//2, "is_avgR": is_avgR,
            "oos_n": n//2, "oos_avgR": oos_avgR, "edge": "edge"}


def _weak_row(key):
    """A row that fails the gate (n < GATE_N)."""
    return {"key": key, "tf": "1h", "side": "all", "school": "ICT",
            "n": 20, "avgR": 0.40, "t": 5.0,
            "is_n": 10, "is_avgR": 0.50,
            "oos_n": 10, "oos_avgR": 0.30, "edge": ""}


# ── tests ───────────────────────────────────────────────────────────────────
def test_empty_lab_returns_empty():
    """No lab data → pipeline_filters returns {}."""
    with tempfile.TemporaryDirectory() as d:
        _make_lab([], d)
        import modules.pipeline_wire as pw
        result = pw.pipeline_filters()
        assert result == {}, f"Expected empty dict, got {result}"
    print("PASS test_empty_lab_returns_empty")


def test_no_gate_winners_returns_empty():
    """All rows fail gate → pipeline_filters returns {}."""
    with tempfile.TemporaryDirectory() as d:
        _make_lab([_weak_row("level"), _weak_row("ob")], d)
        import importlib, modules.pipeline_wire as pw
        importlib.reload(pw)
        result = pw.pipeline_filters()
        assert result == {}, f"Expected empty dict, got {result}"
    print("PASS test_no_gate_winners_returns_empty")


def test_known_key_produces_filter():
    """A gate-passing row with a known key → one filter entry."""
    with tempfile.TemporaryDirectory() as d:
        _make_lab([_gate_row("level")], d)
        import importlib, modules.pipeline_wire as pw
        importlib.reload(pw)
        result = pw.pipeline_filters()
        assert "st_pip_level" in result, f"Missing st_pip_level in {list(result)}"
        label, matcher = result["st_pip_level"]
        assert "level" in label
        assert matcher == ("key", "level")
    print("PASS test_known_key_produces_filter")


def test_unknown_key_skipped():
    """A gate-passing row with a key not in _KEY_MAP is silently skipped."""
    with tempfile.TemporaryDirectory() as d:
        _make_lab([_gate_row("nonexistent_signal_xyz")], d)
        import importlib, modules.pipeline_wire as pw
        importlib.reload(pw)
        result = pw.pipeline_filters()
        assert all("nonexistent" not in k for k in result), result
    print("PASS test_unknown_key_skipped")


def test_multiple_winners_add_group_filter():
    """Two+ winners → st_pip_any group entry appears."""
    with tempfile.TemporaryDirectory() as d:
        _make_lab([_gate_row("level"), _gate_row("ob")], d)
        import importlib, modules.pipeline_wire as pw
        importlib.reload(pw)
        result = pw.pipeline_filters()
        assert "st_pip_any" in result, f"Missing st_pip_any in {list(result)}"
    print("PASS test_multiple_winners_add_group_filter")


def test_winner_keys_returns_list():
    """winner_keys() returns a list of gate-passing keys."""
    with tempfile.TemporaryDirectory() as d:
        _make_lab([_gate_row("level"), _weak_row("ob")], d)
        import importlib, modules.pipeline_wire as pw
        importlib.reload(pw)
        keys = pw.winner_keys()
        assert keys == ["level"], f"Expected ['level'], got {keys}"
    print("PASS test_winner_keys_returns_list")


def test_chart_scan_import_safe():
    """chart_scan.py imports without error when pipeline_wire returns {}."""
    import importlib
    import modules.chart_scan as cs
    importlib.reload(cs)
    assert "ALL_FILTERS" in dir(cs)
    print("PASS test_chart_scan_import_safe")


if __name__ == "__main__":
    test_empty_lab_returns_empty()
    test_no_gate_winners_returns_empty()
    test_known_key_produces_filter()
    test_unknown_key_skipped()
    test_multiple_winners_add_group_filter()
    test_winner_keys_returns_list()
    test_chart_scan_import_safe()
    print("\nAll 7 tests passed.")
