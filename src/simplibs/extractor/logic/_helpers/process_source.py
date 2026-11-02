import dataclasses
import warnings
from collections.abc import Iterable
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
        A pair: the final report of the file, and its `Entry` (`None` unless the status is `ok` or `partial`).
        A failure of this one file is reported, not raised.
    """
    config, profile = plan.config, plan.profile

    # 1. Read; a skipped or failed file stops here
    report, text = read_source(path, config.source, config.max_file_size)
    if text is None:
        return report, None

    # 2. Transform; the steps are code from a profile, so any error of theirs belongs to this file.
    #    A step that cannot handle the file fully warns instead of failing; the warnings are collected here.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            output = apply_steps(text, profile.steps, path.suffix)
        except Exception as exc:
            failed = dataclasses.replace(report, status="error", reason=f"transform failed: {describe_failure(exc)}")
            return failed, None

    # 3. A warning of a step means the file is in the output, but not fully processed
    reasons = _partial_reasons(caught)

    # 4. Included: remember how large the text is after the steps
    done = dataclasses.replace(
        report,
        status="partial" if reasons else "ok",
        reason="; ".join(reasons) or None,
        bytes_out=len(output.encode("utf-8")),
    )
    return done, Entry(done.relative, path.suffix.lower(), output)


def _partial_reasons(caught: Iterable[warnings.WarningMessage]) -> list[str]:
    """The different warnings the steps gave, one line each, in the order they came.

    Args:
        caught: The warnings recorded while the steps ran.

    Returns:
        The messages of the `UserWarning`s (and their subclasses); other categories
        (`DeprecationWarning`, `FutureWarning`, ...) belong to the code, not to the file.
    """

    # 1. Keep the messages of the right category, collapse them to one line, drop repeats
    reasons: list[str] = []
    for item in caught:
        if not issubclass(item.category, UserWarning):
            continue
        line = " ".join(str(item.message).split())
        if line and line not in reasons:
            reasons.append(line)
    return reasons


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

## A Warning Is Not an Error
A step that cannot handle a file (a Python source that does not parse, say)
returns the text unchanged and warns. The file stays in the output and the
report calls it `partial` with the warning as the reason. Only `UserWarning`
(the default category of `warnings.warn`) counts: a `DeprecationWarning` from
a library inside a step says something about the code, not about the file.

## Why `warnings` and Not an Exception
A step is a plain function of a text and knows nothing about the extractor.
The standard `warnings` module is the one channel such a function can use
without importing anything. The recording is not thread-safe
(`warnings.catch_warnings` changes a global), which is fine here: the files
are processed one after another.
"""
