"""HUB TAB 4 - DECISION TRAIL: for every logged signal, which gates did it pass, and was it written down BEFORE its outcome?

Reads the signal log (modules/signal_log.py records) and shows each signal's path: Scan -> Detect -> Validate -> Size -> Settle.
  Scan      the signal was logged at time t
  Detect    score/max and the layers that fired
  Validate  plan is coherent (entry/stop/target on the right sides) AND the rule behind it is proven. 'Proven' = its setup id or
            a layer name matches a rule the Truth Court promoted. Until then it is shown as UNPROVEN, not hidden.
  Size      risk distance (% of price) and reward:risk straight from the plan
  Settle    tp / sl / exp / nofill; R is shown net of the lab's planning cost (0.10R per closed trade)
Integrity: a resolved record must carry t_out >= t. Otherwise it is flagged (a number whose time we cannot trust is not evidence).
It publishes the ordered live R series for the Decay Watch tab. This tab tests no hypothesis itself (n_trials = 0).
Identity: violet, glyph "⟡". Pure Python; render() takes st so the module imports without streamlit."""
from __future__ import annotations

import json

from modules import hub_core

SPEC = hub_core.TabSpec(
    id="trail", title="Decision Trail", glyph="⟡", accent="#9B6BFF",
    purpose="Shows each signal's path through the gates, flags unproven rules, and keeps the live R series honest.",
    consumes=("truth",),
)
COST_R = 0.10          # lab planning cost per closed trade, same number as kpi.py / strategy_lab.py
MIN_N = hub_core.MIN_N
STAGES = ("Scan", "Detect", "Validate", "Size", "Settle")


def plan_check(rec: dict) -> tuple[bool, float | None, float | None]:
    """(coherent?, risk as fraction of entry, reward:risk) from entry/stop/tp1 and direction."""
    try:
        e, sl, tp = float(rec["entry"]), float(rec["stop"]), float(rec["tp1"])
    except (KeyError, TypeError, ValueError):
        return False, None, None
    long_ = rec.get("dir") == "bullish"
    if e <= 0 or abs(e - sl) <= 0:
        return False, None, None
    ok = (sl < e < tp) if long_ else (tp < e < sl)
    risk = abs(e - sl)
    return ok, risk / e, (abs(tp - e) / risk if ok else None)


def rule_names(rec: dict) -> set:
    names = set()
    sid = rec.get("setup_id")
    if sid:
        names.add(str(sid).lower())
    for l in rec.get("layers") or []:
        names.add(str(l).lower())
    return names


def promoted_keys(root=None) -> set:
    """Rule keys the Truth Court currently promotes (empty when it never ran or nothing passes)."""
    snap = hub_core.read("truth", root)
    if not snap:
        return set()
    return {str(f.get("key")).lower() for f in snap.get("findings", []) if f.get("promote")}


def row(rec: dict, proven: set) -> dict:
    """One signal's trail. Each stage is (status, detail); 'flags' lists integrity problems."""
    ok, risk_frac, rr = plan_check(rec)
    names = rule_names(rec)
    flags = []
    out = rec.get("out")
    if out and (rec.get("t_out") is None or rec.get("t_out") < rec.get("t", 0)):
        flags.append("outcome time missing or before signal time")
    detect = f"{rec.get('score', 0)}/{rec.get('max', 0)}" + (f" {','.join(rec['layers'])}" if rec.get("layers") else "")
    if not ok:
        validate = ("bad plan", "entry/stop/target not on the right sides")
    elif names & proven:
        validate = ("pass", "rule promoted by the Truth Court")
    else:
        validate = ("UNPROVEN", "no promoted rule behind this setup" if names else "no rule recorded (setup_id/layers missing)")
    size = ("ok", f"risk {risk_frac * 100:.2f}% of price, RR {rr:.2f}") if ok else ("n/a", "")
    if out in ("tp", "sl"):
        settle = (out, f"{rec['r']:+.2f}R gross, {rec['r'] - COST_R:+.2f}R net")
    elif out:
        settle = (out, "not counted in win rate")
    else:
        settle = ("open", "")
    return {"t": rec.get("t"), "symbol": rec.get("symbol"), "tf": rec.get("tf"), "dir": rec.get("dir"),
            "stages": {"Scan": ("logged", ""), "Detect": ("ok" if rec.get("score", 0) >= 1 else "weak", detect),
                       "Validate": validate, "Size": size, "Settle": settle},
            "net_r": (rec["r"] - COST_R) if out in ("tp", "sl") else None, "flags": flags,
            "t_out": rec.get("t_out")}


