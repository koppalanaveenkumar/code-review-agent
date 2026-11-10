def word_count(text: str) -> int:
    return len(text.split())


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Shorten text to max_length characters, adding suffix if cut."""
    if max_length < len(suffix):
        raise ValueError("max_length must be at least the suffix length")
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix