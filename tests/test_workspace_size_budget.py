"""Size budget for the chart page (maintenance plan M3 / step 1.6, 2026-11-25).

modules/workspace_app.html is sent to the browser again every time the Workspace frame reloads, so its size is a direct
cost for the owner ("the site is very slow"). It grew from ~400 KB (old notes) to 1.29 MB without anyone noticing.
This test fails when it grows past the budget, so growth becomes a decision instead of an accident.

Budget = size on 2026-11-25 + a small margin for normal edits. To raise it on purpose: change the number below in the
same PR, and write the reason + before/after size in docs/MEETING_ROOM.md (maintenance thread work log).
When step 2 (light chart) lands, LOWER these numbers to the new size so the gain is kept.
Run: PYTHONPATH=. python3 tests/test_workspace_size_budget.py"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOTAL_BUDGET = 1_350_000      # bytes; 1_290_470 on 2026-11-25 (+~4.6%)
PART_BUDGET = 310_000         # bytes per modules/ws part; largest was 22_panels.js at 291_792 on 2026-11-25

page = os.path.join(ROOT, "modules", "workspace_app.html")
size = os.path.getsize(page)
assert size <= TOTAL_BUDGET, (
    f"modules/workspace_app.html is {size:,} bytes, budget {TOTAL_BUDGET:,}. Shrink it, or raise TOTAL_BUDGET on purpose "
    "and log why in docs/MEETING_ROOM.md (maintenance thread)")
print(f"ok workspace_app.html {size:,} / {TOTAL_BUDGET:,} bytes")

parts_dir = os.path.join(ROOT, "modules", "ws")
big = [(os.path.getsize(os.path.join(parts_dir, f)), f) for f in sorted(os.listdir(parts_dir))
       if os.path.isfile(os.path.join(parts_dir, f)) and os.path.getsize(os.path.join(parts_dir, f)) > PART_BUDGET]
assert not big, f"modules/ws parts over {PART_BUDGET:,} bytes: {big}. Split the part or raise PART_BUDGET on purpose (log it)"
print(f"ok every modules/ws part <= {PART_BUDGET:,} bytes")
print("ALL OK")
