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


def ladder_html(ladder: pd.DataFrame, big_mult: float = 3.0) -> str:
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

    rows = []
    spread_done = False
    for _, r in ladder.iterrows():
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
            bid_cell = _bar_cell(fmt_qty(r["bid_qty"]), w, GREEN, "right", big)
        if r["ask_qty"] > 0:
            w = max(4, int(100 * r["ask_qty"] / max_q))
            big = med_q and r["ask_qty"] >= big_mult * med_q
            ask_cell = _bar_cell(fmt_qty(r["ask_qty"]), w, RED, "left", big)

        color = RED if r["side"] == "ask" else GREEN
        rows.append(
            "<tr>"
            f"<td style='width:38%'>{bid_cell}</td>"
            f"<td style='width:24%;text-align:center;color:{color};font-weight:600;"
            f"font-size:12px'>{fmt_price(r['price'])}</td>"
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


def _bar_cell(text: str, width_pct: int, color: str, align: str, big: bool) -> str:
    # bars grow towards the price column: bids from the right, asks from the left
    anchor = "right" if align == "right" else "left"
    border = f"border:1px solid {GOLD};" if big else ""
    flag = "&#9733; " if big else ""
    return (
        f"<div style='position:relative;height:18px;{border}'>"
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
    rows = []
    for _, r in t.iterrows():
        col = GREEN if r["side"] == "Buy" else RED
        tier = r["tier"]
        tag = {"whale": "WHALE", "smart": "SMART"}.get(tier, "")
        weight = "700" if tier != "normal" else "400"
        bg = {"whale": "rgba(240,185,11,.22)", "smart": "rgba(240,185,11,.10)"}.get(tier, "transparent")
        rows.append(
            f"<tr style='background:{bg};color:{col};font-weight:{weight};font-size:12px'>"
            f"<td style='color:{MUTED};font-weight:400'>{r['time'].strftime('%H:%M:%S')}</td>"
            f"<td>{fmt_price(r['price'])}</td>"
            f"<td style='text-align:right'>{fmt_qty(r['qty'])}</td>"
            f"<td style='text-align:right;color:#eaecef;font-weight:400'>&#36;{r['notional']:,.0f}</td>"
            f"<td style='color:{GOLD};font-size:10px'>{tag}</td></tr>"
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


def limit_events_html(events: pd.DataFrame, max_rows: int = 15) -> str:
    if events.empty:
        return (
            "<div style='color:#848e9c;font-size:12px'>Watching for big limit orders... "
            "events appear here as the book changes between refreshes.</div>"
        )
    colors = {"PLACED": "#4aa3ff", "PULLED": GOLD, "FILLED": MUTED}
    notes = {"PLACED": "new big order", "PULLED": "removed w/o trading - possible fake wall",
             "FILLED": "traded through"}
    rows = []
    for _, r in events.head(max_rows).iterrows():
        side_col = GREEN if r["side"] == "bid" else RED
        c = colors.get(r["event"], "#eaecef")
        rows.append(
            "<tr style='font-size:12px'>"
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
