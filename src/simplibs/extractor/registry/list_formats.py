from simplibs.validate import validate_call
# Inners
from ._helpers import RENDERER_REGISTRY


@validate_call
def list_formats() -> list[str]:
    """List the registered output formats, sorted."""

    # 1. Sorted names of the registered renderers
    return sorted(RENDERER_REGISTRY)


_DESIGN_NOTES = """
# list_formats — The Choices Behind `--format`

## Purpose
The CLI shows the choices from here instead of a fixed list, so a registered
format appears without a change in the CLI.
"""
