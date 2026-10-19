# tests/test_checker_rules.py
import os
import json
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")).replace("\\", "/")
FIXTURES_DIR = os.path.join(ROOT_DIR, "tests", "fixtures-tooling").replace("\\", "/")
CHECKER_JS = os.path.join(ROOT_DIR, "scripts", "tools", "check_evidence_consistency.js").replace("\\", "/")
LINT_PY = os.path.join(ROOT_DIR, "contracts", "ConsensusLint.py").replace("\\", "/")
BADGES_PY = os.path.join(ROOT_DIR, "contracts", "HygieneBadges.py").replace("\\", "/")


def run_node_eval(script: str) -> dict:
    cmd = ["node", "-e", script]
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
    try:
        out = json.loads(res.stdout) if res.stdout.strip() else {}
    except Exception:
        out = {"raw": res.stdout, "stderr": res.stderr}
    return {"code": res.returncode, "stdout": res.stdout, "stderr": res.stderr, "json": out}


class TestCheckerRulesTooling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(LINT_PY, "r", encoding="utf-8") as f:
            cls.lint_code = f.read()
        with open(BADGES_PY, "r", encoding="utf-8") as f:
            cls.badges_code = f.read()

    def test_k1_bad_fails_and_good_passes(self):
        script = f"""
        const checker = require('{CHECKER_JS}');
        const fs = require('fs');
        const c1 = fs.readFileSync('{LINT_PY}', 'utf8');
        const badErrors = checker.checkK1_CallSiteArity(['{FIXTURES_DIR}/k1_bad_script.js'], [c1]);
        const goodErrors = checker.checkK1_CallSiteArity(['{FIXTURES_DIR}/k1_good_script.js'], [c1]);
        console.log(JSON.stringify({{ badCount: badErrors.length, goodCount: goodErrors.length }}));
        """
        res = run_node_eval(script)
        self.assertEqual(res["code"], 0, res["stderr"])
        data = res["json"]
        self.assertGreater(data["badCount"], 0)
        self.assertEqual(data["goodCount"], 0)

    def test_k2_bad_fails_and_good_passes(self):
        script = f"""
        const checker = require('{CHECKER_JS}');
        const fs = require('fs');
        const c1 = fs.readFileSync('{LINT_PY}', 'utf8');
        const badJson = JSON.parse(fs.readFileSync('{FIXTURES_DIR}/k2_bad_evidence.json', 'utf8'));
        const goodJson = JSON.parse(fs.readFileSync('{FIXTURES_DIR}/k2_good_evidence.json', 'utf8'));
        const badErrors = checker.checkK2_DecodedErrors(badJson, [c1]);
        const goodErrors = checker.checkK2_DecodedErrors(goodJson, [c1]);
        console.log(JSON.stringify({{ badCount: badErrors.length, goodCount: goodErrors.length }}));
        """
        res = run_node_eval(script)
        self.assertEqual(res["code"], 0, res["stderr"])
        data = res["json"]
        self.assertGreater(data["badCount"], 0)
        self.assertEqual(data["goodCount"], 0)

    def test_k3_bad_fails_and_good_passes(self):
        script = f"""
        const checker = require('{CHECKER_JS}');
        const fs = require('fs');
        const badJson = JSON.parse(fs.readFileSync('{FIXTURES_DIR}/k3_bad_evidence.json', 'utf8'));
        const goodJson = JSON.parse(fs.readFileSync('{FIXTURES_DIR}/k3_good_evidence.json', 'utf8'));
        const badErrors = checker.checkK3_MaintainerResponses(badJson);
        const goodErrors = checker.checkK3_MaintainerResponses(goodJson);
        console.log(JSON.stringify({{ badCount: badErrors.length, goodCount: goodErrors.length }}));
        """
        res = run_node_eval(script)
        self.assertEqual(res["code"], 0, res["stderr"])
        data = res["json"]
        self.assertGreater(data["badCount"], 0)
        self.assertEqual(data["goodCount"], 0)

    def test_k4_bad_fails_and_good_passes(self):
        script = f"""
        const checker = require('{CHECKER_JS}');
        const dummyLive = {{ targets: {{}}, self_lint: {{}}, maintainer_responses: [], badges: {{}}, negative_tests: [] }};
        const badErrors = checker.checkK4_OnchainClaimsTraced('{FIXTURES_DIR}/k4_bad_doc.md', dummyLive);
        const goodErrors = checker.checkK4_OnchainClaimsTraced('{FIXTURES_DIR}/k4_good_doc.md', dummyLive);
        console.log(JSON.stringify({{ badCount: badErrors.length, goodCount: goodErrors.length }}));
        """
        res = run_node_eval(script)
        self.assertEqual(res["code"], 0, res["stderr"])
        data = res["json"]
        self.assertGreater(data["badCount"], 0)
        self.assertEqual(data["goodCount"], 0)

    def test_k5_bad_fails_and_good_passes(self):
        script = f"""
        const checker = require('{CHECKER_JS}');
        const badErrors = checker.checkK5_CalibrationCounters('{FIXTURES_DIR}/k5_bad_calib.json');
        const goodErrors = checker.checkK5_CalibrationCounters('{FIXTURES_DIR}/k5_good_calib.json');
        console.log(JSON.stringify({{ badCount: badErrors.length, goodCount: goodErrors.length }}));
        """
        res = run_node_eval(script)
        self.assertEqual(res["code"], 0, res["stderr"])
        data = res["json"]
        self.assertGreater(data["badCount"], 0)
        self.assertEqual(data["goodCount"], 0)

    def test_k6_bad_fails_and_good_passes(self):
        script = f"""
        const checker = require('{CHECKER_JS}');
        const live = {{ targets: {{ shell_like: {{ label: "ShellLike Large Fixture", auditRecord: {{ truncated: true }} }} }} }};
        const badErrors = checker.checkK6_TruncationLabels('{FIXTURES_DIR}/k6_bad_doc.md', live);
        const goodErrors = checker.checkK6_TruncationLabels('{FIXTURES_DIR}/k6_good_doc.md', live);
        console.log(JSON.stringify({{ badCount: badErrors.length, goodCount: goodErrors.length }}));
        """
        res = run_node_eval(script)
        self.assertEqual(res["code"], 0, res["stderr"])
        data = res["json"]
        self.assertGreater(data["badCount"], 0)
        self.assertEqual(data["goodCount"], 0)

    def test_k7_bad_fails_and_good_passes(self):
        script = f"""
        const checker = require('{CHECKER_JS}');
        const badErrors = checker.checkK7_RenderedTablesByteIdentical('{FIXTURES_DIR}/k7_bad_doc.md', '{FIXTURES_DIR}/k7_mock_renderer.js');
        const goodErrors = checker.checkK7_RenderedTablesByteIdentical('{FIXTURES_DIR}/k7_good_doc.md', '{FIXTURES_DIR}/k7_mock_renderer.js');
        console.log(JSON.stringify({{ badCount: badErrors.length, goodCount: goodErrors.length }}));
        """
        res = run_node_eval(script)
        self.assertEqual(res["code"], 0, res["stderr"])
        data = res["json"]
        self.assertGreater(data["badCount"], 0)
        self.assertEqual(data["goodCount"], 0)


if __name__ == "__main__":
    unittest.main()
