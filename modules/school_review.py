"""Ask an external model (Gemini; DeepSeek / OpenAI if their key is set) to review the trading schools, and save each answer.

Run in GitHub Actions (workflow school-review.yml) so the keys stay in repo Secrets, never in chat or in the code:
  GEMINI_API_KEY (required), DEEPSEEK_API_KEY (optional), OPENAI_API_KEY (optional)
Output: docs/reviews/<topic>-<provider>.md. Claude (the director) reads them, checks the claims against the lab, and decides.
The reviews are opinions with sources to verify - not evidence. Only the lab (n >= 100, t > 3, out-of-sample) is evidence.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "reviews"
CONTEXT = (ROOT / "docs" / "SCHOOLS.md").read_text(encoding="utf-8") if (ROOT / "docs" / "SCHOOLS.md").exists() else ""

TOPICS = {
    "schools": ("Review each school we use (SMC/ICT, price action, Elliott, Gann, harmonic, Fibonacci, sessions, trend, levels). "
                "For each: core rules in one paragraph, what is objectively codeable, what is subjective, the biggest known weaknesses, "
                "and the published evidence (name the study or source; say if you are not sure). Then list which schools overlap and which are complementary. "
                "Answer in English, be concise, no price predictions."),
    "scalp4h": ("A trader wants 15-minute scalps that end within 4 hours (time stop). Propose a checklist of at most 7 conditions in order "
                "(regime, higher-timeframe bias, location, trigger, confirmation, timing, risk), with one measurable rule each, and say which "
                "published evidence supports each rule and which is only convention. No price levels."),
    "risk": ("Summarise the evidence on risk management for discretionary and systematic traders: break-even win rate vs reward:risk, "
             "fixed-fraction sizing, daily loss limits, overtrading, and what peer-reviewed studies say about retail futures traders. "
             "Name sources; flag anything you are unsure of."),
}


GEMINI_MODELS = [os.environ.get("GEMINI_MODEL", ""), "gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash"]


def _gemini(prompt: str) -> str:
    """Gemini with retries: 404 = this model name is not available to the key (try the next); 429 / 503 / timeout = busy (wait, retry)."""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return ""
    last = ""
    for model in [m for m in GEMINI_MODELS if m]:
        for attempt in range(3):
            try:
                r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                  headers={"x-goog-api-key": key, "content-type": "application/json"},
                                  json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.3, "maxOutputTokens": 3000}}, timeout=300)
            except requests.Timeout:
                last = f"{model} timeout"
                time.sleep(20)
                continue
            if r.status_code == 404:
                last = f"model {model} not found"
                break
            if r.status_code in (429, 503):
                last = f"{model} busy ({r.status_code})"
                time.sleep(20 * (attempt + 1))
                continue
            r.raise_for_status()
            return "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"])
    raise RuntimeError(last or "no Gemini model answered")


def _openai_compat(url: str, key: str, model: str, prompt: str) -> str:
    r = requests.post(url, headers={"authorization": "Bearer " + key}, timeout=120,
                      json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 3000})
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


PROVIDERS = {
    "gemini": _gemini,
    "deepseek": lambda p: _openai_compat("https://api.deepseek.com/chat/completions", os.environ.get("DEEPSEEK_API_KEY", ""), "deepseek-chat", p) if os.environ.get("DEEPSEEK_API_KEY") else "",
    "openai": lambda p: _openai_compat("https://api.openai.com/v1/chat/completions", os.environ.get("OPENAI_API_KEY", ""), os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), p) if os.environ.get("OPENAI_API_KEY") else "",
}


# who answers what: every topic goes to Gemini (the one key that works) plus one second model, so two opinions can be compared.
# Add a provider here once its key works; a provider with no key or a failing key is skipped and logged.
ROUTES = {
    "schools": ["gemini", "openai"],
    "scalp4h": ["gemini", "deepseek"],
    "risk": ["gemini", "deepseek"],
}


def run(topics=None, providers=None, log=print):
    OUT.mkdir(parents=True, exist_ok=True)
    done = []
    for t in topics or TOPICS:
        prompt = (CONTEXT + "\n\n" if CONTEXT else "") + TOPICS[t]
        for name in providers or ROUTES.get(t, list(PROVIDERS)):
            try:
                text = PROVIDERS[name](prompt)
            except Exception as e:  # one failing model must not stop the others
                log(f"{t} {name}: {type(e).__name__} {str(e)[:200]}")
                continue
            if not text:
                log(f"{t} {name}: no key set, skipped")
                continue
            f = OUT / f"{t}-{name}.md"
            f.write_text(f"# {t} - {name}\n\n_Model opinion, not evidence. Verify every source._\n\n{text}\n", encoding="utf-8")
            done.append(str(f.relative_to(ROOT)))
            log(f"saved {f.name}")
            time.sleep(2)
    (OUT / "index.json").write_text(json.dumps({"files": done, "built": int(time.time())}, indent=1), encoding="utf-8")
    return done


if __name__ == "__main__":
    run(sys.argv[1:] or None)
