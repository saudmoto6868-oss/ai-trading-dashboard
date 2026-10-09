"""
THE ORDER-FLOW DESK
Pure-logic helpers (no Streamlit imports, so they are easy to test) for the
Crypto tab's professional-style panels:

  * build_ladder()        - bids + asks merged into ONE price ladder (DOM style)
  * classify_trades()     - flags large prints as "Smart" / "Whale" trades
  * LimitTracker          - remembers the previous order-book snapshot and
                            logs big limit orders that were PLACED, PULLED
                            (vanished without trading = possible fake wall)
                            or FILLED (price traded through them).
  * *_html() functions    - turn the above into compact HTML for st.markdown.

Everything is built independently from public order-book / trade data.
Limit tracking is snapshot-based: it can only see changes between page
refreshes (every ~20s), not every individual cancel, so treat "pulled" as a
hint, not proof of spoofing.
"""

from __future__ import annotations

import html
from collections import deque
from datetime import datetime, timezone

import pandas as pd

GREEN = "#0ecb81"
RED = "#f6465d"
GOLD = "#f0b90b"
MUTED = "#848e9c"



# --------------------------------------------------------------------------
# Live visual feedback (colors + flash / pulse animations)
# --------------------------------------------------------------------------
# Animations replay whenever the panel is re-rendered, so only rows/levels
# that carry an animated class (new print, level just hit, big order...) move;
# everything else stays still. That is what makes the pace "feelable".

ORDERFLOW_CSS = """
@keyframes of-flash-buy{0%{background:rgba(14,203,129,.65)}100%{background:transparent}}
@keyframes of-flash-sell{0%{background:rgba(246,70,93,.65)}100%{background:transparent}}
@keyframes of-glow{0%{box-shadow:0 0 0 0 rgba(240,185,11,.0)}50%{box-shadow:0 0 9px 2px rgba(240,185,11,.85)}100%{box-shadow:0 0 0 0 rgba(240,185,11,.0)}}
@keyframes of-hot{0%,100%{box-shadow:0 0 2px 0 rgba(255,255,255,.2);filter:brightness(1)}50%{box-shadow:0 0 12px 3px rgba(255,255,255,.9);filter:brightness(1.6)}}
@keyframes of-absorb{0%,100%{background:rgba(181,124,255,.15)}50%{background:rgba(181,124,255,.55)}}
@keyframes of-grow{0%{outline:2px solid rgba(74,163,255,.95)}100%{outline:2px solid rgba(74,163,255,0)}}
@keyframes of-blink{0%,100%{opacity:1}50%{opacity:.25}}
.of-new-buy{animation:of-flash-buy 1.4s ease-out 1}
.of-new-sell{animation:of-flash-sell 1.4s ease-out 1}
.of-whale-new{animation:of-flash-buy 1.4s ease-out 1,of-blink .5s linear 4}
.of-smart-new{animation:of-blink .6s linear 2}
.of-absorb{animation:of-absorb 1.1s ease-in-out infinite}
.of-big{animation:of-glow 1.8s ease-in-out infinite}
.of-hot{animation:of-hot .55s ease-in-out infinite}
.of-hit-buy{animation:of-flash-buy 1.2s ease-out 1}
.of-hit-sell{animation:of-flash-sell 1.2s ease-out 1}
.of-grow{animation:of-grow 1.3s ease-out 1}
.of-ev-new{animation:of-blink .5s linear 4}
.of-abs-tag{color:#b57cff;font-weight:700}
@media (prefers-reduced-motion:reduce){[class*="of-"]{animation:none!important}}
"""

LEGEND_HTML = (
    "<div style='font-size:11px;color:#848e9c;line-height:1.6'>"
    "<span style='color:#0ecb81'>&#9632;</span> buy &nbsp;"
    "<span style='color:#f6465d'>&#9632;</span> sell &nbsp;"
    "<span style='color:#f0b90b'>&#9632;</span> big/SMART/WHALE (blinks) &nbsp;"
    "<span style='color:#b57cff'>&#9632;</span> absorption &nbsp;"
    "<span style='color:#4aa3ff'>&#9632;</span> level grew &nbsp;"
    "flash = new print / level just traded</div>"
)


