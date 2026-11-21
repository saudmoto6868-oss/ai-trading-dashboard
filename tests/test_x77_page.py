"""AppTest for the X77 page: it renders and saves a text item. Run: python3 -I tests/test_x77_page.py"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

with tempfile.TemporaryDirectory() as t:
    os.environ["X77_DATA_DIR"] = str(Path(t) / "x77")
    from streamlit.testing.v1 import AppTest  # noqa: E402

    script = ROOT / "tests" / "_x77_page_app.py"
    script.write_text(
        "import sys\nsys.path.insert(0, %r)\nfrom modules.x77_page import render\nrender()\n" % str(ROOT),
        encoding="utf-8",
    )
    try:
        at = AppTest.from_file(str(script), default_timeout=30).run()
        assert not at.exception, at.exception
        at.text_area[0].input("AppTest text item")
        at.button[0].click().run()
        assert not at.exception, at.exception
        from modules import x77_store as store
        items = store.list_items(base=Path(t) / "x77")
        assert len(items) == 1 and items[0]["text"] == "AppTest text item", items

        # Arabic mode (owner: explanations in Arabic): labels switch, guide is there
        at = AppTest.from_file(str(script), default_timeout=30)
        at.session_state["ws_lang"] = "ar"
        at.run()
        assert not at.exception, at.exception
        assert any(b.label == "احفظ في X77" for b in at.button), [b.label for b in at.button]
        assert any("بيشتغل إزاي" in e.label for e in at.expander), [e.label for e in at.expander]

        # Radar send box: saves a 'setup' with symbol + timeframe tags
        script.write_text(
            "import sys\nsys.path.insert(0, %r)\nfrom modules.x77_page import send_box\nsend_box(['ETH-USDT'])\n" % str(ROOT),
            encoding="utf-8",
        )
        at = AppTest.from_file(str(script), default_timeout=30).run()
        assert not at.exception, at.exception
        at.text_input[0].input("bull flag")
        at.button[0].click().run()
        assert not at.exception, at.exception
        setups = store.list_items("setup", base=Path(t) / "x77")
        assert len(setups) == 1 and setups[0]["text"] == "ETH-USDT 1h bull flag", setups
        assert "radar" in setups[0]["tags"], setups
    finally:
        script.unlink(missing_ok=True)
print("x77_page: AppTest passed")
