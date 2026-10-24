"""
THE CHART VENDOR
Builds the embedded TradingView widget (advanced chart, with full
indicator toolbar) for a given symbol.
"""

import streamlit.components.v1 as components
from config import TV_SYMBOL_MAP


def render_tv_chart(symbol: str, height: int = 500, interval: str = "60", key: str = ""):
    """interval: TradingView code ("1","5","15","60","240","D","W"). key keeps the
    container id unique when two charts of the same symbol are on one page."""
    tv_symbol = TV_SYMBOL_MAP.get(symbol, symbol)
    cid = "tv_" + "".join(ch if ch.isalnum() else "_" for ch in f"{key}_{symbol}_{interval}")
    widget_html = f"""
    <div class="tradingview-widget-container">
      <div id="{cid}"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": {height},
        "symbol": "{tv_symbol}",
        "interval": "{interval}",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#131722",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "studies": ["RSI@tv-basicstudies"],
        "container_id": "{cid}"
      }});
      </script>
    </div>
    """
    components.html(widget_html, height=height + 20)
