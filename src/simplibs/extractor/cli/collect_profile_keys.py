import argparse
from simplibs.cli import prompt_choice, prompt_multi_choice, require_interactive
# Outers
from ..registry import expand_profile_keys
# Inners
from ._helpers import profile_options, system_options
from ._validations import raise_unknown_system_error


def collect_profile_keys(args: argparse.Namespace) -> list[str]:
    """Get the profile keys from the command line, or ask for them.

    Args:
        args: The normalized arguments.

    Returns:
        The full keys, in the order given.

    Raises:
        ParamError: If the system is unknown.
        StateError: If profiles are missing and there is nobody to ask.
    """

    # 1. Given on the command line: just expand them
    if args.profiles:
        return expand_profile_keys(args.system, args.profiles)

    # 2. Missing: a terminal can be asked, a pipe or a CI job gets a card instead of a hang
    require_interactive("no profile was given - pass SYSTEM PROFILES, or run in a terminal")

    # 3. The system: given, or asked
    system = args.system or prompt_choice("System", system_options())
    options = profile_options(system)
    if not options:
        raise_unknown_system_error(system)

    # 4. The profiles of that system
    names = prompt_multi_choice("Profiles", options)
    return expand_profile_keys(system, list(names))


_DESIGN_NOTES = """
# collect_profile_keys — Command Line First, Question Second

## Purpose
`simplibs-extractor python code-clean .` runs without asking anything. Leave
out the profiles and, in a terminal, the tool asks; in a pipe it refuses with
a card that says what to pass.

## Unknown System
Checked before the question, because `prompt_multi_choice` has nothing to
offer for a system without profiles.
"""
