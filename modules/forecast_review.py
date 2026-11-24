"""Continuous review of the daily calls: what worked, what did not, and what to study next. Rule-based, free, no LLM.

Reads the recorded calls (data/forecasts/<symbol>.jsonl) and their outcomes (data/forecasts/outcomes.jsonl), and writes
docs/forecasts/REVIEW.md. Honest gate: break-even win rate for a 1.5R target is 40 %; a row only 'beats break-even'
when n >= 100 and the Wilson 95 % lower bound is above 40 %. Smaller samples are 'not evidence' / 'too small'.
'Candidates to study' are ranked by the lower bound (the cautious end), and are things to test in the lab, not trades.
Nothing here changes a rule by itself: observations are written down for a person to decide.
Run: python -m modules.forecast_review     Tests: python3 tests/test_forecast_review.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FDIR = ROOT / "data" / "forecasts"
OUT = ROOT / "docs" / "forecasts" / "REVIEW.md"
TARGET_R = 1.5
BREAK_EVEN = 1 / (1 + TARGET_R)      # 0.40


def _load(p):
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf8").splitlines() if x.strip()]


def rows(folder=None):
    """Outcome rows (symbol, class, side, outcome, R) of valid calls only (see daily_forecast.valid_ids)."""
    from modules.daily_forecast import scored
    return scored(folder or FDIR)


def verdict(n, lo, hi):
    if n < 30:
        return "not evidence (n < 30)"
    if n < 100:
        return "too small (n < 100)"
    if lo > BREAK_EVEN:
        return "beats break-even (check costs)"
    if hi < BREAK_EVEN:
        return "below break-even"
    return "undecided"


def table(res, key):
    from modules.forecast_log import wilson
    by = {}
    for r in res:
        by.setdefault(r.get(key) or "—", []).append(r)
    out = []
    for k, rs in by.items():
        n = len(rs)
        w = sum(1 for r in rs if r["outcome"] == "win")
        l = sum(1 for r in rs if r["outcome"] == "loss")
        decided = w + l
        lo, hi = wilson(w, decided) if decided else (0.0, 0.0)
        out.append({"key": k, "n": n, "wins": w, "losses": l, "timeouts": n - decided,
                    "win_rate": round(w / decided, 3) if decided else None, "lo": round(lo, 3), "hi": round(hi, 3),
                    "avg_R": round(sum(r["R"] for r in rs) / n, 3) if n else 0.0, "verdict": verdict(n, lo, hi)})
    return sorted(out, key=lambda x: (-x["lo"], -x["n"]))


def observations(res):
    """Plain findings for a person to read. Never applied automatically."""
    obs = []
    n = len(res)
    if not n:
        return ["No scored calls yet."]
    to = sum(1 for r in res if r["outcome"] == "timeout")
    if to / n > 0.4:
        obs.append(f"{to} of {n} calls ran out of time: the 5-bar horizon may be too short for a 1.5R target.")
    for side in ("long", "short"):
        rs = [r for r in res if r.get("side") == side]
        if len(rs) >= 30:
            w = sum(1 for r in rs if r["outcome"] == "win")
            obs.append(f"{side}: {w} wins of {len(rs)} calls.")
    if n < 30:
        obs.append(f"Only {n} scored calls in total: nothing here is evidence yet.")
    return obs


def candidates(res, k=5):
    """Symbols worth a closer test next: n >= 30, ranked by the Wilson lower bound (cautious). Not trades."""
    return [r for r in table(res, "symbol") if r["n"] >= 30][:k]


def write(folder=None, out=None):
    res = rows(folder)
    lines = ["# Daily calls: review (auto)", "",
             f"Break-even win rate for a {TARGET_R}R target: {BREAK_EVEN:.0%}. A row beats it only with n >= 100 and the 95 % lower bound above it.",
             "Candidates are for the lab, not trades. Observations are for a person to decide; nothing is changed automatically.", ""]
    for title, key in (("By class", "class"), ("By symbol", "symbol"), ("By side", "side")):
        lines += [f"## {title}", "", "| | n | wins | losses | timeouts | win rate | 95% CI | avg R | verdict |", "|---|---|---|---|---|---|---|---|---|"]
        t = table(res, key)
        lines += [f"| {r['key']} | {r['n']} | {r['wins']} | {r['losses']} | {r['timeouts']} | {r['win_rate']} | {r['lo']}–{r['hi']} | {r['avg_R']} | {r['verdict']} |" for r in t] or ["| — | 0 | | | | | | | no scored calls yet |"]
        lines.append("")
    lines += ["## Candidates to study next (n >= 30, cautious ranking)", ""]
    lines += [f"- {r['key']}: n {r['n']}, win rate {r['win_rate']}, lower bound {r['lo']}" for r in candidates(res)] or ["- none yet (no symbol has 30 scored calls)"]
    lines += ["", "## Observations", ""] + [f"- {o}" for o in observations(res)]
    text = "\n".join(lines) + "\n"
    dest = out or OUT
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf8")
    return text


if __name__ == "__main__":
    print(write()[:400])
