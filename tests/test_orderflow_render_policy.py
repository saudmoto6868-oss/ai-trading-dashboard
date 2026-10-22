"""Regression checks for Order Flow rendering staying outside candle bodies.

Static source assertions only; browser/canvas behavior still requires Playwright.
Run with: python tests/test_orderflow_render_policy.py
"""
from pathlib import Path

source = (Path(__file__).resolve().parents[1] / "modules" / "workspace_app.html").read_text(encoding="utf-8")

checks = {
    "DOM heat fallback over candles removed": "if (this.domOn && !this.colOn) this.paintDom" not in source,
    "bubble fallback over candles removed": "if (this.bubOn && !this.colOn) this.paintBub" not in source,
    "DOM balance paint gated by dedicated column": "if (this.domOn && this.colOn) this.paintBal(c, PB, PR);" in source,
    "combined Order Flow toggle enables column": 'if (v) c_.colOn = true; Object.assign(this.state, {bub:v, dot:v, dom:v, mk:v, col:v ? true : this.state.col});' in source,
    "bubble toggle enables column": 'c_.bubOn = v; if (v) c_.colOn = true; this.state.bub = v; if (v) this.state.col = true;' in source,
    "DOM toggle enables column": 'c_.domOn = v; if (v) c_.colOn = true; this.state.dom = v; if (v) this.state.col = true;' in source,
}
failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
if failed:
    raise SystemExit(1)
print("PASS: static Order Flow render policy checks (no browser test performed).")
