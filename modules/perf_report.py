"""
OPTIONAL helpers around two third-party libraries. Nothing in the dashboard depends on them: every function works
without them (own implementation) and only uses the library when it is installed.

  pip install -r requirements-extra.txt        # QuantStats + pandas-ta (kept out of requirements.txt so the Streamlit deploy stays light)

  perf_stats(returns)        -> dict of Sharpe / Sortino / max drawdown / CAGR / win rate  (own code; QuantStats numbers when available)
  quantstats_html(returns)   -> HTML tearsheet string, or None when QuantStats is not installed
  ta_extra(df)               -> df + RSI / MACD / ATR / Bollinger columns via pandas-ta when installed, else the same via own code
returns = pandas Series of per-period fractional returns (e.g. 0.012 = +1.2 %), index = time.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _periods_per_year(idx) -> float:
    try:
        d = pd.Series(pd.to_datetime(idx)).diff().dropna().median()
        return float(365.25 * 86400 / d.total_seconds()) if d.total_seconds() > 0 else 252.0
    except Exception:
        return 252.0


def perf_stats(returns: pd.Series) -> dict:
    r = pd.Series(returns).dropna().astype(float)
    if len(r) < 5:
        return {"n": int(len(r))}
    ppy = _periods_per_year(r.index) if isinstance(r.index, pd.DatetimeIndex) else 252.0
    eq = (1 + r).cumprod()
    dd = eq / eq.cummax() - 1
    sd, dsd = r.std(ddof=1), r[r < 0].std(ddof=1)
    years = len(r) / ppy
    out = {
        "n": int(len(r)), "total_return": float(eq.iloc[-1] - 1),
        "cagr": float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 and eq.iloc[-1] > 0 else float("nan"),
        "sharpe": float(r.mean() / sd * np.sqrt(ppy)) if sd and sd > 0 else float("nan"),
        "sortino": float(r.mean() / dsd * np.sqrt(ppy)) if dsd and dsd > 0 else float("nan"),
        "max_drawdown": float(dd.min()), "win_rate": float((r > 0).mean()),
        "source": "own",
    }
    try:
        import quantstats as qs   # same metrics from the library when present (it may differ slightly in conventions)
        out.update({"sharpe": float(qs.stats.sharpe(r, periods=ppy)), "sortino": float(qs.stats.sortino(r, periods=ppy)),
                    "max_drawdown": float(qs.stats.max_drawdown(r)), "source": "quantstats"})
    except Exception:
        pass
    return out


def quantstats_html(returns: pd.Series, benchmark: pd.Series | None = None, title: str = "Strategy") -> str | None:
    """Full QuantStats tearsheet as an HTML string (show it with streamlit.components.v1.html), None if not installed."""
    try:
        import os, tempfile
        import quantstats as qs
    except Exception:
        return None
    path = os.path.join(tempfile.mkdtemp(), "qs.html")
    qs.reports.html(pd.Series(returns).dropna(), benchmark=benchmark, title=title, output=path)
    with open(path, encoding="utf-8") as f:
        return f.read()


def ta_extra(df: pd.DataFrame) -> pd.DataFrame:
    """Add rsi14 / macd / macd_sig / atr14 / bb_lo / bb_hi columns (candles with open/high/low/close)."""
    out = df.copy()
    try:
        try:
            import pandas_ta_classic as ta   # maintained fork (pip install pandas-ta-classic)
        except ImportError:
            import pandas_ta as ta           # original package
        out["rsi14"] = ta.rsi(out["close"], length=14)
        m = ta.macd(out["close"])
        out["macd"], out["macd_sig"] = m.iloc[:, 0], m.iloc[:, 2]
        out["atr14"] = ta.atr(out["high"], out["low"], out["close"], length=14)
        b = ta.bbands(out["close"], length=20)
        out["bb_lo"], out["bb_hi"] = b.iloc[:, 0], b.iloc[:, 2]
        return out
    except Exception:
        pass
    c = out["close"]
    d = c.diff(); up, dn = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(), (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    out["rsi14"] = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    ema = lambda s, n: s.ewm(span=n, adjust=False).mean()
    out["macd"] = ema(c, 12) - ema(c, 26); out["macd_sig"] = ema(out["macd"], 9)
    pc = c.shift(1)
    tr = pd.concat([out["high"] - out["low"], (out["high"] - pc).abs(), (out["low"] - pc).abs()], axis=1).max(axis=1)
    out["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    ma, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    out["bb_lo"], out["bb_hi"] = ma - 2 * sd, ma + 2 * sd
    return out
