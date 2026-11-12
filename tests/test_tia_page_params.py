"""Unit tests for modules/tia_page.py (render_tia) and modules/tia_workspace.py.

Tests query parameters: tia_mkt, tia_sym, tia_run, empty symbols warning,
ctrl payload construction, report caching, and workspace HTML injection.
Completely isolated: no network, no live Streamlit daemon, works offline.
Can be executed directly via:
    python3 tests/test_tia_page_params.py
or under pytest.
"""
from __future__ import annotations
import contextlib
import os
import sys
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Safely mock third-party dependencies in sys.modules if not installed or running offline
for mod_name in ["streamlit", "streamlit.components", "streamlit.components.v1", "requests", "numpy"]:
    try:
        __import__(mod_name)          # real package wins; the stub is used only when it cannot be imported
    except ImportError:
        sys.modules[mod_name] = MagicMock()

import modules.asset_classes
import modules.tia_intelligence
import modules.tia_workspace
import modules.tia_page as tia_page


class MockQueryParams(dict):
    """Dict-like container that supports .get() and del qp[k] like st.query_params."""
    def get(self, key, default=None):
        return super().get(key, default)


class MockStreamlit:
    """Mock streamlit runtime environment for render_tia tests."""
    def __init__(self, query_params: dict | None = None, session_state: dict | None = None):
        self.query_params = MockQueryParams(query_params or {})
        self.session_state = dict(session_state or {})
        self.warning = MagicMock()
        self.caption = MagicMock()
        self.markdown = MagicMock()
        self.subheader = MagicMock()
        self.write = MagicMock()
        self.metric = MagicMock()
        self.json = MagicMock()

    @contextlib.contextmanager
    def spinner(self, text=""):
        yield

    @contextlib.contextmanager
    def expander(self, label="", expanded=False):
        yield

    def columns(self, spec):
        n = spec if isinstance(spec, int) else len(spec)
        return [self._create_column_mock() for _ in range(n)]

    def _create_column_mock(self):
        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        return col


MOCK_CLASSES = ("Crypto", "Forex", "Commodities", "Indices")


def _run_render_tia_with_mocks(qp=None, ss=None, symbols=None, note=None, report=None):
    """Helper to run render_tia under isolated patches."""
    mock_st = MockStreamlit(query_params=qp, session_state=ss)
    symbols_list = ["BTC-USDT", "ETH-USDT", "SOL-USDT"] if symbols is None else symbols
    catalog = {"symbols": symbols_list}
    if note:
        catalog["note"] = note

    mock_symbols_for_class = MagicMock(return_value=catalog)
    mock_director_report = MagicMock(return_value=report or {
        "stance": "BULLISH",
        "director_summary": "Test summary",
        "technical": {"1h": {"status": "ok", "trend": "up", "rsi14": 55, "return20_pct": 2.5}},
        "sources": {"binance": {"status": "ok"}},
        "warnings": ["Low volume warning"],
        "flow": {},
        "options": {},
    })
    mock_render_workspace = MagicMock()

    with patch.object(tia_page, "st", mock_st), \
         patch("modules.asset_classes.CLASSES", MOCK_CLASSES), \
         patch("modules.tia_intelligence.symbols_for_class", mock_symbols_for_class), \
         patch("modules.tia_intelligence.director_report", mock_director_report), \
         patch("modules.tia_workspace.render_tia_workspace", mock_render_workspace):
        tia_page.render_tia()

    return {
        "st": mock_st,
        "mock_symbols_for_class": mock_symbols_for_class,
        "mock_director_report": mock_director_report,
        "mock_render_workspace": mock_render_workspace,
    }


def test_tia_mkt_valid_uses_specified_market():
    """1a. Valid tia_mkt in CLASSES is respected."""
    res = _run_render_tia_with_mocks(qp={"tia_mkt": "Forex"})
    res["mock_symbols_for_class"].assert_called_once_with("Forex", top=60)
    res["mock_render_workspace"].assert_called_once()
    kwargs = res["mock_render_workspace"].call_args.kwargs
    assert kwargs["universe"] == "Forex"
    assert kwargs["ctrl"]["market"] == "Forex"


def test_tia_mkt_invalid_or_missing_falls_back_to_default():
    """1b. Invalid or missing tia_mkt falls back to CLASSES[0]."""
    # Missing
    res1 = _run_render_tia_with_mocks(qp={})
    assert res1["mock_render_workspace"].call_args.kwargs["universe"] == MOCK_CLASSES[0]
    assert res1["mock_render_workspace"].call_args.kwargs["ctrl"]["market"] == MOCK_CLASSES[0]

    # Invalid
    res2 = _run_render_tia_with_mocks(qp={"tia_mkt": "UNKNOWN_PLANET"})
    assert res2["mock_render_workspace"].call_args.kwargs["universe"] == MOCK_CLASSES[0]
    assert res2["mock_render_workspace"].call_args.kwargs["ctrl"]["market"] == MOCK_CLASSES[0]


