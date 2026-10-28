"""English twins of the texts in modules/arabic.py (owner rule 2026-10-23: one language at a time).
Same inputs and same return shapes as the Arabic functions; modules/arabic.py calls these when the page language is English.
Wording stays descriptive and educational: it says what the detector saw, never what price will do."""
from __future__ import annotations

from modules.signals import fp

TRADE_EN = {"Scalp": "Scalp", "Day Trade": "Day trade", "Swing": "Swing", "Position": "Position"}
TF_EN = {"1m": "1 min", "13m": "13 min", "1h": "1 hour", "2h": "2 hours", "3h": "3 hours", "6h": "6 hours", "7h": "7 hours", "8h": "8 hours",
         "12h": "12 hours", "1d": "Daily", "3d": "3 days", "1w": "Weekly", "1mo": "Monthly"}
DIR_EN = {"bullish": "Bullish", "bearish": "Bearish", "neutral": "Neutral"}

# tag text per detector family / key (colours stay in modules/arabic.py)
TAGS_EN = {"Elliott": "Elliott", "Unicorn": "Unicorn", "MSB-OB": "MSB-OB", "Fib": "Fib", "MA": "MAs", "VWAP": "VWAP", "TL": "Trend break"}
KEY_TAGS_EN = {
    "m2022": "Model 2022", "cisd": "CISD", "tlbreak": "Trend break", "sweep": "Liquidity", "liqline": "Liquidity", "breakout": "Breakout",
    "ohl_break": "Breakout", "ohl_open": "OHL", "level": "Support/Resistance", "zombie": "Zombie", "ew3": "Wave 3", "ob": "OB", "ote": "OTE",
    "fvg": "FVG", "breaker": "Breaker", "judas": "Judas", "crt": "CRT", "smt": "SMT", "rsi_div": "RSI divergence", "macd_div": "MACD divergence",
    "donch": "Donchian", "sess_amd": "Session AMD", "orb": "Opening range", "kzs": "KZ sniper", "po3": "Power of 3", "sma1040": "SMA 10/40",
    "turtle55": "Turtle 55",
}


