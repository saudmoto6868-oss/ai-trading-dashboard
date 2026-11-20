"""Tests for the shared Academy Intelligence core (no network/API calls)."""
import json
import tempfile
from pathlib import Path

from modules.academy_intelligence import (
    initialize, upsert_record, search_records, promotion_gate, import_legacy_lessons,
    review_record, list_review_events,
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
        review_record(rid, "accept", "Source is useful context, not a tested edge.",
                      source_class="secondary", actor="owner", path=db)
        accepted = search_records("sweep", path=db)[0]
        assert accepted["status"] == "accepted"
        assert accepted["evidence_grade"] == "unreviewed"
        assert accepted["details"]["source_class"] == "secondary"
        review_record(rid, "return_to_review", "Need independent replication.",
                      source_class="primary", path=db)
        events = list_review_events(rid, path=db)
        assert [event["decision"] for event in events] == ["accept", "return_to_review"]
        assert events[0]["reason"] == "Source is useful context, not a tested edge."
        assert search_records("sweep", path=db)[0]["evidence_grade"] == "unreviewed"
        for kwargs in (
            {"decision": "approve", "reason": "x"},
            {"decision": "reject", "reason": ""},
            {"decision": "reject", "reason": "x", "source_class": "endorsement"},
        ):
            try:
                review_record(rid, kwargs.pop("decision"), kwargs.pop("reason"), path=db, **kwargs)
                raise AssertionError("invalid review input should be rejected")
            except ValueError:
                pass
        try:
            upsert_record({
                "title": "Unsafe source", "summary": "Should be rejected.",
                "topic": "Security", "claim_type": "fact", "source_url": "javascript:alert(1)",
            }, db)
            raise AssertionError("non-HTTP source URLs should be rejected")
        except ValueError:
            pass
        # after return_to_review the record is back in "review" (REVIEW_DECISIONS), so the status filter must find it there, not under accepted
        assert search_records(topic="Liquidity", status="review", path=db)
        assert not search_records(topic="Liquidity", status="accepted", path=db)
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
        assert import_legacy_lessons(db, legacy) == 1
        legacy_rows = search_records("Legacy lesson", path=db)
        assert len(legacy_rows) == 1 and legacy_rows[0]["status"] == "inbox"
        assert legacy_rows[0]["claim_type"] == "hypothesis"
        reviewed = dict(legacy_rows[0], status="accepted", evidence_grade="corroborated")
        upsert_record(reviewed, db)
        assert import_legacy_lessons(db, legacy) == 1
        preserved = search_records("Legacy lesson", path=db)[0]
        assert preserved["status"] == "accepted"
        assert preserved["evidence_grade"] == "corroborated"

        refs = Path(td) / "academy_refs.json"
        refs.write_text(json.dumps({
            "sources": [{"id": "s1", "title": "Primary source", "origin": "primary",
                         "path": "docs/source.md", "takeaways": ["Claim"], "open": ["Check date"]}],
            "claims": [{"id": "c1", "claim": "A research claim", "verdict": "confirmed",
                        "origin": "reputable", "evidence": "Secondary evidence",
                        "urls": ["https://example.org"]}],
        }), encoding="utf-8")
        from modules.academy_intelligence import import_legacy_references
        assert import_legacy_references(db, refs) == 2
        ref_source = search_records("Primary source", path=db)[0]
        ref_claim = search_records("A research claim", path=db)[0]
        assert ref_source["status"] == "inbox" and ref_source["evidence_grade"] == "source_only"
        assert ref_claim["status"] == "inbox" and ref_claim["evidence_grade"] == "source_only"
        assert ref_claim["claim_type"] == "hypothesis"


def test_academy_intelligence_core():
    run()


if __name__ == "__main__":
    run()
