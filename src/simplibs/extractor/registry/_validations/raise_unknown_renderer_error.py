from typing import NoReturn
from simplibs.exception import ParamError
# Inners
from .._helpers import RENDERER_REGISTRY


def raise_unknown_renderer_error(name: str) -> NoReturn:
    """Raise ParamError when no renderer is registered for a format name.

    The card lists the formats that are registered.

    Args:
        name: The format name that was asked for.
    """

    # 1. The formats that exist, for the card
    known = ", ".join(sorted(RENDERER_REGISTRY)) or "(none registered)"

    # 2. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'format'",
        value=name,
        problem=f"No renderer is registered for the format {name!r}.",
        expected=f"One of the registered formats: {known}.",
        how_to_fix="Choose a registered format, or add one with register_renderer().",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_unknown_renderer_error — A Format Nobody Renders

## Purpose
Reads the registry itself, so the call stays one line and the list on the
card is always the current one.
"""
