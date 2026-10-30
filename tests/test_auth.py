"""Item 22: login gate - off by default, shared password, named users, lock-out. Run: python tests/test_auth.py"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import auth  # noqa: E402

for k in ("APP_PASSWORD", "APP_USERS"):
    os.environ.pop(k, None)
assert auth.users() == {}                                    # nothing set -> gate off
os.environ["APP_PASSWORD"] = "s3cret"
t = auth.users()
assert t == {"": "s3cret"} and auth.check("", "s3cret", t) and not auth.check("", "nope", t) and auth.check("anyone", "s3cret", t)
os.environ["APP_USERS"] = "Saud:abc, ali:xyz ,bad"
t = auth.users()
assert t["saud"] == "abc" and t["ali"] == "xyz" and "bad" not in t
assert auth.check("SAUD", "abc", t) and not auth.check("saud", "xyz", t) and auth.check("", "s3cret", t)
os.environ.pop("APP_PASSWORD")
assert not auth.check("", "abc", auth.users()) and not auth.check("ghost", "abc", auth.users())

# the real app: locked page shows only the form; right password opens it; 5 wrong tries lock for 60 s
import requests  # noqa: E402
requests.get = requests.post = requests.request = lambda *a, **k: (_ for _ in ()).throw(requests.ConnectionError("offline test"))
requests.Session.request = lambda self, *a, **k: (_ for _ in ()).throw(requests.ConnectionError("offline test"))
from streamlit.testing.v1 import AppTest  # noqa: E402
os.environ.pop("APP_USERS"); os.environ["APP_PASSWORD"] = "s3cret"
import re
_N_PAGES = len(eval(re.search(r"_PAGE_ORDER = (\[[^\]]*\])", open(os.path.join(os.path.dirname(__file__), "..", "main.py"), encoding="utf8").read()).group(1)))   # the page bar after login = the pages main.py lists (was a hard-coded 7: failed since the pages grew)
at = AppTest.from_file(os.path.join(os.path.dirname(__file__), "..", "main.py"), default_timeout=280)
at.run()
pages = lambda: [r for r in at.radio if r.key == "page"]   # the page selector (replaced st.tabs)
assert not at.exception and not pages() and len(at.text_input) == 1, (at.exception, len(pages()))
for i in range(5):
    at.text_input(key="auth_pw").input("wrong"); at.button[0].click(); at.run()
assert at.session_state["auth_lock"] > time.time()
at.run()
assert any("wait" in e.value for e in at.error) and not at.text_input, [e.value for e in at.error]
at.session_state["auth_lock"] = 0
at.run()
at.text_input(key="auth_pw").input("s3cret"); at.button[0].click(); at.run()
assert at.session_state["auth_ok"] and len(pages()) == 1 and len(pages()[0].options) == _N_PAGES and not at.exception, (at.exception,)
print("test_auth: all passed")
