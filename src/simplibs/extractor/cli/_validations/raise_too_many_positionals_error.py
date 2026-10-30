from pathlib import Path
from typing import NoReturn
from simplibs.exception import ParamError


def raise_too_many_positionals_error(
    system: str,
    profiles: str | None,
    source: Path,
) -> NoReturn:
    """Raise ParamError when full profile keys are followed by two more words.

    Args:
        system: The first word, which holds the full keys.
        profiles: The second word.
        source: The third word.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="command-line arguments",
        value=[system, profiles, str(source)],
        problem="Full profile keys were followed by two more words.",
        expected="KEYS [SOURCE] or SYSTEM PROFILES [SOURCE].",
        how_to_fix="Write 'generic/all ./src', or 'python code-clean ./src'.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_too_many_positionals_error — Keys Plus Two Words

## Purpose
`generic/all a b` fits neither `KEYS [SOURCE]` nor `SYSTEM PROFILES [SOURCE]`;
the card shows both valid shapes.
"""
