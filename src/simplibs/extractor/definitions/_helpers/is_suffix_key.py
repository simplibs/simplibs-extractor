def is_suffix_key(value: str) -> bool:
    """Check whether a value is a valid key of a suffix -> action mapping.

    Args:
        value: The candidate (`".py"`, `"*"`).

    Returns:
        True for `"*"` (the fallback) or a lowercase suffix that starts with
        a dot and has at least one more character; False for anything else.
    """

    # 1. Only a string can be a key
    if not isinstance(value, str):
        return False

    # 2. The fallback
    if value == "*":
        return True

    # 3. A suffix: a dot, something after it, lowercase (suffixes are compared lowercased)
    return len(value) > 1 and value.startswith(".") and value == value.lower()


_DESIGN_NOTES = """
# is_suffix_key — Keys of a Suffix Mapping

## Purpose
`Profile.steps` may be a mapping `suffix -> Action`. A key like `"py"` or
`".PY"` would never match a file, so it is rejected when the profile is
built instead of silently doing nothing on every run.

## Lowercase Only
File suffixes are lowercased before the lookup, so only lowercase keys can
ever match.
"""
