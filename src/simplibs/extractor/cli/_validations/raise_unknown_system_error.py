from typing import NoReturn
from simplibs.exception import ParamError
# Outers
from .._helpers import system_options


def raise_unknown_system_error(system: str) -> NoReturn:
    """Raise ParamError when no profile is registered for a system.

    Args:
        system: The system that was named or chosen.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="system",
        value=system,
        problem=f"No profile is registered for the system {system!r}.",
        expected=f"One of the registered systems: {', '.join(system_options()) or '(none)'}.",
        how_to_fix="Check the spelling, or install the package that provides the system.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_unknown_system_error — A System Nobody Provides

## Purpose
Raised before the question about profiles, because there is nothing to offer
for a system without profiles. The card lists the systems that do exist.
"""
