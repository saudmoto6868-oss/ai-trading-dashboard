"""Decision Trail on hand-made signal-log records (plain script). MOCK DATA ONLY."""
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import hub_core, hub_trail as ht

def rec(**kw):
    r = {"t": 1000, "key": "k", "symbol": "BTC-USDT", "dir": "bullish", "tf": "1h", "score": 4, "max": 7, "q": 72,
         "entry": 100, "stop": 98, "tp1": 104, "px0": 100, "sent": True}
    r.update(kw); return r

# --- plan check ---
ok, risk, rr = ht.plan_check(rec())
assert ok and abs(risk - 0.02) < 1e-9 and abs(rr - 2.0) < 1e-9
assert not ht.plan_check(rec(stop=102))[0]                       # stop on the wrong side of a long
assert ht.plan_check(rec(dir="bearish", entry=100, stop=102, tp1=96))[0]
assert not ht.plan_check(rec(entry=None))[0] and not ht.plan_check({})[0]
assert not ht.plan_check(rec(stop=100))[0]                       # zero risk

# --- validate stage: UNPROVEN by default, pass only when the Truth Court promoted the rule ---
tmp = Path(tempfile.mkdtemp())
assert ht.promoted_keys(tmp) == set()
x = ht.row(rec(setup_id="OB-RETEST-HTF", layers=["HTF", "Location"]), set())
assert x["stages"]["Validate"][0] == "UNPROVEN"
assert ht.row(rec(), set())["stages"]["Validate"][1].startswith("no rule recorded")
hub_core.publish("truth", [{"key": "Location", "promote": True}, {"key": "level", "promote": False}], 500, root=tmp)
assert ht.promoted_keys(tmp) == {"location"}
assert ht.row(rec(layers=["HTF", "Location"]), {"location"})["stages"]["Validate"][0] == "pass"
assert ht.row(rec(layers=["level"]), {"location"})["stages"]["Validate"][0] == "UNPROVEN"
assert ht.row(rec(stop=102), set())["stages"]["Validate"][0] == "bad plan"

# --- settle: R is net of cost, exp/nofill are not counted ---
tp = ht.row(rec(out="tp", r=2.0, t_out=2000), set())
assert tp["stages"]["Settle"][0] == "tp" and abs(tp["net_r"] - 1.9) < 1e-9
sl = ht.row(rec(out="sl", r=-1.0, t_out=2000), set())
assert abs(sl["net_r"] - (-1.1)) < 1e-9
assert ht.row(rec(out="exp", r=0.0, t_out=2000), set())["net_r"] is None
assert ht.row(rec(), set())["stages"]["Settle"][0] == "open"

# --- integrity: outcome time missing or before the signal -> flagged and excluded ---
assert ht.row(rec(out="tp", r=2.0), set())["flags"]
assert ht.row(rec(out="tp", r=2.0, t_out=500), set())["flags"]
assert not ht.row(rec(out="tp", r=2.0, t_out=1000), set())["flags"]

# --- analyse: counts, ordering by t_out, publish for Decay Watch ---
recs = [rec(t=1, out="sl", r=-1.0, t_out=30), rec(t=2, out="tp", r=2.0, t_out=10), rec(t=3, out="tp", r=2.0),   # no t_out: flagged
        rec(t=4), rec(t=5, stop=102)]
res = ht.analyse(recs, root=tmp)
s = res["summary"]
assert s["signals"] == 5 and s["closed_trusted"] == 2 and s["flagged"] == 1 and s["open"] == 2 and s["bad_plan"] == 1
assert res["live_r"] == [1.9, -1.1]                              # ordered by outcome time, net of cost
assert abs(s["live_net_avg_r"] - 0.4) < 1e-9 and not s["enough"] and "not evidence" in s["verdict"]
snap = hub_core.read("trail", tmp)
assert snap["live_r"] == [1.9, -1.1] and snap["n_trials"] == 0
assert ht.analyse([], root=tmp)["summary"]["verdict"].startswith("no closed signals")

# --- enough trades flips the evidence flag ---
big = [rec(t=i, out="tp" if i % 3 else "sl", r=2.0 if i % 3 else -1.0, t_out=i + 1) for i in range(1, 121)]
assert ht.analyse(big, root=tmp)["summary"]["enough"]

# --- parser keeps good lines past a damaged one ---
assert len(ht.parse_jsonl('{"a":1}\nnot json\n\n{"b":2}\n')) == 2
print("test_hub_trail: all passed")
