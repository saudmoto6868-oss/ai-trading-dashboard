"""Price alarms checked on the server (owner 2026-11-21: "GitHub every 30 min"), page open or not.

sync(req)  - called by the Workspace through the hidden bridge (modules/guide_ai.render_bridge): stores the browser's alarms in
             the online store (palarms.json next to the Spot ledger: SPOT_GH_TOKEN + SPOT_GH_REPO) and hands back the merged list.
run()      - the GitHub Actions job (every ~30 min, GitHub may delay it): loads palarms.json, checks every active alarm against
             live candles (modules/palarm_core.py, the same rules as the browser), sends each hit to Telegram (bot secrets),
             ntfy (if the alarm has phone push on) and a CallMeBot Telegram call (if call is on), then saves the fired state.
No online store = both do nothing (a CI runner's disk is empty). Run: python -m modules.palarm_server"""
from __future__ import annotations

import sys
import time

import pandas as pd

from modules import palarm_core as P

FILE = "palarms.json"
WINDOW = 90 * 60000   # runs are every ~30 min but GitHub can delay them; overlap is safe (a fire moves lastT forward)


def _store():
    from modules.spot_store import get_store
    return get_store()


def sync(req: dict, store=None) -> dict:
    out = {"id": req.get("id"), "kind": "palarms"}
    st = store or _store()
    if st.kind != "github" and store is None:
        return {**out, "ok": False, "err": "no online store (SPOT_GH_TOKEN / SPOT_GH_REPO) - alarms are checked only while the page is open"}
    try:
        d = st.get_json(FILE) or {}
        merged = P.merge(d.get("alarms", []), req.get("list") if isinstance(req.get("list"), list) else [])
        nt = req.get("notify") if isinstance(req.get("notify"), dict) else {}
        notify = {k: str(nt.get(k) or "")[:120] for k in ("ntfy", "tg")}   # topic / CallMeBot user only; no keys leave the browser
        if merged != d.get("alarms") or notify != d.get("notify"):
            st.put_json(FILE, {"alarms": merged, "notify": notify, "t": int(time.time() * 1000)}, "palarms: sync from the Workspace")
        return {**out, "ok": True, "list": merged}
    except Exception as e:
        return {**out, "ok": False, "err": f"{type(e).__name__}: {e}"[:200]}


def _ms(t) -> int:
    return int(pd.Timestamp(t).timestamp() * 1000)


def _rows(sym: str, tf: str) -> list[dict]:
    from modules.market_cache import get_klines
    df = get_klines(sym, tf, 300)
    return [{"t": _ms(r.time), "h": float(r.high), "l": float(r.low), "c": float(r.close)} for r in df.itertuples()]


def _send_all(a: dict, px, notify: dict, send, http) -> None:
    title, msg, ch = "⏰ " + (a.get("name") or a["sym"]), P.text(a, px), a.get("ch") or {}
    err = send(f"<b>{title}</b>\n{msg}\n<i>(server check, every ~30 min)</i>")
    if err:
        print("palarms: telegram:", err)
    if ch.get("push") and notify.get("ntfy"):
        try:
            http.post("https://ntfy.sh/" + notify["ntfy"], data=msg.encode("utf8"), timeout=10,
                      headers={"Title": "".join(c for c in title if 32 <= ord(c) < 127).strip() or "Alarm", "Priority": "5", "Tags": "rotating_light"})
        except Exception as e:
            print("palarms: ntfy:", type(e).__name__)
    if ch.get("call") and notify.get("tg"):
        try:
            http.get("https://api.callmebot.com/start.php", params={"user": notify["tg"], "text": msg, "lang": "en-US-Standard-B", "rpt": 2}, timeout=20)
        except Exception as e:
            print("palarms: call:", type(e).__name__)


def run(store=None, rows=None, send=None, http=None, now=None, log=print) -> int:
    st = store or _store()
    if st.kind != "github" and store is None:
        log("palarms: no online store (SPOT_GH_TOKEN / SPOT_GH_REPO not set) - skipped")
        return 0
    d = st.get_json(FILE) or {}
    alarms = d.get("alarms", [])
    if not any(a.get("on") for a in alarms):
        log("palarms: none active")
        return 0
    rows = rows or _rows
    if send is None:
        from modules.telegram_alerts import send
    if http is None:
        import requests as http
    now = now or int(time.time() * 1000)
    cache, fired, dirty = {}, 0, False

    def get(sym, tf):
        if (sym, tf) not in cache:
            try:
                cache[(sym, tf)] = rows(sym, tf)
            except Exception as e:
                log(f"palarms: {sym} {tf}: {type(e).__name__}")
                cache[(sym, tf)] = []
        return cache[(sym, tf)]

    for a in alarms:
        if not a.get("on") or not a.get("sym"):
            continue
        tf_rows, m1 = get(a["sym"], P.tf_server(a.get("tf"))), get(a["sym"], "1m")
        if not tf_rows or not m1:
            continue
        # look back over the 1m bars since the last edit / fire, at most WINDOW: a cross between two runs is caught from their high / low
        since = max(a.get("editT") or 0, a.get("lastT") or 0, now - WINDOW)
        before_b = [r for r in m1 if r["t"] < since]
        span = [r for r in m1 if r["t"] >= since]
        p0 = before_b[-1]["c"] if before_b else (span[0]["c"] if span else None)   # short feed: the window's first close
        stt = {"p0": p0, "p1": m1[-1]["c"], "curT": tf_rows[-1]["t"], "rows": tf_rows,
               "hi": max(r["h"] for r in span) if span else None, "lo": min(r["l"] for r in span) if span else None}
        was = [a.get(k) for k in P.FIRE_STATE]
        px = P.check(a, stt, now)
        if px is not None:
            fired += 1
            _send_all(a, px, d.get("notify") or {}, send, http)
        dirty = dirty or was != [a.get(k) for k in P.FIRE_STATE]
    if dirty:
        d["alarms"], d["t"] = alarms, now
        st.put_json(FILE, d, f"palarms: server check ({fired} fired)")
    log(f"palarms: {sum(1 for a in alarms if a.get('on'))} active, {fired} fired")
    return fired


if __name__ == "__main__":
    try:
        run()
    except Exception as e:   # never fail the whole alerts job
        print("palarms: error", type(e).__name__, e)
    sys.exit(0)
