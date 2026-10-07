import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import helpers
import demo_snapshot
import verify_release

SHA = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
LEAK = "sk-" + "live0000"   # built here so the repo itself never holds the pattern


def site(commit=SHA, bundle=b"let x = 1;", extra=None):
    routes = {
        "/api/health": (200, json.dumps({"commit": commit}).encode()),
        "/": (200, b'<html><script src="/app.js"></script><script src="https://cdn.example/x.js"></script></html>'),
        "/app.js": (200, bundle),
        "/about": (200, b"about"),
    }
    routes.update(extra or {})
    return helpers.FakeSite(routes)


class Verify(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "kit.toml").write_text('profile = "hackathon"\n[release]\nsmoke_paths = ["/", "/about"]\n')

    def tearDown(self):
        self._tmp.cleanup()

    def run_verify(self, origin, commit=SHA):
        out = io.StringIO()
        with redirect_stdout(out):
            rc = verify_release.main(["--root", str(self.root), "--url", origin, "--commit", commit, "--allow-http"])
        return rc, out.getvalue()

    def test_pass_and_receipt(self):
        with site() as s:
            rc, out = self.run_verify(s.origin, SHA[:7])
        self.assertEqual(rc, 0, out)
        self.assertIn("1 bundles scanned", out)       # the cross-origin CDN script is skipped
        self.assertIn("PASS", (self.root / "reports/deploys.md").read_text())

    def test_wrong_commit(self):
        with site(commit="ffffffffffff") as s:
            rc, out = self.run_verify(s.origin)
        self.assertEqual(rc, 1)
        self.assertIn("serving ffffffffffff", out)

    def test_smoke_failure(self):
        with site(extra={"/about": (500, b"")}) as s:
            rc, out = self.run_verify(s.origin)
        self.assertEqual(rc, 1)
        self.assertIn("status 500", out)

    def test_secret_in_bundle_reported_without_value(self):
        with site(bundle=f'const k = "{LEAK}";'.encode()) as s:
            rc, out = self.run_verify(s.origin)
        self.assertEqual(rc, 1)
        self.assertIn("/app.js: sk-", out)
        self.assertNotIn("live0000", out)

    def test_missing_health_field(self):
        with site(extra={"/api/health": (200, b"{}")}) as s:
            self.assertEqual(self.run_verify(s.origin)[0], 1)

    def test_https_required_and_bare_origin(self):
        with self.assertRaises(ValueError):
            verify_release.check_origin("http://example.com", allow_http=False)
        with self.assertRaises(ValueError):
            verify_release.check_origin("https://user:pw@example.com", allow_http=False)
        with self.assertRaises(ValueError):
            verify_release.check_origin("https://example.com/path", allow_http=False)
        self.assertEqual(verify_release.check_origin("https://example.com/", False), "https://example.com")

    def test_commits_match(self):
        self.assertTrue(verify_release.commits_match(SHA, SHA[:7]))
        self.assertFalse(verify_release.commits_match(SHA, SHA[:6]))
        self.assertFalse(verify_release.commits_match("", SHA))


class Snapshot(unittest.TestCase):
    def test_snapshot_and_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "kit.toml").write_text('profile = "hackathon"\n[release]\nsnapshot_paths = ["/", "/api/health", "/missing"]\n')
            out = root / "snap"
            with site() as s, redirect_stdout(io.StringIO()):
                rc = demo_snapshot.main(["--root", str(root), "--url", s.origin, "--out", str(out), "--allow-http"])
            self.assertEqual(rc, 1)  # /missing is 404
            m = json.loads((out / "manifest.json").read_text())
            self.assertEqual(m["commit"], SHA)
            self.assertIn("<script", (out / "index.html").read_text())
            self.assertTrue((out / "api/health").is_file())
            self.assertEqual([f["status"] for f in m["files"]], [200, 200, 404])
            self.assertEqual(len(m["files"][0]["sha256"]), 64)

    def test_refuses_parent_paths(self):
        with self.assertRaises(ValueError):
            demo_snapshot.target(Path("/tmp/x"), "/../etc/passwd")


if __name__ == "__main__":
    unittest.main()
