"""TIA interactive single-screen trading intelligence cockpit.
Existing public market sources only; account data is explicitly not connected.
"""
from __future__ import annotations
from datetime import datetime, timezone
import pandas as pd
import streamlit as st


@st.cache_data(ttl=45, show_spinner=False)
def _flow(asset, cls):
    from modules.spot_flow import fetch
    return fetch(asset, cls)


@st.cache_data(ttl=120, show_spinner=False)
def _options(currency):
    from modules.options_desk import fetch, summarize, dvol, iv_rank
    rows = fetch(currency)
    out = summarize(rows)
    history = dvol(currency, 365)
    out["dvol_history"] = history[-90:]
    out["dvol_rank"] = iv_rank([x[1] for x in history])
    return out


@st.cache_data(ttl=180, show_spinner=False)
def _news():
    from modules.news_feed import get_latest_news
    return get_latest_news("general", 12)


@st.cache_data(ttl=90, show_spinner=False)
def _candles(symbol, tf):
    from modules.market_cache import get_klines
    return get_klines(symbol, tf, 180)


def _fmt(v, digits=2, suffix=""):
    try:
        n = float(v)
        return "—" if pd.isna(n) else f"{n:,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return "—"


def _metric(col, label, value, help_text=""):
    col.metric(label, value, help=help_text or None)


