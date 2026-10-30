from collections.abc import Callable
from typing import Final


RENDERER_REGISTRY: Final[dict[str, Callable[..., str]]] = {}
"""The registered renderers, by format name."""


_DESIGN_NOTES = """
# RENDERER_REGISTRY — Formats Are Registered, Not Hard-Coded

## Purpose
`markdown` and `plain` are registered by the render phase when the package is
imported. A later format (a JSON manifest, say) needs one `register_renderer`
call and no change in the core.

## Why It Lives in the Registry
The configuration is resolved before anything is rendered, and it has to know
which formats exist. Keeping the dictionary here lets the select phase ask
without importing the render phase.
"""
