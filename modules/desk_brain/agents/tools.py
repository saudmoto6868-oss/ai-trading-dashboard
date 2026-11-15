"""Tools the agents can call (OpenAI function-calling format). Each call returns a slim JSON
result for the model and the full result for the UI board, and is written to the run's
evidence ledger so the auditor can check every number an agent writes."""
from __future__ import annotations

import json
from typing import Any, Callable

from .. import journal, risk
from ..config import UNIVERSE
from ..tools import framework as fw
from ..tools import macro, market
from ..tools.orderflow import orderflow_tool
from ..tools import schools

SYM = {"type": "string", "enum": list(UNIVERSE), "description": "market symbol"}
DIR = {"type": "integer", "enum": [1, -1], "description": "1 = long, -1 = short"}


def _slim(res: dict) -> dict:
    def strip(x):
        if isinstance(x, dict):
            return {k: strip(v) for k, v in x.items() if k not in ("chart", "series", "markers", "footprint", "levels")}
        if isinstance(x, list):
            return [strip(v) for v in x[:12]]
        if isinstance(x, float):
            return round(x, 5)
        return x
    return {"tool": res.get("tool"), "source": res.get("source"), "data": strip(res.get("data", {})),
            "summary": res.get("look_at")}


class Ctx:
    """Shared per-run cache so parallel agents don't refetch the same thing."""
    def __init__(self) -> None:
        self.rates = None
        self.cache: dict[str, Any] = {}

    def get(self, key: str, fn: Callable[[], Any]) -> Any:
        if key not in self.cache:
            self.cache[key] = fn()
        return self.cache[key]


def _bias(ctx: Ctx, symbol: str) -> dict:
    rates = ctx.get("rates", macro.rate_differentials)
    c = ctx.get(f"cot:{symbol}", lambda: market.cot_tool(symbol))
    s = ctx.get(f"seas:{symbol}", lambda: market.seasonality_tool(symbol))
    return ctx.get(f"bias:{symbol}", lambda: market.bias_tool(symbol, rates["data"], c, s))


def _watchlist(ctx: Ctx) -> dict:
    from ..views import watchlist
    w = watchlist(ctx.cache.get("last"))
    rows = [{"symbol": r["symbol"], "direction": r["direction"], "stars": r["stars"], "score": r["score"],
             "promoted": r["promoted"], "departments": r["departments"], "blocked": r["blocked"],
             "reasons": [x["text"] for x in r["reasons"]]} for r in w["rows"]]
    return {"tool": "watchlist", "title": "Watchlist", "source": w["source"], "data": {"rows": rows},
            "look_at": f"{sum(r['promoted'] for r in rows)} سوق مترقّي من {len(rows)}"}


def _size(symbol: str, entry: float, stop: float) -> dict:
    s = risk.size(symbol, entry, stop)
    return {"tool": "position_size", "title": "Position size", "source": ["accounts"], "data": s,
            "look_at": f"الوقف {s['stop_pips']} نقطة ({s['pip_rule']})"}


def _accounts() -> dict:
    s = risk.state()
    keep = ("id", "name", "tier", "balance", "personal_floor", "room_today", "risk_per_trade",
            "trades_left_today", "stopped_today", "tier_rule", "daily_profit_cap")
    return {"tool": "accounts", "title": "Accounts", "source": ["accounts"],
            "data": {"accounts": [{k: a.get(k) for k in keep} for a in s["accounts"]], "discipline": s["discipline"]},
            "look_at": "حالة الحسابات الثلاثة"}


