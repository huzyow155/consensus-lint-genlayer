# tests/test_rule_fixtures.py
import os
import unittest
import glob
from scripts.tools.local_lint import lint_source, RULE_SPECS


class TestRuleFixtures(unittest.TestCase):
    def test_all_rule_fixtures_ast(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures-local/rules"))
        rules = sorted(os.listdir(base_dir))
        self.assertEqual(len(rules), 18, "Must have exactly 18 rules")

        results = {}
        for rule in rules:
            rdir = os.path.join(base_dir, rule)
            pass_files = sorted(glob.glob(os.path.join(rdir, "pass_*.py")))
            fail_files = sorted(glob.glob(os.path.join(rdir, "fail_*.py")))

            self.assertGreaterEqual(len(pass_files), 2, f"{rule} must have at least 2 pass fixtures")
            self.assertGreaterEqual(len(fail_files), 2, f"{rule} must have at least 2 fail fixtures")

            results[rule] = {"pass_ok": 0, "pass_total": len(pass_files), "fail_ok": 0, "fail_total": len(fail_files)}

            # Test pass fixtures
            for pf in pass_files:
                with open(pf, "r", encoding="utf-8") as f:
                    content = f.read()
                mode, findings, score, grade = lint_source(content, parser_mode="ast")
                if rule == "CL04":
                    # For CL04 pass means mode == CONTRACT
                    self.assertEqual(mode, "CONTRACT", f"Expected CONTRACT for {pf}")
                else:
                    self.assertNotIn(rule, findings, f"Rule {rule} should NOT have fired on {pf}, findings: {findings}")
                results[rule]["pass_ok"] += 1

            # Test fail fixtures
            for ff in fail_files:
                with open(ff, "r", encoding="utf-8") as f:
                    content = f.read()
                mode, findings, score, grade = lint_source(content, parser_mode="ast")
                if rule == "CL04":
                    self.assertEqual(mode, "NOT_A_CONTRACT", f"Expected NOT_A_CONTRACT for {ff}")
                else:
                    self.assertIn(rule, findings, f"Rule {rule} SHOULD have fired on {ff}, findings: {findings}")
                results[rule]["fail_ok"] += 1

        print("\n--- RULE FIXTURE TEST RESULTS (AST PARSER) ---")
        for rule, stats in results.items():
            pass_acc = stats["pass_ok"] / stats["pass_total"] * 100
            fail_acc = stats["fail_ok"] / stats["fail_total"] * 100
            print(f"{rule}: Pass {stats['pass_ok']}/{stats['pass_total']} ({pass_acc:.0f}%), Fail {stats['fail_ok']}/{stats['fail_total']} ({fail_acc:.0f}%) -> 100% precision & recall")


if __name__ == "__main__":
    unittest.main()
