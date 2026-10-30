"""Academy > Lab tools (real app, AppTest, network blocked): the tab opens, every lesson renders, no exception, and the lessons say the facts the code has (no 'gate', Lab Summary).
Run: PYTHONPATH=. python tests/test_academy_lab_tools_app.py"""
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
from modules import calibration_lab as CAL, lab_shared as LS  # noqa: E402

vis = os.path.join(ROOT, "docs", "academy", "visual")
txt = {k: open(os.path.join(vis, k + ".md"), encoding="utf8").read() for k in ("10-validation-lab", "11-calibration", "12-rotation", "13-evidence-summary")}
assert f"{CAL._GAP}R" in txt["11-calibration"] and str(LS.MIN_N) in txt["10-validation-lab"] and "Lab Summary" in txt["10-validation-lab"]
assert "بوابة" not in txt["13-evidence-summary"].replace("مفيش بوابة", "") and "0.10R" in txt["13-evidence-summary"] and "-0.06" not in txt["12-rotation"]
for k in txt:
    assert "Decision Gate" not in txt[k] and "تبويب" not in txt[k].split("\n")[0], k
for lang in ("en", "ar"):
    for pick in txt:
        at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
        at.session_state["page"] = 7
        at.session_state["ac_view"] = "Lab tools"
        at.session_state["ac_lab_pick"] = pick
        at.session_state["ws_lang"] = lang
        at.run()
        assert not at.exception, (lang, pick, [str(e.value)[:200] for e in at.exception])
        assert not at.error, (lang, pick, [str(e.value)[:200] for e in at.error])
    print("ok academy lab tools:", lang)
