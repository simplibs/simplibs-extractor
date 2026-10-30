from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_profile_output_name_error(value: Any) -> NoReturn:
    """Raise ParamError when the output name of a profile is not a portable file name.

    Args:
        value: The rejected output name.
    """

    # 1. What a valid name looks like; the fix is built from it
    expected = "a portable file name (no path separators or forbidden characters)"

    # 2. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile output_name",
        value=value,
        problem=f"The output name {value!r} is not a usable file name.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_profile_output_name_error — An Output Name That Is Not a Name

## Purpose
The output is written next to the source or into `-o`, so the profile may
give only a file name, never a path.
"""
