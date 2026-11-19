"""Comprehensive synthetic test suite for new modules (Tasks 1-8)."""
from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.archive_klines import get_klines_archive_first, update_archive_for_symbol
from modules.portfolio_simulator import PropRules, lab_to_portfolio_trades, simulate_portfolio
from modules.market_costs import build_cost_comparison, get_cost
from modules.lab_stats import (
    aggregate_by_regime, apply_bh_correction, block_bootstrap, dedup_clusters,
    oos_split_by_date, run_fill_sensitivity, simulate_limit_fill,
)
from modules.broker_import import compute_mae_mfe, filter_imported_trades, match_trades_with_signals, parse_mt5_csv


class TestDashboardModules(unittest.TestCase):
    def test_1_kline_archive_500_plus_100(self) -> None:
        """Task 1: archive klines, prune old ones."""
        now = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            arch = Path(tmp) / "kline_archive.json"
            base_500 = [
                {
                    "timestamp": (now - timedelta(hours=600 - i)).isoformat(),
                    "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 50,
                }
                for i in range(500)
            ]
            update_archive_for_symbol("HL:GOLD", "1h", base_500, archive_path=arch, now=now)
            new_100 = [
                {
                    "timestamp": (now - timedelta(hours=100 - i)).isoformat(),
                    "open": 101, "high": 102, "low": 100, "close": 101.5, "volume": 60,
                }
                for i in range(100)
            ]
            combined = get_klines_archive_first(
                "HL:GOLD", "1h", live_fetcher=lambda s, tf: new_100, archive_path=arch
            )
            self.assertEqual(len(combined), 600)

    def test_2_portfolio_simulator_100_trades(self) -> None:
        """Task 2: portfolio sim with prop rules."""
        base = datetime(2026, 9, 1, tzinfo=timezone.utc)
        rows = []
        for i in range(100):
            ts = (base + timedelta(days=i // 2, hours=(i % 2) * 4)).isoformat()
            rows.append(
                {
                    "trade_id": i + 1,
                    "symbol": "HL:GOLD",
                    "side": "long",
                    "entry": 2500.0,
                    "stop": 2490.0,
                    "take_profit": 2520.0,
                    "pnl_r": 2.0 if i % 2 == 0 else -1.0,
                    "open_time": ts,
                    "close_time": ts,
                }
            )
        trades = lab_to_portfolio_trades(rows)
        res = simulate_portfolio(trades, PropRules(initial_equity=100_000.0, risk_per_trade_pct=0.01))
        self.assertEqual(res["executed_trades"], 100)
        self.assertEqual(res["win_pct"], 50.0)
        self.assertTrue(res["prop_pass"])
        self.assertGreater(res["final_equity"], 100_000.0)

    def test_3_market_costs(self) -> None:
        """Task 3: cost estimation."""
        self.assertEqual(get_cost("HL:GOLD", "15m"), 0.30)
        self.assertEqual(get_cost("BTC", "1h"), 0.06)
        comp = build_cost_comparison("HL:GOLD", "15m", actual_cost_r=0.28)
        self.assertEqual(comp["cost_actual"], 0.28)

    def test_4_5_clustering_bootstrap_bh(self) -> None:
        """Tasks 4-5: clustering, bootstrap, BH correction."""
        trades = [{"symbol": "BTC", "cluster_id": i // 2, "pnl_r": 0.4 if i % 3 else -0.5} for i in range(1000)]
        unique = dedup_clusters(trades)
        self.assertEqual(len(unique), 500)

        boot = block_bootstrap([t["pnl_r"] for t in unique], n_resamples=100, block_size=5)
        self.assertIn("t_bootstrap", boot)

        rows = [{"id": i, "p_value": 0.0001 if i < 3 else 0.50} for i in range(605)]
        out, msg = apply_bh_correction(rows, alpha=0.05)
        passed = [r for r in out if r["significant_bh"]]
        self.assertEqual(len(passed), 3)

    def test_6_broker_import_mae_mfe(self) -> None:
        """Task 6: broker import and MAE/MFE."""
        base = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "mt5.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["timestamp", "symbol", "type", "entry", "stop", "tp", "profit"])
                for i in range(10):
                    w.writerow([
                        (base + timedelta(minutes=i * 30)).isoformat(),
                        "XAUUSD", "buy", 2500.0, 2490.0, 2520.0, 100.0 if i < 5 else -50.0
                    ])
            broker_trades = parse_mt5_csv(csv_path)
            self.assertEqual(len(broker_trades), 10)

        candles = [{"high": 2515.0, "low": 2495.0}, {"high": 2518.0, "low": 2496.0}]
        ex = compute_mae_mfe({"entry": 2500.0, "stop": 2490.0, "tp": 2520.0, "side": "buy"}, candles)
        self.assertEqual(ex["mae_points"], 5.0)
        self.assertEqual(ex["mfe_points"], 18.0)

    def test_7_limit_fill_realism(self) -> None:
        """Task 7: realistic fill simulation (default fill_distance=0.0)."""
        self.assertTrue(simulate_limit_fill(100.0, "sell", 100.3, fill_distance=0.0))
        self.assertFalse(simulate_limit_fill(100.0, "sell", 99.9, fill_distance=0.5))
        sens = run_fill_sensitivity([{"order_price": 100.0, "side": "sell", "candle_close": 100.6}])
        self.assertEqual(sens[0]["filled_count"], 1)

    def test_8_regime_breakdown(self) -> None:
        """Task 8: regime aggregation."""
        trades = [
            {"regime": "Trend Up", "pnl_r": 1.0},
            {"regime": "Trend Up", "pnl_r": -0.5},
            {"regime": "Range", "pnl_r": 0.8},
        ]
        agg = {r["regime"]: r for r in aggregate_by_regime(trades)}
        self.assertEqual(agg["Trend Up"]["n"], 2)
        self.assertEqual(agg["Range"]["regime_avg_r"], 0.8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
