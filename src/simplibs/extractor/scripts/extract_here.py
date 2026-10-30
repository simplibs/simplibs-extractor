from typing import Any
from simplibs.path import PathLike, is_valid_filename, normalize_path
# Outers
from ..definitions import ExtractionResult, Profile
from ..logic import extract
from ..logic.select import resolve_profile
# Inners
from ._helpers import print_result
from ._validations import raise_invalid_output_name_error


def extract_here(
    anchor: PathLike,
    profile: Profile | str | None = None,
    *,
    output_name: str | None = None,
    quiet: bool = False,
    logger: Any = None,
    **overrides: Any,
) -> ExtractionResult:
    """Extract the folder a script lies in, into a file next to the script.

    The two-line script:

        from simplibs.extractor import extract_here
        extract_here(__file__, profile="python/code-clean")

    Args:
        anchor: `__file__` of the script (its folder is the source and the script itself
            is left out of the output), or a folder.
        profile: A `Profile`, a registered key, or `None` for `generic/all`.
        output_name: The output file name; by default the profile's.
        quiet: If True, print nothing.
        logger: Where progress goes (see `extract`).
        **overrides: Any other `ExtractionConfig` field; these win over what is derived here.

    Returns:
        The result of the extraction.

    Raises:
        ParamError, NotFoundError: As for `extract` (unknown profile, ...).
    """

    # 1. Where we are: a file means "its folder", a folder means itself
    anchor_path = normalize_path(anchor)
    is_file = anchor_path.is_file()
    root = anchor_path.parent if is_file else anchor_path

    # 2. The profile is resolved now: its output name is needed and a typo should fail first
    chosen = resolve_profile(profile)

    # 3. A file name, not a path: the output always lies in the script's folder
    name = output_name if output_name is not None else chosen.output_name
    if not is_valid_filename(name):
        raise_invalid_output_name_error(name)

    # 4. Derived values first, then the caller's own; the script is never its own input
    skipped = tuple(overrides.pop("skip_paths", ())) + ((anchor_path,) if is_file else ())
    params: dict[str, Any] = {
        "source": root,
        "target": root / name,
        "profile": chosen,
        "skip_paths": skipped,
    }
    params.update(overrides)

    # 5. Run, then show the outcome unless asked not to
    result = extract(logger=logger, **params)
    if not quiet:
        print_result(result)
    return result


_DESIGN_NOTES = """
# extract_here — The Whole Script in One Call

## Purpose
A script lies in the folder it should extract, and says only which profile.
Source, target and the exclusion of the script itself follow from where it is.

## Derived Values Lose to Explicit Ones
`extract_here(__file__, target=..., recursive=False)` works: what the caller
passes replaces what was derived, except `skip_paths`, which is extended (the
script must stay out of its own output).

## Prints, Unlike Everything Else
Library functions stay silent and return a result. A script has no one to
print for it, so this entry point does, unless `quiet=True`.

## Not Wrapped in `@validate_call`
The inputs are checked where they are used: the profile by the registry, the
file name here, everything else by `ExtractionConfig`.
"""
