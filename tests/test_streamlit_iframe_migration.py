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


if __name__ == "__main__":
    test_no_deprecated_html_component_calls_remain()
    print("ok all JavaScript HTML embeds use st.iframe")
