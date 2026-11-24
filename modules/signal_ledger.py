"""Signal ledger: EVERY strategy's trades in one place, each strategy kept apart, each trade replayed on the candles and explained
(owner 2026-11-24: "record each strategy on its own, see the scenario that was written, what the best chance was, was the entry early or
late, why it hit TP, why it hit SL, why it missed TP2 ... then conclude the best and recommend gradually").

Flow
  record(sig)           a strategy wrote a plan (server scanner, brain setup alerts, chart indicators via the journal bridge). Deduplicated.
  review(sig, bars)     replays the candles AFTER the signal: fill, every target / stop in time order, MFE / MAE, what happened after the exit,
                        the best entry and the best move that existed, and the same trade under other stop / target sizes. Pure.
  lessons -> text       "why" sentences built only from what the candles and the saved context show.
  grade_pending(fetch)  reviews the signals whose time has passed (fetch = market_cache.get_klines).
  stats() / advice()    per strategy (and strategy + detail, and timeframe): win rate, R per exit style, how often each target is reached,
                        early / late entries, stop hunts, profit left, the best stop / target size from the grid; then GRADUAL advice:
                        collecting (n < 10) -> lean (10-29, NOT evidence) -> evidence (n >= 30, after costs, lower bound > 0).

Honest rules (house rules): R is per unit of the plan's own risk; costs are taken off (COST_R per filled trade) in stats; a candle that touches
the stop and a target counts the stop (worst case); on the fill candle only the stop counts; nothing here changes a live strategy by itself:
advice is a suggestion for the lab / the owner. Times are UTC ms."""
from __future__ import annotations

import hashlib
import json
import math
import os
import threading
import time
from collections import defaultdict
from pathlib import Path

PATH = Path(os.environ.get("SIGNAL_LEDGER_PATH", "data/ledger/signals.json"))
KEEP = 6000                   # newest signals kept in the file
COST_R = 0.05                 # fees + slippage per filled trade, in R (same order as the lab's cost)
MIN_LEAN, MIN_N = 10, 30
TF_MS = {"1m": 60_000, "3m": 180_000, "5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000, "4h": 14_400_000,
         "6h": 21_600_000, "12h": 43_200_000, "1d": 86_400_000, "1w": 604_800_000, "1mo": 2_592_000_000}
FILL_BARS, HOLD_BARS, POST_BARS = 20, 120, 30   # wait for the entry / hold after the fill / look after the exit (bars of the signal's timeframe)
SL_GRID = (0.75, 1.0, 1.25, 1.5, 2.0)          # stop size as a multiple of the plan's stop distance
TP_GRID = (0.5, 1.0, 1.5, 2.0, 3.0)            # one target, in multiples of the plan's stop distance
_lock = threading.Lock()


def tf_ms(tf: str) -> int:
    return TF_MS.get(str(tf or "").lower().replace("min", "m"), 3_600_000)


# ---------------------------------------------------------------- store
def _load(path: Path | None = None) -> dict:
    p = path or PATH
    try:
        return json.loads(p.read_text(encoding="utf8")) if p.exists() else {}
    except Exception:
        return {}


def _save(data: dict, path: Path | None = None) -> None:
    p = path or PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    if len(data) > KEEP:
        data = dict(sorted(data.items(), key=lambda kv: kv[1].get("t0", 0))[-KEEP:])
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    os.replace(tmp, p)


