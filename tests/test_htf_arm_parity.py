"""Setup Card HtfArm.arm (modules/ws/14_journal_chain.js) == research/htf_arms (htf_state + arm) on the same closed bars. Plain script (node)."""
import json, re, subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from research.htf_arms.run_htf_arms import arm, htf_state

src = (Path(__file__).resolve().parent.parent / "modules/ws/14_journal_chain.js").read_text()
m = re.search(r"(  arm\(rows, d\)\{.*?\n.*?\n.*?\n.*?\n.*?\); \},)", src, re.S)
assert m, "HtfArm.arm not found"
cases, rng = [], np.random.default_rng(3)
for k in range(60):
    c = 100 + np.cumsum(rng.normal(0, 1, 60) + rng.choice([-0.6, 0, 0.6]))
    h, l = c + rng.uniform(.2, 1.5, 60), c - rng.uniform(.2, 1.5, 60)
    rows = [{"t": i, "o": float(c[i]), "h": float(h[i]), "l": float(l[i]), "c": float(c[i])} for i in range(60)]
    cases.append(rows)
js = "const H = {" + m.group(1) + "};\nconst cases = " + json.dumps(cases) + ";\nconsole.log(JSON.stringify(cases.map(r => [H.arm(r, 1), H.arm(r, -1)])));"
r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
assert r.returncode == 0, r.stderr
got = json.loads(r.stdout)
for rows, (jl, js_) in zip(cases, got):
    df = pd.DataFrame(rows[:-1]).rename(columns={"o": "open", "h": "high", "l": "low", "c": "close"}); df["time"] = pd.to_datetime(df["t"], unit="D")   # the last bar is still open: JS drops it
    st = htf_state(df).iloc[-1]
    assert jl == arm(1, int(st["trend"]), float(st["pos"])) and js_ == arm(-1, int(st["trend"]), float(st["pos"])), (jl, js_, st.to_dict())
print("ok htf arm parity", len(cases), "cases")
