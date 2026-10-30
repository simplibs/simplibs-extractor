from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_no_profile_given_error(names: Any) -> NoReturn:
    """Raise ParamError when no profile name was given at all.

    Args:
        names: What the caller passed (an empty text, an empty sequence, blanks only).
    """

    # 1. What a valid input looks like; the fix is built from it
    expected = "at least one profile name"

    # 2. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile keys",
        value=names,
        problem="No profile was given.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_no_profile_given_error — Nothing to Expand

## Purpose
`""`, `" , "` and `[]` all mean "no profile"; an empty list of keys would
only fail later and less clearly.
"""
