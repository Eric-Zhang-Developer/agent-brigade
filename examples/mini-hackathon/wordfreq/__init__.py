"""wordfreq (toy example): the frozen public API. The tokenize and rank features implement it."""

from collections import Counter

from wordfreq.rank import ranked
from wordfreq.tokenize import words


def count(text: str) -> dict[str, int]:
    return dict(Counter(words(text)))


def top(counts: dict[str, int], n: int) -> list[tuple[str, int]]:
    return ranked(counts, n)
