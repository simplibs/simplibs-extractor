from simplibs.validate import validate_call
# Inners
from ._helpers import PROFILE_REGISTRY


@validate_call
def list_systems() -> list[str]:
    """List the systems that have at least one registered profile, sorted."""

    # 1. Each profile names its system; a set removes the repeats
    return sorted({profile.system for profile in PROFILE_REGISTRY.values()})


_DESIGN_NOTES = """
# list_systems — Which Families Exist

## Purpose
Feeds `--list-systems` and the first question of the interactive wizard.
A system is not registered on its own; it exists while a profile names it.
"""
