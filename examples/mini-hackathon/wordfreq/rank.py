def ranked(counts: dict[str, int], n: int) -> list[tuple[str, int]]:
    """Highest count first, ties alphabetical, at most n items."""
    if n <= 0:
        return []
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
