import argparse
from simplibs.cli import print_choices
# Inners
from ._helpers import profile_options, system_options
from ._validations import raise_list_unknown_system_error


def handle_list_options(args: argparse.Namespace) -> bool:
    """Answer `--list-systems` and `--list-profiles`.

    Args:
        args: The normalized arguments.

    Returns:
        True if a list was printed (the command is finished), False if no list was asked for.

    Raises:
        ParamError: If `--list-profiles` names a system without profiles.
    """

    # 1. The systems
    if args.list_systems:
        print_choices(system_options(), title="Systems:")
        return True

    # 2. The profiles of one system; an unknown system is an error, not an empty list
    if args.list_profiles:
        options = profile_options(args.list_profiles)
        if not options:
            raise_list_unknown_system_error(args.list_profiles)
        print_choices(options, title=f"Profiles of {args.list_profiles}:")
        return True

    # 3. Nothing to list
    return False


_DESIGN_NOTES = """
# handle_list_options — Questions About the Registry

## Purpose
`--list-systems` and `--list-profiles` answer from the registry and end the
command; nothing is extracted.

## Unknown System Is an Error
An empty list would look like "no profiles exist", which hides the typo.
"""
