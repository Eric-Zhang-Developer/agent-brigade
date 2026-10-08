#!/usr/bin/env node
// `npx agent-brigade ...`: run the bundled install.py with the first Python 3.11+ on PATH.
const { spawnSync } = require("node:child_process");
const path = require("node:path");

const isNew = (py) => spawnSync(py, ["-c", "import sys; sys.exit(sys.version_info < (3, 11))"]).status === 0;
const py = ["python3.14", "python3.13", "python3.12", "python3.11", "python3", "python"].find(isNew);
if (!py) {
  console.error("agent-brigade: needs Python 3.11+ on PATH (macOS: brew install python; others: python.org)");
  process.exit(1);
}
const r = spawnSync(py, [path.join(__dirname, "..", "install.py"), ...process.argv.slice(2)], { stdio: "inherit" });
process.exit(r.status ?? 1);
