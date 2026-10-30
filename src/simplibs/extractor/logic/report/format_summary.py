from simplibs.validate import validate_call
# Outers
from ...definitions import ExtractionResult


@validate_call
def format_summary(
    result: ExtractionResult,
    *,
    max_listed: int = 10,
) -> str:
    """Describe the outcome of one extraction as readable text.

    Args:
        result: The result of `extract()`.
        max_listed: How many failed and skipped files are listed by name.

    Returns:
        A few lines: what was extracted, where it went, the counts and sizes,
        and the files that need attention (errors first).
    """

    # 1. A run that stopped early has one thing to say
    lines = [f"Extraction: {result.profile_key}"]
    if result.fatal:
        return "\n".join(lines + [f"  FAILED: {result.fatal}"])

    # 2. What happened to the output
    if result.dry_run:
        state = "dry run, not written"
    else:
        state = "written" if result.written else "not written"

    # 3. The facts
    lines += [
        f"  source : {result.config.source}",
        f"  target : {result.target} ({state})",
        f"  files  : {len(result.ok_files)} ok, {len(result.skipped_files)} skipped, {len(result.error_files)} errors",
        f"  size   : {result.bytes_in:,} B in -> {result.bytes_out:,} B out (~{result.tokens_estimate:,} tokens)",
    ]

    # 4. Files that need a look: errors before skipped ones, capped
    for report in (*result.error_files, *result.skipped_files)[:max_listed]:
        lines.append(f"  {report.status:<7}: {report.relative} ({report.reason})")

    # 5. The most common mistake deserves its own hint
    if not result.ok_files:
        lines.append("  nothing to extract (check the source and the include/exclude rules)")

    return "\n".join(lines)


_DESIGN_NOTES = """
# format_summary — The Report Is Text Built From the Result

## Purpose
The CLI prints it, a script can log it, a test can compare it. Nothing in
the run prints on its own; everything goes through the result.

## Errors First
A failed file is what a reader is looking for; skipped files are listed after
them and only up to `max_listed`.

## Colors
None here. The CLI decides how to color the text; the function stays usable
in logs and files.
"""
