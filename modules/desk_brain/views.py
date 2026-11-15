"""Data for the framework tabs: Watchlist, Levels & Structure, Order Flow, Routine."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from . import risk
from .config import UNIVERSE
from .data import sources
from .data.cache import cached
from .tools import framework as fw
from .tools import macro
from .tools.orderflow import orderflow_tool

_pool = ThreadPoolExecutor(max_workers=8)


def _strip(row: dict) -> dict:
    return {k: v for k, v in row.items() if k != "_tools"}


def watchlist(last: dict | None = None) -> dict:
    """Score every market. Bias comes from the last desk scan when there is one."""
    def build():
        cal = macro.calendar_risk()
        smt = fw.smt_tool()
        matrix = {r["symbol"]: r for r in (last or {}).get("matrix", [])}
        def one(sym):
            of = orderflow_tool(sym) if UNIVERSE[sym].get("binance") else None
            return _strip(fw.watchlist_row(sym, smt, cal["data"]["blocked"], matrix.get(sym), of))
        rows = list(_pool.map(one, UNIVERSE))
        rows.sort(key=lambda r: (not r["promoted"], -r["score"]))
        srcs = sorted({s for r in rows for s in r["source"]} | set(cal["source"]) | set(smt["source"]))
        return {"rows": rows, "smt": smt, "calendar": cal["data"], "source": srcs, "has_bias": bool(matrix),
                "time": datetime.now(timezone.utc).isoformat()}
    key = f"wl:{(last or {}).get('time', 0)}"
    return cached(key, 300, build, disk=False)


def analyze(symbol: str, direction: int | None = None) -> dict:
    if symbol not in UNIVERSE:
        raise KeyError(symbol)
    if direction is None:
        wl = fw.watchlist_row(symbol, fw.smt_tool(), macro.calendar_risk()["data"]["blocked"], None)
        direction, t = wl["direction"], wl["_tools"]
        td, fib, smc, tech = t["topdown"], t["fib"], t["smc"], t["tech"]
    else:
        td, fib, smc, tech = (fw.topdown_tool(symbol), fw.fib_tool(symbol, direction),
                              fw.smc_tool(symbol, direction), fw.tech_tool(symbol, direction))
    sc = fw.scenarios(symbol, direction, td, smc, fib)
    return {"symbol": symbol, "direction": direction, "topdown": td, "fib": fib, "smc": smc, "tech": tech,
            "scenarios": sc, "orderflow": orderflow_tool(symbol)}


def routine(last: dict | None = None) -> dict:
    """Pre-market checklist, filled automatically where the desk can check it."""
    cal = macro.calendar_risk()
    now = datetime.now(timezone.utc)
    overnight = []
    for sym in UNIVERSE:
        df, src = sources.prices(UNIVERSE[sym]["yf"], "1h")
        asia = df[df.index >= now.replace(hour=0, minute=0, second=0, microsecond=0)]
        asia = asia[asia.index.hour < 7]
        if len(asia):
            overnight.append({"symbol": sym, "high": float(asia["High"].max()), "low": float(asia["Low"].min()),
                              "last": float(df["Close"].iloc[-1]), "source": src})
    wl = watchlist(last)
    top = [r for r in wl["rows"] if r["promoted"]][:6]
    rs = risk.state()
    checks = [
        {"id": "calendar", "text": "راجعت الأجندة الاقتصادية لليوم", "auto": True,
         "ok": True, "detail": f"{len(cal['data']['events'])} حدث خلال 48 ساعة؛ ممنوع الدخول على: {', '.join(cal['data']['blocked']) or 'لا شيء'}"},
        {"id": "overnight", "text": "حددت مستويات الليلة (جلسة آسيا) والمستويات السابقة", "auto": True,
         "ok": bool(overnight), "detail": f"{len(overnight)} سوق لها نطاق آسيوي اليوم"},
        {"id": "htf", "text": "أكدت انحياز الفريمات الكبيرة (Top-down)", "auto": True,
         "ok": True, "detail": "من تاب Watchlist: عمود Top-down"},
        {"id": "watchlist", "text": "مسحت الـ Watchlist واخترت أفضل 3 أسواق", "auto": True,
         "ok": bool(top), "detail": ", ".join(f"{r['symbol']} {'▲' if r['direction'] > 0 else '▼'} {'★' * r['stars']}" for r in top) or "لا سوق ترقّى اليوم"},
        {"id": "accounts", "text": "حدّثت أرصدة الحسابات الثلاثة وحد الخسارة اليومي", "auto": False, "ok": None,
         "detail": " · ".join(f"{a['name']}: مساحة اليوم ${a['room_today']:,.0f}" for a in rs["accounts"])},
        {"id": "scenarios", "text": "كتبت 2 أو 3 سيناريوهات لكل سوق قبل وصول السعر للمستوى", "auto": False, "ok": None,
         "detail": "من تاب المستويات والهيكل"},
        {"id": "mind", "text": "حالتي النفسية مستقرة: لا انتقام من خسارة أمس، ولا زيادة حجم", "auto": False, "ok": None, "detail": ""},
    ]
    rules = ["لا تداول انتقامي بعد خسارة.",
             "عند الوصول لحد الخسارة اليومي الشخصي: قفل التداول حتى الجلسة التالية.",
             "لا زيادة في حجم الصفقة لتعويض خسارة.",
             "حدود الحساب اليومية والكلية حدود صلبة، وليست اقتراحات.",
             "لا دخول من قراءة دفتر الأوامر وحدها: الشارت لازم يؤكد.",
             "الحساب الممول (Account 3) لصفقات A+++ فقط، ومع سقف ربح يومي."]
    return {"checks": checks, "rules": rules, "overnight": overnight, "calendar": cal["data"],
            "discipline": rs["discipline"], "time": now.isoformat()}
