from types import MappingProxyType
from typing import Final


LANGUAGE_BY_SUFFIX: Final[MappingProxyType[str, str]] = MappingProxyType({
    ".py": "python",
    ".js": "javascript",
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
"""The code-fence language of a file suffix. Unknown suffixes get no language."""


_DESIGN_NOTES = """
# LANGUAGE_BY_SUFFIX — Syntax Highlighting in the Output

## Purpose
A fenced block in Markdown is highlighted by its language name. The suffix is
the cheapest reliable way to pick it.

## Read-Only
A `MappingProxyType`, so no caller can change the table for everyone else.
"""
