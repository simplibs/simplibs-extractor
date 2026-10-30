from simplibs.exception import SimpleException
# Outers
from ..constants import DEFAULT_PROFILE_KEY
from ..definitions import ExtractionConfig, ExtractionResult, Profile
# Inners
from ._common import describe_failure


def failure_result(
    config: ExtractionConfig,
    error: SimpleException,
) -> ExtractionResult:
    """Turn the error of a run that could not start into a result.

    Args:
        config: The config of the failed run.
        error: The error that stopped it.

    Returns:
        A result with `fatal` set to a one-line description, no files and no output.
    """

    # 1. The profile's key as far as it is known without resolving anything
    profile = config.profile
    if isinstance(profile, Profile):
        key = profile.key
    else:
        key = profile or DEFAULT_PROFILE_KEY

    # 2. Everything else stays at its empty default
    return ExtractionResult(
        config=config,
        profile_key=key,
        target=None,
        dry_run=config.dry_run,
        fatal=describe_failure(error),
    )


_DESIGN_NOTES = """
# failure_result — A Failed Run Is Still a Result

## Purpose
`extract_many` runs several configs. If one of them is broken, the others
should still run and the report should still list all of them; a result with
`fatal` set is how the broken one appears in that list.
"""
