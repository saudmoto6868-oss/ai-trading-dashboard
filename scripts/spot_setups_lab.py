"""Spot setup lab (owner 2026-11-06: 'measure every setup, keep reviewing'). Weekly on GitHub Actions; writes
data/spot_setup_evidence.json that the brain, the ideas desk and the setup library show next to each setup.

Walk-forward, no look-ahead: at each step the frames are cut at that bar (monthly frame: closed months only) and the SAME
code as the live desk runs (spot_setups.radar + spot_only on spot_ind.analyse reads). For every setup that fires:
  forward return over H bars (1W: 8 weeks, 1D: 10 days), compared with the average forward return of ALL steps of the same
  market group (the baseline). Buy setups should beat the baseline; exit setups should come before a WORSE return (their
  sign is flipped so 'positive = it helped' for both). A setup firing again within H bars on the same market is not counted
  twice (no overlap). t = Welch t of the setup's returns vs the baseline returns. n < 30 = not evidence.
Order flow and COT setups are not in this test (no free history of them here) - said in the file."""
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
from modules import spot_setups as SS

CRYPTO = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK", "LTC", "BCH", "XLM"]
OTHER = {"GOLD": "Y:GC=F", "SILVER": "Y:SI=F", "COPPER": "Y:HG=F", "PLATINUM": "Y:PL=F", "OIL": "Y:CL=F", "EURUSD": "Y:EURUSD=X"}
PLAN = {"1w": (8, 2, 80), "1d": (10, 3, 120)}   # tf: (forward bars H, step every k bars, warm-up bars)


def _closed_months(m, t_close):
    end = pd.to_datetime(m["time"]) + pd.offsets.MonthBegin(1)
    return m[end <= t_close].reset_index(drop=True)


def walk(sym_frames: dict, tf: str) -> tuple[list, list]:
    """-> (setup rows, baseline returns) for one market on one timeframe."""
    H, step, warm = PLAN[tf]
    df = sym_frames[tf].reset_index(drop=True)
    m = sym_frames.get("1mo")
    c = df["close"].to_numpy(float)
    rows, base, last = [], [], {}
    for i in range(warm, len(df) - H, step):
        cut = df.iloc[max(0, i - 299):i + 1].reset_index(drop=True)
        fwd = c[i + H] / c[i] - 1
        base.append(fwd)
        frames = {tf: cut}
        if m is not None and tf == "1w":
            mt = _closed_months(m, pd.to_datetime(df["time"].iloc[i]) + pd.Timedelta(days=7))
            if len(mt) >= 30:
                frames["1mo"] = mt.tail(300)
        reads = {k: I.analyse(v) for k, v in frames.items()}
        b = {"reads": reads, "frames": frames, "price": float(c[i]), "stats": I.spot_stats(cut if tf == "1d" else None, cut if tf == "1w" else None, frames.get("1mo"))}
        try:
            found = SS.radar(frames, tfs=(tf,)) + SS.spot_only(b)
        except Exception:
            continue
        for s in found:
            if s["tf"] != tf:
                continue
            key = f"{s['id']}|{tf}"
            if i - last.get(key, -10 ** 9) < H:
                continue
            last[key] = i
            rows.append({"key": key, "school": s["school"], "side": s["side"], "ret": fwd if s["side"] == "buy" else -fwd, "i": i})
    return rows, base


def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return None
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return float((a.mean() - b.mean()) / se) if se else None


