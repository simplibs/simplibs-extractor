import argparse
from pathlib import Path
from simplibs.cli import prompt_path, require_interactive, resolve_or_prompt
from simplibs.path import normalize_path


def collect_source(args: argparse.Namespace) -> Path:
    """Get the source folder from the command line, or ask for it.

    Args:
        args: The normalized arguments.

    Returns:
        The normalized path of an existing folder.

    Raises:
        StateError: If the source is missing or not a folder and there is nobody to ask.
    """

    # 1. Anything that is not a usable folder needs an answer; without a terminal that is a card
    if args.source is None or not Path(args.source).is_dir():
        require_interactive("the SOURCE folder is missing or is not a folder")

    # 2. A good value is used as it is; a bad or missing one is replaced by a question
    answer = resolve_or_prompt(
        args.source,
        is_valid=lambda value: value is not None and Path(value).is_dir(),
        prompt=lambda: prompt_path("Source folder", kind="dir", must_exist=True),
        invalid_message=f"'{args.source}' is not a folder.",
    )
    return normalize_path(answer)


_DESIGN_NOTES = """
# collect_source — The Folder to Extract

## Purpose
Same rule as the profiles: command line first, question second, card instead
of a hang.

## Check Before `resolve_or_prompt`
`resolve_or_prompt` would ask in any case; the card must come first so a CI
job learns which argument is missing.
"""
