"""Reversal boxes, no stop and no target. Zone = leg origin -/+ range / ratio (buy below the low of an up leg,
sell above the high of a down leg). Box = zone +/- half * ATR14, active from leg confirmation until the first touch
or `wait` bars. Mirrors s26Boxes in modules/ws/15_ws_hub_indicators.js (parity: tests/test_reversal_boxes_js_parity.py).
"""
from modules import two_six_chart as tc


def reversal_boxes(bars, ratio=2.6, left=3, right=3, min_atr=2.0, half=0.25, wait=80):
    n = len(bars)
    atr = tc.atr14(bars)
    legs = tc.real_legs(bars, tc.es.confirmed_pivots(bars, left, right), min_atr)
    out = []
    for a, b in legs:
        known = b.known_at
        if known >= n - 1:
            continue
        r = abs(a.price - b.price)
        up = a.kind == "L"
        zone = a.price - r / ratio if up else a.price + r / ratio
        h = half * atr[min(known, n - 1)]
        touch = None
        for i in range(known + 1, min(n, known + 1 + wait)):
            bi = bars[i]
            if bi.low <= zone + h and bi.high >= zone - h:
                touch = i
                break
        end = touch if touch is not None else min(n - 1, known + wait)
        out.append({"dir": "BUY" if up else "SELL", "zone": zone, "top": zone + h, "bottom": zone - h,
                    "start": known, "end": end, "touched": touch is not None})
    return out