def main(candles=None, crypto=None, other=None) -> dict:
    from modules.market_cache import get_klines
    get = candles or get_klines
    groups = {"crypto": [(a, f"{a}-USDT") for a in (CRYPTO if crypto is None else crypto)], "other": list((OTHER if other is None else other).items())}
    agg, ok, bad = {}, [], []
    for grp, items in groups.items():
        rows_g, base_g = [], []
        for name, sym in items:
            try:
                fr = {"1w": get(sym, "1w", 300), "1d": get(sym, "1d", 300), "1mo": get(sym, "1mo", 300)}
                for tf in ("1w", "1d"):
                    if fr[tf] is None or len(fr[tf]) < PLAN[tf][2] + 20:
                        continue
                    r, bse = walk(fr, tf)
                    for x in r:
                        x["grp"] = grp
                    rows_g += r
                    base_g += [(tf, v) for v in bse]
                ok.append(name)
            except Exception as e:
                bad.append(f"{name} ({type(e).__name__})")
            time.sleep(0.2)
        for key in sorted({r["key"] for r in rows_g}):
            tf = key.split("|")[1]
            rs = [r for r in rows_g if r["key"] == key]
            side = rs[0]["side"]
            bs = [v if side == "buy" else -v for t, v in base_g if t == tf]
            a = agg.setdefault(key, {"school": rs[0]["school"], "side": side, "rets": [], "base": []})
            a["rets"] += [r["ret"] for r in rs]
            a["base"] += bs
    setups = {}
    for key, a in agg.items():
        r = np.asarray(a["rets"], float)
        setups[key] = {"school": a["school"], "side": a["side"], "n": int(len(r)), "mean_pct": float(r.mean() * 100) if len(r) else None,
                       "base_pct": float(np.mean(a["base"]) * 100) if a["base"] else None, "pos_pct": float((r > 0).mean() * 100) if len(r) else None,
                       "t": welch(r, a["base"])}
    return {"run": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "markets_ok": ok, "markets_failed": bad, "setups": setups,
            "note": "1W: 8-week forward return, 1D: 10-day; vs the baseline of all steps; exit setups sign-flipped; order-flow / COT setups not tested (no history)."}


def report(res: dict) -> str:
    lines = [f"# Spot setup lab - {res['run']} UTC", f"Markets: {', '.join(res['markets_ok'])}" + (f" · missing {', '.join(res['markets_failed'])}" if res["markets_failed"] else ""), "",
             "| setup | side | school | n | mean | baseline | positive | t | verdict |", "|---|---|---|---|---|---|---|---|---|"]
    for k, s in sorted(res["setups"].items(), key=lambda kv: -(kv[1]["t"] or -99)):
        lines.append(f"| {k} | {s['side']} | {s['school']} | {s['n']} | {s['mean_pct']:+.2f}% | {s['base_pct']:+.2f}% | {s['pos_pct']:.0f}% | "
                     + (f"{s['t']:+.2f}" if s["t"] is not None else "—") + f" | {SS.ev_label(s)} |")
    lines.append("")
    lines.append(res["note"])
    return "\n".join(lines)


def summary_ar(res: dict) -> str:
    good = [(k, s) for k, s in res["setups"].items() if s["n"] >= 30 and (s["t"] or 0) >= 3]
    bad = [(k, s) for k, s in res["setups"].items() if s["n"] >= 30 and (s["t"] or 0) <= -3]
    out = [f"🧪 معمل سيت أبات السبوت ({res['run']} UTC): {len(res['setups'])} سيت أب اتقاس على {len(res['markets_ok'])} سوق"]
    out.append("✅ اشتغلت أحسن من العادي: " + (", ".join(f"{k} (n {s['n']}, t {s['t']:+.1f})" for k, s in sorted(good, key=lambda x: -x[1]["t"])[:8]) or "ولا واحدة"))
    out.append("❌ كانت أسوأ: " + (", ".join(f"{k} (t {s['t']:+.1f})" for k, s in sorted(bad, key=lambda x: x[1]["t"])[:6]) or "ولا واحدة"))
    out.append("الحد: t ≥ 3 و 30 مرة على الأقل (لأن حوالي 90 سيت أب بيتقاسوا مع بعض والحظ بيدي t = 2 أحيانًا). الباقي مفيش فرق أو قليل. ده ماضي مش وعد.")
    return "\n".join(out)


if __name__ == "__main__":
    res = main()
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "spot_setup_evidence.json"), "w") as f:
        json.dump(res, f, indent=1)
    md = report(res)
    print(md)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(md + "\n")
    if "--telegram" in sys.argv:
        from modules.telegram_alerts import send
        print("telegram:", send(summary_ar(res)) or "sent")