def _k(p) -> float:
    return round(float(p), 8)


class TapeMemory:
    """Remembers which prints were already shown so only NEW ones flash.
    The first call after creation (or after a long gap) flashes nothing."""

    def __init__(self, keep: int = 600, stale_after: float = 120.0):
        self.seen: set = set()
        self.order: deque = deque(maxlen=keep)
        self.last_ts = None
        self.stale_after = stale_after

    def mark(self, trades: pd.DataFrame) -> pd.DataFrame:
        if trades is None or trades.empty:
            return trades
        t = trades.copy()
        now = datetime.now(timezone.utc)
        if self.last_ts is not None and (now - self.last_ts).total_seconds() > self.stale_after:
            self.seen.clear()
            self.order.clear()
        first = not self.seen
        self.last_ts = now
        keys = [(r.time, _k(r.price), float(r.qty), r.side) for r in t.itertuples()]
        t["is_new"] = [(not first) and (k not in self.seen) for k in keys]
        for k in keys:
            if k not in self.seen:
                if len(self.order) == self.order.maxlen:
                    self.seen.discard(self.order[0])
                self.order.append(k)
                self.seen.add(k)
        return t


class DomMemory:
    """Remembers the previous ladder so levels that GREW / SHRANK can flash."""

    def __init__(self, grow_pct: float = 0.25, stale_after: float = 120.0):
        self.prev: dict | None = None
        self.grow_pct = grow_pct
        self.last_ts = None
        self.stale_after = stale_after

    def changes(self, ladder: pd.DataFrame) -> dict:
        """price -> 'grow' for levels whose size rose by >= grow_pct (or are new)."""
        now = datetime.now(timezone.utc)
        if self.last_ts is not None and (now - self.last_ts).total_seconds() > self.stale_after:
            self.prev = None
        self.last_ts = now
        cur = {_k(r.price): float(r.bid_qty + r.ask_qty) for r in ladder.itertuples()}
        out = {}
        if self.prev is not None:
            for p, q in cur.items():
                old = self.prev.get(p)
                if old is None or q >= old * (1 + self.grow_pct):
                    out[p] = "grow"
        self.prev = cur
        return out


def hits_from(trades: pd.DataFrame) -> dict:
    """price -> 'Buy'/'Sell' for the NEW prints (needs the is_new column)."""
    if trades is None or trades.empty or "is_new" not in trades.columns:
        return {}
    out = {}
    for r in trades[trades["is_new"]].sort_values("time").itertuples():
        out[_k(r.price)] = r.side
    return out


def mark_absorption(trades: pd.DataFrame, vol_mult: float = 3.0, range_pct: float = 0.05,
                    min_prints: int = 4) -> pd.DataFrame:
    """Adds 'absorb' (bool) and 'absorb_dir'.
    Absorption = lots of volume trading at ONE price level while the whole
    window barely moved (range <= range_pct percent of price). Aggressive
    BUYING absorbed by a passive seller -> 'sellers' (bearish hint); aggressive
    SELLING absorbed by a passive buyer -> 'buyers' (bullish hint)."""
    if trades is None or trades.empty:
        return trades
    t = trades.copy()
    t["absorb"] = False
    t["absorb_dir"] = ""
    if len(t) < 10:
        return t
    mid = float(t["price"].median())
    if mid <= 0 or (float(t["price"].max()) - float(t["price"].min())) / mid * 100 > range_pct:
        return t
    lvl = t.groupby("price")["qty"].agg(["sum", "count"])
    med = float(lvl["sum"].median()) or 1e-12
    hot = lvl[(lvl["sum"] >= vol_mult * med) & (lvl["count"] >= min_prints)]
    for price in hot.index:
        m = t["price"] == price
        buy = float(t.loc[m & (t["side"] == "Buy"), "qty"].sum())
        sell = float(t.loc[m & (t["side"] == "Sell"), "qty"].sum())
        t.loc[m, "absorb"] = True
        t.loc[m, "absorb_dir"] = "sellers" if buy >= sell else "buyers"
    return t


