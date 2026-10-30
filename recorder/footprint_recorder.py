"""Always-on footprint recorder (option B of the room plan, owner 2026-10-30): listens to the OKX PUBLIC `trades` WebSocket for a few symbols, sums the prints per 1-minute x price
(buy / sell), keeps 7 days in SQLite, remembers WHEN it was listening (so a gap is never shown as "no trades"), and serves it as JSON for the app's footprint.

  pip install websockets
  SYMBOLS=BTC-USDT,ETH-USDT,XAUT-USDT PORT=8080 DB=fp.sqlite python recorder/footprint_recorder.py

  GET /fp?sym=BTC-USDT&from=<ms>&to=<ms>  ->  {"sym", "cov": [[from, to], ...], "mins": {"<minute ms>": [price, buy, sell, price, buy, sell, ...]}}
  GET /health                              ->  {"ok": true, "symbols": [...], "since": {...}}

`cov` = the time ranges (from, to] in which the recorder was connected and subscribed: inside them the minutes are COMPLETE; outside them nothing is known. Same shape as the
page's own store (modules/workspace_app.html, block FPS). Public data only: no keys, no orders, no user data. CORS is open (read-only market data)."""
from __future__ import annotations

import asyncio
import gzip
import json
import os
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

MIN = 60_000
KEEP = 7 * 86_400_000
MAX_SPAN = 72 * 3_600_000          # one request never returns more than 72 h
OKX_WS = "wss://ws.okx.com/ws/v5/public"


