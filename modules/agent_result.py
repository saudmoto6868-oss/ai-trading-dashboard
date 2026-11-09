"""The shared agent result (docs/AGENT_CONTRACT.md on branch claude/agent-contract-2026-11-09): one object every agent returns, whoever wrote it
(Grok's desk agents, TIA's functions, Claude's brain jobs). make() builds it, validate() lists what is wrong with one (empty list = fine).
It only describes and checks data: no network, no orders, no secrets. Rules enforced here are the repo rules: mock / estimate / missing data is never 'live';
a statistic with n < 30 is NOT EVIDENCE; a verdict is never a probability."""
from __future__ import annotations

import time

VERDICTS = ("bullish", "bearish", "neutral", "skip", "info")
STREAMS = ("grok", "tia", "claude")
QUALITY = ("live", "delayed", "mock", "estimate", "missing")
MIN_N = 30


def make(agent: str, stream: str, symbol: str, verdict: str, evidence=None, source: str = "", quality: str = "missing", n: int = 0, ts=None, coverage: str = "", note: str = "") -> dict:
    ts = ts if ts is not None else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return {"agent": agent, "stream": stream, "symbol": symbol, "verdict": verdict, "evidence": list(evidence or []), "source": source, "ts": ts, "coverage": coverage,
            "quality": quality, "n": int(n), "note": note, "evidence_ok": int(n) >= MIN_N}


def validate(r) -> list:
    """Problems found in one result (strings); [] when it follows the contract."""
    bad = []
    if not isinstance(r, dict):
        return ["not an object"]
    for k in ("agent", "stream", "symbol", "verdict", "source", "ts", "quality"):
        if not r.get(k):
            bad.append(f"missing {k}")
    if r.get("stream") and r["stream"] not in STREAMS:
        bad.append(f"unknown stream {r['stream']!r}")
    if r.get("verdict") and r["verdict"] not in VERDICTS:
        bad.append(f"unknown verdict {r['verdict']!r}")
    if r.get("quality") and r["quality"] not in QUALITY:
        bad.append(f"unknown quality {r['quality']!r}")
    if r.get("quality") == "live" and str(r.get("source", "")).lower() in ("mock", "estimate", "manual", "lab"):
        bad.append("quality 'live' with a non-live source")
    if r.get("verdict") in ("bullish", "bearish") and not r.get("evidence"):
        bad.append("a directional verdict needs evidence")
    for e in r.get("evidence") or []:
        if not isinstance(e, dict) or "what" not in e:
            bad.append("evidence items need a 'what'")
            break
    n = r.get("n", 0)
    if not isinstance(n, int) or n < 0:
        bad.append("n must be a non-negative integer")
    elif r.get("evidence_ok") is True and n < MIN_N:
        bad.append(f"evidence_ok with n={n} < {MIN_N}")
    for k in r:
        if any(w in k.lower() for w in ("token", "secret", "password", "apikey", "api_key")):
            bad.append(f"field {k!r} looks like a secret")
    if any(isinstance(r.get(k), float) and 0 <= r[k] <= 1 and k in ("probability", "win_rate", "confidence") for k in r):
        bad.append("probabilities are not allowed (count agreeing evidence instead)")
    return bad


def summarize(results) -> dict:
    """{agent: {'bullish': n, 'bearish': n, ...}} per symbol-less view, plus the list of invalid results: for the daily review text."""
    out, invalid = {}, []
    for r in results:
        p = validate(r)
        if p:
            invalid.append((r.get("agent") if isinstance(r, dict) else None, p))
            continue
        d = out.setdefault(r["agent"], {})
        d[r["verdict"]] = d.get(r["verdict"], 0) + 1
    return {"by_agent": out, "invalid": invalid}
