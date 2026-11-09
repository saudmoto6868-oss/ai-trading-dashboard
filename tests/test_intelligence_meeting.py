from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path


class MeetingJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ.pop("DATABASE_URL", None)
        os.environ["ACADEMY_DB_PATH"] = str(Path(self.tmp.name) / "academy.sqlite3")

    def tearDown(self):
        os.environ.pop("ACADEMY_DB_PATH", None)
        self.tmp.cleanup()

    def test_append_and_list_are_persistent_and_ordered(self):
        from modules.intelligence_meeting import append_entry, list_entries, meeting_summary
        first = append_entry(entry_type="owner_request", title="Consolidate tabs", body="Build one center.")
        second = append_entry(entry_type="decision", title="Keep Lab authoritative", body="Lab owns empirical validation.")
        rows = list_entries(limit=10)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["id"], second)
        self.assertEqual(rows[1]["id"], first)
        self.assertEqual(meeting_summary()["by_type"]["decision"], 1)

    def test_task_proposal_and_review_are_append_only(self):
        from modules.intelligence_meeting import append_entry, list_entries
        proposal_id = append_entry(
            entry_type="recommendation",
            title="Add regime classifier",
            body="Calculate regime from historical candles.",
            status="awaiting_owner_review",
            metadata={"kind": "task_proposal", "priority": "P1", "official_board_written": False},
        )
        append_entry(
            entry_type="decision",
            title="Task proposal approved: Add regime classifier",
            body="Approved for manual entry only.",
            status="approved_for_board_entry",
            metadata={"kind": "task_proposal_review", "proposal_id": proposal_id,
                      "official_board_written": False},
        )
        rows = list_entries(limit=10)
        review = next(row for row in rows if row["entry_type"] == "decision")
        proposal = next(row for row in rows if row["id"] == proposal_id)
        self.assertEqual(review["metadata"]["proposal_id"], proposal_id)
        self.assertEqual(review["status"], "approved_for_board_entry")
        self.assertFalse(review["metadata"]["official_board_written"])
        self.assertEqual(proposal["status"], "awaiting_owner_review")
        self.assertEqual(proposal["metadata"]["kind"], "task_proposal")

    def test_rejects_invalid_type_and_empty_content(self):
        from modules.intelligence_meeting import append_entry
        with self.assertRaises(ValueError):
            append_entry(entry_type="random", title="x", body="y")
        with self.assertRaises(ValueError):
            append_entry(entry_type="decision", title=" ", body="y")

    def test_rejects_non_http_source(self):
        from modules.intelligence_meeting import append_entry
        with self.assertRaises(ValueError):
            append_entry(entry_type="meeting_note", title="Source", body="note", related_url="javascript:alert(1)")


if __name__ == "__main__":
    unittest.main()
