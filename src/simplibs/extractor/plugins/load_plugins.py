import importlib.metadata
# Outers
from ..constants import PLUGIN_GROUP
from ..logic._common import describe_failure


def load_plugins(
    *,
    group: str = PLUGIN_GROUP,
    entry_points=None,
) -> tuple[list[str], dict[str, str]]:
    """Find the installed add-ons and let each register its profiles.

    Every entry point of the group names a function that takes no arguments
    and registers profiles (and renderers) in the extractor's registry.

    Args:
        group: The entry-point group.
        entry_points: A replacement for `importlib.metadata.entry_points` (for tests);
            called as `entry_points(group=group)`.

    Returns:
        A pair: the names of the add-ons that loaded, and a dictionary
        `{name: one-line reason}` of those that failed. A failed add-on never
        stops the others.
    """

    # 1. The real lookup, unless a test supplies its own
    finder = entry_points or importlib.metadata.entry_points

    # 2. Load and run each add-on; its code is foreign, so any error of it is its own
    loaded: list[str] = []
    failed: dict[str, str] = {}
    for entry_point in finder(group=group):
        try:
            entry_point.load()()
        except Exception as exc:
            failed[entry_point.name] = describe_failure(exc)
        else:
            loaded.append(entry_point.name)

    return loaded, failed


_DESIGN_NOTES = """
# load_plugins — Installed Add-Ons Show Up on Their Own

## Purpose
`pip install simplibs-code-extractor` is the whole installation: the next
`simplibs-extractor --list-systems` already shows `python` and `react`.

## Returns Failures Instead of Logging Them
A broken add-on should not take the tool down, and the person should still
hear about it. The function reports; the caller (the command line) decides
how to say it.

## The Second Broad `except`
As in `process_source`: the code is someone else's, and "this add-on does not
load" is the useful answer whatever the cause.

## Safe to Call Twice
Add-ons register with `replace_existing=True`, so calling the function again
(a second `run_cli` in a test, a reload) changes nothing.
"""
