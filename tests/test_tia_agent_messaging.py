import unittest
from modules.tia_agent_store import TIAStore

class TiaAgentMailboxTests(unittest.TestCase):
    def setUp(self):
        self.store = TIAStore(":memory:")
        self.sender, self.receiver = [a["agent_id"] for a in self.store.list_agents()[:2]]

    def test_message_inbox_outbox_and_receiver_only_ack(self):
        mid = self.store.create_agent_message(self.sender, self.receiver, "analysis",
            "London handoff", "Sweep completed; monitor retest.", {"session": "London"}, "corr-1")
        self.assertEqual(self.store.list_agent_messages(self.receiver)[0]["message_id"], mid)
        self.assertEqual(self.store.list_agent_messages(self.sender, "outbox")[0]["correlation_id"], "corr-1")
        with self.assertRaises(PermissionError): self.store.acknowledge_agent_message(mid, self.sender)
        self.store.acknowledge_agent_message(mid, self.receiver)
        self.assertEqual(self.store.list_agent_messages(self.receiver, status="acknowledged")[0]["message_id"], mid)

    def test_message_type_and_secret_payload_validation(self):
        with self.assertRaises(ValueError):
            self.store.create_agent_message(self.sender, self.receiver, "execute_order", "x", "y")
        with self.assertRaises(ValueError):
            self.store.create_agent_message(self.sender, self.receiver, "alert", "x", "y", {"api_key": "secret"})

class TiaMemoryRetrievalTests(unittest.TestCase):
    def test_search_is_scoped_to_agent_and_keyword_terms(self):
        store = TIAStore(":memory:")
        a, b = [x["agent_id"] for x in store.list_agents()[:2]]
        store.add_memory(a, "research", "London session liquidity sweep")
        store.add_memory(b, "research", "London session macro outlook")
        found = store.search_memory(a, "London liquidity")
        self.assertEqual(len(found), 1)
        self.assertIn("liquidity", found[0]["content"])

if __name__ == "__main__":
    unittest.main()
