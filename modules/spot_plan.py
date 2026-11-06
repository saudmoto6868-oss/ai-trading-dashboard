"""Spot desk plan engine (page 11): long-only, high timeframes (1D trigger, 1W + 1M trend, yearly context).

Every school votes per timeframe with the CODE WE ALREADY HAVE (no new rules):
  trend     modules.mtf.tf_state          swing structure + EMA 50
  elliott   modules.elliott_lab + signals Elliott / Fib families
  smc_ict   signals families MSB-OB, Unicorn, Liquidity (order blocks, FVG, sweeps, CISD, 2022 model ...)
  gann      modules.gann_lab.fit           price levels (support / resistance), no vote
  time      gann_lab time cycle (tsp)      'turn window' when the next cycle bar is <= 2 bars away, no vote
  regime    modules.regime.classify        label only
Votes: bull +1 / bear -1, weighted 1M x3, 1W x2, 1D x1 -> score -100..100.
Spot = buy only: a bearish score means 'wait / take profit', never 'sell short'.
NOT BACKTESTED as a combination: the lab showed grades do not rank trades and the htf filter alone was worse than
random, so this is a structured reading of the chart, not evidence. Staged buys (3 levels) + invalidation on a weekly close."""
from __future__ import annotations

import numpy as np

TFS = ("1d", "1w", "1mo")
W = {"1d": 1, "1w": 2, "1mo": 3}
SCHOOLS = ("trend", "elliott", "smc_ict")
SMC_FAM = {"MSB-OB", "Unicorn", "Liquidity"}
EW_FAM = {"Elliott", "Fib"}


