import argparse
from pathlib import Path
# Inners
from ._helpers import is_profile_reference
from ._validations import raise_too_many_positionals_error


def normalize_positionals(args: argparse.Namespace) -> argparse.Namespace:
    """Sort out which positional word is a system, profiles or the source.

    `argparse` fills the three positionals strictly in order, but people type
    `simplibs-extractor ./src` or `simplibs-extractor generic/all ./src`.

    Args:
        args: The parsed arguments.

    Returns:
        A copy with `system`, `profiles` and `source` assigned correctly; `args` is not changed.

    Raises:
        ParamError: If full profile keys are followed by two more words.
    """
    system, profiles, source = args.system, args.profiles, args.source

    # 1. A single word that is a folder and no known system or key is the source
    if system and profiles is None and source is None and not is_profile_reference(system) and Path(system).is_dir():
        system, source = None, Path(system)

    # 2. A first word with full keys (`generic/all` or `a,b`) is the list of profiles; the next one is the source
    elif system and ("/" in system or "," in system):
        if source is not None:
            raise_too_many_positionals_error(system, profiles, source)
        if profiles is not None:
            source = Path(profiles)
        profiles, system = system, None

    # 3. Return a copy, so the caller can still see what was typed
    return argparse.Namespace(**{**vars(args), "system": system, "profiles": profiles, "source": source})


_DESIGN_NOTES = """
# normalize_positionals — "What Did They Mean?"

## Purpose
Three optional positionals cannot be told apart by `argparse`. This is the
one place that guesses, and it guesses from the registry first and from the
disk second.

## Order of the Guesses
A registered system or key is always a profile reference, even if a folder of
the same name exists: `python` means the system. Only a word that is not a
profile reference and is a folder becomes the source.

## A Copy, Not a Mutation
The caller keeps the original namespace for messages and tests.
"""
