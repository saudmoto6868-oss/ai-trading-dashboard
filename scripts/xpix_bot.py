"""XPiX Telegram bot: a CHANNEL between the owner's Telegram group and Claude Code on the Mac (docs/XPIX_BOT_BRIEF.md).

Read + view + draw only. No orders, no trading, no broker/TradingView logins, no keys in code.
  XPIX_BOT_TOKEN      bot token (own bot, NOT Hermes). Env only, Mac only.
  XPIX_OWNER_CHAT_ID  the only chat the bot answers; every other chat is ignored silently.
  XPIX_URL            platform URL (default http://localhost:8501)
  XPIX_PROFILE        Chromium profile dir (default ~/.xpix_bot_profile) - keeps the layout/drawings between runs
Run: python scripts/xpix_bot.py
Commands: /plan | /smt | /help | /shot SYMBOL TF | /today SYMBOL | /signals | /alerts | /deep <text> (Opus) | any other text -> Claude Code (Sonnet, read-only tools).
Spot desk (modules/spot_query.py, needs SPOT_GH_TOKEN + SPOT_GH_REPO in the env): /spot | /inv <no / shop / date> | /find <text> | /spotalerts | /spotxl
HONESTY: nothing here has been run against Telegram unless the owner says so; the XCMD part was tested live (tests/browser/xcmd_live.py)."""
import os, subprocess, sys, time, json, pathlib
import requests
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
TOKEN = os.environ.get("XPIX_BOT_TOKEN", "")
OWNER = os.environ.get("XPIX_OWNER_CHAT_ID", "")
URL = os.environ.get("XPIX_URL", "http://localhost:8501")
PROFILE = os.path.expanduser(os.environ.get("XPIX_PROFILE", "~/.xpix_bot_profile"))
API = f"https://api.telegram.org/bot{TOKEN}"
CACHE_S = 3600          # same symbol+tf is not re-analysed within the hour
RULES = ("You are the brain of the XPiX Telegram channel. READ-ONLY: never place/suggest executing orders, never touch broker, "
         "TradingView or any credentials, never write keys. Never invent prices. Say 'mock-tested only' if untested live and "
         "'n<30 is not evidence'. Answer briefly in the owner's language.")
_cache = {}


def tg(method, **kw):
    r = requests.post(f"{API}/{method}", timeout=70, **kw)
    return r.json()


def say(text, html=False):
    d = {"chat_id": OWNER, "text": text[:4000]}
    if html:
        d["parse_mode"] = "HTML"
        d["disable_web_page_preview"] = True
    tg("sendMessage", data=d)


def send_doc(name, data, caption=""):
    tg("sendDocument", data={"chat_id": OWNER, "caption": caption[:900]}, files={"document": (name, data)})


def send_photo(path, caption=""):
    with open(path, "rb") as f:
        tg("sendPhoto", data={"chat_id": OWNER, "caption": caption[:900]}, files={"photo": f})


class Platform:
    """Chromium + the platform iframe that exposes window.XCMD."""
    def __init__(self, pw):
        self.ctx = pw.chromium.launch_persistent_context(PROFILE, headless=True, viewport={"width": 1600, "height": 950})
        self.page = self.ctx.pages[0] if self.ctx.pages else self.ctx.new_page()
        self.page.goto(URL, wait_until="domcontentloaded")
        self.frame = self._find(90)
        if not self.frame:
            raise RuntimeError("XCMD iframe not found - is the platform running at " + URL + " ?")
        time.sleep(6)
        if not self.x("XCMD.state().panels.some(p=>p.type==='chart')"):   # fresh profile = empty workspace
            self.x("XCMD.addPanel('chart')"); time.sleep(6)

    def _find(self, timeout):
        t0 = time.time()
        while time.time() - t0 < timeout:
            for f in self.page.frames:
                try:
                    if f.evaluate("typeof window.XCMD === 'object'"):
                        return f
                except Exception:
                    pass
            time.sleep(1)

    def x(self, js):
        try:
            return self.frame.evaluate(js)
        except Exception:                       # Streamlit re-render replaced the iframe: find it again
            self.frame = self._find(30)
            return self.frame.evaluate(js)

    def sym(self, s):
        s = s.upper()
        syms = self.x("XCMD.state().sym")
        for c in (s, s + "-USDT"):
            if c in syms:
                return c

    def shot(self, sym=None, tf=None, out="/tmp/xpix_shot.png"):
        if sym:
            r = self.x(f"XCMD.setSymbol({json.dumps(sym)})")
            if not r["ok"]:
                return None, r["err"]
        if tf:
            r = self.x(f"XCMD.setTf({json.dumps(tf)})")
            if not r["ok"]:
                return None, r["err"]
        time.sleep(5)                            # let candles load
        self.page.screenshot(path=out)
        return out, None


def cmd_signals(alerts_only=False):
    from modules import signal_log
    recs = signal_log.load()
    if not recs:
        return "No logged signals on this Mac (.signal_log.jsonl missing/empty). Nothing to report."
    if alerts_only:
        last = sorted(recs, key=lambda r: r.get("t", 0))[-8:]
        return "Latest logged alerts:\n" + "\n".join(f"{time.strftime('%m-%d %H:%M', time.gmtime(r['t']))} {r['symbol']} {r['dir']} {r['tf']} {r.get('out', 'open')}" for r in last)
    return signal_log.format_stats(signal_log.stats(recs))


