from dataclasses import dataclass
from pathlib import Path
# Outers
from ..annotations import FileStatus


@dataclass(frozen=True, slots=True)
class FileReport:
    """What happened to one file.

    Attributes:
        path: The absolute path of the file.
        relative: The path relative to the source, with `/` separators.
        status: `ok`, `skipped` or `error`.
        reason: Why the file was skipped or failed; `None` for `ok`.
        bytes_in: The size of the original text, in bytes.
        bytes_out: The size of the text after the steps, in bytes.
    """

    path: Path
    relative: str
    status: FileStatus
    reason: str | None = None
    bytes_in: int = 0
    bytes_out: int = 0


_DESIGN_NOTES = """
# FileReport — One Line of the Report

## Purpose
The per-file record behind the summary, the exit code and a later JSON
report. A skipped or failed file keeps its reason, so "why is my file
missing?" always has an answer.

## `relative` Next to `path`
The report is read by people (relative, stable across machines); the
absolute path is for code that wants to open the file.
"""
