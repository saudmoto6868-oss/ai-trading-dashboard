"""Guard against the pattern that got the old GitHub account suspended (2026-11):
a hook commits a log line after every tool call, every push starts a CI run, thousands of runs a month.
Fails if the auto activity log is tracked by git, or if any CI workflow runs on a push to every branch."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = "docs/ACTIVITY_LOG_AUTO.md"

r = subprocess.run(["git", "check-ignore", "-q", LOG], cwd=ROOT)
assert r.returncode == 0, f"{LOG} must be in .gitignore (local log only, never committed)"
tracked = subprocess.run(["git", "ls-files", LOG], cwd=ROOT, capture_output=True, text=True).stdout.strip()
assert not tracked, f"{LOG} is tracked: run  git rm --cached {LOG}"

for wf in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
    text = wf.read_text(encoding="utf-8")
    assert not re.search(r"""branches:\s*\[\s*["']\*\*["']\s*\]""", text), f"{wf.name}: push on every branch"

print("ok ci noise guard")
