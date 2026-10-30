from collections.abc import Mapping
from typing import TypeAlias
from simplibs.actions import Action


StepsSpec: TypeAlias = Action | Mapping[str, Action] | None
"""How a profile transforms file text.

`None` keeps the text as it is. One `Action` is applied to every file. A
mapping `suffix -> Action` applies the action of the file's own suffix
(`".py"`); the key `"*"` is the fallback for every other file.
"""


_DESIGN_NOTES = """
# StepsSpec — One Pipeline or One Pipeline per Language

## Purpose
A step receives only the text, never the path, so it cannot know which
language it is cleaning. A profile that cleans Python and JavaScript
differently therefore needs a mapping from suffix to action.

## Why Not Always a Mapping
Most profiles apply one action to everything; forcing `{"*": action}` on them
would be noise.
"""
