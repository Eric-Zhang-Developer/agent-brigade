import argparse
import os
import sys
from pathlib import Path

from jotter import store
from jotter.search import search


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="jotter", description="One-line notes.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("add").add_argument("text")
    sub.add_parser("list")
    sub.add_parser("search").add_argument("word")
    args = ap.parse_args(argv)
    path = Path(os.environ.get("JOTTER_FILE", Path.home() / ".jotter.jsonl"))
    if args.cmd == "add":
        store.append(path, args.text)
        return 0
    notes = store.load(path)
    shown = search(notes, args.word) if args.cmd == "search" else sorted(notes, key=lambda n: n["created"], reverse=True)
    for n in shown:
        print(f"{n['created']}  {n['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
