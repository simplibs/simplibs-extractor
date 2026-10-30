from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RenderContext:
    """What a renderer needs to know besides the entries.

    Attributes:
        title: The heading of the output.
        source: The source folder; only its name is written to the output.
        profile_key: The key of the profile that produced the entries.
        add_tree: Whether the output starts with a directory tree.
    """

    title: str
    source: Path
    profile_key: str
    add_tree: bool


_DESIGN_NOTES = """
# RenderContext — The Rest of a Renderer's Input

## Purpose
A renderer is a function `(entries, context) -> str`. The entries are the
content; the context is everything around it. Passing one object keeps the
signature stable when a field is added.

## The Source Is a Path, but Only Its Name Is Written
An output is typically pasted into a chat or committed. An absolute path
would leak the layout of the machine and make the output differ between
computers.
"""
