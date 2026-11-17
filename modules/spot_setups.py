"""Spot setup library (owner 2026-11-06: 'collect EVERY entry / exit setup of every school, not only my examples, and keep
reviewing and adding').

Two sources, one list:
  1. Every Radar detector (signals.detect_all: SMC / ICT, liquidity, Fibonacci, Elliott, divergence, trend, levels, price
     action, chart patterns, Wyckoff ...) + harmonic patterns + SMT, run on the SPOT timeframes 1M / 1W / 1D. Bullish = a buy
     setup, bearish = an EXIT setup (spot never shorts: it tells us to sell / protect what we hold).
  2. Spot setups the scanner does not have (CATALOG below): more Elliott positions (wave 2, wave 4, wave 5 done), more
     divergences (hidden, triple, MACD histogram, MA-distance, volume / OBV), Gann (square of 9 + time window, 50 % of the
     range, 1x1 angle from the major low, time anniversaries), classic (golden / death cross, 200-week reclaim / loss,
     52-week breakout, Bollinger squeeze), cycle value (Mayer, 200-week, drawdown), institutions (COT extremes) and order flow
     (funding crowding, CVD).
Each live setup: id, school, Arabic name, side (buy / exit), timeframe, horizon, entry zone, stop, target, why, and its
EVIDENCE from the weekly setup lab (data/spot_setup_evidence.json: n, hit %, average 4- / 12-bar return, verdict).
NOTHING here is promoted to a signal without n >= 30 and a clear result; until then the card says 'not evidence'."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

EVIDENCE = Path(__file__).resolve().parent.parent / "data" / "spot_setup_evidence.json"
TF_H = {"1mo": "شهور لسنة", "1w": "أسابيع لشهور", "1d": "أيام لأسابيع", "4h": "ساعات لأيام"}
TF_AR = {"1mo": "شهري", "1w": "أسبوعي", "1d": "يومي", "4h": "4 ساعات"}

# school of each Radar key (strategy_lab.SCHOOL), Arabic labels for the schools
SCHOOL_AR = {"Trend (MA)": "الترند (متوسطات)", "Trend (hedge fund)": "الترند (صناديق)", "SMC / ICT": "SMC / ICT", "Fibonacci": "فيبوناتشي",
             "Liquidity": "السيولة", "Time (sessions)": "الزمن / الجلسات", "Elliott wave": "اليوت", "Momentum / divergence": "الزخم / الدايفرجنس",
             "Levels / breakouts": "المستويات / الاختراق", "Intermarket (SMT)": "SMT", "Price action": "برايس أكشن", "Chart patterns (range)": "نماذج كلاسيك",
             "Wyckoff": "وايكوف", "Harmonic": "هارمونيك", "Gann": "جان", "Classic": "كلاسيك", "Cycle value": "قيمة الدورة", "Institutions": "المؤسسات",
             "Order flow": "الأوردر فلو"}

# spot-only setups (id -> school, Arabic name, side, what it means)
CATALOG = {
    "ew_w2": ("Elliott wave", "اليوت: دخول الموجة 2 (تصحيح 50-61.8% بعد موجة 1)", "buy", "أول موجة دافعة خلصت والتصحيح وقف قبل بدايتها - أحسن دخول قبل الموجة 3"),
    "ew_w3_go": ("Elliott wave", "اليوت: تأكيد الموجة 3 (كسر قمة الموجة 1)", "buy", "السعر كسر قمة الموجة 1 بعد ما الموجة 2 مسكت - الموجة 3 بدأت"),
    "ew_w4": ("Elliott wave", "اليوت: دخول الموجة 4 (تصحيح 38.2%)", "buy", "تصحيح ضحل بعد موجة 3 قوية من غير ما يدخل منطقة الموجة 1 - فاضل موجة 5"),
    "ew_w5_done": ("Elliott wave", "اليوت: الموجة 5 خلصت - خروج", "exit", "5 موجات اكتملت - التصحيح ABC جاي، اجني ربح"),
    "div_hidden_bull": ("Momentum / divergence", "دايفرجنس RSI مخفي صاعد (استمرار الترند)", "buy", "السعر عمل قاع أعلى والـ RSI قاع أوطى - الترند الصاعد مكمّل"),
    "div_triple": ("Momentum / divergence", "دايفرجنس ثلاثي (3 قيعان)", "buy", "تلات قيعان أوطى في السعر والزخم كل مرة أعلى - إرهاق بيع قوي"),
    "div_macd_hist": ("Momentum / divergence", "دايفرجنس هيستوجرام MACD", "buy", "قاع سعري أوطى وهيستوجرام MACD قاعه أعلى"),
    "div_ma_dist": ("Momentum / divergence", "دايفرجنس البعد عن المتوسط (EMA 50)", "buy", "السعر عمل قاع أوطى بس بعده تحت EMA 50 أقل - البيع بيضعف"),
    "div_obv": ("Momentum / divergence", "دايفرجنس الفوليوم (OBV)", "buy", "السعر قاع أوطى والـ OBV قاع أعلى - فيه تجميع"),
    "div_bear_premium": ("Momentum / divergence", "دايفرجنس هابط في البريميوم - خروج", "exit", "قمة أعلى في السعر وقمة أوطى في الزخم والسعر غالي"),
    "gann_sq9_time": ("Gann", "جان: مستوى مربع التسعة + نافذة زمنية", "buy", "السعر على مستوى جان في نفس وقت دورة زمنية"),
    "gann_50": ("Gann", "جان: 50% من الرينج الكبير", "buy", "جان كان بيعتبر نص الرينج أهم مستوى دعم"),
    "gann_1x1": ("Gann", "جان: زاوية 1x1 من القاع الكبير", "buy", "السعر نزل على زاوية 1x1 (سعر = زمن) ومسك - الترند الصاعد سليم"),
    "gann_anniv": ("Gann", "جان: ذكرى زمنية (90 / 180 / 360 يوم من قاع / قمة كبيرة)", "buy", "مواعيد جان الزمنية بتتكرر عندها انعكاسات"),
    "cl_golden": ("Classic", "كلاسيك: الجولدن كروس (50 فوق 200 يومي)", "buy", "المتوسط 50 عدى فوق 200 - تغير ترند طويل"),
    "cl_death": ("Classic", "كلاسيك: الديث كروس - خروج", "exit", "المتوسط 50 نزل تحت 200 - الترند الطويل اتقلب"),
    "cl_200w_reclaim": ("Classic", "كلاسيك: رجوع فوق متوسط 200 أسبوع", "buy", "قفلة أسبوعية فوق متوسط 200 أسبوع بعد ما كان تحته"),
    "cl_200w_loss": ("Classic", "كلاسيك: كسر متوسط 200 أسبوع - خروج", "exit", "قفلة أسبوعية تحت متوسط 200 أسبوع"),
    "cl_52w_break": ("Classic", "كلاسيك: اختراق قمة 52 أسبوع", "buy", "قمة سنة جديدة على قفلة أسبوعية"),
    "cl_bb_squeeze": ("Classic", "كلاسيك: انفجار بعد انضغاط بولينجر", "buy", "البولينجر في أضيق حالاته وقفلة فوق الحد العلوي"),
    "val_mayer": ("Cycle value", "قيمة: مضاعف ماير تحت 0.8 (تجميع على دفعات)", "buy", "السعر تحت متوسط 200 يوم بـ 20% أو أكتر - تاريخيًا منطقة تجميع"),
    "val_200w": ("Cycle value", "قيمة: السعر تحت متوسط 200 أسبوع", "buy", "تحت متوسط 4 سنين - نادرًا ما بيحصل"),
    "val_hot": ("Cycle value", "قيمة: سخونة (ماير فوق 2.4) - خروج جزئي", "exit", "السعر بعيد جدًا عن متوسط 200 يوم"),
    "inst_comm_long": ("Institutions", "المؤسسات: التجار شاريين بزيادة (COT ≥ 90%)", "buy", "الفلوس الذكية في أعلى شراء ليها في 3 سنين"),
    "inst_spec_crowd": ("Institutions", "المؤسسات: المضاربين لونج زحمة (COT ≥ 95%) - خروج", "exit", "الصناديق في أعلى لونج - خطر تصفية"),
    "flow_funding_neg": ("Order flow", "أوردر فلو: تمويل سالب على دعم (وقود طلوع)", "buy", "الشورت زحمة والسعر على دعم"),
    "flow_funding_hot": ("Order flow", "أوردر فلو: تمويل عالي جدًا - خروج جزئي", "exit", "اللونج زحمة - خطر تصفية لونج"),
    "flow_cvd_div": ("Order flow", "أوردر فلو: CVD طالع والسعر نازل (امتصاص)", "buy", "المشترين بيشتروا بالسوق والسعر مش بينزل أكتر"),
}


def _f(x):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    ax = abs(x)
    return f"{x:,.0f}" if ax >= 1000 else f"{x:,.2f}" if ax >= 1 else f"{x:.4f}"


def evidence() -> dict:
    try:
        return json.loads(EVIDENCE.read_text(encoding="utf8")).get("setups", {})
    except Exception:
        return {}


def ev_label(e: dict | None) -> str:
    if not e or not e.get("n"):
        return "لسه ماتقاسش"
    n = e["n"]
    if n < 30:
        return f"مش دليل (n {n})"
    t = e.get("t")   # ~90 setups are tested together: t >= 2 happens by luck a few times, so 'worked' needs t >= 3
    if t is not None and t >= 3:
        return f"اشتغل في الماضي (n {n}, t {t:+.1f})"
    if t is not None and t >= 2:
        return f"مشجع بس مش كفاية - اختبارات كتير (n {n}, t {t:+.1f})"
    if t is not None and t <= -3:
        return f"كان أسوأ من العادي (n {n}, t {t:+.1f})"
    return f"مفيش فرق واضح (n {n})"


def _mk(sid, tf, px, entry, stop, target, why, school=None, name=None, side=None):
    sch, nm, sd, _ = CATALOG.get(sid, (school, name, side, ""))
    return {"id": sid, "school": sch, "school_ar": SCHOOL_AR.get((sch or "").split(":")[0], sch), "name": name or nm, "side": side or sd, "tf": tf,
            "horizon": TF_H.get(tf, ""), "entry": entry, "stop": stop, "target": target, "why": why, "price": px}


# ---------------------------------------------------------------- 1. Radar detectors on spot timeframes
def radar(frames: dict, tfs=("1mo", "1w", "1d")) -> list[dict]:
    from modules import signals
    try:
        from modules.strategy_lab import SCHOOL
    except Exception:
        SCHOOL = {}
    out = []
    for tf in tfs:
        df = frames.get(tf)
        if df is None or len(df) < 60:
            continue
        px = float(df["close"].iloc[-1])
        sigs, _ = signals.detect_all(df.reset_index(drop=True))
        for s in sigs:
            sch = SCHOOL.get(s["key"]) or ("Elliott wave" if s["family"] == "Elliott" else s["family"])
            p = s.get("prices") or {}
            bull = s["direction"] == signals.BULL
            stop = next((p[k] for k in ("inv", "sl", "stop") if k in p), None)
            tgt = next((p[k] for k in ("t", "tp", "t1", "target") if k in p), None)
            z = s.get("zone")
            entry = (min(z), max(z)) if z else (px, px)
            if not bull:
                stop, tgt, entry = None, None, None
            try:
                from modules.arabic import signal_ar
                nm_ar, det_ar = signal_ar(s, True)
            except Exception:
                nm_ar, det_ar = s["name"], s.get("detail", s["name"])
            out.append(_mk(f"radar:{s['key']}", tf, px, entry, stop, tgt, str(det_ar)[:160], school=sch,
                           name=f"{SCHOOL_AR.get(sch.split(':')[0], sch)}: {nm_ar}" + ("" if bull else " (خروج)"), side="buy" if bull else "exit"))
    # harmonic patterns (bull PRZ = buy, bear PRZ = exit) on 1W / 1D
    try:
        from modules.harmonic import find_harmonics
        for tf in ("1w", "1d"):
            df = frames.get(tf)
            if df is None or len(df) < 60:
                continue
            px = float(df["close"].iloc[-1])
            for h in find_harmonics(df.reset_index(drop=True), vol=True):
                d = h["pts"][-1][1]
                bull = h["dir"] == "bull"
                x = h["pts"][0][1]
                out.append(_mk(f"harm:{h['name'].lower()}", tf, px, (d * 0.995, d * 1.005) if bull else None, (min(x, d) * 0.97 if bull else None),
                               (h["pts"][-2][1] if bull else None), f"{h['name']} {'صاعد' if bull else 'هابط'} - النقطة D عند {_f(d)}" + (" (لسه بيتكون)" if h.get("forming") else ""),
                               school="Harmonic", name=f"هارمونيك: {h['name']} {'صاعد' if bull else 'هابط (خروج)'}", side="buy" if bull else "exit"))
    except Exception:
        pass
    return out


# ---------------------------------------------------------------- 2. spot-only setups
def _ema(c, n):
    return pd.Series(c).ewm(span=n, adjust=False).mean().to_numpy()


def spot_only(b: dict, flow: dict | None = None, cot: dict | None = None) -> list[dict]:
    from modules import spot_ind as I
    R, st = b["reads"], b.get("stats", {})
    frames = b.get("frames") or {}
    out = []
    for tf in ("1w", "1d"):
        r = R.get(tf) or {}
        if not r.get("ok"):
            continue
        px, atr, c, h, l = r["px"], r["atr"] or r["px"] * 0.02, r["c"], r["h"], r["l"]
        n = len(c)
        dr = r.get("dr") or {}
        # Elliott positions from the zig-zag
        zz = (r.get("elliott") or {}).get("pivots") or []
        if len(zz) >= 3:
            a, bb, cc = zz[-3:]
            if a[2] == "L" and bb[2] == "H":            # wave 1 up then a pullback in progress / done
                w1 = bb[1] - a[1]
                ret = (bb[1] - min(px, cc[1] if cc[2] == "L" else px)) / w1 if w1 > 0 else 0
                if 0.45 <= ret <= 0.70 and px > a[1]:
                    out.append(_mk("ew_w2", tf, px, (bb[1] - 0.618 * w1, bb[1] - 0.5 * w1), a[1] - 0.2 * atr, bb[1] + 0.618 * w1,
                                   f"موجة 1 من {_f(a[1])} لـ {_f(bb[1])} والتصحيح {ret * 100:.0f}% فوق بدايتها"))
            if len(zz) >= 4:
                p0, p1, p2, p3 = zz[-4:]
                if p0[2] == "L" and p1[2] == "H" and p2[2] == "L" and p2[1] > p0[1] and px > p1[1] and c[-2] <= p1[1] * 1.01:
                    out.append(_mk("ew_w3_go", tf, px, (p1[1], px), p2[1] - 0.2 * atr, p2[1] + 1.618 * (p1[1] - p0[1]),
                                   f"كسر قمة الموجة 1 {_f(p1[1])} والموجة 2 مسكت عند {_f(p2[1])} - هدف 1.618 = {_f(p2[1] + 1.618 * (p1[1] - p0[1]))}"))
        ew = r.get("elliott") or {}
        if ew.get("kind") == "impulse_up":
            labs = ew["labels"]
            if len(labs) == 6:
                out.append(_mk("ew_w5_done", tf, px, None, None, None, f"5 موجات صاعدة اكتملت عند {_f(labs[5][1])} - التصحيح غالبًا جاي"))
            p3, p4 = labs[3][1], labs[4][1]
            if len(labs) >= 5 and labs[4][0] >= n - 6 and labs[1][1] < p4 and (labs[3][1] - p4) <= 0.5 * (labs[3][1] - labs[2][1]):
                out.append(_mk("ew_w4", tf, px, (p4, px), labs[1][1], p3 + (labs[1][1] - labs[0][1]), f"تصحيح الموجة 4 عند {_f(p4)} فوق قمة الموجة 1 {_f(labs[1][1])}"))
        # divergences (beyond the Radar's regular RSI / MACD line)
        piv = r.get("piv") or []
        lows = [(i, p) for i, p, k in piv if k == "L" and i >= n - 80]
        rsi = r["rsi"]
        if len(lows) >= 2:
            (i1, a1), (i2, a2) = lows[-2:]
            if a2 > a1 and rsi[i2] < rsi[i1] - 3 and r.get("trend") == "up" and i2 >= n - 8:
                out.append(_mk("div_hidden_bull", tf, px, (a2, px), a2 - 0.5 * atr, None, f"قاع أعلى {_f(a2)} و RSI أوطى ({rsi[i1]:.0f} → {rsi[i2]:.0f}) في ترند صاعد"))
            hist = r["hist"]
            if a2 < a1 and hist[i2] > hist[i1] and hist[i1] < 0 and i2 >= n - 8:
                out.append(_mk("div_macd_hist", tf, px, (a2, px), a2 - 0.5 * atr, None, f"قاع أوطى {_f(a2)} وهيستوجرام MACD قاعه أعلى"))
            e50 = _ema(c, 50)
            d1, d2 = (e50[i1] - a1) / e50[i1], (e50[i2] - a2) / e50[i2]
            if a2 < a1 and 0 < d2 < d1 * 0.7 and i2 >= n - 8:
                out.append(_mk("div_ma_dist", tf, px, (a2, px), a2 - 0.5 * atr, None, f"قاع أوطى بس البعد تحت EMA 50 قل من {d1 * 100:.1f}% لـ {d2 * 100:.1f}%"))
            df = frames.get(tf)
            if df is not None and "volume" in df and len(df) == n and df["volume"].sum() > 0:
                obv = np.cumsum(np.sign(np.diff(c, prepend=c[0])) * df["volume"].to_numpy(float))
                if a2 < a1 and obv[i2] > obv[i1] and i2 >= n - 8:
                    out.append(_mk("div_obv", tf, px, (a2, px), a2 - 0.5 * atr, None, f"قاع أوطى {_f(a2)} والـ OBV أعلى - تجميع"))
        if len(lows) >= 3:
            (j1, b1), (j2, b2), (j3, b3) = lows[-3:]
            if b3 < b2 < b1 and rsi[j3] > rsi[j2] > rsi[j1] and j3 >= n - 8:
                out.append(_mk("div_triple", tf, px, (b3, px), b3 - 0.5 * atr, None, f"3 قيعان أوطى ({_f(b1)} / {_f(b2)} / {_f(b3)}) والـ RSI كل مرة أعلى"))
        highs = [(i, p) for i, p, k in piv if k == "H" and i >= n - 80]
        if len(highs) >= 2 and dr.get("zone") == "premium":
            (i1, h1), (i2, h2) = highs[-2:]
            if h2 > h1 and rsi[i2] < rsi[i1] - 3 and i2 >= n - 8:
                out.append(_mk("div_bear_premium", tf, px, None, None, None, f"قمة أعلى {_f(h2)} والـ RSI أوطى والسعر في البريميوم {dr['pos'] * 100:.0f}%"))
        # Gann
        g = r.get("gann") or {}
        fit = g.get("fit") or {}
        near = [v for v in g.get("sq9", []) if abs(v / px - 1) < 0.012]
        if near and fit.get("bars_to_turn") is not None and fit["bars_to_turn"] <= 2:
            out.append(_mk("gann_sq9_time", tf, px, (near[0] - 0.3 * atr, near[0] + 0.3 * atr), near[0] - atr, None,
                           f"مستوى مربع التسعة {_f(near[0])} ونافذة زمنية خلال {fit['bars_to_turn']} شمعة (دورة {fit.get('tsp')})"))
        if n >= 100:
            hi, lo = float(h[-200:].max()), float(l[-200:].min())
            mid = (hi + lo) / 2
            if abs(px / mid - 1) < 0.015 and c[-1] > c[-2]:
                out.append(_mk("gann_50", tf, px, (mid - 0.3 * atr, mid + 0.3 * atr), mid - atr, hi, f"نص الرينج الكبير {_f(lo)}-{_f(hi)} = {_f(mid)} والشمعة الأخيرة قفلت طالعة"))
            i_lo = int(np.argmin(l[-200:])) + max(0, n - 200)
            bars = n - 1 - i_lo
            if bars >= 10:
                unit = float(np.mean(h[-50:] - l[-50:])) * 0.5   # 1x1 scale = half the average range per bar (Gann needs a scale; this one is stated)
                line = l[i_lo] + unit * bars
                if abs(l[-1] / line - 1) < 0.01 and c[-1] > line:
                    out.append(_mk("gann_1x1", tf, px, (line, px), line - atr, None, f"زاوية 1x1 من قاع {_f(l[i_lo])} قبل {bars} شمعة عند {_f(line)} ومسكت"))
            if tf == "1d" and "time" in (frames.get("1d") if frames.get("1d") is not None else {}):
                t = pd.to_datetime(frames["1d"]["time"]).to_numpy()
                for i_p in (int(np.argmin(l[-400:])) + max(0, n - 400), int(np.argmax(h[-400:])) + max(0, n - 400)):
                    days = (t[-1] - t[i_p]) / np.timedelta64(1, "D")
                    for k in (90, 180, 360):
                        if abs(days - k) <= 3:
                            out.append(_mk("gann_anniv", tf, px, (px - 0.5 * atr, px), px - 1.5 * atr, None, f"{k} يوم من {'القاع' if i_p == int(np.argmin(l[-400:])) + max(0, n - 400) else 'القمة'} الكبير - موعد جان"))
        # classic
        if tf == "1d" and n >= 210:
            s50, s200 = pd.Series(c).rolling(50).mean().to_numpy(), pd.Series(c).rolling(200).mean().to_numpy()
            if s50[-1] > s200[-1] and s50[-6] <= s200[-6]:
                out.append(_mk("cl_golden", tf, px, (s50[-1], px), s200[-1] - atr, None, f"المتوسط 50 ({_f(s50[-1])}) عدى فوق 200 ({_f(s200[-1])})"))
            if s50[-1] < s200[-1] and s50[-6] >= s200[-6]:
                out.append(_mk("cl_death", tf, px, None, None, None, f"المتوسط 50 نزل تحت 200 ({_f(s200[-1])})"))
        if tf == "1w":
            if n >= 60:
                s200w = pd.Series(c).rolling(min(200, n - 1)).mean().to_numpy()
                if c[-1] > s200w[-1] and c[-2] <= s200w[-2]:
                    out.append(_mk("cl_200w_reclaim", tf, px, (s200w[-1], px), s200w[-1] - atr, None, f"قفلة فوق متوسط {min(200, n - 1)} أسبوع {_f(s200w[-1])}"))
                if c[-1] < s200w[-1] and c[-2] >= s200w[-2]:
                    out.append(_mk("cl_200w_loss", tf, px, None, None, None, f"قفلة تحت متوسط {min(200, n - 1)} أسبوع {_f(s200w[-1])}"))
            if n >= 53 and c[-1] > h[-53:-1].max() and c[-2] <= h[-53:-1].max():
                lvl = float(h[-53:-1].max())
                out.append(_mk("cl_52w_break", tf, px, (lvl, px), lvl - 1.2 * atr, None, f"قفلة فوق قمة 52 أسبوع {_f(lvl)}"))
        bw = pd.Series(c).rolling(20).std().to_numpy() / pd.Series(c).rolling(20).mean().to_numpy()
        if n >= 140 and np.isfinite(bw[-2]) and bw[-2] <= np.nanpercentile(bw[-120:], 10):
            up = pd.Series(c).rolling(20).mean().to_numpy() + 2 * pd.Series(c).rolling(20).std().to_numpy()
            if c[-1] > up[-1]:
                out.append(_mk("cl_bb_squeeze", tf, px, (up[-2], px), float(pd.Series(c).rolling(20).mean().iloc[-1]), None, "البولينجر كان في أضيق 10% وقفلة فوق الحد العلوي"))
    # cycle value (spot), institutions, order flow
    px = b.get("price")
    if px:
        if st.get("mayer") is not None and st["mayer"] < 0.8:
            out.append(_mk("val_mayer", "1d", px, (px * 0.92, px), None, None, f"مضاعف ماير {st['mayer']:.2f} - تجميع على دفعات بكمية صغيرة"))
        if st.get("mayer") is not None and st["mayer"] > 2.4:
            out.append(_mk("val_hot", "1d", px, None, None, None, f"مضاعف ماير {st['mayer']:.2f} - اجني جزء"))
        if st.get("dist_200w") is not None and st["dist_200w"] < 0:
            out.append(_mk("val_200w", "1w", px, (px * 0.9, px), None, None, f"السعر {st['dist_200w']:+.0f}% عن متوسط 200 أسبوع"))
    if cot and cot.get("ok"):
        if cot["comm_idx"] >= 90:
            out.append(_mk("inst_comm_long", "1w", px, None, None, None, f"مؤشر COT للتجار {cot['comm_idx']:.0f}% ({cot['date']})"))
        if cot["spec_idx"] >= 95:
            out.append(_mk("inst_spec_crowd", "1w", px, None, None, None, f"مؤشر COT للمضاربين {cot['spec_idx']:.0f}% - زحمة"))
    if flow:
        dv, tk = flow.get("deriv") or {}, flow.get("taker") or {}
        d1 = R.get("1d") or {}
        if dv.get("ok") and dv.get("funding") is not None:
            if dv["funding"] < -0.01 and (d1.get("dr") or {}).get("zone") == "discount":
                out.append(_mk("flow_funding_neg", "4h", px, None, None, None, f"التمويل {dv['funding']:+.4f}% والسعر في الديسكاونت اليومي"))
            if dv["funding"] > 0.05:
                out.append(_mk("flow_funding_hot", "4h", px, None, None, None, f"التمويل {dv['funding']:+.4f}%"))
        h4 = R.get("4h") or {}
        if tk.get("ok") and tk["slope"] > 0 and h4.get("ok") and h4["c"][-1] < h4["c"][-7]:
            out.append(_mk("flow_cvd_div", "4h", px, None, None, None, "CVD 24 ساعة طالع والسعر نازل - امتصاص"))
    return out


def scan(b: dict, flow: dict | None = None, cot: dict | None = None) -> list[dict]:
    """All live setups for one market (Radar detectors + harmonic on 1M / 1W / 1D, then the spot-only setups), with evidence."""
    out = radar(b.get("frames") or {}) + spot_only(b, flow, cot)
    ev = evidence()
    seen = set()
    res = []
    for s in out:
        k = (s["id"], s["tf"])
        if k in seen:
            continue
        seen.add(k)
        e = ev.get(f"{s['id']}|{s['tf']}") or ev.get(s["id"])
        s["evidence"] = e
        s["ev_label"] = ev_label(e)
        res.append(s)
    order = {"1mo": 0, "1w": 1, "1d": 2, "4h": 3}
    return sorted(res, key=lambda s: (s["side"] != "buy", -((s.get("evidence") or {}).get("t") or 0), order.get(s["tf"], 9)))


def library() -> list[dict]:
    """Every setup the desk knows (for the library tab): Radar keys by school + the spot catalog, with evidence."""
    rows = []
    ev = evidence()
    try:
        from modules.strategy_lab import SCHOOL
    except Exception:
        SCHOOL = {}
    for k, sch in SCHOOL.items():
        e = {tf: ev.get(f"radar:{k}|{tf}") for tf in ("1mo", "1w", "1d")}
        rows.append({"id": f"radar:{k}", "school": SCHOOL_AR.get(sch.split(":")[0], sch), "name": k, "side": "buy + exit", "source": "الرادار",
                     "evidence": {tf: ev_label(x) for tf, x in e.items()}})
    for sid, (sch, nm, side, why) in CATALOG.items():
        e = {tf: ev.get(f"{sid}|{tf}") for tf in ("1mo", "1w", "1d", "4h")}
        rows.append({"id": sid, "school": SCHOOL_AR.get(sch, sch), "name": nm, "side": "شراء" if side == "buy" else "خروج", "source": "مكتب السبوت", "why": why,
                     "evidence": {tf: ev_label(x) for tf, x in e.items() if x} or {"-": "لسه ماتقاسش"}})
    return rows
