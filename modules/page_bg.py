"""Background scan, workers and shared caches used by the Workspace and the Radar. Moved from main.py unchanged (maintenance plan M7).
Everything here is process-wide (st.cache_resource / threads), so it must never read per-session values: callers pass them as arguments."""
import os
import time

import streamlit as st

from config import CRYPTO_SYMBOLS
from modules.alerts import ALERT_SCORE_THRESHOLD
from modules.arabic import scan_entry
from modules.asset_classes import class_symbols
from modules.market_cache import fetch_frames, get_klines
from modules.scorer import scan_symbol, fetch_tfs, SCAN_TFS, MAX_SAME_SIDE
from modules.workspace import seed_from_df


@st.cache_data(ttl=120, show_spinner=False)
def _peer_frames(symbols, tf):
    """Candles (timeframe `tf`) of the correlated markets needed for SMT divergence, fetched once for the whole list."""
    from modules.smt import peers_of
    need = sorted({p for sy in symbols for p, _i in peers_of(sy)})
    if not need:
        return {}
    try:
        fr, _e = fetch_frames(need, [tf])
    except Exception:
        return {}
    return {sy: v.get(tf) for sy, v in fr.items() if v.get(tf) is not None}


def _peers_for(sym, tf, pframes):
    from modules.smt import peers_of
    return {p: (inv, pframes[p]) for p, inv in peers_of(sym) if p in pframes}


def scan_crypto_group(symbols, tf):
    """Multi-timeframe scan: candles for the chosen timeframe PLUS its higher
    context timeframes are fetched in parallel (cached), then scored."""
    frames, fetch_errors = fetch_frames(symbols, fetch_tfs(tf))
    pframes = _peer_frames(symbols, tf)
    results, errors = [], []
    for sym in symbols:
        try:
            results.append(scan_symbol(sym, frames[sym], tf, peers=_peers_for(sym, tf, pframes)))
        except Exception as e:
            if fetch_errors.get(sym) or "not enough" not in str(e):   # a coin with a short history is just skipped, not a "problem"
                errors.append(f"{sym}: {fetch_errors.get(sym) or e}")
    return results, "; ".join(errors)


@st.cache_resource
def _bg_store():
    import threading
    return {"lock": threading.Lock(), "val": {}, "busy": set(), "t": {}}


def _bg(name, fn, default, ttl=300, wait=1.5):
    """Never let an outside feed hold up the page: run fn() in a thread, wait at most `wait` s, else draw with the last value
    (or `default`) and pick the fresh one up on the next run. Errors keep the last value."""
    import threading
    S = _bg_store()
    have = name in S["val"]
    if (not have or time.time() - S["t"].get(name, 0) > ttl) and name not in S["busy"]:
        with S["lock"]:
            S["busy"].add(name)

        def job():
            from modules.perf_log import timed
            try:
                with timed("_bg " + name):   # PERF_LOG=1 (M0 0.4)
                    S["val"][name] = fn()
                S["t"][name] = time.time()
            except Exception:
                S["t"][name] = time.time() - ttl + 60   # retry in a minute
            finally:
                S["busy"].discard(name)
        th = threading.Thread(target=job, daemon=True)
        th.start()
        th.join(wait if not have else 0)
    return S["val"].get(name, default)


@st.cache_resource
def _scan_store():
    import threading
    return {"lock": threading.Lock(), "running": False, "key": None, "payload": None, "built": 0.0, "t0": time.time()}


