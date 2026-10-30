from collections.abc import Callable
from simplibs.validate import validate_call
# Outers
from ..annotations import OutputFormat
# Inners
from ._helpers import RENDERER_REGISTRY
from ._validations import raise_renderer_exists_error


@validate_call
def register_renderer(
    name: OutputFormat,
    func: Callable[..., str],
    *,
    replace_existing: bool = False,
) -> None:
    """Register a renderer under a format name.

    Args:
        name: The format name (`"markdown"`).
        func: The renderer: it takes the entries and the render context and returns the output text.
        replace_existing: Allow replacing a renderer that already has this name.

    Raises:
        ParamError: If the name is taken and `replace_existing` is False.
    """

    # 1. Refuse a taken name unless replacing was asked for
    if name in RENDERER_REGISTRY and not replace_existing:
        raise_renderer_exists_error(name)

    # 2. Store
    RENDERER_REGISTRY[name] = func


_DESIGN_NOTES = """
# register_renderer — Adding an Output Format

## Purpose
The built-in formats use it too, so there is one way to add a format and the
core never branches on a format name.

## The Renderer Signature
Described by the render phase (batch E4): entries in, text out. It is typed
here only as "a callable returning text", because the registry sits to the
left of the render phase.
"""
