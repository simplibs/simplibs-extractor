from typing import NoReturn
from simplibs.exception import ParamError


def raise_invalid_output_name_error(name: str) -> NoReturn:
    """Raise ParamError when the output name is not a usable file name.

    Args:
        name: The rejected name.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'output_name'",
        value=name,
        problem=f"{name!r} is not a usable file name.",
        expected="A plain file name such as 'extraction.md' (no folders).",
        how_to_fix="Pass only a name, or give a full path through target=... instead.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_invalid_output_name_error — A Name, Not a Path

## Purpose
The output of `extract_here` always lies in the script's folder, so only a
file name is accepted; a path is given through `target=...`.
"""
