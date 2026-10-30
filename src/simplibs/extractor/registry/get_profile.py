from simplibs.validate import validate_call
# Outers
from ..definitions import Profile
# Inners
from ._helpers import PROFILE_REGISTRY
from ._validations import raise_profile_not_found_error

@validate_call
def get_profile(key: str) -> Profile:
    """Return the profile registered under a key.

    Args:
        key: The full key (`"python/code-clean"`).

    Returns:
        The registered profile.

    Raises:
        NotFoundError: If no profile has this key; the card lists the registered keys.
    """

    # 1. Look the key up
    profile = PROFILE_REGISTRY.get(key)

    # 2. Unknown key: say what exists
    if profile is None:
        raise_profile_not_found_error(key, sorted(PROFILE_REGISTRY))

    # 3. Found
    return profile


_DESIGN_NOTES = """
# get_profile — Lookup With a Useful Failure

## Purpose
The only reader of a single profile. The failure card lists the registered
keys, which is almost always what a mistyped key needs.
"""
