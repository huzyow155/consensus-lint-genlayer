# tests/test_url_policy.py
import unittest
from scripts.tools.local_lint import parse_and_validate_source_url


class TestUrlPolicy(unittest.TestCase):
    def test_valid_pinned_commit_url(self):
        url = "https://raw.githubusercontent.com/octocat/Hello-World/4a1999768180230ebc990f4177f0d5dd5b6f10a6/contract.py"
        canonical, owner_repo, ref, ref_kind, path, fname = parse_and_validate_source_url(url)
        self.assertEqual(canonical, url)
        self.assertEqual(owner_repo, "octocat/Hello-World")
        self.assertEqual(ref, "4a1999768180230ebc990f4177f0d5dd5b6f10a6")
        self.assertEqual(ref_kind, "PINNED_COMMIT")
        self.assertEqual(path, "contract.py")
        self.assertEqual(fname, "contract.py")

    def test_valid_mutable_ref_url(self):
        url = "https://raw.githubusercontent.com/owner-name/repo_name/main/contracts/sub/my_contract.py"
        canonical, owner_repo, ref, ref_kind, path, fname = parse_and_validate_source_url(url)
        self.assertEqual(canonical, url)
        self.assertEqual(owner_repo, "owner-name/repo_name")
        self.assertEqual(ref, "main")
        self.assertEqual(ref_kind, "MUTABLE_REF")
        self.assertEqual(path, "contracts/sub/my_contract.py")
        self.assertEqual(fname, "my_contract.py")

    def test_trailing_dot_and_case_normalization(self):
        url = "https://RAW.GITHUBUSERCONTENT.COM./octocat/Hello-World/v1.0.0/contract.py"
        canonical, owner_repo, ref, ref_kind, path, fname = parse_and_validate_source_url(url)
        self.assertEqual(canonical, "https://raw.githubusercontent.com/octocat/Hello-World/v1.0.0/contract.py")

    def test_scheme_must_be_https(self):
        with self.assertRaises(ValueError) as ctx:
            parse_and_validate_source_url("http://raw.githubusercontent.com/a/b/c/d.py")
        self.assertEqual(str(ctx.exception), "source url must use https")

    def test_host_spoof_rejections(self):
        banned_hosts = [
            "https://raw.githubusercontent.com.evil.com/a/b/c/d.py",
            "https://github.com/a/b/c/d.py",
            "https://raw.github.com/a/b/c/d.py",
            "https://notgithub.com/a/b/c/d.py",
        ]
        for bh in banned_hosts:
            with self.assertRaises(ValueError) as ctx:
                parse_and_validate_source_url(bh)
            self.assertEqual(str(ctx.exception), "source host not allowed")

    def test_credentials_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            parse_and_validate_source_url("https://user:pass@raw.githubusercontent.com/a/b/c/d.py")
        self.assertEqual(str(ctx.exception), "source url contains credentials")

    def test_port_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            parse_and_validate_source_url("https://raw.githubusercontent.com:8080/a/b/c/d.py")
        self.assertEqual(str(ctx.exception), "source url port not allowed")

    def test_query_and_fragment_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            parse_and_validate_source_url("https://raw.githubusercontent.com/a/b/c/d.py?query=1")
        self.assertEqual(str(ctx.exception), "source url has query or fragment")

        with self.assertRaises(ValueError) as ctx:
            parse_and_validate_source_url("https://raw.githubusercontent.com/a/b/c/d.py#heading")
        self.assertEqual(str(ctx.exception), "source url has query or fragment")

    def test_path_tricks_and_extensions(self):
        invalid_paths = [
            "https://raw.githubusercontent.com/a/b/c/d.js",
            "https://raw.githubusercontent.com/a/b/c/d.txt",
            "https://raw.githubusercontent.com/a/b/c/.. /d.py",
            "https://raw.githubusercontent.com/a/b//c/d.py",
            "https://raw.githubusercontent.com/a/b/c/d%2fsub.py",
            "https://raw.githubusercontent.com/a/b/c/1/2/3/4/5/6/7/d.py",
        ]
        for ip in invalid_paths:
            with self.assertRaises(ValueError):
                parse_and_validate_source_url(ip)

    def test_overlength_url(self):
        long_url = "https://raw.githubusercontent.com/a/b/main/" + ("x" * 280) + ".py"
        with self.assertRaises(ValueError) as ctx:
            parse_and_validate_source_url(long_url)
        self.assertEqual(str(ctx.exception), "source url too long")


if __name__ == "__main__":
    unittest.main()
