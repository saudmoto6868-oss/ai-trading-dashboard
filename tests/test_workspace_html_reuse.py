"""The Workspace iframe reloads whenever its HTML string changes, so render_workspace must reuse the last HTML while the
layout is the same, the scan is still running (up to the max age), and the data is not yet due for a refresh.
Streamlit is replaced by a small fake so this runs without a server."""
import os, sys, types
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

sent = []
state = {}
fake_st = types.ModuleType("streamlit")
fake_st.session_state = state
fake_components = types.ModuleType("streamlit.components.v1")
fake_components.html = lambda doc, height=None, scrolling=None: sent.append(doc)
sys.modules["streamlit"] = fake_st
sys.modules["streamlit.components"] = types.ModuleType("streamlit.components")
sys.modules["streamlit.components.v1"] = fake_components

from modules import workspace as W

builds = []
clock = {"t": 1000.0}
W.time = types.SimpleNamespace(time=lambda: clock["t"])


def fake_build(symbols, news, lang, **kw):
    builds.append(kw.get("scanning"))
    return f"<html>{len(builds)}</html>"


W.build_workspace_html = fake_build
W._fh_token = lambda: ""


def render(scanning=False, syms=("BTC-USDT",)):
    W.render_workspace(list(syms), None, "en", height=800, scanning=scanning)
    return sent[-1]


def test_first_render_builds_and_sends():
    state.clear(); sent.clear(); builds.clear()
    assert render() == "<html>1</html>" and len(builds) == 1


def test_same_layout_within_refresh_window_reuses_html():
    clock["t"] += 10
    assert render() == "<html>1</html>" and len(builds) == 1


def test_scanning_keeps_old_html_until_max_age():
    clock["t"] += W.WS_HTML_REFRESH_SECS          # due for refresh, but a scan is running -> keep showing the old page
    assert render(scanning=True) == "<html>1</html>" and len(builds) == 1
    clock["t"] += W.WS_HTML_MAX_SECS                # too old even for a running scan -> rebuild
    assert render(scanning=True) == "<html>2</html>" and len(builds) == 2


def test_idle_scan_refreshes_after_interval():
    state.clear(); sent.clear(); builds.clear()
    render()
    clock["t"] += W.WS_HTML_REFRESH_SECS
    assert render() == "<html>2</html>" and len(builds) == 2


def test_layout_change_rebuilds_at_once():
    clock["t"] += 1
    assert render(syms=("ETH-USDT",)) == "<html>3</html>"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