def test_tia_sym_valid_uses_specified_symbol():
    """2a. Valid tia_sym in symbols catalog is selected."""
    res = _run_render_tia_with_mocks(qp={"tia_sym": "ETH-USDT"})
    kwargs = res["mock_render_workspace"].call_args.kwargs
    assert kwargs["ctrl"]["selected"] == "ETH-USDT"
    # First symbol in symbols arg passed to workspace must be the selected symbol
    assert kwargs["symbols"][0] == "ETH-USDT"


def test_tia_sym_invalid_or_missing_falls_back_to_first():
    """2b. Invalid or missing tia_sym falls back to symbols[0]."""
    # Missing
    res1 = _run_render_tia_with_mocks(qp={})
    assert res1["mock_render_workspace"].call_args.kwargs["ctrl"]["selected"] == "BTC-USDT"

    # Invalid
    res2 = _run_render_tia_with_mocks(qp={"tia_sym": "DOGE_NONEXISTENT"})
    assert res2["mock_render_workspace"].call_args.kwargs["ctrl"]["selected"] == "BTC-USDT"


def test_tia_empty_symbols_shows_warning_and_returns():
    """3. If symbols catalog is empty, st.warning is displayed and workspace is NOT rendered."""
    res = _run_render_tia_with_mocks(symbols=[])
    res["st"].warning.assert_called_once_with(
        "No verified symbols are currently available for this tab. No placeholder prices will be shown."
    )
    res["mock_render_workspace"].assert_not_called()


def test_tia_run_executes_director_once_and_cleans_param():
    """4a. tia_run runs director_report exactly once, caches in session_state, and removes tia_run."""
    qp = {"tia_mkt": "Crypto", "tia_sym": "ETH-USDT", "tia_run": "1731234567"}
    ss = {}
    report_fixture = {"stance": "ACCUMULATE", "director_summary": "Bullish divergence"}

    res = _run_render_tia_with_mocks(qp=qp, ss=ss, report=report_fixture)

    # director_report called once with (selected, market)
    res["mock_director_report"].assert_called_once_with("ETH-USDT", "Crypto")

    # Stored in session_state under the expected key
    key = "tia_director_Crypto_ETH-USDT"
    assert res["st"].session_state[key] == report_fixture

    # tia_run is deleted from query_params
    assert "tia_run" not in res["st"].query_params


def test_tia_no_run_does_not_execute_director():
    """4b. When tia_run is not present, director_report is not executed."""
    res = _run_render_tia_with_mocks(qp={"tia_mkt": "Crypto", "tia_sym": "BTC-USDT"})
    res["mock_director_report"].assert_not_called()


def test_ctrl_structure_and_selected_first_in_symbols():
    """5. Verify ctrl payload structure and that selected symbol is placed first in workspace symbols."""
    symbols = ["SOL-USDT", "BTC-USDT", "ETH-USDT"]
    res = _run_render_tia_with_mocks(qp={"tia_mkt": "Crypto", "tia_sym": "BTC-USDT"}, symbols=symbols)
    call_kwargs = res["mock_render_workspace"].call_args.kwargs

    # Symbols passed to workspace has selected ("BTC-USDT") as the first item
    assert call_kwargs["symbols"] == ["BTC-USDT", "SOL-USDT", "ETH-USDT"]
    assert call_kwargs["symbols"][0] == "BTC-USDT"

    ctrl = call_kwargs["ctrl"]
    assert ctrl["markets"] == list(MOCK_CLASSES)
    assert ctrl["market"] == "Crypto"
    assert ctrl["symbols"] == symbols
    assert ctrl["selected"] == "BTC-USDT"
    assert "agents" in ctrl
    assert ctrl["agents"]["ran"] is False
    assert ctrl["agents"]["stance"] is None


