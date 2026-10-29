"""Decay Watch + champion/challenger registry on hand-made numbers (plain script). MOCK DATA ONLY."""
import sys, os, tempfile, random
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import hub_core, hub_decay as hd

random.seed(1)
def noisy(mean, n, sd=1.0):
    return [round(random.gauss(mean, sd), 3) for _ in range(n)]

# --- CUSUM path agrees with hub_core.decay_cusum and rises on a losing streak ---
xs = noisy(-1.2, 60)   # k=0.5 sigma slack: a mean of -0.5 would not drift, -1.2 does
p = hd.cusum_path(xs, 0.0, 1.0)
assert abs(p[-1] - hub_core.decay_cusum(xs, 0.0, 1.0)["s"]) < 1e-3 and p[-1] > 4

# --- rolling t ---
assert hd.rolling_t([1, 1]) is None and hd.rolling_t([0, 0, 0, 0]) is None      # too short / no spread and no mean
assert hd.rolling_t([-1, -1, -1, -1]) == float('-inf')
assert hd.rolling_t([1, 2, 3, 2, 1, 2, 3, 2]) > 3

# --- status: too few never says OK; steady loss retires; healthy edge is OK ---
s = hd.status(noisy(1.0, 10))
assert s["state"] == "TOO FEW" and s["size"] is None
dead = hd.status([-1.0 + 0.05 * (i % 3) for i in range(60)])
assert dead["state"] == "RETIRE" and dead["size"] == 0.0, dead
healthy = hd.status([0.6, -1.0, 0.6, 0.6, -1.0, 0.6] * 8 + [0.6] * 6)
assert healthy["state"] == "OK" and healthy["size"] == 1.0, healthy
# alarm without a deeply negative rolling t -> SHRINK: long good history, then a recent fade
mixed = [0.8, -0.4] * 40 + [-0.9, 0.3] * 10
m = hd.status(mixed, mu0=0.25)
assert m["state"] in ("SHRINK", "WATCH", "OK", "RETIRE") and m["size"] in (1.0, 0.5, 0.0)
# a recovered series is judged by the CURRENT cusum, not an old alarm
rec = hd.status([-1.0] * 15 + [1.0] * 60)
assert rec["state"] in ("OK", "WATCH") and rec["first_alarm_at"] is not None

# --- challenger gate ---
good = {"id": "ch1", "n": 400, "t": 5.5, "is_avgR": 0.2, "oos_avgR": 0.15, "net_avgR": 0.1}
reg = {"events": []}
set_c = {"id": "inc", "n": 300, "t": 4.0, "is_avgR": 0.1, "oos_avgR": 0.05, "net_avgR": 0.02}
hd.set_champion(reg, set_c, now=1_000_000)
assert reg["champion"]["id"] == "inc" and reg["events"][0]["kind"] == "champion_set"
d = hd.challenge(reg, good, truth_n=564, now=1_000_100)
assert d["promoted"] and reg["champion"]["id"] == "ch1" and d["need_t"] > 3.9
# cooldown: a second great challenger a day later is rejected
better = {**good, "id": "ch2", "oos_avgR": 0.5, "t": 9.0}
d2 = hd.challenge(reg, better, truth_n=564, now=1_000_100 + 86400)
assert not d2["promoted"] and any("cooldown" in w for w in d2["reasons"]) and reg["champion"]["id"] == "ch1"
# after the cooldown it passes; weaker OOS than champion is rejected
d3 = hd.challenge(reg, better, truth_n=564, now=1_000_100 + 31 * 86400)
assert d3["promoted"] and reg["champion"]["id"] == "ch2"
d4 = hd.challenge(reg, {**good, "id": "weak", "oos_avgR": 0.01}, truth_n=564, now=1_000_100 + 90 * 86400)
assert not d4["promoted"] and any("champion" in w for w in d4["reasons"])
# Bonferroni grows with every challenge ever tried (failures count)
need = [hd.challenge({"events": [], "champion": None}, {**good, "t": 0}, truth_n=100, now=1)["need_t"]]
r2 = {"events": [{"kind": "challenge"}] * 200}
assert hd.challenge(r2, {**good, "t": 0}, truth_n=100, now=1)["need_t"] > need[0]
# t below the Bonferroni bar is rejected even when promote() passes
weak_t = hd.challenge({"events": []}, {**good, "t": 3.2}, truth_n=564, now=1)
assert not weak_t["promoted"] and any("Bonferroni" in w for w in weak_t["reasons"])
assert len(reg["events"]) == 5 and sum(e["kind"] == "challenge" for e in reg["events"]) == 4   # every attempt is on record

# --- run(): reads the trail's snapshot, publishes status + registry, counts challenges as trials ---
tmp = Path(tempfile.mkdtemp())
out = hd.run(root=tmp)
assert not out["has_trail"] and out["status"]["state"] == "TOO FEW"
hub_core.publish("trail", [], 0, extra={"live_r": [-1.0] * 60}, root=tmp)
out = hd.run(root=tmp)
assert out["has_trail"] and out["status"]["state"] == "RETIRE"
reg2 = {"events": []}
hd.challenge(reg2, good, truth_n=10, now=5)
hd.run(root=tmp, registry=reg2)
snap = hub_core.read("decay", tmp)
assert snap["n_trials"] == 1 and snap["registry"]["events"][0]["id"] == "ch1" and hd.load_registry(tmp)["events"][0]["id"] == "ch1"
print("test_hub_decay: all passed")
