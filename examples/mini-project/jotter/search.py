def search(notes: list[dict], word: str) -> list[dict]:
    """Case-insensitive substring match, newest first."""
    w = word.lower()
    return sorted((n for n in notes if w in n["text"].lower()), key=lambda n: n["created"], reverse=True)
