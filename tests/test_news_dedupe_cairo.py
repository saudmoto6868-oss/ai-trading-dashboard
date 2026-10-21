"""News phase 1: title de-duplication + Cairo time. Pure mocks, no network."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest import mock
from modules import news_utils as nu, rss_news, world_news

assert nu.norm_title("  Fed HOLDS rates -- again! ") == nu.norm_title("fed holds rates again")
assert nu.norm_title("الاقتصادُ يرتفع") == nu.norm_title("الاقتصاد يرتفع")
assert nu.norm_title("") == ""

items = [{"headline": "Gold hits record", "url": "a", "source": "S1"},
         {"headline": "GOLD hits record!", "url": "b", "source": "S2"},
         {"headline": "Oil falls", "url": "c", "source": "S1"},
         {"headline": "", "url": "d"}, {"headline": "", "url": "e"}]
d = nu.dedupe(items)
assert [x["url"] for x in d] == ["a", "c", "d", "e"], d      # first kept, fields untouched
assert d[0]["headline"] == "Gold hits record" and d[0]["source"] == "S1"

HAS_TZ = nu._CAIRO is not None
if HAS_TZ:
    assert nu.cairo_str(1790000000) == "2026-09-21 17:13 Cairo"   # UTC+3 (summer time)
    assert nu.cairo_str(1768000000) == "2026-01-10 01:06 Cairo"   # UTC+2 (winter)
assert nu.cairo_str(0) == "" and nu.cairo_str(None) == "" and nu.cairo_str("x") == ""


def feed(pub):
    return ("t", "u", "en", "economic", "SRC"), (
        "<rss><channel><item><title>Hello &amp; World</title><link>https://x.com/1</link>"
        "<pubDate>%s</pubDate><description>&lt;b&gt;s&lt;/b&gt;</description></item></channel></rss>" % pub)


f, xml = feed("Mon, 21 Sep 2026 14:13:20 GMT")
r = world_news.parse_rss(xml, f)[0]
assert r["ts"] == 1790000000 and r["headline"] == "Hello & World"
assert r["url"] == "https://x.com/1" and r["source"] == "SRC"
if HAS_TZ:
    assert r["datetime"] == "2026-09-21 17:13 Cairo", r["datetime"]
f, xml = feed("2026-09-21T14:13:20")           # ISO date with no timezone
r = world_news.parse_rss(xml, f)[0]
assert r["ts"] == 0 and r["datetime"] == "", r    # not guessed, not shown
f, xml = feed("garbage")
assert world_news.parse_rss(xml, f)[0]["datetime"] == ""


def fake_one(fd, timeout=8):
    ts = 100 if fd[0] == "a" else 200
    return fd[0], [{"headline": "Same Title", "source": fd[4], "url": "u" + fd[0], "ts": ts}], None


with mock.patch.object(world_news, "_one", fake_one):
    rows, errs = world_news.fetch_world(feeds=[("a", "", "en", "x", "A"), ("b", "", "en", "x", "B")])
assert len(rows) == 1 and rows[0]["source"] == "B" and not errs   # newest copy wins

x = ("<rss><channel><item><title>T</title><link>l</link>"
     "<pubDate>Mon, 21 Sep 2026 14:13:20 +0000</pubDate></item></channel></rss>")
if HAS_TZ:
    assert rss_news.parse_rss(x, "S")[0]["time"] == "2026-09-21 17:13 Cairo"
x = x.replace("+0000", "-0000")   # RFC 2822 "-0000" = timezone unknown
assert rss_news.parse_rss(x, "S")[0]["time"].startswith("Mon, 21 Sep 2026")


class R:
    status_code = 200

    def __init__(self, t):
        self.text = t


def fake_get(url, **k):
    return R("<rss><channel><item><title>Dup news</title><link>l1</link></item></channel></rss>")


with mock.patch.object(rss_news.requests, "get", fake_get):
    out = rss_news.fetch(15)
assert len(out) == 1, out
print("news dedupe + cairo tests OK (tz data: %s)" % HAS_TZ)
