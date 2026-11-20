"""Trade-review database (owner 2026-11-20, priority 1): every idea in SQL tables, ready for review queries.

Tables (SQLite):
  ideas       one row per idea: source (lab / desk / telegram), symbol, tf, time, side, entry, stop, target, primary detector,
              school, taken (desk: filled or not), skip/status, plus OOS flag for lab rows
  context     what the market looked like at the idea bar (no look-ahead): nearest swing support / resistance and their
              distance in ATR, RSI14, price vs EMA20/50/200, ATR %, position in the 50-bar range, relative volume,
              session, weekday, same-tf 100-bar trend, real higher-timeframe arm (1D / 4H from research/htf_arms)
  votes       every OTHER detector that fired on the same symbol and bar: +1 confirms the idea's side, -1 contradicts
  outcomes    how it ended under the lab's own exit rule (1.5 ATR stop, 1.5R target, lab horizon): exit type
              (tp / sl / time), R, net R (minus 0.10R), bars and minutes to exit, MFE and MAE in R, and the result of
              the OPPOSITE side on the same bar (was the other side the trade?)
  lab_evidence  weekly-lab verdict per detector on 1h (modules.lab_tiers.card: n, net R after cost, verdict)
Views: v_detector, v_vote_edge (does a confirming / contradicting detector change results?), v_sr_room, v_session,
v_missed (opposite side won while the idea lost), v_studied (the "studied trade" filter, owner 2026-11-20: only these feed
the shared brain) and v_studied_edge (does the filter actually beat the rest? measured, not assumed).
A studied idea: no detector or desk doubt against it, at least one confirming detector the lab rates 'edge' or
'positive, not proven', no confirming detector the lab rates 'loses', and its own detector is not rated 'loses'.

Lab rows come from research/htf_arms/events.csv.gz (every detector signal on 1h, 12 markets). Desk rows come from an
ai-desk journal.sqlite if one is given; Telegram rows from the alerts cron's .signal_log.jsonl (the 'signal-log' artifact of
the telegram-alerts workflow). Desk and Telegram ideas get the lab detectors that fired on the same symbol and 1h bar as votes,
so every source is checked against the same schools. Candles are re-fetched from the same feeds (needs network).

Usage: python -m research.trade_db.build_db [--desk journal.sqlite] [--telegram .signal_log.jsonl]   (a bare path = desk)"""
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from modules.signals import atr_series
from modules.strategy_lab import COST_R, HORIZON, RR, STOP_ATR, _fetch

HERE = Path(__file__).parent
DB = HERE / "trade_review.sqlite"
EVENTS = HERE.parent / "htf_arms" / "events.csv.gz"
LTF, BARS, PIV = "1h", 4000, 3
DESK_MAP = {"BTCUSD": "BTC-USDT", "ETHUSD": "ETH-USDT", "SOLUSD": "SOL-USDT", "BNBUSD": "BNB-USDT", "DOGEUSD": "DOGE-USDT",
            "XRPUSD": "XRP-USDT", "XAUUSD": "HL:xyz:GOLD", "XAGUSD": "HL:xyz:SILVER", "EURUSD": "HL:xyz:EUR", "GBPUSD": "HL:xyz:GBP",
            "USDJPY": "HL:xyz:JPY", "USOIL": "HL:xyz:CL", "SPX": "HL:xyz:SP500", "NDX": "HL:xyz:XYZ100"}