def _scan_worker(store, ws_tf, ws_key):
    """Heavy OKX scan, run in a background thread so the page renders immediately.
    The chosen timeframe goes first and partial results are published as they arrive."""
    try:
        # just after a (re)start let the first page render before the heavy scan takes the CPU (Streamlit Cloud gives little CPU)
        wait = 45 - (time.time() - store.get("t0", 0))
        if wait > 0:
            time.sleep(wait)
        ws_alerts, ws_scan, ws_seed, ws_mini, ws_errs = [], {}, None, [], []
        syms_ = list(ws_key[2])

        def publish(done):
            store["payload"] = {"key": ws_key, "alerts": list(ws_alerts), "scan": {k_: dict(v_) for k_, v_ in ws_scan.items()}, "seed": ws_seed,
                                "mini": list(ws_mini), "errs": list(ws_errs), "built": time.time(), "loading": not done}

        try:
            ws_seed = seed_from_df(syms_[0], "1h", get_klines(syms_[0], "1h", 300))
        except Exception:
            ws_seed = None
        from modules.perf_log import timed
        with timed("scan worker %d symbols" % len(syms_)):   # PERF_LOG=1 (M0 0.4): the whole scan, all timeframes
            for tf_ in [ws_tf] + [t for t in SCAN_TFS if t != ws_tf]:
                tf_alerts = []
                try:
                    ws_results, _ws_notice = scan_crypto_group(syms_, tf_)
                    if _ws_notice:
                        ws_errs.append(f"{tf_}: {_ws_notice[:120]}")
                except Exception as ex_:
                    ws_errs.append(f"{tf_}: {ex_}")
                    publish(False)
                    continue
                for r_ in ws_results:
                    try:
                        df_ = get_klines(r_["symbol"], tf_, 300)
                        e_ = scan_entry(r_, df_)
                        if e_:
                            try:
                                from modules.telegram_alerts import quality as _tq
                                e_["q"], e_["qwhy"] = _tq(r_, e_)   # evidence rank 0-100 (used to pick what goes to Telegram)
                            except Exception:
                                e_["q"], e_["qwhy"] = 0, []
                            e_["spark"] = [round(float(x), 6) for x in df_["close"].iloc[-41:-1]]
                    except Exception:
                        e_ = None
                    if not e_:
                        continue
                    if e_.get("plan"):
                        try:   # signal ledger (modules/signal_ledger.py): every scanner plan, replayed and explained later. t0 = the next candle's open (no look-ahead)
                            import pandas as pd
                            from modules import signal_ledger as _SL
                            _t_last = int(pd.Timestamp(df_["time"].iloc[-1]).value // 1_000_000)
                            _SL.record({"src": "scanner", "sub": str(e_.get("ttype") or ""), "symbol": r_["symbol"], "tf": tf_, "dir": e_["direction"],
                                        "entry": e_["plan"]["entry"], "sl": e_["plan"]["stop"], "tps": e_["plan"]["tps"], "t0": _t_last + _SL.tf_ms(tf_),
                                        "score": e_.get("score"), "max": e_.get("max"), "why": e_.get("keys") or [],
                                        "ctx": {"against_signal": bool(r_.get("against"))}})
                        except Exception:
                            pass   # the ledger must never break the scan
                        ws_mini.append({k: e_.get(k) for k in ("symbol", "direction", "tfk", "ttype", "trade", "tags", "tags_en", "plan", "score", "max", "tv", "spark")}
                                       | {"keys": [str(x_.get("key")) for x_ in (r_.get("signals") or []) if x_.get("key")][:20], "against": bool(r_.get("against"))})   # detector keys + opposing flag for the Evidence summary tab
                    # one entry per symbol AND chart timeframe: the chart only draws the setup that belongs to the timeframe it shows
                    _slot = ws_scan.setdefault(r_["symbol"], {})
                    if e_["tfc"] not in _slot or e_["score"] > _slot[e_["tfc"]]["score"]:
                        _slot[e_["tfc"]] = ({k: e_[k] for k in ("tfc", "tags", "zones", "plan", "score", "max", "tv", "trade", "spark", "ttype", "ew")}
                                            | {"tf": e_["tfc"], "dir": e_["direction"], "keys": e_.get("keys", [])})   # keys: X77 chart indicator labels this setup by school
                    if r_["score"] >= ALERT_SCORE_THRESHOLD and (tf_ != "1m" or "1m" in SCAN_TFS) and not r_.get("against"):   # 1m only with SCAN_1M=1; no opposing signal (lab: opposed setups lost ~ -280R)
                        tf_alerts.append(e_ | {"id": f"scan|{r_['symbol']}|{tf_}|{r_['direction']}|{r_['score']}|{ws_key[1]}"})
                for side_ in ("bullish", "bearish"):   # same-direction alerts at one moment are one market-wide bet: keep the best few
                    ws_alerts.extend(sorted((a for a in tf_alerts if a.get("direction") == side_), key=lambda a: -(a.get("q") or 0))[:MAX_SAME_SIDE])
                publish(False)
        publish(True)
        try:   # the brain's setup detectors (CISD, CRT, sweeps, Model 2022, Elliott ...) -> the ledger, each detector its own strategy; every 15 min, capped symbols
            from modules import signal_ledger as _SL
            if time.time() - store.get("ledger_setups_t", 0) >= 900:
                store["ledger_setups_t"] = time.time()
                _SL.record_setups(syms_[:int(os.environ.get("LEDGER_SETUP_SYMBOLS", "20") or 20)], lambda s_, t_: get_klines(s_, t_, 300))
        except Exception:
            pass
        try:   # replay the ledger's signals whose time has come (cached candles, at most 60 per pass)
            from modules import signal_ledger as _SL
            _SL.grade_pending(get_klines, limit=60)
        except Exception:
            pass
        store["key"] = ws_key
        store["built"] = time.time()
    except Exception as ex_:
        store["payload"] = {"key": ws_key, "alerts": [], "scan": {}, "seed": None, "mini": [],
                            "errs": [f"scan crashed: {type(ex_).__name__}: {ex_}"], "built": time.time(), "loading": False}
        store["key"] = ws_key
        store["built"] = time.time()
    finally:
        store["running"] = False


@st.cache_resource
def _tg_sent():
    """symbol|side|tf -> (time, quality) of what was already sent to Telegram (shared across reruns)."""
    return {}


@st.cache_resource
def _tfstats_store():
    return {"running": False, "data": None, "t": 0.0}


def _tf_worker(store):
    try:
        from modules import backtest_tf as B
        p = B.run(CRYPTO_SYMBOLS[:6], stride=8)
        B.save(p)
        store["data"] = p
    except Exception:
        pass
    finally:
        store["running"] = False


def get_tf_stats():
    """Per-strategy best-timeframe table (walk-forward TP1 hit-rates). Cached on disk; rebuilt in the background once a day."""
    import threading
    from modules import backtest_tf as B
    store = _tfstats_store()
    d, stale = B.load(max_age=86400*8)
    if d:
        store["data"] = d
    # the walk-forward rebuild is heavy: it runs in GitHub Actions (weekly) and is only READ here, unless TF_STATS_BUILD=1
    if os.environ.get("TF_STATS_BUILD") == "1" and (stale or not store["data"]) and not store["running"] and time.time() - store["t"] > 1800:
        store["running"], store["t"] = True, time.time()
        threading.Thread(target=_tf_worker, args=(store,), daemon=True).start()
    d = store["data"]
    return {"stats": d["stats"], "best": d["best"], "min_n": d["min_n"], "built": d["built"]} if d else {}


def _ws_universe(active):
    """The symbols the Workspace scan covers: the chosen asset class PLUS a few liquid markets of the other classes (gold, silver, copper, S&P 500,
    Nasdaq-100, JPY / EUR / GBP from Hyperliquid), so Setup / Signals / the chart's trade box also have data when the chart shows gold, an index or forex
    (before, only the class picked in the Radar was scanned and everything else stayed empty)."""
    out = list(active)
    try:
        from modules.asset_classes import WS_EXTRA
        for cls, n in WS_EXTRA:
            syms, _m = class_symbols(cls, CRYPTO_SYMBOLS)
            out += [x for x in syms if x.startswith("HL:")][:n]
    except Exception:
        pass
    seen = set()
    return tuple(x for x in out if not (x in seen or seen.add(x)))


SMT_TFS = tuple(x.strip() for x in os.environ.get("SMT_TFS", "5m,15m,1h,4h,1d").split(",") if x.strip())


def _smt_worker(store):
    """SMT between correlated pairs on several timeframes (modules/intermarket.py), in its own thread: never holds the page or the main scan up."""
    try:
        from modules import intermarket as _IM
        store["smt"] = _IM.scan_pairs(lambda s_, t_: get_klines(s_, t_, 300), tfs=SMT_TFS)
        store["smt_t"] = time.time()
        store.pop("smt_err", None)
    except Exception as e_:
        store["smt_err"] = f"{type(e_).__name__}: {e_}"
        store["smt_t"] = time.time() - 600   # retry in about 5 minutes
    finally:
        store["smt_running"] = False


DAY_SYMBOLS = tuple(x.strip() for x in os.environ.get("DAY_SYMBOLS", "BTC-USDT,ETH-USDT,SOL-USDT,HL:xyz:GOLD,HL:xyz:SILVER,HL:xyz:SP500,HL:xyz:XYZ100,HL:xyz:CL,Y:EURUSD=X,Y:GBPUSD=X").split(",") if x.strip())


def _dayplan_worker(store):
    """Standard day plan (timeframe confluence) for the day-plan universe, in its own thread; feeds the Telegram alerts."""
    try:
        from modules import day_plan as _DP
        store["dayplan"] = _DP.scan(list(DAY_SYMBOLS), lambda s_, t_: get_klines(s_, t_, 300), mode="conf")
        store["dayplan_watch"] = _DP.scan_watch(list(DAY_SYMBOLS), lambda s_, t_: get_klines(s_, t_, 300))
        store["dayplan_t"] = time.time()
        store.pop("dayplan_err", None)
    except Exception as e_:
        store["dayplan_err"] = f"{type(e_).__name__}: {e_}"
        store["dayplan_t"] = time.time() - 600
    finally:
        store["dayplan_running"] = False


def _dayplan_watch():
    _dayplan_events()
    return _scan_store().get("dayplan_watch", [])


def _dayplan_events():
    import threading
    store = _scan_store()
    if not store.get("dayplan_running") and time.time() - store.get("dayplan_t", 0) > 900 and time.time() - store.get("t0", 0) > 45:
        store["dayplan_running"] = True
        threading.Thread(target=_dayplan_worker, args=(store,), daemon=True).start()
    return store.get("dayplan", [])


def _smt_events():
    """The latest intermarket events (starts / refreshes the background scan when it is older than 15 minutes)."""
    import threading
    store = _scan_store()
    if not store.get("smt_running") and time.time() - store.get("smt_t", 0) > 900 and time.time() - store.get("t0", 0) > 30:
        store["smt_running"] = True
        threading.Thread(target=_smt_worker, args=(store,), daemon=True).start()
    return store.get("smt", [])


def build_ws_payload(symbols=None):
    """Never blocks the page: returns the latest (possibly partial / still-loading) scan and starts a
    background refresh when the 30-minute bucket changes or an empty result is older than 60 s."""
    import threading
    ws_tf = st.session_state.get("scan_tf", "1h")
    ws_key = (ws_tf, str(int(time.time() // 1800)), tuple(symbols or CRYPTO_SYMBOLS))
    store = _scan_store()
    pl = store["payload"]
    stale_empty = bool(pl) and not pl.get("mini") and not pl.get("loading") and time.time() - pl.get("built", 0) > 60
    if store["key"] != ws_key or stale_empty:
        with store["lock"]:
            # also restart a worker that has been silent for 5 minutes (hung)
            hung = store["running"] and time.time() - store.get("started", 0) > 300
            if (not store["running"] or hung) and (store["key"] != ws_key or stale_empty):
                store["running"] = True
                store["started"] = time.time()
                threading.Thread(target=_scan_worker, args=(store, ws_tf, ws_key), daemon=True).start()
    pl = store["payload"]
    if pl is None:
        return {"key": ws_key, "alerts": [], "scan": {}, "seed": None, "mini": [],
                "errs": ["Scanning OKX in the background - results appear here in a few seconds..."],
                "built": time.time(), "loading": True}
    return pl
