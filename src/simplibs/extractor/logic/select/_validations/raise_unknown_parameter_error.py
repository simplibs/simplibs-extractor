from collections.abc import Sequence
from typing import NoReturn
from simplibs.exception import ParamError


def raise_unknown_parameter_error(
    unknown: Sequence[str],
    known: Sequence[str],
) -> NoReturn:
    """Raise ParamError when a name is not a field of the extraction config.

    Args:
        unknown: The rejected names.
        known: The valid names, listed on the card.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="extraction parameters",
        value=unknown,
        problem=f"Unknown parameter(s): {', '.join(unknown)}.",
        expected=f"Only these parameters: {', '.join(known)}.",
        how_to_fix="Check the spelling of the parameter names.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_unknown_parameter_error — A Typo Must Not Vanish

## Purpose
`extract(sourse=...)` would disappear into `**overrides`. The card lists the
valid names.
"""
