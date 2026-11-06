"""Backtest of the Spot analyzer score (owner 2026-11-06: 'let it run on its own, tell me when results appear').

Question: does a high weekly + monthly confluence score (modules/spot_ind.confluence, the same code the Analyzer shows) come
before better 4- and 12-week returns than a low score, for a spot buyer?
Method (walk-forward, no look-ahead):
  * weekly candles (OKX spot for crypto, Yahoo futures for metals) + monthly candles;
  * at each week i: the weekly frame up to i and only the months that had CLOSED by the end of week i;
  * score = confluence of 1W + 1M (1D / 4H are not available far enough back in one request - said in the report);
  * forward return from the close of week i to week i+4 and i+12.
Report: buckets by score, n, mean return, share of positive weeks, vs all weeks; Welch t of (score >= 35) vs the rest;
also on NON-overlapping samples (every 4th / 12th week), because overlapping windows inflate n.
Under 30 non-overlapping samples = not evidence. Run: python scripts/spot_backtest.py  (needs network)"""
from __future__ import annotations

import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd

from modules import spot_ind as I

CRYPTO = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK", "DOT", "LTC", "TRX", "BCH", "ATOM", "XLM", "ETC", "UNI", "NEAR"]
METALS = {"GOLD": "Y:GC=F", "SILVER": "Y:SI=F", "COPPER": "Y:HG=F", "PLATINUM": "Y:PL=F"}
BUCKETS = [(-101, -35, "<= -35"), (-35, -10, "-35..-10"), (-10, 10, "-10..10"), (10, 35, "10..35"), (35, 101, ">= 35")]
WARM = 60   # weekly bars before the first score


def closed_months(m: pd.DataFrame, week_close: pd.Timestamp) -> pd.DataFrame:
    end = pd.to_datetime(m["time"]) + pd.offsets.MonthBegin(1)
    return m[end <= week_close].reset_index(drop=True)


def walk(w: pd.DataFrame, m: pd.DataFrame) -> list[dict]:
    w = w.reset_index(drop=True)
    c = w["close"].to_numpy(float)
    out = []
    for i in range(WARM, len(w) - 4):
        wc = pd.to_datetime(w["time"].iloc[i]) + pd.Timedelta(days=7)
        mt = closed_months(m, wc)
        reads = {"1w": I.analyse(w.iloc[max(0, i - 299):i + 1])}
        if len(mt) >= 30:
            reads["1mo"] = I.analyse(mt.tail(300))
        sc = I.confluence(reads)["score"]
        out.append({"i": i, "t": str(w["time"].iloc[i])[:10], "score": sc, "has_m": "1mo" in reads,
                    "r4": c[i + 4] / c[i] - 1, "r12": (c[i + 12] / c[i] - 1) if i + 12 < len(c) else None})
    return out


def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return None
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return float((a.mean() - b.mean()) / se) if se else None


def summarise(rows: list[dict], key: str, step: int) -> dict:
    """Bucket table for one horizon; step > 1 keeps every step-th week per symbol (non-overlapping)."""
    rr = [r for r in rows if r.get(key) is not None and (step == 1 or r["i"] % step == 0)]
    allv = [r[key] for r in rr]
    tab = []
    for lo, hi, lab in BUCKETS:
        v = [r[key] for r in rr if lo < r["score"] <= hi]
        tab.append({"bucket": lab, "n": len(v), "mean_pct": float(np.mean(v)) * 100 if v else None,
                    "pos_pct": float(np.mean([x > 0 for x in v])) * 100 if v else None})
    top = [r[key] for r in rr if r["score"] >= 35]
    rest = [r[key] for r in rr if r["score"] < 35]
    return {"horizon": key, "step": step, "n": len(allv), "all_mean_pct": float(np.mean(allv)) * 100 if allv else None,
            "all_pos_pct": float(np.mean([x > 0 for x in allv])) * 100 if allv else None, "buckets": tab,
            "t_top_vs_rest": welch(top, rest), "n_top": len(top)}


