from collections.abc import Sequence
from typing import Any
from simplibs.exception import SimpleException
from simplibs.validate import validate_call
# Outers
from ..definitions import ExtractionConfig, ExtractionResult
# Inners
from .extract import extract
from .failure_result import failure_result


@validate_call
def extract_many(
    configs: Sequence[ExtractionConfig],
    *,
    logger: Any = None,
    stop_on_error: bool = False,
) -> list[ExtractionResult]:
    """Run several extractions one after another.

    A run that cannot start or cannot write does not stop the others: it
    appears in the list as a result with `fatal` set.

    Args:
        configs: The configurations, in the order to run them.
        logger: Where progress goes (see `extract`).
        stop_on_error: If True, stop after the first run that failed.

    Returns:
        One result per run that was started, in order.
    """

    # 1. One result per config; a library error becomes a failed result
    results: list[ExtractionResult] = []
    for config in configs:
        try:
            results.append(extract(config, logger=logger))
        except SimpleException as exc:
            results.append(failure_result(config, exc))
            if stop_on_error:
                break

    return results


_DESIGN_NOTES = """
# extract_many — Several Profiles in One Command

## Purpose
`simplibs-extractor python code-clean,data-all` is two extractions. A typo in
the second profile must not throw away the first one's output.

## What Is Caught
Only the library's own cards (`SimpleException`). A bug in the code or in a
step is not a "failed run" and keeps its traceback.

## Order
Results come back in the order of the configs, so they can be zipped back
with them.
"""