SCHEMA = """
CREATE TABLE ideas (id INTEGER PRIMARY KEY, source TEXT, symbol TEXT, tf TEXT, ts INTEGER, time TEXT, side INTEGER,
  entry REAL, stop REAL, target REAL, key TEXT, school TEXT, taken INTEGER, status TEXT, oos INTEGER, ext_id TEXT);
CREATE TABLE context (idea_id INTEGER PRIMARY KEY, support REAL, resistance REAL, room_atr REAL, risk_to_sr_atr REAL,
  rsi14 REAL, vs_ema20 INTEGER, vs_ema50 INTEGER, vs_ema200 INTEGER, atr_pct REAL, range_pos REAL, rel_vol REAL,
  session TEXT, weekday TEXT, trend_100 TEXT, htf_1d TEXT, htf_4h TEXT);
CREATE TABLE votes (idea_id INTEGER, key TEXT, school TEXT, vote INTEGER);
CREATE TABLE outcomes (idea_id INTEGER PRIMARY KEY, exit TEXT, r REAL, r_net REAL, bars_to_exit INTEGER, minutes_to_exit INTEGER,
  mfe_r REAL, mae_r REAL, opp_exit TEXT, opp_r REAL);
CREATE TABLE lab_evidence (key TEXT PRIMARY KEY, school TEXT, tf TEXT, n INTEGER, net REAL, verdict TEXT);
CREATE INDEX ix_votes ON votes(idea_id);
CREATE VIEW v_studied_flag AS SELECT i.id idea_id, i.source,
  (NOT EXISTS (SELECT 1 FROM votes v WHERE v.idea_id=i.id AND v.vote<0)
   AND EXISTS (SELECT 1 FROM votes v JOIN lab_evidence e ON e.key=v.key WHERE v.idea_id=i.id AND v.vote>0
               AND e.verdict IN ('edge','positive, not proven'))
   AND NOT EXISTS (SELECT 1 FROM votes v JOIN lab_evidence e ON e.key=v.key WHERE v.idea_id=i.id AND v.vote>0 AND e.verdict='loses')
   AND NOT EXISTS (SELECT 1 FROM lab_evidence e WHERE e.key=i.key AND e.verdict='loses')) studied FROM ideas i;
CREATE VIEW v_studied AS SELECT i.*, o.exit, o.r_net FROM ideas i JOIN v_studied_flag f ON f.idea_id=i.id
  JOIN outcomes o ON o.idea_id=i.id WHERE f.studied;
CREATE VIEW v_studied_edge AS SELECT f.source, f.studied, COUNT(*) n, ROUND(AVG(o.r_net),3) avg_net, ROUND(AVG(o.exit='tp'),3) tp_rate,
  CASE WHEN COUNT(*)<30 THEN 'not evidence (n<30)' ELSE '' END note
  FROM v_studied_flag f JOIN outcomes o ON o.idea_id=f.idea_id GROUP BY f.source, f.studied;
CREATE VIEW v_detector AS SELECT i.key, i.school, COUNT(*) n, ROUND(AVG(o.r_net),3) avg_net, ROUND(AVG(o.exit='tp'),3) tp_rate,
  ROUND(AVG(o.bars_to_exit),1) avg_bars FROM ideas i JOIN outcomes o ON o.idea_id=i.id GROUP BY i.key ORDER BY n DESC;
CREATE VIEW v_vote_edge AS SELECT v.key voter, v.vote, COUNT(*) n, ROUND(AVG(o.r_net),3) avg_net FROM votes v
  JOIN outcomes o ON o.idea_id=v.idea_id GROUP BY v.key, v.vote HAVING n>=30 ORDER BY avg_net DESC;
CREATE VIEW v_sr_room AS SELECT CASE WHEN c.room_atr IS NULL THEN 'none' WHEN c.room_atr<1 THEN '<1 ATR' WHEN c.room_atr<2.25 THEN '1-2.25 ATR'
  ELSE '>=2.25 ATR (target fits)' END room, COUNT(*) n, ROUND(AVG(o.r_net),3) avg_net, ROUND(AVG(o.exit='tp'),3) tp_rate
  FROM context c JOIN outcomes o ON o.idea_id=c.idea_id GROUP BY room;
CREATE VIEW v_session AS SELECT c.session, COUNT(*) n, ROUND(AVG(o.r_net),3) avg_net FROM context c JOIN outcomes o ON o.idea_id=c.idea_id GROUP BY c.session;
CREATE VIEW v_missed AS SELECT i.*, o.r, o.opp_r FROM ideas i JOIN outcomes o ON o.idea_id=i.id WHERE o.exit='sl' AND o.opp_exit='tp';
"""


def swings(hi, lo, c, i, n=PIV, look=200):
    """Nearest confirmed swing low BELOW / swing high ABOVE close i, using only pivots confirmed by bar i (n bars after the pivot)."""
    a = max(n, i - look)
    sup = res = None
    for k in range(i - n, a - 1, -1):
        w_h, w_l = hi[k - n:k + n + 1], lo[k - n:k + n + 1]
        if res is None and hi[k] == w_h.max() and hi[k] > c:
            res = hi[k]
        if sup is None and lo[k] == w_l.min() and lo[k] < c:
            sup = lo[k]
        if sup is not None and res is not None:
            break
    return sup, res