def fmt(res: dict) -> str:
    lines = ["# Spot analyzer score - backtest", "",
             f"Run {res['when']} UTC. Symbols: {', '.join(res['symbols_ok'])}" + (f". Missing: {', '.join(res['symbols_failed'])}" if res["symbols_failed"] else ""),
             "Score = 1W + 1M confluence (1D / 4H not included in this test). Returns from the weekly close, spot long only, no costs.", ""]
    for grp, sums in res["groups"].items():
        lines.append(f"## {grp}")
        for s in sums:
            ov = "overlapping weeks" if s["step"] == 1 else f"non-overlapping (every {s['step']} weeks)"
            lines.append(f"### {s['horizon']} - {ov}: n {s['n']}, all weeks mean {s['all_mean_pct']:+.2f}% , positive {s['all_pos_pct']:.0f}%" if s["n"] else f"### {s['horizon']}: no data")
            lines.append("| score | n | mean return | positive |")
            lines.append("|---|---|---|---|")
            for b in s["buckets"]:
                lines.append(f"| {b['bucket']} | {b['n']} | " + (f"{b['mean_pct']:+.2f}%" if b["mean_pct"] is not None else "—") + " | " +
                             (f"{b['pos_pct']:.0f}%" if b["pos_pct"] is not None else "—") + " |")
            t = s["t_top_vs_rest"]
            verdict = ("not evidence (n of the top bucket < 30)" if s["n_top"] < 30 else
                       "score >= 35 did better (t >= 2)" if t is not None and t >= 2 else
                       "score >= 35 did worse (t <= -2)" if t is not None and t <= -2 else "no clear difference (|t| < 2)")
            lines.append(f"Top bucket vs rest: t = {t:+.2f} -> {verdict}" if t is not None else f"Top bucket vs rest: {verdict}")
            lines.append("")
    lines.append("Overlapping rows share the same future weeks, so their n overstates the evidence; read the non-overlapping tables first.")
    return "\n".join(lines)


def main(candles=None) -> dict:
    from modules.market_cache import get_klines
    get = candles or get_klines
    rows = {"crypto": [], "metals": []}
    ok, bad = [], []
    for grp, items in (("crypto", [(a, f"{a}-USDT") for a in CRYPTO]), ("metals", list(METALS.items()))):
        for name, sym in items:
            try:
                w = get(sym, "1w", 300)
                m = get(sym, "1mo", 300)
                if w is None or len(w) < WARM + 20:
                    raise ValueError(f"only {0 if w is None else len(w)} weekly bars")
                r = walk(w, m)
                for x in r:
                    x["sym"] = name
                rows[grp] += r
                ok.append(name)
            except Exception as e:
                bad.append(f"{name} ({type(e).__name__})")
            time.sleep(0.2)
    res = {"when": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "symbols_ok": ok, "symbols_failed": bad, "groups": {}}
    for grp in ("crypto", "metals"):
        res["groups"][grp] = [summarise(rows[grp], "r4", 1), summarise(rows[grp], "r4", 4), summarise(rows[grp], "r12", 12)]
    res["rows"] = sum(len(v) for v in rows.values())
    return res


def summary_ar(res: dict) -> str:
    """Short Arabic Telegram message: per group, the non-overlapping 4-week and 12-week tables in one line each."""
    out = [f"🧪 باك تيست محلل السبوت ({res['when']} UTC) - {len(res['symbols_ok'])} رمز"]
    for grp, sums in res["groups"].items():
        name = "الكريبتو" if grp == "crypto" else "المعادن"
        for s in sums[1:]:
            top = next(b for b in s["buckets"] if b["bucket"] == ">= 35")
            low = next(b for b in s["buckets"] if b["bucket"] == "<= -35")
            hz = "4 أسابيع" if s["horizon"] == "r4" else "12 أسبوع"
            t = s["t_top_vs_rest"]
            verdict = ("مش دليل (أقل من 30 عينة)" if s["n_top"] < 30 else "الدرجة العالية كانت أحسن ✅" if t is not None and t >= 2 else
                       "الدرجة العالية كانت أسوأ ❌" if t is not None and t <= -2 else "مفيش فرق واضح")
            f = lambda b: "—" if b["mean_pct"] is None else f"{b['mean_pct']:+.1f}% (n {b['n']})"
            out.append(f"{name} · {hz}: درجة ≥35 {f(top)} · درجة ≤-35 {f(low)} · كل الأسابيع {s['all_mean_pct']:+.1f}% → {verdict}" if s["n"] else f"{name} · {hz}: مفيش داتا")
    if res["symbols_failed"]:
        out.append("ناقص: " + ", ".join(res["symbols_failed"]))
    out.append("التفاصيل في GitHub Actions > Spot backtest > Summary. ده ماضي مش وعد.")
    return "\n".join(out)


if __name__ == "__main__":
    res = main()
    md = fmt(res)
    print(md)
    with open("spot_backtest.json", "w") as f:
        json.dump(res, f, indent=1)
    with open("spot_backtest.md", "w") as f:
        f.write(md)
    if "--telegram" in sys.argv:
        from modules.telegram_alerts import send
        err = send(summary_ar(res))
        print("telegram:", err or "sent")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(md + "\n")
