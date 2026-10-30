from pathlib import Path
from simplibs.path import collect_files, normalize_path, relativize_path
# Outers
from ...definitions import Resolved
# Inners
from .all_of import all_of
from .any_of import any_of
from .resolve_ignore_names import resolve_ignore_names


def select_sources(plan: Resolved) -> list[Path]:
    """Collect the files an extraction takes.

    The rules of the profile and the config are evaluated on the path
    **relative to the source**, so it does not matter where the project lies
    on the disk. Rules that need the disk (size, content) do not belong here;
    the read phase handles them.

    Args:
        plan: The resolved configuration.

    Returns:
        The absolute paths of the selected files, sorted.
    """
    config, profile = plan.config, plan.profile

    # 1. One rule each: the config can only narrow the profile
    include = all_of(profile.include, config.include)
    exclude = any_of(profile.exclude, config.exclude)

    # 2. Scan the folder (only collecting; the rules are applied below)
    files = collect_files(
        config.source,
        recursive=config.recursive,
        ignore_names=resolve_ignore_names(config.ignore_names),
    )

    # 3. Never read the output itself or anything the caller asked to skip
    banned = {config.target, *(normalize_path(path) for path in config.skip_paths)}

    # 4. Apply the rules to the relative path
    selected: list[Path] = []
    for file in files:
        if normalize_path(file) in banned:
            continue
        try:
            relative = file.relative_to(config.source)       # lexically: a link keeps its own name
        except ValueError:
            relative = relativize_path(file, root=config.source)
        if include is not None and not include(relative):
            continue
        if exclude is not None and exclude(relative):
            continue
        selected.append(file)

    return selected


_DESIGN_NOTES = """
# select_sources — Which Files Take Part

## Purpose
The whole select phase in one function: scan, drop the output and the skipped
files, apply the include and exclude rules.

## Relative Paths
With an absolute path a rule such as "any parent folder is named `tests`"
would drop a whole project that merely lies inside a folder called `tests`.
On the relative path only the project's own folders count.

## The Output Is Never Its Own Input
`config.target` and `skip_paths` are removed first. Older outputs under other
names are caught later by the read phase (`GENERATED_MARKER`).

## Why Not `include_filter` of `collect_files`
Those filters would see absolute paths. The scan only collects; the rules
are applied here.

## Symbolic Links
The relative path is taken lexically (`file.relative_to(source)`), so a link
keeps its own name and the rules see `link.txt`, not where it points.
`relativize_path` resolves links first and would refuse one that leads out of
the source. Whether a link's content may be read is decided by the read phase
(`read_source`), which skips a link that leads outside the source.
"""
