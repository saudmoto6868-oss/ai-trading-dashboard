"""Price alarms, pure logic shared by the server check (modules/palarm_cron.py) and the browser (modules/ws/21d_price_alarms.js).

hit / check / text are a line-by-line port of the PALARM-PURE block in the JS (tests/test_palarm_server.py runs both on the same
cases). One server-only extra: the job runs every ~30 min, so a cross between two runs is caught from the 1m high / low of the
bars since the last check (hi / lo), not only from two prices 30 min apart.
merge() joins the browser's list with the stored one: the browser owns which alarms exist and their settings; the side that
fired last owns the fired state (so an alarm the server fired while the page was closed does not fire again in the browser)."""
from __future__ import annotations

from datetime import datetime, timezone

CONDS = {"cross": "Crossing", "up": "Crossing Up", "down": "Crossing Down", "gt": "Greater Than", "lt": "Less Than",
         "enter": "Entering Channel", "exit": "Exiting Channel", "inside": "Inside Channel", "outside": "Outside Channel",
         "mup": "Moving Up", "mdn": "Moving Down", "mupp": "Moving Up %", "mdnp": "Moving Down %"}
CH = {"enter", "exit", "inside", "outside"}
MOVE = {"mup", "mdn", "mupp", "mdnp"}
FIRE_STATE = ("on", "status", "lastT", "fired", "lastBar", "lastClose")


def hit(a: dict, p0, p1, closes=None, hi=None, lo=None) -> bool:
    v, v2 = a["v"], a.get("v2")
    lo_c, hi_c = min(v, v if v2 is None else v2), max(v, v if v2 is None else v2)
    ins = lambda p: lo_c <= p <= hi_c   # noqa: E731
    top, bot = max(p1, hi) if hi is not None else p1, min(p1, lo) if lo is not None else p1   # server: the range since the last check
    c = a.get("cond")
    if c == "cross":
        return p0 is not None and ((p0 < v and top >= v) or (p0 > v and bot <= v))
    if c == "up":
        return p0 is not None and p0 < v and top >= v
    if c == "down":
        return p0 is not None and p0 > v and bot <= v
    if c == "gt":
        return p1 > v
    if c == "lt":
        return p1 < v
    if c == "enter":
        return p0 is not None and not ins(p0) and ins(p1)
    if c == "exit":
        return p0 is not None and ins(p0) and not ins(p1)
    if c == "inside":
        return ins(p1)
    if c == "outside":
        return not ins(p1)
    if c in MOVE:
        n, cl = max(1, int(a.get("n") or 0)), closes or []
        if len(cl) <= n:
            return False
        ref = cl[-1 - n]
        d = p1 - ref
        pct = d / ref * 100 if ref else 0
        return {"mup": d >= v, "mdn": -d >= v, "mupp": pct >= v, "mdnp": -pct >= v}[c]
    return False


def check(a: dict, st: dict, now: int):
    """st = {p0, p1, curT, rows:[{t,c}] oldest..newest incl. the running bar, hi?, lo?} -> trigger price or None; updates a."""
    if not a.get("on"):
        return None
    if a.get("exp") and now > a["exp"]:
        a["on"], a["status"] = False, "expired"
        return None
    rows = st.get("rows") or []
    closes = [r["c"] for r in rows]
    px = None
    if a.get("trig") == "close":   # closed bars only, once per newly closed bar
        cl = rows[:-1]
        last = cl[-1] if cl else None
        if not last or a.get("lastClose") == last["t"]:
            return None
        first = a.get("lastClose") is None
        a["lastClose"] = last["t"]
        if first:
            return None
        if hit(a, cl[-2]["c"] if len(cl) > 1 else None, last["c"], [r["c"] for r in cl]):
            px = last["c"]
    else:
        if st.get("p1") is None or not hit(a, st.get("p0"), st["p1"], closes, st.get("hi"), st.get("lo")):
            return None
        if a.get("trig") == "bar" and a.get("lastBar") == st.get("curT"):
            return None
        if a.get("trig") == "min" and a.get("lastT") and now - a["lastT"] < 60000:
            return None
        px = st["p1"]
        a["lastBar"] = st.get("curT")
    if px is None:
        return None
    a["lastT"] = now
    a["fired"] = (a.get("fired") or 0) + 1
    if a.get("trig") == "once":
        a["on"], a["status"] = False, "triggered"
    return px


def _num(x) -> str:   # the JS prints 101.5 / 100 (no trailing .0)
    return str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)


def text(a: dict, px, now: datetime | None = None) -> str:
    cond = CONDS.get(a.get("cond"), a.get("cond"))
    dflt = f"{a['sym']} {cond} {_num(a['v'])}" + (f" / {_num(a['v2'])}" if a.get("v2") is not None and a.get("cond") in CH else "")
    t = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M") + " UTC"
    return (str(a.get("msg") or dflt).replace("{{ticker}}", a["sym"]).replace("{{close}}", _num(px))
            .replace("{{interval}}", a.get("tf") or "").replace("{{time}}", t))


def merge(server: list, client: list) -> list:
    """Browser list = which alarms exist + their settings. Fired state comes from whichever side fired after the last edit."""
    srv = {a.get("id"): a for a in server or [] if isinstance(a, dict)}
    out = []
    for c in client or []:
        if not isinstance(c, dict) or not c.get("id") or not isinstance(c.get("v"), (int, float)):
            continue   # trust boundary: the list comes from the browser
        a = dict(c)
        s = srv.get(a["id"])
        if s:
            if (s.get("lastT") or 0) > max(a.get("lastT") or 0, a.get("editT") or 0):
                for k in FIRE_STATE:
                    if k in s:
                        a[k] = s[k]
        out.append(a)
    return out


def tf_server(tf: str) -> str:
    """Workspace tf ('1H', '4H', '1D', '5m') -> market_cache tf ('1h', '4h', '1d', '5m')."""
    tf = (tf or "1m").strip()
    return tf[:-1] + tf[-1].lower() if tf[-1:] in ("H", "D", "W") else tf
