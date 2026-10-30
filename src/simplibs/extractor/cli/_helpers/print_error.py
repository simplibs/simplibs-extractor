import sys


def print_error(error: BaseException) -> None:
    """Print an error card to standard error.

    Args:
        error: The exception; a `simplibs` card prints as its framed block.
    """

    # 1. Diagnostics go to standard error, so they never mix with a piped result
    print(error, file=sys.stderr)


_DESIGN_NOTES = """
# print_error — One Way to Show a Refused Command

## Purpose
`run_cli` and `run_init` end a refused command the same way. The card is
printed as it is: it already says what, why and how to fix it.

## Not the Logger
A logger prefixes the first line of a multi-line card with time and level,
which breaks its frame.
"""
