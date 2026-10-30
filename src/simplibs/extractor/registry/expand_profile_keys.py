from collections.abc import Sequence
from simplibs.validate import validate_call
# Inners
from ._validations import raise_missing_system_error, raise_no_profile_given_error


@validate_call
def expand_profile_keys(
    system: str | None,
    names: str | Sequence[str],
) -> list[str]:
    """Turn what a person typed into full profile keys.

    Args:
        system: The default system for names without one; `None` if there is none.
        names: One text with names separated by commas (`"a,b"`), or a sequence of names.

    Returns:
        The full keys, in the order given: `("python", "a,b")` gives
        `["python/a", "python/b"]`. A name that already contains `/` is kept as it is.

    Raises:
        ParamError: If a name has no system and none was given, or if no name was given at all.
    """

    # 1. One text and a sequence are handled alike: split every item on commas
    items = [names] if isinstance(names, str) else list(names)
    parts = [part.strip() for item in items for part in item.split(",")]

    # 2. Build the keys
    keys: list[str] = []
    for part in parts:
        if not part:
            continue
        if "/" in part:
            keys.append(part)
        elif system:
            keys.append(f"{system}/{part}")
        else:
            raise_missing_system_error(part)

    # 3. Nothing usable was given
    if not keys:
        raise_no_profile_given_error(names)

    return keys


_DESIGN_NOTES = """
# expand_profile_keys — "python a,b" Becomes Two Keys

## Purpose
The CLI takes `simplibs-extractor python code-clean,data-all`. This function
is the single place where that text becomes registry keys, so the CLI and
the Python API agree.

## Full Keys Win
`generic/all` typed in a list stays `generic/all` even when a default system
is given, so one run can mix systems.
"""
