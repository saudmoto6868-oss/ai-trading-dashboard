"""XPiX bot + spot: Arabic router, weekly briefing text, analyzer image (real headless Chromium), action runner against a
fake platform, weekly schedule. Telegram itself is faked (nothing is sent). Plain script: python3 tests/test_bot_spot.py"""
import datetime as dt
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import numpy as np
import pandas as pd

from modules import bot_router as R
from modules import spot_outlook as O

# router
cases = {
    "ابعتلي صورة الدهب على الأسبوعي مع اليوت": [{"cmd": "ind", "id": "ew", "on": True}, {"cmd": "shot", "asset": "GOLD", "tf": "1W"}],
    "افتح التايم اند سيلز للبيتكوين": [{"cmd": "panel", "type": "tape"}, {"cmd": "shot", "asset": "BTC", "tf": None}],
    "شيل الجان": [{"cmd": "ind", "id": "gann", "on": False}, {"cmd": "shot", "asset": None, "tf": None}],
    "الدهب هيطلع الاسبوع الجاي؟": [{"cmd": "outlook", "asset": "GOLD"}],
    "وريني المحلل للفضة": [{"cmd": "spotchart", "asset": "SILVER"}],
    "افتح تتبع الأوامر وعمق السوق": [{"cmd": "panel", "type": "limits"}, {"cmd": "panel", "type": "dom"}, {"cmd": "shot", "asset": None, "tf": None}],
    "شوفلي SMT على الايث 4 ساعات": [{"cmd": "ind", "id": "smt", "on": True}, {"cmd": "shot", "asset": "ETH", "tf": "4H"}],
    "ازيك عامل ايه": [],
}
for text, want in cases.items():
    assert R.route(text) == want, (text, R.route(text))
assert R.route("هات فاتورة INV-12")[0]["cmd"] == "ledger"
assert R.platform_symbols("GOLD", ["BTC-USDT", "HL:xyz:GOLD"]) == "HL:xyz:GOLD" and R.platform_symbols("XYZ", ["BTC-USDT"]) is None
assert all(a["cmd"] in ("shot", "panel", "ind", "outlook", "spotchart", "ledger", "ideas") for t in cases for a in R.route(t))   # whitelist only

# fake candles (gold-like weekly ranges)
rng = np.random.default_rng(4)


def frame(base, n=2600):
    c = base * np.exp(np.cumsum(rng.normal(0.0004, 0.01, n)))
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"time": pd.date_range("2018-01-01", periods=n, freq="D"), "open": o, "high": np.maximum(o, c) * 1.004,
                         "low": np.minimum(o, c) * 0.996, "close": c, "volume": 1.0})


B = {"Y:GC=F": frame(1300), "Y:SI=F": frame(17), "Y:HG=F": frame(3)}


def get(sym, tf, limit=300):
    d = B[sym].set_index("time")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    return {"1mo": d.resample("MS").agg(agg).dropna().reset_index(), "1w": d.resample("W").agg(agg).dropna().reset_index().tail(limit)}.get(tf, B[sym].tail(limit)).reset_index(drop=True)


b, msg = O.build("GOLD", get)
o = O.outlook(b)
assert o["atr_w"] > 0 and o["range"][0] < o["price"] < o["range"][1] and o["bias"] in ("up", "down", "flat")
assert "الدهب" in msg and "دولار للأونصة" in msg and "الحركة المعتادة في الأسبوع" in msg and "مش وعد" in msg and "الأسبوع ده" in msg
assert o["down_to"] < o["price"] < o["up_to"]

# bot module with Telegram faked
import xpix_bot as X
sent = []
X.say = lambda t: sent.append(("text", t))
X.send_photo = lambda path, cap="": sent.append(("photo", path, cap))
X.send_doc = lambda name, data, cap="": sent.append(("doc", name))
X.ask_claude = lambda t, deep=False: "LLM: " + t
import modules.spot_outlook as SO
_orig_build = SO.build
SO.build = lambda asset, candles=None: _orig_build(asset, get)
from playwright.sync_api import sync_playwright


class FakePlatform:
    def __init__(self, ctx):
        self.ctx, self.calls = ctx, []

    def x(self, js):
        self.calls.append(js)
        return {"ok": True, "sym": ["BTC-USDT", "ETH-USDT", "HL:xyz:GOLD"], "panels": [{"type": "chart"}]}

    def panel(self, t):
        self.calls.append(("panel", t))
        return {"ok": True}

    def ind(self, i, on=True):
        self.calls.append(("ind", i, on))
        return {"ok": True}

    def shot(self, sym=None, tf=None, out="/tmp/x.png"):
        self.calls.append(("shot", sym, tf))
        return out, None


with sync_playwright() as pw:
    try:
        br = pw.chromium.launch()
    except Exception:   # sandbox: the pre-installed browser of another Playwright version
        br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    ctx = br.new_context()
    p = FakePlatform(ctx)
    X.handle(p, "ابعتلي صورة الدهب على الأسبوعي مع اليوت")
    assert ("ind", "ew", True) in p.calls and ("shot", "HL:xyz:GOLD", "1W") in p.calls
    assert sent[-1][0] == "photo" and "اليوت" in sent[-1][2] and "الأسبوعي" in sent[-1][2]
    X.handle(p, "افتح التايم اند سيلز للبيتكوين")
    assert ("panel", "tape") in p.calls and ("shot", "BTC-USDT", None) in p.calls
    X.handle(p, "صورة DOGE")
    assert "مش في قايمة المنصة" in sent[-1][1]
    X.handle(p, "ازيك عامل ايه")
    assert sent[-1] == ("text", "LLM: ازيك عامل ايه")
    n = len(sent)
    X.handle(p, "الدهب هيطلع الاسبوع الجاي؟")
    ph = [s for s in sent[n:] if s[0] == "photo"]
    assert ph and os.path.getsize(ph[0][1]) > 50_000 and "الدهب" in ph[0][2], sent[n:]
    X.handle(p, "/spotchart GOLD")
    assert sent[-1][0] == "photo" and "محلل السبوت" in sent[-1][2]
    X.handle(p, "/help")
    assert "أوامر XPiX" in sent[-1][1]
    br.close()

# weekly schedule: once per ISO week, only on the day / after the hour
st = os.path.join(tempfile.mkdtemp(), "s.json")
os.environ["XPIX_OUTLOOK_DAY"], os.environ["XPIX_OUTLOOK_HOUR"] = "6", "20"
sun8pm, sun7pm, mon = dt.datetime(2026, 11, 8, 20, 5), dt.datetime(2026, 11, 8, 19, 0), dt.datetime(2026, 11, 9, 21, 0)
assert not X.weekly_due(sun7pm, st) and X.weekly_due(sun8pm, st) and not X.weekly_due(sun8pm, st) and not X.weekly_due(mon, st)
assert X.weekly_due(dt.datetime(2026, 11, 15, 22, 0), st)
print("test_bot_spot OK")
