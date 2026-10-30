from typing import Final


MARKER_SCAN_LINES: Final[int] = 3
"""How many leading lines of a file are searched for `GENERATED_MARKER`."""


_DESIGN_NOTES = """
# MARKER_SCAN_LINES — Look at the Head, Never the Whole File

## Purpose
Outputs are large. Reading only the first lines keeps the check cheap and
makes it independent of the size limit.

## Why Not One Line
A format may put a title or a front matter line before the marker; three
lines leave room for that without scanning content.
"""
