import re


_FORMAT_NAME = re.compile(r"[a-z][a-z0-9_-]*")


def is_output_format(name: str) -> bool:
    """Check whether a value has the shape of an output format name.

    Args:
        name: The candidate (`"markdown"`, `"plain"`, `"json-manifest"`).

    Returns:
        True for a lowercase name made of letters, digits, `_` and `-` that
        starts with a letter; False for anything else, including non-strings.
    """

    # 1. Only a string can name a format
    if not isinstance(name, str):
        return False

    # 2. Lowercase word characters only — no spaces, no path separators
    return _FORMAT_NAME.fullmatch(name) is not None


_DESIGN_NOTES = """
# is_output_format — "Does This Look Like a Format Name?"

## Purpose
The single rule behind the `OutputFormat` annotation.

## Shape, Not Existence
Whether a renderer with that name is registered is known only to the
registry, a layer further to the right. This helper checks the shape; the
registry check happens when the configuration is resolved.
"""
