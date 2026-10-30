# Outers
from ...registry import list_profiles, list_systems


def is_profile_reference(value: str) -> bool:
    """Check whether a command-line word names a registered system or registered profile keys.

    Args:
        value: The word (`"python"`, `"generic/all"`, `"python/a,python/b"`, `"./src"`).

    Returns:
        True if it is a system, or a comma list made only of registered full keys.
    """

    # 1. A system
    if value in list_systems():
        return True

    # 2. Full keys, one or several; every part must be registered
    keys = {profile.key for profile in list_profiles()}
    return all(part.strip() in keys for part in value.split(","))


_DESIGN_NOTES = """
# is_profile_reference — Profile or Folder?

## Purpose
`simplibs-extractor src` could mean "the system `src`" or "the folder
`src`". A word that is a registered system or key is a profile reference;
anything else may be a folder.

## Why the Registry Decides
Not the shape of the word: `generic/all` and `./src` both contain a slash.
"""
