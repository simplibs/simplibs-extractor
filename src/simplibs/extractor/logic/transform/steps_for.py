from collections.abc import Mapping
from simplibs.actions import Action
# Outers
from ...annotations import StepsSpec


def steps_for(steps: StepsSpec, suffix: str) -> Action | None:
    """Pick the action that applies to a file suffix.

    Args:
        steps: The profile's steps (see `StepsSpec`).
        suffix: The suffix of the file (`".py"`); the case is ignored.

    Returns:
        The action, or `None` if the text stays as it is.
    """

    # 1. No steps at all
    if steps is None:
        return None

    # 2. A mapping: the file's own suffix, otherwise the fallback "*"
    if isinstance(steps, Mapping):
        return steps.get(suffix.lower(), steps.get("*"))

    # 3. One action for every file
    return steps


_DESIGN_NOTES = """
# steps_for — Which Pipeline Does This File Get

## Purpose
The one place that understands the three shapes of `StepsSpec`. The caller
asks "what applies to `.py`?" and gets an action or nothing.

## Case
Suffix keys of a profile are lowercase (checked when the profile is built),
so the suffix of the file is lowercased for the lookup.
"""
