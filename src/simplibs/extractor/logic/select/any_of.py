import functools
import operator
from simplibs.rules import Rule


def any_of(*rules: Rule | None) -> Rule | None:
    """Combine rules with OR, ignoring the ones that are `None`.

    Args:
        *rules: The rules; `None` means "no rule here".

    Returns:
        One rule that passes when any given rule passes; `None` if no rule was given.
    """

    # 1. Keep only real rules
    present = [rule for rule in rules if rule is not None]

    # 2. Fold with `|`, or return None when there is nothing to combine
    return functools.reduce(operator.or_, present) if present else None


_DESIGN_NOTES = """
# any_of — "Any Exclusion Is Enough", Where Some May Be Absent

## Purpose
Exclusions add up: a file is dropped if the profile excludes it or the config
does. An absent exclusion excludes nothing, so it is dropped from the fold.
"""
