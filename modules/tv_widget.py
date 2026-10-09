"""
THE CHART VENDOR
Builds the embedded TradingView widget (advanced chart, with full
indicator toolbar) for a given symbol.
"""

import streamlit.components.v1 as components
from config import TV_SYMBOL_MAP


def render_tv_chart(symbol: str, height: int = 500):
    tv_symbol = TV_SYMBOL_MAP.get(symbol, symbol)
    widget_html = f"""
    <div class="tradingview-widget-container">
      <div id="tv_chart_{symbol}"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": {height},
        "symbol": "{tv_symbol}",
        "interval": "60",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#131722",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "studies": ["RSI@tv-basicstudies"],
        "container_id": "tv_chart_{symbol}"
      }});
      </script>
    </div>
    """
    components.html(widget_html, height=height + 20)
