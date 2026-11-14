"""2.6 evaluation protocol (research/strategies/2.6/evaluation.py) on hand-made bars and events.
Run: python3 -m unittest tests/test_two_six_evaluation.py"""
import importlib.util
import sys
import unittest
from pathlib import Path

FOLDER = Path(__file__).resolve().parents[1] / "research" / "strategies" / "2.6"
sys.path.insert(0, str(FOLDER))
SPEC = importlib.util.spec_from_file_location("two_six_eval", FOLDER / "evaluation.py")
ev = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ev)
es = sys.modules["event_study"]


def bars(n=200, step=0.0):
    return [es.Bar(str(i), 100 + i * step, 101 + i * step, 99 + i * step, 100 + i * step) for i in range(n)]


def event(i, ratio=2.6, side="BUY", r=0.1, b=None):
    t = str(i)
    return es.Event(ratio, side, t, t, t, t, 100.0, 10.0, 1, 0.5, -0.5, {"10": r})


class EvaluationTests(unittest.TestCase):
    def test_decluster_drops_overlapping_windows_per_ratio(self):
        b = bars()
        evs = [event(10), event(15), event(21), event(15, ratio=2.5)]
        kept = ev.decluster(evs, b, horizon_bars=10)
        self.assertEqual(sorted((e.ratio, e.entry_time) for e in kept), [(2.5, "15"), (2.6, "10"), (2.6, "21")])
        with self.assertRaises(ValueError):
            ev.decluster(evs, b, 0)

    def test_split_and_purge_at_boundaries(self):
        bounds = ev.split_bounds(100)
        self.assertEqual(bounds, ((0, 60), (60, 80), (80, 100)))
        self.assertEqual(ev.segment_of(10, 10, bounds), "train")
        self.assertIsNone(ev.segment_of(55, 10, bounds))      # window crosses into validation
        self.assertEqual(ev.segment_of(62, 10, bounds), "validation")
        self.assertIsNone(ev.segment_of(95, 10, bounds))      # runs past the data
        with self.assertRaises(ValueError):
            ev.split_bounds(100, (0.5, 0.5, 0.1))

    def test_block_bootstrap_ci(self):
        self.assertIsNone(ev.block_bootstrap_ci([1.0]))
        lo, hi = ev.block_bootstrap_ci([0.0, 1.0] * 20, block=4, n_boot=500)
        self.assertLessEqual(lo, 0.5); self.assertGreaterEqual(hi, 0.5); self.assertLess(hi - lo, 0.5)
        self.assertEqual(ev.block_bootstrap_ci([0.3] * 10), (0.3, 0.3))
        self.assertEqual(ev.block_bootstrap_ci([0, 1, 2, 3], seed=7), ev.block_bootstrap_ci([0, 1, 2, 3], seed=7))

    def test_controls_flat_market_return_minus_cost(self):
        b = bars()  # flat: open 100, close 100 -> control return = -cost / span
        ctrl = ev.matched_controls(b, [event(10)], 10, cost=0.5, key="10", bounds=ev.split_bounds(len(b)), k=3)
        self.assertEqual(len(ctrl), 3)
        self.assertTrue(all(abs(x + 0.05) < 1e-9 for x in ctrl))

    def test_evaluate_locks_test_and_refuses_mixed_families(self):
        b = bars()
        evs = [event(i, r=0.2) for i in range(0, 200, 15)]
        rep = ev.evaluate(b, evs, horizon_bars=10, cost=0.0, key="10")
        row = rep["ratios"]["2.6"]
        self.assertTrue(rep["test_locked"]); self.assertEqual(row["test"].get("locked"), True); self.assertNotIn("mean", row["test"])
        self.assertEqual(row["n_raw"], len(evs)); self.assertEqual(row["n_declustered"], len(evs))
        self.assertAlmostEqual(row["train"]["mean"], 0.2); self.assertAlmostEqual(row["train"]["vs_control"], 0.2)
        self.assertGreater(row["purged"], 0)
        full = ev.evaluate(b, evs, horizon_bars=10, cost=0.0, key="10", reveal_test=True)
        self.assertIn("mean", full["ratios"]["2.6"]["test"])

        class H2Event:  # a different family must not be pooled with H1
            ratio, entry_time, returns_leg = 2.6, "5", {"10": 0.0}
        with self.assertRaises(ValueError):
            ev.evaluate(b, evs + [H2Event()], horizon_bars=10, cost=0.0, key="10")


if __name__ == "__main__":
    unittest.main()
