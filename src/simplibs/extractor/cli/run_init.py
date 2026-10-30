import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from simplibs.cli import is_interactive, prompt_choice
from simplibs.exception import SimpleError
from simplibs.style import SUCCESS
# Outers
from ..constants import DEFAULT_PROFILE_KEY
from ..registry import list_profiles
from ..scripts import generate_local_script
# Inners
from ._helpers import print_error


def run_init(argv: Sequence[str]) -> int:
    """The `init` command: write a local `extract_here.py` script.

    Args:
        argv: The arguments after the word `init`.

    Returns:
        The exit code: 0 if the script was written, 2 if the command was refused.
    """

    # 1. The command's own small parser
    parser = argparse.ArgumentParser(prog="simplibs-extractor init", description="Write a local extraction script.")
    parser.add_argument("directory", nargs="?", type=Path, default=Path("."), help="the folder for the script (default: here)")
    parser.add_argument("--profile", help="the profile key the script uses (default: asked, or generic/all)")
    parser.add_argument("--force", action="store_true", help="replace an existing script")
    args = parser.parse_args(list(argv))

    # 2. No profile given: a terminal is asked, anything else gets the default
    profile = args.profile
    if profile is None and is_interactive():
        options = {item.key: item.description for item in list_profiles()}
        profile = prompt_choice("Profile", options, default=DEFAULT_PROFILE_KEY)

    # 3. Write the script; every refusal of the library is a card
    try:
        created = generate_local_script(args.directory, profile, overwrite=args.force)
    except SimpleError as exc:
        print_error(exc)
        return 2

    # 4. Say what to do next
    print(SUCCESS(f"Created: {created}"))
    print(f"Run it with:  {Path(sys.executable).name} {created.name}")
    return 0


_DESIGN_NOTES = """
# run_init — A Script You Can Double-Click

## Purpose
`simplibs-extractor init my_project` leaves a two-line script in the project;
from then on the extraction is `python extract_here.py`.

## Default Without a Terminal
`generic/all` (what `generate_local_script` does for `None`): a pipe or a CI
job must not hang on a question.

## Existing Script
Refused unless `--force`; the card is the one `simplibs-file` raises.
"""
