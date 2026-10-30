from typing import NoReturn
from simplibs.exception import ParamError


def raise_renderer_exists_error(name: str) -> NoReturn:
    """Raise ParamError when a renderer is already registered under a format name.

    Args:
        name: The format name that is taken.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label=f"renderer '{name}'",
        value=name,
        problem=f"A renderer is already registered for the format '{name}'.",
        expected="A format name that is not registered yet, or replace_existing=True.",
        how_to_fix="Pass replace_existing=True, or choose a different format name.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_renderer_exists_error — A Taken Format Name

## Purpose
Replacing a renderer has to be asked for, so one add-on cannot quietly
replace the format of another.
"""
