from typing import NoReturn
from simplibs.exception import ParamError


def raise_language_suffix_error(suffix: str) -> NoReturn:
    """Raise ParamError when a suffix cannot be the key of a language.

    Args:
        suffix: The unusable suffix.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'suffix'",
        value=suffix,
        problem=f"{suffix!r} is not a usable file suffix.",
        expected="A lowercase suffix that starts with a dot and has at least one more character, without whitespace (\".mjs\").",
        how_to_fix="Write the suffix as the scanner sees it: lowercase, with the dot.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_language_suffix_error — A Suffix That Would Never Match

## Purpose
`"py"` and `".PY"` look right and never match a file, because the renderer
asks for the lowercase suffix with its dot. Failing when the language is
registered is cheaper than a highlight that silently never appears.
"""
