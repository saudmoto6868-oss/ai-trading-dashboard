"""Ensure the V7 page actually embeds and parses the live structure engine."""
import re
import subprocess
import tempfile

from modules import v7_page


def test_live_structure_is_wired_and_scripts_parse():
    html, error = v7_page.live_html()
    assert not error, error
    assert "V7STRUCT" in html
    assert "Structure &amp; liquidity" in html
    assert "S.compute(closed)" in html

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
