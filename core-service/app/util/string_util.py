import re


def normalize_string(s: str) -> str:
    """
    Replace all whitespace with underscores and convert to lowercase.

    Args:
        s (str): Input string.

    Returns:
        str: Normalized string (whitespace -> '_', lowercase).
    """
    return re.sub(r"\s+", "_", s.strip()).lower()