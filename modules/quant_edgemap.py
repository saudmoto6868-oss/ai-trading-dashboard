"""Edge Map tab — force graph: strategies as nodes, edges = correlations."""
from pathlib import Path
import streamlit.components.v1 as _components

_TEMPLATE = Path(__file__).with_name("edge_map_app.html")


def render() -> None:
    from modules.lab_banner import with_demo_banner
    _html = with_demo_banner(_TEMPLATE.read_text(encoding="utf-8"), 'كل العقد والارتباطات مثال', 'every node and correlation is an example')
    _components.html(_html, height=900, scrolling=True)
