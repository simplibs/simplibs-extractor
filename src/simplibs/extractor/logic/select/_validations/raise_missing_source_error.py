from typing import NoReturn
from simplibs.exception import ParamError


def raise_missing_source_error() -> NoReturn:
    """Raise ParamError when no config and no `source` were given."""

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'source'",
        value=None,
        problem="No config and no 'source' were given.",
        expected="An ExtractionConfig, or at least source='path/to/folder'.",
        how_to_fix="Pass a config, or pass source=... as a keyword.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_missing_source_error — Nothing to Extract From

## Purpose
`source` is the one field without a default, so a run with no config needs it
as a keyword.
"""
