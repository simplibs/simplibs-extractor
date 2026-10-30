from typing import Final
# Outers
from ...definitions import Profile


PROFILE_REGISTRY: Final[dict[str, Profile]] = {}
"""The registered profiles, by key (`"system/name"`)."""


_DESIGN_NOTES = """
# PROFILE_REGISTRY — The One Place Profiles Live

## Purpose
Module-level state shared by every function of the registry. It is a private
detail: callers use `register_profile`, `get_profile` and `list_profiles`,
never the dictionary itself.

## Why a Dictionary and Not a Class
There is exactly one registry per process, and add-ons register into it when
they are imported. A class would only add an instance nobody else may create.
"""