def _f(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def normalize(sig: dict) -> dict | None:
    """A plan from any strategy -> the ledger shape, or None when it cannot be graded (no stop, stop on the wrong side ...)."""
    if not isinstance(sig, dict):
        return None
    d = str(sig.get("dir") or sig.get("direction") or sig.get("side") or "").lower()
    d = "long" if d in ("long", "bullish", "buy", "bull", "1") else "short" if d in ("short", "bearish", "sell", "bear", "-1") else ""
    entry, sl = _f(sig.get("entry")), _f(sig.get("sl", sig.get("stop")))
    tps = [x for x in (_f(v) for v in (sig.get("tps") or [sig.get(k) for k in ("tp1", "tp2", "tp3")])) if x is not None]
    sym, src, t0 = str(sig.get("symbol") or ""), str(sig.get("src") or ""), int(_f(sig.get("t0")) or 0)
    if not (d and sym and src and entry and sl and tps and t0 > 0):
        return None
    long_ = d == "long"
    if (long_ and not sl < entry) or (not long_ and not sl > entry):
        return None
    tps = sorted({t for t in tps if (t > entry if long_ else t < entry)}, reverse=not long_)[:3]
    if not tps:
        return None
    tf = str(sig.get("tf") or sig.get("tfk") or "1h")
    tf = tf if tf == "1M" else tf.lower()
    sub = str(sig.get("sub") or "")
    if tf == "1M":
        tf = "1mo"
    bucket = t0 // tf_ms(tf)   # the same plan re-sent on every scan pass of the same candle = one signal
    pk = "|".join([src, sub, sym, tf, d, f"{entry:.6g}", f"{sl:.6g}"])   # the plan itself (same entry + stop = same idea on later candles too)
    key = pk + "|" + str(bucket)
    return {"id": hashlib.sha1(key.encode()).hexdigest()[:16], "pk": pk, "src": src, "sub": sub, "symbol": sym, "tf": tf, "dir": d,
            "entry": entry, "sl": sl, "tps": tps, "t0": t0, "ctx": sig.get("ctx") if isinstance(sig.get("ctx"), dict) else {},
            "why": [str(x) for x in (sig.get("why") or sig.get("tags") or [])][:12], "score": _f(sig.get("score")), "max": _f(sig.get("max")),
            "status": "pending", "added": int(time.time() * 1000)}


def record(sig: dict, path: Path | None = None) -> str | None:
    """Add one plan. Returns its id (also when it was already there), None when it is not gradable."""
    return record_many([sig], path)[0]


def record_many(sigs: list, path: Path | None = None) -> list:
    out, recs = [], []
    for s in sigs or []:
        n = normalize(s)
        out.append(n["id"] if n else None)
        if n:
            recs.append(n)
    if not recs:
        return out
    with _lock:
        data = _load(path)
        last = {}   # plan key -> newest t0 already stored
        for v in data.values():
            if v.get("pk") and v.get("t0", 0) > last.get(v["pk"], 0):
                last[v["pk"]] = v["t0"]
        new = False
        for n in recs:
            if n["id"] in data:
                continue
            prev = last.get(n["pk"])
            if prev is not None and 0 <= n["t0"] - prev < FILL_BARS * tf_ms(n["tf"]):
                continue   # the same plan written again on a later candle while the first copy is still waiting / running: one idea, counted once
            data[n["id"]] = n
            last[n["pk"]] = n["t0"]
            new = True
        if new:
            _save(data, path)
    return out


def all_signals(path: Path | None = None) -> list:
    return sorted(_load(path).values(), key=lambda s: s.get("t0", 0), reverse=True)


# ---------------------------------------------------------------- replay (pure)
def _bars_from_df(df) -> list:
    """DataFrame (time, open, high, low, close) -> [(t_ms, o, h, l, c)] sorted."""
    if df is None or len(df) == 0:
        return []
    t = df["time"]
    if str(t.dtype).startswith("datetime64"):   # any resolution (pandas 2 may keep ms): convert through ns explicitly
        import pandas as pd
        ms = (pd.to_datetime(t).dt.tz_localize(None).astype("datetime64[ns]").astype("int64") // 1_000_000).tolist() if getattr(t.dt, "tz", None) else \
             (t.astype("datetime64[ns]").astype("int64") // 1_000_000).tolist()
    else:
        ms = [int(x) for x in t]
    return sorted(zip(ms, df["open"].astype(float), df["high"].astype(float), df["low"].astype(float), df["close"].astype(float)))


def _sim_one(bars, f, long_, entry, stop, target, hold):
    """One target, one stop, from fill bar f (stop only on the fill bar). -> R in units of this stop (win = reward/risk, loss = -1, time exit = mark)."""
    risk = abs(entry - stop)
    for k in range(f, min(len(bars), f + hold)):
        _, _, h, l, c = bars[k]
        if (l <= stop) if long_ else (h >= stop):
            return -1.0
        if k > f and ((h >= target) if long_ else (l <= target)):
            return abs(target - entry) / risk
    last = bars[min(len(bars), f + hold) - 1][4]
    return ((last - entry) if long_ else (entry - last)) / risk


def review(sig: dict, bars: list, tfms: int | None = None, now_ms: int | None = None) -> dict | None:
    """Replay a signal on bars [(t, o, h, l, c)]. None = not enough candles yet (the signal stays pending).

    The returned dict (all prices raw, all moves in R of the plan's stop distance):
      outcome: no_fill | ran_away | sl | tp1 | tp2 | tp3 | time | open
      r: {split, tp1_all, last_all}   split = equal parts at each target, stop to entry after TP1
      fill_t, bars_to_fill, exit_t, bars_held, hits {tp1: t, ...}, sl_t
      mfe_r, mae_r, mae_before_tp1_r, peak_t, pre_fill_better_r, after_exit {to_tp1, beyond_sl_r, extra_r}
      best {entry, t, move_r}, grid {"m|k": R}, lessons [{code, ...}]"""
    tfms = tfms or tf_ms(sig.get("tf"))
    long_, entry, sl, tps = sig["dir"] == "long", float(sig["entry"]), float(sig["sl"]), list(sig["tps"])
    R = abs(entry - sl)
    if R <= 0:
        return None
    fav = (lambda p: (p - entry) / R) if long_ else (lambda p: (entry - p) / R)
    after = [b for b in bars if b[0] >= sig["t0"]]
    if not after:
        return None
    now_ms = now_ms or int(time.time() * 1000)
    # ---- 1) fill
    f, ran = None, False
    for k, (t, o, h, l, c) in enumerate(after[:FILL_BARS]):
        if l <= entry <= h:
            f = k
            break
        if (h >= tps[0]) if long_ else (l <= tps[0]):
            ran = True
    lessons = []
    if f is None:
        if len(after) < FILL_BARS and now_ms < sig["t0"] + FILL_BARS * tfms:
            return None   # still inside its fill window
        lessons.append({"code": "ran_away"} if ran else {"code": "no_fill"})
        mv = max((fav(b[2] if long_ else b[3]) for b in after[:FILL_BARS]), default=0.0)
        return {"outcome": "ran_away" if ran else "no_fill", "filled": False, "r": {}, "move_without_us_r": round(mv, 2), "lessons": lessons,
                "graded": now_ms}
    fill_t = after[f][0]
    # candles BEFORE the fill candle: was price already better than the entry? (a breakout / late entry paid for the move)
    pre_fill_better = max(0.0, max(((entry - b[3]) if long_ else (b[2] - entry)) / R for b in after[:f])) if f else 0.0
    # ---- 2) walk after the fill
    trade = after[f:]
    end = min(len(trade), HOLD_BARS)
    hits, sl_t, mfe, mae, peak_t, mae_pre_tp1, be_after = {}, None, 0.0, 0.0, fill_t, 0.0, False
    done_k = None
    for k in range(end):
        t, o, h, l, c = trade[k]
        best, worst = fav(h if long_ else l), fav(l if long_ else h)
        stop_now = entry if be_after else sl
        if (l <= stop_now) if long_ else (h >= stop_now):   # stop first (worst case), on the fill bar only the stop counts
            mae = max(mae, -worst) if not be_after else mae
            if "tp1" not in hits:
                mae_pre_tp1 = max(mae_pre_tp1, -worst)
            sl_t = t
            done_k = k
            break
        mae = max(mae, -worst)
        if "tp1" not in hits:
            mae_pre_tp1 = max(mae_pre_tp1, -worst)
        if best > mfe:
            mfe, peak_t = best, t
        if k > 0:
            for j, tp in enumerate(tps):
                lv = "tp%d" % (j + 1)
                if lv not in hits and ((h >= tp) if long_ else (l <= tp)):
                    hits[lv] = t
            if "tp1" in hits:
                be_after = True
            if len(hits) == len(tps):
                done_k = k
                break
    if done_k is None and end < HOLD_BARS and now_ms < fill_t + HOLD_BARS * tfms:
        return None   # still running inside its holding time: grade later
    exit_k = done_k if done_k is not None else end - 1
    if len(trade) - exit_k - 1 < POST_BARS and now_ms < trade[exit_k][0] + (POST_BARS + 1) * tfms:
        return None   # the look-after window (stop hunt? profit left?) is not complete yet
    exit_t, exit_px = trade[exit_k][0], trade[exit_k][4]
    rr = [fav(tp) for tp in tps]
    # ---- 3) R under three exit styles
    n = len(tps)
    split = 0.0
    for j in range(n):
        lv = "tp%d" % (j + 1)
        if lv in hits:
            split += rr[j] / n
        elif sl_t is not None:
            split += (0.0 if "tp1" in hits else -1.0) / n
        else:
            split += fav(exit_px) / n
    tp1_all = rr[0] if "tp1" in hits else (-1.0 if sl_t is not None else fav(exit_px))
    last_lv = "tp%d" % n
    last_all = rr[-1] if last_lv in hits else (-1.0 if sl_t is not None and "tp1" not in hits else (0.0 if sl_t is not None else fav(exit_px)))
    if sl_t is not None and "tp1" not in hits:
        outcome = "sl"
    elif hits:
        outcome = max(hits, key=lambda x: int(x[2:]))
    else:
        outcome = "time"
    # ---- 4) after the exit: did the idea work anyway, how much was left
    post = trade[exit_k + 1: exit_k + 1 + POST_BARS]
    to_tp1, beyond_sl, extra = False, 0.0, 0.0
    if outcome == "sl":
        worst_after = mae_pre_tp1
        for (t, o, h, l, c) in post:
            worst_after = max(worst_after, -fav(l if long_ else h))
            if (h >= tps[0]) if long_ else (l <= tps[0]):
                to_tp1 = True
                break
        beyond_sl = max(0.0, worst_after - 1.0)
    if outcome.startswith("tp") or outcome == "time":
        far = max((fav(b[2] if long_ else b[3]) for b in post), default=mfe)
        extra = max(0.0, far - max(rr[int(outcome[2:]) - 1] if outcome.startswith("tp") else fav(exit_px), 0.0))
    # ---- 5) best entry / best move that existed with this stop size (from the signal to the end of the look-after window)
    win = after[: f + exit_k + 1 + POST_BARS + 1]
    best_move, best_entry, best_t = 0.0, entry, sig["t0"]
    lo_px, lo_t = None, None
    for (t, o, h, l, c) in win:
        px_in = l if long_ else h
        if lo_px is None or ((px_in < lo_px) if long_ else (px_in > lo_px)):
            lo_px, lo_t = px_in, t
        mv = ((h - lo_px) if long_ else (lo_px - l)) / R
        if mv > best_move:
            best_move, best_entry, best_t = mv, lo_px, lo_t
    # ---- 6) the same trade with other stop / target sizes
    grid = {}
    for m in SL_GRID:
        st_ = entry - m * R if long_ else entry + m * R
        for kk in TP_GRID:
            tg = entry + kk * R if long_ else entry - kk * R
            grid["%g|%g" % (m, kk)] = round(_sim_one(trade, 0, long_, entry, st_, tg, HOLD_BARS), 3)
    # ---- 7) lessons (only from what was measured)
    if pre_fill_better >= 0.25:
        lessons.append({"code": "late_entry", "better_r": round(pre_fill_better, 2)})
    if mae_pre_tp1 >= 0.6 and outcome != "sl":
        lessons.append({"code": "early_entry", "mae_r": round(mae_pre_tp1, 2)})
    if outcome == "sl":
        if to_tp1:
            lessons.append({"code": "stop_hunt", "need_r": round(1.0 + beyond_sl + 0.05, 2)})
        elif mfe >= 0.8 * (rr[0] if rr else 1):
            lessons.append({"code": "near_tp1_then_sl", "peak_r": round(mfe, 2), "tp1_r": round(rr[0], 2)})
        elif mfe < 0.3:
            lessons.append({"code": "wrong_side", "mfe_r": round(mfe, 2)})
        else:
            lessons.append({"code": "reversed", "peak_r": round(mfe, 2)})
    if "tp1" in hits:
        k1 = next(k for k, b in enumerate(trade) if b[0] == hits["tp1"])
        lessons.append({"code": "tp1_fast" if k1 <= 3 else "tp1_slow", "bars": k1})
    for j in range(1, n):
        lv = "tp%d" % (j + 1)
        if "tp1" in hits and lv not in hits:
            lessons.append({"code": "missed_tp", "level": lv, "peak_r": round(mfe, 2), "need_r": round(rr[j], 2),
                            "pct": int(round(100 * max(0.0, mfe) / rr[j])) if rr[j] > 0 else 0,
                            "then": "be_stop" if sl_t is not None else "time"})
            break
    if extra >= 1.0:
        lessons.append({"code": "left_on_table", "extra_r": round(extra, 2)})
    if outcome == "time":
        lessons.append({"code": "time_exit", "bars": exit_k})
    best_cell = max(grid.items(), key=lambda kv: kv[1]) if grid else None
    return {"outcome": outcome, "filled": True, "fill_t": fill_t, "bars_to_fill": f, "exit_t": exit_t, "bars_held": exit_k,
            "hits": hits, "sl_t": sl_t, "rr": [round(x, 3) for x in rr],
            "r": {"split": round(split, 3), "tp1_all": round(tp1_all, 3), "last_all": round(last_all, 3)},
            "mfe_r": round(mfe, 3), "mae_r": round(mae, 3), "mae_before_tp1_r": round(mae_pre_tp1, 3), "peak_t": peak_t,
            "pre_fill_better_r": round(pre_fill_better, 3),
            "after_exit": {"to_tp1": to_tp1, "beyond_sl_r": round(beyond_sl, 3), "extra_r": round(extra, 3)},
            "best": {"entry": best_entry, "t": best_t, "move_r": round(best_move, 2)},
            "grid": grid, "best_cell": best_cell[0] if best_cell else None, "lessons": lessons, "graded": now_ms}


# ---------------------------------------------------------------- words
_TXT = {
    "no_fill": ("Never filled: price did not come back to the entry within %d candles." % FILL_BARS,
                "ما اتنفذتش: السعر مارجعش للدخول خلال %d شمعة." % FILL_BARS),
    "ran_away": ("Missed: price reached TP1 WITHOUT touching the entry - the idea was right, the entry was too far.",
                 "فاتتنا: السعر وصل TP1 من غير ما يلمس الدخول - الفكرة صح والدخول كان بعيد."),
    "late_entry": ("Late entry: before the fill price was {better_r}R better than the entry (a breakout entry paid the move).",
                   "دخول متأخر: قبل التنفيذ السعر كان أحسن من الدخول بـ {better_r}R (الدخول بعد الكسر دفع تمن الحركة)."),
    "early_entry": ("Early entry: price went {mae_r}R against us before it worked - a confirmation close would have given a better price.",
                    "دخول بدري: السعر راح ضدنا {mae_r}R قبل ما يشتغل - إغلاق تأكيد كان هيدي سعر أحسن."),
    "stop_hunt": ("Stop hunt: the stop was hit, then price went to TP1 anyway. A stop of about {need_r}R would have survived.",
                  "صيد ستوب: ضرب الستوب وبعدين السعر راح TP1 برضه. ستوب حوالي {need_r}R كان هيستحمل."),
    "near_tp1_then_sl": ("Came to {peak_r}R (TP1 is {tp1_r}R) and turned to the stop: a closer TP1 or a break-even rule would have saved it.",
                         "وصل {peak_r}R (TP1 عند {tp1_r}R) ورجع للستوب: TP1 أقرب أو نقل الستوب للدخول كان هينقذها."),
    "wrong_side": ("Wrong side: price never moved more than {mfe_r}R our way before the stop.",
                   "الاتجاه غلط: السعر ماتحركش في صالحنا أكتر من {mfe_r}R قبل الستوب."),
    "reversed": ("Worked to {peak_r}R, then reversed to the stop.", "اشتغلت لحد {peak_r}R وبعدين رجعت للستوب."),
    "tp1_fast": ("TP1 in {bars} candles: momentum was with the trade.", "TP1 في {bars} شمعة: الزخم كان معانا."),
    "tp1_slow": ("TP1 after {bars} candles: slow follow-through.", "TP1 بعد {bars} شمعة: متابعة بطيئة."),
    "missed_tp": ("{level} missed: the best price was {peak_r}R, {pct}% of the {need_r}R needed; then it {then_en}.",
                  "{level} مااتضربش: أحسن سعر كان {peak_r}R، يعني {pct}% من {need_r}R المطلوبة؛ وبعدين {then_ar}."),
    "left_on_table": ("Profit left: price went {extra_r}R further after the last exit - a trailing runner would have kept more.",
                      "ربح اتساب: السعر كمّل {extra_r}R بعد آخر خروج - ترك جزء بستوب متحرك كان هيكسب أكتر."),
    "time_exit": ("No target and no stop in {bars} candles: closed on time.", "لا هدف ولا ستوب في {bars} شمعة: اتقفلت بالوقت."),
}


def lesson_text(ls: dict, ar: bool = False) -> str:
    t = _TXT.get(ls.get("code"))
    if not t:
        return str(ls.get("code"))
    v = dict(ls)
    v["then_en"] = "came back to the break-even stop" if ls.get("then") == "be_stop" else "ran out of time"
    v["then_ar"] = "رجع لستوب الدخول" if ls.get("then") == "be_stop" else "الوقت خلص"
    try:
        return t[1 if ar else 0].format(**v)
    except Exception:
        return t[1 if ar else 0]


def context_notes(sig: dict, ar: bool = False) -> list:
    """What the saved context at entry said (with / against): read only, never invented."""
    c = sig.get("ctx") or {}
    out = []
    if c.get("htf") in ("with", "against"):
        out.append(("bigger timeframes were %s the trade" % c["htf"], "الفريمات الأكبر كانت %s الصفقة" % ("مع" if c["htf"] == "with" else "ضد")))
    if c.get("of") in ("with", "against"):
        out.append(("order flow was %s the trade at entry" % c["of"], "الأوردر فلو كان %s الصفقة وقت الدخول" % ("مع" if c["of"] == "with" else "ضد")))
    if c.get("delta_pct") is not None:
        out.append(("last candle buy share %s%% (%s)" % (c["delta_pct"], "real trades" if c.get("of_real") else "estimate"),
                    "نسبة الشراء في آخر شمعة %s%% (%s)" % (c["delta_pct"], "صفقات حقيقية" if c.get("of_real") else "تقدير")))
    if c.get("regime"):
        out.append(("market regime: %s" % c["regime"], "حالة السوق: %s" % c["regime"]))
    if c.get("news"):
        out.append(("news was active", "كان في أخبار"))
    return [x[1 if ar else 0] for x in out]


# ---------------------------------------------------------------- grading
def grade_pending(fetch, path: Path | None = None, limit: int = 40, now_ms: int | None = None, bars_needed: int = 300) -> int:
    """Review pending signals whose time has come. fetch(symbol, tf, n) -> DataFrame. Returns how many were graded.
    One candle request per (symbol, tf). A failed fetch leaves the signals pending (tried again later)."""
    now_ms = now_ms or int(time.time() * 1000)
    with _lock:
        data = _load(path)
    todo = [s for s in data.values() if s.get("status") == "pending" and now_ms >= s["t0"] + 2 * tf_ms(s["tf"])]
    todo.sort(key=lambda s: s["t0"])
    todo = todo[:limit]
    if not todo:
        return 0
    cache, done = {}, {}
    for s in todo:
        key = (s["symbol"], s["tf"])
        if key not in cache:
            try:
                cache[key] = _bars_from_df(fetch(s["symbol"], s["tf"], bars_needed))
            except Exception:
                cache[key] = None
        bars = cache[key]
        if not bars:
            continue
        if bars[0][0] > s["t0"]:   # the candles no longer reach back to the signal: cannot be replayed honestly
            done[s["id"]] = {"status": "lost", "review": {"outcome": "no_data"}}
            continue
        rv = review(s, bars, tf_ms(s["tf"]), now_ms)
        if rv is not None:
            done[s["id"]] = {"status": "graded", "review": rv}
    if done:
        with _lock:
            data = _load(path)
            for k, v in done.items():
                if k in data:
                    data[k].update(v)
            _save(data, path)
    return sum(1 for v in done.values() if v["status"] == "graded")


# ---------------------------------------------------------------- stats + advice
STYLES = ("split", "tp1_all", "last_all")


def _row(sigs: list) -> dict:
    g = [s for s in sigs if s.get("status") == "graded"]
    filled = [s for s in g if s["review"].get("filled")]
    n = len(filled)
    row = {"signals": len(g), "n": n, "no_fill_pct": round(100 * (len(g) - n) / len(g), 1) if g else None,
           "ran_away": sum(1 for s in g if s["review"].get("outcome") == "ran_away")}
    if not n:
        row["level"] = "collecting"
        return row
    for st in STYLES:
        rs = [s["review"]["r"][st] - COST_R for s in filled]
        avg = sum(rs) / n
        sd = (sum((x - avg) ** 2 for x in rs) / (n - 1)) ** .5 if n > 1 else 0.0
        row[st] = {"avg_r": round(avg, 3), "win_pct": round(100 * sum(1 for x in rs if x > 0) / n, 1), "lb": round(avg - sd / math.sqrt(n), 3) if n > 1 else None}
    best = max(STYLES, key=lambda st: row[st]["avg_r"])
    row["best_style"] = best
    row["reach"] = {lv: round(100 * sum(1 for s in filled if lv in s["review"].get("hits", {})) / n, 1) for lv in ("tp1", "tp2", "tp3")}
    row["sl_pct"] = round(100 * sum(1 for s in filled if s["review"]["outcome"] == "sl") / n, 1)
    codes = defaultdict(int)
    for s in filled:
        for ls in s["review"].get("lessons", []):
            codes[ls["code"]] += 1
    row["lessons"] = {k: round(100 * v / n, 1) for k, v in codes.items()}
    row["mfe_avg"] = round(sum(s["review"]["mfe_r"] for s in filled) / n, 2)
    row["mae_avg"] = round(sum(s["review"]["mae_before_tp1_r"] for s in filled) / n, 2)
    cells = defaultdict(list)
    for s in filled:
        for k, v in (s["review"].get("grid") or {}).items():
            cells[k].append(v - COST_R)
    if cells:
        bk, bv = max(((k, sum(v) / len(v)) for k, v in cells.items()), key=lambda kv: kv[1])
        base = cells.get("1|1") or [0.0]
        row["best_cell"] = {"cell": bk, "avg_r": round(bv, 3), "plan_cell_avg_r": round(sum(base) / len(base), 3)}
    lb = row[best]["lb"]
    row["level"] = ("evidence" if n >= MIN_N and lb is not None and lb > 0 else "evidence_weak" if n >= MIN_N else
                    "lean" if n >= MIN_LEAN else "collecting")
    return row


def stats(path: Path | None = None, by: str = "src", sigs: list | None = None) -> dict:
    """{group: row}. by = "src" | "src_sub" | "src_tf" | "symbol"."""
    sigs = all_signals(path) if sigs is None else sigs
    groups = defaultdict(list)
    for s in sigs:
        if by == "why":   # one signal counts for every detector / reason it listed (scanner keys): which ingredient carries the strategy
            for w in s.get("why") or ["-"]:
                groups[s["src"] + " · " + w].append(s)
            continue
        k = s["src"] if by == "src" else (s["src"] + " · " + (s.get("sub") or "-")) if by == "src_sub" else \
            (s["src"] + " · " + s["tf"]) if by == "src_tf" else s["symbol"]
        groups[k].append(s)
    return {k: _row(v) for k, v in groups.items()}


def advice(row: dict, ar: bool = False) -> list:
    """Gradual suggestions for one strategy row. Never an order: a suggestion with its sample size and level."""
    n, L = row.get("n", 0), row.get("lessons", {})
    out = []
    if not n:
        if row.get("signals", 0) >= 5 and (row.get("no_fill_pct") or 0) >= 60:
            out.append(("Most plans never fill: the entry is too far from price.", "أغلب الخطط مابتتنفذش: الدخول بعيد عن السعر."))
        return [x[1 if ar else 0] for x in out] or [("Collecting: no filled trade yet.", "بنجمّع: لسه مفيش صفقة اتنفذت.")[1 if ar else 0]]
    tag = {"collecting": ("watch only", "مراقبة بس"), "lean": ("lean, NOT evidence", "ميل، مش دليل"), "evidence": ("evidence, after costs", "دليل بعد التكاليف"),
           "evidence_weak": ("enough trades, edge not proven", "صفقات كفاية، الميزة مش مثبتة")}[row["level"]][1 if ar else 0]
    pre = "[n=%d · %s] " % (n, tag)
    best = row.get("best_style")
    names = {"split": ("thirds at each target + stop to entry after TP1", "تلت عند كل هدف + الستوب للدخول بعد TP1"),
             "tp1_all": ("everything at TP1", "كله عند TP1"), "last_all": ("everything at the last target", "كله عند آخر هدف")}
    if best and best != "split" and row[best]["avg_r"] - row["split"]["avg_r"] >= 0.1:
        out.append(("Exit style: '%s' did best (%.2fR vs %.2fR per trade)." % (names[best][0], row[best]["avg_r"], row["split"]["avg_r"]),
                    "طريقة الخروج: '%s' كانت الأحسن (%.2fR مقابل %.2fR للصفقة)." % (names[best][1], row[best]["avg_r"], row["split"]["avg_r"])))
    if L.get("stop_hunt", 0) >= 25:
        out.append(("Stops too tight: %.0f%% of trades hit the stop and then reached TP1." % L["stop_hunt"],
                    "الستوب ضيق: %.0f%% من الصفقات ضربت الستوب وبعدين وصلت TP1." % L["stop_hunt"]))
    if L.get("early_entry", 0) >= 35:
        out.append(("Entries early: %.0f%% went 0.6R+ against first (avg %.2fR) - wait for a confirming close." % (L["early_entry"], row.get("mae_avg", 0)),
                    "الدخول بدري: %.0f%% راحت ضدنا 0.6R أو أكتر الأول (متوسط %.2fR) - استنى إغلاق تأكيد." % (L["early_entry"], row.get("mae_avg", 0))))
    if L.get("late_entry", 0) >= 35:
        out.append(("Entries late: %.0f%% had a better price before the fill - use a limit at the pullback." % L["late_entry"],
                    "الدخول متأخر: %.0f%% كان فيها سعر أحسن قبل التنفيذ - استخدم ليمت عند الارتداد." % L["late_entry"]))
    rc = row.get("reach", {})
    if rc.get("tp1", 0) >= 50 and rc.get("tp2", 100) < 30:
        out.append(("TP1 is reached %.0f%%, TP2 only %.0f%%: TP2 / TP3 are too far for this strategy." % (rc["tp1"], rc["tp2"]),
                    "TP1 بيتضرب %.0f%%، وTP2 بس %.0f%%: TP2 / TP3 بعاد على الاستراتيجية دي." % (rc["tp1"], rc["tp2"])))
    if L.get("left_on_table", 0) >= 30:
        out.append(("Price often ran 1R+ past the last exit (%.0f%%): trail the runner." % L["left_on_table"],
                    "السعر كتير بيكمّل 1R+ بعد آخر خروج (%.0f%%): سيب جزء بستوب متحرك." % L["left_on_table"]))
    if L.get("wrong_side", 0) >= 35:
        out.append(("%.0f%% never moved our way: the direction filter is the weak part, not the stop." % L["wrong_side"],
                    "%.0f%% ماتحركتش في صالحنا خالص: فلتر الاتجاه هو الضعيف، مش الستوب." % L["wrong_side"]))
    bc = row.get("best_cell")
    if bc and bc["cell"] != "1|1" and bc["avg_r"] - bc["plan_cell_avg_r"] >= 0.1:
        m, k = bc["cell"].split("|")
        out.append(("Grid: stop %s× and one target at %sR did best (%.2fR vs %.2fR with stop 1× / target 1R). Test it in the lab before using it." % (m, k, bc["avg_r"], bc["plan_cell_avg_r"]),
                    "الشبكة: ستوب %s× وهدف واحد عند %sR كان الأحسن (%.2fR مقابل %.2fR بستوب 1× وهدف 1R). جرّبه في المعمل قبل ما تستخدمه." % (m, k, bc["avg_r"], bc["plan_cell_avg_r"])))
    b = row[best]
    if row["level"] == "evidence":
        out.append(("RECOMMENDED: positive after costs with n >= %d (%.2fR per trade, lower bound %.2fR)." % (MIN_N, b["avg_r"], b["lb"]),
                    "مرشّحة: موجبة بعد التكاليف وn >= %d (%.2fR للصفقة، الحد الأدنى %.2fR)." % (MIN_N, b["avg_r"], b["lb"])))
    elif row["level"] in ("lean", "evidence_weak") and b["avg_r"] < 0:
        out.append(("Losing so far (%.2fR per trade after costs): do not trade it live." % b["avg_r"], "خسرانة لحد دلوقتي (%.2fR للصفقة بعد التكاليف): ماتتداولهاش حي." % b["avg_r"]))
    if not out:
        out.append(("Nothing stands out yet.", "لسه مفيش حاجة واضحة."))
    return [pre + x[1 if ar else 0] for x in out]


def ranking(path: Path | None = None, sigs: list | None = None) -> list:
    """Strategies ranked for recommendation: evidence first, then by the lower bound of the best exit style (conservative)."""
    st = stats(path, "src", sigs)
    order = {"evidence": 0, "evidence_weak": 1, "lean": 2, "collecting": 3}
    rows = [(k, v) for k, v in st.items()]
    rows.sort(key=lambda kv: (order[kv[1]["level"]], -((kv[1].get(kv[1].get("best_style") or "split") or {}).get("lb") or -9)))
    return rows


def brain_lines(path: Path | None = None, top: int = 5, ar: bool = False) -> list:
    """Short lines for the brain's daily review: the strategies with enough trades, best first, each with its first advice. [] when nothing is graded."""
    out = []
    for k, r in ranking(path):
        if not r.get("n"):
            continue
        b = r.get(r.get("best_style") or "split") or {}
        adv = advice(r, ar)
        out.append("ledger %s: n=%d, %.2fR/trade (%s), win %.0f%% - %s" % (k, r["n"], b.get("avg_r", 0), r["level"], b.get("win_pct", 0), adv[0] if adv else ""))
        if len(out) >= top:
            break
    return out
