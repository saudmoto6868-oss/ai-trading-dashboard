"""Provider-agnostic LLM client (OpenAI-compatible chat/completions).

Point LLM_BASE_URL at LiteLLM / OpenRouter / Ollama / DeepSeek / Anthropic's OpenAI-compatible
endpoint and every provider works the same way. If nothing is configured, `available()` is
False and the desk falls back to rule-based Arabic narration.
"""
from __future__ import annotations

import json
import logging
import os
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import threading

import requests

from .. import config

log = logging.getLogger("desk.llm")
SKILLS_DIR = Path(__file__).parent / "skills"


RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}
USAGE: Counter = Counter()   # successful calls per provider, shown in the UI


def providers(model: str | None = None) -> list[dict]:
    """Main model first, then LLM_FALLBACKS in order (free first, paid last)."""
    out = []
    if config.LLM_BASE_URL and (model or config.LLM_MODEL):
        out.append({"name": model or config.LLM_MODEL, "base_url": config.LLM_BASE_URL,
                    "model": model or config.LLM_MODEL, "key": config.LLM_API_KEY})
    for f in config.LLM_FALLBACKS:
        if f.get("base_url") and f.get("model"):
            out.append({"name": f.get("name") or f["model"], "base_url": f["base_url"], "model": f["model"],
                        "key": os.getenv(f["key_env"], "") if f.get("key_env") else ""})
    return out


def available() -> bool:
    return bool(providers())


def _extra(base_url: str) -> dict:
    return config.LLM_EXTRA.get(urlparse(base_url).hostname or "", {})


_pace_lock = threading.Lock()
_next_slot = [0.0]


def _pace() -> None:
    """Space calls to config.LLM_RPM per minute across all threads (free tiers reject bursts with 429)."""
    if config.LLM_RPM <= 0:
        return
    gap = 60.0 / config.LLM_RPM
    with _pace_lock:
        now = time.monotonic()
        slot = max(now, _next_slot[0])
        _next_slot[0] = slot + gap
    if slot > now:
        time.sleep(slot - now)


def _complete(body: dict, model: str | None = None) -> dict:
    """POST chat/completions down the provider chain. A 429/5xx is retried on the same provider
    with backoff (Retry-After when given); any other failure moves to the next provider."""
    errors = []
    for p in providers(model):
        b = dict(body, model=p["model"], **_extra(p["base_url"]))
        headers = {"Content-Type": "application/json"}
        if p["key"]:
            headers["Authorization"] = f"Bearer {p['key']}"
        url = p["base_url"].rstrip("/") + "/chat/completions"
        for attempt in range(config.LLM_RETRIES + 1):
            _pace()
            try:
                r = requests.post(url, headers=headers, data=json.dumps(b), timeout=config.LLM_TIMEOUT)
            except requests.RequestException as e:
                errors.append(f"{p['name']}: {e.__class__.__name__}")
                break
            if r.status_code == 400 and _extra(p["base_url"]) and attempt == 0:
                b = dict(body, model=p["model"])  # provider rejected an extra field: try plain
                continue
            if r.status_code in RETRY_STATUS and attempt < config.LLM_RETRIES:
                try:
                    wait = float(r.headers.get("Retry-After", ""))
                except ValueError:
                    wait = 2.0 * (attempt + 1)
                time.sleep(min(max(wait, 0.5), config.LLM_MAX_WAIT))
                continue
            if r.status_code >= 400:
                errors.append(f"{p['name']}: HTTP {r.status_code}")
                break
            try:
                msg = r.json()["choices"][0]["message"]
            except Exception:
                errors.append(f"{p['name']}: bad response")
                break
            USAGE[p["name"]] += 1
            return msg
        else:
            errors.append(f"{p['name']}: HTTP {r.status_code} بعد {config.LLM_RETRIES + 1} محاولات")
    raise RuntimeError("كل النماذج فشلت: " + "؛ ".join(errors or ["لا يوجد نموذج مضبوط"]))


def skills_text(names: list[str] | None = None) -> str:
    parts = []
    for p in sorted(SKILLS_DIR.glob("*.md")):
        if names is None or p.stem in names:
            parts.append(p.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


SYSTEM = """أنت "رئيس المكتب" في مكتب تداول ماكرو. تعمل بالعربية.
قواعدك:
- لا تخترع أرقاماً. استخدم فقط الأرقام الموجودة في البيانات المرسلة إليك.
- البيانات المعلّمة بـ demo اصطناعية: قل ذلك صراحة ولا تبنِ عليها قراراً.
- القرار النهائي تتخذه بوابة قواعد ثابتة، ودورك الشرح: ما الذي يجب أن ينظر إليه المتداول، ولماذا، وما الذي يبطل الفكرة.
- لا تنفذ صفقات. كل الأفكار ورقية.
- اكتب باختصار: 3 إلى 6 أسطر لكل مرحلة."""


def chat(messages: list[dict], max_tokens: int = 600, skills: list[str] | None = None) -> str | None:
    if not available():
        return None
    sys = SYSTEM + "\n\nمرجع المدارس:\n" + skills_text(skills)
    body = {"messages": [{"role": "system", "content": sys}] + messages,
            "max_tokens": max_tokens, "temperature": 0.3}
    try:
        return (_complete(body).get("content") or "").strip() or None
    except Exception as e:
        log.warning("LLM call failed: %s", e)
        return None


def chat_tools(messages: list[dict], tools: list[dict] | None = None, model: str | None = None,
               max_tokens: int = 1200, temperature: float = 0.2) -> dict:
    """One OpenAI-compatible chat/completions call with function calling. Returns the
    assistant message dict ({content, tool_calls}). Raises on failure so the agent can show it."""
    body = {"messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    msg = _complete(body, model)
    return {"content": msg.get("content") or "", "tool_calls": msg.get("tool_calls") or []}
