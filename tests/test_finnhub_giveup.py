"""Finnhub socket: a handshake the browser cannot explain (wrong or blocked token) must not be retried forever. Wiring check; the behaviour was simulated in node."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf-8").read()


def test_giveup_wiring():
    for k in ("const FH_GIVEUP = 4;", "let opened = false;", "opened = true; this.fails = 0;", "if (!opened && ++this.fails >= FH_GIVEUP){ this.state = \"refused\"; return; }",
              "this.state !== \"off\" && this.state !== \"refused\"", "FH.state === \"refused\""):
        assert k in H, k


if __name__ == "__main__":
    test_giveup_wiring()
    print("ok finnhub giveup")
