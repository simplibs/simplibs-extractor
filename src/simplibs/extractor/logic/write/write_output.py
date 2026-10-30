from pathlib import Path
from simplibs.file import backup_file, write_text
from simplibs.path import make_unique_path
# Outers
from ...annotations import OverwritePolicy
# Inners
from ._validations import raise_target_exists_error, raise_target_is_dir_error


def write_output(
    target: Path,
    text: str,
    policy: OverwritePolicy,
    dry_run: bool,
) -> Path:
    """Write the output according to the overwrite policy, or only plan the write.

    Args:
        target: The intended output file.
        text: The rendered output.
        policy: What to do when `target` exists (`overwrite`, `unique`, `backup`, `error`).
        dry_run: If True, decide everything and write nothing.

    Returns:
        The path that is (or, in a dry run, would be) written. It differs from
        `target` only under the `unique` policy.

    Raises:
        StateError: If `target` is a directory.
        AlreadyExistsError: If `target` exists and the policy is `error`, even in a dry run.
    """

    # 1. A directory can never be the output, real run or not
    if target.is_dir():
        raise_target_is_dir_error(target)

    # 2. The `error` policy fails before anything else, also in a dry run
    exists = target.exists()
    if exists and policy == "error":
        raise_target_exists_error(target)

    # 3. `unique` writes next to the existing file under a numbered name
    final = make_unique_path(target) if exists and policy == "unique" else target

    # 4. A dry run stops here: the decision is made, the disk is untouched
    if dry_run:
        return final

    # 5. `backup` keeps the old file before it is replaced
    if exists and policy == "backup":
        backup_file(target)

    # 6. The write itself is atomic (draft and swap); the folder is created if missing
    write_text(final, text)
    return final


_DESIGN_NOTES = """
# write_output — The Only Place the Extractor Touches the Disk

## Purpose
All four overwrite policies and the dry run in one short function, so the
rule "a dry run reports what the real run would do" is easy to see.

## Dry Run Gives the Same Verdicts
A directory in the way and the `error` policy are checked before the dry-run
exit. A dry run that passes and a real run that then fails would be worse
than no dry run.

## Backups Are Copies With the Marker
`backup_file` copies the old output, marker included, so the next scan
recognizes the backup as generated and skips it.

## Raw Text
The output is written as it was rendered. `write_text` uses `"\\n"` line
endings and UTF-8 without a BOM by default, the same on every platform.
"""
