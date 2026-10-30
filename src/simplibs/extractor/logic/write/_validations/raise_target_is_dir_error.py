from pathlib import Path
from typing import NoReturn
from simplibs.exception import StateError


def raise_target_is_dir_error(path: Path) -> NoReturn:
    """Raise StateError when the output path is an existing directory.

    Args:
        path: The path that was meant to be an output file.
    """

    # 1. Raise structured StateError wrapping an IsADirectoryError
    raise StateError(
        error_name="EXTRACTOR_TARGET_IS_DIR",
        label=f"output '{path}'",
        value=str(path),
        problem=f"The output '{path}' is an existing directory, not a file.",
        expected="The path of a file, in a folder that exists or can be created.",
        how_to_fix=(
            "Pass a file path as the target (for example 'out/extraction.md').",
            "On the command line, -o takes a folder; the file name comes from the profile.",
        ),
        exception=IsADirectoryError,
    )


_DESIGN_NOTES = """
# raise_target_is_dir_error — Caught Before the Write, Also in a Dry Run

## Purpose
`write_text` would refuse a directory too, but only in a real run. A dry run
must give the same verdict, otherwise it promises a write that then fails.
"""
