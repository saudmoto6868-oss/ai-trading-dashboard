"""LIVE XCMD check against the real running platform (Streamlit iframe, real OKX data).
Run: python tests/browser/xcmd_live.py http://localhost:8599 OUT_DIR
Read + view + draw only. No orders, no logins."""
import json, sys, time
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
OUT = sys.argv[2] if len(sys.argv) > 2 else "."


def find_frame(page, timeout=90):
    """Return the iframe that exposes window.XCMD."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        for f in page.frames:
            try:
                if f.evaluate("typeof window.XCMD === 'object'"):
                    return f
            except Exception:
                pass
        time.sleep(1)
    return None


def main():
    res, errs = {}, []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_context(viewport={"width": 1600, "height": 950}).new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        pg.goto(URL, wait_until="domcontentloaded")
        fr = find_frame(pg)
        res["frame_found"] = bool(fr)
        if not fr:
            print(json.dumps(res)); b.close(); return 1
        time.sleep(8)  # let real candles load
        X = lambda js: fr.evaluate(js)
        res["state_fresh"] = X("XCMD.state()")
        if not X("XCMD.state().panels.some(p=>p.type==='chart')"):  # fresh profile = empty workspace
            res["addPanel_chart"] = X("XCMD.addPanel('chart')"); time.sleep(8)
        res["state"] = X("XCMD.state()")
        res["list"] = X("XCMD.list()")
        pg.screenshot(path=f"{OUT}/00_page.png")
        res["setTf"] = X("XCMD.setTf('1H')"); time.sleep(3)
        res["setSymbol"] = X("XCMD.setSymbol(XCMD.state().sym[1])"); time.sleep(5)
        last = X("XCMD.state().panels.find(p=>p.type==='chart').last")
        res["last_price"] = last
        res["toggle_on"] = X("XCMD.toggle('vwap', true)")
        res["draw_hline"] = X(f"XCMD.draw({{kind:'hline', price:{last or 0}, color:'#f0b90b', label:'live test'}})") if last else None
        res["draw_text"] = X(f"XCMD.draw({{kind:'text', price:{last or 0}, text:'xcmd live'}})") if last else None
        time.sleep(1)
        res["draws_in_state"] = X("XCMD.state().panels.find(p=>p.type==='chart').draws")
        pg.screenshot(path=f"{OUT}/01_after_draw.png")
        shot = X("XCMD.shot(1)")
        if shot.get("ok"):
            import base64
            open(f"{OUT}/02_xcmd_shot.png", "wb").write(base64.b64decode(shot["png"].split(",", 1)[1]))
            shot = {k: v for k, v in shot.items() if k != "png"}
        res["shot"] = shot
        res["toggle_off"] = X("XCMD.toggle('vwap', false)")
        res["clear"] = X("XCMD.clearDrawings()")
        res["refuse_web"] = X("XCMD.addPanel('web')")
        res["refuse_sym"] = X("XCMD.setSymbol('NOPE-USDT')")
        res["pageerrors"] = errs
        b.close()
    print(json.dumps(res, indent=1, ensure_ascii=False)[:6000])
    return 0


sys.exit(main())
