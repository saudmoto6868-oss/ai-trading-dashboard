"""Daily Spot learning cycle (modules/spot_learn_job.py): record -> score -> report. Synthetic data, no network. Plain script."""
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import spot_learn_job as J

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def brain(asset="GOLD", price=100.0):
    return {"asset": asset, "price": price,
            "horizons": {"day": {"verdict": "buy", "score": 70, "entry": price, "stop": 95.0, "target": 110.0},
                         "month": {"verdict": "sell", "score": 30, "entry": price, "stop": 110.0, "target": 90.0}},
            "setups": [{"id": "pullback", "tf": "1d", "side": "buy", "entry": price, "stop": 95.0, "target": 110.0}]}


def daily_bars(start, closes):
    out = []
    for i, c in enumerate(closes):
        t = start + timedelta(days=i)
        out.append({"time": t.isoformat(), "high": c * 1.01, "low": c * 0.99, "close": c})
    return out


def main():
    ok = 0
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "log.jsonl"
        # Cycle 1 at T0: records only. Nothing can be scored yet (no bars after T0 at all).
        r1 = J.cycle([brain()], path, {"GOLD": []}, now=T0)
        assert r1["wrote_verdicts"] == 2 and r1["wrote_setups"] == 1, r1
        assert r1["rows_total"] == 3 and r1["scored"] == 0 and r1["pending"] == 3, r1
        assert "لسه مستني الأفق 3" in r1["text"]
        ok += 1

        # Cycle 2 at T0+5d: 'day' (3 days) is over, 'month' (90 days) and '1D'-setup horizon (10 days) are not...
        # the setup horizon 1d = 10 days, so it stays pending too. Only the 'day' verdict may be scored.
        closes = [100 + i for i in range(0, 6)]        # rises 1 per day
        bars = {"GOLD": daily_bars(T0 + timedelta(days=1), closes)}
        r2 = J.cycle([], path, bars, now=T0 + timedelta(days=5))
        assert r2["rows_total"] == 3, r2
        assert r2["scored"] == 1, r2                    # only the 'day' buy verdict
        k = [x for x in r2["summary"] if x.startswith("day")]
        assert k, r2["summary"]
        assert r2["summary"][k[0]]["n"] == 1
        ok += 1

        # Re-running the same cycle must not double-count: scoring is recomputed from the log, not appended.
        r3 = J.cycle([], path, bars, now=T0 + timedelta(days=5))
        assert r3["scored"] == 1 and r3["rows_total"] == 3, r3
        ok += 1

        # Far in the future: everything matured, the report must say so and stay under the Telegram limit.
        far = {"GOLD": daily_bars(T0 + timedelta(days=1), [100 + (i % 7) for i in range(400)])}
        r4 = J.cycle([], path, far, now=T0 + timedelta(days=400))
        assert r4["scored"] == 3 and r4["pending"] == 0, r4
        assert len(r4["text"]) <= J.MAX_TG
        assert "لسه مستني الأفق 0" in r4["text"]
        ok += 1

    # Empty bars never crash and never score.
    with tempfile.TemporaryDirectory() as d:
        r = J.cycle([brain("BTC")], Path(d) / "x.jsonl", {}, now=T0)
        assert r["scored"] == 0 and r["wrote_verdicts"] == 2
        ok += 1

    # A brain result with no price (data down) is not logged at all.
    with tempfile.TemporaryDirectory() as d:
        nb = brain("SILVER", price=None)
        r = J.cycle([nb], Path(d) / "y.jsonl", {}, now=T0)
        assert r["wrote_verdicts"] == 0 and r["wrote_setups"] == 0 and r["rows_total"] == 0, r
        ok += 1

    # bars_from_df: tz-naive pandas times become UTC ISO strings, oldest first kept.
    import pandas as pd
    df = pd.DataFrame({"time": pd.to_datetime(["2026-01-01", "2026-01-02"]), "high": [2.0, 3.0], "low": [1.0, 2.0], "close": [1.5, 2.5]})
    bl = J.bars_from_df(df)
    assert bl[0]["time"].startswith("2026-01-01T00:00:00") and bl[0]["time"].endswith("+00:00"), bl[0]
    assert bl[1]["close"] == 2.5
    ok += 1
    print(f"test_spot_learn_job: {ok} groups passed")


if __name__ == "__main__":
    main()
