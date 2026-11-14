"""2.6 report (research/strategies/2.6/report.py) on a synthetic zig-zag CSV. Run: python3 -m unittest tests/test_two_six_report.py"""
import contextlib
import importlib.util
import io
import json
import math
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

FOLDER = Path(__file__).resolve().parents[1] / "research" / "strategies" / "2.6"
sys.path.insert(0, str(FOLDER))
SPEC = importlib.util.spec_from_file_location("two_six_report", FOLDER / "report.py")
rp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rp)
ds = sys.modules["dataset"]


def zigzag_csv(folder, n=900):
    t0 = datetime(2026, 11, 2, tzinfo=timezone.utc)
    rows = ["datetime,open,high,low,close"]
    prev = 2000.0
    for i in range(n):
        c = 2000 + 20 * math.sin(i / 7.0) + 6 * math.sin(i / 2.3)
        o = (prev + c) / 2; h = max(o, c) + 0.8; lo = min(o, c) - 0.8
        rows.append(f"{(t0 + timedelta(minutes=5 * i)).isoformat()},{o:.2f},{h:.2f},{lo:.2f},{c:.2f}")
        prev = c
    path = Path(folder) / "xau.csv"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return str(path)


class ReportTests(unittest.TestCase):
    def test_report_sections_locked_test_and_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = zigzag_csv(tmp)
            m = ds.build_manifest(path, "Synthetic", "XAUUSD", "5m", spread=0.3)
            md, ev = rp.build(path, m)
            self.assertIn("## H1 retracement", md); self.assertIn("## H2 liquidity projection", md)
            self.assertIn(m["sha256"][:16], md); self.assertIn("locked", md); self.assertIn("UNKNOWN", md)
            self.assertTrue(ev["h1"]["test_locked"] and ev["h2"]["test_locked"])
            self.assertGreater(sum(r["n_raw"] for r in ev["h1"]["ratios"].values()), 0)
            for r in ev["h1"]["ratios"].values():
                self.assertLessEqual(r["n_declustered"], r["n_raw"]); self.assertNotIn("mean", r["test"])
            self.assertGreater(rp.h1_candidates(ds.verify(path, m)), 0)
            # same input -> same report (reproducible)
            self.assertEqual(md, rp.build(path, m)[0])
            # a changed file is refused
            Path(path).write_text(Path(path).read_text().replace("2000.00", "2000.01", 1))
            with self.assertRaises(ValueError):
                rp.build(path, m)

    def test_cli_out_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = zigzag_csv(tmp)
            mp = Path(tmp) / "m.json"; mp.write_text(json.dumps(ds.build_manifest(path, "Synthetic", "XAUUSD", "5m", spread=0.3)))
            out = Path(tmp) / "r.md"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(rp.main([path, str(mp), "--out", str(out)]), 0)
            self.assertTrue(out.read_text().startswith("# 2.6 research report"))


if __name__ == "__main__":
    unittest.main()
