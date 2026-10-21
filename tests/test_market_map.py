"""Market map numbers on hand-made rows (plain script, like the other tests)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.market_map import board, breadth, by_class

rows = [{"id": "HL:xyz:GOLD", "cls": "Metals", "px": 110, "prev": 100, "vol": 5e6},
        {"id": "HL:xyz:SILVER", "cls": "Metals", "px": 95, "prev": 100, "vol": 2e6},
        {"id": "HL:xyz:SP500", "cls": "Indices", "px": 101, "prev": 100, "vol": 3e6},
        {"id": "HL:xyz:NOPREV", "cls": "Indices", "px": 101, "prev": 0, "vol": 1e6}]
b = board(rows)
assert len(b) == 3, "market without a reference price must be left out"
g = b.set_index("name")
assert abs(g.loc["GOLD", "chg"] - 10) < 1e-9
assert abs(g.loc["GOLD", "rel"] - 7.5) < 1e-9        # Metals average is (10 - 5) / 2 = 2.5
bd = breadth(b)
assert bd["n"] == 3 and abs(bd["up_share"] - 2 / 3) < 1e-9
assert by_class(b).iloc[0]["cls"] == "Metals"
assert breadth(board([]))["n"] == 0
print("test_market_map: all passed")
