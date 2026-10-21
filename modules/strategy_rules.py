"""Strategy rules data model for Technical Office v2: rules (indicator + condition + value) joined by AND / OR,
saved under a name, shown as JSON. Pure functions on an OHLCV DataFrame; nothing here places an order or stores anything
(saving is session-only until the owner picks a store)."""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

OPS = (">", ">=", "<", "<=", "crosses_above", "crosses_below")
LOGIC = ("AND", "OR")
SIDES = ("long", "short")
# indicator name -> parameter names allowed (all take one integer period except price fields)
INDICATORS = {"close": (), "open": (), "high": (), "low": (), "volume": (), "sma": ("period",), "ema": ("period",),
              "rsi": ("period",), "atr": ("period",), "roc": ("period",)}
_NAME = re.compile(r"^[\w\- ]{1,60}$", re.U)


def _series(df: pd.DataFrame, ind: str, period: int | None) -> pd.Series:
    c = df["close"].astype(float)
    if ind in ("close", "open", "high", "low", "volume"):
        return df[ind].astype(float)
    if ind == "sma":
        return c.rolling(period).mean()
    if ind == "ema":
        return c.ewm(span=period, adjust=False).mean()
    if ind == "roc":
        return c.pct_change(period) * 100
    if ind == "rsi":
        d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
        dn = (-d.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
        return 100 - 100 / (1 + up / dn.replace(0, np.nan))
    if ind == "atr":
        pc = df["close"].shift(1)
        tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
        return tr.ewm(alpha=1 / period, adjust=False).mean()
    raise ValueError(f"unknown indicator '{ind}'")


def validate(strategy: dict) -> list[str]:
    """Return a list of human-readable errors (empty = valid)."""
    errs = []
    if not isinstance(strategy, dict):
        return ["strategy must be an object"]
    if not _NAME.match(str(strategy.get("name", ""))):
        errs.append("name: 1-60 letters / digits / space / - / _")
    if strategy.get("side") not in SIDES:
        errs.append(f"side must be one of {SIDES}")
    if strategy.get("logic", "AND") not in LOGIC:
        errs.append(f"logic must be one of {LOGIC}")
    rules = strategy.get("rules")
    if not isinstance(rules, list) or not rules:
        errs.append("at least one rule is required")
        return errs
    if len(rules) > 12:
        errs.append("at most 12 rules")
    for i, r in enumerate(rules, 1):
        p = f"rule {i}: "
        if not isinstance(r, dict):
            errs.append(p + "must be an object"); continue
        ind = r.get("indicator")
        if ind not in INDICATORS:
            errs.append(p + f"unknown indicator '{ind}'"); continue
        if INDICATORS[ind]:
            per = r.get("period")
            if not isinstance(per, int) or isinstance(per, bool) or not 2 <= per <= 500:
                errs.append(p + "period must be an integer 2-500")
        if r.get("op") not in OPS:
            errs.append(p + f"op must be one of {OPS}")
        v = r.get("value")
        if isinstance(v, dict):   # compare against another indicator, e.g. ema(20) crosses_above ema(50)
            vi = v.get("indicator")
            if vi not in INDICATORS:
                errs.append(p + f"value indicator '{vi}' unknown")
            elif INDICATORS[vi] and not (isinstance(v.get("period"), int) and 2 <= v["period"] <= 500):
                errs.append(p + "value period must be an integer 2-500")
        elif isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v):
            errs.append(p + "value must be a finite number or an indicator")
    return errs


def evaluate(strategy: dict, df: pd.DataFrame) -> pd.Series:
    """Boolean entry series (True on bars where the rules fire), aligned to df. Raises ValueError on an invalid strategy."""
    errs = validate(strategy)
    if errs:
        raise ValueError("; ".join(errs))
    masks = []
    for r in strategy["rules"]:
        a = _series(df, r["indicator"], r.get("period"))
        v = r["value"]
        b = _series(df, v["indicator"], v.get("period")) if isinstance(v, dict) else pd.Series(float(v), index=df.index)
        op = r["op"]
        if op == "crosses_above":
            m = (a > b) & (a.shift(1) <= b.shift(1))
        elif op == "crosses_below":
            m = (a < b) & (a.shift(1) >= b.shift(1))
        else:
            m = {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}[op]
        masks.append(m.fillna(False))
    out = masks[0]
    for m in masks[1:]:
        out = (out & m) if strategy.get("logic", "AND") == "AND" else (out | m)
    return out.astype(bool)


def to_json(strategy: dict) -> str:
    errs = validate(strategy)
    if errs:
        raise ValueError("; ".join(errs))
    return json.dumps(strategy, ensure_ascii=False, indent=2, sort_keys=True)


def from_json(text: str) -> dict:
    try:
        s = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"not valid JSON: {e.msg}") from None
    errs = validate(s)
    if errs:
        raise ValueError("; ".join(errs))
    return s


class SessionStore:
    """Named strategies kept in a plain dict (pass st.session_state). Lost on refresh - the UI must say so."""
    KEY = "_strategies"

    def __init__(self, state):
        self.state = state
        self.state.setdefault(self.KEY, {})

    def save(self, strategy: dict) -> None:
        errs = validate(strategy)
        if errs:
            raise ValueError("; ".join(errs))
        self.state[self.KEY][strategy["name"]] = json.loads(to_json(strategy))

    def names(self) -> list[str]:
        return sorted(self.state[self.KEY])

    def get(self, name: str) -> dict:
        return json.loads(json.dumps(self.state[self.KEY][name]))

    def delete(self, name: str) -> None:
        self.state[self.KEY].pop(name, None)
