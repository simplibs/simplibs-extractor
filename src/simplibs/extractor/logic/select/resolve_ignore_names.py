from simplibs.file import IGNORE_DRAFTS
from simplibs.path import DEFAULT_IGNORE_NAMES


def resolve_ignore_names(ignore_names: frozenset[str] | None) -> frozenset[str]:
    """Return the names the scan skips.

    Args:
        ignore_names: The names chosen in the config, or `None`.

    Returns:
        The chosen names as they are, or — for `None` — the default set of
        `simplibs.path` plus the draft files of `SafeFileWriter`.
    """

    # 1. A choice replaces the default completely
    if ignore_names is not None:
        return ignore_names

    # 2. Default: the usual housekeeping folders and half-written drafts
    return DEFAULT_IGNORE_NAMES | IGNORE_DRAFTS


_DESIGN_NOTES = """
# resolve_ignore_names — What the Scan Never Looks At

## Purpose
The extractor writes its output with `SafeFileWriter`, which leaves a draft
file for the moment of the write (or for good after a crash). The default must
therefore include `IGNORE_DRAFTS`, which `simplibs-path` does not know.

## A Choice Replaces, It Does Not Extend
`ignore_names=frozenset({"vendor"})` means exactly that. A caller who wants
the default plus something writes `DEFAULT_IGNORE_NAMES | {...}` themselves,
the same rule `simplibs-path` follows.
"""