def walk_trade(hi, lo, cl, i, d, stop_d, H, rr=RR):
    """Same exit rule as strategy_lab._outcome, plus exit type, bars to exit, MFE and MAE in R."""
    e = cl[i]; sl = e - d * stop_d; tp = e + d * rr * stop_d; mfe = mae = 0.0
    for j in range(i + 1, min(len(cl), i + 1 + H)):
        fav = (hi[j] - e) if d > 0 else (e - lo[j]); adv = (e - lo[j]) if d > 0 else (hi[j] - e)
        mfe, mae = max(mfe, fav / stop_d), max(mae, adv / stop_d)
        if (lo[j] <= sl) if d > 0 else (hi[j] >= sl):
            return "sl", -1.0, j - i, mfe, mae
        if (hi[j] >= tp) if d > 0 else (lo[j] <= tp):
            return "tp", rr, j - i, mfe, mae
    j = min(len(cl) - 1, i + H)
    return "time", float(np.clip(d * (cl[j] - e) / stop_d, -1.0, rr)), j - i, mfe, mae


def rsi(c, n=14):
    d = np.diff(c, prepend=c[0]); up = pd.Series(np.clip(d, 0, None)).ewm(alpha=1 / n).mean(); dn = pd.Series(np.clip(-d, 0, None)).ewm(alpha=1 / n).mean()
    return (100 - 100 / (1 + up / dn.replace(0, np.nan))).fillna(50).values


def frame(sym):
    df = _fetch(sym, LTF, BARS).reset_index(drop=True)
    c = df["close"].values
    ind = {"atr": atr_series(df, 14).values, "rsi": rsi(c)}
    for n in (20, 50, 200):
        ind[f"ema{n}"] = df["close"].ewm(span=n, adjust=False).mean().values
    ind["vol"] = df["volume"].values.astype(float) if "volume" in df else np.zeros(len(df))
    ind["tms"] = np.array([t.value // 10**6 for t in df["time"]], dtype=np.int64)   # ms, same as strategy_lab events (astype int64 depends on the datetime unit)
    return df, ind


def context(df, ind, i, d):
    hi, lo, cl = df["high"].values, df["low"].values, df["close"].values
    a = ind["atr"][i]; sup, res = swings(hi, lo, cl[i], i)
    room = ((res - cl[i]) if d > 0 else (cl[i] - sup)) / a if a > 0 and (res if d > 0 else sup) is not None else None
    risk = ((cl[i] - sup) if d > 0 else (res - cl[i])) / a if a > 0 and (sup if d > 0 else res) is not None else None
    w = slice(max(0, i - 49), i + 1); h, l = hi[w].max(), lo[w].min()
    v0 = ind["vol"][max(0, i - 20):i]
    ts = df["time"].iloc[i]; hr = ts.hour
    ses = "Asia 00-07" if hr < 7 else "London 07-12" if hr < 12 else "New York 12-20" if hr < 20 else "Late 20-24"
    return {"support": sup, "resistance": res, "room_atr": None if room is None else round(float(room), 2),
            "risk_to_sr_atr": None if risk is None else round(float(risk), 2), "rsi14": round(float(ind["rsi"][i]), 1),
            **{f"vs_ema{n}": int(np.sign(cl[i] - ind[f"ema{n}"][i])) for n in (20, 50, 200)},
            "atr_pct": round(float(a / cl[i] * 100), 3) if cl[i] else None, "range_pos": round(float((cl[i] - l) / (h - l)), 3) if h > l else .5,
            "rel_vol": round(float(ind["vol"][i] / v0.mean()), 2) if len(v0) and v0.mean() > 0 else None, "session": ses, "weekday": ts.strftime("%a")}


def school_of(key):
    from modules.strategy_lab import SCHOOL
    return SCHOOL.get(key, key)


def insert(con, idea, ctx, out, votes):
    cur = con.execute("INSERT INTO ideas (source,symbol,tf,ts,time,side,entry,stop,target,key,school,taken,status,oos,ext_id) "
                      "VALUES (:source,:symbol,:tf,:ts,:time,:side,:entry,:stop,:target,:key,:school,:taken,:status,:oos,:ext_id)", idea)
    iid = cur.lastrowid
    con.execute("INSERT INTO context VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (iid, *[ctx.get(k) for k in (
        "support", "resistance", "room_atr", "risk_to_sr_atr", "rsi14", "vs_ema20", "vs_ema50", "vs_ema200", "atr_pct", "range_pos",
        "rel_vol", "session", "weekday", "trend_100", "htf_1d", "htf_4h")]))
    con.execute("INSERT INTO outcomes VALUES (?,?,?,?,?,?,?,?,?,?)", (iid, *out))
    con.executemany("INSERT INTO votes VALUES (?,?,?,?)", [(iid, *v) for v in votes])


