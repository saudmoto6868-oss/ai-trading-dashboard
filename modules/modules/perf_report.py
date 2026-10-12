from modules.perf_report import perf_stats, quantstats_html
import streamlit.components.v1 as components
st.json(perf_stats(returns))            # returns = Series عوائد الصفقات بالتاريخ
html = quantstats_html(returns)
if html: components.html(html, height=900, scrolling=True)
