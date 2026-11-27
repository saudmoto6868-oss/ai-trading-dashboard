"""Nothing may be defined after `if __name__ == "__main__":` at module level (2026-11-27).

`python -m modules.brain_cron` exits inside that block, so a def placed below it never runs:
`_lessons` sat under the guard and the brain's daily review crashed with NameError in the Telegram alerts workflow.
ruff cannot see this (the name IS defined in the file). Scans main.py, modules/*.py, scripts/*.py.
Run: PYTHONPATH=. python3 tests/test_no_defs_after_main_guard.py"""
import ast
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad = []
for f in [os.path.join(ROOT, "main.py")] + sorted(glob.glob(os.path.join(ROOT, "modules", "*.py")) + glob.glob(os.path.join(ROOT, "scripts", "*.py"))):
    tree = ast.parse(open(f, encoding="utf-8").read(), f)
    guard = False
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and getattr(node.test.left, "id", "") == "__name__":
            guard = True
            continue
        if guard and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign, ast.Import, ast.ImportFrom)):
            bad.append(f"{os.path.relpath(f, ROOT)}:{node.lineno}")
assert not bad, f"defined after the __main__ guard (never runs under python -m / script): {bad}"
print("ok nothing defined after a __main__ guard")
print("ALL OK")
