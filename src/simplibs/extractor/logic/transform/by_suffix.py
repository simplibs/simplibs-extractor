from collections.abc import Sequence
from simplibs.actions import Action
from simplibs.validate import validate_call


@validate_call
def by_suffix(step: Action, suffixes: Sequence[str]) -> dict[str, Action]:
    """Give the same step to every one of the given suffixes.

    Args:
        step: The pipeline of a profile.
        suffixes: The suffixes it applies to (`".js"`, `".tsx"`).

    Returns:
        A mapping `suffix -> step`, the form of `Profile.steps` that chooses by file type.
    """

    # 1. One entry per suffix
    return {suffix: step for suffix in suffixes}


_DESIGN_NOTES = """
# by_suffix — One Step for a Family of File Types

## Purpose
A step sees only the text, never the path. A profile that must treat `.py`
and `.js` differently (or the six JavaScript suffixes alike) says so with a
mapping `suffix -> step`; this builds it. Every add-on that handles more than
one suffix needs the same three lines, so the extractor offers them.

## One Object Shared
The same step object is used for every suffix; it holds no state.

## The Keys Are Checked Where They Are Used
Whether a key is a usable suffix (lowercase, a dot and something after it)
is decided when the `Profile` is built (`EXTRACTOR_PROFILE_INVALID`), so a
mistake is reported against the profile, once, with its name.
"""
