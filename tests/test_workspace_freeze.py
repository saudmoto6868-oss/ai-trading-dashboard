"""The Workspace page (iframe srcdoc) must be byte-identical between reruns while only slow feeds change (news ...), so the browser does not re-create the iframe;
it must change when something structural changes (symbols, scan state) and after the freeze time. Run: python tests/test_workspace_freeze.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from streamlit.testing.v1 import AppTest  # noqa: E402

SCRIPT = '''
import sys, time
sys.path.insert(0, %r)
import streamlit as st
from modules import workspace as W
n = st.session_state.setdefault("n", 0); st.session_state["n"] = n + 1
syms = ["BTC-USDT", "ETH-USDT"] + (["SOL-USDT"] if st.session_state.get("more") else [])
if st.session_state.get("age"): W.FREEZE_SECS = 0
W.render_workspace(syms, news=[{"headline": "headline %%d" %% n, "url": "https://x.com/a"}], lang="en", height=700, scanning=bool(st.session_state.get("scanning")))
'''


def srcdoc(at):
    return [e.proto.srcdoc for e in at.get("iframe")][0]


root = os.path.join(os.path.dirname(__file__), "..")
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
    f.write(SCRIPT % os.path.abspath(root))
at = AppTest.from_file(f.name, default_timeout=60).run()
assert not at.exception, at.exception
a = srcdoc(at)
at.run(); assert not at.exception; b = srcdoc(at)
assert a == b, "news changed between reruns but the Workspace page must stay byte-identical (frozen)"
at.session_state["scanning"] = True; at.run(); c = srcdoc(at)
assert c != b, "scan state is structural: the page must be rebuilt"
at.session_state["more"] = True; at.run(); d = srcdoc(at)
assert d != c and "SOL-USDT" in d, "symbols changed: the page must be rebuilt"
at.session_state["age"] = True; at.run(); e = srcdoc(at)
assert e != d, "after the freeze time the page is rebuilt (fresh news)"
print("ok workspace freeze")
