"""SERVER-SIDE SIGNAL LOG: every scanner alert the headless cron (tg_cron.py) sees is written down, then later checked
against what price really did, so the dashboard's hit-rate is MEASURED on logged signals instead of assumed.

  python -m modules.signal_log                 # print the stats of the log
  python -m modules.signal_log --csv out.csv   # closed trades as time,symbol,side,tf,r  (upload it in the Performance tab)

Rules of the outcome check (deliberately pessimistic, no hindsight):
  * entry counts as filled at signal time if the plan entry is within 0.15 % of the price then, otherwise when a later candle
    touches it (never touched within MAX_BARS -> 'nofill', excluded from stats);
  * after the fill the candles are walked in order: stop touched -> loss (-1 R); first target touched -> win (+RR to TP1);
    BOTH inside one candle -> loss (we cannot know the order);
  * nothing hit within MAX_BARS -> 'exp' (excluded from win rate, counted separately).
Stats always print n; with n < 30 the number is not evidence. File: .signal_log.jsonl (path via SIGNAL_LOG), kept between
GitHub Actions runs by actions/cache and uploaded as an artifact. No logged signals -> no numbers."""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path

PATH = Path(os.environ.get("SIGNAL_LOG", ".signal_log.jsonl"))
DEDUPE_S = 4 * 3600            # same symbol+side+timeframe is logged once per 4 h (the same setup stays 'live' for several scans)
MAX_BARS = 48                  # bars an open signal is followed before it expires
NEAR = 0.0015                  # entry within 0.15 % of the signal-time price = filled at once
MIN_N = 30


def load(path: Path | None = None) -> list[dict]:
    p = path or PATH
    out = []
    try:
        for line in p.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    except FileNotFoundError:
        pass
    except Exception:
        pass   # a damaged line must not stop the cron; the readable part is kept
    return out


def save(recs: list[dict], path: Path | None = None):
    (path or PATH).write_text("\n".join(json.dumps(r, separators=(",", ":")) for r in recs) + ("\n" if recs else ""))


def log_alerts(alerts: list[dict], recs: list[dict], sent_keys: set | None = None, now: float | None = None, px: dict | None = None) -> int:
    """Append the new alerts (all of them, sent or not - the quality filter is evaluated later from the stored q). -> number added.
    px = {symbol: last price} to decide whether the plan entry was 'at market'."""
    now = now or time.time()
    added = 0
    for a in alerts:
        p = a.get("plan") or {}
        if not p.get("entry") or not p.get("stop") or not p.get("tps"):
            continue
        key = f"{a['symbol']}|{a['direction']}|{a.get('tfk') or a.get('tfc')}"
        if any(r["key"] == key and now - r["t"] < DEDUPE_S for r in recs):
            continue
        recs.append({"t": int(now), "key": key, "symbol": a["symbol"], "dir": a["direction"], "tf": a.get("tfk") or a.get("tfc"),
                     "score": int(a.get("score", 0)), "max": int(a.get("max", 0)), "q": a.get("q"), "entry": p["entry"], "stop": p["stop"],
                     "tp1": p["tps"][0], "px0": (px or {}).get(a["symbol"]), "sent": bool(sent_keys and key in sent_keys)})
        added += 1
    return added


_TF_S = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400, "1w": 604800}


