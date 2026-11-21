"""Radar grid = our Workspace chart widget (owner 2026-11-21): solo="radar" config, the radar part is wired in, pattern lines come
with the scan, the radar layout never touches the Workspace's saved layout. Plain script."""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np   # noqa: E402
import pandas as pd   # noqa: E402
from modules import chart_scan as CS   # noqa: E402
from modules.workspace import build_workspace_html   # noqa: E402

# 1) the config reaches the page
item = {"sym": "BTC-USDT", "tf": "1h", "tag": "x", "info": "<b>i</b>", "pts": [{"label": "Elliott", "kind": "ind", "ind": "ew"}]}
doc = build_workspace_html(["BTC-USDT"], None, "en", solo="radar", radar={"cols": 3, "h": 300, "items": [item]})
cfg = json.loads(re.search(r'"solo": "radar", "radar": (\{.*?\}), "spot"', doc).group(1))
assert cfg["cols"] == 3 and cfg["items"][0]["pts"][0]["ind"] == "ew"
assert '"solo": ""' in build_workspace_html(["BTC-USDT"], None, "en", solo="bogus")   # only known modes

# 2) the parts are wired: own saved layout, decorate hook, menu save exposed, radar lines never saved
src = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf-8").read()
for s in ('CFG.solo === "radar" ? "ai_ws_radar"', "RadarMode.decorate(this)", "const save = this.indSave =", "this.draws.filter(d => !d._rd)",
          "Ws.build(RadarMode.layout(", "const RadarMode = {"):
    assert s in src, s

# 3) features() hands back the pattern lines per pattern (Radar points draw them)
rng = np.random.default_rng(1)
c = 100 + np.cumsum(rng.normal(0, 1, 260))
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=260, freq="h"), "open": c, "high": c + 1, "low": c - 1, "close": c, "volume": 1000.0})
f = CS.features(df)
assert isinstance(f["plines"], dict) and all(k.startswith("cp_") for k in f["plines"])

# 4) RadarMode.tf maps the Radar timeframe names to the chart's (node, pure function)
if shutil.which("node"):
    js = re.search(r"  tf\(t\)\{.*?\},\n", open(os.path.join(ROOT, "modules", "ws", "24f_radar.js"), encoding="utf-8").read(), re.S).group(0)
    r = subprocess.run([shutil.which("node"), "-e", "const R = {" + js + "}; console.log(JSON.stringify(['1h','4h','1d','1w','15m','1mo','x'].map(t => R.tf(t))))"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == ["1H", "4H", "1D", "1W", "15m", "1M", "1H"], r.stdout
print("ok radar widget")
