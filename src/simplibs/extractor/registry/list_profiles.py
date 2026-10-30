from simplibs.validate import validate_call
# Outers
from ..definitions import Profile
# Inners
from ._helpers import PROFILE_REGISTRY


@validate_call
def list_profiles(system: str | None = None) -> list[Profile]:
    """List the registered profiles, sorted by key.

    Args:
        system: Only the profiles of this system; `None` lists all.

    Returns:
        A new list; changing it does not touch the registry.
    """

    # 1. Sort by key so listings are stable
    profiles = sorted(PROFILE_REGISTRY.values(), key=lambda profile: profile.key)

    # 2. Narrow to one system if asked
    return [profile for profile in profiles if system is None or profile.system == system]


_DESIGN_NOTES = """
# list_profiles — A Stable, Detached Listing

## Purpose
Feeds `--list-profiles`, the interactive choice and the tests. The result is
a copy, so the registry cannot be changed through it.
"""
