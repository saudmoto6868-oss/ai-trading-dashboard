"""Run every tests/test_*.py (plain scripts; pytest files via pytest) and fail if any fails.

Used by .github/workflows/tests.yml and locally: python3 scripts/run_tests.py [-k name] [--timeout 180]
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PYTEST = re.compile(r"^(import pytest|from pytest)", re.M)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", default="", help="only files whose name contains this")
    ap.add_argument("--timeout", type=int, default=180, help="seconds per file")
    a = ap.parse_args()
    files = sorted(p for p in (ROOT / "tests").glob("test_*.py") if a.k in p.name)
    env = {**os.environ, "PYTHONPATH": str(ROOT)}  # tests import `modules` from the repo root
    failed, t0 = [], time.time()
    for f in files:
        cmd = [sys.executable, "-m", "pytest", "-q", str(f)] if PYTEST.search(f.read_text(encoding="utf-8")) else [sys.executable, str(f)]
        st = time.time()
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=a.timeout, env=env)
            ok, out = r.returncode == 0, r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            ok, out = False, f"TIMEOUT after {a.timeout}s"
        print(f"{'ok  ' if ok else 'FAIL'} {time.time() - st:5.1f}s {f.name}", flush=True)
        if not ok:
            failed.append(f.name)
            print("\n".join(out.strip().splitlines()[-25:]), flush=True)
    print(f"\n{len(files) - len(failed)}/{len(files)} passed in {time.time() - t0:.0f}s")
    if failed:
        print("FAILED: " + " ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