def tape_stats(trades: pd.DataFrame) -> dict:
    """Pace (prints/sec), buy/sell volume split and delta over the fetched window."""
    if trades is None or trades.empty:
        return {"pace": 0.0, "buy_pct": 50.0, "delta": 0.0, "n": 0}
    span = (trades["time"].max() - trades["time"].min()).total_seconds()
    buy = float(trades.loc[trades["side"] == "Buy", "qty"].sum())
    sell = float(trades.loc[trades["side"] == "Sell", "qty"].sum())
    tot = buy + sell
    return {
        "pace": len(trades) / span if span > 0 else float(len(trades)),
        "buy_pct": 100 * buy / tot if tot else 50.0,
        "delta": buy - sell,
        "n": len(trades),
    }


def stats_html(stats: dict, absorbed: str = "") -> str:
    bp = max(0.0, min(100.0, stats["buy_pct"]))
    d = stats["delta"]
    dc = GREEN if d >= 0 else RED
    ab = f" &nbsp;<span class='of-abs-tag of-absorb'>ABSORB {html.escape(absorbed)}</span>" if absorbed else ""
    return (
        "<div style='font-size:11px;color:#848e9c;margin-bottom:4px'>"
        f"pace <b style='color:#eaecef'>{stats['pace']:.1f}</b>/s &nbsp;"
        f"delta <b style='color:{dc}'>{fmt_qty(abs(d))}{'+' if d >= 0 else '-'}</b>{ab}"
        f"<div style='display:flex;height:5px;margin-top:3px;border-radius:2px;overflow:hidden'>"
        f"<div style='width:{bp:.0f}%;background:{GREEN}'></div>"
        f"<div style='width:{100 - bp:.0f}%;background:{RED}'></div></div></div>"
    )


# --------------------------------------------------------------------------
# Depth-of-market ladder
# --------------------------------------------------------------------------

def build_ladder(bids: pd.DataFrame, asks: pd.DataFrame, depth: int = 12) -> pd.DataFrame:
    """One unified ladder, highest price on top.
    Columns: price, bid_qty, ask_qty, side ("ask"/"bid"). Asks above the
    spread, bids below it - never two separate tables."""
    a = asks.sort_values("price").head(depth).copy()
    b = bids.sort_values("price", ascending=False).head(depth).copy()
    a["ask_qty"], a["bid_qty"], a["side"] = a["qty"], 0.0, "ask"
    b["bid_qty"], b["ask_qty"], b["side"] = b["qty"], 0.0, "bid"
    ladder = pd.concat([a, b])[["price", "bid_qty", "ask_qty", "side"]]
    return ladder.sort_values("price", ascending=False).reset_index(drop=True)


def fmt_price(p: float) -> str:
    if p >= 1000:
        return f"{p:,.2f}"
    if p >= 1:
        return f"{p:,.4f}"
    return f"{p:.6f}"


def fmt_qty(q: float) -> str:
    if q >= 1000:
        return f"{q:,.0f}"
    if q >= 1:
        return f"{q:,.2f}"
    return f"{q:.4f}"


