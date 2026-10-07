"""Test helpers: put core/scripts on sys.path, build throwaway git repos, serve fake HTTP."""

import http.server
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))


def sh(cwd, *args) -> str:
    return subprocess.run(list(args), cwd=cwd, check=True, capture_output=True, text=True).stdout


def write(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)


def spec(fid: str, owns: list[str], depends_on=(), phase=1, extra="") -> str:
    return (f"---\nid: {fid}\nname: Feature {fid}\nphase: {phase}\ndepends_on: [{', '.join(depends_on)}]\n"
            f"owns: [{', '.join(owns)}]\ncut: ok\n{extra}---\n\n# {fid}\n")


class RepoCase(unittest.TestCase):
    """A temp git repo with an initial commit on `main`. self.root is its path."""

    files: dict[str, str] = {"kit.toml": 'profile = "hackathon"\n'}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        sh(self.root, "git", "init", "-q", "-b", "main")
        sh(self.root, "git", "config", "user.email", "test@example.com")
        sh(self.root, "git", "config", "user.name", "Test")
        sh(self.root, "git", "config", "commit.gpgsign", "false")
        write(self.root, self.files)
        self.commit("initial")

    def tearDown(self):
        self._tmp.cleanup()

    def commit(self, msg="change", files: dict[str, str] | None = None, date: str | None = None):
        if files:
            write(self.root, files)
        sh(self.root, "git", "add", "-A")
        env_args = ["-c", "core.hooksPath=/dev/null"]
        cmd = ["git", *env_args, "commit", "-q", "--allow-empty", "-m", msg]
        if date:
            cmd += ["--date", date]
        sh(self.root, *cmd)

    def branch(self, name: str):
        sh(self.root, "git", "checkout", "-q", "-b", name)


class FakeSite:
    """Serve {path: (status, body_bytes)} on 127.0.0.1 in a thread. Use as a context manager; .origin is the URL."""

    def __init__(self, routes: dict[str, tuple[int, bytes]]):

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                status, body = routes.get(self.path, (404, b"not found"))
                self.send_response(status)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.origin = f"http://127.0.0.1:{self.server.server_address[1]}"

    def __enter__(self):
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