def outcome_row(df, ind, i, d):
    hi, lo, cl = df["high"].values, df["low"].values, df["close"].values
    stop_d = STOP_ATR * ind["atr"][i]; H = HORIZON[LTF]
    ex, r, b, mfe, mae = walk_trade(hi, lo, cl, i, d, stop_d, H)
    oex, orr, *_ = walk_trade(hi, lo, cl, i, -d, stop_d, H)
    step = int(np.median(np.diff(ind["tms"][-50:])) // 60000)
    return (ex, r, round(r - COST_R, 3), b, b * step, round(mfe, 2), round(mae, 2), oex, orr), stop_d


def lab_votes(evg, sym, ts, d):
    """The lab detectors that fired on this symbol and 1h bar (ts in ms), as votes for side d."""
    rows = evg.get((sym, int(ts)))
    return [] if rows is None else [(o["key"], school_of(o["key"]), 1 if int(o["d"]) == d else -1) for _, o in rows.iterrows()]


def fill_lab_evidence(con, keys):
    from modules.lab_tiers import card
    con.executemany("INSERT OR REPLACE INTO lab_evidence VALUES (?,?,?,?,?,?)",
                    [(c["key"], c["school"], c["tf"], c["n"], c["net"], c["verdict"]) for c in card(sorted(keys), LTF)])


def build(desk_path=None, log=print, tg_path=None):
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB); con.executescript(SCHEMA)
    ev = pd.read_csv(EVENTS) if EVENTS.exists() else pd.DataFrame()
    evg = {(s, int(t)): g for (s, t), g in ev.groupby(["sym", "ts"])} if len(ev) else {}
    frames = {}
    for sym, g in ev.groupby("sym") if len(ev) else []:
        try:
            frames[sym] = frame(sym)
        except Exception as e:
            log(f"skip {sym}: {type(e).__name__} {e}"); continue
        df, ind = frames[sym]
        pos = {t: k for k, t in enumerate(ind["tms"])}
        by_bar = g.groupby("ts")
        n = 0
        for ts, rows in by_bar:
            i = pos.get(int(ts))
            if i is None or not ind["atr"][i] > 0:
                continue
            for _, e in rows.iterrows():
                d = int(e["d"]); out, stop_d = outcome_row(df, ind, i, d)
                ctx = context(df, ind, i, d) | {"trend_100": e["trend"], "htf_1d": e.get("htf_1d"), "htf_4h": e.get("htf_4h")}
                cl = df["close"].values[i]
                idea = {"source": "lab", "symbol": sym, "tf": LTF, "ts": int(ts), "time": str(df["time"].iloc[i]), "side": d, "entry": cl,
                        "stop": cl - d * stop_d, "target": cl + d * RR * stop_d, "key": e["key"], "school": school_of(e["key"]),
                        "taken": None, "status": "signal", "oos": int(bool(e["oos"])), "ext_id": None}
                votes = [(o["key"], school_of(o["key"]), 1 if int(o["d"]) == d else -1) for _, o in rows.iterrows() if o["key"] != e["key"]]
                insert(con, idea, ctx, out, votes); n += 1
        log(f"{sym}: {n} lab ideas")
    if desk_path:
        add_desk(con, desk_path, frames, log, evg)
    if tg_path:
        add_telegram(con, tg_path, frames, log, evg)
    fill_lab_evidence(con, set(ev["key"]) if len(ev) else set())
    con.commit()
    log(f"wrote {DB}: " + ", ".join(f"{t}={con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]}" for t in ("ideas", "context", "votes", "outcomes")))
    con.close()


