# tests/test_consensus_lint_contract.py
import json
import unittest
from tests.genlayer import gl, Address
from contracts.ConsensusLint import ConsensusLint, AUDIT_COOLDOWN_SECONDS, MAX_AUDITS_PER_TARGET


class TestConsensusLintContract(unittest.TestCase):
    def setUp(self):
        gl.contracts_registry.clear()
        gl.message.sender_address.as_hex = "0x1111111111111111111111111111111111111111"
        gl.message_raw = {"datetime": "2026-10-18T10:00:00Z"}
        self.contract = ConsensusLint()

    def test_register_target_validations_and_rejections(self):
        # 1. Label length bounds
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.contract.register_target("ab", "series-1", "https://raw.githubusercontent.com/owner/repo/main/c.py")
        self.assertEqual(str(ctx.exception), "invalid label length")

        with self.assertRaises(gl.vm.UserError) as ctx:
            self.contract.register_target("a" * 81, "series-1", "https://raw.githubusercontent.com/owner/repo/main/c.py")
        self.assertEqual(str(ctx.exception), "invalid label length")

        # 2. Series length bounds
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.contract.register_target("Valid Label", "s" * 41, "https://raw.githubusercontent.com/owner/repo/main/c.py")
        self.assertEqual(str(ctx.exception), "invalid series length")

        # 3. URL policy rejection
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.contract.register_target("Valid Label", "series-1", "http://raw.githubusercontent.com/owner/repo/main/c.py")
        self.assertEqual(str(ctx.exception), "source url must use https")

        # 4. Success registration
        good_url = "https://raw.githubusercontent.com/huzyow155/consensus-lint-fixtures/4a1999768180230ebc990f4177f0d5dd5b6f10a6/good_contract.py"
        self.contract.register_target("Good Contract", "v1-series", good_url)

        meta = json.loads(self.contract.get_meta())
        self.assertEqual(meta["targets_total"], "1")

        # 5. Duplicate registration
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.contract.register_target("Duplicate Label", "v1-series", good_url)
        self.assertEqual(str(ctx.exception), "target already registered")

    def test_audit_flow_and_ecosystem_stats(self):
        good_url = "https://raw.githubusercontent.com/huzyow155/consensus-lint-fixtures/4a1999768180230ebc990f4177f0d5dd5b6f10a6/good_contract.py"
        self.contract.register_target("Good Contract", "core", good_url)
        target_ids = json.loads(self.contract.list_target_ids(0, 10))
        tid = target_ids[0]

        # Mock web fetch for good_contract
        with open("fixtures-local/contracts/good_contract.py", "rb") as f:
            good_bytes = f.read()
        gl.nondet.web.pages[good_url] = good_bytes

        # First audit
        self.contract.audit_target(tid)
        summary = json.loads(self.contract.get_target_summary(tid))
        self.assertEqual(summary["latest_grade"], "A")
        self.assertEqual(summary["latest_score"], 100)
        self.assertEqual(summary["latest_n"], 1)

        # Audit cooldown active
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.contract.audit_target(tid)
        self.assertEqual(str(ctx.exception), "audit cooldown active")

        # Advance chain clock past cooldown (300 seconds)
        gl.message_raw = {"datetime": "2026-10-18T10:10:00Z"}
        self.contract.audit_target(tid)
        summary2 = json.loads(self.contract.get_target_summary(tid))
        self.assertEqual(summary2["latest_n"], 2)

        # Check ecosystem stats
        stats = json.loads(self.contract.get_rule_stats())
        self.assertIn("CL01", stats)
        self.assertEqual(stats["CL01"]["targets_with_finding"], 0)

    def test_registrant_response_flow(self):
        bad_url = "https://raw.githubusercontent.com/huzyow155/consensus-lint-fixtures/4a1999768180230ebc990f4177f0d5dd5b6f10a6/bad_contract.py"
        self.contract.register_target("Bad Contract", "test-series", bad_url)
        target_ids = json.loads(self.contract.list_target_ids(0, 10))
        tid = target_ids[0]

        with open("fixtures-local/contracts/bad_contract.py", "rb") as f:
            bad_bytes = f.read()
        gl.nondet.web.pages[bad_url] = bad_bytes

        self.contract.audit_target(tid)
        audit_1 = json.loads(self.contract.get_audit(tid, 1))
        self.assertIn("CL05", audit_1["findings"])

        # Non-registrant response rejected
        gl.message.sender_address.as_hex = "0x9999999999999999999999999999999999999999"
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.contract.respond_to_finding(tid, 1, "CL05", "FIXED_NEXT", "Will fix in next commit")
        self.assertEqual(str(ctx.exception), "only the registrant can do this")

        # Registrant response succeeds
        gl.message.sender_address.as_hex = "0x1111111111111111111111111111111111111111"
        self.contract.respond_to_finding(tid, 1, "CL05", "FIXED_NEXT", "Will fix in next commit")

        updated_audit = json.loads(self.contract.get_audit(tid, 1))
        self.assertEqual(len(updated_audit["responses"]), 1)
        self.assertEqual(updated_audit["responses"][0]["stance"], "FIXED_NEXT")

        # Response for finding not in audit
        with self.assertRaises(gl.vm.UserError) as ctx:
            self.contract.respond_to_finding(tid, 1, "CL04", "DISPUTE", "Not present finding note")
        self.assertEqual(str(ctx.exception), "finding not present in audit")

    def test_progress_tracking(self):
        url = "https://raw.githubusercontent.com/huzyow155/consensus-lint-fixtures/main/evolving_contract.py"
        self.contract.register_target("Evolving", "series-ev", url)
        tid = json.loads(self.contract.list_target_ids(0, 1))[0]

        # Audit 1: v1
        with open("fixtures-local/contracts/evolving_contract_v1.py", "rb") as f:
            v1_bytes = f.read()
        gl.nondet.web.pages[url] = v1_bytes
        self.contract.audit_target(tid)

        # Check progress with only 1 audit
        prog1 = json.loads(self.contract.get_progress(tid))
        self.assertFalse(prog1["has_progress"])

        # Advance clock and update to v2
        gl.message_raw = {"datetime": "2026-10-18T11:00:00Z"}
        with open("fixtures-local/contracts/evolving_contract_v2.py", "rb") as f:
            v2_bytes = f.read()
        gl.nondet.web.pages[url] = v2_bytes
        self.contract.audit_target(tid)

        # Check progress with 2 audits
        prog2 = json.loads(self.contract.get_progress(tid))
        self.assertTrue(prog2["has_progress"])
        self.assertGreater(prog2["score_delta"], 0)
        self.assertEqual(prog2["grade_after"], "A")


if __name__ == "__main__":
    unittest.main()
