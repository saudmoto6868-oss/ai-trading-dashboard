"""The Stats > My journal page shows the luck check (Monte Carlo on the uploaded journal CSV) in the REAL app (AppTest, network blocked).
Run: PYTHONPATH=. python tests/test_journal_mc_app.py"""
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
import io  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from modules import perf_report as PR  # noqa: E402

rs = np.random.default_rng(5).normal(0.4, 1.0, 60).round(2)
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=60, freq="D").astype(str), "r": rs})
ret = PR.returns_from_trades(df, 1.0)
assert len(ret) == 60, len(ret)
from modules.mc_journal import mc_summary  # noqa: E402
mc = mc_summary(ret.values, seed=7)
assert mc["ok"] and mc["n"] == 60 and 0 <= mc["p_value"] <= 1 and mc["verdict"] in ("unlikely_luck", "could_be_luck"), mc
import streamlit as st  # noqa: E402
_csv = io.BytesIO(df.to_csv(index=False).encode())
_orig = st.file_uploader
st.file_uploader = lambda *a, **k: (io.BytesIO(_csv.getvalue()) if k.get("key") == "perf_csv" else _orig(*a, **k))   # AppTest cannot upload a file: feed the CSV to the page
from streamlit.testing.v1 import AppTest  # noqa: E402
at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
at.session_state["page"] = 4
at.session_state["stats_tab"] = "My journal"
at.run()
assert not at.exception, [str(e.value)[:200] for e in at.exception]
labs = [m.label for m in at.metric]
assert any("P-value" in l for l in labs) and any("Ruin" in l or "الخسارة" in l for l in labs), labs
print("ok real app shows the luck check:", [m.value for m in at.metric if "P-value" in m.label or "Ruin" in m.label])
src = open(os.path.join(ROOT, "main.py"), encoding="utf8").read()
assert "mc_summary as _mc_summary" in src and "Luck check" in src
print("ok journal Monte Carlo wired:", {k: mc[k] for k in ("n", "p_value", "ruin", "verdict")})
