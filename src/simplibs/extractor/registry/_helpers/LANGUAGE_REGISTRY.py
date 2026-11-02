from typing import Final
# Outers
from ...constants import LANGUAGE_BY_SUFFIX


LANGUAGE_REGISTRY: Final[dict[str, str]] = dict(LANGUAGE_BY_SUFFIX)
"""The registered code-fence languages, by suffix. It starts as a copy of `LANGUAGE_BY_SUFFIX`."""


_DESIGN_NOTES = """
# LANGUAGE_REGISTRY — Languages Are Registered, Not Hard-Coded

## Purpose
A Markdown fence is highlighted by its language name. The built-in table
knows the common suffixes; an add-on that brings a language of its own (`.lua`,
`.rs`) registers its suffix with one `register_language` call and no change
in the core.

## A Copy, Not the Constant
`LANGUAGE_BY_SUFFIX` is read-only, so no caller can change the built-in table
for everyone. The registry starts as a copy of it and is the one that can grow.
"""