def _frame_for(frames, sym, log, tag):
    if sym not in frames:
        try:
            frames[sym] = frame(sym)
        except Exception as e:
            log(f"{tag} skip {sym}: {e}"); return None
    return frames[sym]


def add_desk(con, path, frames, log, evg=None):
    src = sqlite3.connect(f"file:{path}?mode=ro", uri=True); src.row_factory = sqlite3.Row
    n = 0
    for r in src.execute("SELECT * FROM ideas ORDER BY id"):
        sym = DESK_MAP.get(r["symbol"])
        if not sym:
            continue
        fr = _frame_for(frames, sym, log, "desk")
        if fr is None:
            continue
        df, ind = fr
        t = pd.Timestamp(r["created"])
        ts = int((t.tz_convert("UTC").tz_localize(None) if t.tzinfo else t).value // 10**6)   # feed candle times are naive UTC
        i = int(np.searchsorted(ind["tms"], ts, side="right") - 1)
        if i < 210 or not ind["atr"][i] > 0:
            continue
        d = int(r["direction"]); out, _ = outcome_row(df, ind, i, d)
        ctx = context(df, ind, i, d) | {"trend_100": None, "htf_1d": None, "htf_4h": None}
        reasons = json.loads(r["reasons"] or "[]")
        idea = {"source": "desk", "symbol": sym, "tf": LTF, "ts": ts, "time": r["created"], "side": d, "entry": r["entry"], "stop": r["stop"],
                "target": r["t1"], "key": "desk", "school": "ai-desk framework", "taken": int(bool(r["filled"])), "status": r["status"],
                "oos": None, "ext_id": f"desk:{r['id']}"}
        insert(con, idea, ctx, out, [(x[:60], "desk reason", 1) for x in reasons] + [(x[:60], "desk doubt", -1) for x in json.loads(r["doubts"] or "[]")]
               + lab_votes(evg or {}, sym, ind["tms"][i], d))
        n += 1
    log(f"desk: {n} ideas mapped to our feeds (lab exit rule applied for comparability; the desk's own result stays in status)")


def telegram_records(path):
    """Readable lines of .signal_log.jsonl with a full plan; a damaged line is skipped (same rule as modules.signal_log.load)."""
    out = []
    for line in Path(path).read_text().splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("symbol") and r.get("dir") in ("bullish", "bearish") and r.get("entry") and r.get("stop") and r.get("t"):
            out.append(r)
    return out


def add_telegram(con, path, frames, log, evg=None):
    n = 0
    for r in telegram_records(path):
        fr = _frame_for(frames, r["symbol"], log, "telegram")
        if fr is None:
            continue
        df, ind = fr
        ts = int(r["t"]) * 1000
        i = int(np.searchsorted(ind["tms"], ts, side="right") - 1)
        if i < 210 or not ind["atr"][i] > 0:
            continue
        d = 1 if r["dir"] == "bullish" else -1
        out, _ = outcome_row(df, ind, i, d)
        ctx = context(df, ind, i, d) | {"trend_100": None, "htf_1d": None, "htf_4h": None}
        idea = {"source": "telegram", "symbol": r["symbol"], "tf": r.get("tf") or LTF, "ts": ts, "time": str(pd.Timestamp(ts, unit="ms")),
                "side": d, "entry": r["entry"], "stop": r["stop"], "target": r.get("tp1"), "key": "telegram", "school": "scanner alert",
                "taken": int(bool(r.get("sent"))), "status": r.get("out") or "signal", "oos": None, "ext_id": f"tg:{r.get('key')}:{r['t']}"}
        insert(con, idea, ctx, out, lab_votes(evg or {}, r["symbol"], ind["tms"][i], d))
        n += 1
    log(f"telegram: {n} alerts (lab exit rule applied for comparability; taken = sent to Telegram)")


def _args(argv):
    a = {"desk": None, "telegram": None}
    it = iter(argv)
    for x in it:
        if x in ("--desk", "--telegram"):
            a[x[2:]] = next(it, None)
        else:
            a["desk"] = x
    return a


if __name__ == "__main__":
    _a = _args(sys.argv[1:])
    build(_a["desk"], tg_path=_a["telegram"])