def test_cached_report_reflects_in_ctrl_and_renders_ui():
    """6. When a report is already stored in session_state, ctrl shows ran=True and stance, and UI renders."""
    key = "tia_director_Crypto_BTC-USDT"
    cached_report = {
        "stance": "NEUTRAL",
        "director_summary": "Consolidation phase",
        "technical": {"15m": {"status": "ok", "trend": "range", "rsi14": 50, "return20_pct": 0.1}},
        "sources": {"binance": {"status": "ok"}},
        "warnings": ["Weekend liquidity drop"],
    }
    res = _run_render_tia_with_mocks(
        qp={"tia_mkt": "Crypto", "tia_sym": "BTC-USDT"},
        ss={key: cached_report}
    )

    ctrl = res["mock_render_workspace"].call_args.kwargs["ctrl"]
    assert ctrl["agents"]["ran"] is True
    assert ctrl["agents"]["stance"] == "NEUTRAL"

    # UI renders markdown and subheader for report
    res["st"].markdown.assert_any_call("### TIA Intelligence Director")
    res["st"].subheader.assert_called_with("NEUTRAL")
    res["st"].warning.assert_called_with("Weekend liquidity drop")


def test_tia_workspace_html_structure():
    """7 (Optional). Verify modules/tia_workspace.py generates script tags and isolated layout."""
    import modules.tia_workspace as tw

    base_html = (
        "<html><head></head><body>"
        "const WGROUPS = () => ["
        "/* the older layout (signals strip, 15 s + 5 m charts, scanner ...): phones, first visit only */"
        "Ws.builtinStandard = () => {"
        "<title>6868 X</title>"
        "ai_ws_v5"
        "</body></html>"
    )

    mock_components = MagicMock()
    mock_build_workspace_html = MagicMock(return_value=base_html)

    ctrl_sample = {
        "markets": ["Crypto", "Forex"],
        "market": "Crypto",
        "symbols": ["BTC-USDT"],
        "selected": "BTC-USDT",
        "agents": {"ran": True, "stance": "BULLISH"}
    }

    # Force options_desk import error to test fallback handling
    with patch.object(tw, "components", mock_components), \
         patch.object(tw, "build_workspace_html", mock_build_workspace_html), \
         patch.dict("sys.modules", {"modules.options_desk": None}):
        tw.render_tia_workspace(height=920, universe="Crypto", symbols=["BTC-USDT"], ctrl=ctrl_sample)

    mock_components.html.assert_called_once()
    rendered_doc = mock_components.html.call_args[0][0]

    # Verify TIA-specific markers are present
    assert "window.TIA_CTRL" in rendered_doc
    assert "tia_ws_v" in rendered_doc and "ai_ws_v5" not in rendered_doc   # TIA-only storage key (version bumps when the start layout changes)
    assert "Ws.builtinStandard = () => {" in rendered_doc
    assert "TIA Command Workspace" in rendered_doc
    assert "const TIA_OPTIONS = " in rendered_doc


import unittest


class TestTiaPageParams(unittest.TestCase):
    """TestCase wrapper enabling discovery by unittest as well as pytest."""
    def test_tia_mkt_valid(self):
        test_tia_mkt_valid_uses_specified_market()

    def test_tia_mkt_fallback(self):
        test_tia_mkt_invalid_or_missing_falls_back_to_default()

    def test_tia_sym_valid(self):
        test_tia_sym_valid_uses_specified_symbol()

    def test_tia_sym_fallback(self):
        test_tia_sym_invalid_or_missing_falls_back_to_first()

    def test_tia_empty_symbols(self):
        test_tia_empty_symbols_shows_warning_and_returns()

    def test_tia_run_execution(self):
        test_tia_run_executes_director_once_and_cleans_param()

    def test_tia_no_run(self):
        test_tia_no_run_does_not_execute_director()

    def test_ctrl_structure(self):
        test_ctrl_structure_and_selected_first_in_symbols()

    def test_cached_report(self):
        test_cached_report_reflects_in_ctrl_and_renders_ui()

    def test_workspace_html(self):
        test_tia_workspace_html_structure()


if __name__ == "__main__":
    test_functions = [
        test_tia_mkt_valid_uses_specified_market,
        test_tia_mkt_invalid_or_missing_falls_back_to_default,
        test_tia_sym_valid_uses_specified_symbol,
        test_tia_sym_invalid_or_missing_falls_back_to_first,
        test_tia_empty_symbols_shows_warning_and_returns,
        test_tia_run_executes_director_once_and_cleans_param,
        test_tia_no_run_does_not_execute_director,
        test_ctrl_structure_and_selected_first_in_symbols,
        test_cached_report_reflects_in_ctrl_and_renders_ui,
        test_tia_workspace_html_structure,
    ]

    print(f"Running {len(test_functions)} TIA page tests...")
    passed = 0
    for test_fn in test_functions:
        test_fn()
        passed += 1
        print(f"  ✓ {test_fn.__name__}")

    print(f"\nALL {passed} TESTS PASSED SUCCESSFULLY.")
