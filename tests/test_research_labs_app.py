"""Research pages in the REAL app (AppTest, network blocked): the four Stats tabs (Monte Carlo, Edge Map, Robustness, Execution) and the sidebar lab (Micro) open without an
exception; the sidebar offers ONLY Micro + 2.6 Strategy Intelligence (Monte Carlo / Robustness live in Stats, no duplicates); the DEMO banner is injected into every mock page.
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
for f in ("edge_map_app", "execution_app", "micro_foundations"):   # Robustness now reads the real lab rows (no mock page)
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

at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)   # Robustness (real lab rows) lives in Research Hub > Plateau & regime
at.session_state["page"] = 9
at.session_state["hub_tab"] = "Plateau & regime"
at.run()
assert not at.exception and not at.error, ([str(e.value)[:200] for e in at.exception], [str(e.value)[:200] for e in at.error])
assert any("Strategy robustness" in str(h.value) or "متانة الاستراتيجيات" in str(h.value) for h in at.subheader), [str(h.value) for h in at.subheader]
assert at.dataframe or any("strategy_lab.json" in str(i.value) for i in at.info), "Robustness shows neither the lab table nor the no-data note"
assert any("Portfolio & drawdown simulator" in str(h.value) or "محاكي المحفظة" in str(h.value) for h in at.subheader), [str(h.value) for h in at.subheader]
print("ok research hub: robustness + portfolio simulator on real lab rows")

at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
at.run()
labs = [r for r in at.sidebar.radio if r.key == "lab_choice"]
assert labs and list(labs[0].options) == ["—", "⬡ Micro · Foundations", "2.6 Strategy Intelligence"], [list(r.options) for r in at.sidebar.radio]
at.session_state["lab_choice"] = "⬡ Micro · Foundations"
at.run()
assert not at.exception and not at.error
at.session_state["lab_choice"] = "2.6 Strategy Intelligence"
at.run()
assert not at.exception and not at.error, [str(e.value)[:200] for e in at.exception]
assert any("2.6 Strategy" in t.value for t in at.title), [t.value for t in at.title]
at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
at.run()
# 2026-11-15: 2.6 Lab moved from the top bar into the Lab hub (sub-tab row, key hub_14)
at.radio(key="page").set_value(14).run()
assert "2.6 Lab" in list(at.radio(key="hub_14").options), list(at.radio(key="hub_14").options)
at.radio(key="hub_14").set_value(19).run()
assert not at.exception and not at.error, [str(e.value)[:200] for e in at.exception]
assert any("2.6 Strategy" in t.value for t in at.title), [t.value for t in at.title]
print("ok 2.6 Lab top tab")
print("ok research labs in the real app")
