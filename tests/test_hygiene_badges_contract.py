# tests/test_hygiene_badges_contract.py
import json
import unittest
from tests.genlayer import gl, Address
from contracts.ConsensusLint import ConsensusLint
from contracts.HygieneBadges import HygieneBadges


class TestHygieneBadgesContract(unittest.TestCase):
    def setUp(self):
        gl.contracts_registry.clear()
        gl.message.sender_address.as_hex = "0x1111111111111111111111111111111111111111"
        gl.message_raw = {"datetime": "2026-10-18T10:00:00Z"}

        # Deploy mock ConsensusLint
        self.ledger = ConsensusLint()
        self.ledger_addr = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        gl.contracts_registry[self.ledger_addr] = self.ledger

        # Deploy HygieneBadges
        self.badges = HygieneBadges()

    def test_set_ledger_owner_only_and_single_use(self):
        # Non-owner fails
        gl.message.sender_address.as_hex = "0x2222222222222222222222222222222222222222"
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.badges.set_ledger(self.ledger_addr)
        self.assertEqual(str(ctx.exception), "only owner can set ledger address")

        # Owner succeeds
        gl.message.sender_address.as_hex = "0x1111111111111111111111111111111111111111"
        self.badges.set_ledger(self.ledger_addr)
        self.assertEqual(self.badges.get_ledger_address(), self.ledger_addr)

        # Second call fails
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.badges.set_ledger(self.ledger_addr)
        self.assertEqual(str(ctx.exception), "ledger address already set")

    def test_claim_badge_flow_and_rejections(self):
        self.badges.set_ledger(self.ledger_addr)

        # Register target in ledger
        good_url = "https://raw.githubusercontent.com/huzyow155/consensus-lint-fixtures/4a1999768180230ebc990f4177f0d5dd5b6f10a6/good_contract.py"
        self.ledger.register_target("Good Contract", "main", good_url)
        target_ids = json.loads(self.ledger.list_target_ids(0, 1))
        tid = target_ids[0]

        # Target not scored yet -> claim_badge fails
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.badges.claim_badge(tid, "Verified Target Badge")
        self.assertEqual(str(ctx.exception), "target has no scored audit")

        # Audit target in ledger
        with open("fixtures-local/contracts/good_contract.py", "rb") as f:
            good_bytes = f.read()
        gl.nondet.web.pages[good_url] = good_bytes
        self.ledger.audit_target(tid)

        # Claim badge succeeds
        self.badges.claim_badge(tid, "Verified Target Badge")
        badge_ids = json.loads(self.badges.list_badge_ids(0, 1))
        self.assertEqual(len(badge_ids), 1)
        bid = badge_ids[0]

        badge = json.loads(self.badges.get_badge(bid))
        self.assertEqual(badge["current_status"], "BADGE_A")
        self.assertEqual(badge["current_grade"], "A")
        self.assertEqual(badge["current_score"], 100)

        # Duplicate claim by same sender fails
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.badges.claim_badge(tid, "Another Badge")
        self.assertEqual(str(ctx.exception), "badge already claimed for this target and sender")

    def test_refresh_badge_status_transitions(self):
        self.badges.set_ledger(self.ledger_addr)

        url = "https://raw.githubusercontent.com/huzyow155/consensus-lint-fixtures/main/evolving_contract.py"
        self.ledger.register_target("Evolving", "series-ev", url)
        tid = json.loads(self.ledger.list_target_ids(0, 1))[0]

        # Audit v1 (Score ~86 Grade B)
        with open("fixtures-local/contracts/evolving_contract_v1.py", "rb") as f:
            v1_bytes = f.read()
        gl.nondet.web.pages[url] = v1_bytes
        self.ledger.audit_target(tid)

        # Claim badge initially
        self.badges.claim_badge(tid, "Evolving Project Badge")
        bid = json.loads(self.badges.list_badge_ids(0, 1))[0]
        b1 = json.loads(self.badges.get_badge(bid))
        self.assertEqual(b1["current_grade"], "B")

        # Refresh with no audit change -> no-op
        self.badges.refresh_badge(bid)
        b1_ref = json.loads(self.badges.get_badge(bid))
        self.assertEqual(len(b1_ref["badge_history"]), 1)

        # Update to v2 and re-audit in ledger
        gl.message_raw = {"datetime": "2026-10-18T12:00:00Z"}
        with open("fixtures-local/contracts/evolving_contract_v2.py", "rb") as f:
            v2_bytes = f.read()
        gl.nondet.web.pages[url] = v2_bytes
        self.ledger.audit_target(tid)

        # Refresh badge -> transition IMPROVED
        self.badges.refresh_badge(bid)
        b2 = json.loads(self.badges.get_badge(bid))
        self.assertEqual(b2["current_status"], "BADGE_A")
        self.assertEqual(b2["current_grade"], "A")
        self.assertEqual(len(b2["badge_history"]), 2)
        self.assertEqual(b2["badge_history"][-1]["transition"], "IMPROVED")


if __name__ == "__main__":
    unittest.main()
