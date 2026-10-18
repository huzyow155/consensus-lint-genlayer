# tests/test_mocked_consensus.py
import json
import unittest
import hashlib
from scripts.tools.local_lint import (
    lint_source,
    select_model_call_sites,
    build_model_prompt,
    parse_and_verify_model_response,
    compute_model_penalty,
)


class TestMockedConsensus(unittest.TestCase):
    def setUp(self):
        with open("fixtures-local/contracts/good_contract.py", "r", encoding="utf-8") as f:
            self.good_src = f.read()
        self.good_sha = hashlib.sha256(self.good_src.encode("utf-8")).hexdigest()

    def simulate_validator_acceptance(self, leader_payload: dict, validator_source: str, validator_model_raw: str = None) -> bool:
        # Recompute validator side
        val_sha = hashlib.sha256(validator_source.encode("utf-8")).hexdigest()
        if val_sha != leader_payload.get("source_sha256"):
            return False

        mode, findings, score, grade = lint_source(validator_source)
        if mode != leader_payload.get("mode"):
            return False

        val_counts = {r: d["count"] for r, d in findings.items()}
        if val_counts != leader_payload.get("rule_counts"):
            return False

        # Model bucket check
        if validator_model_raw is not None:
            import ast
            tree = ast.parse(validator_source)
            lines = validator_source.split("\n")
            sites = select_model_call_sites(tree, lines)
            try:
                judgements = parse_and_verify_model_response(sites, validator_model_raw)
            except Exception:
                return False
            _, val_bucket = compute_model_penalty(judgements)
            if val_bucket != leader_payload.get("penalty_bucket"):
                return False

        return True

    def test_honest_leader_accepted(self):
        mode, findings, score, grade = lint_source(self.good_src)
        lead_payload = {
            "source_sha256": self.good_sha,
            "mode": mode,
            "rule_counts": {r: d["count"] for r, d in findings.items()},
            "penalty_bucket": "0",
        }
        accepted = self.simulate_validator_acceptance(lead_payload, self.good_src)
        self.assertTrue(accepted)

    def test_leader_inflating_counts_rejected(self):
        mode, findings, score, grade = lint_source(self.good_src)
        fake_counts = {r: d["count"] for r, d in findings.items()}
        fake_counts["CL01"] = 1  # Fabricated finding

        lead_payload = {
            "source_sha256": self.good_sha,
            "mode": mode,
            "rule_counts": fake_counts,
            "penalty_bucket": "0",
        }
        accepted = self.simulate_validator_acceptance(lead_payload, self.good_src)
        self.assertFalse(accepted, "Validator must reject leader inflating counts")

    def test_leader_hash_mismatch_rejected(self):
        mode, findings, score, grade = lint_source(self.good_src)
        lead_payload = {
            "source_sha256": "0" * 64,  # wrong hash
            "mode": mode,
            "rule_counts": {r: d["count"] for r, d in findings.items()},
            "penalty_bucket": "0",
        }
        accepted = self.simulate_validator_acceptance(lead_payload, self.good_src)
        self.assertFalse(accepted, "Validator must reject hash mismatch")

    def test_mutable_ref_moved_between_fetches_rejected(self):
        # Leader fetched v1, validator fetched v2
        with open("fixtures-local/contracts/evolving_contract_v1.py", "r", encoding="utf-8") as f:
            v1_src = f.read()
        with open("fixtures-local/contracts/evolving_contract_v2.py", "r", encoding="utf-8") as f:
            v2_src = f.read()

        v1_sha = hashlib.sha256(v1_src.encode("utf-8")).hexdigest()
        mode, findings, score, grade = lint_source(v1_src)
        lead_payload = {
            "source_sha256": v1_sha,
            "mode": mode,
            "rule_counts": {r: d["count"] for r, d in findings.items()},
            "penalty_bucket": "0",
        }
        # Validator re-fetches and gets v2
        accepted = self.simulate_validator_acceptance(lead_payload, v2_src)
        self.assertFalse(accepted, "Disagreement when mutable ref moves is expected consensus outcome")

    def test_validator_bucket_agreement_with_minor_label_variance(self):
        # Leader had COMPARES_ONLY (penalty 6 -> bucket "1-6")
        lead_payload = {
            "source_sha256": self.good_sha,
            "mode": "CONTRACT",
            "rule_counts": {},
            "penalty_bucket": "1-6",
        }
        # Validator had NOT_ISOLATED (penalty 4 -> bucket "1-6")
        # Even with different individual labels, same penalty bucket allows consensus!
        p_val, b_val = compute_model_penalty([{"label": "NOT_ISOLATED"}])
        self.assertEqual(b_val, "1-6")
        self.assertEqual(lead_payload["penalty_bucket"], b_val)


if __name__ == "__main__":
    unittest.main()
