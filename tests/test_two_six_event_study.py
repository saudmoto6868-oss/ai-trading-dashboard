import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "research" / "strategies" / "2.6" / "event_study.py"
SPEC = importlib.util.spec_from_file_location("two_six_event_study", MODULE)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

Bar, Pivot = mod.Bar, mod.Pivot


class TwoSixTests(unittest.TestCase):
    def test_ratio_math(self):
        self.assertAlmostEqual(1 / 2.6, 0.3846153846153846)
        self.assertAlmostEqual(1 / 2.618, 0.3819709702062643)

    def test_pivot_known_only_after_right_bars(self):
        bars = [Bar(str(i), 10, h, l, 10) for i, (h, l) in enumerate(
            [(11, 9), (12, 8), (15, 9), (12, 8), (11, 7), (10, 6), (11, 7), (12, 8)])]
        pivot = next(p for p in mod.confirmed_pivots(bars, left=1, right=1) if p.kind == "H")
        self.assertEqual(pivot.idx, 2)
        self.assertEqual(pivot.known_at, 3)

    def test_same_side_pivots_are_not_retroactively_replaced(self):
        bars = [
            Bar(str(i), 10, h, l, 10)
            for i, (h, l) in enumerate([
                (10, 8), (12, 9), (11, 9), (10, 8),
                (13, 9), (11, 8), (10, 7), (9, 8),
            ])
        ]
        highs = [p for p in mod.confirmed_pivots(bars, left=1, right=1) if p.kind == "H"]
        self.assertEqual([p.idx for p in highs], [1, 4])

    def test_leg_direction(self):
        legs = list(mod.make_legs([
            Pivot(1, "L", 100, 2), Pivot(5, "H", 120, 6),
            Pivot(9, "L", 110, 10),
        ]))
        self.assertEqual((legs[0][0], legs[0][3]), ("BUY", 20))
        self.assertEqual((legs[1][0], legs[1][3]), ("SELL", 10))

    def test_same_kind_pivots_do_not_form_legs(self):
        legs = list(mod.make_legs([
            Pivot(1, "L", 100, 2), Pivot(3, "L", 98, 4),
            Pivot(5, "H", 120, 6),
        ]))
        self.assertEqual(len(legs), 1)
        self.assertEqual(legs[0][1].idx, 3)

    def test_gap_fill_uses_open_price_improvement(self):
        self.assertEqual(mod._fill_price(Bar("t", 98, 101, 97, 100), "BUY", 99), 98)
        self.assertEqual(mod._fill_price(Bar("t", 102, 104, 101, 103), "SELL", 101), 102)

    def test_bar_wholly_past_limit_fills_at_open(self):
        flat = (100, 101, 99, 100)
        rows = [flat] * 3 + [(100, 101, 90, 100)] + [flat] * 3 + [(100, 120, 99, 100)]
        rows += [flat] * 3 + [(95, 96, 94, 95)] + [flat] * 88
        bars = [Bar(str(i), *r) for i, r in enumerate(rows)]
        events, _ = mod.run_event_study(bars, ratios=[2.6])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].entry, 95)
        self.assertEqual(events[0].bars_to_fill, 1)

    def test_summary_normalizes_each_event_by_its_own_leg(self):
        e1 = mod.Event(2.6, "BUY", "a", "b", "c", "d", 100, 10, 1, .2, -.1, {"20": .1})
        e2 = mod.Event(2.6, "BUY", "a", "b", "c", "e", 100, 20, 2, .4, -.2, {"20": .3})
        result = mod.summarize([e1, e2])["2.6"]["all"]
        self.assertAlmostEqual(result["mean_20bar_return_leg_units"], .2)
        self.assertEqual(result["n_20bar"], 2)

    def test_summary_does_not_label_event_tail_as_oos(self):
        event = mod.Event(2.6, "BUY", "a", "b", "c", "d", 100, 10, 1, .2, -.1, {"20": .1})
        result = mod.summarize([event])["2.6"]
        self.assertIn("late_30pct_descriptive_not_oos", result)
        self.assertNotIn("out_of_sample", result)

    def test_csv_timestamp_validation_and_duplicate_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bars.csv"
            rows = ["datetime,open,high,low,close"]
            rows.extend(["2026-01-01T00:00:00Z,10,11,9,10"] * 100)
            path.write_text("\n".join(rows), encoding="utf-8")
            with self.assertRaises(ValueError):
                mod.load_bars(path)

    def test_naive_timestamp_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bars.csv"
            rows = ["datetime,open,high,low,close"]
            rows.extend([f"2026-01-01T00:{i // 60:02d}:{i % 60:02d},10,11,9,10" for i in range(100)])
            path.write_text("\n".join(rows), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "timezone"):
                mod.load_bars(path)

    def test_non_finite_cost_and_ratio_are_rejected(self):
        bars = [Bar(str(i), 10, 11, 9, 10) for i in range(100)]
        with self.assertRaisesRegex(ValueError, "cost"):
            mod.run_event_study(bars, cost=float("nan"))
        with self.assertRaisesRegex(ValueError, "ratios"):
            mod.run_event_study(bars, ratios=[float("nan")])

    def test_dual_high_low_pivot_bar_is_excluded(self):
        bars = [
            Bar(str(i), 10, high, low, 10)
            for i, (high, low) in enumerate([
                (11, 4), (11, 4), (15, 1), (11, 4), (11, 4),
            ])
        ]
        pivots = mod.confirmed_pivots(bars, left=1, right=1)
        self.assertFalse(any(p.idx == 2 for p in pivots))

    def test_ratio_comparators(self):
        self.assertIn(2.6, mod.RATIOS)
        self.assertIn(2.618, mod.RATIOS)
        self.assertAlmostEqual(1 / 0.382, 2.617801047120419)


if __name__ == "__main__":
    unittest.main()
