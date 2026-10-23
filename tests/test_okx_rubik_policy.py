"""Static checks: the browser stops asking OKX /rubik/ (no CORS header) after one real failure (plain script, no browser)."""
import os
src = open(os.path.join(os.path.dirname(__file__), "..", "modules", "workspace_app.html"), encoding="utf-8").read()
i = src.index("function okx(path){"); body = src[i:i + 5200]
checks = {
    "dead flag is shared and persisted": 'localStorage.setItem("okx_rub_dead"' in src and 'localStorage.getItem("okx_rub_dead")' in src,
    "rubik skipped while dead": "Date.now() < OKX_RUB_DEAD" in body,
    "other coins wait for the first probe": "OKX_RUB_PROBE.then(() => okx(path))" in body,
    "probe is registered for the first rubik request": "if (rub && !OKX_RUB_PROBE)" in body,
    "dead for 6 hours on a CORS / network failure": "6*3600e3" in body,
}
for k, v in checks.items(): print(("PASS" if v else "FAIL") + ": " + k)
assert all(checks.values())
print("PASS: okx rubik policy (static only, no browser run)")
