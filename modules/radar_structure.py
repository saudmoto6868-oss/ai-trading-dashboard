"""Structure read-out for a Radar chart (owner 2026-11-16): SMT, chart patterns, candlestick patterns, Elliott setups,
price action and trendline support / resistance, with the direction and a three-step plain explanation (1, 2, 3).
Built only from the scanner flags already computed per symbol. Read only: research, not a trade signal."""
from __future__ import annotations

from modules.radar_open_setups import direction_of

# flag -> (group, English name, what it means in three steps)
_LABELS = {
    "st_smt": ("SMT", "SMT divergence", ["Two correlated markets make a new extreme; one of them does not.", "The divergence is marked on the chart where the swing happened.", "It is weak if the peer does not confirm it on the next swing."]),
    "sch_smt": ("SMT", "SMT divergence (scanner)", ["The same SMT check, run on the scanner universe.", "Compare the swing points on this chart with the peer.", "Needs a confirming candle; the scanner does not wait for it."]),
    "st_elliott": ("Elliott", "Elliott wave setup", ["Price shows a 5-wave impulse or a corrective count on the scanner window.", "Wave 2 and wave 4 rules are checked on the swing points.", "The count is a view, not a fact: a break of the wave start cancels it."]),
    "sch_elliott": ("Elliott", "Elliott wave (scanner)", ["Elliott count from the scanner, same rules as above.", "Look at where the current wave starts.", "Invalid if the wave start is broken."]),
    "st_ew3": ("Elliott", "Elliott wave 3", ["Wave 3 is the strongest move of the count.", "It starts after the wave 2 correction holds above the wave 1 start.", "A deep correction below wave 1 start cancels the count."]),
    "dbl_top": ("Chart pattern", "Double top", ["Two swing highs at about the same level.", "The neckline is the low between them.", "Bearish only after a close below the neckline."]),
    "dbl_bottom": ("Chart pattern", "Double bottom", ["Two swing lows at about the same level.", "The neckline is the high between them.", "Bullish only after a close above the neckline."]),
    "cp_wedge_up": ("Chart pattern", "Rising wedge", ["Higher highs and higher lows with a narrowing range.", "Often ends with a break of the lower line.", "The pattern is void if price closes above the upper line."]),
    "cp_wedge_dn": ("Chart pattern", "Falling wedge", ["Lower highs and lower lows with a narrowing range.", "Often ends with a break of the upper line.", "The pattern is void if price closes below the lower line."]),
    "cp_tri_asc": ("Chart pattern", "Ascending triangle", ["Flat top, rising lows.", "Bullish on a close above the flat top.", "Invalid if the rising lows break."]),
    "cp_tri_desc": ("Chart pattern", "Descending triangle", ["Flat bottom, falling highs.", "Bearish on a close below the flat bottom.", "Invalid if the falling highs break."]),
    "cp_tri_sym": ("Chart pattern", "Symmetrical triangle", ["Falling highs and rising lows meet.", "Direction is decided by the breakout close.", "Wait for the close; the first touch is not a signal."]),
    "cp_multi_bottom": ("Chart pattern", "Multiple bottoms", ["Three or more lows at about the same level.", "The level is the support.", "Broken if price closes below it."]),
    "st_pa_engulf": ("Candlestick", "Engulfing candle", ["A candle's body fully covers the body of the previous candle.", "Opposite colour to the trend it reverses.", "Needs context: a support or resistance level nearby."]),
    "st_pa_inside": ("Candlestick", "Inside bar", ["The candle's range is inside the previous candle.", "Shows compression before a move.", "Direction comes from the break of the mother candle."]),
    "st_pa_pin": ("Candlestick", "Pin bar", ["Long wick, small body: price was rejected.", "Stronger at a level.", "Invalid if the next candle closes through the wick."]),
    "st_pa_star": ("Candlestick", "Morning / evening star", ["Three candles: a strong move, an indecision candle, a reversal candle.", "The third candle must close into the first body.", "Needs a confirming close after the pattern."]),
    "st_breaker": ("Price action", "Breaker block", ["A failed order block that price closed through.", "The old zone now acts as the opposite level.", "Invalid if price closes back through it."]),
    "cp_tl_support": ("Support / resistance", "Trendline support", ["A rising line touched at least twice.", "Price is near it now.", "Broken on a close below the line."]),
    "cp_tl_resist": ("Support / resistance", "Trendline resistance", ["A falling line touched at least twice.", "Price is near it now.", "Broken on a close above the line."]),
}


def read(d: dict) -> list[dict]:
    """Structure items found on one chart result (the scanner dict: 'flags', 'sides')."""
    out = []
    for flag in d.get("flags") or []:
        lab = _LABELS.get(flag)
        if not lab:
            continue
        group, name, steps = lab
        out.append({"group": group, "name": name, "direction": direction_of(flag, d), "steps": steps})
    return out


def html_block(items: list[dict], lang_ar: bool = False) -> str:
    """Small HTML list: group, name, direction, then the three steps. Empty when nothing was found."""
    import html as _h
    if not items:
        return "<div class='xr-hint'>No SMT, pattern, Elliott or support/resistance reading on this chart now.</div>"
    rows = []
    for it in items:
        steps = "".join(f"<div>{i}. {_h.escape(s)}</div>" for i, s in enumerate(it["steps"], 1))
        col = {"long": "#0ecb81", "short": "#f6465d"}.get(it["direction"], "#9aa3ad")
        rows.append(f"<div style='margin:3px 0'><b style='color:#eaecef'>{_h.escape(it['group'])}</b> · "
                    f"{_h.escape(it['name'])} <span style='color:{col}'>({_h.escape(it['direction'])})</span>{steps}</div>")
    return "<div style='font-size:11px;line-height:16px;color:#c9d1d9'>" + "".join(rows) + "<div class='xr-hint'>Reading only, not a trade signal.</div></div>"
