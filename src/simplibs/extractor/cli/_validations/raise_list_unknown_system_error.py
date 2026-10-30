from typing import NoReturn
from simplibs.exception import ParamError
# Outers
from .._helpers import system_options


def raise_list_unknown_system_error(system: str) -> NoReturn:
    """Raise ParamError when `--list-profiles` names a system without profiles.

    Args:
        system: The system that was asked for.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="option '--list-profiles'",
        value=system,
        problem=f"No profile is registered for the system {system!r}.",
        expected=f"One of the registered systems: {', '.join(system_options()) or '(none)'}.",
        how_to_fix="Run --list-systems to see what is installed.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_list_unknown_system_error — A Typo Is Not an Empty List

## Purpose
An empty list would look like "no profiles exist" and hide the typo.

## Close Relative of `raise_unknown_system_error`
Same problem, other option: the label and the advice differ.
"""
