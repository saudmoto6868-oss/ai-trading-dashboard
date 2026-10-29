"""Research pages in the REAL app (AppTest, network blocked): the four Stats tabs (Monte Carlo, Edge Map, Robustness, Execution) and the sidebar lab (Micro) open without an
exception; the sidebar offers ONLY Micro (Monte Carlo / Robustness live in Stats, no duplicates); the DEMO banner is injected into every mock page.
Run: PYTHONPATH=. python tests/test_research_labs_app.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import requests  # noqa: E402


def _fail(*a, **k):
    raise requests.exceptions.ConnectionError("blocked in test")


requests.get = _fail
requests.post = _fail
requests.Session.request = _fail
from streamlit.testing.v1 import AppTest  # noqa: E402
from modules.lab_banner import with_demo_banner  # noqa: E402

h = with_demo_banner("<html><body class='x'><p>hi</p></body></html>")
assert h.index("demo-banner") > h.index("<body") and h.index("demo-banner") < h.index("<p>hi</p>"), h
assert "DEMO" in h and "not evidence" in h and with_demo_banner("<p>no body</p>").startswith("<div")
for f in ("edge_map_app", "robustness_app", "execution_app", "micro_foundations"):
    src = open(os.path.join(ROOT, "modules", f + ".html"), encoding="utf8").read()
    assert 'id="demo-banner"' in with_demo_banner(src), f
mc = open(os.path.join(ROOT, "modules", "montecarlo_app.html"), encoding="utf8").read()
assert 'id="demo-banner"' in mc and "runSimulation, 200" not in mc

for tab in ("Monte Carlo", "Edge Map", "Robustness", "Execution"):
    at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
    at.session_state["page"] = 4
    at.session_state["stats_tab"] = tab
    at.run()
    assert not at.exception, (tab, [str(e.value)[:200] for e in at.exception])
    assert not at.error, (tab, [str(e.value)[:200] for e in at.error])
    print("ok stats tab:", tab)

at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
at.run()
labs = [r for r in at.sidebar.radio if r.key == "lab_choice"]
assert labs and list(labs[0].options) == ["—", "⬡ Micro · Foundations"], [list(r.options) for r in at.sidebar.radio]
at.session_state["lab_choice"] = "⬡ Micro · Foundations"
at.run()
assert not at.exception and not at.error
print("ok research labs in the real app")
