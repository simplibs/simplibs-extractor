def describe_failure(exc: BaseException) -> str:
    """Shorten an exception to one readable line for a report.

    Args:
        exc: The exception. A `simplibs` card prints as a framed block of
            several lines; any other exception prints as one.

    Returns:
        The class name and the first line of the message that contains a
        letter or a digit (so frame lines made of `═` or `─` are skipped).
    """

    # 1. Split the printed message into stripped lines
    lines = [line.strip() for line in str(exc).splitlines()]

    # 2. The first line with real content; frames and blank lines have none
    message = next((line for line in lines if any(char.isalnum() for char in line)), "")

    # 3. The class name is always shown; the message only if there is one
    name = type(exc).__name__
    return f"{name}: {message}" if message else name


_DESIGN_NOTES = """
# describe_failure — One Line per Failed File

## Purpose
A report lists many files; a failed one gets a single line, not a full
diagnostic card. The card is for the person debugging one error; the report
is for scanning many.

## Why Not an Attribute of the Card
The card's fields are not part of what this library relies on. Reading the
printed text works for every exception, with or without a card.

## Shared by the Phases
Read, transform and write all report per-file failures the same way, so the
helper lives in `logic/_common`.
"""
