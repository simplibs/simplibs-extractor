from simplibs.validate import validate_call
# Outers
from ..definitions import Profile
# Inners
from ._helpers import PROFILE_REGISTRY
from ._validations import raise_profile_exists_error

@validate_call
def register_profile(
    profile: Profile,
    *,
    replace_existing: bool = False,
) -> Profile:
    """Register a profile under its key.

    Args:
        profile: The profile to register.
        replace_existing: Allow replacing a profile that already has this key.

    Returns:
        The registered profile, so the call can be used as an expression.

    Raises:
        AlreadyExistsError: If the key is taken and `replace_existing` is False.
    """

    # 1. Refuse a taken key unless replacing was asked for
    if profile.key in PROFILE_REGISTRY and not replace_existing:
        raise_profile_exists_error(profile.key)

    # 2. Store and hand back
    PROFILE_REGISTRY[profile.key] = profile
    return profile


_DESIGN_NOTES = """
# register_profile — How an Add-On Teaches the Extractor

## Purpose
The one entry point for new profiles. An add-on calls it for each of its
profiles when it is loaded.

## Returns the Profile
So a module can write `PYTHON_CLEAN = register_profile(Profile(...))` and
keep the object.
"""
