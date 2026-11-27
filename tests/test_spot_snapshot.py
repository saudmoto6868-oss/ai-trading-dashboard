"""Spot desk snapshot for the Workspace (owner 2026-11-15). Synthetic desk + brain only; no network.
Run: python3 tests/test_spot_snapshot.py"""
import datetime as dt
import json
import os
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import spot_snapshot as S  # noqa: E402

desk = {"ideas": [{"asset": "GOLD", "name": "الدهب", "kind": "buy", "title": "شراء", "entry": (2300.0, 2310.0), "stop": np.float64(2280.0),
                   "targets": [2350.0, 2400.0], "rr": 2.5, "conf": 4, "pros": ["دعم شهري"], "cons": ["دولار قوي"]}],
        "log": ["الدهب: 3 مدد"], "markets": [{"asset": "GOLD", "name": "الدهب", "price": np.float64(2305.5), "wk": 1.2, "score": 3, "zone": "support",
                                              "news": 0, "spark": list(np.linspace(2200, 2305, 60)), "n_ideas": 1}],
        "news": [{"title": "x"}], "risk_off": np.int64(1)}
brain = {"asset": "GOLD", "price": 2305.5, "head": "شراء على المدى المتوسط", "horizons": {"day": {"label": "يوم", "tf": "1D", "score": -10, "verdict": "wait",
          "verdict_ar": "استنى", "reasons": ["ضغط"], "levels": {"x": 1}}}, "flow": {"ok": True}, "inst": {}, "news": {"score": 0, "items": []}, "guard": [],
         "ideas": [], "stats": {}, "setups": [{"id": "s1", "school_ar": "كلاسيك", "name": "كوب", "side": "buy", "tf": "1W", "entry": [1, 2], "stop": 0.5,
                                               "targets": [3], "ev_label": "t 3.2 n 41", "extra_big": "drop me"}]}
snap = S.build(desk, [brain, {"no_asset": True}], now=dt.datetime(2026, 11, 15, 5, 0, tzinfo=dt.timezone.utc))
assert snap["generated"] == "2026-11-15T05:00:00Z" and len(snap["brains"]) == 1, snap.get("generated")
assert snap["ideas"][0]["stop"] == 2280.0 and snap["ideas"][0]["targets"] == [2350.0, 2400.0]
assert len(snap["markets"][0]["spark"]) == 52 and snap["risk_off"] == 1
st = snap["brains"][0]["setups"][0]
assert "extra_big" not in st and st["ev_label"] == "t 3.2 n 41", st
json.dumps(snap, ensure_ascii=False)   # must be pure JSON

with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "sub", "snapshot.json")
    S.write(snap, p)
    assert S.load(p)["brains"][0]["asset"] == "GOLD"
    assert S.load(os.path.join(d, "missing.json")) == {}
    open(p, "w").write("{broken")
    assert S.load(p) == {}

from modules import workspace as W  # noqa: E402
html = W.build_workspace_html(["BTC-USDT"])
assert '"spot":' in html and "build_spot" in html and "مكتب السبوت" in html
print("ok spot snapshot: JSON-clean, setups keep evidence, broken/missing file -> {}, Workspace embeds it and has the widget")

# ideas log: each idea once per day, outcome measured later (not decided here)
with tempfile.TemporaryDirectory() as d:
    lp = os.path.join(d, "ideas_log.jsonl")
    snap2 = {"generated": "2026-11-15T05:00:00Z", "ideas": [{"asset": "GOLD", "kind": "buy", "horizon": "أسابيع لشهور", "entry": (2300.0, 2310.0), "stop": 2280.0, "targets": [2350.0], "rr": 2.5, "conf": 4},
                                                              {"asset": "BTC", "kind": "avoid", "entry": None, "stop": None}]}
    assert S.append_log(snap2, lp) == 1
    assert S.append_log(snap2, lp) == 0                     # same day, same idea: not repeated
    assert S.append_log({**snap2, "generated": "2026-11-16T05:00:00Z"}, lp) == 1   # next day: a new row
    rows_ = [json.loads(x) for x in open(lp, encoding="utf-8")]
    assert len(rows_) == 2 and rows_[0]["entry"] == [2300.0, 2310.0] and "outcome" not in rows_[0]
print("ok ideas log: once per day, no outcome written (measured later)")
