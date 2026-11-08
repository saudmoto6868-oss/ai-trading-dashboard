"""The sidebar shows which commit the running app was built from (real app, AppTest, network blocked). Run: PYTHONPATH=. python tests/test_build_stamp_app.py"""
import os
import re
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

at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
at.run()
assert not at.exception and not at.error
caps = [c.value for c in at.sidebar.caption if c.value.startswith("Build:") or "Build" in c.value]
assert caps and (re.search(r"[0-9a-f]{7} · \d{4}-\d\d-\d\d", caps[0]) or caps[0].endswith("unknown")), caps
print("ok build stamp:", caps[0])