class Store:
    """minute x price sums + the listening runs, in SQLite (":memory:" in tests). Thread-safe."""

    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS fp (sym TEXT, minute INTEGER, px REAL, buy REAL, sell REAL, PRIMARY KEY (sym, minute, px));
            CREATE TABLE IF NOT EXISTS runs (sym TEXT, start INTEGER, last INTEGER, PRIMARY KEY (sym, start));
        """)
        self.seen: dict[str, set] = {}

    def begin(self, sym: str, now: int) -> int:
        """A new listening run starts: nothing before `now` is covered by it."""
        with self.lock:
            self.db.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?)", (sym, now, now)); self.db.commit()
        return now

    def beat(self, sym: str, start: int, now: int) -> None:
        with self.lock:
            self.db.execute("UPDATE runs SET last=? WHERE sym=? AND start=?", (now, sym, start)); self.db.commit()

    def add(self, sym: str, trade_id: str, ts: int, px: float, sz: float, side: str) -> bool:
        """One print. Returns False for a duplicate id (the exchange can resend)."""
        s = self.seen.setdefault(sym, set())
        if trade_id in s:
            return False
        s.add(trade_id)
        if len(s) > 20000:
            for x in list(s)[:5000]:
                s.discard(x)
        m, buy, sell = ts // MIN * MIN, (sz if side == "buy" else 0.0), (sz if side != "buy" else 0.0)
        with self.lock:
            self.db.execute("INSERT INTO fp VALUES (?,?,?,?,?) ON CONFLICT(sym, minute, px) DO UPDATE SET buy=buy+excluded.buy, sell=sell+excluded.sell", (sym, m, px, buy, sell))
        return True

    def commit(self) -> None:
        with self.lock:
            self.db.commit()

    def purge(self, now: int) -> None:
        with self.lock:
            self.db.execute("DELETE FROM fp WHERE minute < ?", (now - KEEP,)); self.db.execute("DELETE FROM runs WHERE last < ?", (now - KEEP,)); self.db.commit()

    def query(self, sym: str, a: int, b: int) -> dict:
        b = min(b, a + MAX_SPAN)
        with self.lock:
            runs = self.db.execute("SELECT start, last FROM runs WHERE sym=? AND last>? AND start<? ORDER BY start", (sym, a, b)).fetchall()
            rows = self.db.execute("SELECT minute, px, buy, sell FROM fp WHERE sym=? AND minute>=? AND minute<? ORDER BY minute, px", (sym, a // MIN * MIN, b)).fetchall()
        cov: list[list[int]] = []
        for s, l in runs:
            s, l = max(s, a), min(l, b)
            if l <= s:
                continue
            if cov and s <= cov[-1][1]:
                cov[-1][1] = max(cov[-1][1], l)
            else:
                cov.append([s, l])
        mins: dict[str, list] = {}
        for m, px, bu, se in rows:
            mins.setdefault(str(m), []).extend([px, bu, se])
        return {"sym": sym, "cov": cov, "mins": mins}

    def since(self, sym: str):
        with self.lock:
            r = self.db.execute("SELECT MIN(start) FROM runs WHERE sym=?", (sym,)).fetchone()
        return r[0] if r else None


def make_handler(store: Store, symbols: set):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code: int, obj: dict):
            body = json.dumps(obj, separators=(",", ":")).encode()
            gz = "gzip" in (self.headers.get("Accept-Encoding") or "") and len(body) > 1024
            if gz:
                body = gzip.compress(body)
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            if gz:
                self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS"); self.end_headers()

        def do_GET(self):
            u = urlparse(self.path); q = parse_qs(u.query)
            if u.path == "/health":
                return self._send(200, {"ok": True, "symbols": sorted(symbols), "since": {s: store.since(s) for s in sorted(symbols)}, "now": int(time.time() * 1000)})
            if u.path != "/fp":
                return self._send(404, {"error": "not found"})
            sym = (q.get("sym") or [""])[0]
            if sym not in symbols:
                return self._send(404, {"error": "symbol not recorded", "symbols": sorted(symbols)})
            try:
                a, b = int((q.get("from") or ["0"])[0]), int((q.get("to") or [str(int(time.time() * 1000))])[0])
            except ValueError:
                return self._send(400, {"error": "from / to must be milliseconds"})
            self._send(200, store.query(sym, a, b))
    return H


async def listen(store: Store, symbols: list, url: str = OKX_WS, connect=None) -> None:
    """Subscribe to the public trades channel for all symbols; on any drop the run ends and a NEW run starts after the reconnect (the hole stays a hole)."""
    if connect is None:
        import websockets
        connect = websockets.connect
    delay = 1
    while True:
        runs: dict[str, int] = {}
        try:
            async with connect(url, ping_interval=20) as ws:
                await ws.send(json.dumps({"op": "subscribe", "args": [{"channel": "trades", "instId": s} for s in symbols]}))
                last_beat = 0.0
                async for raw in ws:
                    now = int(time.time() * 1000)
                    try:
                        m = json.loads(raw)
                    except ValueError:
                        continue
                    if m.get("event") == "subscribe":
                        sym = (m.get("arg") or {}).get("instId")
                        if sym:
                            runs[sym] = store.begin(sym, now)
                        continue
                    for t in m.get("data") or []:
                        sym = t.get("instId") or (m.get("arg") or {}).get("instId")
                        if sym in runs:
                            store.add(sym, str(t["tradeId"]), int(t["ts"]), float(t["px"]), float(t["sz"]), t.get("side", ""))
                    if time.time() - last_beat > 1:
                        last_beat = time.time()
                        for sym, st in runs.items():
                            store.beat(sym, st, now)
                        store.commit()
                delay = 1
        except Exception as e:   # noqa: BLE001 - reconnect on anything
            print("recorder: connection lost:", repr(e)[:120], flush=True)
        await asyncio.sleep(delay)
        delay = min(delay * 2, 30)


def main() -> None:
    symbols = [s.strip() for s in os.environ.get("SYMBOLS", "BTC-USDT,ETH-USDT").split(",") if s.strip()]
    store = Store(os.environ.get("DB", "fp.sqlite"))
    srv = ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), make_handler(store, set(symbols)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def janitor():
        while True:
            time.sleep(3600); store.purge(int(time.time() * 1000))
    threading.Thread(target=janitor, daemon=True).start()
    print("recorder: listening for", symbols, "on port", srv.server_port, flush=True)
    asyncio.run(listen(store, symbols))


if __name__ == "__main__":
    main()
