"""Radar presets (plain script): every built-in preset only uses filter keys that exist, apply() resets leftovers, user presets round-trip."""
import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import radar_presets as R
from modules.chart_scan import ALL_FILTERS, MOVE_FILTERS, RSI_FILTERS, PATTERN_FILTERS, STRATEGY_FILTERS

mom, vol = R.split_moves(MOVE_FILTERS)
assert mom and vol and set(mom) | set(vol) == set(MOVE_FILTERS), (mom, vol)
pool = {"cs_rsi": RSI_FILTERS, "cs_mom_a": mom, "cs_mom_v": vol, "cs_pat": PATTERN_FILTERS, "cs_strat": STRATEGY_FILTERS}
for name, p in R.BUILTIN.items():
    for k, v in p.items():
        assert k in R.ALL_KEYS, (name, k)
        if k in R.LIST_KEYS:
            assert all(x in pool[k] for x in v), (name, k, [x for x in v if x not in pool[k]])
ss = {"cs_rsi": ["rsi_gt70"], "cs_pat": ["dbl_top"], "cs_side": "Sell only", "cs_stack": "Above all EMAs"}
assert R.apply(ss, "Oversold bounce")
assert ss["cs_rsi"] == ["rsi_lt30"] and ss["cs_pat"] == [] and ss["cs_stack"] == "—" and ss["cs_side"] == "Buy only" and ss["cs_mode"] == "All selected", ss   # old choices are gone
assert not R.apply(ss, "no such preset")
snap = R.snapshot(ss); assert snap == {"cs_rsi": ["rsi_lt30"], "cs_mom_v": ["vol_2x"], "cs_side": "Buy only"}, snap
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "p.json")
    assert R.save_user("  My  scalp ", snap, path)[0] and not R.save_user("", snap, path)[0] and not R.save_user("x", {}, path)[0]
    P = R.all_presets(path); assert "★ My scalp" in P and P["★ My scalp"] == snap
    ss2 = {}; assert R.apply(ss2, "★ My scalp", P) and ss2["cs_rsi"] == ["rsi_lt30"]
    assert R.delete_user("★ My scalp", path) and "★ My scalp" not in R.all_presets(path)
# browser-store presets: damaged data must never break anything
bad = {"ok": {"cs_rsi": ["rsi_lt30"], "cs_side": "Buy only", "junk": 1}, "": {"cs_rsi": ["x"]}, "str": "no", "lists": {"cs_rsi": "notalist"}, 7: {}}
c = R.clean(bad); assert c == {"ok": {"cs_rsi": ["rsi_lt30"], "cs_side": "Buy only"}}, c
assert R.clean(None) == {} and R.clean([1]) == {} and "★ ok" in R.all_presets(path="/nonexistent/p.json", extra=bad)
print("PASS: radar presets", len(R.BUILTIN), "built-in")
