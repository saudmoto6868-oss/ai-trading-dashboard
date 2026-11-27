"""Spot brain key view (spot_brain_view.render_key): one screen, no page scroll. Reuses the synthetic brain fixture of
tests/test_spot_brain.py (it runs its asserts on import). Writes the page to $SPOT_KEY_OUT (optional) for a browser check."""
import importlib.util
import io
import contextlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from modules import spot_brain_view as V

spec = importlib.util.spec_from_file_location("tsb", os.path.join(HERE, "test_spot_brain.py"))
tsb = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(tsb)

markets = [{"name": "الدهب", "price": tsb.px, "wk": 1.0, "score": 20}]
h = V.render_key(tsb.br, markets)
assert h.count('class="kc"') >= 8, h.count('class="kc"')
for lab in ("يوم-3", "أسبوع-4", "شهر-3", "6-12 شهر"):
    assert lab in h, lab
assert "القرار" in h and "العقل المدبر" in h and 'dir="rtl"' in h
assert "None" not in h and "undefined" not in h
assert "مش أمر تنفيذ" in h
out = os.environ.get("SPOT_KEY_OUT") or os.path.join(tempfile.gettempdir(), "spot_key_view_test.html")
with open(out, "w", encoding="utf8") as fh:
    fh.write(h)
print("test_spot_key_view OK")
