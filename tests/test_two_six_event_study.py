import importlib.util
import sys
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "research" / "strategies" / "2.6" / "event_study.py"
SPEC = importlib.util.spec_from_file_location("two_six_event_study", MODULE)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)
Bar, confirmed_pivots, make_legs, RATIOS, Pivot = mod.Bar, mod.confirmed_pivots, mod.make_legs, mod.RATIOS, mod.Pivot

class TwoSixTests(unittest.TestCase):
    def test_ratio_math(self):
        self.assertAlmostEqual(1/2.6,0.3846153846153846)
        self.assertAlmostEqual(1/2.618,0.3819709702062643)
    def test_pivot_known_only_after_right_bars(self):
        bars=[Bar(str(i),10,h,l,10) for i,(h,l) in enumerate(
            [(11,9),(12,8),(15,9),(12,8),(11,7),(10,6),(11,7),(12,8)])]
        p=next(x for x in confirmed_pivots(bars,left=1,right=1) if x.kind=="H")
        self.assertEqual(p.idx,2); self.assertEqual(p.known_at,3)
    def test_leg_direction(self):
        legs=list(make_legs([Pivot(1,"L",100,2),Pivot(5,"H",120,6),Pivot(9,"L",110,10)]))
        self.assertEqual((legs[0][0],legs[0][3]),("BUY",20))
        self.assertEqual((legs[1][0],legs[1][3]),("SELL",10))
    def test_ratio_comparators(self):
        self.assertIn(2.6,RATIOS); self.assertIn(2.618,RATIOS)
        self.assertAlmostEqual(1/0.382,2.617801047120419)
if __name__=="__main__": unittest.main()
