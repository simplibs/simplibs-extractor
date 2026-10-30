from .RenderContext import RenderContext
from .build_tree import build_tree
from .register_builtin_renderers import register_builtin_renderers
from .render_markdown import render_markdown
from .render_plain import render_plain


# The built-in formats exist as soon as the render phase is imported
register_builtin_renderers()


_DESIGN_NOTES = """
# logic/render — Phase 4: Turn Entries Into Text

Plain imports, no `__all__`. The only side effect of importing this package
is the registration of the formats `markdown` and `plain`.

## Internal Components Registry

| Component                    | Type      | Description                                        |
| :--------------------------- | :-------- | :------------------------------------------------- |
| `RenderContext`              | Dataclass | Title, source, profile and tree switch.            |
| `build_tree`                 | Function  | Draws a directory tree from relative paths.        |
| `register_builtin_renderers` | Function  | Registers `markdown` and `plain`.                  |
| `render_markdown`            | Function  | Renders the entries as a Markdown document.        |
| `render_plain`               | Function  | Renders the entries in the old `# FILE:` layout.   |

## Renderer Contract
`renderer(entries: Sequence[Entry], context: RenderContext) -> str`. A new
format is a function of that shape plus a `register_renderer` call.
"""
