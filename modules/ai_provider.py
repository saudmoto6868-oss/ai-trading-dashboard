"""OpenAI (ChatGPT) JSON chat for the dashboard's AI features (owner 2026-10-23: ChatGPT takes the backtest analysis, the questions and the
assistant's text answers instead of Gemini). The key is read from OPENAI_API_KEY (environment or Streamlit secrets), never stored in a
file. With no OpenAI key every feature keeps using the free Gemini key, so nothing is spent unless the owner has set the key.

Voice is NOT moved here: the live voice character still runs on Gemini Live (OpenAI's realtime voice is a different, paid API and needs
the owner's approval); its text answers use whichever provider pick() returns.
Model: OPENAI_MODEL (default gpt-4o-mini); an unknown / retired name (404) tries the next one, and a model that wants
max_completion_tokens (and no temperature) is retried that way."""
from __future__ import annotations

import json
import os

URL = "https://api.openai.com/v1/chat/completions"
FALLBACK_MODELS = ("gpt-4o-mini", "gpt-4.1-mini")


def _cfg(name: str, default: str = "") -> str:
    v = os.environ.get(name, "")
    if not v:
        try:
            import streamlit as st
            v = str(st.secrets.get(name, "") or "")
        except Exception:
            v = ""
    return v or default


def openai_key() -> str:
    return _cfg("OPENAI_API_KEY")


def gemini_key() -> str:
    return _cfg("GEMINI_API_KEY") or _cfg("GOOGLE_API_KEY") or _cfg("GEMINI_KEY")


def pick() -> tuple[str, str]:
    """(provider, key): ChatGPT when its key is set, else the free Gemini key, else ('', '')."""
    want = _cfg("AI_PROVIDER").lower()
    ok, gk = openai_key(), gemini_key()
    if want == "gemini" and gk:
        return "gemini", gk
    if ok:
        return "openai", ok
    return ("gemini", gk) if gk else ("", "")


def describe(schema) -> str:
    """Gemini-style schema (OBJECT / STRING ...) -> compact lower-case JSON-schema text for the prompt."""
    def conv(x):
        if isinstance(x, dict):
            return {k: (str(v).lower() if k == "type" and isinstance(v, str) else conv(v)) for k, v in x.items()}
        if isinstance(x, list):
            return [conv(i) for i in x]
        return x
    return json.dumps(conv(schema), ensure_ascii=False, separators=(",", ":"))


def chat_json(system: str, messages: list, schema_text: str, key: str | None = None, model: str | None = None,
              timeout: int = 30, max_tokens: int = 1024) -> dict:
    """One ChatGPT turn that must answer with ONE JSON object (response_format json_object). messages = [{'role','content'}]."""
    import requests
    key = key or openai_key()
    if not key:
        raise RuntimeError("no OPENAI_API_KEY")
    sys_txt = system + "\n\nAnswer with ONE JSON object only, matching this schema (field names exactly): " + schema_text
    base = {"messages": [{"role": "system", "content": sys_txt}] + list(messages), "response_format": {"type": "json_object"}}
    r = None
    for m in dict.fromkeys([model or _cfg("OPENAI_MODEL", FALLBACK_MODELS[0])] + list(FALLBACK_MODELS)):
        body = dict(base, model=m, max_tokens=max_tokens, temperature=0.2)
        r = requests.post(URL, headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, json=body, timeout=timeout)
        if r.status_code == 400 and "max_completion_tokens" in r.text:   # newer / reasoning models
            body.pop("max_tokens"); body.pop("temperature", None); body["max_completion_tokens"] = max_tokens
            r = requests.post(URL, headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, json=body, timeout=timeout)
        if r.status_code not in (404,) and not (r.status_code == 400 and "model" in r.text.lower() and "not" in r.text.lower()):
            break
    r.raise_for_status()
    content = ((r.json().get("choices") or [{}])[0].get("message") or {}).get("content") or "{}"
    try:
        out = json.loads(content)
    except ValueError:
        out = {}
    return out if isinstance(out, dict) else {}
