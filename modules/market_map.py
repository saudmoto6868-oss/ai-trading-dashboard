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


SORTS = ("vol", "chg", "chg_abs", "rel")


def apply_filters(df: pd.DataFrame, classes=None, top_n: int = 0, direction: str = "all", min_abs: float = 0.0, q: str = "", sort: str = "vol") -> pd.DataFrame:
    """Heat-map filters (owner 2026-10-23: they did nothing). classes = keep only these asset classes (empty / None = all), top_n = the N biggest by 24h volume
    after the other filters (0 = all), direction = all | up | down, min_abs = smallest |change %|, q = text in the name, sort = vol | chg | chg_abs | rel."""
    if df.empty:
        return df
    out = df
    if classes:
        out = out[out["cls"].isin(list(classes))]
    if direction == "up":
        out = out[out["chg"] > 0]
    elif direction == "down":
        out = out[out["chg"] < 0]
    if min_abs:
        out = out[out["chg"].abs() >= float(min_abs)]
    if q and q.strip():
        out = out[out["name"].str.contains(q.strip(), case=False, regex=False)]
    if top_n and top_n > 0:
        out = out.sort_values("vol", ascending=False).head(int(top_n))
    key = sort if sort in SORTS else "vol"
    if key == "chg_abs":
        out = out.assign(_k=out["chg"].abs()).sort_values("_k", ascending=False).drop(columns="_k")
    else:
        out = out.sort_values(key, ascending=False)
    return out.reset_index(drop=True)