# name -> (description, params schema, callable(ctx, **args))
REGISTRY: dict[str, tuple[str, dict, Callable]] = {
    "risk_regime": ("Risk-on/off score from VIX, S&P vs EMA50, AUDJPY, gold.", {}, lambda c: c.get("regime", macro.risk_regime)),
    "currency_strength": ("Strength of 8 currencies over 28 pairs (1/5/20 days).", {}, lambda c: c.get("strength", macro.currency_strength)),
    "rate_differentials": ("3-month interest rates and 3-month change per currency (FRED).", {}, lambda c: c.get("rates", macro.rate_differentials)),
    "calendar_risk": ("High/medium impact events in the next 48h and blocked currencies.", {}, lambda c: c.get("calendar", macro.calendar_risk)),
    "watchlist": ("Watchlist engine: every market's best direction, stars, reasons by department.", {}, _watchlist),
    "cot": ("CFTC COT positioning (index 0-100, weekly change) for a market.", {"symbol": SYM}, lambda c, symbol: c.get(f"cot:{symbol}", lambda: market.cot_tool(symbol))),
    "seasonality": ("10-year seasonality for the current month.", {"symbol": SYM}, lambda c, symbol: c.get(f"seas:{symbol}", lambda: market.seasonality_tool(symbol))),
    "smart_bias": ("Composite bias: trend 32%, COT 27%, momentum 18%, rates 13%, seasonality 10%.", {"symbol": SYM}, _bias),
    "topdown": ("Yearly/monthly/weekly/daily open-high-low levels and where price sits.", {"symbol": SYM}, lambda c, symbol: c.get(f"td:{symbol}", lambda: fw.topdown_tool(symbol))),
    "fibonacci": ("Last 4h impulse leg: OTE 0.62-0.79, POP, EQ, extensions.", {"symbol": SYM, "direction": DIR}, lambda c, symbol, direction: c.get(f"fib:{symbol}:{direction}", lambda: fw.fib_tool(symbol, direction))),
    "structure": ("1h SMC/ICT: BOS/CHoCH, order block, FVGs, sweeps, liquidity, unicorn.", {"symbol": SYM, "direction": DIR}, lambda c, symbol, direction: c.get(f"smc:{symbol}:{direction}", lambda: fw.smc_tool(symbol, direction))),
    "technicals": ("EMA9/21 and session VWAP agreement with a direction.", {"symbol": SYM, "direction": DIR}, lambda c, symbol, direction: c.get(f"tech:{symbol}:{direction}", lambda: fw.tech_tool(symbol, direction))),
    "smt": ("SMT divergence across correlated pairs (incl. DXY).", {}, lambda c: c.get("smt", fw.smt_tool)),
    "timing": ("1h entry plan: entry, stop, 2R/3R targets, nearest obstacle, room in R.", {"symbol": SYM, "direction": DIR}, lambda c, symbol, direction: c.get(f"timing:{symbol}:{direction}", lambda: market.timing_tool(symbol, direction))),
    "orderflow": ("Crypto only: delta, CVD, footprint, book walls, absorption (Binance).", {"symbol": SYM}, lambda c, symbol: c.get(f"of:{symbol}", lambda: orderflow_tool(symbol))),
    "wyckoff": ("Wyckoff: trading range, prior trend, spring/upthrust, SOS/SOW, effort vs result.", {"symbol": SYM}, lambda c, symbol: c.get(f"wy:{symbol}", lambda: schools.wyckoff_tool(symbol))),
    "news": ("Upcoming events for the market's currencies + headline sentiment (if a key is set).", {"symbol": SYM}, lambda c, symbol: c.get(f"news:{symbol}", lambda: schools.news_tool(symbol))),
    "sentiment": ("Crowd proxy (RSI + 20d move z-score). Real retail positioning is not available free.", {"symbol": SYM}, lambda c, symbol: c.get(f"sent:{symbol}", lambda: schools.sentiment_tool(symbol))),
    "accounts": ("The three prop accounts: floors, room today, risk per trade, tier rules.", {}, lambda c: _accounts()),
    "position_size": ("Lots per account for an entry and stop.", {"symbol": SYM, "entry": {"type": "number"}, "stop": {"type": "number"}},
                      lambda c, symbol, entry, stop: _size(symbol, float(entry), float(stop))),
    "journal_stats": ("Paper journal results: win rate, avg R, by stars and component.", {},
                      lambda c: {"tool": "journal_stats", "title": "Journal", "source": ["journal"], "data": journal.stats(), "look_at": "نتائج الدفتر"}),
}


def schema(names: list[str]) -> list[dict]:
    out = []
    for n in names:
        desc, params, _ = REGISTRY[n]
        out.append({"type": "function", "function": {"name": n, "description": desc, "parameters": {
            "type": "object", "properties": params, "required": list(params)}}})
    return out


def call(ctx: Ctx, name: str, args: dict) -> tuple[dict, dict]:
    if name not in REGISTRY:
        raise KeyError(f"unknown tool {name}")
    _, params, fn = REGISTRY[name]
    args = {k: v for k, v in (args or {}).items() if k in params}
    if "symbol" in params and args.get("symbol") not in UNIVERSE:
        raise ValueError(f"unknown symbol {args.get('symbol')}")
    if "direction" in params:
        args["direction"] = 1 if int(args.get("direction", 1)) >= 0 else -1
    full = fn(ctx, **args)
    return _slim(full), full


def numbers_in(obj: Any) -> list[float]:
    """Every number inside a tool result (used by the auditor's ledger)."""
    out = []
    if isinstance(obj, bool):
        return out
    if isinstance(obj, (int, float)):
        return [float(obj)]
    if isinstance(obj, dict):
        for v in obj.values():
            out += numbers_in(v)
    elif isinstance(obj, list):
        for v in obj:
            out += numbers_in(v)
    elif isinstance(obj, str):
        import re
        out += [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*\.?\d*", obj) if x not in ("-",)]
    return out


def dumps(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False, default=str)
