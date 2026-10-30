from pathlib import Path
from typing import NoReturn
from simplibs.exception import ParamError


def raise_not_python_script_error(target: Path) -> NoReturn:
    """Raise ParamError when the script name does not end with `.py`.

    Args:
        target: The rejected script path.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'path'",
        value=str(target),
        problem=f"The script name {target.name!r} does not end with '.py'.",
        expected="A file name ending with '.py', or a folder.",
        how_to_fix="Add '.py' to the name, or pass the folder the script should lie in.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_not_python_script_error — A Script That Could Not Run

## Purpose
A generated script without `.py` could not be run, so it is not written.
"""