def cmd_today(p, s):
    sym = p.sym(s)
    if not sym:
        return None, "unknown symbol"
    key = ("today", sym)
    if key in _cache and time.time() - _cache[key][0] < CACHE_S:
        return _cache[key][1]
    png, err = p.shot(sym, "1H", "/tmp/xpix_today.png")
    if err:
        return None, err
    st = p.x("XCMD.state()")["panels"]
    ch = next((q for q in st if q["type"] == "chart"), {})
    from modules import signal_log
    day = [r for r in signal_log.load() if r.get("symbol", "").startswith(sym.split("-")[0]) and time.time() - r.get("t", 0) < 86400]
    txt = (f"{sym} 1H | last {ch.get('last')} | {ch.get('bars')} bars loaded\n"
           f"Logged signals in last 24h: {len(day)}" + ("" if day else " (none)") + "\n"
           "Chart only, no trade advice. n<30 is not evidence.")
    _cache[key] = (time.time(), (png, txt))
    return _cache[key][1]


def cmd_plan(a):
    """/plan [scalp|conf] [5m|15m|1h] [SYMBOL ...] : today's trades by timeframe confluence (standard) or a scalp on one timeframe (modules/day_plan.py)."""
    from modules import day_plan as D
    from modules.market_cache import get_klines
    mode, trig, syms = "conf", None, []
    for x in a:
        lx = x.lower()
        if lx in ("scalp", "conf"):
            mode = lx
        elif lx in ("5m", "15m", "1h"):
            trig = (lx,)
        else:
            syms.append(x.upper() if "-" in x or ":" in x else x.upper() + "-USDT")
    syms = syms or [x for x in os.environ.get("DAY_SYMBOLS", "BTC-USDT,ETH-USDT,SOL-USDT,HL:xyz:GOLD,HL:xyz:SILVER,HL:xyz:SP500,HL:xyz:XYZ100,HL:xyz:CL,Y:EURUSD=X,Y:GBPUSD=X").split(",") if x]
    plans = D.scan(syms, lambda s_, t_: get_klines(s_, t_, 300), mode=mode, trigger_tfs=trig)
    return D.format_telegram(plans, ar=True)


def cmd_smt():
    """/smt : SMT between the correlated pairs right now (modules/intermarket.py)."""
    from modules import intermarket as IM
    from modules.market_cache import get_klines
    ev = IM.scan_pairs(lambda s_, t_: get_klines(s_, t_, 300))
    if not ev:
        return "No clear SMT between the correlated pairs right now."
    return "SMT now:\n" + "\n".join(f"• {c['label']} · {c['session']} · {c['bars_ago']} bars" for c in IM.chips(ev, ar=False, limit=15))


def ask_claude(text, deep=False):
    cmd = ["claude", "-p", text, "--model", "opus" if deep else "sonnet", "--allowedTools", "Read,Grep,Glob",
           "--append-system-prompt", RULES]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
        return (r.stdout or r.stderr or "(no answer)").strip()
    except Exception as e:
        return f"Claude Code call failed: {e}"


def handle(p, text):
    a = text.strip().split()
    c = a[0].lower().split("@")[0] if a else ""
    if c in ("/spot", "/inv", "/find", "/spotalerts", "/spotxl"):   # spot desk ledger (read-only)
        from modules import spot_query
        reply, files = spot_query.handle(text)
        say(reply)
        for name, data in files:
            send_doc(name, data)
        return None
    if c == "/shot":
        sym = p.sym(a[1]) if len(a) > 1 else None
        if len(a) > 1 and not sym:
            return say("unknown symbol")
        png, err = p.shot(sym, a[2] if len(a) > 2 else None)
        return send_photo(png, f"{sym or ''} {a[2] if len(a) > 2 else ''} live platform shot") if png else say(err)
    if c == "/today":
        r = cmd_today(p, a[1] if len(a) > 1 else "BTC")
        return (send_photo(r[0], r[1]) if r[0] else say(r[1]))
    if c == "/plan":
        return say(cmd_plan(a[1:]), html=True)
    if c == "/smt":
        return say(cmd_smt())
    if c in ("/help", "/start"):
        return say("/plan [scalp|conf] [5m|15m|1h] [SYMBOL...] day plan · /smt intermarket SMT · /shot SYMBOL TF · /today SYMBOL · /signals · /alerts · /deep <text> · any other text = ask Claude (read-only).")
    if c == "/signals":
        return say(cmd_signals())
    if c == "/alerts":
        return say(cmd_signals(True))
    if c == "/deep":
        return say(ask_claude(" ".join(a[1:]), deep=True))
    return say(ask_claude(text))


def main():
    if not TOKEN or not OWNER:
        sys.exit("Set XPIX_BOT_TOKEN and XPIX_OWNER_CHAT_ID in the environment (never in the repo).")
    with sync_playwright() as pw:
        p = Platform(pw)
        off = 0
        while True:
            try:
                for u in tg("getUpdates", params={"timeout": 50, "offset": off}).get("result", []):
                    off = u["update_id"] + 1
                    m = u.get("message") or {}
                    if str(m.get("chat", {}).get("id")) != str(OWNER) or not m.get("text"):
                        continue                     # any other chat is ignored
                    try:
                        handle(p, m["text"])
                    except Exception as e:
                        say(f"error: {str(e)[:300]}")
            except requests.RequestException:
                time.sleep(5)


if __name__ == "__main__":
    main()
