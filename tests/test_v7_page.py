"""modules/v7_page.py: loader, grouping and the page's hard limits (no signals / orders). Plain script, no network, no Streamlit."""
import json, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import v7_page as V

SRC = os.path.join(os.path.dirname(V.__file__), "v7_page.py")


def _write(d, S, C):
    json.dump(S, open(os.path.join(d, "sources.json"), "w")); json.dump(C, open(os.path.join(d, "claims.json"), "w"))


def _claim(i, cat, status="unverified"):
    return {"id": i, "source_id": "s1", "timestamp_or_locator": "x", "claim": "c", "category": cat, "status": status, "confidence": "high"}


def test_loader_and_grouping():
    with tempfile.TemporaryDirectory() as d:
        _write(d, [{"id": "s1", "fetched": "2026-11-10"}], [_claim("a", "indicator"), _claim("b", "project-setting"), _claim("c", "backtest"), _claim("d", "smc", "measured")])
        r = V.load(d)
        assert r["error"] == "" and len(r["claims"]) == 4
        s = V.summarize(r)
        assert (s["market"], s["project"], s["own"], s["measured"], s["pct_tested"]) == (2, 1, 1, 1, 50.0), s
    print("ok loader and grouping")


def test_broken_data_gives_error_and_no_rows():
    with tempfile.TemporaryDirectory() as d:
        r = V.load(d)   # files missing
        assert r["error"] and r["claims"] == [] and r["sources"] == []
        open(os.path.join(d, "sources.json"), "w").write("{not json"); open(os.path.join(d, "claims.json"), "w").write("[]")
        r = V.load(d)
        assert r["error"] and r["claims"] == []
        _write(d, [{"id": "s1"}], [dict(_claim("a", "smc"), source_id="nope")])
        assert "unknown source" in V.load(d)["error"]
        bad = _claim("a", "smc"); del bad["status"]
        _write(d, [{"id": "s1"}], [bad])
        assert "lacks 'status'" in V.load(d)["error"]
    print("ok broken data")


def test_page_has_no_signal_or_order_controls():
    t = open(SRC, encoding="utf-8").read()
    assert "st.button" not in t and "st.form" not in t, "no action controls on a research page"
    assert not re.search(r"\b(BUY|SELL|LONG|SHORT)\b", t), "no signal wording"
    print("ok no signals / orders")


def test_real_data_if_present():
    r = V.load()
    if not os.path.isdir(V.DATA):
        print("skip real data (data/v7 absent)"); return
    assert r["error"] == "", r["error"]
    s = V.summarize(r)
    assert s["sources"] > 0 and s["claims"] == s["market"] + s["project"] + s["own"]
    print("ok real data", s)


def test_dashboard_inlines_scripts_and_fails_closed():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "vendor"))
        open(os.path.join(d, "index.html"), "w").write("<html>" + V._LIB_TAG + V._DATA_TAG + "</html>")
        open(os.path.join(d, "vendor", "lightweight-charts.standalone.production.js"), "w").write("var LW=1;/* </script> */")
        open(os.path.join(d, "data.js"), "w").write("window.CFX_DATA={};")
        html, err = V.dashboard_html(d)
        assert err == "" and "var LW=1" in html and "window.CFX_DATA" in html
        assert 'src="data.js"' not in html and 'src="vendor' not in html, "external scripts must be inlined"
        assert html.count("</script>") == 2, "a </script> inside a library must not close the tag early"
        open(os.path.join(d, "index.html"), "w").write("<html>no tags</html>")
        h2, e2 = V.dashboard_html(d)
        assert h2 == "" and "no longer references" in e2
        h3, e3 = V.dashboard_html(os.path.join(d, "missing"))
        assert h3 == "" and e3
    print("ok dashboard inlining")


def test_live_html_builds():
    if not os.path.exists(V.LIVE_LIB):
        print("skip live html (chart library absent)"); return
    html, err = V.live_html()
    assert err == "" and "V7IND" in html and "createChart" in html, err
    assert "/*LIB*/" not in html and "/*IND*/" not in html and 'src="' not in html, "everything must be inlined"
    print("ok live html")


if __name__ == "__main__":
    test_live_html_builds(); test_loader_and_grouping(); test_broken_data_gives_error_and_no_rows(); test_page_has_no_signal_or_order_controls(); test_real_data_if_present(); test_dashboard_inlines_scripts_and_fails_closed()
    print("ALL V7 PAGE TESTS PASSED")
