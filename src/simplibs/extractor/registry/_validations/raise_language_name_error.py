from typing import NoReturn
from simplibs.exception import ParamError


def raise_language_name_error(language: str) -> NoReturn:
    """Raise ParamError when a language name cannot be written after a fence.

    Args:
        language: The unusable name.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'language'",
        value=language,
        problem=f"{language!r} cannot be written after a code fence.",
        expected="A language name that is not empty and has no whitespace and no backtick (\"javascript\").",
        how_to_fix="Use the short name a Markdown viewer knows: python, javascript, bash.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_language_name_error — A Name That Would Break the Fence

## Purpose
The name is written right after the opening backticks. A space would turn
the rest into the info string, and a backtick would end the fence.
"""
