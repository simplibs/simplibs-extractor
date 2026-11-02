from simplibs.validate import validate_call
# Inners
from ._helpers import LANGUAGE_REGISTRY
from ._validations import (
    raise_language_exists_error,
    raise_language_name_error,
    raise_language_suffix_error,
)


@validate_call
def register_language(
    suffix: str,
    language: str,
    *,
    replace_existing: bool = False,
) -> None:
    """Register the code-fence language of a file suffix.

    Args:
        suffix: The suffix with its dot, lowercase (`".mjs"`).
        language: The language name written after the opening fence (`"javascript"`).
        replace_existing: Allow replacing the language of a suffix that already has one.

    Raises:
        ParamError: If the suffix or the language has an unusable shape, or if the suffix is taken and `replace_existing` is False.
    """

    # 1. A suffix a file can have: a dot, something after it, lowercase, no whitespace
    if len(suffix) < 2 or not suffix.startswith(".") or suffix != suffix.lower() or any(char.isspace() for char in suffix):
        raise_language_suffix_error(suffix)

    # 2. The language ends up in the opening fence: not empty, no whitespace, no backticks
    if not language or any(char.isspace() or char == "`" for char in language):
        raise_language_name_error(language)

    # 3. Refuse a taken suffix unless replacing was asked for
    if suffix in LANGUAGE_REGISTRY and not replace_existing:
        raise_language_exists_error(suffix)

    # 4. Store
    LANGUAGE_REGISTRY[suffix] = language


_DESIGN_NOTES = """
# register_language — Adding a Language to the Output

## Purpose
The built-in languages are registered the same way, so there is one door for
all of them. An add-on registers the suffixes of its language in
`register_all`, with `replace_existing=True` like everything else it
registers, so calling it twice changes nothing.

## The Checks
A suffix the scanner could never produce (`"py"`, `".PY"`) would never match
a file, and a language with a space or a backtick would break the fence it is
written into. Both are refused here, once, instead of spoiling every output.
"""
