"""Static checks for the Limits (order-book events) table style (plain script, no browser)."""
import os
src = open(os.path.join(os.path.dirname(__file__), "..", "modules", "workspace_app.html"), encoding="utf-8").read()
i = src.index("function renderEvents(panel, evAll){"); body = src[i:i + 3400]
checks = {
    "legend line above the table": 'class="evl"' in body,
    "no tinted row background": "background:rgba('+rgb[" not in body,
    "no bold coloured event text": "font-weight:700" not in body,
    "short event labels with a glyph": 'nm = {PLACED:"NEW", PULLED:"PULL", FILLED:"FILL", ABSORB:"ABS"}' in body,
    "flash only on rows younger than 1.5 s": "now-e.t < 1500" in body,
    "soft flash defined": ".evf{animation:evfl 1s" in src,
}
for k, v in checks.items(): print(("PASS" if v else "FAIL") + ": " + k)
assert all(checks.values())
print("PASS: limits table style (static only; look checked once by a headless screenshot with fake events)")
