from typing import Final


DEFAULT_MAX_FILE_SIZE: Final[int] = 1_000_000
"""The largest file, in bytes, that is read into an extraction."""


_DESIGN_NOTES = """
# DEFAULT_MAX_FILE_SIZE — One Megabyte

## Purpose
A single lock file or data dump can be larger than the rest of a project
together and would drown the output. Larger files are reported as skipped,
not silently dropped.

## Not a Fixed Rule
`ExtractionConfig.max_file_size` overrides it; `None` switches the limit off.
"""
