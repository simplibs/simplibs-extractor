import argparse
from collections.abc import Sequence
from pathlib import Path
from simplibs.path import normalize_path
# Outers
from ..definitions import ExtractionConfig
from ..registry import get_profile
# Inners
from ._validations import raise_duplicate_output_error, raise_output_is_file_error


def build_configs(
    args: argparse.Namespace,
    keys: Sequence[str],
    source: Path,
    dry_run: bool,
) -> list[ExtractionConfig]:
    """Make one `ExtractionConfig` per profile key.

    Args:
        args: The normalized arguments.
        keys: The full profile keys.
        source: The source folder.
        dry_run: Whether the run only plans.

    Returns:
        The configs, in the order of the keys. Each writes
        `<output folder>/<profile.output_name>`.

    Raises:
        NotFoundError: If a key is not registered.
        ParamError: If the output folder is a file, or two profiles would write the same file.
    """

    # 1. The output folder: `-o` or the source itself; it must not be a file
    out_dir = normalize_path(args.output) if args.output else normalize_path(source)
    if out_dir.is_file():
        raise_output_is_file_error(out_dir)

    # 2. One config per key; an unknown key fails here, before anything runs
    configs = [
        ExtractionConfig(
            source=source,
            target=out_dir / get_profile(key).output_name,
            profile=key,
            format=args.format,
            overwrite=args.overwrite,
            dry_run=dry_run,
            add_tree=args.add_tree,
        )
        for key in keys
    ]

    # 3. Two profiles with the same output name would overwrite each other
    targets = [config.target for config in configs]
    if len(set(targets)) != len(targets):
        raise_duplicate_output_error(keys)

    return configs


_DESIGN_NOTES = """
# build_configs — From Words to Configurations

## Purpose
The last step of the command line: every profile becomes one config, and
`extract_many` runs them.

## Checked Before Anything Runs
A mistyped key, a file given as the output folder and two profiles aiming at
one file are all the person's mistakes and cost nothing to find here.
`extract_many` would report them too, but only after the earlier profiles had
already written their files.

## `target` Is Given, `format` May Be `None`
`None` lets each profile use its own format.
"""
