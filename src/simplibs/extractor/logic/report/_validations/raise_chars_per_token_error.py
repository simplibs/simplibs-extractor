from typing import NoReturn
from simplibs.exception import ParamError


def raise_chars_per_token_error(chars_per_token: float | int) -> NoReturn:
    """Raise ParamError when the assumed characters per token is not positive.

    Args:
        chars_per_token: The rejected ratio.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'chars_per_token'",
        value=chars_per_token,
        problem="The number of characters per token must be positive.",
        expected="A number greater than zero (about 4 for English text and code).",
        how_to_fix="Pass a positive number, or leave the default.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_chars_per_token_error — A Ratio That Cannot Divide

## Purpose
A zero ratio would divide by zero, a negative one would return nonsense.
"""
