import dataclasses
from pathlib import Path
# Outers
from ...definitions import Entry, FileReport, Resolved
from .._common import describe_failure
from ..read import read_source
from ..transform import apply_steps


def process_source(
    path: Path,
    plan: Resolved,
) -> tuple[FileReport, Entry | None]:
    """Read one file and run the profile's steps on it.

    Args:
        path: The absolute path of the file.
        plan: The resolved configuration.

    Returns:
        A pair: the final report of the file, and its `Entry` (`None` unless the status is `ok`).
        A failure of this one file is reported, not raised.
    """
    config, profile = plan.config, plan.profile

    # 1. Read; a skipped or failed file stops here
    report, text = read_source(path, config.source, config.max_file_size)
    if text is None:
        return report, None

    # 2. Transform; the steps are code from a profile, so any error of theirs belongs to this file
    try:
        output = apply_steps(text, profile.steps, path.suffix)
    except Exception as exc:
        failed = dataclasses.replace(report, status="error", reason=f"transform failed: {describe_failure(exc)}")
        return failed, None

    # 3. Included: remember how large the text is after the steps
    done = dataclasses.replace(report, bytes_out=len(output.encode("utf-8")))
    return done, Entry(done.relative, path.suffix.lower(), output)


_DESIGN_NOTES = """
# process_source — The Body of the Per-File Loop

## Purpose
Keeps `extract()` short and keeps the rule "one bad file never stops the run"
in one place.

## The One Broad `except`
Everything else in the library catches only the cards and OS errors it knows.
Here the code is a profile's step, written by someone else, and may fail in
any way. Reporting it against the file it failed on is the useful behavior;
a bug in this library would surface in the other phases, not here.

## `bytes_out`
The size of the text after the steps, in UTF-8 bytes: what the file
contributes to the output, so the report shows what a profile saves.
"""
