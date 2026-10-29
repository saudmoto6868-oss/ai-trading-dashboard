"""Kill Funnel + break-even table on hand-made rows and the real lab file (plain script)."""
import sys, os, tempfile, json
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import hub_core, hub_funnel as hf

def row(key, n=300, avg=0.2, t=4.0, is_=0.2, oos=0.2, school="s", **kw):
    r = {"key": key, "school": school, "tf": "1h", "side": "all", "n": n, "avgR": avg, "t": t, "is_avgR": is_, "oos_avgR": oos, "win": 40}
    r.update(kw); return r

rows = [row("notest", t=None, is_=None, oos=None),               # dies at Testable
        row("small", n=50),                                      # dies at Enough trades
        row("gross_neg", avg=-0.02, t=-1.0),                     # dies at Gross edge
        row("net_neg", avg=0.05, t=3.5),                         # 0.05 - 0.10 < 0: dies at Net edge
        row("one_half", oos=-0.05),                              # dies at Both halves
        row("low_t", t=2.0),                                     # dies at t >= 3
        row("lucky", t=3.4),                                     # passes t>=3 but not the Bonferroni bar below
        row("real", t=6.0)]
f = hf.funnel(rows, bonf_t=3.9)
n = [s["n"] for s in f["stages"]]
assert n == [8, 7, 6, 5, 4, 3, 2, 1], n          # each hand-made row dies at exactly the stage it was built for
assert [s["name"] for s in f["stages"]] == list(hf.STAGE_NAMES)
assert all(n[i] >= n[i + 1] for i in range(len(n) - 1))           # strictly a funnel: never grows
assert [c["key"] for c in f["closest"]] == ["lucky", "low_t"]          # alive after "Both halves" but not survivors, best t first
assert f["biggest_kill"] != "Testable"                                          # missing t-stats are not a verdict
assert f["survived"] == 1 and f["survivors"][0]["key"] == "real" and f["kill_rate"] == 87.5
assert f["stages"][1]["killed"] == 1 and f["stages"][2]["killed"] == 1 and f["biggest_kill"] in hf.STAGE_NAMES
# exit rows carry their own 'net'
assert hf._net({"net": 0.3, "avgR": 0.0}) == 0.3 and abs(hf._net({"avgR": 0.25}) - 0.15) < 1e-9
# negative t never counts as an edge even when large
assert hf.funnel([row("short", avg=-0.3, t=-9.0)], bonf_t=3.9)["survived"] == 0
assert hf.funnel([])["kill_rate"] is None and hf.funnel([])["stages"][0]["n"] == 0
# schools table sums to the stage counts
assert sum(v[0] for v in f["schools"].values()) == 8 and sum(v[-1] for v in f["schools"].values()) == 1

assert f["untested_schools"] == []                                               # every school in the hand-made pool has a testable row
u = hf.funnel([row("x", t=None, is_=None, oos=None, school="unjudged"), row("y", school="judged")], bonf_t=3.9)
assert u["untested_schools"] == ["unjudged"]

# --- break-even maths ---
assert abs(hf.breakeven_win(1.0, 0.0) - 0.5) < 1e-12 and abs(hf.breakeven_win(2.0, 0.0) - 1 / 3) < 1e-12
assert abs(hf.breakeven_win(1.0, 0.10) - 0.55) < 1e-12 and hf.breakeven_win(3.0) < hf.breakeven_win(1.0)
lab = [{"key": "*VAR*", "tf": "all", "side": "rr1.0", "n": 1000, "win": 48.4, "avgR": -0.032},
       {"key": "*VAR*", "tf": "all", "side": "rr3.0", "n": 1000, "win": 29.0, "avgR": 0.003},     # above 27.5% BE yet net R < 0
       {"key": "*VAR*", "tf": "all", "side": "rr2.0_be", "n": 1000, "win": 27.1, "avgR": -0.001}]  # variants are ignored
bt = {b["rr"]: b for b in hf.breakeven_table(lab)}
assert bt[1.0]["breakeven_win_pct"] == 55.0 and bt[1.0]["note"] == "win% below break-even"
assert "winners pay less than the target" in bt[3.0]["note"] and bt[3.0]["lab_net_r"] < 0
assert bt[0.5]["lab_win_pct"] is None and bt[2.0]["lab_win_pct"] is None
good = hf.breakeven_table([{"key": "*VAR*", "tf": "all", "side": "rr2.0", "n": 1, "win": 50.0, "avgR": 0.5}])
assert [b for b in good if b["rr"] == 2.0][0]["note"].startswith("above break-even and net R positive")

# --- run(): publishes, uses the Truth Court's bar when present, tolerates a missing lab ---
tmp = Path(tempfile.mkdtemp()); labf = tmp / "lab.json"; labf.write_text(json.dumps({"rows": rows}))
out = hf.run(lab_path=labf, root=tmp)
assert not out["used_truth_bar"] and out["survived"] >= 1
hub_core.publish("truth", [], 500, extra={"bonferroni_t": 6.5}, root=tmp)
out2 = hf.run(lab_path=labf, root=tmp)
assert out2["used_truth_bar"] and out2["bonferroni_t"] == 6.5 and out2["survived"] == 0            # t=6.0 < 6.5: raising N kills it
snap = hub_core.read("funnel", tmp)
assert snap["n_trials"] == 0 and snap["tested"] == 8 and snap["kill_rate"] == 100.0
assert hf.run(lab_path=tmp / "nope.json", root=tmp) is None

# --- real lab file end to end ---
real = hf.run(root=Path(tempfile.mkdtemp()))
assert "Elliott wave" in real["untested_schools"] and "SMC / ICT" in real["untested_schools"] and "Chain" not in real["untested_schools"]
assert real["tested"] == 1175 and real["stages"][1]["n"] == 564 and real["survived"] == 0 and real["kill_rate"] == 100.0
assert [b["rr"] for b in real["breakeven"] if b["lab_win_pct"] is not None] == [1.0, 1.5, 2.0, 3.0]
assert "winners pay less" in {b["rr"]: b for b in real["breakeven"]}[3.0]["note"]       # the lab's rr3.0 row: win% 29 > 27.5 break-even, net R still negative
print("test_hub_funnel: all passed")
