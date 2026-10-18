# tests/test_normalization.py
import unittest
import hashlib
from scripts.tools.local_lint import normalize_source_text, MAX_SOURCE_BYTES


class TestNormalization(unittest.TestCase):
    def test_bom_stripping(self):
        content = b"\xef\xbb\xbf# v0.2.16\nprint('hello')\n"
        norm, trunc, sha, rlen = normalize_source_text(content)
        self.assertFalse(norm.startswith("\ufeff"))
        self.assertFalse(trunc)
        self.assertEqual(rlen, len(content))
        self.assertTrue(norm.startswith("# v0.2.16\n"))

    def test_crlf_normalization(self):
        content = b"# v0.2.16\r\nclass A:\r\n    pass\r\n"
        norm, trunc, sha, rlen = normalize_source_text(content)
        self.assertNotIn("\r\n", norm)
        self.assertIn("\n", norm)
        self.assertEqual(sha, hashlib.sha256(norm.encode("utf-8")).hexdigest())

    def test_invalid_utf8_rejection(self):
        bad_bytes = b"# v0.2.16\n\xff\xfe\xfa not valid utf8"
        with self.assertRaises(ValueError) as ctx:
            normalize_source_text(bad_bytes)
        self.assertEqual(str(ctx.exception), "source is not valid utf-8")

    def test_truncation_behavior(self):
        large_source = b"# v0.2.16\n" + (b"def foo():\n    pass\n" * 4000)
        self.assertGreater(len(large_source), MAX_SOURCE_BYTES)
        norm, trunc, sha, rlen = normalize_source_text(large_source)
        self.assertTrue(trunc)
        self.assertLessEqual(len(norm.encode("utf-8")), MAX_SOURCE_BYTES)
        self.assertEqual(rlen, len(large_source))
        self.assertEqual(sha, hashlib.sha256(norm.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    unittest.main()