def signal_en(s: dict) -> tuple:
    """(English name, English detail) for one finalized signal dict (twin of arabic.signal_ar)."""
    k, p, v = s.get("key"), s.get("prices", {}), s.get("vals", {})
    bull = s["direction"] == "bullish"
    up, dn = ("above", "below") if bull else ("below", "above")
    f = lambda key: fp(p[key]) if key in p else "-"
    ago = v.get("ago", "?")
    pct = lambda key: format(v.get(key, 0), ".0%")
    if k == "m2022":
        return ("Model 2022: sweep + structure break + FVG" if bull else "Model 2022 (bearish)",
                f"Swept the {'low' if bull else 'high'} {f('lvl')}, then an impulse candle closed {up} the {'high' if bull else 'low'} {f('sh')} {ago} candles ago and left an FVG gap; "
                f"entry inside the gap · stop {dn} the sweep ({f('sl')}) · target the liquidity pool {f('pool')} · inside the New York kill zone")
    if k == "cisd":
        q = f" · confirmations: {v.get('q', 0)}" if v.get("q") else ""
        return ("Liquidity sweep + CISD" if bull else "Liquidity sweep + CISD (bearish)",
                f"Price swept the {'low' if bull else 'high'} {f('lvl')}, then a candle body closed {up} the CISD level ({f('cl')}) {ago} candles ago and structure has not broken yet · "
                f"stop {dn} the sweep ({f('sl')}) · target {f('st')}{q}")
    if k == "tlbreak":
        why = {"volume expansion": "volume above normal", "3+ touches": "3 touches on the line", "strong close": "a strong breakout candle", "retest held": "the retest held"}
        en = s.get("detail", "").split("confirmed by: ")[-1].split(", ") if "confirmed by" in s.get("detail", "") else []
        return ("Downtrend line broken upward" if bull else "Uptrend line broken downward",
                f"Close {up} the trendline ({f('tp')}) {ago} candles ago · touches {v.get('touches', '?')} · confirmations: " + (", ".join(why.get(x, x) for x in en) or "-"))
    if k == "ma_cross":
        nm = s["name"].replace(" bullish cross", "").replace(" bearish cross", "")
        return (f"{nm} {'bullish' if bull else 'bearish'} cross",
                f"The fast average crossed the slow one {'upward' if bull else 'downward'} {ago} candles ago")
    if k == "ema_stack":
        return ("EMA 9/21/50 order", f"Price {up} fully ordered averages (a strong {'uptrend' if bull else 'downtrend'})")
    if k == "vwap":
        return (f"{up.capitalize()} VWAP", f"Price {f('p')} is {up} the rolling VWAP {f('v')} (the fair-value balance point supports {'buying' if bull else 'selling'})")
    if k == "ew3":
        ideal = " (ideal zone 50-61.8%)" if v.get("ideal") else ""
        return ("Start of wave 3 (Elliott)",
                f"Wave 2 retraced {pct('ret')} of wave 1{ideal} and bounced from {v.get('ma_name', 'the average')} at {f('ma')}; target 1.618 x wave 1 = {f('t')}; "
                f"the idea is cancelled {dn} {f('inv')}")
    if k == "ew5":
        return ("Start of wave 5 (Elliott)",
                f"Wave 4 retraced {pct('ret')} of wave 3 (typical 38.2%); target: wave 5 = wave 1 at {f('t1')}, "
                f"or 1.618x from the start of wave 1 to the end of wave 3 at {f('t2')}")
    if k == "abc":
        return ("Start of an ABC correction (wave A)",
                f"A 5-wave impulse completed at {f('top')}; price has retraced 23.6%+ of it; the usual correction 38.2-61.8% = {f('a')} - {f('b')}")
    if k == "wavec":
        return ("Start of wave C",
                f"After the impulse and waves A-B, price is moving away from B ({f('b')}); wave C target = the length of A at {f('t1')}, or 1.618xA at {f('t2')}")
    if k == "fib":
        label = str(v.get("label", ""))
        label = (label.replace("Gold zone", "Golden zone")
                 .replace("38.2% pullback (strong-trend continuation)", "38.2% pullback (strong-trend continuation)")
                 .replace("23.6% pullback (very strong trend)", "23.6% pullback (very strong trend)"))
        return ("Fibonacci zone",
                f"Price is at a {pct('ret')} retracement of the last {'rising' if bull else 'falling'} wave ({label}); "
                f"extensions 1.272/1.618/2.0: {f('x1')} / {f('x2')} / {f('x3')}; Monkey targets: {f('m1')} / {f('m2')} / {f('m3')}; "
                f"wave start {f('start')}")
    if k == "msb_ob":
        return ("Structure break + order block retest",
                f"Close {up} the structure {'high' if bull else 'low'} {f('lvl')}; price is retesting the order block {f('zl')} - {f('zh')} "
                f"(the idea is cancelled {dn} {f('zl') if bull else f('zh')})")
    if k == "sweep":
        return (f"{'Sell-side' if bull else 'Buy-side'} liquidity sweep",
                f"The candle's wick broke the {'low' if bull else 'high'} {f('lvl')} and closed back {up} the level - stops were collected")
    if k == "unicorn":
        return ("ICT Unicorn (retest)",
                f"Liquidity sweep at {f('lvl')}, then a structure shift {f('hh')}, and a breaker block overlapping a fair value gap (FVG) at {f('zl')} - {f('zh')}")
    if k == "zombie":
        return ("Zombie move (liquidity sweep at EMA9)",
                f"A wick broke the {'low' if bull else 'high'} {f('lvl')} at EMA9 ({f('e')}) then rebounded hard {'upward' if bull else 'downward'} - stops swept, then a quick reversal")
    if k == "ob":
        fresh = v.get("fresh")
        return ("Order block " + ("fresh (untested)" if fresh else "tested"),
                f"{'Bullish' if bull else 'Bearish'} order block {f('zl')} - {f('zh')} before the structure break at {f('lvl')}; "
                + ("price has not returned to it before (unmitigated) - stronger" if fresh else "price touched it before and it is still valid - weaker")
                + f"; the idea is cancelled by a close {dn} {f('zl') if bull else f('zh')}")
    if k == "ote":
        return ("OTE entry (62-79% zone)",
                f"An impulse wave from {f('a')} to {f('b')}; price retraced {pct('ret')} into the optimal entry zone {f('zl')} - {f('zh')}")
    if k == "fvg":
        return ("Fair value gap (FVG) retest",
                f"A {'bullish' if bull else 'bearish'} price gap {f('zl')} - {f('zh')} (formed {ago} candles ago) not closed yet; price is filling it - a {'support' if bull else 'resistance'} zone")
    if k == "breaker":
        return ("Breaker block retest",
                f"Liquidity sweep at {f('lvl')}, then a structure shift {f('hh')}; price is retesting the breaker {f('zl')} - {f('zh')}")
    if k == "judas":
        return ("Judas swing (fake move at the open)",
                f"After today's open {f('op')}, price {'dropped' if bull else 'rose'} falsely to {f('lo')} (stop sweep) then reclaimed the open and trades {up} it")
    if k == "sess_amd":
        return (f"Session AMD: sweep of the Asia range {'low' if bull else 'high'}",
                f"The Asia range (accumulation) {'low' if bull else 'high'} {f('al')} was swept down to {f('sw')} in the London window (manipulation), then price closed back inside the range; "
                f"the distribution phase targets the Asia range {'high' if bull else 'low'} {f('ah')}, stop {dn} the sweep area {f('sw')}")
    if k == "orb":
        sess = "London" if v.get("sess") == "London" else "New York"
        return (f"{sess} opening range breakout",
                f"The first-15-minute range after the {sess} open ran from {f('ol')} to {f('oh')}; price closed {'above the high' if bull else 'below the low'} of the range and did not close on the other side; "
                f"stop {dn} the range {'low' if bull else 'high'}")
    if k == "donch":
        return (f"Donchian channels (combined trend) {'bullish' if bull else 'bearish'}",
                f"{v.get('k', '?')} of {v.get('m', '?')} Donchian channels (from {v.get('lo', '?')} to {v.get('hi', '?')} candles) are in a {'bullish' if bull else 'bearish'} breakout state "
                f"(close {up} the {'highest' if bull else 'lowest'} close in the channel), and a fresh breakout happened in the last 3 candles; trend following by combining several periods instead of one")
    if k == "sma1040":
        return (f"SMA 10/40 {'bullish' if bull else 'bearish'} cross (hedge-fund rule)",
                f"The 10-average {f('s10')} crossed the 40-average {f('s40')} {'upward' if bull else 'downward'} {v.get('ago', 0)} candles ago and the close is {up} both; "
                f"a trend-following rule used by futures funds; stop 2N (twice the ATR of the last 20 candles) at {f('inv')}")
    if k == "turtle55":
        return (f"Donchian 55 breakout {'upward' if bull else 'downward'} (Turtle system 2)",
                f"A close {'above the highest high' if bull else 'below the lowest low'} of the last 55 candles {f('lvl')}, {v.get('ago', 0)} candles ago: a Turtle system 2 entry; "
                f"stop 2N at {f('inv')}, trailing exit on a close {'below the lowest low' if bull else 'above the highest high'} of the last 20 candles {f('x')}")
    if k == "kzs":
        vr = f" and volume {v.get('vr')}x the usual" if v.get("vr") else ""
        return (f"Kill Zone Sniper: sweep of the last 20 candles' {'low' if bull else 'high'} inside the kill zone",
                f"Inside the {'London' if v.get('kz') == 'London' else 'New York'} kill zone a candle broke the {'low' if bull else 'high'} of the last 20 candles {f('lvl')} and closed back {up} the level with an impulsive body{vr}; "
                f"stop {dn} the sweep wick {f('sl')}, target {f('t')}")
    if k == "po3":
        return ("Power of Three: rebound after manipulation inside the kill zone",
                f"Today's open {f('op')}; price dropped on manipulation to {f('ml')} inside the kill zone, then rebounded with an impulse candle and closed {up} today's open (rebound confirmation); "
                f"stop {dn} the manipulation low, distribution target {f('t')}")
    if k == "crt":
        tf = v.get("tf", "")
        return (f"CRT: sweep of a {tf} candle's {'low' if bull else 'high'} then a return",
                f"The {tf} reference candle runs from {f('rl')} (the swept side) to {f('rh')} (the opposite side); price broke the range {'low' if bull else 'high'} with a wick (liquidity sweep) then closed back inside; "
                f"entry at the return close, stop {dn} the sweep wick {f('sl')}, target the opposite side of the range {f('rh')}")
    if k == "smt":
        peer = v.get("peer", "")
        return (f"SMT: no confirmation from {peer}",
                f"This market made a {'lower low' if bull else 'higher high'} {f('p2')} (previous {f('p1')}) but {peer} did not confirm the move and held a {'higher low' if bull else 'lower high'} than before; "
                f"disagreement between correlated markets = a {'bullish' if bull else 'bearish'} reversal footprint (SMT)")
    if k in ("rsi_div", "macd_div"):
        nm = "RSI" if k == "rsi_div" else "MACD"
        return (f"{nm} {'bullish' if bull else 'bearish'} divergence",
                f"Price made a {'lower low' if bull else 'higher high'} {f('p2')} (previous {f('p1')}) while {nm} made a {'higher low' if bull else 'lower high'} "
                f"({v.get('o2', '?')} vs {v.get('o1', '?')}) - momentum does not confirm the move, and a {'bullish' if bull else 'bearish'} reversal is possible")
    if k == "liqline":
        return ("Liquidity line break", f"A close across the liquidity level {f('lvl')} (a level built on unusually high volume)")
    if k == "ohl_open":
        return (f"OHL: open = {'low' if bull else 'high'}",
                f"The candle opened at its {'low' if bull else 'high'} and closed {'up' if bull else 'down'} - {'buyers' if bull else 'sellers'} in control from the open")
    if k == "ohl_break":
        return (f"OHL: break of the previous candle's {'high' if bull else 'low'}",
                f"A strong close {up} the previous candle's {'high' if bull else 'low'} ({f('ph')})")
    if k == "level":
        return (f"At {'support' if bull else 'resistance'}", f"Price is on a {'support' if bull else 'resistance'} level {f('lvl')}")
    if k == "breakout":
        n = "".join(ch for ch in s["name"] if ch.isdigit()) or "20"
        return (f"{'Breakout' if bull else 'Breakdown'} of the last {n} candles",
                f"A close {'above the highest' if bull else 'below the lowest'} of {n} candles at {f('lvl')}")
    return (s.get("name", ""), s.get("detail", ""))