def check(rec: dict, df) -> dict | None:
    """Walk candles after the signal. -> {'out': 'tp'|'sl'|'exp'|'nofill', 'r': float} or None while still open."""
    long_ = rec["dir"] == "bullish"
    e, sl, tp = float(rec["entry"]), float(rec["stop"]), float(rec["tp1"])
    risk = abs(e - sl)
    if risk <= 0 or (long_ and not tp > e) or (not long_ and not tp < e):
        return {"out": "bad", "r": 0.0}
    rr = abs(tp - e) / risk
    px0 = rec.get("px0")
    filled = bool(px0) and abs(e - px0) / px0 <= NEAR
    t_ms = rec["t"] * 1000
    import pandas as pd
    ms = pd.to_datetime(df["time"]).astype("datetime64[ns]").astype("int64") // 10**6 if "time" in df.columns else None   # naive UTC -> epoch ms
    rows = df[ms > t_ms] if ms is not None else df.iloc[0:0]
    seen = 0
    for hi, lo in zip(rows["high"].values, rows["low"].values):
        seen += 1
        if not filled:
            if lo <= e <= hi:
                filled = True
            elif seen >= MAX_BARS:
                return {"out": "nofill", "r": 0.0}
            else:
                continue
        hit_sl = lo <= sl if long_ else hi >= sl
        hit_tp = hi >= tp if long_ else lo <= tp
        if hit_sl:
            return {"out": "sl", "r": -1.0}      # includes the both-in-one-candle case
        if hit_tp:
            return {"out": "tp", "r": round(rr, 2)}
        if seen >= MAX_BARS:
            return {"out": "exp", "r": 0.0}
    return None


def resolve(recs: list[dict], get_df, now: float | None = None) -> int:
    """Fill in the outcome of open records. get_df(symbol, tf) -> candles DataFrame (raises on failure -> record stays open)."""
    n = 0
    for r in recs:
        if "out" in r:
            continue
        try:
            res = check(r, get_df(r["symbol"], r["tf"]))
        except Exception:
            continue
        if res:
            r.update(res); r["t_out"] = int(now or time.time()); n += 1
    return n


def stats(recs: list[dict]) -> dict:
    closed = [r for r in recs if r.get("out") in ("tp", "sl")]

    def agg(rs):
        n = len(rs)
        w = sum(1 for r in rs if r["out"] == "tp")
        return {"n": n, "win_pct": round(100 * w / n, 1) if n else None, "avg_r": round(sum(r["r"] for r in rs) / n, 3) if n else None,
                "enough": n >= MIN_N}

    out = {"logged": len(recs), "open": sum(1 for r in recs if "out" not in r),
           "expired": sum(1 for r in recs if r.get("out") == "exp"), "nofill": sum(1 for r in recs if r.get("out") == "nofill"),
           "all": agg(closed), "by": {}}
    for name, fn in (("tf", lambda r: r["tf"]), ("side", lambda r: r["dir"]), ("stars", lambda r: str(r["score"])),
                     ("q>=70", lambda r: "yes" if (r.get("q") or 0) >= 70 else "no"), ("sent", lambda r: "yes" if r.get("sent") else "no")):
        g = {}
        for r in closed:
            g.setdefault(fn(r), []).append(r)
        out["by"][name] = {k: agg(v) for k, v in sorted(g.items())}
    return out


def to_csv(recs: list[dict], path: str):
    """Closed trades in the Journal-export format (time,symbol,side,tf,r) for the Performance tab."""
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["time", "symbol", "side", "tf", "r"])
        for r in sorted((r for r in recs if r.get("out") in ("tp", "sl")), key=lambda r: r.get("t_out", r["t"])):
            w.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(r.get("t_out", r["t"]))), r["symbol"], "buy" if r["dir"] == "bullish" else "sell", r["tf"], r["r"]])


def format_stats(s: dict) -> str:
    a = s["all"]
    lines = [f"logged {s['logged']} | open {s['open']} | expired {s['expired']} | no-fill {s['nofill']} | closed (tp/sl) {a['n']}"]
    if not a["n"]:
        lines.append("no closed signals yet - no statistics.")
        return "\n".join(lines)
    lines.append(f"ALL: n={a['n']} win={a['win_pct']}% avgR={a['avg_r']}" + ("" if a["enough"] else f"  (n < {MIN_N}: NOT evidence yet)"))
    for name, g in s["by"].items():
        lines.append(f"  by {name}: " + "; ".join(f"{k}: n={v['n']} win={v['win_pct']}% R={v['avg_r']}" for k, v in g.items()))
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    recs = load()
    if "--csv" in argv:
        to_csv(recs, argv[argv.index("--csv") + 1]); print("written")
        return 0
    print(format_stats(stats(recs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