def render_tia():
    st.markdown("""
    <style>
    .tia-top{background:linear-gradient(110deg,#080a0d,#17140e 68%,#2a1e0b);border:1px solid #66502a;border-radius:15px;padding:16px 20px;margin:0 0 12px}
    .tia-k{font-size:10px;letter-spacing:3px;color:#c6a35e;font-weight:700}
    .tia-h{font-size:27px;letter-spacing:5px;color:#f3dfb5;font-weight:800}
    .tia-s{font-size:11px;letter-spacing:1.5px;color:#b9ad96}
    div[data-testid="stMetric"]{background:#111216;border:1px solid #393124;padding:9px 11px;border-radius:10px}
    div[data-testid="stMetricLabel"]{color:#c5ad7d}
    </style>
    <div class="tia-top"><div class="tia-k">TRADE INTELLIGENCE AGENCY · 6868</div>
    <div class="tia-h">TIA COMMAND COCKPIT</div>
    <div class="tia-s">MARKET · STRUCTURE · LIQUIDITY · DERIVATIVES · RISK · DECISION</div></div>
    """, unsafe_allow_html=True)

    # One persistent screen; controls drive every linked panel below.
    c1,c2,c3,c4=st.columns([1.15,1,1,0.8])
    universe=c1.selectbox("Market universe",["Crypto","TradFi proxies"],key="tia_universe")
    symbols=["BTC","ETH","SOL","XRP"] if universe=="Crypto" else ["GOLD","SILVER","SP500","EUR"]
    asset=c2.selectbox("Focus asset",symbols,key="tia_asset")
    tf=c3.selectbox("Timeframe",["5m","15m","1h","4h","1d"],index=2,key="tia_tf")
    if c4.button("↻ Refresh",use_container_width=True,key="tia_refresh"):
        st.cache_data.clear(); st.rerun()
    st.caption("Evidence cockpit · "+datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")+" · Selected asset: "+asset)

    flow=_flow(asset,"crypto" if universe=="Crypto" else "metals")
    tape=flow.get("tape",{}); taker=flow.get("taker",{}); book=flow.get("book",{})
    deriv=flow.get("deriv",{}); prem=flow.get("premium",{}); vp=flow.get("vp",{})
    st.subheader("LIVE MARKET KPIs")
    k=st.columns(6)
    _metric(k[0],"Aggressor buy share",_fmt(tape.get("buy_share")*100 if tape.get("ok") else None,1,"%"),"Recent executed prints")
    _metric(k[1],"Taker buy share",_fmt(taker.get("buy_share")*100 if taker.get("ok") else None,1,"%"),"Provider taker history")
    _metric(k[2],"Book imbalance",_fmt(book.get("imbalance")*100 if book.get("ok") else None,1,"%"),"Venue snapshot, not global depth")
    _metric(k[3],"Funding",_fmt(deriv.get("funding") if deriv.get("ok") else None,4,"%"),"Perpetual funding")
    _metric(k[4],"Open interest",_fmt(deriv.get("oi") if deriv.get("ok") else deriv.get("oi_chg_7d") if deriv.get("ok") else None), "Provider units / coverage vary")
    _metric(k[5],"Coinbase premium",_fmt(prem.get("premium_pct") if prem.get("ok") else None,3,"%"),"BTC / ETH / SOL only")
    st.caption("Feed: "+str(flow.get("src","unknown"))+" · Missing values stay blank; unavailable is never converted to zero.")

    left,right=st.columns([1.65,1])
    with left:
        st.subheader("01 · PRICE ACTION & STRUCTURE")
        try:
            sym=asset if universe=="Crypto" else "HL:xyz:"+asset
            df=_candles(sym,tf)
            if df is not None and not df.empty:
                st.line_chart(df.set_index("time")[["close"]],height=280,use_container_width=True)
                q=st.columns(3)
                _metric(q[0],"Last",_fmt(df.iloc[-1]["close"],4))
                _metric(q[1],"50-bar high",_fmt(df["high"].tail(50).max(),4))
                _metric(q[2],"50-bar low",_fmt(df["low"].tail(50).min(),4))
                st.area_chart(df.set_index("time")[["volume"]],height=105,use_container_width=True)
            else: st.info("No candles returned for this selection.")
        except Exception as exc: st.warning("Chart feed unavailable: "+type(exc).__name__)
    with right:
        st.subheader("02 · ORDER FLOW & LIQUIDITY")
        if book.get("ok"):
            st.progress(min(1.0,max(0.0,float(book.get("imbalance",0))*.5+.5)),text="Bid / ask depth balance")
            st.dataframe(pd.DataFrame([
                {"Level":"Bid wall","Price":book.get("wall_bid"),"Size":book.get("wall_bid_size")},
                {"Level":"Ask wall","Price":book.get("wall_ask"),"Size":book.get("wall_ask_size")}]),hide_index=True,use_container_width=True)
        else: st.info("No order-book snapshot for this instrument.")
        if tape.get("ok"):
            st.write(f"Prints **{tape.get('n','—')}** · large buys **{tape.get('big_buy','—')}** · large sells **{tape.get('big_sell','—')}**")
        if vp.get("ok"):
            st.write(f"7-day candle volume profile · POC **{_fmt(vp.get('poc'),4)}** · VAL **{_fmt(vp.get('val'),4)}** · VAH **{_fmt(vp.get('vah'),4)}**")
        st.caption("Volume profile is candle-derived; it is not exchange-native footprint or aggressor delta.")

    st.divider()
    a,b=st.columns([1.25,1])
    with a:
        st.subheader("03 · OPTIONS & VOLATILITY")
        if universe=="Crypto" and asset in ("BTC","ETH"):
            try:
                opt=_options(asset); totals=opt.get("totals",{}); rank=opt.get("dvol_rank") or {}
                x=st.columns(4)
                _metric(x[0],"Options OI",_fmt(totals.get("oi"),0))
                _metric(x[1],"Put / Call OI",_fmt(totals.get("pc_oi")))
                _metric(x[2],"Options volume",_fmt(totals.get("vol"),0))
                _metric(x[3],"DVOL rank",_fmt(rank.get("rank"),0,"%"))
                ex=opt.get("expiries",[])
                if ex: st.dataframe(pd.DataFrame([{"Expiry":str(z["exp"]),"DTE":z["days"],"P/C OI":z["pc_oi"],"ATM IV":z["iv"],"Max pain":z["max_pain"]} for z in ex[:10]]),hide_index=True,use_container_width=True)
                if opt.get("dvol_history"): st.line_chart(pd.DataFrame(opt["dvol_history"],columns=["Date","DVOL"]).set_index("Date"),height=130)
                st.caption("Deribit BTC/ETH only. OI does not reveal dealer inventory or opening/closing intent.")
            except Exception as exc: st.warning("Options feed unavailable: "+type(exc).__name__)
        else: st.info("Deribit options panel is available for BTC/ETH only. Cboe US options are separate and delayed.")
        st.subheader("04 · NEWS & CATALYSTS")
        try:
            for item in (_news() or [])[:8]:
                head=item.get("headline",""); url=item.get("url","")
                if head:
                    if url.startswith(("https://","http://")): st.markdown(f"- [{head}]({url}) · {item.get('source','')} · {item.get('datetime','')}")
                    else: st.markdown(f"- {head} · {item.get('source','')}")
        except Exception as exc: st.caption("News unavailable: "+type(exc).__name__)
    with b:
        st.subheader("05 · PROVIDER HEALTH")
        rows=[]
        for label,obj in [("Time & Sales",tape),("Taker volume",taker),("Order book",book),("Derivatives",deriv),("Cross-venue premium",prem),("Volume profile",vp)]:
            rows.append({"Feed":label,"Status":"AVAILABLE" if obj.get("ok") else "UNAVAILABLE","Detail":"" if obj.get("ok") else obj.get("why","Not supplied")})
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
        st.caption("Provider event timestamps are not yet exposed by the existing order-flow adapter.")
        st.subheader("06 · ACCOUNT RISK")
        st.warning("Broker balance, equity, margin, open positions, fills, fees and funding are not connected. Account KPIs are intentionally not fabricated.")
        _metric(st,"Portfolio exposure","NOT CONNECTED")
        _metric(st,"Daily loss / open risk","NOT VERIFIED")
        st.subheader("07 · EVIDENCE SYNTHESIS")
        evidence=[]
        for label,obj,key in [("Executed buy share",tape,"buy_share"),("Taker buy share",taker,"buy_share"),("Book imbalance",book,"imbalance")]:
            if obj.get("ok") and obj.get(key) is not None: evidence.append({"Evidence":label,"Value":_fmt(obj[key],4),"Scope":"Provider / venue specific"})
        if evidence: st.dataframe(pd.DataFrame(evidence),hide_index=True,use_container_width=True)
        else: st.info("Insufficient verified directional evidence. No signal issued.")
        st.caption("No synthetic confidence score. This cockpit does not place orders.")

    st.divider()
    st.subheader("08 · ALL CONNECTED DATA DOMAINS")
    st.dataframe(pd.DataFrame([
        {"Domain":"Crypto spot / derivatives","Provider":"OKX","Coverage":"Trades, book, taker history, OI/funding, L/S accounts"},
        {"Domain":"TradFi proxy markets","Provider":"Hyperliquid xyz","Coverage":"Oracle-linked perpetuals: metals, FX, indices, selected stocks"},
        {"Domain":"Crypto options","Provider":"Deribit","Coverage":"BTC/ETH chain, DVOL; dealer direction unknown"},
        {"Domain":"US options","Provider":"Cboe delayed endpoint","Coverage":"Delayed / unofficial; not live validated"},
        {"Domain":"News","Provider":"Finnhub / Alpha Vantage / RSS","Coverage":"Headlines; impact attribution not inferred"},
        {"Domain":"Macro","Provider":"Existing FRED modules","Coverage":"Series depend on module configuration"},
        {"Domain":"Broker account","Provider":"Not connected","Coverage":"Authenticated adapter and reconciliation required"},
        {"Domain":"Historical depth","Provider":"Not yet recorded","Coverage":"Sequenced WebSocket capture required; never inferred from OHLCV"},
    ]),hide_index=True,use_container_width=True)
