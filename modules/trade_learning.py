"""The journal learns: per-factor win rate and average R over CLOSED trades, lesson candidates, and a readable trade table.

Factors come from each trade's own record at entry (setup type, timeframe, side, score band, tags, order flow, news,
funding, open interest, session). A factor becomes a lesson only with n >= MIN_N and a clear gap vs the baseline. Lessons are
written as CANDIDATES: nothing changes the live scanner by itself; a candidate is promoted by a person after review
(same rule as modules/brain.py). Costs are not included. Times are UTC."""
from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict
from pathlib import Path

from modules import trade_journal as TJ

MIN_N = 30
GAP_PTS = 15.0  # win-rate gap vs baseline (percentage points) before a factor counts as a lesson
LESSONS = Path(os.environ.get("TRADE_LESSONS_PATH", "data/journal/lessons.json"))


def factors(tr: dict) -> list[str]:
    ctx = tr.get("ctx") or {}
    out = [f"setup:{tr.get('ttype')}", f"tf:{tr.get('tfk')}", f"side:{'long' if tr.get('dir') == 'bullish' else 'short'}"]
    s, m = tr.get("score"), tr.get("max")
    if s is not None and m:
        pct = 100 * s / m
        out.append("score:<60" if pct < 60 else "score:60-79" if pct < 80 else "score:80+")
    out += [f"of:{ctx.get('of', 'n/a')}", f"news:{'yes' if ctx.get('news') else 'no'}", f"fund:{ctx.get('fund') or 'none'}",
            f"oi:{ctx.get('oi') or 'n/a'}", f"ses:{ctx.get('ses') or 'n/a'}"]
    out += [f"tag:{t}" for t in (tr.get("tags") or [])[:4]]
    nm = ctx.get("newsMin")
    if nm is not None:  # news timing: minutes to a high-impact event at entry (the window is -30 .. +60 min)
        out.append("news_t:before_15m" if 0 <= nm <= 15 else "news_t:before_60m" if 15 < nm <= 60 else "news_t:just_after" if -30 <= nm < 0 else "news_t:none")
    out += school_factors(ctx, tr)
    return out


def _norm(label: str) -> str:
    """Strip numbers so 'Limit order at 1234.5' and 'Limit order at 1240' are the same factor."""
    return " ".join(re.sub(r"[\d.,%:+\-]+", " ", str(label)).split())[:60]


def school_factors(ctx: dict, tr: dict) -> list[str]:
    """Factors from what every school said at entry: each pro / con / veto (by label), the verdict, and where price sat
    against the nearest level in ATR units (at level / near / far). Missing readings add nothing."""
    out: list[str] = []
    sc = ctx.get("schools") or {}
    if sc:
        out.append(f"verdict:{sc.get('verdict', 'n/a')}")
        out += [f"pro:{_norm(p[1])}" for p in (sc.get("pros") or []) if len(p) > 1]
        out += [f"con:{_norm(p[1])}" for p in (sc.get("cons") or []) if len(p) > 1]
        out += [f"veto:{_norm(v)}" for v in (sc.get("vetoes") or [])]
    snap = ctx.get("snap") or {}
    if snap.get("regime"):
        out.append(f"regime:{snap['regime']}")
    atr, entry = snap.get("atr"), tr.get("entry")
    levels = [l.get("p") for l in (snap.get("lv") or []) if l.get("p") is not None]
    if atr and entry and levels:
        d = min(abs(entry - p) for p in levels) / atr
        out.append("level:at" if d < 0.3 else "level:near" if d < 1 else "level:far")
    return out


def _closed(trades: list) -> list:
    return [t for t in trades if t.get("status") in ("tp", "sl", "exp")]


def learn(trades: list | None = None, path: Path | None = None) -> dict:
    """Factor table + lesson candidates. Pass trades (dicts) or let it read the journal."""
    trades = trades if trades is not None else TJ.all_trades(path)
    closed = _closed(trades)
    n = len(closed)
    base_rs = [TJ.r_total(t) for t in closed]
    base_win = 100 * sum(1 for r in base_rs if r > 0) / n if n else 0.0
    groups: dict = defaultdict(list)
    for t in closed:
        for f in factors(t):
            groups[f].append(t)
    table = []
    for f, ts in sorted(groups.items()):
        rs = [TJ.r_total(t) for t in ts]
        win = 100 * sum(1 for r in rs if r > 0) / len(rs)
        gap = win - base_win
        ev = len(ts) >= MIN_N
        verdict = "not evidence" if not ev else "avoid" if gap <= -GAP_PTS else "prefer" if gap >= GAP_PTS else "neutral"
        table.append({"factor": f, "n": len(ts), "win_pct": round(win, 1), "avg_r": round(sum(rs) / len(rs), 3),
                      "gap_pts": round(gap, 1), "verdict": verdict})
    candidates = [{"status": "candidate", "rule": (f"require confirmation before entry when {r['factor']}" if r["verdict"] == "avoid"
                                                   else f"take this setup when {r['factor']}"),
                   "evidence": f"n={r['n']}, win {r['win_pct']}% vs baseline {round(base_win, 1)}%, avg R {r['avg_r']}"}
                  for r in table if r["verdict"] in ("avoid", "prefer")]
    out = {"ts": int(time.time()), "n_closed": n, "evidence": n >= MIN_N, "baseline_win_pct": round(base_win, 1),
           "table": table, "candidates": candidates}
    return out


def save_lessons(result: dict, path: Path | None = None) -> None:
    """Write the lessons file (replaces the previous one). Read by the journal panel; never read by the scanner."""
    p = path or LESSONS
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def trade_table(trades: list | None = None, path: Path | None = None) -> str:
    """Markdown table: one row per closed trade, with the reason it won or lost. For the meeting room."""
    trades = trades if trades is not None else TJ.all_trades(path)
    rows = ["| UTC set | Symbol | Setup | TF | Side | Result | R | Why | Next time |", "|---|---|---|---|---|---|---|---|---|"]
    for t in _closed(trades):
        a = TJ.analyze(t)
        why = "; ".join(a["postmortem"]["why"]) if a["postmortem"] else "won: " + ", ".join(e["level"] for e in a["exits"])
        nxt = a["postmortem"]["next"] if a["postmortem"] else "keep the same rule"
        rows.append(f"| {a['set_utc']} | {a['symbol']} | {a['setup']} | {a['tf']} | {a['side']} | {a['status']} | {a['r_total']} | {why} | {nxt} |")
    return "\n".join(rows)


def suggestions(path: Path | None = None, k: int = 3) -> list[str]:
    """Read-only: up to k lesson candidates from the lessons file, for the daily brain review. Never applied to any scanner."""
    p = path or LESSONS
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not data.get("evidence"):
        return []
    return [f"{c['rule']} ({c['evidence']}) [candidate]" for c in (data.get("candidates") or [])[:k]]
