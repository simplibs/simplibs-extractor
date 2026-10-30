from pathlib import Path
from typing import NoReturn
from simplibs.exception import ParamError


def raise_output_is_file_error(out_dir: Path) -> NoReturn:
    """Raise ParamError when the output folder given with `-o` is a file.

    Args:
        out_dir: The path that was meant to be a folder.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="option '-o'",
        value=str(out_dir),
        problem=f"'{out_dir}' is a file, but -o takes a folder.",
        expected="A folder (existing or to be created).",
        how_to_fix="Pass a folder; the file name comes from the profile.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_output_is_file_error — `-o` Takes a Folder

## Purpose
The file name always comes from the profile, so `-o` can only be a folder.
"""
