from typing import NoReturn
from simplibs.exception import ParamError


def raise_missing_system_error(name: str) -> NoReturn:
    """Raise ParamError when a profile name has no system and no default system was given.

    Args:
        name: The name without a system (`"code-clean"`).
    """

    # 1. What a valid reference looks like; the fix is built from it
    expected = "a full key 'system/name', or a system given separately"

    # 2. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile keys",
        value=name,
        problem=f"The profile {name!r} has no system.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_missing_system_error — A Name Without a Family

## Purpose
`code-clean` alone does not say which add-on it belongs to; either the full
key or the system has to come with it.
"""
