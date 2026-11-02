from dataclasses import dataclass
from pathlib import Path
# Inners
from .ExtractionConfig import ExtractionConfig
from .FileReport import FileReport


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """The outcome of one extraction.

    Attributes:
        config: The configuration the run started from.
        profile_key: The key of the profile that was used.
        target: The output path (planned in a dry run, real otherwise); `None` if the run failed early.
        written: Whether the output was actually written.
        dry_run: Whether the run only planned.
        files: One report per file that was considered.
        bytes_in: The total size of the original texts.
        bytes_out: The total size of the texts after the steps.
        tokens_estimate: A rough token count of the output text.
        duration: The run time in seconds.
        fatal: The reason the whole run stopped, or `None`.
    """

    config: ExtractionConfig
    profile_key: str
    target: Path | None
    written: bool = False
    dry_run: bool = False
    files: tuple[FileReport, ...] = ()
    bytes_in: int = 0
    bytes_out: int = 0
    tokens_estimate: int = 0
    duration: float = 0.0
    fatal: str | None = None

    @property
    def ok_files(self) -> tuple[FileReport, ...]:
        """The files that entered the output, processed fully."""
        return tuple(report for report in self.files if report.status == "ok")

    @property
    def partial_files(self) -> tuple[FileReport, ...]:
        """The files that entered the output, but a step could not process them fully."""
        return tuple(report for report in self.files if report.status == "partial")

    @property
    def skipped_files(self) -> tuple[FileReport, ...]:
        """The files that were left out on purpose."""
        return tuple(report for report in self.files if report.status == "skipped")

    @property
    def error_files(self) -> tuple[FileReport, ...]:
        """The files that failed."""
        return tuple(report for report in self.files if report.status == "error")

    @property
    def success(self) -> bool:
        """True if nothing failed and at least one file entered the output (whole or partial)."""
        return self.fatal is None and not self.error_files and bool(self.ok_files or self.partial_files)


_DESIGN_NOTES = """
# ExtractionResult — The Single Source of the Report

## Purpose
The CLI summary, the exit code and a later JSON report are all built from
this one object. Nothing is printed from inside the run.

## `success` Needs at Least One File
An extraction that selected nothing is almost always a wrong filter or a
wrong folder, so it counts as a failure (exit code 1) even though nothing
raised. A `partial` file is in the output, so it counts as a file; a run that
has only partial files is successful, and `partial_files` is there for a
caller who wants to look at them.

## A Failed Run Is a Result Too
`fatal` carries the reason, so `extract_many` can report one broken
configuration and still finish the others.
"""