def ladder_html(ladder: pd.DataFrame, big_mult: float = 3.0, hits: dict | None = None,
                changes: dict | None = None, absorb_prices: set | None = None) -> str:
    """Heat-bar ladder: bid size | price | ask size. Levels whose size is
    >= big_mult x the median level size are highlighted as 'big' orders."""
    if ladder.empty:
        return "<div style='color:#848e9c'>No order book data.</div>"

    sizes = pd.concat([ladder["bid_qty"], ladder["ask_qty"]])
    sizes = sizes[sizes > 0]
    max_q = float(sizes.max()) if not sizes.empty else 1.0
    med_q = float(sizes.median()) if not sizes.empty else 0.0

    best_ask = ladder.loc[ladder["side"] == "ask", "price"].min()
    best_bid = ladder.loc[ladder["side"] == "bid", "price"].max()

    hits = hits or {}
    changes = changes or {}
    absorb_prices = absorb_prices or set()
    rows = []
    spread_done = False
    for _, r in ladder.iterrows():
        pk = _k(r["price"])
        hit = hits.get(pk)
        grew = changes.get(pk) == "grow"
        # spread marker between the last ask row and the first bid row
        if r["side"] == "bid" and not spread_done:
            if pd.notna(best_ask) and pd.notna(best_bid):
                spread = best_ask - best_bid
                rows.append(
                    f"<tr><td colspan='3' style='text-align:center;color:{GOLD};"
                    f"font-size:11px;padding:2px 0;border-top:1px solid #2b3139;"
                    f"border-bottom:1px solid #2b3139'>spread {fmt_price(spread)}</td></tr>"
                )
            spread_done = True

        bid_cell = ask_cell = ""
        if r["bid_qty"] > 0:
            w = max(4, int(100 * r["bid_qty"] / max_q))
            big = med_q and r["bid_qty"] >= big_mult * med_q
            bid_cell = _bar_cell(fmt_qty(r["bid_qty"]), w, GREEN, "right", big, bool(big and hit), grew)
        if r["ask_qty"] > 0:
            w = max(4, int(100 * r["ask_qty"] / max_q))
            big = med_q and r["ask_qty"] >= big_mult * med_q
            ask_cell = _bar_cell(fmt_qty(r["ask_qty"]), w, RED, "left", big, bool(big and hit), grew)

        color = RED if r["side"] == "ask" else GREEN
        pcls = ""
        if pk in absorb_prices:
            pcls = "of-absorb"
        elif hit:
            pcls = "of-hit-buy" if hit == "Buy" else "of-hit-sell"
        mark = " <span class='of-abs-tag'>ABS</span>" if pk in absorb_prices else ""
        rows.append(
            "<tr>"
            f"<td style='width:38%'>{bid_cell}</td>"
            f"<td class='{pcls}' style='width:24%;text-align:center;color:{color};font-weight:600;"
            f"font-size:12px'>{fmt_price(r['price'])}{mark}</td>"
            f"<td style='width:38%'>{ask_cell}</td>"
            "</tr>"
        )

    head = (
        f"<tr style='color:{MUTED};font-size:11px'><th>Bid size</th>"
        f"<th>Price</th><th>Ask size</th></tr>"
    )
    return (
        "<table style='width:100%;border-collapse:collapse;font-family:monospace'>"
        + head + "".join(rows) + "</table>"
    )


def _bar_cell(text: str, width_pct: int, color: str, align: str, big: bool,
              hot: bool = False, grew: bool = False) -> str:
    # bars grow towards the price column: bids from the right, asks from the left
    anchor = "right" if align == "right" else "left"
    border = f"border:1px solid {GOLD};" if big else ""
    flag = "&#9733; " if big else ""
    cls = "of-hot" if hot else ("of-big" if big else ("of-grow" if grew else ""))
    return (
        f"<div class='{cls}' style='position:relative;height:18px;{border}'>"
        f"<div style='position:absolute;top:0;{anchor}:0;height:100%;width:{width_pct}%;"
        f"background:{color};opacity:.28'></div>"
        f"<div style='position:relative;text-align:{align};padding:0 4px;font-size:11px;"
        f"line-height:18px;color:#eaecef'>{flag}{text}</div></div>"
    )


# --------------------------------------------------------------------------
# Smart-trade classification (time & sales)
# --------------------------------------------------------------------------

