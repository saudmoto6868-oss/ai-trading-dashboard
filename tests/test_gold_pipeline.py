"""HL:xyz:GOLD end to end on the server side with a MOCKED Hyperliquid (fixed candles): candleSnapshot -> market_cache.fetch_frames -> scan_symbol for 1h / 1d / 1w, scored the same as a crypto symbol on the same candles. Not a live test. Run: python tests/test_gold_pipeline.py"""
import sys, math, time
import os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import modules.hl_feed as hl
MS = hl.MS
def candles(iv, n=400):
    step = int(MS[iv]); end = int(time.time()*1000)//step*step; out = []; px = 2500.0
    for i in range(n):
        t = end - (n-1-i)*step
        if i < n-30: px += 6*math.sin(i/11) - 0.4      # choppy, slightly down
        else: px += 7 + (i-(n-30))*0.5                  # last 30 bars: strong impulsive rally through the old highs
        o = px - (5 if i >= n-30 else 0); c = px; h = max(o, c)+3; l = min(o, c)-3
        out.append({"t": t, "o": str(o), "h": str(h), "l": str(l), "c": str(c), "v": str(100 if i < n-30 else 400)})
    return out
def fake_post(body, timeout=12):
    if body.get("type") == "candleSnapshot":
        r = body["req"]; assert r["coin"] == "xyz:GOLD", r["coin"]; return candles(r["interval"])
    if body.get("type") == "metaAndAssetCtxs":
        return ({"universe": [{"name": "xyz:GOLD"}, {"name": "xyz:CL"}]}, [{"midPx": "2600", "dayNtlVlm": "9e8", "openInterest": "1e6", "prevDayPx": "2590"}, {"midPx": "70", "dayNtlVlm": "5e8", "openInterest": "1e6", "prevDayPx": "69"}])
    raise RuntimeError("unexpected "+str(body))
hl._post = fake_post
from modules.market_cache import fetch_frames
from modules.scorer import scan_symbol, fetch_tfs, SCAN_TFS
print("SCAN_TFS", SCAN_TFS)
for tf in SCAN_TFS:
    fr1, e1 = fetch_frames(["HL:xyz:GOLD"], fetch_tfs(tf))
    r1 = scan_symbol("HL:xyz:GOLD", fr1["HL:xyz:GOLD"], tf, peers=None)
    assert r1["direction"] == "bullish" and not e1, (tf, r1.get("direction"), e1)
    print(tf, "OK score", r1["score"], "/", r1["max_score"], r1["direction"], r1["trade_type"])
fr, errs = fetch_frames(["HL:xyz:GOLD"], fetch_tfs("1h"))
a = scan_symbol("HL:xyz:GOLD", fr["HL:xyz:GOLD"], "1h", peers=None)
b = scan_symbol("BTC-USDT", fr["HL:xyz:GOLD"], "1h", peers=None)
assert a["direction"] == "bullish" and a["score"] >= 1, a
assert (a["score"], a["direction"], a["reasons"]) == (b["score"], b["direction"], b["reasons"]), "gold must score like any symbol on the same candles"
assert hl.category("HL:xyz:GOLD") == "Metals"
print("ok gold pipeline (mock Hyperliquid, fixed candles)")
