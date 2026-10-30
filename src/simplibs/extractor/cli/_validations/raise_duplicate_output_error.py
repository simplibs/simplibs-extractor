from collections.abc import Sequence
from typing import NoReturn
from simplibs.exception import ParamError


def raise_duplicate_output_error(keys: Sequence[str]) -> NoReturn:
    """Raise ParamError when two or more profiles would write the same output file.

    Args:
        keys: The profile keys of the run.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="profiles",
        value=list(keys),
        problem="Two or more of these profiles write the same output file.",
        expected="Profiles with different output names, or one profile per run.",
        how_to_fix="Run the profiles separately, or give them different output_name values.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_duplicate_output_error — Two Profiles, One File

## Purpose
The profiles of one run would overwrite each other. Found before anything
runs, it costs nothing; found by `extract_many` it would cost the files the
earlier profiles had already written.
"""
