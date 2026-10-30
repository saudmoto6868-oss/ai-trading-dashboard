"""Every detector key the alert rules and the trade-plan books name must be a REAL key of the weekly lab (data/strategy_lab.json = what the detectors actually emit).
Found 2026-10-30: 11 of the 17 whitelist keys were invented (fib_ote, sweep_high, vwap_reclaim, sr_bounce ...), so the plan 'levels' book could never trigger and CALL fired from 5 keys only.
Also: the plan uses the scan's real ATR when it is there. Run: PYTHONPATH=. python tests/test_alert_keys_real.py"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules.alerts import CALL_TRIGGER_WHITELIST  # noqa: E402
from modules import risk_engine as RE  # noqa: E402

lab = {r["key"] for r in json.load(open(os.path.join(ROOT, "data", "strategy_lab.json")))["rows"] if r.get("key") and not str(r["key"]).startswith("*")}
for name, ks in (("CALL_TRIGGER_WHITELIST", CALL_TRIGGER_WHITELIST), ("_REVERSAL_KEYS", RE._REVERSAL_KEYS), ("_LEVELS_KEYS", RE._LEVELS_KEYS), ("_TREND_KEYS", RE._TREND_KEYS)):
    bad = sorted(k for k in ks if k not in lab)
    assert not bad, f"{name} names keys that no detector emits: {bad}"
assert not (RE._REVERSAL_KEYS & RE._LEVELS_KEYS) and not (RE._LEVELS_KEYS & RE._TREND_KEYS) and not (RE._REVERSAL_KEYS & RE._TREND_KEYS)
assert not any(k.startswith("ew") for k in CALL_TRIGGER_WHITELIST), "Elliott is context only (T4)"
# every book can actually trigger from a real key
for key, book in (("ob", "levels"), ("vwap", "levels"), ("sweep", "reversal"), ("ma_cross", "trend"), ("turtle55", "trend"), ("zombie", "fallback")):
    assert RE._detect_book([{"key": key}]) == book, (key, RE._detect_book([{"key": key}]))
# the plan's distances follow the real ATR
base = {"price": 100.0, "trend_bias": "bullish", "supports": [], "resistances": [], "signals": [{"key": "ma_cross", "prices": {}}], "direction": "bullish"}
small, big = RE.build_trade_plan({**base, "atr": 0.5}), RE.build_trade_plan({**base, "atr": 2.0})
noatr = RE.build_trade_plan(dict(base))
assert abs(small["stop_loss"] - 100) <= abs(big["stop_loss"] - 100) and small["stop_loss"] != big["stop_loss"], (small, big)
assert RE._atr_estimate({"price": 200.0}) == 1.0 and RE._atr_estimate({"price": 200.0, "atr": 3.0}) == 3.0
print("ok alert / plan keys are real; ATR used:", {"whitelist": len(CALL_TRIGGER_WHITELIST), "stop(atr .5)": small["stop_loss"], "stop(atr 2)": big["stop_loss"], "no atr": noatr["stop_loss"]})
