from typing import Annotated
# Inners
from ._helpers import is_output_format


OutputFormat = Annotated[str, is_output_format]
"""The name of an output format (`"markdown"`, `"plain"`, or a registered one).

A lowercase name that starts with a letter. Whether a renderer with that
name exists is checked when the configuration is resolved.
"""


_DESIGN_NOTES = """
# OutputFormat — a Name, Not a Closed List

## Purpose
Renderers are registered by name, so the set of formats is open. A `Literal`
would freeze it at the two built-in formats and make every added renderer a
typing error.

## Why `Annotated`
An editor sees a plain `str`; `@validate_call` reads the predicate from the
metadata and rejects `"Markdown"`, `""` or `"md file"` at the signature.
"""
