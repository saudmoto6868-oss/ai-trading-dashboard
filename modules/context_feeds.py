"""Context feeds shared by the desk Workspace (main.py) and TIA: economic calendar, crypto market metrics (CMC),
stock fundamentals and macro fundamentals. Moved out of main.py on 2026-11-20 so TIA gets the same data with the same caching.
Each function is cached by Streamlit with the same TTL it had in main.py. No behaviour change for the desk."""
import streamlit as st


@st.cache_data(ttl=900, show_spinner=False)
def calendar_rows() -> list:
    from modules.calendar_feed import fetch_calendar
    return fetch_calendar()


@st.cache_data(ttl=900, show_spinner=False)
def cmc_data():
    from modules.cmc import fetch_cmc
    return fetch_cmc()


@st.cache_data(ttl=21600, show_spinner=False)
def stock_fund(tickers: tuple):
    from modules.stock_fund import fetch_stock_fund
    return fetch_stock_fund(tickers)


@st.cache_data(ttl=21600, show_spinner=False)
def macro_fund():
    from modules.macro_fund import fetch_macro_fund
    return fetch_macro_fund()