def htf_lines_en(res: dict, signal_name) -> list:
    out = []
    for h in res.get("htf", []):
        label = TF_EN.get(h["tf"], h["tf"])
        if not h["available"]:
            out.append(f"{label}: no data")
        elif h["confirms"]:
            names = ", ".join(signal_name(s)[0] for s in h["confirms"][:3])
            out.append(f"{label}: confirms - {names}")
        else:
            trend = "trend aligned, " if h.get("trend_aligned") else ""
            out.append(f"{label}: {trend}no structure/zone signal in this direction")
    return out


def scenarios_en(res: dict) -> list:
    d = res["direction"]
    if d == "neutral" or not res["signals"]:
        return ["No dominant direction - nothing to plan for. Wait for signals to line up."]
    long = d == "bullish"
    prices = {}
    for s in res["signals"]:
        prices.update(s["prices"])
    zones = [s["zone"] for s in res["signals"] if s.get("zone")]
    inv = prices.get("inv") or prices.get("start")
    if zones:
        lo, hi = zones[0]
        inv = lo if long else hi
    tgt = prices.get("t") or prices.get("x1") or prices.get("t1") or prices.get("m3")
    first = ("1) The zone/level holds: wait for a candle that " + ("holds and bounces" if long else "holds and is rejected")
             + f", then enter {'long' if long else 'short'}" + (f"; first target around {fp(tgt)}." if tgt else "."))
    out = [first]
    if inv:
        out.append(f"2) The level fails: a candle closing {'below' if long else 'above'} {fp(inv)} cancels the idea - step aside or look at the opposite direction.")
    out.append("3) Trap: price breaks out, then returns and closes back - do not fade the breakout until the order book / trades confirm it (wall absorbed and no follow-through).")
    return out