def _atr(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    tr = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    return float(tr[-n:].mean()) if len(tr) else 0.0


def _gann(df):
    from modules import gann_lab
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    f = gann_lab.fit(h, l, c)
    if not f:
        return None
    lo, hi = float(l.min()), float(h.max()) * 1.6
    lv = gann_lab.grid(f["P"], f["s"], f["d"], gann_lab.cycles_needed(f["P"], f["s"], f["d"], lo * 0.5, hi))
    n = len(df)
    nxt = f["i0"] + f["tsp"]
    while nxt <= n - 1:
        nxt += f["tsp"]
    return {"levels": sorted(float(x) for x in lv if x > 0), "tsp": int(f["tsp"]), "bars_to_turn": int(nxt - (n - 1)), "z": float(f["z"])}


def tf_read(df) -> dict:
    """Votes + levels for one timeframe frame."""
    from modules import mtf, regime, signals
    from modules.elliott_lab import elliott_signals
    out = {"available": df is not None and len(df) >= 60, "votes": {}, "notes": [], "zones": []}
    if not out["available"]:
        return out
    d = df.reset_index(drop=True)
    st = mtf.tf_state(d)
    out["state"] = st
    out["votes"]["trend"] = {"bull": 1, "bear": -1}.get(st.get("bias"), 0)
    out["regime"] = regime.classify(d).get("regime")
    sigs, _ = signals.detect_all(d)
    try:
        sigs += elliott_signals(d)
    except Exception:
        pass
    for school, fams in (("elliott", EW_FAM), ("smc_ict", SMC_FAM)):
        s = [x for x in sigs if x.get("family") in fams]
        v = sum(1 if x["direction"] == signals.BULL else -1 for x in s)
        out["votes"][school] = int(np.sign(v))
        out["notes"] += [f"{x['family']}: {x['name']}" for x in s][:4]
        out["zones"] += [(x["zone"], x["direction"] == signals.BULL) for x in s if x.get("zone")]
    try:
        out["gann"] = _gann(d)
    except Exception:
        out["gann"] = None
    out["atr"] = _atr(d)
    out["close"] = float(d["close"].iloc[-1])
    return out


def _pick(cands, px, below, k=3, tol=0.015, span=0.35):
    c = sorted({float(x) for x in cands if x and x > 0 and ((x < px * 0.997) if below else (x > px * 1.003))}, reverse=below)
    lim = px * (1 - span) if below else px * (1 + 3 * span)
    c = [x for x in c if (x >= lim if below else x <= lim)]
    out = []
    for x in c:
        if all(abs(x / y - 1) > tol for y in out):
            out.append(x)
        if len(out) == k:
            break
    return out


def plan(frames: dict, yearly=None) -> dict:
    """frames = {'1d': df, '1w': df, '1mo': df}. -> score, action, buy levels, targets, invalidation, per-tf table."""
    reads = {tf: tf_read(frames.get(tf)) for tf in TFS}
    av = {tf: r for tf, r in reads.items() if r["available"]}
    if not av:
        return {"ok": False, "why": "not enough candles (need 60+ bars on at least one of 1D / 1W / 1M)"}
    px = next(r["close"] for tf, r in reads.items() if r["available"])
    num = sum(W[tf] * v for tf, r in av.items() for v in r["votes"].values())
    den = sum(W[tf] * len(r["votes"]) for tf, r in av.items())
    score = round(100 * num / den) if den else 0
    below, above = [], []
    for tf, r in av.items():
        st = r.get("state", {})
        below.append(st.get("lo"))
        above.append(st.get("hi"))
        for (z0, z1), bull in r["zones"]:
            (below if bull else above).append((z0 + z1) / 2)
        g = r.get("gann")
        if g and tf in ("1w", "1mo"):
            below += [x for x in g["levels"] if x < px]
            above += [x for x in g["levels"] if x > px]
    if yearly is not None and len(yearly) >= 2:
        above.append(float(yearly["high"].max()))
        below.append(float(yearly["low"].iloc[-2]))
    atr_w = (av.get("1w") or next(iter(av.values())))["atr"]
    buys = _pick(below, px, True)
    k = 1
    while len(buys) < 3 and atr_w > 0 and k < 8:   # not enough structure below: fill with weekly-ATR steps
        cand = px - k * min(atr_w, 0.08 * px)
        if cand > 0 and all(abs(cand / y - 1) > 0.015 for y in buys):
            buys.append(cand)
        k += 1
    buys = sorted(buys, reverse=True)[:3]
    sells = _pick(above, px, False)
    inval = (min(buys) - min(atr_w, 0.10 * min(buys))) if buys else None   # one weekly ATR under the lowest buy, at most 10 %
    if score >= 40:
        action = "accumulate" if buys and px <= buys[0] * 1.03 else "hold_buy_dips"
    elif score <= -40:
        action = "take_profit_wait"
    else:
        action = "wait"
    turn = [tf for tf, r in av.items() if r.get("gann") and r["gann"]["bars_to_turn"] <= 2]
    rows = []
    for tf in TFS:
        r = reads[tf]
        if not r["available"]:
            rows.append({"tf": tf, "available": False})
            continue
        g = r.get("gann") or {}
        rows.append({"tf": tf, "available": True, **{f"v_{s}": r["votes"].get(s, 0) for s in SCHOOLS}, "regime": r.get("regime"),
                     "trend": r["state"].get("trend"), "ema": r["state"].get("ema"), "gann_turn_in": g.get("bars_to_turn"),
                     "gann_cycle": g.get("tsp"), "notes": r["notes"]})
    return {"ok": True, "price": px, "score": score, "action": action, "buys": buys, "sells": sells, "invalidation": inval,
            "atr_w": atr_w, "time_turn": turn, "rows": rows}


ACTION_TXT = {
    "accumulate": ("Accumulate (staged buys)", "تجميع على دفعات"),
    "hold_buy_dips": ("Hold / buy the dips at the levels", "احتفظ / اشتري على المستويات"),
    "take_profit_wait": ("Take profit / wait (spot never shorts)", "جني ربح / استنى (السبوت مفيهوش بيع على المكشوف)"),
    "wait": ("Wait - schools disagree", "استنى - المدارس مش متفقة"),
}
