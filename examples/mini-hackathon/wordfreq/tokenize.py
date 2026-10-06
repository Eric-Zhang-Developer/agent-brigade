import re


def words(text: str) -> list[str]:
    """Maximal runs of a-z after lowercasing (mission rule). Everything else separates words."""
    return re.findall(r"[a-z]+", text.lower())
