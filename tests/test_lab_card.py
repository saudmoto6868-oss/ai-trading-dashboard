"""lab_tiers.card: one row per detector key, own timeframe when n >= 30 else all timeframes, net = avgR - cost, verdicts. Plain script."""
import json, os, tempfile
from pathlib import Path

import modules.lab_tiers as LT

rows = [{"key": "a", "school": "S", "tf": "1h", "side": "all", "n": 50, "avgR": 0.25, "t": 3.4, "is_avgR": .2, "oos_avgR": .3, "edge": True},
        {"key": "b", "school": "S", "tf": "1h", "side": "all", "n": 10, "avgR": 0.5},
        {"key": "b", "school": "S", "tf": "all", "side": "all", "n": 400, "avgR": 0.02},
        {"key": "c", "school": "S", "tf": "1h", "side": "all", "n": 40, "avgR": 0.15}]
d = Path(tempfile.mkdtemp()); p = d / "lab.json"; p.write_text(json.dumps({"rows": rows}))
LT.PATH = p; LT._cache["mtime"] = None
c = {x["key"]: x for x in LT.card(["a", "b", "c", "a", "zz", None], "1h")}
assert set(c) == {"a", "b", "c"}
assert c["a"]["verdict"] == "edge" and c["a"]["tf"] == "1h" and abs(c["a"]["net"] - 0.15) < 1e-9
assert c["b"]["tf"] == "all" and c["b"]["verdict"] == "loses"          # own-tf n=10 too small -> all-timeframes row; net 0.02-0.10 < 0
assert c["c"]["verdict"] == "positive, not proven"                    # net +0.05 but no lab edge
print("ok lab_card")
