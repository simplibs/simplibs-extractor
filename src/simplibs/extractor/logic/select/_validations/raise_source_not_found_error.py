from pathlib import Path
from typing import NoReturn
from simplibs.exception import NotFoundError


def raise_source_not_found_error(path: Path) -> NoReturn:
    """Raise NotFoundError when the source of an extraction is not an existing directory.

    Args:
        path: The configured source.
    """

    # 1. Raise structured NotFoundError wrapping a FileNotFoundError
    raise NotFoundError(
        error_name="EXTRACTOR_SOURCE_NOT_FOUND",
        label=f"source '{path}'",
        value=str(path),
        problem=f"'{path}' is not an existing directory.",
        expected="The path of an existing directory to extract from.",
        how_to_fix=(
            "Check the path for typos.",
            "Create the directory, or point 'source' at the folder that holds the files.",
        ),
        exception=FileNotFoundError,
    )


_DESIGN_NOTES = """
# raise_source_not_found_error — The Folder Must Exist

## Purpose
Checked before anything is collected, so a typo in the source never turns
into an "empty extraction" that looks like a configuration of its own.

## Missing and Not-a-Directory Share One Card
For the caller both mean the same thing: there is no folder to scan there.
"""
