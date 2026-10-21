"""Market map for the Hyperliquid TradFi markets (xyz dex): change over the day, breadth, and each market's strength
against its own asset class. Pure functions on the rows from hl_feed.markets(); nothing here places an order.

Breadth = share of markets up on the day. Relative strength = a market's change minus its class average. These are
descriptive: they show where movement is, not whether it will continue."""
import pandas as pd

from modules.hl_feed import base


def board(rows: list[dict]) -> pd.DataFrame:
    """One row per market: id, name, class, price, change % vs the previous day, 24h volume (USD), and strength vs class."""
    out = []
    for r in rows:
        prev, px = float(r.get("prev") or 0), float(r.get("px") or 0)
        if prev <= 0 or px <= 0:
            continue   # no reference price: the change would be meaningless
        out.append({"id": r["id"], "name": base(r["id"]), "cls": r.get("cls") or "Other", "px": px,
                    "chg": (px / prev - 1) * 100, "vol": float(r.get("vol") or 0)})
    df = pd.DataFrame(out, columns=["id", "name", "cls", "px", "chg", "vol"])
    if df.empty:
        return df
    df["class_avg"] = df.groupby("cls")["chg"].transform("mean")
    df["rel"] = df["chg"] - df["class_avg"]
    return df.sort_values("vol", ascending=False).reset_index(drop=True)


def breadth(df: pd.DataFrame) -> dict:
    """Share of markets up, share down, and the median change. Empty board -> NaN values."""
    if df.empty:
        return {"n": 0, "up_share": float("nan"), "down_share": float("nan"), "median_chg": float("nan")}
    return {"n": int(len(df)), "up_share": float((df["chg"] > 0).mean()), "down_share": float((df["chg"] < 0).mean()),
            "median_chg": float(df["chg"].median())}


def by_class(df: pd.DataFrame) -> pd.DataFrame:
    """Per asset class: how many markets, the average change, and the share up. Strongest class first."""
    if df.empty:
        return pd.DataFrame(columns=["cls", "n", "avg_chg", "up_share"])
    g = df.groupby("cls").agg(n=("id", "count"), avg_chg=("chg", "mean"), up_share=("chg", lambda s: (s > 0).mean()))
    return g.sort_values("avg_chg", ascending=False).reset_index().rename(columns={"index": "cls"})
