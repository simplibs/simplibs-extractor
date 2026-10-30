from simplibs.style import ERROR, SUCCESS
# Outers
from ...definitions import ExtractionResult
from ...logic import format_summary


def print_result(result: ExtractionResult) -> None:
    """Print the summary of a result; the first line is green on success and red otherwise.

    Args:
        result: The result of an extraction.
    """

    # 1. Build the text with the same function every other caller uses
    head, _, rest = format_summary(result).partition("\n")

    # 2. Color only the headline; `style` turns itself off when the output is not a terminal
    paint = SUCCESS if result.success else ERROR
    print(paint(head) + (f"\n{rest}" if rest else ""))


_DESIGN_NOTES = """
# print_result — The One Place the Library Prints

## Purpose
A script is run by a person who wants to see what happened. The library
itself never prints; only this function, and only for the scripts.

## Colors Without Conditions
`simplibs.style` is plain text in a pipe, a file or a log, so there is no
`isatty` check here.
"""
