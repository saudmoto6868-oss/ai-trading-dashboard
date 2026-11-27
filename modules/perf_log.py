"""Server timing log (maintenance plan M0 0.4). Off unless PERF_LOG=1 (env): then every timed block prints one line to stderr,
   PERF <ms> ms <name>
so the slowest points of a run can be listed with:  grep '^PERF' log | sort -k2 -n -r | head
Costs nothing when off (one bool check)."""
import contextlib
import os
import sys
import time

ON = os.environ.get("PERF_LOG", "") == "1"


@contextlib.contextmanager
def timed(name: str):
    if not ON:
        yield
        return
    t = time.perf_counter()
    try:
        yield
    finally:
        print("PERF %8.1f ms %s" % ((time.perf_counter() - t) * 1000, name), file=sys.stderr, flush=True)
