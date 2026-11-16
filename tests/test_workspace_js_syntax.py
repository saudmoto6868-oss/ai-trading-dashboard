"""The built workspace must parse: a single syntax error in the main script stops the whole Workspace from running.
Needs node. Run: python3 tests/test_workspace_js_syntax.py"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
node = shutil.which("node")
if not node:
    print("SKIP: node not installed")
    sys.exit(0)
H = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf-8").read()
scripts = re.findall(r"<script(?![^>]*src)[^>]*>(.*?)</script>", H, re.S)
assert scripts, "no inline script found"
for i, s in enumerate(scripts):
    p = os.path.join(tempfile.mkdtemp(), f"ws_{i}.js")
    open(p, "w", encoding="utf-8").write(s)
    r = subprocess.run([node, "--check", p], capture_output=True, text=True)
    assert r.returncode == 0, f"inline script {i}: {r.stderr[:400]}"
print(f"ok workspace inline scripts parse ({len(scripts)})")
