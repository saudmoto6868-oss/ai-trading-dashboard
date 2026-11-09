"""Tests for the shared Academy Intelligence core (no network/API calls)."""
import json
import tempfile
from pathlib import Path

from modules.academy_intelligence import (
    initialize, upsert_record, search_records, promotion_gate, import_legacy_lessons,
)


def run():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "academy.sqlite3"
        initialize(db)
        rid = upsert_record({
            "id": "test-1", "title": "Liquidity sweep", "summary": "Sweep and reclaim.",
            "topic": "Liquidity", "school": "smc", "claim_type": "hypothesis",
            "asset": "XAUUSD", "timeframe": "M5", "provenance": [{"url": "https://example.org"}],
        }, db)
        assert rid == "test-1"
        rows = search_records("sweep", asset="XAUUSD", path=db)
        assert len(rows) == 1 and rows[0]["id"] == rid
        assert rows[0]["provenance"][0]["url"] == "https://example.org"
        try:
            upsert_record({
                "title": "Unsafe source", "summary": "Should be rejected.",
                "topic": "Security", "claim_type": "fact", "source_url": "javascript:alert(1)",
            }, db)
            raise AssertionError("non-HTTP source URLs should be rejected")
        except ValueError:
            pass
        assert search_records(topic="Liquidity", status="inbox", path=db)
        try:
            upsert_record({"title": "bad"}, db)
            raise AssertionError("required fields should be enforced")
        except ValueError:
            pass
        ok, reasons = promotion_gate({"claim_type": "hypothesis", "evidence_grade": "unreviewed"})
        assert not ok and reasons
        ok, reasons = promotion_gate({
            "claim_type": "empirically_validated", "evidence_grade": "validated",
            "details": {"sample_size": 150, "out_of_sample": True,
                        "costs_included": True, "lookahead_checked": True}
        })
        assert ok and not reasons

        legacy = Path(td) / "academy.json"
        legacy.write_text(json.dumps({"lessons": [{
            "id": "legacy-one", "title": "Legacy lesson", "summary": "Imported",
            "topic": "Order flow", "status": "draft", "verdict": "hypothesis",
            "sources": ["https://example.org"], "points": ["A"], "caveats": ["B"]
        }]}), encoding="utf-8")
        assert import_legacy_lessons(db, legacy) == 1
        assert import_legacy_lessons(db, legacy) == 1  # idempotent upsert
        legacy_rows = search_records("Legacy lesson", path=db)
        assert len(legacy_rows) == 1 and legacy_rows[0]["status"] == "review"
    print("PASS: academy intelligence core")


if __name__ == "__main__":
    run()
