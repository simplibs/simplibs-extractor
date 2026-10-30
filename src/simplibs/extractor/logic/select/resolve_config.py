import dataclasses
from collections.abc import Mapping
from typing import Any
from simplibs.path import normalize_path
# Outers
from ...definitions import ExtractionConfig, Resolved
from ...registry import get_renderer
# Inners
from .resolve_profile import resolve_profile
from ._validations import (
    raise_missing_source_error,
    raise_unknown_parameter_error,
    raise_source_not_found_error
)


def resolve_config(
    config: ExtractionConfig | None,
    overrides: Mapping[str, Any],
) -> Resolved:
    """Fill in every default and check what can be checked before any file is read.

    Args:
        config: A ready config, or `None` to build one from `overrides` alone.
        overrides: Config fields to set (or to change in `config`).

    Returns:
        The resolved plan: a normalized source, a concrete target, a profile
        object and a known format.

    Raises:
        ParamError: For an unknown field, a missing source or an unknown format.
        NotFoundError: If the source is not a directory or a profile key is unknown.
    """

    # 1. Reject names that are not config fields (a typo should not vanish)
    known = sorted(field.name for field in dataclasses.fields(ExtractionConfig))
    unknown = sorted(set(overrides) - set(known))
    if unknown:
        raise_unknown_parameter_error(unknown, known)

    # 2. Build or change the config
    if config is None:
        if "source" not in overrides:
            raise_missing_source_error()
        config = ExtractionConfig(**overrides)
    elif overrides:
        config = dataclasses.replace(config, **overrides)

    # 3. The source must be a real folder
    source = normalize_path(config.source)
    if not source.is_dir():
        raise_source_not_found_error(source)

    # 4. The profile, and from it the default target and format
    profile = resolve_profile(config.profile)
    target = normalize_path(config.target) if config.target is not None else source / profile.output_name
    output_format = config.format if config.format is not None else profile.format

    # 5. The format must have a renderer (raises with the list of known formats)
    get_renderer(output_format)

    # 6. Everything is concrete from here on
    resolved_config = dataclasses.replace(config, source=source, target=target)
    return Resolved(resolved_config, profile, output_format)


_DESIGN_NOTES = """
# resolve_config — Everything That Can Fail Before the Work Starts

## Purpose
Turns "what the caller wrote" into "what the run will do" and refuses early.
A wrong folder, an unknown profile or an unknown format cost nothing here;
found after a scan they would cost the whole scan.

## Unknown Parameters Are Checked by Name
`extract(sourse=...)` must not disappear into `**overrides`. The card lists
the valid names.

## The Target Is Never `None` Afterwards
`source / profile.output_name` unless the caller chose a path.

## Not a Public Function
Called by `extract()`, which is the validated entry point.
"""
