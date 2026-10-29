"""Hub presentation + honest-N loop (plain script)."""
import sys, os, tempfile, json
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import hub_core, hub_ui, hub_truth, hub_plateau, hub_regime, hub_trail, hub_decay, hub_consensus

# --- identity table matches every tab's own SPEC (no drift between the picture and the tabs) ---
for mod in (hub_truth, hub_plateau, hub_regime, hub_trail, hub_decay, hub_consensus):
    t = hub_ui.BY_ID[mod.SPEC.id]
    assert (t[1], t[2], t[3], tuple(t[4])) == (mod.SPEC.title, mod.SPEC.glyph, mod.SPEC.accent, tuple(mod.SPEC.consumes)), mod.SPEC.id
assert len({t[3] for t in hub_ui.TABS}) == len(hub_ui.TABS)          # every tab has its own colour

# --- tabs never import each other's code (the hub rule), only hub_core / hub_ui ---
import re
for name in ("truth", "plateau", "regime", "trail", "decay", "consensus"):
    src = Path(f"modules/hub_{name}.py").read_text()
    others = set(re.findall(r"hub_(truth|plateau|regime|trail|decay|consensus)", " ".join(re.findall(r"^\s*(?:from modules import .*|from modules\.hub_\w+ import .*|import modules\.hub_\w+.*)$", src, re.M))))
    assert not (others - {name}), (name, others)

# --- HTML builders: escape text, survive empty input ---
spec = hub_plateau.SPEC
h = hub_ui.header(spec, "<script>alert(1)</script>", "T<i>")
assert "<script>" not in h and "&lt;script&gt;" in h and spec.accent in h and "Truth Court" in h      # consumes shown as a chip
assert hub_ui.cards([("i", "<b>lbl</b>", "<v>", "sub", "up", 50)]).count("uk-card") >= 1 and "<b>lbl</b>" not in hub_ui.cards([("i", "<b>lbl</b>", "v", "", "", None)])
assert hub_ui.ruler([]) == "" and hub_ui.graph([]) == ""
r = hub_ui.ruler([("luck", 3.09, "#888"), ("best", None, "#f00"), ("bonf", 3.92, "#fa0")], lo=0, hi=5)
assert "luck 3.09" in r and "best" not in r and "bonf 3.92" in r                                   # a missing value draws no marker
g = hub_ui.graph([("a", "b", 0.9, "REDUNDANT"), ("a", "c", -0.5, "OPPOSED"), ("b", "c", 0.0, "INDEPENDENT")])
assert g.count("<circle") == 3 and g.count("<line") == 3 and "redundant" in g
assert "nobody reads the regime yet" in hub_ui.flow() and hub_ui.flow().count("<rect") == 6
hub_ui.set_theme({"accent": "#123456"}, 6)
assert "#123456" in hub_ui.css() and "border-radius:6px" in hub_ui.css()
hub_ui.set_theme(None, None)

# --- overview: every card says 'not run yet' with no snapshots, and reads published ones with them ---
tmp = Path(tempfile.mkdtemp())
cs = hub_ui.overview_cards(tmp)
assert len(cs) == 6 and all(c[2] == "—" for c in cs)
hub_core.publish("truth", [], 564, extra={"bonferroni_t": 3.92, "expected_max_null_t": 3.09, "n_promotable": 0}, root=tmp)
hub_core.publish("decay", [{"state": "RETIRE", "size": 0.0, "n": 52, "why": "x"}], 1, root=tmp)
hub_core.publish("consensus", [], 25, extra={"counts": {"REDUNDANT": 8, "OPPOSED": 9, "INDEPENDENT": 8}}, root=tmp)
hub_core.publish("trail", [], 0, extra={"summary": {"signals": 12, "unproven": 12, "closed_trusted": 8, "live_net_avg_r": 0.775}}, root=tmp)
by = {c[1]: c for c in hub_ui.overview_cards(tmp)}
assert by["Truth Court"][2] == "N=564" and by["Truth Court"][4] == "warn"
assert by["Decay Watch"][2] == "RETIRE" and by["Decay Watch"][4] == "down"
assert by["Consensus Map"][2] == "8 / 9 / 8" and by["Decision Trail"][2] == "12 signals"

# --- the honest-N loop: other tabs' trials raise Truth Court's bar ---
rows = [{"key": f"k{i}", "school": "x", "tf": "1h", "side": "all", "n": 300, "avgR": 0.0, "t": 0.1, "is_avgR": 0.0, "oos_avgR": 0.0} for i in range(100)]
base = hub_truth.judge(rows)
more = hub_truth.judge(rows, extra_trials=900)
assert base["n_total"] == 100 and more["n_total"] == 1000 and more["bonferroni_t"] > base["bonferroni_t"] and more["n_trials"] == 100
lab = tmp / "lab.json"; lab.write_text(json.dumps({"rows": rows}))
hub_core.publish("plateau", [], 40, root=tmp); hub_core.publish("regime", [], 12, root=tmp)
out = hub_truth.run(lab_path=lab, root=tmp)
assert out["n_total"] == 100 + 40 + 12 + 1 + 25 and hub_core.read("truth", tmp)["n_total"] == out["n_total"]   # decay (1) and consensus (25) count too
print("test_hub_ui: all passed")
