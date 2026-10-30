"""Hub core + Truth Court on hand-made numbers (plain script, like the other tests). Mock data only: not evidence of any edge."""
import sys, os, tempfile, json
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import hub_core, hub_truth

# --- promote(): every gate must hold ---
good = {"n": 250, "t": 3.8, "is_avgR": 0.12, "oos_avgR": 0.09, "net_avgR": 0.05}
assert hub_core.promote(good) == (True, [])
for patch, frag in (({"n": 60}, "n=60"), ({"t": 2.1}, "|t|"), ({"t": None}, "no t-stat"), ({"oos_avgR": -0.01}, "out-of-sample"),
                    ({"is_avgR": None}, "in-sample"), ({"net_avgR": -0.02}, "net of costs"), ({"net_avgR": None}, "costs not included")):
    ok, why = hub_core.promote({**good, **patch})
    assert not ok and any(frag in w for w in why), (patch, why)
ok, why = hub_core.promote(good, champion={"oos_avgR": 0.20})
assert not ok and "champion" in why[0]
assert hub_core.promote(good, champion={"oos_avgR": 0.01})[0]

# --- decay_cusum(): a faded edge alarms, a healthy one does not ---
healthy = [0.3, -1, 0.3, 0.3, -1, 0.3, 0.3, 0.3] * 5
assert not hub_core.decay_cusum(healthy, mu0=0.0, sigma=0.8)["alarm"]
faded = [-1.0] * 30
d = hub_core.decay_cusum(faded, mu0=0.2, sigma=0.8)
assert d["alarm"] and d["at"] is not None and d["at"] < 10
assert not hub_core.decay_cusum([1, 2], mu0=0, sigma=0)["alarm"]

# --- publish/read round trip, owner file only, safe names ---
tmp = Path(tempfile.mkdtemp())
hub_core.publish("alpha", [{"x": 1}], 7, root=tmp)
hub_core.publish("beta", [], 5, root=tmp)
assert hub_core.read("alpha", tmp)["findings"] == [{"x": 1}]
assert hub_core.read("missing", tmp) is None
assert hub_core.total_trials(["alpha", "beta", "missing"], tmp) == 12
hub_core.publish("../evil", [], 1, root=tmp)
assert not (tmp.parent / "evil.json").exists() and (tmp / "evil.json").exists()

# --- multiple-testing maths ---
assert abs(hub_truth.bonferroni_t(1) - 1.96) < 0.01
assert hub_truth.bonferroni_t(564) > hub_truth.bonferroni_t(10) > hub_truth.bonferroni_t(1)
assert hub_truth.expected_max_null_t(1000) > hub_truth.expected_max_null_t(10) > 0
assert hub_truth.benjamini_hochberg([0.001, 0.2, 0.8]) == [True, False, False]
assert hub_truth.benjamini_hochberg([]) == []

# --- judge(): lucky small-n row is rejected, a strong row with both halves passes ---
rows = [{"key": f"noise{i}", "school": "x", "tf": "1h", "side": "all", "n": 300, "avgR": 0.0, "t": 0.1 * (i % 5), "is_avgR": 0.0, "oos_avgR": 0.0} for i in range(200)]
rows.append({"key": "lucky", "school": "x", "tf": "1h", "side": "all", "n": 40, "avgR": 0.6, "t": 3.3, "is_avgR": 0.7, "oos_avgR": 0.5})
rows.append({"key": "real", "school": "x", "tf": "1h", "side": "all", "n": 900, "avgR": 0.35, "t": 6.0, "is_avgR": 0.33, "oos_avgR": 0.37})
rows.append({"key": "notest", "school": "x", "n": 50, "avgR": 1.0})
res = hub_truth.judge(rows)
assert res["n_trials"] == 202 and res["n_untestable"] == 1
by = {v["key"]: v for v in res["verdicts"]}
assert not by["lucky"]["promote"] and any("n=40" in w for w in by["lucky"]["why_not"])
assert by["real"]["promote"] and res["n_promotable"] == 1
assert "notest" not in by

# --- run() on a mock lab file publishes a snapshot and survives a missing file ---
lab = tmp / "lab.json"
lab.write_text(json.dumps({"rows": rows}))
out = hub_truth.run(lab_path=lab, root=tmp)
assert out["n_promotable"] == 1 and hub_core.read("truth", tmp)["n_trials"] == 202
assert hub_truth.run(lab_path=tmp / "nope.json", root=tmp) is None
print("test_hub_core: all passed")
