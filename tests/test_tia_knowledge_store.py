"""Contract tests for the native TIA institutional store."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from modules.tia_knowledge_store import (
    TIAKnowledgeStore, TIAStoreError, ValidationError,
)


class TIAKnowledgeStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "tia.db"
        self.store = TIAKnowledgeStore(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_health_is_explicitly_local_sqlite(self):
        health = self.store.health()
        self.assertEqual(health.status, "ready")
        self.assertEqual(health.backend, "sqlite")
        self.assertIn("shared durability is not implied", health.detail)

    def test_knowledge_lifecycle_and_content_hash(self):
        item_id = self.store.add_knowledge(
            title="Gold macro framework",
            body="A documented framework with evidence.",
            category="macro",
            created_by="TIA Market Intelligence",
            tags=["Gold", "Macro", "gold"],
            metadata={"source_quality": "partial"},
        )
        item = self.store.list_knowledge(status="draft")[0]
        self.assertEqual(item["id"], item_id)
        self.assertEqual(item["tags"], ["gold", "macro"])
        self.assertEqual(len(item["content_sha256"]), 64)
        self.store.transition_knowledge(item_id, "review")
        self.store.transition_knowledge(item_id, "approved")
        self.assertEqual(self.store.list_knowledge(status="approved")[0]["id"], item_id)

    def test_invalid_transition_is_rejected(self):
        item_id = self.store.add_knowledge(
            title="Test", body="Evidence", category="research",
            created_by="tester",
        )
        with self.assertRaises(ValidationError):
            self.store.transition_knowledge(item_id, "approved")

    def test_missing_item_is_not_silently_ignored(self):
        with self.assertRaises(TIAStoreError):
            self.store.transition_knowledge("missing", "review")

    def test_rejects_bad_url_and_oversized_metadata(self):
        with self.assertRaises(ValidationError):
            self.store.add_knowledge(
                title="Test", body="Body", category="research",
                created_by="tester", source_url="javascript:alert(1)",
            )
        with self.assertRaises(ValidationError):
            self.store.add_knowledge(
                title="Test", body="Body", category="research",
                created_by="tester", metadata={"payload": "x" * 20_000},
            )

    def test_meeting_events_are_hash_chained_and_append_only(self):
        first = self.store.append_meeting_event(
            meeting_id="tia-weekly", kind="decision", title="Evidence gate",
            body="Do not promote unverified metrics.", actor="Intelligence Director",
        )
        second = self.store.append_meeting_event(
            meeting_id="tia-weekly", kind="action", title="Add source health",
            body="Expose unavailable and stale source states.", actor="Engineering",
            related_ids=[first],
        )
        self.assertEqual(len(self.store.list_meeting_events(meeting_id="tia-weekly")), 2)
        self.assertTrue(self.store.verify_meeting_chain())
        with sqlite3.connect(self.db) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "UPDATE tia_meeting_events SET title='rewritten' WHERE event_id=?",
                    (first,),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "DELETE FROM tia_meeting_events WHERE event_id=?", (second,)
                )

    def test_meeting_event_validation(self):
        with self.assertRaises(ValidationError):
            self.store.append_meeting_event(
                meeting_id="room", kind="unknown", title="Bad", body="Bad",
                actor="tester",
            )
        with self.assertRaises(ValidationError):
            self.store.append_meeting_event(
                meeting_id="room", kind="decision", title="Bad", body="Bad",
                actor="tester", metadata={"bad": object()},
            )

    def test_limits_are_bounded(self):
        with self.assertRaises(ValidationError):
            self.store.list_knowledge(limit=1000)
        with self.assertRaises(ValidationError):
            self.store.list_meeting_events(limit=1000)


if __name__ == "__main__":
    unittest.main()
