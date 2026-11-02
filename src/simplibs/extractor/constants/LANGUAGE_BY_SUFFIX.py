from types import MappingProxyType
from typing import Final


LANGUAGE_BY_SUFFIX: Final[MappingProxyType[str, str]] = MappingProxyType({
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".json": "json",
    ".md": "markdown",
    ".css": "css",
    ".html": "html",
    ".toml": "toml",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".sh": "bash",
    ".sql": "sql",
    ".txt": "text",
})
"""The built-in code-fence language of a file suffix. The registry starts from it; an add-on adds more with `register_language`."""


_DESIGN_NOTES = """
# LANGUAGE_BY_SUFFIX — Syntax Highlighting in the Output

## Purpose
A fenced block in Markdown is highlighted by its language name. The suffix is
the cheapest reliable way to pick it.

## Read-Only
A `MappingProxyType`, so no caller can change the table for everyone else.
The table that renderers actually ask is the language registry
(`get_language`), which starts as a copy of this one; an add-on registers
the suffixes of its own languages there with `register_language`.

## `.mjs` and `.cjs`
ES modules and CommonJS files with an explicit module type are JavaScript.
"""
