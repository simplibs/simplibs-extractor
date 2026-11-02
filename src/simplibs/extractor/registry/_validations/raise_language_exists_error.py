from typing import NoReturn
from simplibs.exception import ParamError


def raise_language_exists_error(suffix: str) -> NoReturn:
    """Raise ParamError when a language is already registered for a suffix.

    Args:
        suffix: The suffix that is taken.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label=f"language of '{suffix}'",
        value=suffix,
        problem=f"A language is already registered for the suffix '{suffix}'.",
        expected="A suffix that has no language yet, or replace_existing=True.",
        how_to_fix="Pass replace_existing=True, or choose a different suffix.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_language_exists_error — A Taken Suffix

## Purpose
Replacing a language has to be asked for, so one add-on cannot quietly change
how another one's files are highlighted.
"""
