"""modules/ui_kit.py: the HTML / SVG pieces build, escape text, and clamp values."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import ui_kit as U  # noqa: E402


def test_pieces():
    k = U.kpi("🎯", "Matched <b>", "3 / 9", "sub", tone="up", pct=250)
    assert "&lt;b&gt;" in k and "uk-card up" in k and "stroke-dasharray" in k
    assert U.row([k, k]).count("uk-card") == 4 * 1 + 0 or "uk-row" in U.row([k])
    d = U.donut([("up", 3, U.UP), ("down", 1, U.DOWN)], "4"); assert d.count("<circle") == 3 and "up 3" in d
    assert U.donut([("a", 0, "#fff")], "0")                       # all-zero does not divide by zero
    g = U.gauge(140, "x"); assert "100%" in g
    assert U.bars([("a", 3), ("b", 0)]).count("<rect") == 2 and U.bars([]) == ""
    for n in list(U.THEMES) + ["nope"]:
        assert "--uk-acc" in U.css(n)


if __name__ == "__main__":
    test_pieces(); print("ok ui_kit")
