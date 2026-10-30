import argparse
from simplibs.cli import is_interactive, prompt_confirm


def collect_dry_run(args: argparse.Namespace, asked: bool) -> bool:
    """Decide whether this run is a dry run.

    Args:
        args: The normalized arguments.
        asked: Whether the person was already asked something (a profile or the source).

    Returns:
        `True` or `False` from the flag if it was given. Otherwise it is asked
        in a terminal, but only when the person is in the wizard already;
        everything else is `False`.
    """

    # 1. The flag decides
    if args.dry_run is not None:
        return args.dry_run

    # 2. A person who typed the full command wants it to run, not another question
    if asked and is_interactive():
        return prompt_confirm("Dry run (write nothing)?", default=False)

    return False


_DESIGN_NOTES = """
# collect_dry_run — Ask Only Those Who Are Already Being Asked

## Purpose
The draft asked every time in a terminal, including after a complete command
line. That is one question too many for someone who typed everything.

## `asked`
The caller knows whether the wizard asked anything; this function only
applies the rule.
"""
