"""X77 phase 3: run the repo's existing OHLCV detectors on one candle frame and label each hit with an X77 school / event.

No new detection math here: signals.detect_all, patterns.find and regime.classify do the work. This file only maps their
keys to the X77 taxonomy (data/x77/taxonomy.json, 2026-11-20). A label is a description, not evidence: lab numbers decide.
"""
from __future__ import annotations

import pandas as pd

from modules import patterns, regime, signals

# lab key -> (school, event); copied from data/x77/taxonomy.json (git-ignored) so the code runs without it
KEY_MAP = {
    "level": ("S_SR", "E_SR_TOUCH"), "tlbreak": ("S_SR", "E_SR_FLIP"), "breakout": ("S_SR", "E_SR_BREAK"),
    "ma_cross": ("S_MA", "E_MA_CROSS"), "ema_stack": ("S_MA", "E_MA_STACK"), "sma1040": ("S_MA", "E_MA_SMA1040"),
    "vwap": ("S_VP", "E_VP_POC"),
    "msb_ob": ("S_SMC_ICT", "E_SMC_BOS"), "ob": ("S_SMC_ICT", "E_SMC_OB"), "fvg": ("S_SMC_ICT", "E_SMC_FVG"),
    "sweep": ("S_SMC_ICT", "E_SMC_SWEEP"), "breaker": ("S_SMC_ICT", "E_SMC_BREAKER"), "ote": ("S_SMC_ICT", "E_SMC_OTE"),
    "unicorn": ("S_SMC_ICT", "E_SMC_UNICORN"), "judas": ("S_SMC_ICT", "E_SMC_JUDAS"), "kzs": ("S_SMC_ICT", "E_SMC_KZ"),
    "cisd": ("S_SMC_ICT", "E_SMC_CISD"), "m2022": ("S_SMC_ICT", "E_SMC_M2022"), "crt": ("S_SMC_ICT", "E_SMC_CRT"),
    "sess_amd": ("S_AMD", "E_AMD_ASIA_RANGE"), "po3": ("S_AMD", "E_AMD_MANIP"), "orb": ("S_AMD", "E_AMD_ORB"),
    "ew3": ("S_ELLIOTT", "E_EW_WAVE3_START"), "ew5": ("S_ELLIOTT", "E_EW_IMP"), "abc": ("S_ELLIOTT", "E_EW_ABC"),
    "wavec": ("S_ELLIOTT", "E_EW_ABC"), "fib": ("S_FIB", "F_RET_W2"),
    "rsi_div": ("S_OSC", "E_OSC_RSI_DIV"), "macd_div": ("S_OSC", "E_OSC_MACD_DIV"), "smt": ("S_SMT", "E_SMT"),
    "donch": ("S_STRUCTURE", "E_ST_HH_HL"), "turtle55": ("S_STRUCTURE", "E_ST_TURTLE"), "zombie": ("S_STRUCTURE", "E_ST_ZOMBIE"),
    "pa_engulf": ("S_CANDLES", "E_C_ENGULF"), "pa_pin": ("S_CANDLES", "E_C_PIN"), "pa_inside": ("S_CANDLES", "E_C_INSIDE"),
    "pa_star": ("S_CANDLES", "E_C_STAR"), "rect": ("S_CLASSIC", "E_CP_RECT"), "dbl": ("S_CLASSIC", "E_CP_DOUBLE"),
    "wyck": ("S_WYCKOFF", "E_WY_SPRING"),
}


# school -> (Arabic name, English name, one-line Arabic explanation); shown on the X77 page, widget and chart labels
SCHOOLS = {
    "S_SR": ("دعم ومقاومة", "Support / resistance", "السعر عند مستوى اتلمس قبل كده: ارتداد أو كسر."),
    "S_MA": ("المتوسطات", "Moving averages", "اتجاه الترند من ترتيب وتقاطع المتوسطات."),
    "S_VP": ("الفوليوم / VWAP", "Volume / VWAP", "السعر فوق أو تحت متوسط السعر بالحجم (القيمة العادلة)."),
    "S_SMC_ICT": ("SMC / ICT", "SMC / ICT", "سيولة واوردر بلوك وفجوات وكسر هيكل (فلوس كبيرة)."),
    "S_AMD": ("جلسات AMD", "Sessions (AMD)", "تجميع ثم تلاعب ثم توزيع حسب جلسات اليوم."),
    "S_ELLIOTT": ("إليوت", "Elliott wave", "عد الموجات: دافعة 5 وتصحيح ABC."),
    "S_FIB": ("فيبوناتشي", "Fibonacci", "ارتداد لنسب فيبو (0.5 / 0.618 / OTE 0.62-0.79)."),
    "S_OSC": ("الدايفرجنس", "Divergence", "السعر عمل قاع/قمة جديدة والـ RSI أو MACD ماأكدش."),
    "S_SMT": ("SMT", "SMT", "زوجين مرتبطين واحد كسر والتاني ماكسرش."),
    "S_STRUCTURE": ("الهيكل والترند", "Structure / trend", "قمم وقيعان أعلى أو أقل، اختراق قنوات (ترتل / دونشيان)."),
    "S_CANDLES": ("الشموع", "Candles", "شمعة رفض أو ابتلاع أو نجمة عند منطقة مهمة."),
    "S_CLASSIC": ("النماذج الكلاسيك", "Classic patterns", "مثلثات وقنوات ورأس وكتفين وقمتين وقاعين."),
    "S_WYCKOFF": ("وايكوف", "Wyckoff", "سبرينج أو أبثرست: كسر وهمي للرينج ورجوع."),
    "S_OTHER": ("غير مصنف", "Other", "إشارة لسه ماتصنفتش في X77."),
}


def js_config() -> dict:
    """What the Workspace X77 widget needs: key -> school, school -> names + Arabic explanation."""
    return {"keys": {k: v[0] for k, v in KEY_MAP.items()}, "schools": {s: list(v) for s, v in SCHOOLS.items()}}


def events(df: pd.DataFrame) -> dict:
    """-> {'events': [{school, event, key, side, name, detail}], 'patterns': [{school, event, key, side}], 'regime': str|None, 'errors': [...]}."""
    out = {"events": [], "patterns": [], "regime": None, "errors": []}
    if df is None or len(df) < 60:
        out["errors"].append("not enough candles (need 60)")
        return out
    sigs, errs = signals.detect_all(df)
    out["errors"] += errs
    for s in sigs:
        school, ev = KEY_MAP.get(s["key"], ("S_OTHER", "E_" + s["key"].upper()))
        out["events"].append({"school": school, "event": ev, "key": s["key"], "side": s["direction"],
                              "name": s["name"], "detail": s["detail"]})
    try:
        for pid in patterns.find(df):
            name, side = patterns.PATTERNS.get(pid, (pid, None))
            out["patterns"].append({"school": "S_CLASSIC", "event": pid.upper(), "key": pid, "side": side, "name": name})
    except Exception as exc:  # one broken detector must not kill the rest
        out["errors"].append(f"patterns: {exc}")
    try:
        out["regime"] = regime.classify(df).get("regime")
    except Exception as exc:
        out["errors"].append(f"regime: {exc}")
    return out


def summary(res: dict) -> dict:
    """school -> count of hits (events + chart patterns)."""
    cnt: dict = {}
    for e in res["events"] + res["patterns"]:
        cnt[e["school"]] = cnt.get(e["school"], 0) + 1
    return dict(sorted(cnt.items(), key=lambda kv: -kv[1]))
