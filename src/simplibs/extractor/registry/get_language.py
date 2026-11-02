from simplibs.validate import validate_call
# Inners
from ._helpers import LANGUAGE_REGISTRY


@validate_call
def get_language(suffix: str) -> str | None:
    """Return the code-fence language registered for a file suffix.

    Args:
        suffix: The suffix with its dot (`".py"`); the case is ignored.

    Returns:
        The language name (`"python"`), or `None` if nobody registered this suffix.
    """

    # 1. Look the suffix up, lowercased like the keys
    return LANGUAGE_REGISTRY.get(suffix.lower())


_DESIGN_NOTES = """
# get_language — Not Finding It Is an Answer

## Purpose
`render_markdown` asks it for every file. A suffix without a language is
normal (a `Makefile`, `.lua` before the add-on is installed), so the answer
is `None` and not an error; the renderer decides what to write in that case.
"""
