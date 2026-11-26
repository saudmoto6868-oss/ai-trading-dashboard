"""M1 1.4: OKX hub (WSX) and Hyperliquid socket reconnect with backoff 3 s -> 30 s plus jitter, never stack ping timers, and idle Hyperliquid trade feeds are unsubscribed.
Real headless Chromium with a fake WebSocket, network blocked (MOCK-TESTED ONLY). Run: python3 tests/test_ws_hardening_browser.py"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules.workspace import build_workspace_html  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP: playwright not installed (CI installs it from requirements-dev.txt)")
    sys.exit(0)

html = build_workspace_html(["BTC-USDT"], lang="en")
path = os.path.join(tempfile.mkdtemp(), "ws.html")
open(path, "w", encoding="utf-8").write(html)

FAKE_WS = """window.__fws = []; window.WebSocket = class { constructor(u){ this.url = u; this.sent = []; this.readyState = 0; window.__fws.push(this); }
  send(m){ this.sent.push(m); } close(){ this.readyState = 3; this.onclose && this.onclose({code:1006}); } };"""

CHECK = """() => {
  const out = {}, st = window.setTimeout, si = window.setInterval, ci = window.clearInterval, live = new Set(), delays = [];
  window.setInterval = (f, ms) => { const id = si(f, ms); if (ms === 20000 || ms === 30000) live.add(id); return id; };
  window.clearInterval = id => { live.delete(id); return ci(id); };
  // OKX hub: two opens on one socket leave one ping timer; closes back off 3 -> 30 s with < 1 s jitter; a good open resets
  const c = WSX.conn("hardening-test"), ws1 = window.__fws[window.__fws.length - 1];
  ws1.onopen(); ws1.onopen(); out.wsxPings = live.size;
  window.setTimeout = (f, ms) => { delays.push(ms); return 0; };
  for (let i = 0; i < 6; i++) ws1.onclose();
  window.setTimeout = st;
  out.wsxDelays = delays.splice(0); out.wsxPingsAfterClose = live.size;
  ws1.onopen(); out.wsxWaitReset = c.wait; ws1.onclose();
  // Hyperliquid socket: same backoff (cap 30 s) and one ping timer
  live.clear(); HL.on = true; HL.sock(); const h = window.__fws[window.__fws.length - 1];
  h.onopen(); h.onopen(); out.hlPings = live.size;
  window.setTimeout = (f, ms) => { delays.push(ms); return 0; };
  for (let i = 0; i < 6; i++) h.onclose();
  window.setTimeout = st; out.hlDelays = delays.splice(0);
  // idle trade feeds: subscribed on first ask, unsubscribed after 60 s with no ask, recent ones kept
  const fake = {sent:[], send(m){ this.sent.push(m); }}; HL.ws = fake; HL.seedT = {AAA: Date.now(), BBB: Date.now()};
  HL.tr.AAA = {ids:new Set(), rows:Array(20).fill({ts:"1"})}; HL.tr.BBB = {ids:new Set(), rows:Array(20).fill({ts:"1"})};
  HL.trades("AAA"); HL.trades("BBB"); HL.trAsk.AAA = Date.now() - 61000; HL.trSweep();
  out.hlSub = HL.trSub.has("AAA") + "," + HL.trSub.has("BBB") + "," + ("AAA" in HL.tr);
  out.hlMsgs = fake.sent.map(m => JSON.parse(m)).map(m => m.method + ":" + m.subscription.coin);
  HL.ws = null; window.setInterval = si; window.clearInterval = ci; return out; }"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page(viewport={"width": 1400, "height": 900})
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)[:160]))
    p.route("**/*", lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())
    p.add_init_script(FAKE_WS)
    p.goto("file://" + path + "?blank=1")
    p.wait_for_timeout(1500)
    o = p.evaluate(CHECK)
    b.close()

def ok_backoff(d):
    base = [3000, 6000, 12000, 24000, 30000, 30000]
    return len(d) == 6 and all(x <= y < x + 1000 for x, y in zip(base, d))

assert o["wsxPings"] == 1, ("OKX hub: one ping timer after a second open", o)
assert o["wsxPingsAfterClose"] == 0, ("OKX hub: ping timer cleared on close", o)
assert ok_backoff(o["wsxDelays"]), ("OKX hub backoff 3 -> 30 s with jitter", o["wsxDelays"])
assert o["wsxWaitReset"] == 3000, ("OKX hub: a good open resets the wait", o)
assert o["hlPings"] == 1, ("Hyperliquid: one ping timer after a second open", o)
assert ok_backoff(o["hlDelays"]), ("Hyperliquid backoff 3 -> 30 s with jitter", o["hlDelays"])
assert o["hlSub"] == "false,true,false", ("idle coin dropped, recent coin kept", o)
assert o["hlMsgs"] == ["subscribe:AAA", "subscribe:BBB", "unsubscribe:AAA"], o["hlMsgs"]
assert not errs, errs
print("ok ws hardening:", [round(x) for x in o["wsxDelays"]], o["hlSub"], o["hlMsgs"])
