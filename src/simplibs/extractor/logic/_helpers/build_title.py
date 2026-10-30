# Outers
from ...definitions import ExtractionConfig


def build_title(config: ExtractionConfig) -> str:
    """Return the heading of the output.

    Args:
        config: The resolved config (its `source` is a normalized path).

    Returns:
        The configured title, or `"Extraction: <source folder name>"`.
    """

    # 1. A chosen title wins
    if config.title:
        return config.title

    # 2. The folder's name; a filesystem root has none, so its whole path is used
    return f"Extraction: {config.source.name or config.source}"


_DESIGN_NOTES = """
# build_title — A Heading Nobody Had to Write

## Purpose
Every output needs a title; most callers do not care what it is.
"""
