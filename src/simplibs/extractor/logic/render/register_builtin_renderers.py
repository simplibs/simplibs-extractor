# Outers
from ...registry import register_renderer
# Inners
from .render_markdown import render_markdown
from .render_plain import render_plain


def register_builtin_renderers() -> None:
    """Register the two built-in formats: `markdown` and `plain`."""

    # 1. `replace_existing`: importing again (or reloading) must not fail on our own formats
    register_renderer("markdown", render_markdown, replace_existing=True)
    register_renderer("plain", render_plain, replace_existing=True)


_DESIGN_NOTES = """
# register_builtin_renderers — The Core Uses the Same Door as Everyone

## Purpose
The built-in formats are registered like any later one, so the core never
branches on a format name.

## When It Runs
`logic/render/__init__.py` calls it on import, which is before any
configuration can be resolved.
"""
