"""Regression (2026-11-20 review): an active account whose inactivity limit is due TODAY (0 days left) must count as expiring
and sort first, not be dropped by `_days_left(a) or 999`. No network. Run: PYTHONPATH=. python3 tests/test_prop_firms_days_left.py"""
import os
import sys
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import prop_firms as P  # noqa: E402

today = lambda n: (date.today() - timedelta(days=n)).isoformat()
due = {"name": "due", "status": "active", "inactivity_limit": 30, "last_trade_date": today(30)}      # 0 days left
soon = {"name": "soon", "status": "active", "inactivity_limit": 30, "last_trade_date": today(25)}    # 5 days left
nodate = {"name": "nodate", "status": "active", "inactivity_limit": 30}
assert P._days_left(due) == 0 and P._days_left(soon) == 5 and P._days_left(nodate) is None
assert P._days_left_sort(due) == 0 and P._days_left_sort(nodate) == 9999
assert [a["name"] for a in sorted([nodate, soon, due], key=P._days_left_sort)] == ["due", "soon", "nodate"]
assert [a for a in (due, soon, nodate) if P._days_left_sort(a) <= 7] == [due, soon]
print("ok due-today account counts as expiring and sorts first")
print("ALL OK")
