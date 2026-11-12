"""Ensure the V7 page actually embeds and parses the live structure engine."""
import os
import re
import inspect
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import v7_page


def test_live_structure_is_wired_and_scripts_parse():
    html, error = v7_page.live_html()
    assert not error, error
    assert "V7STRUCT" in html
    assert "Structure &amp; liquidity" in html
    assert "S.compute(closed)" in html
    page_source = inspect.getsource(v7_page)
    assert "components.html(" not in page_source
    assert "components.v1.html(" not in page_source
    assert page_source.count("st.iframe(") >= 2   # live chart + the separate snapshot view (the snapshot no longer sits under the live chart)
    assert "One live chart" not in page_source and "What else the CFX research built" not in page_source, "the default view must stay a single chart workspace"

    scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S | re.I)
    assert len(scripts) >= 4, f"expected library, indicators, structure, and app scripts; got {len(scripts)}"
    for i, script in enumerate(scripts):
        if not script.strip():
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as f:
            f.write(script)
            f.flush()
            result = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
        assert result.returncode == 0, f"inline script {i} has a syntax error: {result.stderr}"


if __name__ == "__main__":
    test_live_structure_is_wired_and_scripts_parse()
    print("ok V7 live page embeds structure engine and all inline JavaScript parses")
