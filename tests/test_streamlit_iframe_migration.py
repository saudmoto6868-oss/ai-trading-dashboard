"""Guard the Streamlit 1.56+ migration from components.html() to st.iframe()."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = (
    "modules/workspace.py",
    "modules/header_bar.py",
    "modules/tv_widget.py",
    "main.py",
)


def test_no_deprecated_html_component_calls_remain():
    for rel in FILES:
        source = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        assert "components.html(" not in source, f"deprecated components.html remains in {rel}"
        assert "st.iframe(" in source, f"expected st.iframe in {rel}"
        compile(source, rel, "exec")  # syntax-check each migrated Python module

    header_html = open(os.path.join(ROOT, "modules/header_bar.html"), encoding="utf-8").read()
    workspace_html = open(os.path.join(ROOT, "modules/workspace_app.html"), encoding="utf-8").read()
    tv_source = open(os.path.join(ROOT, "modules/tv_widget.py"), encoding="utf-8").read()
    assert "html,body" in header_html and "overflow:hidden" in header_html
    assert "html,body" in workspace_html and "overflow:hidden" in workspace_html
    assert "overflow:hidden!important" in tv_source  # st.iframe has no scrolling=False; contain the three fixed-height embeds in their own HTML
    main_source = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert 'st.iframe(_html, height=900, alt="QuantStats performance report")' in main_source  # report intentionally remains scrollable


if __name__ == "__main__":
    test_no_deprecated_html_component_calls_remain()
    print("ok all JavaScript HTML embeds use st.iframe")
