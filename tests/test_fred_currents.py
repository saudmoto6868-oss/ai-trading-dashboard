import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import currents_news as cn   # 2026-11-20: fred_feed removed (unused; FRED lives in fred_regime / macro_fund)

class R:
    def __init__(s, j, code=200): s._j, s.status_code = j, code
    def json(s): return s._j
    def raise_for_status(s): pass

news = cn.fetch(5, key="k", get=lambda *a, **k: R({"news": [{"title": "Gold up", "url": "u", "published": "2026-10-13 04:00:00 +0000"}, {"title": ""}]}))
assert len(news) == 1 and news[0]["title"] == "Gold up"
try: cn.fetch(5, key="k", get=lambda *a, **k: R({"news": []})); raise SystemExit("x")
except RuntimeError: pass
print("currents tests OK")
