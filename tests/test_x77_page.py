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
    finally:
        script.unlink(missing_ok=True)
print("x77_page: AppTest passed")
