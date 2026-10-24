"""Static checks for the cross-tab OKX cooldown policy in workspace_app.html (plain script, no browser).
The browser check lives in tests/browser/okx_two_tabs_mock.js (mock only)."""
import os, re
src = open(os.path.join(os.path.dirname(__file__), "..", "modules", "workspace_app.html"), encoding="utf-8").read()
i = src.index("function okx(path){"); body = src[i:i + 4200]
checks = {
    "live refresh polls are classified": "liveTick" in body and "limit=(?:[1-9]|[1-3]\\d|40)" in body,
    "shared cross-tab pause is skipped for live polls": "liveTick ? 0 : shared" in body,
    "far-future shared pause is ignored": "shared > Date.now() + 20000" in body,
    "shared pause is not extended while still active": 'getItem("okx_cool_all") || 0)) < Date.now()' in body,
    "429 pause has jitter": "Math.random()*7000" in body,
}
for k, v in checks.items(): print(("PASS" if v else "FAIL") + ": " + k)
assert all(checks.values())
print("PASS: okx cooldown policy (static only, no browser run)")
