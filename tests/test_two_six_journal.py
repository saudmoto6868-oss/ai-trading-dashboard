"""Tests for modules/two_six_journal.py (plain script). Synthetic candles only: these prove the logic, not the strategy."""
import os
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd  # noqa: E402
from modules import two_six_chart as tc  # noqa: E402
from modules import two_six_journal as tj  # noqa: E402


def _df(n=400, seed=3):
    rnd = random.Random(seed)
    px, rows = 3850.0, []
    for i in range(n):
        o = px
        c = o + rnd.uniform(-3, 3)
        h, l = max(o, c) + rnd.uniform(0, 1.5), min(o, c) - rnd.uniform(0, 1.5)
        rows.append((pd.Timestamp("2026-01-01") + pd.Timedelta(minutes=15 * i), o, h, l, c))
        px = c
    return pd.DataFrame(rows, columns=["time", "open", "high", "low", "close"])


def test_records_cover_every_play_and_status_rules():
    df = _df()
    plays = tc.setups(tc.bars_from_df(df), ratio=2.6, left=5, right=5)
    assert plays, "synthetic data should give setups"
    times = [str(t) for t in df["time"]]
    recs = tj.build_records(plays, times, "XAUUSD", "15m", last_price=float(df["close"].iloc[-1]))
    assert len(recs) == len(plays)
    assert len({r["id"] for r in recs}) == len(recs), "ids must be unique"
    for r in recs:
        if r["status"] == "TP2":
            assert r["outcome_r"] == 2.0
        elif r["status"] == "stopped":
            assert r["outcome_r"] == -1.0
        else:
            assert r["outcome_r"] is None, r["status"]
        assert r["review"] and r["followup"] and r["strategy"]
    assert sum(r["best_now"] for r in recs) <= 1
    print("ok records: status -> outcome rules, unique ids, one best_now at most")


def test_best_now_is_nearest_live_setup():
    plays = [
        {"kind": "H1", "side": "BUY", "known": 1, "entry": 100.0, "stop": 99.0, "tp1": 101.0, "tp2": 102.0,
         "status": "waiting", "fill": None},
        {"kind": "H1", "side": "SELL", "known": 2, "entry": 110.0, "stop": 111.0, "tp1": 109.0, "tp2": 108.0,
         "status": "waiting", "fill": None},
        {"kind": "H1", "side": "BUY", "known": 3, "entry": 95.0, "stop": 94.0, "tp1": 96.0, "tp2": 97.0,
         "status": "expired", "fill": None},
    ]
    recs = tj.build_records(plays, ["a", "b", "c", "d"], "XAUUSD", "15m", last_price=101.0)
    assert [r["best_now"] for r in recs] == [True, False, False], "expired is never best"
    print("ok best_now = nearest live setup, expired never")


def test_upsert_keeps_owner_note_and_is_idempotent():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "j.jsonl"
        plays = [{"kind": "H1", "side": "BUY", "known": 1, "entry": 100.0, "stop": 99.0, "tp1": 101.0, "tp2": 102.0,
                  "status": "waiting", "fill": None}]
        recs = tj.build_records(plays, ["a", "b"], "XAUUSD", "15m")
        assert tj.upsert(recs, path) == 1
        rows = tj.load(path)
        rows[0]["note"] = "owner: looked good"
        path.write_text("\n".join(__import__("json").dumps(r) for r in rows) + "\n", encoding="utf-8")
        assert tj.upsert(tj.build_records(plays, ["a", "b"], "XAUUSD", "15m"), path) == 0, "same data: no change"
        plays[0]["status"], plays[0]["fill"], plays[0]["exit"] = "TP2", 1, 2
        assert tj.upsert(tj.build_records(plays, ["a", "b"], "XAUUSD", "15m"), path) == 1
        out = tj.load(path)
        assert len(out) == 1 and out[0]["status"] == "TP2" and out[0]["outcome_r"] == 2.0
        assert out[0]["note"] == "owner: looked good", "owner note must survive an update"
    print("ok upsert: one row per setup, owner note kept, no-op when unchanged")


def test_summary_says_not_evidence_below_30():
    rows = [{"status": "TP2", "outcome_r": 2.0}, {"status": "stopped", "outcome_r": -1.0},
            {"status": "waiting", "outcome_r": None}, {"status": "expired", "outcome_r": None}]
    s = tj.summary(rows)
    assert s["closed"] == 2 and s["wins"] == 1 and s["avg_r"] == 0.5 and s["live"] == 1 and s["expired"] == 1
    assert s["evidence"] is False and "NOT EVIDENCE" in s["text"]
    print("ok summary: n, wins, avg R, and 'not evidence' under 30")


def test_htf_agreement_uses_latest_known_setup_before_time():
    idx = [("2026-01-01 10:00", "BUY"), ("2026-01-01 12:00", "SELL")]
    assert tj.htf_agreement(idx, "2026-01-01 11:00", "BUY", "1h") == "1h✓", "latest before 11:00 is BUY"
    assert tj.htf_agreement(idx, "2026-01-01 13:00", "BUY", "1h") == "1h✗", "latest before 13:00 is SELL"
    assert tj.htf_agreement(idx, "2026-01-01 09:00", "BUY", "1h") == "", "no bigger-timeframe setup yet"
    print("ok htf agreement: latest known setup at or before the time, '' when none")


def test_build_records_adds_htf_column_and_reason():
    plays = [{"kind": "H1", "side": "BUY", "known": 1, "entry": 100.0, "stop": 99.0, "tp1": 101.0, "tp2": 102.0,
              "status": "waiting", "fill": None}]
    htf = {"1h": [("a", "BUY")], "4h": [("a", "SELL")]}
    rec = tj.build_records(plays, ["a", "b"], "XAUUSD", "15m", htf=htf)[0]
    assert rec["htf"] == ["1h✓", "4h✗"], rec["htf"]
    assert any("bigger timeframes" in r for r in rec["why_taken"])
    print("ok build_records: htf column and a reason line")


if __name__ == "__main__":
    test_records_cover_every_play_and_status_rules()
    test_best_now_is_nearest_live_setup()
    test_upsert_keeps_owner_note_and_is_idempotent()
    test_summary_says_not_evidence_below_30()
    test_htf_agreement_uses_latest_known_setup_before_time()
    test_build_records_adds_htf_column_and_reason()
    print("two_six_journal: all ok")
