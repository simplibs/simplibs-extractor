from pathlib import Path
from typing import NoReturn
from simplibs.exception import AlreadyExistsError


def raise_target_exists_error(path: Path) -> NoReturn:
    """Raise AlreadyExistsError when the output exists and the policy is 'error'.

    Args:
        path: The existing output.
    """

    # 1. Raise structured AlreadyExistsError wrapping a FileExistsError
    raise AlreadyExistsError(
        error_name="EXTRACTOR_TARGET_EXISTS",
        label=f"output '{path}'",
        value=str(path),
        problem=f"The output '{path}' already exists and the overwrite policy is 'error'.",
        expected="An output path that does not exist yet, or another overwrite policy.",
        how_to_fix=(
            "Use overwrite='overwrite' to replace it, 'unique' to write a numbered copy, or 'backup' to keep the old one.",
            "Choose a different output folder or name.",
        ),
        exception=FileExistsError,
    )


_DESIGN_NOTES = """
# raise_target_exists_error — The 'error' Policy Is Honest

## Purpose
`overwrite="error"` must fail even in a dry run, otherwise a dry run would
promise a write that the real run refuses.
"""
