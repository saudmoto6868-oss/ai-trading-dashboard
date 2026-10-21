"""One-shot news and X digest from xAI (Grok) for the assets we watch. Manual run only (workflow_dispatch).

Cost control: one request per run, capped output tokens, the model is picked from the account's own model list
(cheapest 'mini' / 'fast' name first), and the output is an artifact, not committed. Output is news to read, not a
trading signal: it does not count as evidence (n >= 100, t > 3, out-of-sample)."""
import json
import os
import sys

import requests

API = "https://api.x.ai/v1"
ASSETS = "gold, silver, crude oil, S&P 500, Nasdaq 100, EUR/USD, GBP/USD, USD/JPY, bitcoin, ethereum"
MAX_OUT = 900   # output tokens per run: the spend cap


def pick_model(ids: list[str]) -> str:
    """Cheapest-looking model first: names with 'mini' or 'fast', then any grok model. Empty string if none."""
    grok = [i for i in ids if "grok" in i.lower()]
    for key in ("mini", "fast"):
        hit = [i for i in grok if key in i.lower()]
        if hit:
            return sorted(hit)[0]
    return sorted(grok)[0] if grok else ""


def build_messages(day: str) -> list[dict]:
    system = ("You summarise market-moving news and X posts for a trader. Use only facts you can source; "
              "name the source and time for each item. No buy or sell advice, no price targets. "
              "Say 'unverified' for anything from a single post.")
    user = (f"Date: {day}. Assets: {ASSETS}. List up to 8 items from the last 24 hours that could move these assets "
            "(central banks, tariffs and trade posts, government or political statements, large company news, "
            "major social posts). For each: time, asset(s), one-line fact, source, confidence (high / unverified), "
            "and expected direction only as 'up / down / unclear'. Keep it short.")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def main() -> int:
    key = os.environ.get("XAI_API_KEY", "")
    if not key:
        print("XAI_API_KEY is empty", file=sys.stderr)
        return 1
    h = {"Authorization": f"Bearer {key}"}
    models = requests.get(f"{API}/models", headers=h, timeout=30).json().get("data", [])
    model = pick_model([m.get("id", "") for m in models])
    if not model:
        print("no grok model on this account", file=sys.stderr)
        return 1
    import datetime
    day = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    r = requests.post(f"{API}/chat/completions", headers=h, timeout=180,
                      json={"model": model, "messages": build_messages(day), "max_tokens": MAX_OUT, "temperature": 0.2})
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"]
    out = {"day": day, "model": model, "digest": text}
    with open("grok_digest.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"model={model} chars={len(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
