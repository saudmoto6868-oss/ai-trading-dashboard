"""Daily baseline calls: call rule, one record per symbol per day, scoring after the horizon, summary file (synthetic, no network)."""
import os, sys, tempfile, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import daily_forecast as df_

def leg_rows(up=True, n=80, end_extra=None):
    """Rows whose last zig-zag leg goes up (or down). Days are 2026-01-01 + i."""
    import datetime as dt
    rows = []
    base = 100.0
    for i in range(n):
        # saw-tooth: zig-zag legs of ~10 % so the swing size is clearly detected
        phase = (i // 10) % 2
        mid = base + (i % 10) * (1.0 if phase == 0 else -1.0)
        if not up:
            mid = base - (i % 10) * (1.0 if phase == 0 else -1.0)
        c = 100 + 10*(i // 10 % 2) + (i % 10)*(1 if phase == 0 else -1)
        rows.append({"day": str(dt.date(2026, 1, 1) + dt.timedelta(days=i)), "h": c + 0.5, "l": c - 0.5, "c": c})
    return rows

import numpy as np

def path_rows(points, n_days=None):
    """Piecewise-linear closes through (bar, price) points, with bar ranges; days 2026-01-01 + bar."""
    import datetime as dt
    xs, ys = zip(*points)
    last = xs[-1]
    out = []
    for i in range(last + 1):
        c = float(np.interp(i, xs, ys))
        out.append({"day": str(dt.date(2026, 1, 1) + dt.timedelta(days=i)), "h": c + 0.6, "l": c - 0.6, "c": c})
    return out

# last confirmed leg goes DOWN (126 -> 96): the baseline calls short, stop at the leg start (126)
down_rows = path_rows([(0, 100), (20, 120), (30, 108), (45, 126), (60, 118), (75, 96), (84, 100)])   # 126 -> 96 is a confirmed down leg; the bounce after it confirms the pivot
call = df_.baseline_call(down_rows)
assert call and call["side"] == "short", call
assert call["stop"] > call["entry"] > call["target"], call

# last confirmed leg goes UP (100 -> 122): long
up_rows = path_rows([(0, 120), (20, 100), (35, 122), (50, 110), (60, 128), (70, 116)])
call = df_.baseline_call(up_rows)
assert call and call["side"] == "long", call
assert call["stop"] < call["entry"] < call["target"], call

# a flat or too short series: no call
assert df_.baseline_call(path_rows([(0, 100), (10, 100.2)])) is None

# record once per symbol per day, skip a symbol whose feed fails
tmp = Path(tempfile.mkdtemp())
cfg_syms = df_.symbols()
def fake_fetch(sym, tf, limit):
    if sym == cfg_syms["Crypto"][0]:
        raise RuntimeError("no feed")
    return down_rows
written = df_.record_day(fake_fetch, today="2026-11-20", folder=tmp)
names = {w["symbol"] for w in written}
assert cfg_syms["Crypto"][0] not in names
assert all(w["id"].endswith("|2026-11-20") for w in written)

# scoring waits until the horizon has passed, then writes an outcome once
later = [{"day": "2026-11-21", "h": 120, "l": 99, "c": 119}, {"day": "2026-11-22", "h": 121, "l": 100, "c": 120},
         {"day": "2026-11-23", "h": 122, "l": 100, "c": 121}, {"day": "2026-11-24", "h": 123, "l": 100, "c": 122},
         {"day": "2026-11-25", "h": 124, "l": 100, "c": 123}]
new = df_.score_due(lambda s, tf, n: later, today="2026-11-26", folder=tmp)
assert new and all(r["outcome"] in ("win", "loss", "timeout") for r in new)
again = df_.score_due(lambda s, tf, n: later, today="2026-11-26", folder=tmp)
assert again == []                       # never scored twice
txt = df_.write_summary(folder=tmp, out=tmp / "SUMMARY.md")
assert "| class |" in txt and "Rule v0" in txt
print("test_daily_forecast: OK", len(written), "calls,", len(new), "scored")

# class_summary reads the same outcomes file the summary uses
rows = df_.class_summary(folder=tmp)
assert rows and all("verdict" in s and "n" in s for _, s in rows)
assert df_.class_summary(folder=Path(tempfile.mkdtemp())) == []
print("test_daily_forecast class_summary: OK")

# regression (2026-11-24): the loader's daily name is "1d"; calls from the "1D" bug are never scored and are left out of reports
seen = []
tmp2 = Path(tempfile.mkdtemp())
df_.record_day(lambda s, tf, n: (seen.append(tf), down_rows)[1], today="2026-11-20", folder=tmp2)
assert seen and set(seen) == {"1d"}, set(seen)
import json as _json
bad = {"id": "OLD|2026-11-21", "symbol": "OLD", "class": "Crypto", "tf": "1D", "side": "long", "entry": 100, "stop": 99, "target": 101.5,
       "made_at": "2026-11-21", "horizon_bars": 5}
(tmp2 / "OLD.jsonl").write_text(_json.dumps(bad) + "\n", encoding="utf8")
with (tmp2 / "outcomes.jsonl").open("a", encoding="utf8") as f:
    f.write(_json.dumps({"id": "OLD|2026-11-21", "symbol": "OLD", "class": "Crypto", "side": "long", "outcome": "win", "R": 1.5}) + "\n")
assert "OLD|2026-11-21" not in df_.valid_ids(tmp2)
assert all(r["id"] != "OLD|2026-11-21" for r in df_.scored(tmp2))
new2 = df_.score_due(lambda s, tf, n: later, today="2026-11-30", folder=tmp2)
assert all(r["id"] != "OLD|2026-11-21" for r in new2)
assert "Left out: 1" in df_.write_summary(folder=tmp2, out=tmp2 / "S.md")
print("test_daily_forecast 1d regression: OK")
