"""modules/tclass_cron.py on mocked candles (no network, no Telegram): finds the range-bottom long, sends only at-zone + strong trades,
remembers what was sent (no resend within 12 h). Run: python3 tests/test_tclass_cron.py"""
import io
import math
import os
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import pandas as pd  # noqa: E402

from modules import market_cache, tclass_cron as C  # noqa: E402
from modules import telegram_alerts as T  # noqa: E402


def frame(n, tf):
    cl, o, rows = [60500 + 500 * math.sin(2 * math.pi * i / 40 - math.pi / 2) + 15 * math.sin(i * 12.9898) for i in range(n)], None, []
    for i, c in enumerate(cl):
        o = c if o is None else o; w = 40 * (1 + 0.5 * abs(math.sin(i * 7.31)))
        rows.append({"open": o, "high": max(o, c) + w, "low": min(o, c) - w, "close": c, "volume": 1.0}); o = c
    return pd.DataFrame(rows)


market_cache.get_klines = lambda sym, tf, limit=300: frame(400, tf).tail(limit).reset_index(drop=True)
os.environ.update({"TC_SYMBOLS": "BTC-USDT", "TC_STYLES": "Day Trade,Swing", "TC_MIN": "4"})
os.environ["TC_STATE"] = C.STATE = os.path.join(tempfile.mkdtemp(), "s.json")
from pathlib import Path  # noqa: E402
C.STATE = Path(C.STATE)

buf = io.StringIO()
with redirect_stdout(buf):
    assert C.main(["--dry"]) == 0
out = buf.getvalue()
assert "2 candidates" in out, out[:300]          # one best idea per symbol x 2 styles, judged (the mock range is a WAIT: nothing to send)
from modules import tclass as TCm  # noqa: E402
real_scan = TCm.scan
r = real_scan("BTC-USDT", "Swing", market_cache.get_klines)
assert r and r[0]["j"]["pros"] is not None and r[0]["j"]["verdict"] in ("TAKE", "WAIT", "SKIP")
# a forced TAKE goes out once, a WAIT / SKIP never, and no resend within 12 h
take = dict(r[0], now=True, j=dict(r[0]["j"], verdict="TAKE", score=4.5))
wait = dict(r[0], det="struct", j=dict(r[0]["j"], verdict="WAIT", score=4.5))
TCm.scan = lambda s_, st, gk, target_pts=0: [take] if st == "Swing" else [wait]
sent_msgs = []
T.send = lambda text, token=None, chat=None: sent_msgs.append(text) or None
with redirect_stdout(io.StringIO()):
    assert C.main([]) == 0
assert len(sent_msgs) == 1 and "ادخل" in sent_msgs[0], sent_msgs
with redirect_stdout(io.StringIO()):
    C.main([])
assert len(sent_msgs) == 1, "re-sent the same trade within 12 h"
TCm.scan = real_scan
print("ok tclass cron: dry run judges every symbol, only TAKE is sent, once")
