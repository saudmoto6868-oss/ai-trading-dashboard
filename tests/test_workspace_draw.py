"""The Workspace drawing tools must not depend on browser dialogs (prompt / alert are blocked inside the Streamlit page frame, so the text tool did nothing),
and the in-chart settings editor must be wired: gear button, double-click, text tool."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf-8").read()


def test_no_blocking_dialogs_in_drawing_code():
    assert "window.prompt" not in H and not re.search(r"(?<![\w.])prompt\(", H), "prompt() is blocked in the page frame"


def test_editor_is_wired():
    assert "openEditor(d)" in H and "closeEditor()" in H
    assert 'add("⚙"' in H                                                       # gear button on the selection bar
    assert 'addEventListener("dblclick", e =>' in H and "this.openEditor(d)" in H  # double-click a drawing
    assert 'this.openEditor(d); return true; }' in H                             # the text tool opens the editor instead of a prompt
    for k in ("dashOf(d)", "fillOf(d", "d.extL", "d.noLbl", "d.fs", "d.tc"):    # the new style fields are read by the painter
        assert k in H, k


def test_tradingview_tool_set():
    for k in ("ellipse", "triangle", "pitchfork", "callout", "plabel", "arrup", "arrdn", "flag", "cross", "info", "extline"):
        assert f'["{k}",' in H, k                                                  # the tool button exists
        assert f'd.type === "{k}"' in H or k in ("info", "extline"), k              # and has a painter / hit test
    assert "press, drag and release also draws" in H                                  # drag-to-draw like TradingView, besides click-click
    assert "cgrip(d, hs)" in H and "this.catBtns" in H                              # centre grip to move a drawing, categories with headings


def test_chart_is_free_by_default():
    assert 'getItem("ai_ac") === "1"' in H                                          # 2026-10-24: auto-centre is OFF unless the user turned it on (it undid every zoom / pan on each live tick)
    assert "freezeY(){" in H                                                        # vertical drag / Shift+wheel switches the price scale to manual


def test_symbol_logos_in_the_workspace():
    assert "function symIcon(sym, px)" in H and "symIcon(s, 13)" in H and "symIcon(this.state.sym, 14)" in H   # logos in the watch list rows and in the panel titles


def test_page_script_parses():
    import shutil, subprocess
    node = shutil.which("node")
    if not node:
        return                                                                       # no node here: skipped
    js = "\n".join(re.findall(r"<script[^>]*>([\s\S]*?)</script>", H.replace("__CONFIG__", "{}")))
    r = subprocess.run([node, "-e", "try{new Function(require('fs').readFileSync(0,'utf8'))}catch(e){console.log('ERR '+e.message);process.exit(1)}"], input=js.encode("utf-8"), capture_output=True)
    assert r.returncode == 0, r.stdout.decode("utf-8", "replace")


def test_two_tabs_do_not_freeze_the_chart():
    assert "new AbortController()" in H and 'throw new Error("OKX timeout")' in H     # a request with no answer is abandoned, the polling loop goes on
    assert 'localStorage.getItem("okx_cool_all")' in H                                # the rate-limit pause is shared by the tabs of one browser
    assert 'addEventListener("visibilitychange", wake)' in H and "p.kick()" in H      # a tab that comes back restarts its charts


if __name__ == "__main__":
    test_no_blocking_dialogs_in_drawing_code(); test_editor_is_wired(); test_tradingview_tool_set(); test_chart_opens_centred(); test_symbol_logos_in_the_workspace(); test_page_script_parses(); test_two_tabs_do_not_freeze_the_chart(); print("ok workspace draw")
