"""XPiX platform tool for Jarvis (OpenClaw agent 'main', Telegram account xpix77bot). Read + view + draw only. No orders, no logins.
Jarvis runs it and sends the printed PNG path back to the owner as a photo.
  python scripts/xpix_ctl.py shot [SYMBOL] [TF]    -> prints PNG path
  python scripts/xpix_ctl.py today SYMBOL          -> prints PNG path + short text (cached 1h)
  python scripts/xpix_ctl.py signals | alerts      -> text from the signal log
  python scripts/xpix_ctl.py state                 -> symbols / panels / last price (JSON)
Env: XPIX_URL (default http://localhost:8501), XPIX_PROFILE (Chromium profile dir)."""
import json, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import xpix_bot as b
from playwright.sync_api import sync_playwright

CACHE = pathlib.Path("/tmp/xpix_ctl_cache.json")


def main(a):
    if not a:
        sys.exit(__doc__)
    c = a[0]
    if c in ("signals", "alerts"):
        return print(b.cmd_signals(c == "alerts"))
    if c == "today" and CACHE.exists():            # same symbol is not re-analysed within the hour
        k = json.loads(CACHE.read_text()).get((a[1] if len(a) > 1 else "BTC").upper())
        if k and time.time() - k["t"] < b.CACHE_S:
            return print(k["png"], "\n" + k["txt"], "\n(cached)")
    with sync_playwright() as pw:
        p = b.Platform(pw)
        if c == "state":
            return print(json.dumps(p.x("XCMD.state()"), ensure_ascii=False))
        if c == "shot":
            sym = p.sym(a[1]) if len(a) > 1 else None
            if len(a) > 1 and not sym:
                sys.exit("unknown symbol")
            png, err = p.shot(sym, a[2] if len(a) > 2 else None, "/tmp/xpix_shot.png")
            return print(png or "error: " + err)
        if c == "today":
            png, txt = b.cmd_today(p, a[1] if len(a) > 1 else "BTC")
            if png:
                d = json.loads(CACHE.read_text()) if CACHE.exists() else {}
                d[(a[1] if len(a) > 1 else "BTC").upper()] = {"t": time.time(), "png": png, "txt": txt}
                CACHE.write_text(json.dumps(d))
            return print(png or "error", "\n" + txt)
    sys.exit("unknown command")


main(sys.argv[1:])
