import argparse
import sys

from wordfreq import count, top


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wordfreq", description="Most frequent words in a text file.")
    ap.add_argument("file")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args(argv)
    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"wordfreq: can't read {args.file}: {e.strerror}", file=sys.stderr)
        return 1
    for word, n in top(count(text), args.top):
        print(f"{word}\t{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
