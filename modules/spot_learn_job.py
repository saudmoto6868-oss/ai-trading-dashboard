"""Daily learning cycle for the Spot brain (owner 2026-11-15). Pure logic, no network: the script feeds it live brain
results and price bars; tests feed it synthetic ones.

One cycle:
  1. record(): log the brain's verdicts (per horizon) for every market this run looked at.
  2. record_setups(): log every live setup for the same markets.
  3. score(): re-score the WHOLE log against the price bars. Scoring is deterministic and only uses bars after the
     record time, and rows whose horizon has not passed stay pending, so re-scoring every day is safe (nothing is stored twice).
  4. summary() + stability(): labels only (n >= 30 and |t| >= 3 for any claim). No weight is changed here.
The report is Arabic text for Telegram. Honest by design: pending counts and 'not evidence' are always shown."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from modules import spot_learn as L

MAX_TG = 3900   # Telegram limit is 4096; keep a margin


def bars_from_df(df) -> list[dict]:
    """pandas OHLC frame (time, high, low, close) -> the oldest-first bar list score() expects, with UTC ISO times."""
    out = []
    if df is None or len(df) == 0:
        return out
    for _, r in df.iterrows():
        t = r["time"]
        ts = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        out.append({"time": ts.astimezone(timezone.utc).isoformat(), "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])})
    return out


def cycle(brains: list[dict], path: Path | None, bars: dict, now: datetime | None = None) -> dict:
    """brains: spot_brain.run() results from this run. bars: {asset: bar list}. Returns counts, the scored rows,
    the summary and the Arabic text. Writes only the new brain/setup rows (to `path`)."""
    now = now or L._now()
    brains = [b for b in brains if b.get("price")]   # no price = no measurable row; skip (keeps the log clean when data is down)
    wrote_v = sum(L.record(b, path=path, when=now) for b in brains)
    wrote_s = sum(L.record_setups(b, path=path, when=now) for b in brains)
    rows = L.load(path)
    scored = L.score(rows, bars, now=now)
    res = L.summary(scored)
    stab = L.stability(scored)
    return {"now": now.replace(microsecond=0).isoformat(), "wrote_verdicts": wrote_v, "wrote_setups": wrote_s,
            "rows_total": len(rows), "scored": len(scored), "pending": max(0, len(rows) - len(scored)),
            "summary": res, "stability": stab, "text": report_text(res, stab, len(rows), len(scored), wrote_v, wrote_s)}


def report_text(res: dict, stab: dict, total: int, scored: int, wrote_v: int, wrote_s: int) -> str:
    """Arabic Telegram report, capped at MAX_TG characters. Shows counts first, then labels, then stability."""
    lines = ["🧠 تقرير التعلم اليومي للمخ (Spot)",
             f"• سجلات جديدة: مخ {wrote_v} · setups {wrote_s}",
             f"• إجمالي السجل: {total} · اتقاس {scored} · لسه مستني الأفق {max(0, total - scored)}",
             "• قاعدة: لا تغيير تلقائي في الأوزان. أي تسمية بتحتاج n ≥ 30 و t ≥ 3."]
    if not res:
        lines.append("مفيش صفقات اتقاست لسه (لازم الأفق يخلص الأول).")
    else:
        lines.append("— الفئات —")
        for k, v in res.items():
            h, verdict = (k.split("|", 1) + [""])[:2]
            st = stab.get(k, "not yet")
            st_ar = {"holds": "الفترتين متفقين", "flips": "اتقلب بين الفترتين", "not yet": "بدري"}.get(st, st)
            lines.append(f"• {h} / {verdict}: {v['label']} · نجاح {v['hit_pct']:.0f}% · متوسط {v['mean_pct']:+.2f}% · {st_ar}")
    text = "\n".join(lines)
    if len(text) > MAX_TG:
        text = text[: MAX_TG - 20] + "\n… (اتقص)"
    return text
