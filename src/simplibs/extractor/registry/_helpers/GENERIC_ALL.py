from typing import Final
# Outers
from ...definitions import Profile


GENERIC_ALL: Final[Profile] = Profile(
    system="generic",
    name="all",
    description="Every text file, unchanged.",
)
"""The built-in profile: no rules of its own, no steps."""


_DESIGN_NOTES = """
# GENERIC_ALL — The Profile That Needs No Add-On

## Purpose
With it the extractor is useful on its own: it takes every text file the scan
finds and changes nothing. The read phase drops binary files, so the profile
needs no rules.

## Registered by the Registry
`registry/__init__.py` registers it when the package is imported.
"""