def classify_trades(trades: pd.DataFrame, smart_mult: float = 4.0, whale_mult: float = 10.0) -> pd.DataFrame:
    """Adds notional + 'tier' (normal/smart/whale). Size is judged relative to
    the median print in the fetched window, so it adapts per symbol (a 'big'
    BTC print and a 'big' XRP print are different absolute numbers)."""
    if trades is None or trades.empty:
        return pd.DataFrame(columns=["time", "price", "qty", "side", "notional", "tier"])
    t = trades.copy()
    t["notional"] = t["price"] * t["qty"]
    med = float(t["qty"].median()) or 1e-12
    t["tier"] = "normal"
    t.loc[t["qty"] >= smart_mult * med, "tier"] = "smart"
    t.loc[t["qty"] >= whale_mult * med, "tier"] = "whale"
    return t


def trades_html(trades: pd.DataFrame, max_rows: int = 25) -> str:
    if trades.empty:
        return "<div style='color:#848e9c'>No trades.</div>"
    t = trades.sort_values("time", ascending=False).head(max_rows)
    has_new = "is_new" in t.columns
    has_abs = "absorb" in t.columns
    rows = []
    for _, r in t.iterrows():
        buy = r["side"] == "Buy"
        col = GREEN if buy else RED
        tier = r["tier"]
        new = bool(r["is_new"]) if has_new else False
        absorb = bool(r["absorb"]) if has_abs else False
        tag = {"whale": "WHALE", "smart": "SMART"}.get(tier, "")
        if absorb:
            tag = (tag + " " if tag else "") + "ABSORB"
        weight = "700" if tier != "normal" else "400"
        bg = {"whale": "rgba(240,185,11,.22)", "smart": "rgba(240,185,11,.10)"}.get(tier, "transparent")
        cls = ""
        if absorb:
            cls = "of-absorb"
        elif new and tier == "whale":
            cls = "of-whale-new"
        elif new and tier == "smart":
            cls = "of-smart-new " + ("of-new-buy" if buy else "of-new-sell")
        elif new:
            cls = "of-new-buy" if buy else "of-new-sell"
        rows.append(
            f"<tr class='{cls}' style='background:{bg};color:{col};font-weight:{weight};font-size:12px'>"
            f"<td style='color:{MUTED};font-weight:400'>{r['time'].strftime('%H:%M:%S')}</td>"
            f"<td>{fmt_price(r['price'])}</td>"
            f"<td style='text-align:right'>{fmt_qty(r['qty'])}</td>"
            f"<td style='text-align:right;color:#eaecef;font-weight:400'>&#36;{r['notional']:,.0f}</td>"
            f"<td style='color:{'#b57cff' if absorb else GOLD};font-size:10px'>{tag}</td></tr>"
        )
    head = (
        f"<tr style='color:{MUTED};font-size:11px;text-align:left'><th>Time</th><th>Price</th>"
        f"<th style='text-align:right'>Size</th><th style='text-align:right'>Value</th><th></th></tr>"
    )
    return (
        "<table style='width:100%;border-collapse:collapse;font-family:monospace'>"
        + head + "".join(rows) + "</table>"
    )


# --------------------------------------------------------------------------
# Limit tracking (large resting orders appearing / disappearing)
# --------------------------------------------------------------------------

