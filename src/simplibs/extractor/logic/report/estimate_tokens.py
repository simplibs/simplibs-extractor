import math
from simplibs.validate import validate_call
# Inners
from ._validations import raise_chars_per_token_error


@validate_call
def estimate_tokens(
    text: str,
    chars_per_token: float | int = 4.0,
) -> int:
    """Estimate how many tokens a language model would count in a text.

    This is a rough estimate, not a count: real tokenizers differ by model
    and by language.

    Args:
        text: The text.
        chars_per_token: The assumed average number of characters per token.

    Returns:
        The estimated number of tokens (`0` for an empty text).

    Raises:
        ParamError: If `chars_per_token` is not greater than zero.
    """

    # 1. A zero or negative ratio would divide by zero or return nonsense
    if chars_per_token <= 0:
        raise_chars_per_token_error(chars_per_token)

    # 2. Round up: a started token is a token
    return math.ceil(len(text) / chars_per_token)


_DESIGN_NOTES = """
# estimate_tokens — A Size Guess, Honestly Labeled

## Purpose
"Will this fit into a context window?" is the first question about an
output. Characters divided by four answers it well enough for code and
English; non-Latin text needs a lower ratio, which is why it is a parameter.

## No Model Name, No Tokenizer
Any exact count would need a particular tokenizer and would age with the
models. The function says "estimate" in its name and does not pretend.
"""
