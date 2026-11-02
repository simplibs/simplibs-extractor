from simplibs.validate import validate_call
# Inners
from ._helpers import LANGUAGE_REGISTRY


@validate_call
def list_languages() -> dict[str, str]:
    """List the registered code-fence languages, sorted by suffix.

    Returns:
        A new dictionary `suffix -> language`; changing it changes nothing in the registry.
    """

    # 1. A sorted copy of the registry
    return dict(sorted(LANGUAGE_REGISTRY.items()))


_DESIGN_NOTES = """
# list_languages — A Copy, Never the Registry

## Purpose
For a person or a test that wants to know what the renderer will highlight.
The registry itself is never handed out, so nobody can change it behind the
back of `register_language`.
"""
