import functools
import operator
from simplibs.rules import Rule


def all_of(*rules: Rule | None) -> Rule | None:
    """Combine rules with AND, ignoring the ones that are `None`.

    Args:
        *rules: The rules; `None` means "no rule here".

    Returns:
        One rule that needs every given rule to pass; `None` if no rule was given.
    """

    # 1. Keep only real rules
    present = [rule for rule in rules if rule is not None]

    # 2. Fold with `&`, or return None when there is nothing to combine
    return functools.reduce(operator.and_, present) if present else None


_DESIGN_NOTES = """
# all_of — "Every Rule Must Agree", Where Some May Be Absent

## Purpose
A profile and a config each may or may not have an `include` rule. This
folds whatever exists into one rule so the scan asks a single question.

## `None` Means No Constraint
For AND an absent rule changes nothing, so it is simply dropped.
"""
