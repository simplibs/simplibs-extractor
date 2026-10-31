from pathlib import Path
from simplibs.file import write_text
from simplibs.path import PathLike, normalize_path
# Outers
from ..constants import DEFAULT_SCRIPT_NAME
from ..definitions import Profile
from ..logic.select import resolve_profile
from ..plugins import load_plugins
# Inners
from ._validations import raise_not_python_script_error
from .render_script import render_script


def generate_local_script(
    path: PathLike,
    profile: Profile | str | None = None,
    *,
    overwrite: bool = False,
) -> Path:
    """Write a local extraction script.

    Args:
        path: The script file (`*.py`), or a folder, which gets `extract_here.py`.
        profile: A `Profile`, a registered key, or `None` for `generic/all`. A key may belong to
            an add-on; the installed add-ons are loaded first (see `load_plugins`).
        overwrite: Replace the script if it already exists.

    Returns:
        The path of the written script.

    Raises:
        ParamError: If the file name does not end with `.py`.
        NotFoundError: If the profile is not registered.
        AlreadyExistsError: If the script exists and `overwrite` is False.
    """

    # 1. A folder means "the default name in it"
    target = normalize_path(path)
    if target.is_dir():
        target = target / DEFAULT_SCRIPT_NAME

    # 2. It has to be a Python file, or it could not be run
    if target.suffix != ".py":
        raise_not_python_script_error(target)

    # 3. A key may belong to an add-on that has not registered yet: let the installed ones do it first
    if isinstance(profile, str):
        load_plugins()

    # 4. The profile is resolved now, so a typo fails before anything is written
    key = resolve_profile(profile).key

    # 5. Written atomically; `overwrite=False` makes the file library refuse an existing script
    return write_text(target, render_script(target.name, key), overwrite=overwrite)


_DESIGN_NOTES = """
# generate_local_script — Drop an Extractor Into a Project

## Purpose
`simplibs-extractor init` calls this. A project gets a script it can run
without remembering any command line.

## An Existing Script Is Not Replaced Quietly
It may have been edited. `overwrite=True` has to be asked for, and the card
that refuses is the one `simplibs-file` already raises.

## Loads Add-Ons Itself, for a Key
The key usually names a profile of an add-on, and nothing has registered it
yet in a fresh process. Loading the installed add-ons first is what lets
`init` and a direct call accept `python/code-clean`. Only for a key: a
`Profile` object or `None` needs nothing found.

## Only the Profile's Key Is Stored
Not the profile itself: the script must work in a Python where the profile's
add-on is installed, and fail clearly where it is not.
"""
