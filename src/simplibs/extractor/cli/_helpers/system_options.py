# Outers
from ...registry import list_profiles, list_systems


def system_options() -> dict[str, str]:
    """Describe the registered systems for a list or a choice.

    Returns:
        `{system: "N profile(s)"}`, sorted by system.
    """

    # 1. One entry per system, with the number of its profiles
    return {system: f"{len(list_profiles(system))} profile(s)" for system in list_systems()}


_DESIGN_NOTES = """
# system_options — What `--list-systems` and the First Question Show

## Purpose
One function for both, so a list and a question never disagree about which
systems exist.
"""
