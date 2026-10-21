"""Prompt shape for the free PR review (no network; plain script)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.pr_review import build_prompt

p = build_prompt("Test PR", [{"filename": "a.py", "status": "modified", "patch": "@@ -1 +1 @@\n-x\n+y"}])
assert "APPROVE_WITH_CHANGES" in p and "a.py" in p and "look-ahead" in p
assert "(binary or too large)" in build_prompt("t", [{"filename": "b.py", "status": "added"}])
print("test_pr_review: all passed")
