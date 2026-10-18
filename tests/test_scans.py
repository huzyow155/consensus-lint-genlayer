# tests/test_scans.py
import unittest
import subprocess
import sys


class TestRepositoryScans(unittest.TestCase):
    def test_ascii_scan(self):
        res = subprocess.run([sys.executable, "scripts/tools/scan_ascii.py"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"ASCII scan failed: {res.stdout}\n{res.stderr}")

    def test_banned_words_and_patterns_scan(self):
        res = subprocess.run([sys.executable, "scripts/tools/scan_banned_words.py"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Banned words scan failed: {res.stdout}\n{res.stderr}")


if __name__ == "__main__":
    unittest.main()
