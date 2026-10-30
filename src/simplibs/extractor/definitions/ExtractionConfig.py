from dataclasses import dataclass
from simplibs.file import ByteCount
from simplibs.path import PathLike
from simplibs.rules import Rule
from simplibs.validate import validate_dataclass
# Outers
from ..annotations import OutputFormat, OverwritePolicy
from ..constants import DEFAULT_MAX_FILE_SIZE
# Inners
from .Profile import Profile


@validate_dataclass
@dataclass(frozen=True, slots=True)
class ExtractionConfig:
    """Everything one extraction needs to know.

    Attributes:
        source: The folder to extract from.
        target: The output file; `None` means `source / profile.output_name`.
        profile: A `Profile`, a registered key (`"python/code-clean"`), or `None` for `generic/all`.
        include: A rule on the relative path, combined with the profile's by AND.
        exclude: A rule on the relative path, combined with the profile's by OR.
        ignore_names: Folder and file names the scan skips; `None` means the default set.
        recursive: Whether sub-folders are scanned.
        format: The output format; `None` means the profile's.
        overwrite: What to do when the output exists.
        dry_run: Plan everything, write nothing.
        max_file_size: Larger files are skipped; `None` switches the limit off.
        add_tree: Whether the output starts with a directory tree.
        title: The heading of the output; `None` means a generated one.
        skip_paths: Extra files that never enter the extraction (for example an embedded script).
    """

    source: PathLike
    target: PathLike | None = None
    profile: Profile | str | None = None
    include: Rule | None = None
    exclude: Rule | None = None
    ignore_names: frozenset[str] | None = None
    recursive: bool = True
    format: OutputFormat | None = None
    overwrite: OverwritePolicy = "overwrite"
    dry_run: bool = False
    max_file_size: ByteCount | None = DEFAULT_MAX_FILE_SIZE
    add_tree: bool = True
    title: str | None = None
    skip_paths: tuple[PathLike, ...] = ()


_DESIGN_NOTES = """
# ExtractionConfig — One Run, Fully Described

## Purpose
The single input of `extract()`. Keyword overrides of `extract()` are applied
with `dataclasses.replace`, so a ready config can be reused with one change.

## One Rule, Not a List
`include` and `exclude` are single `Rule` objects; the caller composes them
with `&`, `|` and `~`. A list would leave open whether its items combine by
AND or by OR.

## The Config Can Only Narrow
`include` is combined with the profile's by AND and `exclude` by OR, so a
config never widens what a profile selected.

## Raw Values
`source`, `target` and `profile` are stored as given. Normalizing and
resolving them is the job of `resolve_config`, which returns a `Resolved`.

## Validated, Unlike the Result Types
This is user input, so `@validate_dataclass` checks it. `FileReport`,
`ExtractionResult`, `Entry` and `Resolved` are built by the library itself
and stay plain dataclasses.
"""
