from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Entry:
    """One file that is ready to be rendered.

    Attributes:
        relative: The path relative to the source, with `/` separators.
        suffix: The lowercased suffix (`".py"`), or an empty string.
        text: The text after the steps were applied.
    """

    relative: str
    suffix: str
    text: str


_DESIGN_NOTES = """
# Entry — What a Renderer Receives

## Purpose
A renderer needs the path (for the header and the language), the suffix (for
the code fence) and the final text — and nothing else. It never sees the
disk, the rules or the steps.
"""
