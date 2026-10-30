from typing import Final


DEFAULT_PROFILE_KEY: Final[str] = "generic/all"
"""The key of the built-in profile used when none is chosen."""


_DESIGN_NOTES = """
# DEFAULT_PROFILE_KEY — The Extractor Works on Its Own

## Purpose
`generic/all` takes every text file and changes nothing, so the extractor is
useful without any language add-on installed.
"""
