"""Tests for TIA timezone scheduling and durable due-job claims."""
from datetime import datetime, timezone
import unittest

from modules.tia_agent_store import TIAStore
from modules.tia_session_scheduler import next_occurrence, preview, validate_weekly_rule, utc_iso


class TiaSessionSchedulerTests(unittest.TestCase):
    def test_weekly_occurrence_uses_timezone_and_dst(self):
        rule = validate_weekly_rule({"weekdays": [6], "local_time": "09:30"})
        after = datetime(2026, 3, 7, 12, 0, tzinfo=timezone.utc)
        result = next_occurrence(rule, "America/New_York", after)
        self.assertEqual(result.astimezone(__import__("zoneinfo").ZoneInfo("America/New_York")).hour, 9)
        self.assertEqual(result.astimezone(__import__("zoneinfo").ZoneInfo("America/New_York")).utcoffset().total_seconds(), -4 * 3600)

    def test_nonexistent_spring_forward_wall_time_is_skipped(self):
        rule = {"weekdays": [6], "local_time": "02:30"}
        after = datetime(2026, 3, 7, 12, 0, tzinfo=timezone.utc)
        result = next_occurrence(rule, "America/New_York", after)
        local = result.astimezone(__import__("zoneinfo").ZoneInfo("America/New_York"))
        self.assertEqual(local.date().isoformat(), "2026-03-15")
        self.assertEqual(local.strftime("%H:%M"), "02:30")

    def test_invalid_timezone_and_naive_datetime_rejected(self):
        rule = {"weekdays": [0], "local_time": "08:00"}
        with self.assertRaises(ValueError):
            next_occurrence(rule, "Not/A_Timezone", datetime.now(timezone.utc))
        with self.assertRaises(ValueError):
            next_occurrence(rule, "Africa/Cairo", datetime(2026, 1, 1))

    def test_preview_count_and_rule_validation(self):
        with self.assertRaises(ValueError):
            validate_weekly_rule({"weekdays": [], "local_time": "08:00"})
        with self.assertRaises(ValueError):
            preview({"weekdays": [0], "local_time": "08:00"}, "Africa/Cairo",
                    datetime.now(timezone.utc), 0)


class TiaScheduledJobStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = TIAStore(":memory:")
        self.agent_id = self.store.list_agents()[0]["agent_id"]

    def test_schedule_creation_is_idempotent_and_claim_is_leased(self):
        schedule = {"frequency": "weekly", "weekdays": [0, 1], "local_time": "08:30"}
        due = "2020-01-01T00:00:00Z"
        first = self.store.create_scheduled_job("Daily briefing", self.agent_id, schedule,
                                                "Africa/Cairo", due, "briefing-v1")
        second = self.store.create_scheduled_job("Daily briefing", self.agent_id, schedule,
                                                 "Africa/Cairo", due, "briefing-v1")
        self.assertEqual(first, second)
        claimed = self.store.claim_due_jobs("2026-11-09T18:00:00Z")
        self.assertEqual([x["job_id"] for x in claimed], [first])
        self.assertEqual(self.store.claim_due_jobs("2026-11-09T18:00:10Z"), [])
        self.store.record_scheduled_run(first, "2026-11-10T06:30:00Z", "enqueued")
        claimed_again = self.store.claim_due_jobs("2026-11-10T07:00:00Z")
        self.assertEqual([x["job_id"] for x in claimed_again], [first])

    def test_timezone_validation_and_pause(self):
        with self.assertRaises(ValueError):
            self.store.create_scheduled_job("Bad zone", self.agent_id, {}, "Mars/Phobos",
                                            "2026-11-09T18:00:00Z")
        job_id = self.store.create_scheduled_job("Paused", self.agent_id, {}, "UTC",
                                                 "2020-01-01T00:00:00Z")
        self.store.set_scheduled_job_enabled(job_id, False)
        self.assertEqual(self.store.claim_due_jobs("2026-11-09T18:00:00Z"), [])


if __name__ == "__main__":
    unittest.main()
