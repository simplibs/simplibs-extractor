from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_profile_steps_key_error(value: Any) -> NoReturn:
    """Raise ParamError when a key of a profile's steps mapping can never match a file.

    Args:
        value: The rejected key.
    """

    # 1. What a valid key looks like; the fix is built from it
    expected = "'*' or a lowercase suffix such as '.py'"

    # 2. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile steps key",
        value=value,
        problem=f"The steps key {value!r} can never match a file.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_profile_steps_key_error — A Suffix That Never Matches

## Purpose
Suffixes are compared lowercased, so `"py"` or `".PY"` would silently never
run. The profile refuses them when it is built.
"""
