import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import fred_feed as fr, currents_news as cn

class R:
    def __init__(s, j, code=200): s._j, s.status_code = j, code
    def json(s): return s._j
    def raise_for_status(s): pass

def fake_get(url, params=None, timeout=0):
    sid = params["series_id"]
    if sid == "CPIAUCSL":
        obs = [{"date": f"2026-{12-i:02d}-01", "value": str(110 - i * .5)} for i in range(13)]
        return R({"observations": obs})
    if sid == "DGS10": return R({"observations": [{"date": "2026-09-30", "value": "."}, {"date": "2026-09-29", "value": "4.2"}]})
    return R({"observations": [{"date": "2026-09-01", "value": "4.33"}]})
rows = fr.snapshot("k", fake_get)
cpi = rows[0]; assert cpi["value"] == round((110 / 104 - 1) * 100, 2), cpi
assert rows[2]["value"] == 4.2 and rows[1]["value"] == 4.33
assert "FRED_API_KEY" in fr.snapshot("", fake_get)[0]["note"]
bad = fr.snapshot("k", lambda *a, **k: R({}, 403)); assert "rejected" in bad[0]["note"]
news = cn.fetch(5, key="k", get=lambda *a, **k: R({"news": [{"title": "Gold up", "url": "u", "published": "2026-10-13 04:00:00 +0000"}, {"title": ""}]}))
assert len(news) == 1 and news[0]["title"] == "Gold up"
try: cn.fetch(5, key="k", get=lambda *a, **k: R({"news": []})); raise SystemExit("x")
except RuntimeError: pass
print("fred/currents tests OK")
