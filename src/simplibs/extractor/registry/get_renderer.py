from collections.abc import Callable
from simplibs.validate import validate_call
# Inners
from ._helpers import RENDERER_REGISTRY
from ._validations import raise_unknown_renderer_error


@validate_call
def get_renderer(name: str) -> Callable[..., str]:
    """Return the renderer registered for a format name.

    Args:
        name: The format name (`"markdown"`).

    Returns:
        The renderer function.

    Raises:
        ParamError: If no renderer has this name; the card lists the known formats.
    """

    # 1. Look the name up
    renderer = RENDERER_REGISTRY.get(name)

    # 2. Unknown format: say what exists
    if renderer is None:
        raise_unknown_renderer_error(name)

    # 3. Found
    return renderer


_DESIGN_NOTES = """
# get_renderer — Also the Format Check

## Purpose
`resolve_config` calls it to learn that a format exists before any file is
read, so a typo fails in the first millisecond and not after the whole
scan.
"""
