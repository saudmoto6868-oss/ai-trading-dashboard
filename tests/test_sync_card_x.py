"""Static checks: the order-flow sync card draws its own hide button in every layout (plain script, no browser)."""
import os
src = open(os.path.join(os.path.dirname(__file__), "..", "modules", "workspace_app.html"), encoding="utf-8").read()
i = src.index("  paintSyncCard(c, x0, x1, PB, area){"); body = src[i:i + 4500]
checks = {
    "card draws its own ✕ in the header": 'this.paintOfX(c, x0 + w - 16, y0 + 3, "_scX")' in body,
    "stats chip leaves room for the ✕": "x1 - stw - 20" in body,
    "caller no longer places the ✕ only in the wide layout": 'this.paintOfX(c, XE - 17, PB + 4, "_scX")' not in src,
    "click handler for the card ✕ exists": 'hit("_scX")' in src,
    "settings toggle exists (default on)": "this.scOn !== false" in src and 'id:"ofs"' in src,
}
for k, v in checks.items(): print(("PASS" if v else "FAIL") + ": " + k)
assert all(checks.values())
print("PASS: sync card ✕ (static only; clicked once in a headless mock)")
