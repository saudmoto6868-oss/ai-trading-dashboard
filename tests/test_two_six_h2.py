"""H2 liquidity projection (research/strategies/2.6/h2_liquidity.py) on hand-made bars.
Run: python3 -m unittest tests/test_two_six_h2.py"""
import importlib.util
import sys
import unittest
from pathlib import Path

FOLDER = Path(__file__).resolve().parents[1] / "research" / "strategies" / "2.6"
SPEC = importlib.util.spec_from_file_location("two_six_h2", FOLDER / "h2_liquidity.py")
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)
Bar = sys.modules["event_study"].Bar

F = (100, 101, 99, 100)  # flat filler: equal highs/lows, never a pivot


def build(sweep_bar, rally_high=120):
    # H pivot 110 @3, L pivot 90 @7 (down leg span 20), H pivot 110.03 @11 -> EQH known @14.
    rows = [F] * 3 + [(100, 110, 99, 100)] + [F] * 3 + [(100, 101, 90, 100)]
    rows += [F] * 3 + [(100, 110.03, 99, 100)] + [F] * 3 + [sweep_bar, F]
    rows += [(100, rally_high, 99, 100)] + [F] * 82
    return [Bar(str(i), *r) for i, r in enumerate(rows)]


class H2Tests(unittest.TestCase):
    def test_sweep_then_projected_sell_zone_fills(self):
        events, pools = mod.run_h2(build((100, 111, 99, 100)), ratios=[2.6])
        self.assertEqual([(p[0], p[1]) for p in pools], [("H", 110.03)])
        self.assertEqual(len(events), 1)
        e = events[0]
        self.assertEqual((e.side, e.sweep_time, e.leg_start, e.leg_end), ("SELL", "15", "3", "7"))
        self.assertEqual(e.leg_range, 20)
        self.assertAlmostEqual(e.entry, 110.03 + 20 / 2.6)
        self.assertEqual(e.bars_to_fill, 2)

    def test_close_beyond_level_is_breakout_not_sweep(self):
        events, _ = mod.run_h2(build((100, 111, 99, 110.5)), ratios=[2.6])
        self.assertEqual(events, [])

    def test_zone_not_reached_gives_no_event(self):
        events, _ = mod.run_h2(build((100, 111, 99, 100), rally_high=105), ratios=[2.6])
        self.assertEqual(events, [])

    def test_unequal_highs_are_not_a_pool(self):
        bars = build((100, 111, 99, 100))
        bars[11] = Bar("11", 100, 112, 99, 100)
        events, pools = mod.run_h2(bars, ratios=[2.6])
        self.assertEqual((pools, events), ([], []))

    def test_invalid_params_rejected(self):
        bars = build((100, 111, 99, 100))
        with self.assertRaisesRegex(ValueError, "eq_tol"):
            mod.run_h2(bars, eq_tol=float("nan"))
        with self.assertRaisesRegex(ValueError, "ratios"):
            mod.run_h2(bars, ratios=[0])


if __name__ == "__main__":
    unittest.main()
