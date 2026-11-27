"""Spot brain: only the inputs of the asked horizons are fetched (modules/spot_brain.run horizons=...).
Reuses the synthetic fixture of tests/test_spot_brain.py. Monkeypatched fetchers raise if called. Plain script."""
import contextlib
import importlib.util
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from modules import spot_brain, spot_flow, spot_inst, spot_ideas, spot_news, spot_setups

spec = importlib.util.spec_from_file_location("tsb", os.path.join(HERE, "test_spot_brain.py"))
tsb = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(tsb)

calls = []


def boom(name):
    def f(*a, **k):
        calls.append(name)
        raise AssertionError(f"{name} should not be fetched for this horizon")
    return f


# Patch every network fetcher to fail loudly.
spot_flow.fetch = boom("flow")
spot_inst.fetch = boom("cot")
spot_news.fetch = boom("news")

# 1) month only: needs COT + setups. Flow and news must NOT be fetched.
calls.clear()
r = spot_brain.run("GOLD", "metals", "الدهب", candles=tsb.get, cot=tsb.ct, horizons=("month",))
assert calls == [], calls
assert r["horizons_asked"] == ["month"] and r["raw_flow"] is None, r["horizons_asked"]
ok = 1

# 2) day only: needs flow + news + setups. COT must NOT be fetched.
spot_inst.fetch = boom("cot")
calls.clear()
r = spot_brain.run("GOLD", "metals", "الدهب", candles=tsb.get, flow=tsb.flow, news_items=[{"title": "x"}], horizons=("day",))
assert r["horizons_asked"] == ["day"] and r["raw_cot"] is None, r
assert "day" in r["horizons"]
ok += 1

# 3) default (no horizons) keeps the old behaviour: all four horizons and every input present.
spot_news.fetch = lambda *a, **k: []
spot_flow.fetch = lambda *a, **k: tsb.flow
spot_inst.fetch = lambda *a, **k: tsb.ct
r = spot_brain.run("GOLD", "metals", "الدهب", candles=tsb.get)
assert set(r["horizons"]) == {"day", "week", "month", "year"} and r["raw_cot"] is not None and r["raw_flow"] is not None
ok += 1

# 4) unknown horizon is refused, not silently ignored.
try:
    spot_brain.run("GOLD", "metals", "الدهب", candles=tsb.get, cot=tsb.ct, horizons=("scalp",))
    raise AssertionError("expected ValueError")
except ValueError:
    pass
ok += 1

print(f"test_spot_brain_lazy: {ok} groups passed")
