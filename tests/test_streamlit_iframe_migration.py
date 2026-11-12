"""Guard the Streamlit 1.56+ migration from components.html() to st.iframe()."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_IFRAME_FILES = (
    "modules/workspace.py",
    "modules/header_bar.py",
    "modules/tv_widget.py",
    "modules/micro_foundations.py",
    "modules/quant_edgemap.py",
    "modules/quant_execution.py",
    "modules/quant_montecarlo.py",
    "modules/quant_robustness.py",
    "modules/spot_page.py",
    "main.py",
)


def test_no_deprecated_html_component_calls_remain():
    scan = [ROOT / "main.py", *sorted((ROOT / "modules").rglob("*.py"))]
    for path in scan:
        source = path.read_text(encoding="utf-8")
        assert "components.html(" not in source, f"deprecated components.html remains in {path.relative_to(ROOT)}"

    for rel in EXPECTED_IFRAME_FILES:
        source = (ROOT / rel).read_text(encoding="utf-8")
        assert "st.iframe(" in source, f"expected st.iframe in {rel}"
        compile(source, rel, "exec")

    header_html = (ROOT / "modules/header_bar.html").read_text(encoding="utf-8")
    workspace_html = (ROOT / "modules/workspace_app.html").read_text(encoding="utf-8")
    tv_source = (ROOT / "modules/tv_widget.py").read_text(encoding="utf-8")
    assert "html,body" in header_html and "overflow:hidden" in header_html
    assert "html,body" in workspace_html and "overflow:hidden" in workspace_html
    assert "overflow:hidden!important" in tv_source
    main_source = (ROOT / "main.py").read_text(encoding="utf-8")
    assert 'st.iframe(_html, height=900, alt="QuantStats performance report")' in main_source


if __name__ == "__main__":
    test_no_deprecated_html_component_calls_remain()
    print("ok no components.html calls in main.py/modules; expected iframe embeds and overflow policy verified")
