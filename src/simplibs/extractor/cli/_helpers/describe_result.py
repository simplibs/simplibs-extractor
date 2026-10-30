# Outers
from ...definitions import ExtractionResult


def describe_result(result: ExtractionResult) -> str:
    """Describe a failed extraction in one line for the batch report.

    Args:
        result: A result that did not succeed.

    Returns:
        `"<profile key>: <why>"`: the fatal reason, the number of failed
        files, or a note that nothing was selected.
    """

    # 1. The whole run stopped
    if result.fatal:
        return f"{result.profile_key}: {result.fatal}"

    # 2. Some files failed
    if result.error_files:
        return f"{result.profile_key}: {len(result.error_files)} file(s) failed"

    # 3. Nothing failed, so nothing was selected
    return f"{result.profile_key}: no file was selected"


_DESIGN_NOTES = """
# describe_result — Why a Run Counts as Failed

## Purpose
`ExtractionResult.success` is False for three different reasons. The report
at the end of a batch should say which.
"""
