"""Frozen storage contract (F00): JSON Lines, one note per line, append-only."""

import json
from datetime import datetime, timezone
from pathlib import Path


def append(path: Path, text: str) -> dict:
    note = {"text": text, "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(note) + "\n")
    return note


def load(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
