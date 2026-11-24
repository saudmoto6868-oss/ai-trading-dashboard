"""Preview page (22, Lab hub): every section renders in AppTest, network blocked, en + ar (buttons clicked in en only: AppTest cannot
match Arabic-formatted radios after a click). Run: PYTHONPATH=. python3 tests/test_unwired_preview_app.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT); os.chdir(ROOT)
import requests
def _fail(*a, **k): raise requests.exceptions.ConnectionError("blocked")
requests.get = _fail; requests.post = _fail; requests.Session.request = _fail
from streamlit.testing.v1 import AppTest
for pick in ["Edge Map", "Robustness Matrix", "Execution Cycle", "Veles Robustness Lab", "Signal comparison", "Wyckoff phases", "Momentum ranking", "Gann square of nine", "Libraries (no screen)"]:
    for lang in ("en", "ar"):
        at = AppTest.from_file(ROOT + "/main.py", default_timeout=300)
        at.session_state["page"] = 14; at.session_state["hub_14"] = 22; at.session_state["pv_pick"] = pick; at.session_state["ws_lang"] = lang
        at.run()
        if pick in ("Wyckoff phases", "Momentum ranking") and lang == "en":
            [b for b in at.button if b.key in ("pv_wy_go", "pv_mo_go")][0].click(); at.run()
        assert any("Preview: built but not shown" in m.value or "معاينة: حاجات متبنية ومش ظاهرة" in m.value for m in at.markdown), (pick, lang, "page 22 not rendered")
        assert not at.exception, (pick, lang, [str(e.value)[:200] for e in at.exception])
        errs = [str(e.value) for e in at.error if "ConnectionError" not in str(e.value)]   # Wyckoff fetches candles: blocked here
        assert not errs, (pick, lang, errs)
        print("ok", pick, lang)
print("ALL OK")
