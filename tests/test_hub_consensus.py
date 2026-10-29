"""Consensus Map on hand-made numbers and the real lab file (plain script)."""
import sys, os, tempfile, json
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import hub_core, hub_consensus as hc

C = lambda a, b, n, o: {"a": a, "b": b, "together": n, "opposite": o, "rate": round(100 * o / max(n, 1), 1)}

# --- pair maths ---
ps = {(p["a"], p["b"]): p for p in hc.pair_stats([C("x", "y", 10000, 500), C("x", "z", 10000, 9500), C("x", "w", 10000, 5000),
                                                   C("x", "v", 10, 3), C("p", "q", 10000, 5100), C("none", "n", 0, 0)])}
assert ps[("x", "y")]["rho"] == 0.9 and ps[("x", "y")]["class"] == "REDUNDANT"
assert ps[("x", "z")]["rho"] == -0.9 and ps[("x", "z")]["class"] == "OPPOSED"
assert ps[("x", "w")]["rho"] == 0.0 and ps[("x", "w")]["class"] == "INDEPENDENT"
assert ps[("x", "v")]["class"] == "INDEPENDENT" and not ps[("x", "v")]["significant"]   # 10 bars, rho 0.4 but z=-1.3: not enough data
assert ps[("p", "q")]["class"] == "INDEPENDENT"            # significant but |rho| 0.02 < 0.10: tiny effect is not "redundant"
assert ("none", "n") not in ps                              # together == 0 skipped

# --- effective votes: redundant detectors are worth ~1, independent ones count fully, opposition never inflates ---
red = [{"a": a, "b": b, "rho": 1.0} for a, b in (("a", "b"), ("a", "c"), ("b", "c"))]
assert hc.effective_votes(["a", "b", "c"], red)["effective"] == 1.0
ind = [{"a": a, "b": b, "rho": 0.0} for a, b in (("a", "b"), ("a", "c"), ("b", "c"))]
assert hc.effective_votes(["a", "b", "c"], ind)["effective"] == 3.0
opp = [{"a": "a", "b": "b", "rho": -0.9}]
assert hc.effective_votes(["a", "b"], opp)["effective"] == 2.0          # clipped at 0, not 2/(2-1.8)=10
e = hc.effective_votes(["a", "b", "z"], red[:1])
assert e["unmeasured"] and len(e["unmeasured"]) == 2 and e["effective"] < 3 and e["effective"] > 1
assert hc.effective_votes([], [])["n"] == 0 and hc.effective_votes(["a", "a"], [])["n"] == 1   # duplicates collapse
assert hc.proven_count(["Location", "level", "Location"], {"location"}) == 1

# --- confluence verdict: net = gross - 0.10, small n not used ---
none_pos = {"1 families": {"n": 34, "avgR": 0.347}, "2 families": {"n": 424, "avgR": -0.039}, "3 families": {"n": 1307, "avgR": -0.067}}
v = hc.confluence_verdict(none_pos)
assert v["n_positive"] == 0 and "none of the 2 usable" in v["verdict"]
assert {r["level"]: r["evidence"] for r in v["rows"]}["1 families"] is False       # the lone good-looking row has n=34
pos = hc.confluence_verdict({"4 families": {"n": 500, "avgR": 0.25}})
assert pos["n_positive"] == 1 and "4 families" in pos["verdict"]
assert "no verdict" in hc.confluence_verdict({"x": {"n": 5, "avgR": 1.0}})["verdict"]
assert hc.confluence_verdict({})["rows"] == []

# --- run(): publishes pairs, counts one trial per pair, tolerates a missing lab file ---
tmp = Path(tempfile.mkdtemp())
lab = tmp / "lab.json"
lab.write_text(json.dumps({"conflicts": [C("x", "y", 10000, 500), C("x", "w", 10000, 5000)], "confluence": none_pos}))
out = hc.run(lab_path=lab, root=tmp)
snap = hub_core.read("consensus", tmp)
assert snap["n_trials"] == 2 and out["counts"]["REDUNDANT"] == 1 and len(snap["findings"]) == 2
assert hc.run(lab_path=tmp / "nope.json", root=tmp) is None

# --- promoted() reads the Truth Court's snapshot only ---
assert hc.promoted(tmp) == set()
hub_core.publish("truth", [{"key": "Fvg", "promote": True}, {"key": "level", "promote": False}], 5, root=tmp)
assert hc.promoted(tmp) == {"fvg"}

# --- the real lab file runs end to end ---
real = hc.run(root=Path(tempfile.mkdtemp()))
assert real and len(real["pairs"]) == 25 and sum(real["counts"].values()) == 25
print("test_hub_consensus: all passed")