def analyse(recs: list, root=None, publish: bool = True) -> dict:
    proven = promoted_keys(root)
    rows = [row(r, proven) for r in recs]
    closed = sorted((x for x in rows if x["net_r"] is not None and not x["flags"]), key=lambda x: x["t_out"])
    live_r = [round(x["net_r"], 3) for x in closed]
    n = len(live_r)
    mean = sum(live_r) / n if n else None
    cnt = lambda st, val: sum(1 for x in rows if x["stages"][st][0] == val)
    summary = {"signals": len(rows), "closed_trusted": n, "open": cnt("Settle", "open"),
               "unproven": cnt("Validate", "UNPROVEN"), "bad_plan": cnt("Validate", "bad plan"), "proven": cnt("Validate", "pass"),
               "flagged": sum(1 for x in rows if x["flags"]), "live_net_avg_r": None if mean is None else round(mean, 3),
               "enough": n >= MIN_N,
               "verdict": ("no closed signals yet: no statistics" if not n else
                           f"n={n} closed signals, net {mean:+.3f}R per trade" + ("" if n >= MIN_N else f" (n < {MIN_N}: not evidence)"))}
    if publish:
        hub_core.publish(SPEC.id, [], 0, extra={"summary": summary, "live_r": live_r}, root=root)
    return {"rows": rows, "summary": summary, "live_r": live_r}


def parse_jsonl(text: str) -> list:
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass   # a damaged line must not hide the rest
    return out


def render(st, L=lambda s: s) -> None:
    st.markdown(f"<div style='border-left:4px solid {SPEC.accent};padding-left:10px'><b>{SPEC.glyph} {L(SPEC.title)}</b><br>"
                f"<span style='opacity:.75'>{L(SPEC.purpose)}</span></div>", unsafe_allow_html=True)
    up = st.file_uploader(L("Signal log (.signal_log.jsonl from the GitHub Actions artifact)"), type=["jsonl", "txt"], key="ht_up")
    if up is not None:
        recs = parse_jsonl(up.getvalue().decode("utf-8", "replace"))
        src = L("uploaded file")
    else:
        from modules import signal_log
        recs = signal_log.load()
        src = str(signal_log.PATH)
    if not recs:
        st.info(L(f"No signals in {src}. Upload the log, or let the cron write it. Nothing is estimated."))
        return
    res = analyse(recs)
    s = res["summary"]
    c = st.columns(4)
    c[0].metric(L("Signals"), s["signals"])
    c[1].metric(L("Unproven rule"), s["unproven"])
    c[2].metric(L("Closed (trusted)"), s["closed_trusted"])
    c[3].metric(L("Live net R / trade"), "n/a" if s["live_net_avg_r"] is None else s["live_net_avg_r"])
    (st.success if s["enough"] else st.warning)(L(s["verdict"]))
    if s["flagged"]:
        st.error(L(f"{s['flagged']} record(s) have an untrustworthy outcome time and are excluded from the R series."))
    st.dataframe([{"time": x["t"], "symbol": x["symbol"], "tf": x["tf"], "dir": x["dir"],
                   **{k: f"{v[0]} {v[1]}".strip() for k, v in x["stages"].items()}, "flags": "; ".join(x["flags"])}
                  for x in sorted(res["rows"], key=lambda x: -(x["t"] or 0))[:200]], hide_index=True, use_container_width=True)
    st.caption(L("The live R series is published for the Decay Watch tab. 'Unproven' is the honest default until the Truth Court promotes a rule."))
