# Outers
from ...constants import DEFAULT_PROFILE_KEY
from ...definitions import Profile
from ...registry import get_profile


def resolve_profile(profile: Profile | str | None) -> Profile:
    """Turn a profile, a key or `None` into a profile object.

    Args:
        profile: A `Profile` (used as it is), a registered key, or `None` for the default.

    Returns:
        The profile.

    Raises:
        NotFoundError: If a key is not registered.
    """

    # 1. Nothing chosen: the built-in profile
    if profile is None:
        return get_profile(DEFAULT_PROFILE_KEY)

    # 2. Already a profile
    if isinstance(profile, Profile):
        return profile

    # 3. A key
    return get_profile(profile)


_DESIGN_NOTES = """
# resolve_profile — Three Ways to Name a Profile, One Result

## Purpose
`ExtractionConfig.profile` accepts a ready object (for a one-off profile that
is never registered), a key (the everyday case) or nothing.
"""