def context_en(c: dict) -> list:
    ag = c.get("agree") or {}
    mark = lambda v: "" if v is None else (" ✓" if v else " ✗")
    out = []
    db = c.get("daily") or {}
    if db.get("bias"):
        nm = {"bullish": "bullish (yesterday closed above the previous day's high)", "bearish": "bearish (yesterday closed below the previous day's low)",
              "inside": "no bias (yesterday stayed inside the previous day's range)", "neutral": "no bias (yesterday closed inside the range)"}[db["bias"]]
        out.append("Daily bias: " + nm + mark(ag.get("bias")))
    if db.get("accumulation"):
        out.append("⚠ Two inside days in a row = accumulation, better not to trade" + mark(not ag.get("stand_aside", False) if "stand_aside" in ag else None))
    pdz = c.get("pd") or {}
    if pdz.get("zone"):
        nm = {"discount": "discount (buy zone)", "premium": "premium (sell zone)", "equilibrium": "mid-range"}[pdz["zone"]]
        out.append(f"Price position in the range: {nm} {round(pdz.get('pos', 0))}%" + mark(ag.get("pd")))
    w = c.get("window") or {}
    if w.get("ny_hour") is not None:
        nm = (("Kill zone " + w["kz"]) if w.get("kz") else "") + (" · Silver Bullet window" if w.get("silver") else "")
        out.append("Timing: " + (nm.strip(" ·") or "outside the kill zone") + mark(ag.get("window")))
    return out


def duration_en(seconds: float) -> str:
    if seconds < 90 * 60:
        return f"~{max(1, round(seconds / 60))} min"
    if seconds < 48 * 3600:
        return f"~{round(seconds / 3600)} h"
    if seconds < 21 * 86400:
        return f"~{round(seconds / 86400)} d"
    return f"~{round(seconds / 604800)} wk"
