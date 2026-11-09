from datetime import datetime, timezone
import unittest

from modules.tia_agent_store import TIAStore
from modules.tia_scheduler_worker import run_once


class TiaSchedulerWorkerTests(unittest.TestCase):
    def test_due_schedule_materializes_queued_task_and_advances(self):
        store = TIAStore(":memory:")
        agent = store.list_agents()[0]["agent_id"]
        job_id = store.create_scheduled_job(
            "Morning market brief", agent,
            {"frequency": "weekly", "weekdays": [0,1,2,3,4], "local_time": "08:00"},
            "Africa/Cairo", "2020-01-01T00:00:00Z",
        )
        result = run_once(store, datetime(2026, 11, 9, 18, 0, tzinfo=timezone.utc))
        self.assertEqual(result["claimed"], 1)
        self.assertEqual(result["enqueued"], 1)
        tasks = store.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["status"], "queued")
        self.assertEqual(tasks[0]["payload"]["schedule_id"], job_id)
        # The next due occurrence is in the future; the same cycle cannot dispatch it again.
        self.assertEqual(run_once(store, datetime(2026, 11, 9, 18, 0, tzinfo=timezone.utc))["claimed"], 0)


if __name__ == "__main__":
    unittest.main()
