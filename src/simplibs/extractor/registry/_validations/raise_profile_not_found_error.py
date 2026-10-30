from collections.abc import Sequence
from typing import NoReturn
from simplibs.exception import NotFoundError


def raise_profile_not_found_error(
    key: str,
    known: Sequence[str],
) -> NoReturn:
    """Raise NotFoundError when a profile key is not registered.

    Args:
        key: The requested key (`"python/code-clean"`).
        known: The keys that are registered.
    """

    # 1. Name the registered profiles, or say there are none
    available = ", ".join(known) if known else "(none registered)"

    # 2. Raise structured NotFoundError wrapping a LookupError
    raise NotFoundError(
        error_name="EXTRACTOR_PROFILE_NOT_FOUND",
        label=f"profile '{key}'",
        value=key,
        problem=f"No profile is registered under '{key}'.",
        expected=f"One of the registered profiles: {available}.",
        how_to_fix=(
            "Check the spelling of the key ('system/name').",
            "Install the package that provides the profile (for example simplibs-code-extractor).",
        ),
        exception=LookupError,
    )


_DESIGN_NOTES = """
# raise_profile_not_found_error — Say What Exists

## Purpose
A mistyped key is the most common profile error; listing the registered keys
turns it into a one-glance fix.

## The Second Hint
Profiles of an add-on exist only after the add-on is installed, which is the
other usual cause.
"""
