"""Backtest agent for the Technical Office (owner 2026-10-22): the owner explains a trading idea in plain words (Arabic or
English); the agent answers in the same language, asks what is missing, and turns the idea into rules the strategy_rules
model understands. The rules are validated before anything runs; the backtest itself is strategy_bt (no orders, ever).

Free first (owner rule): Google Gemini free tier with GEMINI_API_KEY from Streamlit secrets / env. No key -> a clear message.
"""
from __future__ import annotations

import json

from modules import strategy_rules as SR

SYSTEM = (
    "You are the backtest assistant of a trading dashboard. The owner explains a trading idea. Reply in the owner's language, "
    "short and concrete. Turn the idea into rules that can be tested on OHLCV candles with ONLY these indicators: "
    + ", ".join(SR.INDICATORS) + "; conditions: " + ", ".join(SR.OPS) + "; logic AND or OR; side long or short. "
    "A rule compares an indicator (with a period when it takes one) to a number or to another indicator. "
    "hh / ll = highest high / lowest low of the prior N bars (Donchian breakout: close crosses_above hh); macd_hist = MACD histogram "
    "(no period); adx = trend STRENGTH, not direction (use as a filter, e.g. adx > 20); bbw = Bollinger width in % (squeeze = low). "
    "Use at most one indicator per cluster in a strategy (trend / momentum / volatility / breakout) - repeats add no information. "
    "If something cannot be expressed with these indicators (news, order flow, patterns, sessions), say so plainly in 'reply' "
    "and list it in 'assumptions' instead of inventing a rule. Ask at most two questions when the idea is ambiguous. "
    "Never promise profit; the dashboard judges the result with its evidence gate (n >= 100, t > 3, both halves positive after 0.1R costs)."
)

_IND = list(SR.INDICATORS)
SCHEMA = {
    "type": "OBJECT", "required": ["reply", "ready", "name", "side", "logic", "rules", "assumptions", "questions"],
    "properties": {
        "reply": {"type": "STRING"}, "ready": {"type": "BOOLEAN"}, "name": {"type": "STRING"},
        "side": {"type": "STRING", "enum": list(SR.SIDES)}, "logic": {"type": "STRING", "enum": list(SR.LOGIC)},
        "assumptions": {"type": "ARRAY", "items": {"type": "STRING"}}, "questions": {"type": "ARRAY", "items": {"type": "STRING"}},
        "rules": {"type": "ARRAY", "items": {"type": "OBJECT", "required": ["indicator", "op", "compare"], "properties": {
            "indicator": {"type": "STRING", "enum": _IND}, "period": {"type": "INTEGER"},
            "op": {"type": "STRING", "enum": list(SR.OPS)},
            "compare": {"type": "STRING", "enum": ["number"] + _IND},
            "number": {"type": "NUMBER"}, "compare_period": {"type": "INTEGER"}}}},
    },
}


def to_strategy(ans: dict) -> dict:
    """Agent answer -> strategy dict in the strategy_rules shape (not yet validated)."""
    rules = []
    for r in ans.get("rules") or []:
        rule = {"indicator": r.get("indicator"), "op": r.get("op")}
        if SR.INDICATORS.get(rule["indicator"]):
            rule["period"] = int(r.get("period") or 14)
        if r.get("compare", "number") == "number":
            rule["value"] = float(r.get("number") or 0.0)
        else:
            v = {"indicator": r["compare"]}
            if SR.INDICATORS.get(r["compare"]):
                v["period"] = int(r.get("compare_period") or 50)
            rule["value"] = v
        rules.append(rule)
    name = "".join(ch for ch in str(ans.get("name") or "agent idea") if ch.isalnum() or ch in " -_")[:60].strip() or "agent idea"
    return {"name": name, "side": ans.get("side", "long"), "logic": ans.get("logic", "AND"), "rules": rules}


def ask(text: str, history: list, key: str, model: str = "gemini-flash-latest", provider: str = "gemini") -> dict:
    """One turn with the agent. history: [{"q":..., "a":...}]. Returns the answer dict plus 'strategy' and 'errors'.
    provider 'openai' = ChatGPT (modules/ai_provider.py, owner 2026-10-23), 'gemini' = the free Google key (default / fallback)."""
    if provider == "openai":
        from modules import ai_provider as AP
        msgs = []
        for h in history[-6:]:
            msgs += [{"role": "user", "content": h["q"]}, {"role": "assistant", "content": h["a"]}]
        msgs.append({"role": "user", "content": text})
        return finish(AP.chat_json(SYSTEM, msgs, AP.describe(SCHEMA), key=key, model=None if model.startswith("gemini") else model))
    import requests
    contents = []
    for h in history[-6:]:
        contents += [{"role": "user", "parts": [{"text": h["q"]}]}, {"role": "model", "parts": [{"text": h["a"]}]}]
    contents.append({"role": "user", "parts": [{"text": text}]})
    body = {"systemInstruction": {"parts": [{"text": SYSTEM}]}, "contents": contents,
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": SCHEMA, "maxOutputTokens": 2048}}
    r = None
    for m in dict.fromkeys([model, "gemini-2.5-flash", "gemini-2.0-flash"]):   # a retired model name (404) tries the next one
        r = requests.post("https://generativelanguage.googleapis.com/v1beta/models/" + m + ":generateContent",
                          headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, timeout=30)
        if r.status_code != 404:
            break
    r.raise_for_status()
    parts = ((r.json().get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
    ans = json.loads("".join(p.get("text", "") for p in parts if not p.get("thought")) or "{}")
    return finish(ans)


def finish(ans: dict) -> dict:
    strat = to_strategy(ans)
    ans["strategy"] = strat
    ans["errors"] = SR.validate(strat) if ans.get("rules") else ["no testable rule yet"]
    return ans
