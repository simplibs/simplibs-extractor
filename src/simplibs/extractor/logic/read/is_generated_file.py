from contextlib import closing
from itertools import islice
from pathlib import Path
from simplibs.file import iter_lines
# Outers
from ...constants import GENERATED_MARKER, MARKER_SCAN_LINES


def is_generated_file(path: Path) -> bool:
    """Check whether a file is an output of this library.

    Only the first lines are read, so the check is cheap even for a huge output.

    Args:
        path: The file to check.

    Returns:
        True if `GENERATED_MARKER` appears in the first `MARKER_SCAN_LINES` lines.
    """

    # 1. Stream the head only; undecodable bytes become replacement characters, never an error
    lines = iter_lines(path, errors="replace")
    with closing(lines):
        head = list(islice(lines, MARKER_SCAN_LINES))

    # 2. The marker is a plain substring: it sits inside a comment whose syntax depends on the format
    return any(GENERATED_MARKER in line for line in head)


_DESIGN_NOTES = """
# is_generated_file — "Did We Write This?"

## Purpose
An output in the scanned folder must not be read as input, whatever it is
called (`extraction (1).md`, a backup). The marker identifies it.

## Lazy on Purpose
`iter_lines` reads in blocks and the stream is closed right after the head,
so a multi-megabyte output costs a few kilobytes.

## `errors="replace"`
This is a question about a marker, not a read of the content. A file with an
odd byte near its start can still be checked; whether it can be *read* is
decided later, by `read_text`.
"""