class LimitTracker:
    """Compares consecutive order-book snapshots for ONE symbol.

    A level counts as 'big' when its size >= big_mult x the median level size
    of that side of the book. Between two snapshots:
      * big level not seen before            -> PLACED
      * big level gone / cut by >60 percent  -> FILLED if trades printed
        through its price meanwhile, otherwise PULLED (possible fake wall)
    """

    def __init__(self, big_mult: float = 5.0, keep_events: int = 40):
        self.big_mult = big_mult
        self.prev_big: dict[tuple[str, float], float] | None = None
        self.events: deque = deque(maxlen=keep_events)
        self.last_ts = None

    def _big_levels(self, bids: pd.DataFrame, asks: pd.DataFrame) -> dict:
        out = {}
        for side, df in (("bid", bids), ("ask", asks)):
            if df.empty:
                continue
            med = float(df["qty"].median())
            for p, q in zip(df["price"], df["qty"]):
                if med and q >= self.big_mult * med:
                    out[(side, float(p))] = float(q)
        return out

    def update(self, bids: pd.DataFrame, asks: pd.DataFrame, trades: pd.DataFrame | None = None,
               stale_after: float = 120.0):
        now = datetime.now(timezone.utc)
        # if we were not watching this symbol for a while (user was on another
        # symbol/tab), the old snapshot is meaningless - start a fresh baseline
        if self.last_ts is not None and (now - self.last_ts).total_seconds() > stale_after:
            self.prev_big = None
        self.last_ts = now
        cur = self._big_levels(bids, asks)

        lo = hi = None
        if trades is not None and not trades.empty:
            lo, hi = float(trades["price"].min()), float(trades["price"].max())

        if self.prev_big is not None:
            for (side, price), q in cur.items():
                if (side, price) not in self.prev_big:
                    self.events.appendleft((now, "PLACED", side, price, q))
            for (side, price), old_q in self.prev_big.items():
                new_q = cur.get((side, price), 0.0)
                # a level that simply fell outside the fetched depth window
                # (the market moved away from it) is not a cancel - skip it
                if side == "bid" and (bids.empty or price < float(bids["price"].min())):
                    continue
                if side == "ask" and (asks.empty or price > float(asks["price"].max())):
                    continue
                if new_q < 0.4 * old_q:
                    traded_through = (
                        (side == "ask" and hi is not None and hi >= price)
                        or (side == "bid" and lo is not None and lo <= price)
                    )
                    kind = "FILLED" if traded_through else "PULLED"
                    self.events.appendleft((now, kind, side, price, old_q))

        self.prev_big = cur

    def events_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            list(self.events), columns=["time", "event", "side", "price", "qty"]
        )


def limit_events_html(events: pd.DataFrame, max_rows: int = 15, fresh_secs: float = 30.0) -> str:
    if events.empty:
        return (
            "<div style='color:#848e9c;font-size:12px'>Watching for big limit orders... "
            "events appear here as the book changes between refreshes.</div>"
        )
    colors = {"PLACED": "#4aa3ff", "PULLED": GOLD, "FILLED": MUTED}
    notes = {"PLACED": "new big order", "PULLED": "removed w/o trading - possible fake wall",
             "FILLED": "traded through"}
    rows = []
    now = datetime.now(timezone.utc)
    for _, r in events.head(max_rows).iterrows():
        side_col = GREEN if r["side"] == "bid" else RED
        c = colors.get(r["event"], "#eaecef")
        fresh = (now - r["time"]).total_seconds() <= fresh_secs
        rows.append(
            f"<tr class='{'of-ev-new' if fresh else ''}' style='font-size:12px'>"
            f"<td style='color:{MUTED}'>{r['time'].strftime('%H:%M:%S')}</td>"
            f"<td style='color:{c};font-weight:700'>{html.escape(r['event'])}</td>"
            f"<td style='color:{side_col}'>{'BID' if r['side'] == 'bid' else 'ASK'}</td>"
            f"<td>{fmt_price(r['price'])}</td>"
            f"<td style='text-align:right'>{fmt_qty(r['qty'])}</td>"
            f"<td style='color:{MUTED};font-size:10px'>{notes.get(r['event'], '')}</td></tr>"
        )
    head = (
        f"<tr style='color:{MUTED};font-size:11px;text-align:left'><th>Time</th><th>Event</th>"
        f"<th>Side</th><th>Price</th><th style='text-align:right'>Size</th><th></th></tr>"
    )
    return (
        "<table style='width:100%;border-collapse:collapse;font-family:monospace'>"
        + head + "".join(rows) + "</table>"
    )
