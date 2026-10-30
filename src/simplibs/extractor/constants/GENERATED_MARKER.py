from typing import Final


GENERATED_MARKER: Final[str] = "simplibs-extractor:generated"
"""The text every output carries in its first lines to mark it as generated."""


_DESIGN_NOTES = """
# GENERATED_MARKER — "This File Is Our Own Output"

## Purpose
An extraction that lands inside its own source folder would be read again on
the next run. The path alone is not enough: the `unique` policy makes
`extraction (1).md` and `backup` makes a backup file. The marker identifies
an output whatever its name is.

## Where It Is Written
In the first lines of every output, in every format (an HTML comment in
Markdown, a comment line in plain text).
"""
