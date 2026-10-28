"""Validation Lab in the REAL app (AppTest, network blocked, NO mocked app functions): the Stats page > 'Validation Lab' tab must render without any st.error / exception.
(test_validation_lab.py mocked modules.i18n.L with a 2-argument function; the real L() takes one, so that test could not see the crash.) Run: python tests/test_validation_lab_app.py"""
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

for lang in ("en", "ar"):
    at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
    at.session_state["page"] = 4
    at.session_state["stats_tab"] = "Validation Lab"
    at.session_state["ws_lang"] = lang
    at.run()
    assert not at.exception, [str(e.value)[:200] for e in at.exception]
    assert not at.error, [str(e.value)[:200] for e in at.error]
    assert len(at.dataframe) == 1, f"the table must be ONE dataframe element, got {len(at.dataframe)}"
    assert len(at.markdown) < 60, f"too many elements ({len(at.markdown)}): the table must not be a per-row loop"
    md = " ".join(m.value for m in at.markdown if isinstance(m.value, str))
    assert "Positive EV" not in md and "دليل إيجابي" not in md, "the unproven 'positive' wording must be gone"
    print("ok validation lab in the real app:", lang, "dataframe rows:", len(at.dataframe[0].value))
