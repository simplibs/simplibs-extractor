from typing import NoReturn
from simplibs.exception import AlreadyExistsError


def raise_profile_exists_error(key: str) -> NoReturn:
    """Raise AlreadyExistsError when a profile key is registered twice.

    Args:
        key: The key that is already taken.
    """

    # 1. Raise structured AlreadyExistsError wrapping a ValueError
    raise AlreadyExistsError(
        error_name="EXTRACTOR_PROFILE_EXISTS",
        label=f"profile '{key}'",
        value=key,
        problem=f"A profile is already registered under '{key}'.",
        expected="A key that is not registered yet, or replace_existing=True.",
        how_to_fix=(
            "Pass replace_existing=True if replacing the profile is intended.",
            "Choose a different name for the new profile.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_profile_exists_error — No Silent Replacement

## Purpose
Two add-ons registering the same key would otherwise decide by import order.
Replacing is possible, but it has to be asked for.
"""
