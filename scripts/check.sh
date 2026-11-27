#!/usr/bin/env bash
# One command for agents: workspace parts sync + all plain-script tests.
# Quiet: prints only failing tests (last 15 lines each) and a one-line summary.
# Usage: bash scripts/check.sh [pattern]   e.g. bash scripts/check.sh spot
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
pat="${1:-}"
fail=0; pass=0; failed=()
python3 scripts/build_workspace.py --check >/dev/null 2>&1 || { echo "FAIL workspace parts out of sync -> python3 scripts/build_workspace.py"; fail=$((fail+1)); }
for t in tests/test_*${pat}*.py; do
  [ -f "$t" ] || continue
  out=$(timeout 300 python3 "$t" 2>&1)
  if [ $? -eq 0 ]; then pass=$((pass+1)); else
    fail=$((fail+1)); failed+=("$t")
    echo "=== FAIL $t"; echo "$out" | tail -n 15
  fi
done
echo "checks: $pass passed, $fail failed${failed:+ (${failed[*]})}"
[ "$fail" -eq 0 ]
