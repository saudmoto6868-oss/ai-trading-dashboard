"""Central configuration. Everything tunable lives here or in environment variables."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_env_file(path: Path) -> None:
    """Read KEY=VALUE lines from ai-desk/.env (git-ignored). Real environment variables win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env_file(ROOT / ".env")
DATA_DIR = Path(os.getenv("DESK_DATA_DIR", ROOT / ".desk_data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# "live" = try real free sources, fall back to demo data per source if they fail.
# "demo" = synthetic data only (offline, for testing the UI and the pipeline).
DATA_MODE = os.getenv("DESK_DATA_MODE", "live").lower()

# ---- LLM (optional). Any OpenAI-compatible endpoint works:
#   LiteLLM proxy  : http://localhost:4000/v1
#   OpenRouter     : https://openrouter.ai/api/v1
#   Ollama (local) : http://localhost:11434/v1
#   DeepSeek       : https://api.deepseek.com/v1
#   Anthropic      : https://api.anthropic.com/v1/  (OpenAI-compatible endpoint)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60"))

# ---- Free models first. Put the key in your own .env, never in a chat or in the repo.
#   GEMINI_API_KEY : free key from https://aistudio.google.com/apikey . If it is set and
#                    LLM_BASE_URL is empty, the desk uses Gemini's OpenAI-compatible endpoint.
#   LLM_FALLBACKS  : JSON list tried in order when the main model is rate-limited or down,
#                    free first and paid last. key_env names the variable holding that key:
#     LLM_FALLBACKS='[{"base_url": "http://localhost:11434/v1", "model": "qwen2.5:14b"},
#                     {"base_url": "https://openrouter.ai/api/v1", "model": "deepseek/deepseek-chat", "key_env": "OPENROUTER_API_KEY"}]'
import json as _json  # noqa: E402

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not LLM_BASE_URL and GEMINI_API_KEY:
    LLM_BASE_URL, LLM_API_KEY = GEMINI_BASE_URL, GEMINI_API_KEY
    LLM_MODEL = LLM_MODEL or "gemini-2.5-flash"
LLM_FALLBACKS: list = _json.loads(os.getenv("LLM_FALLBACKS", "[]") or "[]")
if GEMINI_API_KEY and not LLM_FALLBACKS and LLM_BASE_URL == GEMINI_BASE_URL:
    # free tier limits are per model, so the other free Gemini models carry on when one is rate-limited
    LLM_FALLBACKS = [{"base_url": GEMINI_BASE_URL, "model": m, "key_env": "GEMINI_API_KEY"}
                     for m in ("gemini-2.5-flash-lite", "gemini-2.0-flash") if m != LLM_MODEL]
# Calls per minute across the whole app (0 = no limit). Free Gemini allows ~10 RPM per model: the agent
# floor runs many agents in parallel, so calls are spaced instead of failing with 429.
LLM_RPM = float(os.getenv("LLM_RPM", "12" if LLM_BASE_URL == GEMINI_BASE_URL else "0"))
LLM_RETRIES = int(os.getenv("LLM_RETRIES", "2"))          # same provider, on 429/5xx, with backoff
LLM_MAX_WAIT = float(os.getenv("LLM_MAX_WAIT", "20"))     # seconds, cap on one backoff wait
# Extra body fields per provider host. Gemini 2.5 "thinks" inside max_tokens, so keep it low.
LLM_EXTRA: dict = _json.loads(os.getenv("LLM_EXTRA", "{}") or "{}") or {
    "generativelanguage.googleapis.com": {"reasoning_effort": "low"}}

# One-click presets shown in Settings (no keys here).
LLM_PRESETS = [
    {"id": "gemini", "name": "Gemini (مجاني)", "base_url": GEMINI_BASE_URL, "model": "gemini-2.5-flash",
     "light_model": "gemini-2.5-flash-lite", "key_url": "https://aistudio.google.com/apikey"},
    {"id": "ollama", "name": "Ollama على جهازك (مجاني)", "base_url": "http://localhost:11434/v1", "model": "qwen2.5:14b"},
    {"id": "openrouter", "name": "OpenRouter", "base_url": "https://openrouter.ai/api/v1", "model": "deepseek/deepseek-chat"},
]

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF"]

# Markets the desk scans. kind: fx | metal | index
UNIVERSE = {
    "EURUSD": {"kind": "fx", "base": "EUR", "quote": "USD", "yf": "EURUSD=X"},
    "GBPUSD": {"kind": "fx", "base": "GBP", "quote": "USD", "yf": "GBPUSD=X"},
    "USDJPY": {"kind": "fx", "base": "USD", "quote": "JPY", "yf": "USDJPY=X"},
    "AUDUSD": {"kind": "fx", "base": "AUD", "quote": "USD", "yf": "AUDUSD=X"},
    "NZDUSD": {"kind": "fx", "base": "NZD", "quote": "USD", "yf": "NZDUSD=X"},
    "USDCAD": {"kind": "fx", "base": "USD", "quote": "CAD", "yf": "USDCAD=X"},
    "USDCHF": {"kind": "fx", "base": "USD", "quote": "CHF", "yf": "USDCHF=X"},
    "EURJPY": {"kind": "fx", "base": "EUR", "quote": "JPY", "yf": "EURJPY=X"},
    "GBPJPY": {"kind": "fx", "base": "GBP", "quote": "JPY", "yf": "GBPJPY=X"},
    "AUDJPY": {"kind": "fx", "base": "AUD", "quote": "JPY", "yf": "AUDJPY=X"},
    "EURGBP": {"kind": "fx", "base": "EUR", "quote": "GBP", "yf": "EURGBP=X"},
    "XAUUSD": {"kind": "metal", "base": "XAU", "quote": "USD", "yf": "GC=F"},
    "SPX": {"kind": "index", "base": "SPX", "quote": "USD", "yf": "^GSPC"},
    "NDX": {"kind": "index", "base": "NDX", "quote": "USD", "yf": "^NDX"},
    "XAGUSD": {"kind": "metal", "base": "XAG", "quote": "USD", "yf": "SI=F"},
    "BTCUSD": {"kind": "crypto", "base": "BTC", "quote": "USD", "yf": "BTC-USD", "binance": "BTCUSDT"},
    "ETHUSD": {"kind": "crypto", "base": "ETH", "quote": "USD", "yf": "ETH-USD", "binance": "ETHUSDT"},
}

# Contract size per 1.0 lot, used by the position-size calculator (CFD conventions; check your broker).
CONTRACT = {"fx": 100_000, "XAU": 100, "XAG": 5_000, "SPX": 1, "NDX": 1, "BTC": 1, "ETH": 1}

# Intermarket / SMT pairs: (A, B, correlation sign). DXY is a yfinance ticker, the rest are UNIVERSE keys.
SMT_PAIRS = [("EURUSD", "GBPUSD", 1), ("SPX", "NDX", 1), ("XAUUSD", "XAGUSD", 1),
             ("BTCUSD", "ETHUSD", 1), ("EURUSD", "DXY", -1)]

# Watchlist engine (from Saud's AI Trading Desk framework): a market is promoted once it
# collects WATCH_MIN_REASONS independent reasons from at least 2 departments.
WATCH_MIN_REASONS = 3
NEWS_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")  # optional: news sentiment (free key, 25 calls/day)

# All 28 crosses of the 8 majors, used for currency strength (yfinance tickers).
def all_fx_pairs() -> list[tuple[str, str]]:
    order = ["EUR", "GBP", "AUD", "NZD", "USD", "CAD", "CHF", "JPY"]  # market convention
    return [(a, b) for i, a in enumerate(order) for b in order[i + 1:]]

# Cross-asset tickers for the risk regime.
REGIME_TICKERS = {
    "VIX": "^VIX",
    "SPX": "^GSPC",
    "AUDJPY": "AUDJPY=X",
    "GOLD": "GC=F",
    "US10Y": "^TNX",
    "DXY": "DX-Y.NYB",
}

# CFTC Legacy Futures-Only contract codes (cftc_contract_market_code).
COT_CODES = {
    "EUR": "099741",
    "GBP": "096742",
    "JPY": "097741",
    "AUD": "232741",
    "NZD": "112741",
    "CAD": "090741",
    "CHF": "092741",
    "USD": "098662",  # ICE US Dollar Index
    "XAU": "088691",  # COMEX gold
    "SPX": "13874A",  # E-mini S&P 500
    "NDX": "209742",  # E-mini Nasdaq-100
    "XAG": "084691",  # COMEX silver
    "BTC": "133741",  # CME Bitcoin
    "ETH": "146021",  # CME Ether
}

# OECD 3-month interbank rates on FRED (monthly). Used for rate differentials.
FRED_RATE_SERIES = {
    "USD": "IR3TIB01USM156N",
    "EUR": "IR3TIB01EZM156N",
    "GBP": "IR3TIB01GBM156N",
    "JPY": "IR3TIB01JPM156N",
    "AUD": "IR3TIB01AUM156N",
    "NZD": "IR3TIB01NZM156N",
    "CAD": "IR3TIB01CAM156N",
    "CHF": "IR3TIB01CHM156N",
}

# Smart-bias weights. Starting point taken from the published KairosBias split
# (EMA 32 / COT 27 / momentum 18 / rates 13 / seasonality 10). Tune with the journal.
BIAS_WEIGHTS = {"trend": 0.32, "cot": 0.27, "momentum": 0.18, "rates": 0.13, "seasonality": 0.10}

# Deterministic decision gate. The LLM can never override these.
GATE = {
    "min_bias": 0.30,          # |bias| needed before timing tools are opened
    "min_room_r": 2.0,         # room (in R) before the nearest opposing swing; <1R blocks, <2R is a doubt
    "event_block_hours": 12,   # high-impact event on either currency inside this window -> wait
    "max_ideas": 5,
}

SCAN_INTERVAL_MIN = int(os.getenv("DESK_SCAN_INTERVAL_MIN", "15"))

# ---- Agents (OmniDesk structure). One model per agent is optional, e.g. through LiteLLM:
#   AGENT_MODELS='{"ict": "claude-sonnet", "macro": "deepseek-chat", "auditor": "claude-opus"}'
AGENT_MODELS: dict = _json.loads(os.getenv("AGENT_MODELS", "{}") or "{}")
AGENT_CONCURRENCY = int(os.getenv("AGENT_CONCURRENCY", "6"))
AGENT_MAX_CANDIDATES = int(os.getenv("AGENT_MAX_CANDIDATES", "3"))
