"""DAILY TOP 7: the seven best-confirmed ideas of the day across forex, metals, crypto, indices and stocks (owner 2026-11-06).

Inputs are what the platform already computes: Day plan plans (day_plan.scan, timeframe confluence), SMT events (intermarket.scan_pairs), Watch items (context setups that agree with the 1D + 4H bias).
Ranking is two-step and transparent:
  1. CALM FIRST: markets that move smoothly (low ATR % for their class and a high efficiency ratio) come before choppy ones; the choppy ones are kept at the bottom ("leave the choppy for the harder days").
  2. CONFIRMATION: each school / tool that agrees adds points: timeframes in the chain (3-5), distinct schools, SMT on the same side, context watch items, the kill zone, R:R >= 1.5.
Points are a count of agreeing evidence, not a probability. Nothing here is validated as a whole; the brain (modules/brain.py) logs every list and grades it afterwards."""
from __future__ import annotations

import numpy as np

CALM_ER = 0.25          # efficiency ratio (20 bars of the 1H chart) below this = choppy
ATR_PCT_Q = 0.75        # ATR % above this quantile of the universe = jumpy


def calm_stats(df, n: int = 20) -> dict | None:
    """{'atr_pct', 'er'} from the 1H candles: ATR14 / close, and the efficiency ratio |net move| / sum |bar moves| over n bars (1 = a straight line, 0 = pure chop)."""
    if df is None or len(df) < n + 15:
        return None
    h, l, c = (df[x].to_numpy(float) for x in ("high", "low", "close"))
    tr = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    atr = float(tr[-14:].mean())
    seg = c[-(n + 1):]
    path = float(np.abs(np.diff(seg)).sum())
    er = float(abs(seg[-1] - seg[0]) / path) if path > 0 else 0.0
    return {"atr_pct": atr / float(c[-1]) if c[-1] else 0.0, "er": er}


def _smt_side(sym, direction, smt_events):
    """Number of SMT events on this symbol pointing the same way (>= 15m)."""
    n = 0
    for e in smt_events or []:
        if sym in (e.get("a"), e.get("b")) and e.get("direction") == direction and e.get("tf") not in ("5m", "1m"):
            n += 1
    return n


def score_plan(p: dict, smt_events=None, watch=None) -> tuple[int, list]:
    cf = p["confluence"]
    pts, why = 0, []
    pts += 2 * cf["n"]
    why.append(f"{cf['n']}/{cf['of']} timeframes agree ({', '.join(t.upper() for t in cf['agree'])})")
    pts += int(p["stars"])
    ns = len(p["schools"])
    pts += ns
    if ns:
        why.append(f"{ns} school(s): {', '.join(p['schools'][:4])}")
    sm = _smt_side(p["symbol"], p["direction"], smt_events)
    if sm:
        pts += 2 * min(sm, 2)
        why.append(f"SMT agrees ({sm})")
    wc = [w for w in (watch or []) if w["symbol"] == p["symbol"] and w["direction"] == p["direction"]]
    if wc:
        sch = {s for w in wc for s in w["schools"]}
        pts += len(sch)
        why.append("context: " + ", ".join(sorted(sch)))
    if (p.get("session") or {}).get("kill_zone"):
        pts += 1
        why.append("inside a kill zone now")
    if p["rr1"] >= 1.5:
        pts += 1
        why.append(f"R:R 1:{p['rr1']}")
    return pts, why


def rank(plans, smt_events=None, watch=None, calm=None, top: int = 7, per_symbol: int = 1) -> list:
    """The top list. calm = {symbol: calm_stats}. One idea per symbol by default (the best timeframe)."""
    calm = calm or {}
    atrs = [c["atr_pct"] for c in calm.values() if c]
    cut = float(np.quantile(atrs, ATR_PCT_Q)) if len(atrs) >= 4 else None
    rows = []
    for p in plans:
        pts, why = score_plan(p, smt_events, watch)
        c = calm.get(p["symbol"])
        choppy = bool(c and (c["er"] < CALM_ER or (cut is not None and c["atr_pct"] > cut)))
        rows.append({**p, "points": pts, "why": why, "calm": c, "choppy": choppy})
    rows.sort(key=lambda r: (r["choppy"], -r["points"], -r["rr1"]))
    out, seen = [], {}
    for r in rows:
        if seen.get(r["symbol"], 0) >= per_symbol:
            continue
        seen[r["symbol"]] = seen.get(r["symbol"], 0) + 1
        out.append(r)
        if len(out) >= top:
            break
    return out


def format_top(items, clock=None, ar: bool = True) -> str:
    import html
    from modules.day_plan import session_label
    esc = html.escape
    head = f"🎯 <b>{'أحسن 7 فرص النهاردة' if ar else 'Top 7 for today'}</b>" + (f" · {esc(session_label(clock, ar))}" if clock else "")
    if not items:
        return head + ("\nمفيش فرصة متأكدة بترابط فريمات كفاية دلوقتي." if ar else "\nNothing confirmed by enough timeframes right now.")
    lines = [head]
    for i, r in enumerate(items, 1):
        up = r["direction"] == "bullish"
        calm = ("هادي" if not r["choppy"] else "متذبذب") if ar else ("calm" if not r["choppy"] else "choppy")
        lines.append(f"\n{i}. {'🟢' if up else '🔴'} <b>{esc(r['symbol'])}</b> {('شراء' if up else 'بيع') if ar else ('BUY' if up else 'SELL')} · {r['tf'].upper()} · {calm} · {r['points']} {'نقطة تأكيد' if ar else 'confirm pts'}\n"
                     f"{'دخول' if ar else 'Entry'} {r['entry']} · {'وقف' if ar else 'Stop'} {r['stop']} · {'أهداف' if ar else 'Targets'} {' / '.join(str(x) for x in r['tps'])} · {'حركة' if ar else 'move'} {r['move_points']} {'نقطة' if ar else 'pts'}\n"
                     f"<i>{esc(' · '.join(r['why'][:3]))}</i>")
    lines.append("\n<i>نقاط التأكيد عدد أدلة متفقة مش نسبة نجاح. الهادي الأول والمتذبذب في الآخر. مش نصيحة مالية.</i>" if ar else
                 "\n<i>Confirm points count agreeing evidence, not a win rate. Calm first, choppy last. Not financial advice.</i>")
    return "\n".join(lines)[:3900]
