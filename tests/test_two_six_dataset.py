"""2.6 dataset contract + manifest (research/strategies/2.6/dataset.py) on hand-made CSVs.
Run: python3 -m unittest tests/test_two_six_dataset.py"""
import importlib.util
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

FOLDER = Path(__file__).resolve().parents[1] / "research" / "strategies" / "2.6"
sys.path.insert(0, str(FOLDER))
SPEC = importlib.util.spec_from_file_location("two_six_dataset", FOLDER / "dataset.py")
ds = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ds)


def write_csv(times, folder):
    path = Path(folder) / "bars.csv"
    rows = ["datetime,open,high,low,close,volume"] + [f"{t.isoformat()},100,101,99,100.5,1" for t in times]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return str(path)


def five_min(start, n):
    return [start + timedelta(minutes=5 * i) for i in range(n)]


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_manifest_fields_costs_and_checksum(self):
        path = write_csv(five_min(datetime(2026, 11, 2, 1, 0, tzinfo=timezone.utc), 120), self.tmp.name)
        m = ds.build_manifest(path, "Broker X", "XAUUSD", "5m", spread=0.3, commission=0.05)
        self.assertEqual((m["bars"], m["symbol"], m["timeframe"]), (120, "XAUUSD", "5m"))
        self.assertAlmostEqual(m["cost_per_event"], 0.35)
        self.assertEqual(m["gaps"]["other_gaps"], 0)
        self.assertEqual(m["utc_first"], "2026-11-02T01:00:00+00:00")
        self.assertEqual(len(ds.verify(path, m)), 120)
        Path(path).write_text(Path(path).read_text().replace("100.5", "100.6", 1))
        with self.assertRaises(ValueError):
            ds.verify(path, m)

    def test_gaps_weekend_vs_other_and_offset_input(self):
        fri = five_min(datetime(2026, 11, 6, 19, 0, tzinfo=timezone.utc), 30)       # Fri 19:00 .. 21:25
        sun = five_min(datetime(2026, 11, 8, 23, 0, tzinfo=timezone.utc), 60)       # Sun 23:00
        hole = five_min(sun[-1] + timedelta(hours=2), 30)                            # 2 h outage mid-week
        tz = timezone(timedelta(hours=2))
        path = write_csv([t.astimezone(tz) for t in fri + sun + hole], self.tmp.name)
        g = ds.build_manifest(path, "Broker X", "XAUUSD", "5m", spread=0.3)["gaps"]
        self.assertEqual((g["weekend_closes"], g["other_gaps"]), (1, 1))
        self.assertEqual(g["largest_other"][0]["seconds"], 7200)

    def test_rejects_proxy_mislabel_missing_provenance_and_bad_costs(self):
        path = write_csv(five_min(datetime(2026, 11, 2, tzinfo=timezone.utc), 120), self.tmp.name)
        with self.assertRaises(ValueError):
            ds.build_manifest(path, "Yahoo", "GC=F", "5m", spread=0.3)               # futures proxy as spot
        ds.build_manifest(path, "Yahoo", "GC=F", "5m", asset_class="futures_proxy", spread=0.3)
        with self.assertRaises(ValueError):
            ds.build_manifest(path, "Yahoo", "XAUUSD", "5m", asset_class="futures_proxy", spread=0.3)
        for bad in ({"provider": " "}, {"spread": None}, {"spread": -1.0}, {"spread": float("nan")}, {"timeframe": "7m"}):
            kw = {"provider": "Broker X", "symbol": "XAUUSD", "timeframe": "5m", "spread": 0.3}; kw.update(bad)
            with self.assertRaises(ValueError):
                ds.build_manifest(path, **kw)

    def test_cli_writes_manifest(self):
        path = write_csv(five_min(datetime(2026, 11, 2, tzinfo=timezone.utc), 120), self.tmp.name)
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ds.main([path, "--provider", "Broker X", "--symbol", "XAUUSD", "--timeframe", "5m", "--spread", "0.3", "--write"]), 0)
        self.assertTrue(Path(path + ".manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
