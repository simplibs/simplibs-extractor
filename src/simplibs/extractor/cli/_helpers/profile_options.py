# Outers
from ...registry import list_profiles


def profile_options(system: str) -> dict[str, str]:
    """Describe the profiles of one system for a list or a choice.

    Args:
        system: The system (`"python"`).

    Returns:
        `{profile name: description}`, sorted by name; empty for an unknown system.
    """

    # 1. The names are the system's own (`code-clean`), without the `system/` part
    return {profile.name: profile.description for profile in list_profiles(system)}


_DESIGN_NOTES = """
# profile_options — Names and Descriptions of One System

## Purpose
Feeds `--list-profiles` and the question "Which profiles?". An empty result
is how the caller learns that a system does not exist.
"""
