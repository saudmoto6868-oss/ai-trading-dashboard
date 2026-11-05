"""modules/workspace_app.html is generated from modules/ws/*: a direct edit of the generated file (or of a part without rebuilding) fails here.
Fix: edit the part, then run  python3 scripts/build_workspace.py"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_workspace.py"), "--check"], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip())
assert r.returncode == 0, "workspace_app.html is out of sync with modules/ws/"
print("ok workspace parts sync")
