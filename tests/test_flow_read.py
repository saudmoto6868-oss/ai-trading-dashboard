"""Order-flow reading engine (FlowRead in modules/workspace_app.html): wall life-cycle, one shared classification, plain-language reading.
Runs the pure-function checks in node (tests/flow_read_cases.js) against the real page source, plus a syntax check of the page scripts.
Run with: python tests/test_flow_read.py   (needs node on PATH)"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "modules" / "workspace_app.html"
NODE = shutil.which("node")


def main():
    if not NODE:
        print("SKIP: node not found"); return 0
    r = subprocess.run([NODE, str(ROOT / "tests" / "flow_read_cases.js"), str(PAGE)], capture_output=True, text=True)
    print(r.stdout.strip(), r.stderr.strip())
    if r.returncode:
        return 1
    html = PAGE.read_text(encoding="utf-8")
    code = "".join("\n;(function(){\n" + m + "\n})();\n" for m in re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", html))
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(code); tmp = f.name
    c = subprocess.run([NODE, "--check", tmp], capture_output=True, text=True)
    Path(tmp).unlink(missing_ok=True)
    if c.returncode:
        print("FAIL page script syntax:", c.stderr[:400]); return 1
    # the old divergent classifiers must be gone: one tracker for the heat map, the list and the lights
    bad = [n for n in ("lt.prev = cur", "const thru = (s===\"ask\" && hi != null") if n in html]
    if bad:
        print("FAIL old classifier still present:", bad); return 1
    print("ok flow_read page checks"); return 0


if __name__ == "__main__":
    sys.exit(main())
