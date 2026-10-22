"""Strategy rules model: validation, AND / OR evaluation, JSON round trip, session store (plain script)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
from modules.strategy_rules import SessionStore, evaluate, from_json, to_json, validate

rng = np.random.default_rng(3)
c = 100 + np.cumsum(rng.normal(0, 1, 300))
df = pd.DataFrame({"open": c, "high": c + 1, "low": c - 1, "close": c, "volume": rng.uniform(1, 9, 300)})

s = {"name": "ema cross", "side": "long", "logic": "AND",
     "rules": [{"indicator": "ema", "period": 10, "op": "crosses_above", "value": {"indicator": "ema", "period": 30}}]}
assert validate(s) == []
m = evaluate(s, df)
assert m.dtype == bool and len(m) == 300 and 0 < m.sum() < 60
# AND is never wider than OR
r2 = {"indicator": "rsi", "period": 14, "op": ">", "value": 50}
a = evaluate({**s, "rules": s["rules"] + [r2]}, df).sum(); o = evaluate({**s, "logic": "OR", "rules": s["rules"] + [r2]}, df).sum()
assert a <= m.sum() <= o
# threshold rule on a hand-made series
t = pd.DataFrame({"open": [1, 2, 3], "high": [1, 2, 3], "low": [1, 2, 3], "close": [1, 2, 3], "volume": [1, 1, 1]})
assert list(evaluate({"name": "x", "side": "short", "rules": [{"indicator": "close", "op": ">=", "value": 2}]}, t)) == [False, True, True]
# invalid inputs give readable errors, never a crash
for bad in ({}, {"name": "", "side": "up", "rules": []}, {"name": "a", "side": "long", "rules": [{"indicator": "foo", "op": "?", "value": "x"}]},
            {"name": "a", "side": "long", "rules": [{"indicator": "rsi", "period": 1, "op": ">", "value": float("nan")}]}):
    assert validate(bad), bad
try:
    evaluate({"name": "a"}, df); raise SystemExit("should fail")
except ValueError:
    pass
# contradictory AND rules are rejected with a readable message; OR, other timeframes and touching bounds are fine
def _rs(*pairs, **kw):
    return {"name": "c", "side": "long", **kw, "rules": [{"indicator": "rsi", "period": 14, "op": o, "value": v} for o, v in pairs]}
for pairs in (((">", 70), ("<", 30)), ((">=", 50), ("<", 50)), ((">", 50), ("<=", 50)), ((">", 70), (">", 80), ("<", 75))):
    e = validate(_rs(*pairs)); assert e and "contradictory" in e[0] and "rsi(14)" in e[0], (pairs, e)
assert validate(_rs((">=", 50), ("<=", 50))) == []
assert validate(_rs((">", 30), ("<", 70))) == []
assert validate(_rs((">", 70), ("<", 30), logic="OR")) == []
mixed = _rs((">", 70)); mixed["rules"].append({"indicator": "rsi", "period": 14, "op": "<", "value": 30, "tf": "4h"})
assert validate(mixed) == []
mixed["rules"][0]["tf"] = "4h"; assert validate(mixed)
assert validate({**_rs((">", 70)), "rules": [{"indicator": "rsi", "period": 7, "op": ">", "value": 70}, {"indicator": "rsi", "period": 14, "op": "<", "value": 30}]}) == []
try:
    evaluate(_rs((">", 70), ("<", 30)), df); raise SystemExit("should fail")
except ValueError as e:
    assert "contradictory" in str(e)
# JSON round trip
assert from_json(to_json(s)) == s
try:
    from_json("{nope"); raise SystemExit("should fail")
except ValueError as e:
    assert "not valid JSON" in str(e)
# session store copies, does not alias
st = SessionStore({}); st.save(s); g = st.get("ema cross"); g["rules"].clear()
assert st.names() == ["ema cross"] and len(st.get("ema cross")["rules"]) == 1
st.delete("ema cross"); assert st.names() == []
print("test_strategy_rules: all passed")

# indicators added for the strategy map: no look-ahead (changing the LAST bar never changes an earlier value) and sane values
from modules.strategy_rules import _series
for ind, per in (("hh", 20), ("ll", 20), ("macd_hist", None), ("adx", 14), ("bbw", 20)):
    a = _series(df, ind, per); d2 = df.copy(); d2.loc[299, ["open", "high", "low", "close"]] = 500.0
    b = _series(d2, ind, per)
    assert a.iloc[:299].equals(b.iloc[:299]) or np.allclose(a.iloc[:299].dropna(), b.iloc[:299].dropna()), ind
    assert a.dropna().size > 200, ind
assert (_series(df, "hh", 20).dropna() >= df["close"].shift(1).rolling(20).min().dropna().reindex(_series(df, "hh", 20).dropna().index)).all()
assert 0 <= _series(df, "adx", 14).dropna().min() and _series(df, "adx", 14).dropna().max() <= 100
brk = {"name": "donch", "side": "long", "rules": [{"indicator": "close", "op": "crosses_above", "value": {"indicator": "hh", "period": 20}}]}
assert validate(brk) == [] and 0 < evaluate(brk, df).sum() < 40
assert validate({"name": "m", "side": "long", "rules": [{"indicator": "macd_hist", "op": "crosses_above", "value": 0}]}) == []
print("ok new indicators")
