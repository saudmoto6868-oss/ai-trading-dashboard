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
